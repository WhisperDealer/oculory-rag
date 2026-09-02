# RAG pipeline — design note

Not built yet. This records how `docs/` and `curated/` are meant to be chunked, embedded and
filtered so the pipeline, when it is written, only has engineering decisions left.

## Inputs

- Every `*.md` under `docs/` except `INDEX.md`, plus every `*.md` under `curated/`. Both carry
  the same frontmatter shape; curated docs have `kind: "curated"`.
- `docs/catalog.json` for the document list, the `links_out` graph and per-source branch/commit.
- The frontmatter values are JSON scalars/collections, so a five-line parser (split on the
  `---` fences, `key: json.loads(value)`) is enough. No YAML dependency is needed.

## Chunking

- Split on `##` and `###` headings. Keep a table intact inside one chunk where possible; if a
  table exceeds the chunk budget, split between rows and repeat the header row.
- Prepend a breadcrumb to every chunk's text before embedding:
  `"<title> › <H2> › <H3>"`. The record-shaped docs (conflict index, new records, magic
  conflicts) are meaningless without it.
- Target roughly 300–600 tokens per chunk; never split inside a fenced code block.
- Chunk id = `<doc id>#<chunk_index>`; also carry `heading_path` as a list.

## Metadata carried per chunk

From the document: `id`, `title`, `section`, `game`, `kind`, `project`, `mod`, `tags`,
`source_repo`, `source_path`, `source_commit`, `generated`, `superseded`, `phase`,
`confidence` (the five counts), `content_sha256`. Per chunk: `chunk_index`, `heading_path`.

## Filtering and ranking guidance

- Default retrieval excludes `superseded: true`. Include on request with a "superseded by …"
  note in the answer.
- The `generated: true` documents are lookup tables, not prose. Put them in a separate
  collection (or a BM25/exact-match index keyed on EditorID and FormID) and query that when the
  question contains a FormID, EditorID or plugin name; keep them out of the default semantic
  collection to stop record rows drowning the explanatory docs.
- `game` is the first filter: a Skyrim question should not retrieve Enderal engine facts, and
  the reverse is worse (`enderal/reference/plugin-architecture` explains why). `both` is always
  eligible.
- Prefer chunks whose parent document has `confidence.verified > 0` when ranking ties.
- `links_out` gives cheap neighbour expansion: after the top-k, pull the first chunk of each
  linked document as extra context.

## Refresh

- Re-embed a document only when its `content_sha256` changed since the last index build; keep
  `rag/index/` (gitignored) with the hash per document.
- A changed `id` is a delete plus an add.

## Tooling

Python, matching `tools/sync.py`. Any embedding model and store will do; the corpus is small
(under 40k lines of markdown), so a local store such as SQLite with an embedding column, or
Chroma, is sufficient. Keep the chunker and the store adapter separate so the same chunks can be
pushed to a hosted store later.
