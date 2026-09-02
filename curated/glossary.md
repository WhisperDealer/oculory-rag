---
id: "curated/glossary"
title: "Glossary — modding and knowledge-base vocabulary"
section: "curated"
game: "both"
kind: "curated"
tags: ["glossary", "terminology"]
---

# Glossary — modding and knowledge-base vocabulary

## Plugins and records

| Term | Meaning |
|---|---|
| Plugin (`.esp` / `.esm` / `.esl`) | A Bethesda data file holding records. `.esm` is a master, `.esp` a normal plugin, `.esl` a light plugin. |
| ESL / ESL-flagged / `Small` | A light plugin sharing one load-order slot with other light plugins. Its own FormIDs are limited to `0x800`–`0xFFF`. |
| Master | A plugin another plugin depends on. Records from a master are referenced by FormKey. |
| FormID | The 24-bit (or 12-bit for ESL) identifier of a record within its defining plugin, written as hex. |
| FormKey | Spriggit/Mutagen's plugin-independent record identity: `<FormID>:<Plugin>`, e.g. `013989:Skyrim.esm`. |
| ModKey | The plugin filename part of a FormKey. |
| EditorID | The human-readable name of a record as set in the Creation Kit. |
| Override | A record in one plugin that replaces a record defined by an earlier plugin; the last loaded wins. |
| Injected record | A record whose FormID belongs to a master that does not itself define it. |
| Record pattern / archetype | A record shape known to work in-game. The record-patterns docs list ones that build cleanly and still do nothing. |
| LVLI / LVLN / LVSP | Leveled item, NPC and spell lists: tables that pick an entry based on player level. |
| Encounter zone (ECZN) | The record that clamps an area's level range. Deleveling mods live here. |
| Bash tags | Flags telling Wrye Bash which record fields a plugin wants merged into a bashed patch. |

## Tools and formats

| Term | Meaning |
|---|---|
| Spriggit | Converts plugins to and from YAML so they can be version-controlled. Pinned at 0.40.0 in the workspaces. |
| Mutagen | The .NET library Spriggit is built on; also used by the MagicExtract tool. |
| Creation Kit (CK) | Bethesda's editor, also the source of `PapyrusCompiler.exe`. |
| xEdit / SSEEdit | The community plugin editor used to verify built plugins and inspect conflicts. |
| Papyrus / `.psc` / `.pex` | The scripting language, its source files and compiled bytecode. |
| Champollion | Decompiles `.pex` back to `.psc` (a reconstruction, not the original). |
| BSA / BA2 | Bethesda archive formats. `bsab.exe` extracts them. |
| MO2 | Mod Organizer 2, the mod manager the modlists run under. |
| Wabbajack | Installs a complete MO2 modlist (game copy, mods, tools) from a `.wabbajack` file. |
| FOMOD | An installer manifest inside a mod archive giving the user options. |
| SPID | Spell Perk Item Distributor: distributes spells, perks, items and keywords to NPCs from `_DISTR.ini` files. |
| SkyPatcher | Runtime patcher driven by INI rules, an alternative to plugin overrides. |
| Reqtificator | Requiem's C# patcher that builds its leveled lists and NPC records at install time. |

## Games, mods and projects

| Term | Meaning |
|---|---|
| Skyrim SE | Skyrim Special Edition, the base game for the Skyrim repos. |
| Enderal SE / Forgotten Stories | SureAI's total conversion. Its `Skyrim.esm` is a wholesale replacement, not Bethesda's file. |
| EGO | Enderal SE - Gameplay Overhaul, the community overhaul most Enderal lists build on. |
| Zenderal | My Enderal modlist: bug fixes, modern combat, modern visuals. `zenderal-patches` holds its patches. |
| Requiem | A Skyrim deleveling overhaul; prior art for Ehlnofey. |
| MorrowLoot (Ultimate) | Skyrim loot and encounter-zone overhaul; prior art for Ehlnofey. |
| Wintersun | Wintersun - Faiths of Skyrim (Enai Siaion), the religion framework the Nordic addon extends. |
| Apocalypse / Triumvirate | Enai Siaion spell packs ported to Enderal in `enderal-mods`. |
| Ehlnofey | My Skyrim deleveling overhaul: difficulty and reward belong to places, not player level. |
| Oculory | The Spriggit workspace template every mod repo is cloned from. |

## Knowledge-base vocabulary

| Term | Meaning |
|---|---|
| Source repo | One of the five git repos the sync reads; canonical for its documents. |
| Mapping | A `sources.json` entry routing source files to a destination folder with metadata. |
| `id` | A document's destination path without `docs/` and `.md`; the stable key for Confluence and RAG. |
| `section` | The folder part of the id; the Confluence ancestor chain and the RAG filter. |
| `kind` | `reference` (how the game is), `world` (vanilla survey), `research` (prior art), `design` (my decisions), `guide` (workspace guides and READMEs), `workspace` (skills, agents), `modlist`, `curated`. |
| `generated` | A machine-made document; regenerate from its `generator`, never edit. |
| `superseded` | Replaced by the document named in `superseded_by`; kept for history. |
| `[verified]` | Measured or read from serialized data on this machine. |
| `[community]` | Established modding knowledge, not re-tested here. |
| `[unverified]` | Plausible, unchecked. |
| `[upstream]` | Taken from tool or game source code. |
| `[author]` | A mod author's own claim; not the same as measured. |
