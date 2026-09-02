---
id: "projects/ehlnofey/workspace-guide"
title: "Ehlnofey — Workspace Guide"
slug: "workspace-guide"
section: "projects/ehlnofey"
game: "skyrim"
kind: "guide"
project: "ehlnofey"
mod: null
tags: ["ehlnofey", "deleveling", "claude-md", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "CLAUDE.md"
source_branch: "main"
source_commit: "bc9623d5ea6a587b6cfba9f63ab13266161490dd"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 8, "unverified": 1, "upstream": 0, "verified": 37}
lines: 755
content_sha256: "299078fdc80b91194976c0c7a77ab6d43d98d0d91787321af21a8083fcde08a7"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Ehlnofey — Workspace Guide

> **This file is the most valuable thing in the repo.** It is what a future session reads instead of
> re-deriving your conventions from scratch. When you learn something the hard way — a FormID
> allocation, a record shape that didn't work, a compile import you needed — write it here.
>
> Everything above *[The mod](#the-mod-ehlnofey)* is generic workspace mechanics. Everything below it
> is Ehlnofey: what we are building, what phase we are in, and where the research lives.

## What this is

**Ehlnofey** is a **deleveling overhaul for SkyrimSE** — it replaces vanilla's player-level scaling
with fixed, hand-set rules so that difficulty and reward belong to *places*, not to the player's
level. See [The mod](#the-mod-ehlnofey) for the design thesis and current phase.

The repo it lives in is a Spriggit YAML workspace: plugins are decompiled to YAML, edited as text,
and re-packed to `.esp`/`.esm`. **Never hand-edit binary plugins — edit the YAML.**

- Spriggit package/source: `Spriggit.Yaml.Skyrim`
- Spriggit CLI version: `0.40.0`
- CLI path + all tool paths: `.claude/config/tools.json` (gitignored; see Tooling config below).

## Tooling config (no hardcoded paths)

All tool paths and per-machine settings live in **`.claude/config/tools.json`** (gitignored;
template at `tools.example.json`). Skills load it via `.claude/config/tools.ps1`, which exposes
`$Tools` (e.g. `$Tools.spriggitCli`, `$Tools.papyrusCompiler`, `$Tools.creationKit`,
`$Tools.gameSourceScripts`) and an `Assert-Tool` guard. **Never reintroduce a hardcoded path into a
skill — change the config instead.**

- **Modlists:** a Wabbajack `.wabbajack` list installs a full MO2 instance (game copy + mods +
  tools, often the **Creation Kit** and Papyrus compiler) that can be hundreds of GB. It is
  gitignored (`/modlist/`, `/downloads/`). Run the **`modlist-install`** skill to install one and
  auto-discover its tool paths into `tools.json`.
- Without a modlist, fill `tools.json` by hand from `tools.example.json`.

## Workflow (round-trip)

```
.esp/.esm  ──serialize──►  YAML (committed)  ──deserialize──►  .esp/.esm
                 ▲                                                  │
                 └──────────── you edit the YAML ◄──────────────────┘
```

Serialize/deserialize commands: see `README.md`. After editing YAML, deserialize and load the plugin
in xEdit/CK to verify before shipping.

## Folder map

```
src/                       # EVERY mod lives here — one folder per mod, add as many as you like
  <ModName>/
    <ModName>ESP/          # Spriggit YAML — COMMITTED, source of truth
    Scripts/source/*.psc   # Papyrus source — COMMITTED
    Scripts/compiled/*.pex # COMMITTED via a .gitignore exception (CI can't compile Papyrus)
build/                     # build.ps1 + manifest.json + committed FOMOD trees
arch-docs/                 # world research + design spec + record-pattern guide (see arch-docs map)
reference/                 # gitignored — vanilla/third-party decompiles, LOOKUP ONLY
                           #   Base/       Skyrim.esm, Update.esm and the 3 DLCs: Phase 1's evidence
                           #   mods/       third-party mods as downloaded (Requiem/ …)
                           #   mods/*Yaml/ Spriggit decompiles of them (RequiemYaml/ = 108 MB)
modlist/                   # gitignored — an installed MO2 instance, hundreds of GB
```

`src/` is the only place mod content goes. A repo can hold several mods side by side — a main
plugin and its compatibility patches, say — each its own `src/<ModName>/` folder with its own
`build/manifest.json` release entry. Only `src/`, `build/`, `arch-docs/`, `.claude/` and the root
configs are committed.

## Guardrails — how to work in this repo

These are distilled from real failures in this workspace's lineage. They cost test cycles to learn.

1. **Ground-truth before claiming.** Do not conclude a patch is or isn't needed, or that a record
   does what its name suggests, from the name alone. Read the serialized record, trace the
   FormKeys, and **show the evidence alongside the verdict**. If a mechanic depends on a third-party
   mod's compiled script, read that script's decompiled source — data-driven parts extend to your
   records, hardcoded index checks do not.
2. **Prefer a proven archetype to an invented mechanism.** Read
   `arch-docs/skyrim-record-patterns.md` first. Skyrim fails silently: an inert record produces no
   error, so an invented mechanism costs a full build-deploy-launch-test cycle to disprove.
3. **Copy records verbatim; never retype hex.** When basing a record on an existing one, copy the
   file and edit the fields that differ. Hand-transcribing `Data:` blobs has produced odd-length hex
   that fails the build, and dropped array entries that fail silently. Prefer a script over
   retyping. Re-check array lengths after any edit.
4. **Ask for paths; don't hunt for them.** Install locations, modlist names, MO2 folders and mod
   names live in `tools.json` or in the user's head. Read the config or ask — filesystem-searching
   for them wastes time and lands on the wrong candidate.
5. **Verify the deploy target before blaming the records.** A mod in a wrongly-named MO2 folder is
   invisible; the game runs fine and the change simply isn't there. The `mod-deploy` skill checks
   this. Rule out "never loaded" before debugging "loaded but broken".
6. **A clean build is not a working mod.** Deserialize, xEdit and the Papyrus compiler all passing
   proves it *builds*. Only launching the game proves it *runs*. Say which of the two you have
   actually established.
7. **Recompile and re-commit `.pex` whenever a `.psc` changes.** CI cannot run the Creation Kit
   compiler. `build/build.ps1` fails on a *missing* `.pex` but cannot detect a *stale* one.
8. **PowerShell 5.1 is the target** for build scripts and skills: `Set-StrictMode` is on, there is
   no `&&`/`||`, no ternary, no null-coalescing, and no built-in YAML parser. Write `-Encoding utf8`
   explicitly when a file will be read by other tools.

## FormKey discipline

- New records use this plugin's name as the FormKey suffix: `<hex>:<YourMod>.esp`.
  Records that **override** a base/third-party record keep the original suffix
  (e.g. `09BC43:Skyrim.esm`) — that is how you tell at a glance which records you invented.
- **ESL (`Small`) plugins are constrained to FormIDs `0x800–0xFFF`.** Confirm with the user before
  exceeding; there is headroom but it is finite.
- Allocate a **contiguous block per feature** for readable diffs.
- ALWAYS grep the whole workspace (your plugin folders + `reference/`) for a hex FormID before
  assigning it — use the `formkey-check` skill.

## Papyrus toolchain

Scripts go through extract → decompile → edit → compile → package. Use the matching skills; the
`papyrus-script-engineer` subagent handles decompiled-source cleanup and compile-error fixing.

**Tool paths:** all resolved from `.claude/config/tools.json` — do not hardcode.

| Step | Tool | Config key |
|------|------|------------|
| Extract `.bsa`/`.ba2` | `bsab.exe` | `$Tools.bsab` |
| Decompile `.pex`→`.psc` | `Champollion.exe` | `$Tools.champollion` |
| Compile `.psc`→`.pex` | `PapyrusCompiler.exe` | `$Tools.papyrusCompiler` |
| Open Creation Kit | `CreationKit.exe` | `$Tools.creationKit` |

**Compiler imports:** base-game source = `$Tools.gameSourceScripts` (extract
`<gameDataDir>/Scripts.zip` once, or use what the modlist ships). Flags file: `$Tools.papyrusFlags`.

**Per-project import dirs** — persist in `tools.json`'s `importDirs` array (the `papyrus-compile`
skill appends them to `-i`). Record each one here as you discover it:

| API / framework | Source `.psc` dir |
|-----------------|-------------------|
| _(base only)_ | Nothing in Ehlnofey compiles against anything but base-game source yet. Add SKSE/SkyUI/MCM/PapyrusUtil dirs here the first time a script needs them. |

**Testing:** MO2 modlists under `$Tools.modlistsRoot`, or a Wabbajack instance at
`$Tools.modlistRoot`. Use the `mod-deploy` skill rather than copying by hand.

## Workspace gotchas

- **FOMOD images that actually render in MO2** — a config can build clean, pass
  `build.ps1 -CheckFomod`, open its wizard normally, and still show *no image at all*. Nothing
  warns you. This recipe is confirmed working in MO2. **There is no longer a worked example in this
  repo** — it went with `ExampleMod`; the live copy is `build/fomod-example/` in the `claudemoddev`
  template workspace. Follow the four points below rather than re-deriving:
  1. `path=` is relative to the **archive root**, so an image at `fomod/images/foo.jpg` is
     referenced as `path="fomod\images\foo.jpg"` — *including* the `fomod` prefix.
  2. Use **backslashes** in `path=`, as the shipped configs do.
  3. Declare an `<installSteps>` block, even for a mod with no real choices (one
     `SelectExactlyOne` group holding a single `Recommended` plugin). A config with only
     `<requiredInstallFiles>` gives MO2 no wizard page to draw the banner on.
  4. Use a **baseline** JPEG or a PNG, not a progressive JPEG. Check with
     `od -A d -t x1 -v img.jpg | grep -oE 'ff c[0-9a-f]'`: `ff c0` is baseline (fine), `ff c2` is
     progressive. Re-encode progressive files via `System.Drawing` before shipping.

  These four were fixed **together** after several one-at-a-time attempts each failed, so which is
  individually decisive is unverified — treat the set as the known-good recipe, and do not drop one
  on the assumption it does not matter.

  `build/build.ps1 -CheckFomod` now enforces points 1, 2 and 4: an unresolvable `path=` or a
  progressive JPEG **fails** the check (with a "did you mean `fomod\…`?" hint for the missing
  prefix), and forward slashes warn. It cannot check point 3 — whether an `<installSteps>` block
  exists at all — because a config legitimately may not want one.
- **Decompiled `.psc` is a reconstruction** (Champollion): auto-named vars, reconstructed control
  flow, lost comments/flags. Always recompile and test in-game; a clean compile is not proof.
- **Missing-type compile errors** → the referenced API's source isn't on the import path; add its
  `Source\Scripts` dir to `importDirs` in `tools.json` and record it in the imports table above.
- **YAML comments do not survive a re-serialize.** Spriggit rewrites the folder from the binary
  plugin, so any `#` comment you add to a record file is lost the next time anyone runs
  `/spriggit-serialize`. Put durable explanation in this file, not in the record YAML.
- Edit `.psc`/YAML, never the binary `.pex`/`.esp`. Commit source, not build artifacts.
- See `arch-docs/skyrim-record-patterns.md` for the in-game failure modes that produce no build
  error — that list is the single highest-value read before authoring a new mechanic.

---

# The mod: Ehlnofey

## The idea, and the name

**Ehlnofey delevels Skyrim.** Vanilla scales the world to the player: bandits, draugr and loot are
generated relative to your level, so a dungeon cleared at level 5 is the same fight at level 40 and
the map has no topography of danger. Ehlnofey replaces that with **fixed, hand-set rules** — every
enemy, dungeon and hoard has a level and a loot profile that does not move — aiming at an
*immersive, lore-friendly and gameplay-optimised* result rather than a difficulty-slider mod.

The name is the thesis. The Ehlnofey were et'Ada who stopped wandering: instead of remaining free,
mutable spirits, they bound themselves into the substance of Nirn and became its fixed laws — the
Earth Bones, the unchanging structure under everything. That is exactly the operation this mod
performs on Skyrim: it takes a world that bends to the player and re-imprints static, indifferent
rules onto it. Docs and record names lean on that vocabulary (**bones** = the fixed structure).

## The three bones (design rules)

Every design decision has to answer to these. If a proposal violates one, it needs an explicit
exception recorded in `arch-docs/design/`, not a quiet pass.

1. **The world does not scale.** Difficulty and reward are properties of a place and a creature, set
   once. Nothing recalculates against the player's level.
2. **Danger is legible.** If the player can be killed by walking somewhere, the world must have told
   them first — geography, lore, faction, visual tier, NPC dialogue, quest gating. A fixed world is
   only fair if it can be read.
   > **This is the load-bearing bone.** `progression.md` found that vanilla gates content by level
   > essentially nowhere (30 conditions across 1,811 quests, none on any questline) and that 20 gold
   > buys a carriage ride to any hold capital from minute one. Legibility is not a nice-to-have — it
   > is the *only* protection a player has once the world stops scaling.
   > **The mechanism already exists: tier display names.** Draugr → Restless Draugr → Wight → Scourge
   > → Deathlord; Dremora Churl → Caitiff → Kynval → Kynreeve → Markynaz → Valkynaz. These are
   > lore-ordered, player-facing, and map 1:1 onto the level ladders. Keeping name aligned with power
   > is a hard constraint — see `lore-constraints.md`.
3. **Reward follows place, not level.** Good loot exists because of *where* it is (a Nordic tomb, a
   Dwemer ruin, a dragon's hoard, a named boss), never because the player happened to be level 40.

**Non-goals** (keep scope honest): not a combat overhaul, not a perk/skill overhaul, not a survival
mod, not a new-content mod. Ehlnofey changes *where the numbers come from*, and nothing else.

## Current phase

**Phase 4 is under way and `Ehlnofey.esp` exists: 2,877 records** (2026-07-31, branch
`design/requiem-method`). Read **`arch-docs/design/requiem-method.md` first** — it is the live
architecture doc, and its §6 is the current order of work. Everything below it in this section is
the Phase 3 record, kept because most of it still holds, but **the architecture it decided has been
replaced.**

**What changed.** Encounter zones govern only 0.3% of the outdoors and cannot reach worn gear, so the
zone-first hybrid could not deliver bone 1. The mod pivoted to **Requiem's method** — flatten the
`LVLN`/`LVLI` gate, keep the pool, fix `PcLevelMult` NPCs — and then to the cheapest possible way of
getting it: **extract Requiem's deleveling layer directly.** Requiem's flat records are
overwhelmingly built from vanilla FormKeys only, and an override keeps its defining master's FormKey
suffix, so most of the job is a file copy. `src/Ehlnofey/extract-requiem.ps1` is the generator.

| | | |
|---|---:|---|
| A copied verbatim | 1,896 | `LVLN`/`LVLI`, every FormKey one of our four masters |
| B stripped | 173 | `LVLI` minus their Requiem-only gear entries |
| C vanilla flatten | 259 | not covered by Requiem, or emptied by B |
| D authored | 64 | the `LCharBandit*` ladder + the biome rosters, from `archetype-tiers.md` (+9 dropped as already-flat) |
| E level graft | 434 | vanilla `NPC_` record + Requiem's `Configuration.Level`, nothing else |

Every entry in every leveled list is now `Level: 1` or the `9999` disable sentinel. Builds clean,
`Test-RecordYaml.ps1` passes 2,878 files, round-trip is byte-stable, **zero new FormIDs**, masters
exactly Skyrim/Update/Dawnguard/Dragonborn. It **has** been launched, and **Bleak Falls Barrow and
Swindler's Den both give a consistent spread of enemy types at player level 1 and 45** — the first
real evidence bone 1 holds in play. Boss-chest loot is still unverified (guardrail 6).

**The first play report found a design bug, not a build bug** (2026-07-30): a band of levels is only
legible if its rungs have *different names*, and the bandit boss ladder's do not. See
`archetype-tiers.md` §3.1.1 for the naming test — **four boss families still fail it** (Forsworn,
Warlock, Thalmor, Vampire) and are an open decision.

**Generators, and the order they must run in:** `author-constants.ps1` → `extract-requiem.ps1` →
`author-bucket-d.ps1` → `author-names.ps1`, then deserialize → re-serialize → adopt Spriggit's output as the source.

**Owed next:** the launch verification proper (draugr tier and boss-chest loot fixed across two
player levels), then the 65 follower + 114 unreached `PcLevelMult` NPCs.

**Licensing:** verbatim-copied records make the plugin a derivative of Requiem. Private use is fine;
publishing needs their permission.

---

The four decisions Phase 3 was convened to make (**the architecture row is superseded**):

| Decision | Verdict |
|---|---|
| **The ladder** | **T1–T7 = 4 / 8 / 14 / 21 / 30 / 40 / 50**, written as `MinLevel == MaxLevel` (zero-width everywhere, no banded exceptions) |
| **The map** | all **355 zones** assigned, generated from rules, in `difficulty-map.md` §7 |
| **Loot** | no truncation pass needed — the tier ladder *is* the vanilla material ladder |
| **Architecture** | **hybrid: places and constants in the plugin, actors in rules** (see below) |

**Scope:** Skyrim + Dawnguard + Dragonborn. Hearthfire excluded (adds no zone, no dungeon, no region).

Three findings worth carrying, each of which overturned something the repo previously recorded:

1. **Vanilla's zone floors must be stretched, not ratified.** 73% of Skyrim's 280 zones sit at level
   ≤ 8 and nothing exceeds 24, while the content ladders run to 46–60 — freezing vanilla's numbers
   would make every rung above ~25 dead content. MLU independently agrees (its zones run 5–64).
   This **supersedes `dungeons.md` §5.1's "ratify the vanilla ladder" recommendation**, which
   predates the clamp research.
2. **The tier ladder lands exactly on the vanilla gear ladder** — T1–T7 select Steel / Orcish /
   Dwarven / Elven / Glass / Ebony / Daedric, one rung each. Bone 3 therefore falls out of the
   difficulty map, and **MLU's 400-list truncation pass is unnecessary**. Daedric ends up reachable in
   ~2 places, both apex, without editing a single list.
3. **No new records are needed.** The whole mod is overrides, so FormID usage stays at zero and
   ESL-flagging is free. **Still true after the pivot** — the extract added 2,877 records and every
   one is an override; the planned wilderness `ECZN` belonged to the replaced architecture.

**Three cheap in-game tests still gate Phase 4** (`implementation-strategy.md` §7) — run them before
authoring: `LevelModifier: None`, NPC gear resolution level, and zeroing
`fSpecialLootMinPCLevelMult`. The instrument (`EhlnofeyProbe.esp`) and the script are in
`design/probe-test-protocol.md`. **Run gear resolution first** — since §7.1 it is the only one that
can still move a large amount of work (up to 1,378 `LVLI`); the `LevelModifier` test's exposure
turned out to be 9 records, not ~1,928.

`src/` holds exactly one mod, **`src/Ehlnofey/`** — the 2,877-record plugin plus its four generator
scripts, `author-constants.ps1` (the 13 constants) and `extract-requiem.ps1` (everything else).
`ExampleMod` and `EhlnofeyProbe` were deleted, and `build/staging/Example Mod/fomod/` went with them
— the confirmed-working FOMOD image recipe now lives only in the gotcha above and in the
`claudemoddev` template workspace. **`Ehlnofey` itself ships no FOMOD**: it is one `.esp` with
nothing to choose, so its release carries `"fomod": false` and packs a plain archive. `reference/` holds
Spriggit decompiles of `Skyrim.esm`, `Update.esm` and all three DLCs — Phase 1's evidence — plus
third-party mods under `reference/mods/` as Phase 2 reads them. **`reference/` is a build input**,
not only a lookup: `extract-requiem.ps1` reads both `reference/Base/` and
`reference/mods/RequiemYaml/` to regenerate the plugin, and
`arch-docs/design/build-difficulty-map.py` regenerates the difficulty map from it.

**Phase 2 is complete.** Three subjects were read: **Requiem** (`prior-art/requiem/`),
**MorrowLoot Ultimate** (`prior-art/morrowloot.md`) and **SkyPatcher** (`prior-art/skypatcher.md`).

Three further candidates were **deliberately dropped** — do not re-add them:

| Dropped | Why |
|---|---|
| Open World Loot | Uses the same method as MorrowLoot Ultimate; `morrowloot.md` already covers it |
| SPID | A distributor, not a record patcher — not a good fit for deleveling |
| Synthesis patchers | Not an option for this mod (see implementation strategy) |

**SkyPatcher resolved the option-B question:** it can express the deleveling core of *either*
architecture below as INI rules with **zero plugin overrides** — flatten lists (`clear` +
`addToLLs`), fix NPC levels (`filterByPCLevelMult` + `level`), band encounter zones
(`minLevel`/`maxLevel`). It **cannot** reach `GMST`s or placed-actor `LevelModifier`, and cannot
filter zones by location keyword. **That points hard at the hybrid**: rules for the distribution, a
tiny plugin for the handful of GMSTs and any new records.

The two reads together defined the **central fork**. **Phase 3 resolved it in MLU's direction and
went further**: Ehlnofey clamps `ECZN` bands (MLU's lever) but at *zero* width, keeps the vanilla
scaling machinery, and edits **no** leveled item lists at all — so it needs neither MLU's truncation
pass nor Requiem's bespoke patcher. The table is kept for context:

| | Requiem | MorrowLoot Ultimate |
|---|---|---|
| Lever | **flatten `LVLN` gates** (100% of 328) | **clamp `ECZN` bands** (324 of 360) |
| Difficulty lives on | the actor record | **the place** |
| Vanilla scaling machinery | deleted | kept, constrained |
| Compatibility | bespoke patcher | **Wrye Bash `Delev`/`Relev`** |
| Repo cost | 108 MB / 26,620 records | **22 MB / 4,751 records** |

Neither actually achieves bone 1: Requiem leaves followers and 114 NPCs scaling; MLU only *narrows*
ranges (a `[38–53]` band still moves with the player). ~~`MinLevel == MaxLevel` is un-taken prior
art~~ — **wrong, and now researched**: MLU itself ships three `Min == Max` zones (ColdRockPass
22–22, ShrineofBoethiah 30–30, its own new `MLU_MQ301` 40–40), and the `[38–53]`-still-moves
problem has a mechanical explanation — zones govern leveled-*list* selection but `PcLevelMult`
actors ignore them entirely. **The five gating engine questions are answered in
`arch-docs/design/engine-behaviour.md`** (2026-07-28). **Ehlnofey's answer to "neither achieves bone
1" is the split in `implementation-strategy.md`**: zero-width zones fix the places, and SkyPatcher
`filterByPCLevelMult` rules fix the actors zones structurally cannot reach.

## Phase plan

| Phase | Output | Done when |
|---|---|---|
| **0 — Workspace** | Spriggit round-trip, skills, CI, base+DLC decompiles in `reference/` | ✅ complete |
| **1 — World research** | `arch-docs/world/*` — enemy taxonomy, factions, dungeons, regions, progression, lore constraints, DLC deltas | Every hostile archetype and every dungeon is in a table with its vanilla scaling behaviour cited from `reference/` |
| **2 — Prior art & method** | `arch-docs/prior-art/*` — how Requiem, MorrowLoot Ultimate and SkyPatcher actually do it | ✅ complete — each has a verified mechanism, a cost, and a compatibility verdict |
| **3 — Design spec** | `arch-docs/design/*` — tier system, region difficulty map, loot model, and the **implementation-strategy decision** | ✅ complete — 5 documents; all 355 zones assigned; architecture decided |
| **4 — Build** | `src/Ehlnofey/` — plugin YAML, any scripts/rule files, release | Deserializes clean, opens clean in xEdit, **and has been launched in-game** |

Phases 1–3 are documentation work. **Do not start authoring records in `src/` before Phase 3 has a
written spec** — the whole point of the arch-docs is that a deleveling pass touches thousands of
records and reversing a bad taxonomy afterwards is far more expensive than deciding it on paper.

## arch-docs map

Research and design live here; this file stays the index. Create these as the phases produce them.

```
arch-docs/
  skyrim-record-patterns.md      # EXISTS — read before authoring any mechanic
  summary/                       # EXISTS — talk material for people who won't read design/.
                                 #   build-deck.py generates ehlnofey-tier-ladders.pptx (16 slides,
                                 #   assumes zero modding knowledge). Needs python-pptx, which is
                                 #   NOT part of the plugin toolchain — use a throwaway venv.
                                 #   Target renderer is LibreOffice Impress; see its README for the
                                 #   layout traps and the soffice render-check.
  world/
    overview.md                  # EXISTS — bird's-eye census of the base game; read this first
    enemy-taxonomy.md            # EXISTS — every hostile archetype, its ladder, its scaling class
    unique-enemies.md            # EXISTS — named bosses + unique enemy races, base game + DLC
    factions.md                  # EXISTS — combat factions, membership counts, relation graph, filter viability
    dungeons.md                  # EXISTS — all 226 dungeons by hold: type, zone, level, boss, word wall
    regions.md                   # EXISTS — the nine holds: map position, composition, the real gradient
    progression.md               # EXISTS — routes, level gates (almost none), the carriage problem
    lore-constraints.md          # EXISTS — what the fiction permits; tier names ARE the lore hierarchy
    dlc-deltas.md                # Dawnguard / Hearthfire / Dragonborn additions and their zones
                                 #   (DLC coverage currently lives inline: taxonomy §2.7, dungeons §3,
                                 #    factions §6, regions §4 — consolidate here if it outgrows them)
  prior-art/
    requiem/                     # EXISTS — README + plugin-analysis + reqtificator + bash-tags
                                 #   + lessons-for-ehlnofey. Read the README first.
    morrowloot.md                # EXISTS — the ECZN-clamp approach; §7 is the Requiem/MLU table
    skypatcher.md                # EXISTS — INI rule syntax; §3.1 filter semantics (filterBy* is a
                                 #   UNION, restrictTo* narrows), §3.4 docs-vs-parser bugs, §5 limits
    enderal.md                   # EXISTS — the total-conversion pole: 0 LVLN, 0 PcLevelMult,
                                 #   0 LevelModifier, 2 ECZN. Existence proof for bone 1 and the
                                 #   third zone data point. §9 = why the METHOD IS NOT USABLE here
                                 #   (Enderal replaced the master; Ehlnofey patches it). Its
                                 #   decompiles were deleted after the read — §"Reproducing the
                                 #   evidence" regenerates them if ever needed again.
    # ^ Phase 2 is CLOSED. Open World Loot, SPID and Synthesis were dropped on
    #   purpose — see "Current phase". Do not add files here without a reason.
    #   enderal.md was added later on request: a total conversion, not a 4th candidate method.
  design/
    requiem-method.md            # EXISTS — READ FIRST. THE live architecture: the pivot away from
                                 #   encounter zones, the four Ehlnofey twists, and 6 = the current
                                 #   order of work. Supersedes implementation-strategy.md 1.
    archetype-tiers.md           # EXISTS — the archetype tier table + the 19 biome rosters. 4/4.1
                                 #   is what bucket D of the extract still has to be authored from.
    bucket-d-provisional.txt     # GENERATED — the 66 LVLN the extract could not copy and left as a
                                 #   naive vanilla flatten. Regenerated by extract-requiem.ps1.
    lvli-reachability.ps1        # EXISTS — plus roster-census / leveled-list-census / lvli-fork-*
                                 #   / biome-rosters .ps1: the evidence scripts behind 5 and 4.1.
    engine-behaviour.md          # EXISTS — the five gating engine questions, answered with sources
                                 #   (ECZN clamp scope, Min==Max, loot, LevelModifier, SkyPatcher
                                 #    timing/saves). Read before tiers/difficulty-map/implementation.
    tiers.md                     # EXISTS — the T1–T7 ladder (4/8/14/21/30/40/50), the LevelModifier
                                 #   GMST decision, archetype home bands, class-D fixed levels, and
                                 #   the bone-1 exception verdicts. Read before difficulty-map/loot.
    difficulty-map.md            # EXISTS — all 355 zones assigned T1–T7, generated. The rules are
                                 #   type→tier + word-wall bump + region floor/ceiling + 44 explicit.
    build-difficulty-map.py      # EXISTS — regenerates difficulty-map.md §7 from reference/.
                                 #   Change the seven numbers in TIER and re-run to recalibrate.
    loot-model.md                # EXISTS — the tier ladder IS the material ladder; no truncation pass
                                 #   needed. One GMST. Hinges on the gear-resolution test.
    implementation-strategy.md   # EXISTS — THE decision, now made. See below.
    probe-test-protocol.md       # EXISTS — the instrument + script for the three gating in-game
                                 #   tests (§9 step 1). §4 holds a census that CUTS the
                                 #   LevelModifier:None exposure from ~1,928 refs to 9.
```

## Research rules (Phases 1–3)

The repo's guardrails apply with extra force here, because deleveling research is exactly where
plausible-sounding claims are cheapest to make and most expensive to act on:

- **Cite `reference/`, not memory.** A claim like "bandits use a level multiplier" must name the
  record and the field as serialized: `reference/Base/01Skyrim/…`. Grep the decompile; quote it.
- **Mark confidence** the same way `skyrim-record-patterns.md` does: `[verified]` = read in
  `reference/` or observed in-game here; `[community]` = established modding knowledge, not re-tested;
  `[unverified]` = plausible, needs checking. Never silently upgrade a mark.
- **Prior art gets read, not recalled.** Before writing that a mod "does X", read its plugin (via
  `/spriggit-decompile-reference` into `reference/mods/`), its INIs, or its documentation. Third-party
  behaviour that lives in a compiled script or SKSE DLL is not knowable from the record data alone.
- **Follow the template chain before concluding.** A leveled spawn's stats can come from an actor
  template rather than the NPC record you are looking at, so "this NPC is level 6" is a claim about
  whichever record actually owns the level. Trace it.

## The vanilla scaling machinery

The levers a deleveling mod has to touch. Field names below are concepts — **confirm the exact
Mutagen/Spriggit field name in `reference/` before writing YAML**, and record the confirmed name here.

| Mechanism | Record type | Why it matters to Ehlnofey |
|---|---|---|
| Static vs. player-relative level | `NPC_` (level is either a fixed number or a PC-level multiplier with calc-min/calc-max) | The core lever. "Delevel an NPC" mostly means replacing the multiplier with a fixed level. `[community]` |
| Actor templates | `NPC_` template + template flags | A spawn may inherit stats/traits from another record, so editing the visible NPC can do nothing. Trace before editing. `[community]` |
| Leveled actor lists | `LVLN` | Chooses which variant spawns, with per-entry level gates and chance-none. Deleveling means flattening or splitting these per tier. `[community]` |
| Leveled item lists | `LVLI` | The loot side of the same machinery — vanilla gates gear tiers by player level here. `[community]` |
| Encounter zones | `ECZN` | Per-location min/max level and flags. **Phase 2 verdict: viable, but only in one of two architectures.** A zone *clamps* the level the leveled-spawn machinery computes. Requiem flattened that machinery away, so its zones are inert (8 records, none for levels). MorrowLoot Ultimate kept it and clamped it — **360 zones, 324 with a real band** — making zones its entire difficulty map. **The `ECZN` and `LVLN` decisions are one decision.** See `arch-docs/prior-art/morrowloot.md` §1. `[verified]`. **Clamp semantics now researched** (`design/engine-behaviour.md`): the zone level is `clamp(playerLevel, min, max)` computed on first visit, **stored in the save, never recalculated** until zone reset; it governs leveled-list selection (and, per docs, loot lists) but **`PcLevelMult` actors ignore it** — they need per-NPC fixing. `[community]` |
| Placed-actor difficulty | `ACHR` / `PlacedNpc` field `LevelModifier` (`Easy`/`Medium`/`Hard`/`VeryHard`) | Vanilla's hand-tuning layer, on **5,685 of 10,504** placed actors (2,524 of 4,452 interior); the four values map to `fLeveledActorMult*` = 0.33/0.67/1/1.25. Keep it. **Prior art disagrees on the multipliers:** Requiem leaves them at vanilla; MLU uses **0.7 / 0.9 / 1.1 / 1.3** — note its Hard is **1.1, not 1.0**, so every Hard-tagged actor sits a notch above its zone's nominal level. **Decided in `design/tiers.md` §4: Ehlnofey uses 0.70 / 0.85 / 1.00 / 1.25** — two GMST overrides, keeping Hard = 1.0 so "a T5 zone is a level-30 zone" is exactly true. `[verified]` |
| Global knobs | `GMST` (level-scaling and difficulty multipliers) | Blunt but cheap; changes everything at once. Use deliberately, never as a substitute for tiering. `[community]` |
| Spawn gating by player level | 12 `LevelGate*` `GLOB` records (Spriggan 8 … Giant 24) | Vanilla's only systematic level gate — it withholds world-encounter *creatures* until the player is roughly their level. **This is a bone-1 violation that already exists**; delete or document as an exception. `[verified]` |
| Capability, not level | `PERK`, `SPEL`, `CSTY` (combat style) | A level-20 bandit's threat comes largely from perks/spells/AI. Deleveling levels without capability produces a flat, boring world. `[community]` |

## Implementation strategy — SUPERSEDED (Phase 3 record)

> ⚠️ **Replaced by `arch-docs/design/requiem-method.md`.** The shipped architecture is a
> **single plugin, no rules**: 2,877 override records extracted from Requiem's deleveling layer —
> flat `LVLN`/`LVLI` plus grafted `NPC_` levels. There are **no encounter-zone bands and no
> SkyPatcher rules** in it. Zones govern 0.3% of the outdoors and cannot reach worn gear, which is
> what killed the hybrid; and once every list is flat there is nothing left for a zone to clamp.
> The section below is kept for the reasoning, which is still worth reading, and because §§2.2–2.4,
> §4 and §8 of `implementation-strategy.md` survive intact.

**Verdict: a hybrid — places and constants in the plugin, actors in rules.** Full reasoning and the
record-by-record manifest are in `arch-docs/design/implementation-strategy.md`; this is the summary.

| Half | Contents | Size |
|---|---|---|
| **`Ehlnofey.esp`** | the **355 encounter-zone bands**, 3 `GMST`s, 12 `LevelGate*` `GLOB`s, 5 capstone bosses, 1 bug fix | **~376 records, all overrides**, ~1–2 MB YAML |
| **SkyPatcher INI rules** | the ~454 `PcLevelMult` actors, the ambient leveled lists | tens of lines |

**This revises the earlier working recommendation**, which had rules doing the zone distribution too.
Phase 3 moved the zones into the plugin for two reasons: the authoring cost is **identical either
way** (SkyPatcher's `encounterzone/` has no keyword or location filter, so all 355 must be enumerated
by FormID regardless — `skypatcher.md` §5.3), and only the plugin route is reachable by
xEdit, `formkey-check` and the Spriggit round-trip. Guardrail 6 decides it: for the mod's
spine there must be *something* to verify. Conversely the ~454 class-D actors stay as rules, because
`filterByPCLevelMult` is a **predicate** that also catches NPCs from other mods and future patches,
where 454 overrides would only be a snapshot.

Bonus property: the plugin half **degrades gracefully**. If SkyPatcher breaks on a game update the
world still has its fixed places; under a rules-only design the mod would do nothing at all.

**Masters:** `Skyrim.esm`, `Update.esm`, `Dawnguard.esm`, `Dragonborn.esm`. **Hearthfire excluded.**

The two candidates as they were framed before the decision, kept for context — a third (a
Synthesis/Mutagen generated patch) was considered and **ruled out: Synthesis is not an option for
this mod.** Do not revive it.

| Approach | Mechanism | Cost |
|---|---|---|
| **A. Plugin overrides** | Override vanilla records directly in Spriggit YAML | Total control, no dependencies. But thousands of override files: a huge repo, unreviewable diffs, and a hard conflict with every other mod touching the same records. Phase 2 measured the ceiling: Requiem is **108 MB / 26,620 records**, MLU **22 MB / 4,751**. |
| **B. Runtime rule engines** | SkyPatcher INI rules, applied at load by SKSE | Few or no overrides, filter-based, very compatibility-friendly. **SkyPatcher's capabilities are `[verified]` from source** — see `arch-docs/prior-art/skypatcher.md`. It can express the deleveling core of *both* Requiem and MLU. It **cannot** touch `GMST`s or placed-actor `LevelModifier`, and cannot filter zones by location/keyword. Requires SKSE, and **none of this workspace's verification tooling applies to a rule file**. |

**The overworld: SOLVED, and it was never as bad as it looked** (`implementation-strategy.md` §6,
rewritten 2026-07-29 after the Tamriel worldspace was actually scanned). Only **40 of 12,148**
exterior cells carry an encounter zone — but the 3,512 unzoned leveled refs resolve to just **88
lists, 23 of them already flat**, so the job is **65 lists**, not 12,148 cells. It splits in two:
**wildlife** flattens by rule and *keeps its regional variation for free*, because vanilla already
ships biome-partitioned lists (`LCharAnimalForestPredator`, `…MountainSnowPredator`, …) — this
retracts the old claim that flattening gives "one wilderness mix for the whole province". **Humanoid
lists cannot be flattened** (they are the same lists the dungeon zones tier), so the **238** unzoned
cells holding them get wilderness zones via SkyPatcher `cell/encounterZone=`, which *adds* a zone
where none exists (`cell.cpp:781–802`, `[verified]`). ~7 new `ECZN` + ~7 rule lines + ~18 list
flattens. Rules beat plugin records here: an exterior-cell override carries the whole cell and
conflicts with every lighting/water mod. **Scope: Tamriel only — Solstheim unmeasured.**

## Naming & FormKey conventions

Fixed now so Phase 4 does not have to argue about it:

- **Plugin:** `Ehlnofey.esp`, **ESL-flagged**. Masters **decided in Phase 3**: `Skyrim.esm`,
  `Update.esm`, `Dawnguard.esm`, `Dragonborn.esm`. Hearthfire is excluded — it adds no worldspace,
  region, dungeon or encounter zone, so taking it as a master would buy nothing.
- **EditorID prefix:** `EHL_`, then the domain, then the specific: `EHL_LVLI_DraugrBossHoard_T4`,
  `EHL_ECZN_BleakFalls`. Tier suffixes are `_T<n>` against the ladder in `design/tiers.md`.
- **New records** start at `0x800` and are allocated in a **contiguous block per feature** (one block
  for encounter zones, one for leveled lists, …). Record each block here as it is claimed.
- **Overrides keep the original master's suffix** (`09BC43:Skyrim.esm`), which is how you tell an
  invented record from a vanilla one at a glance. Ehlnofey will be override-heavy, so this matters
  more here than in a content mod.
- **ESL decision: RESOLVED — yes, ESL-flag it.** The verdict is unchanged but **its premise is not**:
  Phase 3 closed this on "no new records at all", and Phase 4 testing has since added two sources of
  new records — **~7 wilderness `ECZN`** for the overworld (`implementation-strategy.md` §6.4) and
  whatever per-tier gear lists/outfits the loot fix needs (`probe-test-protocol.md` §6.3). Both are
  tens of records against ESL's **2,048-slot** `0x800–0xFFF` range, so ESL still holds comfortably —
  but the mod is no longer override-only, and `implementation-strategy.md` §2.5 still says it is.
- Always `/formkey-check` before claiming a block.

**FormID usage: none, and none planned.** All 2,877 shipped records are overrides. The ~7 wilderness
`ECZN` and the per-tier gear lists belonged to the replaced architecture and are not being built.
**Next free: `0x800`.**

## Useful FormKey constants

Add the encounter-zone, faction and leveled-list FormKeys here as Phase 1 confirms them — that table
is the payoff of the research phase.

| FormKey | Meaning |
|---|---|
| `000014:Skyrim.esm` | PlayerRef |
| `000038:Skyrim.esm` | GameHour global |
| `000039:Skyrim.esm` | GameDaysPassed global |
| `00003C:Skyrim.esm` | Tamriel worldspace |
| `038AB1:Skyrim.esm` | BleakFallsBarrowZone (ECZN) — one of only 6 vanilla+DLC zones with a `MaxLevel` (see `design/engine-behaviour.md` §2) |
| `039CFC:Skyrim.esm` | LCharBanditMelee1H (LVLN) — the worked example of vanilla's scaling chain |
| `0130DB:Skyrim.esm` | LocTypeDungeon keyword (202 locations) |
| `0F5E80:Skyrim.esm` | LocTypeClearable keyword (199 locations) |
| `039CFC:Skyrim.esm` | LCharBanditMelee1H — canonical level-gated LVLN ladder |
| `0E7B2C:Skyrim.esm` | LCharGuardImperial — canonical `PcLevelMult` cluster (guards, ×1, [20–50]) |
| `08E4F1:Skyrim.esm` | AlduinBase — the only fully player-scaled boss (`PcLevelMult` ×1.2, [10–100]) |
| `016771:Skyrim.esm` | LocTypeHold keyword — **10** holds, not 9: Skyrim's nine + `DLC2SolstheimLocation` |
| `016E2A:Dragonborn.esm` | DLC2SolstheimLocation — a tenth `LocTypeHold` root (levels 6–40) |
| `016E2B:Dragonborn.esm` | DLC2ApocryphaLocation — root with **no keywords**; 7 Black Books, all level 25 |
| `000013:Skyrim.esm` | CreatureFaction — the creature/humanoid divide (660 NPCs) |
| `01A1D9` / `01A1DB` / `01A1DA` / `023C0B` `:Skyrim.esm` | `fLeveledActorMult` Easy/Medium/Hard/VeryHard — vanilla 0.33/0.67/1/1.25, Ehlnofey 0.70/0.85/1.00/1.25 (`design/tiers.md` §4) |
| `10FEDD` / `10FEDF` / `10FEDE` `:Skyrim.esm` | `fSpecialLootMinZoneLevelMult` 0.4 / `…MaxZoneLevelMult` 1.0 / `…MinPCLevelMult` 0.6 — the boss-chest loot roll. The `…MinPCLevelMult` is a **live bone-1 leak** (floor at 0.6 × *player* level, zone-independent); one record to close |
| `01E60D:Skyrim.esm` | `EncBandit04TemplateMelee` — the vanilla `L=0` bug; Ehlnofey sets it to 14 |
| `0BC0A4` / `0F5BA8` `:Skyrim.esm` | ColdRockPass / ShrineofBoethiah — MLU's two `Min == Max` overrides of vanilla zones (its third is its own `1D6A71:MLU.esp`) |

The full primary-source list is `arch-docs/world/enemy-taxonomy.md` §8 — cite from there rather than
re-deriving.

## Ehlnofey gotchas

Fill this as the project teaches you things.

- **Mutagen omits default-valued scalars in the YAML.** An absent field means *the default*, not
  "not configured". `EncBandit04TemplateMelee` (01E60D) serializes its level as
  `Level: {MutagenObjectType: NpcLevel}` with no `Level:` line — that is level **0**. Never read
  absence as "unset". `[verified]`
- **`TemplateFlags` decides which record owns a stat.** If an NPC lists `Stats` in `TemplateFlags`,
  its own `Level:` is inert and the template's value wins. Read the flags before believing a number
  on an NPC record. `[verified]`
- **Follow the template chain all the way to an `LVLN`, not just one hop.** A named boss like
  `JyrikGauldurson` templates onto `LvlDraugrAmbushWarlock`, which templates onto `LvlDraugrWarlockMale`,
  which templates onto the **leveled list** `LCharDraugrWarlockMale`. Stopping at the first NPC hop
  reports `L=1` and is wrong — 21 of Skyrim's named bosses have no fixed level at all. A resolver must
  treat "template is a `LeveledNpcs` record" as a distinct terminal case. `[verified]`
- **Nobody here knows how a nameless NPC resolves its displayed name. Do not reason about it — put
  the name on every record in the set.** `[verified that the obvious model is wrong]`
  An NPC's name and its level travel on different template flags (`Traits` carries the name, `Stats`
  the level), so they can diverge — that much holds. What does **not** hold is any tidy rule for what
  a leaf with no `FULL` and no `Traits` flag falls back to. Two vanilla facts contradict every model
  tried so far: `EncBandit01*` and `EncBandit02*` leaves are structurally *identical* (both nameless,
  both without `Traits`) yet display "Bandit" and "Bandit Outlaw" respectively — so the chain is
  walked; but naming `EncBandit01TemplateMelee` (the exact record `EncBandit02TemplateMelee` uses for
  "Bandit Outlaw") changed nothing in game — so it is not walked the way that implies. Ruled out:
  stale deploy (byte-identical), load order (`Ehlnofey.esp` loads last), and the record not being
  written (read back out of the built binary).
  **The working practice:** name *all* records in the rung — templates and every leaf — as
  `author-names.ps1` does for the 44 `EncBandit01*`. Records are cheap; a failed in-game test cycle
  is not.
  ⚠️ **This undermines `design/archetype-tiers.md` §3.1.1's premise**, which asserts that all rungs of
  `LCharBanditBoss` display "Bandit Chief" because the name falls through to `LvlBanditBoss` 03DF17.
  That was never observed on a nameplate, only inferred from the same broken model. Pinning the chief
  to one level is still a fine design call, but **its stated justification is unverified** — check it
  in game before relying on it for the four open boss families.
- **NPC level is a discriminated union at `Configuration.Level`**, tagged by `MutagenObjectType`:
  `NpcLevel` (field `Level:`) or `PcLevelMult` (field `LevelMult:`, with `CalcMinLevel` /
  `CalcMaxLevel` as siblings on `Configuration`). Those are the confirmed Spriggit names. `[verified]`
- **`grep -rl` across `reference/` times out (>2 min).** Match on *filenames* instead: Spriggit names
  every file `<EditorID> - <FormID>_<master>.yaml`, so `ls Npcs | grep 039D26` resolves a FormKey
  instantly. For anything bigger, build a `FormID → EditorID → type` index from filenames once and
  join against it. `[verified]`
- **Never compare a hex FormID numerically in `awk`.** `awk -v i="02E893" '$1==i'` matches *eight*
  rows, because a `-v` value is a strnum: `02E893` parses as `2×10^893` → `+inf`, and every
  similarly-shaped FormID (`02E894`, `04E852`, …) is also `+inf`. Truncation is just as bad —
  `0130DB` numifies to `130`, colliding with the whole `0130xx` keyword block. Force string context
  with `$1""==i""`, or use FormIDs only as **array subscripts** (always strings). `[verified]`
- **Never census a field with `grep -c` — count records, not lines.** `grep -c 'LevelModifier:'` over
  `Cells/` returns 2,739 where the true `PlacedNpc` count is 2,524, because 215 `PlacedObject`
  *markers* (`PatrolIdleMarker`, `XMarker`, `GuardMarker`, …) carry the field inertly. Fields recur
  across record types; always parse to the record and filter by `MutagenObjectType`. `[verified]`
- **EditorIDs are not a reliable search key for a named set.** Only four of Skyrim's eight named
  Dragon Priests have "Priest" in their EditorID, and Vokun's is `Ianusu`. When enumerating a named
  group, match on the English `Name:` string; use EditorIDs only once you have the FormKeys.
  `[verified]`
- **DLC plugins have no display names in the decompile.** `Dawnguard.esm` and `Dragonborn.esm`
  records serialize as `Name:` / `TargetLanguage: English` with **no `Values:` block** — the strings
  live in external `.STRINGS` files that Spriggit did not inline. `Skyrim.esm` names *do* come
  through. So the "match on `Name:`" rule above works only for the base game; for DLC you must
  identify records by EditorID and FormKey. `[verified]`
- **Resolve FormKeys by master, not by bare FormID.** A six-hex FormID is only unique *within* a
  plugin: `01A345:Dawnguard.esm` (Harkon's combat style) collides with an unrelated `Skyrim.esm`
  leveled-NPC record. A lookup that searches the base-game index first will silently return the wrong
  record with a plausible name. Always key on `<hex>:<master>`. `[verified]`
- **Never cache a derived index behind an `if [ ! -f ]` guard.** A stale `index_<dlc>.tsv` built by an
  earlier script with a shorter record-type list silently returned empty for `Classes` and
  `CombatStyles`, which reads identically to "this record has no class". Rebuild derived indexes, or
  version them by the list they were built from. `[verified]`
- **Placed records nest at different indentations.** In `Cells/` a placed ref opens at column 0
  (`- MutagenObjectType: PlacedNpc`); in `Worldspaces/` it is indented two more spaces, and the block
  itself contains inner `- MutagenObjectType: ScriptObjectProperty` entries. A parser anchored on
  column 0, or one that treats any nested `MutagenObjectType` as a record boundary, **silently drops
  records** — that mistake undercounted placed NPCs by half (5,169 vs the true 10,504). Track the
  opening line's indent and close the record only at the same or lesser indent. `[verified]`

- **`GMST` records can be *added*, not only overridden.** Skyrim has game settings that exist as
  hardcoded engine defaults with no record in `Skyrim.esm`; creating one makes it editable. MLU adds
  `fSmithingArmorMax` / `fSmithingWeaponMax` as **new** records (`005901:MLU.esp`, `005902:MLU.esp`)
  — there is no `fSmithing*` record in the base game at all. So "absent from `reference/Base`" does
  not mean "not tunable". `[verified]`
- **A base+DLC index has duplicate keys; last-wins is the correct rule.** Concatenating
  `01Skyrim` … `05Dragonborn` into one `FormID_master → data` index produces **135 duplicate keys**
  for NPCs, because `Update.esm` and the DLC re-override base records under the *same*
  `<hex>:Skyrim.esm` FormKey. Only one (`072B04` Vald) actually disagrees on level type, but a
  naive `if (!(k in a))` first-wins load silently uses the *pre-Update* value. Load in load order
  and let later assignments overwrite — that reproduces the winning record, which is the baseline
  you almost always want. `[verified]`
- **Comparing a mod against vanilla means comparing against the *winning* vanilla record**, and the
  join key must be `<hex>_<master>`, never bare hex — see the "resolve FormKeys by master" gotcha
  above. Requiem overrides records from six different masters. `[verified]`
- **A total conversion may ship a *replaced* `Skyrim.esm`, and it will not look replaced.** Enderal
  SE's `Data/Skyrim.esm` is 182.9 MB / 86,636 records of Enderal content, but keeps Bethesda's
  `mcarofano` author string in the TES4 header. Assuming `reference/Base/01Skyrim/` already covers it
  and serializing only the mod-named plugin gets you ~5% of the mod. Cheap check before deciding:
  scan the file for the mod's EditorID prefix (Enderal's `_00E_` appears 27,059 times, "Whiterun"
  31). `[verified]` — see `prior-art/enderal.md`, "Reproducing the evidence".

- **A flag census is not a gate census.** `overview.md` and `enemy-taxonomy.md` §4 both sized the loot
  job as "1,959 of 3,075 `LVLI` are player-gated" — that is the count carrying
  `CalculateFromAllLevelsLessThanOrEqualPlayer`. Only **1,382** have any entry above level 1, and only
  **1,378** have more than one distinct entry level. **1,693 lists (55%) are flat variety pools
  carrying the flag over entries that are all level 1.** Always count the entries, not the flag.
  `[verified]`
- **Never conclude from a truncated read.** `head -40` on `LItemBanditCuirass` (`037C22`) shows forty
  consecutive `Level: 1` entries and looks like a flat pool; its gates at 6/7/8/9/19…28 are further
  down the file. Spriggit orders entries as authored, not by level. Parse the whole record — or at
  minimum `grep` for the field across it — before saying what shape it is. `[verified]`
- **Search `GameSettings/` by keyword before believing a mechanic is undocumented.** The engine names
  its own operands: `fSpecialLootMinZoneLevelMult` / `…MaxZoneLevelMult` / `…MinPCLevelMult` settled a
  question (does the zone level reach loot?) that UESP itself tags as needing verification, and turned
  up a live bone-1 leak in the process. 1,584 GMSTs exist; `ls | grep -i <concept>` is seconds.
  `[verified]`
- **A "player-visible signal" is only a differentiator if it is not collinear with one you already
  use.** `difficulty-map.md`'s first draft bumped dungeon tier on an ancient tileset
  (`LocSetNordicRuin` / `LocSetDwarvenRuin`) as well as on the type keyword — but essentially every
  `DraugrCrypt` *is* a `NordicRuin`, so the rule differentiated nothing and merely relabelled the
  whole type one tier up. Check the cross-tab before adding a signal. `[verified]`
- **`ls */ | grep` over `reference/` times out the same way `grep -rl` does.** The CLAUDE.md gotcha
  about filename matching applies to *globbed* directory listings too — `ls Npcs | grep <id>` is
  instant, `ls */ | grep <id>` is a 2-minute timeout. Name the one directory. `[verified]`

- **`LevelModifier` is inert unless the placed ref's base resolves to an `LVLN`.** It multiplies the
  *leveled-list lookup level*, so a fixed-level NPC has nothing to modify and a `PcLevelMult` actor
  ignores zones anyway. Censusing "placed refs with no modifier" therefore massively overstates the
  exposure: across 291 zoned interior cells, 1,106 refs are unmodified but only **9** have a leveled
  ladder behind them (1,014 are fixed-level corpses/skeevers/quest NPCs, 83 are `PcLevelMult`).
  Always resolve the template chain to a terminal class before sizing a job off a field census —
  this is the "count records, not lines" gotcha one level deeper. See
  `design/probe-test-protocol.md` §4. `[verified]`
- **Spriggit's canonical field order is not the order you'd write by hand.** An `ECZN` serializes as
  `MinLevel` → `Flags` → `MaxLevel`, so hand-authoring `MinLevel`/`MaxLevel` adjacently builds a
  correct plugin that re-serializes to a *different* file, producing a phantom diff on the next
  round-trip. Fix: after the first deserialize, **re-serialize and adopt Spriggit's output as the
  source**. `[verified]`
- **Line endings will always differ between fresh Spriggit output and a checked-out working copy.**
  Spriggit 0.40 on Windows writes **CRLF**; `.gitattributes` forces `*.yaml text eol=lf`. Both are
  deliberate and neither is wrong — but it means a raw `diff -r <src> <fresh-serialize>` reports
  *every line changed* on a clean round-trip. Compare with **`diff -r --strip-trailing-cr`** (or
  `git diff`, which normalizes) and judge the round-trip on content only. Note `.gitattributes`'
  own comment says Spriggit "uses LF" — that is inaccurate for 0.40 on Windows. `[verified]`
- **`[System.IO.File]` does not use PowerShell's current directory.** `Set-Location` moves the
  PowerShell provider's location; `[Environment]::CurrentDirectory` is a separate thing and stays
  wherever the process started or was last set. So `WriteAllLines('src/…/x.yaml', …)` can silently
  resolve against an unrelated directory and throw `DirectoryNotFoundException` with a path that
  looks nonsensical (`…\reference\Base\src\Ehlnofey\…`). The same script had worked earlier in the
  session, which makes it look intermittent. **Resolve to an absolute path first**
  (`(Resolve-Path $dir).Path`) whenever mixing `[System.IO.File]` with relative paths — and note the
  BOM gotcha below means you often *have* to use it rather than `Set-Content`. `[verified]`
- **PowerShell 5.1's `Set-Content -Encoding utf8` writes a BOM; Spriggit does not.** Any record file
  authored by a script that way differs from Spriggit's output on line 1 and produces a phantom diff
  on the next round-trip. Write YAML with
  `[System.IO.File]::WriteAllLines($path, $lines, (New-Object System.Text.UTF8Encoding($false)))`.
  `[verified]`
- **Overriding a vanilla `NPC_` in a non-localized `.esp` collapses its name to one language.**
  `Skyrim.esm` records serialize a multi-language `Values:` block (the STRINGS table); an `.esp`
  without one stores a single `Value:`, so Spriggit picks English and the other eight are gone. This
  hit all 393 base-game NPCs in the extract's bucket E. It is unavoidable without shipping `.STRINGS`
  — dropping `Name:` is *not* the fix, because a Skyrim override replaces the record wholesale and an
  NPC with no `FULL` has no name at all. Accept it, or ship a localized plugin. `[verified]`
- **A PowerShell function returning `,@(...)` breaks `foreach`, even though it fixes `.Count`.** The
  comma-wrap is needed so a 0- or 1-element result keeps `.Count`, but `foreach ($x in Get-Thing)`
  then iterates **once with `$x = @()`** instead of zero times — which reads as a phantom result, not
  an error. Assign to a variable first and check `.Count` before enumerating. `[verified]`

Candidates still to confirm:

- **Do not assume the DLC follow the base game's structure.** Three traps, all `[verified]`:
  **(a)** Solstheim is a **tenth `LocTypeHold`** — a hold-keyed rule written against `Skyrim.esm`
  silently excludes it. **(b)** **9 of Dawnguard's 19 encounter zones have no `Location:` field**
  (vs 270 of 280 in vanilla), so anything walking `ECZN.Location → LCTN → keywords` misses the Soul
  Cairn, Darkfall, Castle Volkihar and most of the Forgotten Vale. **(c)** Dawnguard's new-world
  locations and *all* of Apocrypha carry **no keywords at all** — invisible to both hold-keyed and
  type-keyed rules. Always test a rule against the DLC separately, never by extrapolation.
- **Hearthfire adds no worldspace, no region and no dungeon** — 22 locations and 141 factions of
  homestead bookkeeping. It is out of scope for world design; adding it as a master buys nothing.
  `[verified]`
- **Override volume vs. Spriggit.** A deleveling pass can generate thousands of override YAML files.
  Watch repo size, round-trip time and `Test-RecordYaml.ps1` runtime before committing to option A.
- **Deleveling levels without deleveling capability** produces a world that is fixed and dull.
  Threat is perks, spells and combat style as much as level.
- **A clean build proves nothing about balance.** Phase 4 is not done at "deserializes clean" — it is
  done when a character has actually walked into a zone and been correctly killed by it.
