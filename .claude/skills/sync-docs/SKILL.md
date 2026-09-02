---
name: sync-docs
description: Re-sync the modding knowledge base in docs/ from the local source repos (oculory, ehlnofey, Wintersun-Nordic-Addon, enderal-mods, zenderal-patches) via tools/sync.py and sources.json. Use when the user wants to refresh, update, resync or rebuild the docs, add a source repo or mapping, or asks why a document is missing or stale.
---

# Sync the knowledge base

`docs/` is generated from the source repos by `tools/sync.py`. This skill runs that end to end.

## Preconditions

- Python 3 on PATH (`python --version`); the script is stdlib-only.
- Every source root in `sources.json` exists and is a git checkout. The sync reads them and never
  changes their branch; it records whichever branch is checked out.

## Steps

1. **Dry run first.**
   ```powershell
   python tools/sync.py --check --verbose
   ```
   Read the header lines (`source <name>: <root> @ <branch> <commit>`). If a source is on a
   feature branch, note it for the commit message. Read any `WARNING:` lines: a "drifted from
   canonical" warning means a skipped duplicate copy no longer matches its canonical file — that
   is fixed in the source repos, never by adding a second mapping.
2. **Sync.**
   ```powershell
   python tools/sync.py
   ```
3. **Review** `docs/INDEX.md`: the per-section tables (flags **G** generated, **S** superseded,
   **D** dirty source), the "Unresolved links" list (expected: links into `src/`, data files, and
   folders without a README) and the "Duplicate-copy checks" table.
4. **Confirm idempotency**: `python tools/sync.py --check` must exit 0 with `0 added, 0 modified`.
5. **Rebuild the retrieval index** if anything under `docs/` changed:
   ```powershell
   .venv\Scripts\python.exe rag\index.py --build
   ```
   It re-chunks and re-embeds only the documents whose bodies moved, so this is seconds unless the
   sync was large. A moved document changes its `id`, which the build handles as a delete plus an
   add. `rag/index.py --check` exits 1 while anything is stale. The index is gitignored — rebuild
   it, never commit it.
6. **Commit** `docs/` together with any `sources.json` change:
   `git add docs sources.json && git commit -m "sync: <what changed> (<repo> @ <branch>)"`.

## Changing what is synced

- New document or folder: add a mapping to `sources.json` (see `tools/README.md` for fields). Put
  single-file mappings before broad globs; the first match wins.
- Moving a document: change `to`/`rename`. Its `id` changes with it, so the retriever treats it as
  a new document — say so in the commit message.
- Skipping a copy that exists in two repos: do not map the copy; add it under `duplicates`.
- Forcing flags a file's head does not announce (`generated`, `superseded`, `title`…): use the
  mapping's `overrides` block keyed by the source-relative path.

## Never

- Edit anything under `docs/` by hand.
- Run `git checkout`, `git pull` or any write operation in a source repo from this skill.
- Add non-stdlib imports to `tools/sync.py` or `rag/chunk.py`.
- Commit `rag/index/` — it is derived state, rebuilt by `rag/index.py --build`.
