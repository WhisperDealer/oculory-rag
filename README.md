# oculory-rag — the modding knowledge base

One place that holds the documentation from all of my Bethesda modding repos: how Skyrim SE and
Enderal SE actually work under the hood, what third-party mods like EGO, Requiem, SkyPatcher and
SPID do, and how my own mods (Ehlnofey, Wintersun Nordic Addon, the Enderal ports, the Zenderal
patches) are designed and built.

Read it here — `curated/overview.md` is the way in, and `docs/INDEX.md` lists every document.

It is also **retrievable from Claude Code**. Every document carries the metadata a chunker and
retriever need (stable id, section, game, kind, tags, generated/superseded flags, confidence-tag
counts, content hash), and `rag/` turns that into a hybrid BM25 + local-embedding index served over
MCP, so any project on this machine can search the knowledge base. See `rag/README.md`.

## How it works

The five source repos stay canonical. **`docs/` is generated** by `tools/sync.py` from the
mappings in `sources.json`: the script copies the selected markdown out of the local checkouts,
stamps a YAML frontmatter block on each file, rewrites relative links so they resolve inside this
repo, and writes `docs/INDEX.md` and `docs/catalog.json`. Re-running it with unchanged sources
writes nothing.

```
source repos (canonical)              this repo
  oculory/arch-docs, CLAUDE.md  ─┐
  ehlnofey/arch-docs, CLAUDE.md  ├─ sources.json ─► tools/sync.py ─► docs/**  (generated, committed)
  Wintersun-Nordic-Addon         │                                  docs/INDEX.md, docs/catalog.json
  enderal-mods/arch-docs         │
  zenderal-patches/arch-docs    ─┘                 curated/**   (hand-written, never synced)
```

**Never edit anything under `docs/`.** Fix the source repo, then re-run the sync. Hand-written
cross-cutting material goes in `curated/`.

## Running the sync

Requires Python 3 (stdlib only) and git. The source repos must be present at the paths in
`sources.json`; the script reads them and never writes to them or changes branches.

```powershell
python tools/sync.py --check          # dry run: what would change (exit 1 if anything)
python tools/sync.py --check --diff   # ...with unified diffs
python tools/sync.py                  # write docs/, prune orphans
python tools/sync.py --verbose        # also list unresolved links and duplicate checks
powershell -File tools/sync.ps1 --check   # same thing from PowerShell 5.1
```

Then review `docs/INDEX.md` (the "Unresolved links" and "Duplicate-copy checks" sections in
particular), rebuild the retrieval index with `.venv\Scripts\python.exe rag\index.py --build`,
and commit `docs/` together with any `sources.json` change. The knowledge base
reflects **whatever branch each source repo has checked out**; the branch and commit are recorded
in every document's frontmatter, so mention the branches in the commit message when they are not
`main`.

## Layout

```
docs/
  workspace/          the Spriggit workspace template (oculory) — guide, readme, contributing,
                      bootstrap prompt, and the Claude Code skills/ and agents/ it ships
  tooling/            third-party tools that apply to both games (SPID)
  skyrim/reference/   engine facts: record patterns that build clean but do nothing, encounter zones
  skyrim/world/       vanilla-world research: dungeons, enemies, factions, regions, progression, lore
  enderal/reference/  how Enderal actually works: plugin architecture, progression, combat, crafting,
                      scripting, factions, bestiary, world; Enderal record patterns
  enderal/tooling/    SPID under Enderal
  mods/<mod>/         third-party mods: ego, requiem, skypatcher, morrowloot
  projects/<repo>/    my mods, one folder per source repo: workspace-guide (CLAUDE.md), readme,
                      design docs, per-mod subfolders (apocalypse, triumvirate)
  modlists/zenderal/  the Zenderal modlist: curation, controller setup, build report, magic dataset
  INDEX.md            generated table of every document, unresolved links, duplicate checks
  catalog.json        the same data as JSON, plus link graph and per-repo branch/commit
curated/              hand-written: overview (start here), glossary, repos
rag/                  the retriever: chunker, SQLite index, MCP server, design note
tools/                sync.py, sync.ps1, README (manifest field reference)
sources.json          the manifest — the only place routing decisions live
```

## Searching it from Claude Code

`rag/` indexes the corpus and serves it as an MCP server, so `search`, `fetch` and `list_docs` are
available in every Claude Code project on this machine — not just this one.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r rag\requirements.txt
.venv\Scripts\python.exe rag\index.py --build --stats

claude mcp add --scope user oculory-rag -- `
  C:/dev/modding/confluence-rag-modding/.venv/Scripts/python.exe `
  C:/dev/modding/confluence-rag-modding/rag/server.py
```

Retrieval is hybrid: SQLite FTS5 for keywords and a local ONNX embedding model for meaning, fused
and filtered on the frontmatter (`game` first — Skyrim and Enderal facts must not mix). It runs
offline, needs no API key, and the index is derived state you rebuild rather than commit. Full
detail, including the retrieval quality bar, is in `rag/README.md`.

A second index covers the **decompiled game files** — 331,641 records and 19,404 Papyrus scripts
from vanilla Skyrim SE and from Enderal's own plugins — behind the `game_search` and `game_read`
tools, so a question can be answered from the actual record rather than from memory of it.

```powershell
.venv\Scripts\python.exe rag\gamedata.py --build     # ~50 seconds
```

That data is copyrighted Bethesda and SureAI content. **It is indexed in place and never copied
into this repo**: the index stores paths into the source repos and reads bodies on demand, so no
game file is ever committed here. See `rag/gamesources.json` for what is indexed and rule 9 in
`CLAUDE.md` for the constraint.

## Source repos

| Source | Path | What is taken | What is skipped |
|---|---|---|---|
| `oculory` | `C:/dev/modding/oculory` | CLAUDE.md, README, CONTRIBUTING, both arch-docs, skills, agents | ExampleMod sources |
| `ehlnofey` | `C:/dev/modding/ehlnofey` | CLAUDE.md, README, world/, prior-art/, design/ (md + one .txt), summary/README | `.ps1`/`.py`/`.csv`/`.pptx` evidence files; template docs (identical to oculory's) |
| `wintersun` | `C:/dev/modding/Wintersun-Nordic-Addon` | CLAUDE.md, README | template docs (identical to oculory's) |
| `enderal-mods` | `C:/dev/modding/enderal-mods` | CLAUDE.md, README, enderal/, EGO/, Apocalypse/, Triumvirate/, enderal-record-patterns, two porter agents | `ego_report.py`; template prompt |
| `zenderal` | `C:/modding/mod-projects/zenderal-patches` | CLAUDE.md, README, curation, controller setup, build report, tools/spid*, magic/*.md, magic-extract skill | enderal/ and EGO/ (older copies of enderal-mods'), magic/data and magic/tools |

The `duplicates` block in `sources.json` lists every skipped copy; the sync compares each one
against its canonical file and warns when a copy that should be identical has drifted.

## Frontmatter

Every synced document starts with a block like this (values are JSON, which is valid YAML, so no
YAML library is needed on either side):

```yaml
---
id: "enderal/reference/bestiary"        # destination path without docs/ and .md — the stable key
title: "Enderal bestiary — …"           # first H1, or a title set in the manifest
slug: "bestiary"
section: "enderal/reference"            # the folder part of the id; the RAG filter
game: "enderal"                         # skyrim | enderal | both
kind: "reference"                       # reference | world | research | design | guide | workspace | modlist
project: null                           # my-mod repo this belongs to, or null
mod: null                               # third-party mod for docs/mods/*
tags: ["enderal", "engine", "source:enderal-mods"]
source_repo: "enderal-mods"
source_path: "arch-docs/enderal/bestiary.md"
source_branch: "main"
source_commit: "…"                      # last commit that touched the source file
source_dirty: false                     # source file had uncommitted edits at sync time
generated: false                        # machine-generated table (conflict index, test matrix…)
generator: null
superseded: false                       # replaced by a newer doc; superseded_by names it
superseded_by: null
phase: null                             # ehlnofey's "Phase N, document M" provenance
confidence: {"author": 0, "community": 3, "unverified": 2, "upstream": 0, "verified": 41}
lines: 316
content_sha256: "…"                     # of the body; synced_at only moves when this changes
synced_at: "2026-09-02T12:00:00Z"
sync_version: 1
---
```

Optional keys: `unique_title` (only when two docs share a title), `skill_name` /
`agent_name` / `description` / `agent_meta` (folded from the skills' and agents' own frontmatter).
The `confidence` counts come from the `[verified]` / `[community]` / `[unverified]` /
`[upstream]` / `[author]` marks the source docs use inline.

## Third-party content

`docs/mods/**` and parts of `docs/modlists/**` describe other people's mods (EGO, Requiem,
SkyPatcher, MorrowLoot, SPID, the Zenderal list's contents). The prose is mine; the generated
record tables are derived from those mods' plugins. **This repo is public on GitHub**, so that
material is already published: check each mod's permissions before adding more of it here, and
before reusing any of it elsewhere.

## Licence

MIT, matching the source repos. See `LICENSE`.
