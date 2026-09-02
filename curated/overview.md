---
id: "curated/overview"
title: "Knowledge base overview — start here"
section: "curated"
game: "both"
kind: "curated"
tags: ["overview", "map", "start-here"]
---

# Knowledge base overview — start here

Everything under `docs/` is a synced copy of documentation that lives in one of five modding
repos (see `repos.md`). This page says what each section holds and where to start reading.

## `docs/workspace/` — how the mods are built

The Spriggit workspace template that every mod repo is cloned from. Plugins are decompiled to YAML,
edited as text under git, and rebuilt with the Spriggit CLI; Papyrus scripts go through a
command-line extract → decompile → compile → package loop. Start with `workspace-guide.md` (the
template's CLAUDE.md: guardrails, FormKey discipline, the pinned Spriggit version and why) and
`readme.md` (setup, round-trip workflow, CI). `skills/` and `agents/` are the Claude Code helpers
each repo ships; they double as step-by-step procedure docs for every tool in the chain.

## `docs/skyrim/` — the Skyrim SE engine and world

`reference/skyrim-record-patterns.md` is the single most valuable read before authoring any
mechanic: record shapes that build cleanly and still do nothing in-game. `reference/engine-behaviour.md`
covers encounter-zone clamping, level scaling and leveled-list selection with per-claim
confidence marks. `world/` is a census of vanilla Skyrim from the serialized plugins: every
dungeon by hold, enemy archetypes and their scaling, factions, regions, progression gates, and the
lore constraints with UESP citations.

## `docs/enderal/` — the Enderal SE engine

Read `reference/plugin-architecture.md` first. Enderal's `Skyrim.esm` is not Bethesda's file; it
is the base Enderal game, and most Skyrim modding intuition breaks on that fact. The rest of
`reference/` covers progression and classes, combat, crafting and economy, repurposed
ActorValues and scripting, visuals and worldspaces, factions, the bestiary and the dungeon census.
`reference/enderal-record-patterns.md` is the Enderal counterpart of the Skyrim record-patterns
guide. `tooling/spid-in-enderal.md` explains what SPID distribution silently loses under Enderal.

## `docs/tooling/` — cross-game tools

`spid.md` is a reference for SPID (Spell Perk Item Distributor) rebuilt from upstream source,
correcting errors in the published documentation.

## `docs/mods/` — third-party mods

- `ego/` — Enderal Gameplay Overhaul: plugin anatomy, combat, magic, crafting, NPCs and loot, its
  scripts, and `patching-ego.md`, the practical guide for any patch that touches a record EGO
  overrides. `conflict-index.md` and `new-records.md` are generated lookup tables.
- `requiem/` — how Requiem deleveled Skyrim, its Reqtificator patcher and Bash tags; written as
  prior art for Ehlnofey.
- `skypatcher/`, `morrowloot/` — distribution-INI semantics and encounter-zone clamping, again as
  prior art.

## `docs/projects/` — my mods

One folder per repo. Each has `workspace-guide.md` (that repo's CLAUDE.md: architecture,
FormKey allocations, hard-won gotchas) and `readme.md`.

- `ehlnofey/` — a Skyrim deleveling overhaul. `design/` holds the tier ladder, the difficulty map
  of every encounter zone, archetype rosters, the loot model and the probe test protocol.
- `wintersun-nordic-addon/` — new deities for Wintersun; all of its design knowledge is in the
  workspace guide.
- `enderal-mods/` — Enderal ports of Apocalypse and Triumvirate plus smaller mods; `apocalypse/`
  and `triumvirate/` hold the gap audits, naming tables, vendor mappings and test matrices.

## `docs/modlists/zenderal/` — the Zenderal modlist

Curation notes for the Enderal modlist (bug fixes, modern combat, modern visuals), controller
setup, the CI build report, and `magic/`, a generated dataset of every magic record in the
installed list with its load-order-winning values.

## Reading the frontmatter

Every document opens with a metadata block. The fields that matter when judging what you are
reading: `generated` (a machine-made table, not prose), `superseded` (replaced; `superseded_by`
names the replacement), `confidence` (how many `[verified]` versus `[unverified]` marks the text
carries), and `source_branch` (the knowledge base reflects whatever branch the source repo had
checked out). See `glossary.md` for the vocabulary.
