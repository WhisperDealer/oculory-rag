#!/usr/bin/env python3
"""server.py -- the knowledge base as an MCP stdio server.

Registered once at user scope, this gives every Claude Code project three tools over
the Skyrim/Enderal modding corpus in this repo. Register it with:

    claude mcp add --scope user oculory-rag -- \
        C:/dev/modding/confluence-rag-modding/.venv/Scripts/python.exe \
        C:/dev/modding/confluence-rag-modding/rag/server.py

Two constraints shape this file. It starts in every session, so nothing heavy is
imported or opened at module scope -- the database and the embedding model are built on
first use. And stdout is the JSON-RPC channel, so every diagnostic goes to stderr;
a stray print() here breaks the protocol for the whole session.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.mcpserver import MCPServer      # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SEARCH_BUDGET = 14000        # characters of chunk text returned by one search
FETCH_BUDGET = 20000         # above this a document is outlined, not dumped

_store = None
_stale_note = ""


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def get_store():
    """Open the index on first use and check it against the current catalog."""
    global _store, _stale_note
    if _store is None:
        from store import Store
        import index as indexer
        _store = Store()
        built = _store.get_meta("catalog_generated_at")
        current = indexer.catalog_stamp()
        if built != current:
            _stale_note = ("\nNOTE: the index is older than docs/catalog.json"
                           " -- run `python rag/index.py --build` to refresh it.")
            log(f"index stale: built against catalog {built}, current is {current}")
    return _store


def _filters(game=None, section=None, kind=None, project=None, mod=None, tag=None,
             include_generated=False, include_superseded=False):
    from store import Filters
    return Filters(game=game, section=section, kind=kind, project=project, mod=mod,
                   tag=tag, include_generated=include_generated,
                   include_superseded=include_superseded)


def _flags(row) -> str:
    bits = []
    if row["generated"]:
        bits.append("generated lookup table")
    if row["superseded"]:
        bits.append(f"SUPERSEDED by {row['superseded_by']}")
    conf = json.loads(row["confidence"] or "{}")
    marks = [f"{n} {tag}" for tag, n in sorted(conf.items()) if n]
    if marks:
        bits.append(", ".join(marks))
    return " | ".join(bits)


server = MCPServer(
    name="oculory-rag",
    version="1.0.0",
    instructions=(
        "Retrieval over a personal Skyrim SE / Enderal SE modding knowledge base: "
        "engine behaviour, record patterns, third-party mods (EGO, Requiem, SkyPatcher, "
        "MorrowLoot, SPID), the Zenderal modlist, and the author's own mod projects. "
        "Search it before answering Bethesda modding questions; cite the doc id you used."
    ),
)


@server.tool(
    name="search",
    description=(
        "Search the Skyrim SE / Enderal SE modding knowledge base and return the most "
        "relevant passages. Use for questions about Bethesda engine behaviour, record "
        "patterns, Papyrus, Spriggit/Mutagen workflows, SPID distribution, Enderal's "
        "plugin architecture, or the mods EGO, Requiem, SkyPatcher, MorrowLoot. "
        "Set game to keep Skyrim and Enderal facts apart -- they differ in ways that "
        "matter. Not for non-modding questions."
    ),
)
def search(query: str, k: int = 6, game: str | None = None, section: str | None = None,
           kind: str | None = None, project: str | None = None, mod: str | None = None,
           tag: str | None = None, include_generated: bool = False,
           include_superseded: bool = False) -> str:
    """Args:
        query: A natural-language question, or record/EditorID/plugin names.
        k: How many passages to return (1-20).
        game: "skyrim" or "enderal". Documents marked "both" always stay eligible.
        section: Restrict to a docs/ section, e.g. "enderal/reference", "mods/ego".
        kind: reference, world, research, design, guide, workspace, modlist, curated.
        project: One of the author's repos: ehlnofey, enderal-mods, zenderal-patches,
            wintersun-nordic-addon.
        mod: A third-party mod: ego, requiem, skypatcher, morrowloot, triumvirate,
            apocalypse.
        tag: A frontmatter tag, e.g. "spells", "deleveling", "engine".
        include_generated: Include the machine-generated record tables. They are
            excluded by default and searched automatically when the query names a
            FormID, EditorID or plugin.
        include_superseded: Include documents replaced by a newer one.
    """
    import search as searcher

    store = get_store()
    k = max(1, min(int(k), 20))
    hits, notes = searcher.search(store, query, k, _filters(
        game, section, kind, project, mod, tag, include_generated, include_superseded))
    if not hits:
        return (f"No matches for {query!r} in the modding knowledge base."
                " Try fewer filters or different wording." + _stale_note)

    out = [f"{len(hits)} passages for {query!r}:"]
    budget = SEARCH_BUDGET
    for i, hit in enumerate(hits, 1):
        row = hit.row
        text = row["text"]
        if len(text) > budget:
            text = text[:max(0, budget)].rstrip() + "\n… (truncated)"
        budget -= len(text)
        source = (f"{row['source_repo']}:{row['source_path']}"
                  if row["source_repo"] else row["path"])
        head = (f"\n--- [{i}] {hit.chunk_id}  (score {hit.score:.3f}, {hit.why})\n"
                f"{row['breadcrumb']}\n"
                f"{row['game']} · {row['kind']} · {source}"
                f" · chunk {row['chunk_index'] + 1}/{row['n_chunks']}")
        flags = _flags(row)
        if flags:
            head += f"\n{flags}"
        out.append(f"{head}\n\n{text}")
        if budget <= 0:
            out.append(f"\n({len(hits) - i} further passages omitted to stay in budget;"
                       " fetch them by chunk_id if needed)")
            break

    if notes.get("routed_to_generated"):
        out.append("\n(The query named a record, so the generated lookup tables were"
                   " searched as well.)")
    if not notes.get("semantic"):
        out.append("\n(Keyword search only -- the embedding model is unavailable.)")
    return "\n".join(out) + _stale_note


@server.tool(
    name="fetch",
    description=(
        "Read one document from the modding knowledge base by its id, or one chunk of "
        "it. Use after search to get the full context around a passage. Very long "
        "documents come back as a heading outline instead of the whole body."
    ),
)
def fetch(id: str, chunk: int | None = None, max_chars: int = FETCH_BUDGET) -> str:
    """Args:
        id: Document id as returned by search, e.g. "enderal/reference/bestiary".
            A "doc#n" chunk id also works.
        chunk: Return only this chunk index, with its immediate neighbours.
        max_chars: Above this the document is outlined rather than returned whole.
    """
    store = get_store()
    if "#" in id and chunk is None:
        id, _, suffix = id.partition("#")
        chunk = int(suffix) if suffix.isdigit() else None

    doc = store.document(id)
    if doc is None:
        return (f"No document with id {id!r}. Use list_docs to browse ids,"
                " or search to find one." + _stale_note)

    source = (f"{doc['source_repo']}:{doc['source_path']}"
              if doc["source_repo"] else doc["path"])
    header = [
        f"# {doc['title']}",
        f"id: {doc['id']} · {doc['game']} · {doc['kind']} · {doc['lines']} lines",
        f"source: {source}",
        f"file: {doc['path']}",
    ]
    flags = _flags(doc)
    if flags:
        header.append(flags)
    links = json.loads(doc["links_out"] or "[]")
    if links:
        header.append(f"links to: {', '.join(links)}")

    chunks = store.document_chunks(id)
    if chunk is not None:
        window = [c for c in chunks if abs(c["chunk_index"] - chunk) <= 1]
        if not window:
            return "\n".join(header) + f"\n\nNo chunk {chunk}; it has {len(chunks)}."
        body = "\n\n".join(
            f"--- {c['chunk_id']}  {c['breadcrumb']}\n{c['text']}" for c in window)
        return "\n".join(header) + f"\n\n{body}" + _stale_note

    path = REPO_ROOT / doc["path"]
    text = ""
    if path.is_file():
        import chunk as chunker
        _, text = chunker.read_document(path)

    if len(text) > max_chars:
        # Consecutive chunks under one heading collapse to a range, or a 250-chunk
        # record table produces an outline nearly as unreadable as the document.
        groups: list[list] = []
        for c in chunks:
            crumb = json.loads(c["heading_path"] or "[]")
            label = " › ".join(crumb) if crumb else "(opening)"
            if groups and groups[-1][0] == label:
                groups[-1][2] = c["chunk_index"]
            else:
                groups.append([label, c["chunk_index"], c["chunk_index"]])
        outline = [f"\nThis document is {len(text)} characters across {len(chunks)}"
                   f" chunks, so here is its outline."
                   f" Read a section with fetch(id, chunk=N)."]
        for label, first, last in groups:
            span = f"{first}" if first == last else f"{first}-{last}"
            outline.append(f"  [{span:>9}] {label}")
        return "\n".join(header) + "\n" + "\n".join(outline) + _stale_note

    return "\n".join(header) + f"\n\n{text}" + _stale_note


@server.tool(
    name="list_docs",
    description=(
        "Browse the modding knowledge base's table of contents: document ids, titles "
        "and flags, without their text. Use to see what the corpus covers before "
        "searching, or to find the id of a document you want to fetch."
    ),
)
def list_docs(section: str | None = None, game: str | None = None,
              kind: str | None = None, project: str | None = None,
              mod: str | None = None, tag: str | None = None,
              q: str | None = None, limit: int = 200) -> str:
    """Args:
        section: A docs/ section prefix, e.g. "enderal", "mods/ego", "skyrim/world".
        game: "skyrim" or "enderal"; "both" documents always stay eligible.
        kind: reference, world, research, design, guide, workspace, modlist, curated.
        project: ehlnofey, enderal-mods, zenderal-patches, wintersun-nordic-addon.
        mod: ego, requiem, skypatcher, morrowloot, triumvirate, apocalypse.
        tag: A frontmatter tag.
        q: Substring match against the id and title.
        limit: Maximum rows.
    """
    store = get_store()
    rows = store.list_documents(
        _filters(game, section, kind, project, mod, tag, include_superseded=True),
        q=q, limit=max(1, min(int(limit), 500)))
    if not rows:
        return "No documents match those filters." + _stale_note

    out = [f"{len(rows)} documents (G = generated lookup table, S = superseded):"]
    current = None
    for row in rows:
        if row["section"] != current:
            current = row["section"]
            out.append(f"\n## {current}")
        mark = "G" if row["generated"] else ("S" if row["superseded"] else " ")
        out.append(f"  {mark} {row['id']:<52} {row['game']:<7} {row['lines']:>5}L"
                   f"  {row['title']}")
    return "\n".join(out) + _stale_note


if __name__ == "__main__":
    server.run("stdio")
