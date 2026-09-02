---
id: "curated/repos"
title: "Source repos — what feeds the knowledge base"
section: "curated"
game: "both"
kind: "curated"
tags: ["repos", "sources", "provenance"]
---

# Source repos — what feeds the knowledge base

Five local git checkouts are canonical. `tools/sync.py` reads them; nothing is ever written back.
The sync records the branch and commit each document came from, so a document synced from a
feature branch says so in its frontmatter.

| Source name | Local path | Remote | Game | Purpose |
|---|---|---|---|---|
| `oculory` | `C:/dev/modding/oculory` | `WhisperDealer/oculory` | Skyrim SE | The Spriggit workspace template. Every other repo is a clone of it. |
| `ehlnofey` | `C:/dev/modding/ehlnofey` | `WhisperDealer/ehlnofey` | Skyrim SE | Deleveling overhaul; the docs-heaviest repo (world research, prior art, design). |
| `wintersun` | `C:/dev/modding/Wintersun-Nordic-Addon` | `WhisperDealer/Wintersun-Nordic-Addon` | Skyrim SE | New Nordic deities for Wintersun. Design knowledge lives in its CLAUDE.md. |
| `enderal-mods` | `C:/dev/modding/enderal-mods` | `WhisperDealer/enderal-mods` | Enderal SE | Enderal mods of any shape: ports (Apocalypse, Triumvirate), fixes, replacements. Canonical for the Enderal and EGO reference docs. |
| `zenderal` | `C:/modding/mod-projects/zenderal-patches` | `stefangouldson/zenderal-patches` | Enderal SE | Patches for the Zenderal modlist plus curation docs, SPID references and the magic dataset. |

## What each contributes

- **oculory** → `docs/workspace/` in full: the template CLAUDE.md, README, CONTRIBUTING, the
  bootstrap prompt, twelve skills and three agents; and `docs/skyrim/reference/skyrim-record-patterns.md`.
- **ehlnofey** → `docs/skyrim/world/` (eight vanilla-world surveys),
  `docs/skyrim/reference/engine-behaviour.md`, `docs/mods/{requiem,skypatcher,morrowloot}/`,
  `docs/enderal/reference/deleveling-prior-art.md`, and `docs/projects/ehlnofey/`.
- **wintersun** → `docs/projects/wintersun-nordic-addon/` (workspace guide and readme).
- **enderal-mods** → `docs/enderal/reference/`, `docs/mods/ego/`, `docs/projects/enderal-mods/`
  with `apocalypse/` and `triumvirate/`, and two porter agents in `docs/workspace/agents/`.
- **zenderal** → `docs/modlists/zenderal/`, `docs/tooling/spid.md`,
  `docs/enderal/tooling/spid-in-enderal.md`, and the `magic-extract` skill.

## Deliberate exclusions

- **Duplicate template docs.** `skyrim-record-patterns.md` and `mod-dev-workspace-prompt.md`
  are byte-identical in oculory, ehlnofey and Wintersun (and the prompt in enderal-mods too).
  Only oculory's copies are synced; the others are checked for drift on every run.
- **zenderal-patches' `arch-docs/enderal/` and `arch-docs/EGO/`.** Older copies of the
  enderal-mods folders with Zenderal-specific framing; enderal-mods removed the Zenderal wording on
  2026-08-16 and has edited them since. The sync expects these to differ and reports them as such.
- **Data and tools inside arch-docs.** The magic dataset's JSON and CSV (600k+ lines), the
  MagicExtract C# project, `ego_report.py`, ehlnofey's evidence scripts and CSVs, the slide deck.
  These are inputs and generators, not knowledge; the markdown they produce is synced.
- **`the-modding-bungalo`.** A Jekyll wiki site in the same folder; not a mod repo and not in
  scope for now. Adding it is one source entry and a few mappings.
- **`Vel-Dun-MO2-Profile`, `Zen-Traits`.** MO2 themes and a third-party mod payload; no docs.

## Branch policy

Sync from whatever is checked out, but say so. When enderal-mods or zenderal-patches are on a
feature branch, the synced docs may describe unreleased work; the `source_branch` field in every
document and the `sources` block in `docs/catalog.json` make that visible.
