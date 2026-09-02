# RAG pipeline

Built. `docs/` and `curated/` are chunked, embedded and served to Claude Code as an MCP server, so
any project on this machine can retrieve from the knowledge base instead of guessing at engine
behaviour. The design decisions below came first and the code follows them; where the build
learned something the note did not anticipate, it is called out.

```
chunk.py    frontmatter parser + heading-aware chunker      stdlib only
store.py    SQLite: documents, chunks, FTS5, embeddings
embed.py    BAAI/bge-small-en-v1.5 via fastembed, lazy-loaded
index.py    CLI: --build / --check / --rebuild / --stats / --eval
search.py   hybrid fusion, filters, ranking, record routing
server.py   the MCP stdio server: search, fetch, list_docs
eval.jsonl  15 question -> expected-document cases
index/      the built index and the model cache (gitignored)
```

## Setup

Needs Python 3 and about 400 MB for the venv, the ONNX model and the index.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r rag\requirements.txt
.venv\Scripts\python.exe rag\index.py --build --stats
```

The first build downloads the embedding model (~130 MB into `rag/index/models/`) and embeds the
whole corpus, which takes about eight minutes on CPU. Every build after that only touches the
documents whose bodies changed — re-adding a single document takes seconds.

Then register the server once, at user scope, so every project gets it:

```powershell
claude mcp add --scope user oculory-rag -- `
  C:/dev/modding/confluence-rag-modding/.venv/Scripts/python.exe `
  C:/dev/modding/confluence-rag-modding/rag/server.py
```

`claude mcp list` should show `oculory-rag ✔ Connected`. The paths are absolute because the server
must resolve the repo from any working directory; it derives the root from its own `__file__`.

## The tools Claude gets

| Tool | What it does |
|---|---|
| `search(query, k, game, section, kind, project, mod, tag, include_generated, include_superseded)` | Ranked passages with breadcrumb, source repo/path, confidence counts and flags. |
| `fetch(id, chunk, max_chars)` | A whole document, or one chunk with its neighbours. Oversized documents come back as a heading outline with chunk indices. |
| `list_docs(section, game, kind, project, mod, tag, q, limit)` | The table of contents, no bodies. |

There is also a CLI for the same retrieval, useful when tuning:

```powershell
.venv\Scripts\python.exe rag\search.py "how does SPID distribute spells" --game enderal --text
```

## Refresh

The index is derived. After a sync that changed `docs/`:

```powershell
.venv\Scripts\python.exe rag\index.py --build
```

`--check` reports what is stale and exits 1 if anything is, mirroring `tools/sync.py`. A document
is re-chunked and re-embedded only when its body hash moved; a changed `id` is a delete plus an
add. The server compares the index against `docs/catalog.json` at startup and appends a one-line
"run index.py --build" note to its answers when it is behind — it never refuses to serve.

---

# Design note

How `docs/` and `curated/` are chunked, embedded and filtered.

## Inputs

- Every `*.md` under `docs/` except `INDEX.md`, plus every `*.md` under `curated/`. Both carry the
  same frontmatter shape; curated docs have `kind: "curated"`.
- `docs/catalog.json` for the document list, the `links_out` graph and per-source branch/commit.
- The frontmatter values are JSON scalars/collections, so a five-line parser (split on the `---`
  fences, `key: json.loads(value)`) is enough. No YAML dependency is needed.

The three curated documents are not in the catalog and carry only the minimal six-key frontmatter,
so `chunk.py` globs them separately and computes their body hash itself. It computes the hash for
every document rather than trusting the catalog, which keeps one refresh path for both.

## Chunking

- Split on `##` and `###` headings. Keep a table intact inside one chunk where possible; if a
  table exceeds the chunk budget, split between rows and repeat the header row.
- Prepend a breadcrumb to every chunk's text before embedding: `"<title> › <H2> › <H3>"`. The
  record-shaped docs (conflict index, new records, magic conflicts) are meaningless without it.
- Target roughly 300–600 tokens per chunk; never split inside a fenced code block.
- Chunk id = `<doc id>#<chunk_index>`; also carry `heading_path` as a list.

Budgets are in characters (1800 target, 3000 hard) at ~4 chars/token, which keeps `chunk.py` free
of a tokenizer. Two rules were added during the build: undersized sections merge forward into a
sibling under the same `##`, or a document of one-line `###` subsections yields a dozen useless
chunks; and an oversized block that is neither a fence nor a table (a long bullet run, a blockquote
with no blank lines) splits on line boundaries. A fenced code block is still never split, so four
chunks in the corpus are over budget on purpose. The corpus chunks to **2046 chunks over 99
documents**.

## Metadata carried per chunk

From the document: `id`, `title`, `section`, `game`, `kind`, `project`, `mod`, `tags`,
`source_repo`, `source_path`, `source_commit`, `generated`, `superseded`, `phase`, `confidence`
(the five counts), `content_sha256`. Per chunk: `chunk_index`, `heading_path`.

`game`, `generated` and `superseded` are denormalised onto `chunks` so filtering happens before
scoring rather than after.

## Filtering and ranking

- Default retrieval excludes `superseded: true`. Include on request with a "superseded by …" note
  in the answer.
- The `generated: true` documents are lookup tables, not prose. They are chunked into the FTS5
  index but **never embedded** — 723 of the 2046 chunks — and stay out of the default pool, so
  record rows cannot drown the explanatory docs. A query naming a FormID, EditorID or plugin
  routes to them automatically.
- `game` is the first filter: a Skyrim question should not retrieve Enderal engine facts, and the
  reverse is worse (`enderal/reference/plugin-architecture` explains why). `both` is always
  eligible.
- Prefer chunks whose parent document has `confidence.verified > 0` when ranking ties.
- `links_out` gives cheap neighbour expansion: `fetch` lists a document's links so the caller can
  pull what it actually wants, rather than inflating every search result.

BM25 and cosine are fused with reciprocal rank fusion, which needs only the two orderings and so
copes with generated chunks that appear in one list and not the other. Three things were measured
rather than assumed, all against `eval.jsonl`:

- **RRF's textbook k=60 is wrong here.** It is calibrated for runs over millions of documents.
  Over 2000 chunks it flattens the ranks until "appears in both lists" outweighs "ranked first at
  0.82 cosine", letting a noisy keyword arm decide the order. `k=10`.
- **Stopwords have to go.** Terms are OR-ed, so `what`/`does`/`about` do not merely score ~0, they
  drag in every chunk containing them and dilute the candidate pool the fusion sees. Questions
  phrased as questions are mostly stopwords.
- **The routed record arm gets no penalty.** Demoting it was backwards: the "don't drown the prose"
  concern is already handled by excluding generated docs from the default pool, and once the
  question names a record, the lookup table is the answer.

`index.py --eval` scores 15/15 recall@5 with MRR 0.80. Retune against it before changing any
constant in `search.py`.

## Refresh

- Re-embed a document only when its `content_sha256` changed since the last index build; keep
  `rag/index/` (gitignored) with the hash per document.
- A changed `id` is a delete plus an add.
- Changing the embedding model drops every vector and re-embeds; `index.py` detects this from the
  `embed_model` key in the index's `meta` table.

## Tooling

Python, matching `tools/sync.py`. SQLite holds the chunks, the FTS5 index and the vectors in one
gitignored file; at 1323 vectors × 384 dimensions a brute-force cosine is faster than any
approximate index would be. The chunker and the store stay separate so the same chunks can be
pushed to a hosted store later — `python rag/chunk.py --all --jsonl` dumps them with their
metadata for exactly that.

Lexical retrieval needs no dependency at all: CPython ships SQLite with FTS5 and `bm25()`. If
fastembed is unavailable, `embed.available()` is False and everything degrades to lexical-only
rather than failing.
