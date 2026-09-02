---
id: "enderal/reference/deleveling-prior-art"
title: "Enderal: Forgotten Stories"
slug: "deleveling-prior-art"
section: "enderal/reference"
game: "enderal"
kind: "research"
project: null
mod: null
tags: ["enderal", "prior-art", "deleveling", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/prior-art/enderal.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 2, "unverified": 3, "upstream": 0, "verified": 12}
lines: 330
content_sha256: "44df47afc224a7e711498a798653795f1577ea9768a2581e6397a7bb99ac4e0f"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Enderal: Forgotten Stories

**Subject:** Enderal SE **2.0.12.4** (SureAI), as installed at
`C:\Gaming\steamapps\common\Enderal Special Edition\Data`.
**Phase:** 2 (prior art & method), reopened deliberately — see the note below.
**Status:** both plugins read from a Spriggit decompile. **No in-game testing.** No Papyrus read.

Enderal is a **third pole** of deleveling prior art, and the only one of the three that actually
achieves bone 1 outright. Requiem flattens the leveled-actor gate; MorrowLoot Ultimate keeps the
gate and clamps its input per place. Enderal **deletes the machinery entirely and hand-places every
actor at a fixed level** — 0 `LVLN`, 0 `PcLevelMult`, 0 `LevelModifier`, 2 `ECZN`.

> **Why this file exists in a closed phase.** `CLAUDE.md` records Phase 2 as CLOSED with three
> candidates deliberately dropped. Enderal is not one of them and is not a Skyrim overhaul at all —
> it is a total conversion, which is precisely why it could take the option Requiem and MLU could
> not. It is read here as an **existence proof and a cautionary tale**, not as a method to copy.
> Ehlnofey cannot do what Enderal did; see §9.

## Reproducing the evidence

The decompiles are **gitignored** and must be regenerated locally. Enderal ships **two** plugins and
you need both:

```powershell
. ".claude/config/tools.ps1"
$cli = Assert-Tool $Tools.spriggitCli 'spriggitCli'
$data = "C:\Gaming\steamapps\common\Enderal Special Edition\Data"

# the replaced master — where essentially all of the deleveling lives
& $cli serialize --InputPath "$data\Skyrim.esm" `
  --OutputPath "reference/Base/enderalSkyrim" `
  --GameRelease $Tools.spriggit.gameRelease `
  --PackageName $Tools.spriggit.packageName `
  --PackageVersion $Tools.spriggit.packageVersion

# the expansion layer
& $cli serialize --InputPath "$data\Enderal - Forgotten Stories.esm" `
  --OutputPath "reference/Base/enderal" `
  --GameRelease $Tools.spriggit.gameRelease `
  --PackageName $Tools.spriggit.packageName `
  --PackageVersion $Tools.spriggit.packageVersion
```

**Two traps, both hit while producing this document:**

1. ⚠️ **Enderal's `Skyrim.esm` is a replaced master, not Bethesda's.** It keeps Bethesda's `mcarofano`
   author string in the TES4 header, so it looks untouched, and the obvious assumption — "we already
   have Skyrim.esm decompiled, skip it" — throws away ~95% of the subject. A raw byte scan of the
   183 MB file finds **27,059** occurrences of `_00E_` (Enderal's EditorID prefix) and **1,180** of
   "Ark" (its capital) against **31** of "Whiterun". Serializing only
   `Enderal - Forgotten Stories.esm` yields 1,052 NPCs and no explanation of anything. `[verified]`
2. **The `Skyrim.esm` serialize exits non-zero and the output is still complete.** Serialization
   logs `Finished serializing`; it is Spriggit's *post-serialize sanity check* — which deserializes
   its own output back to a temp plugin — that throws
   `Malformed FormKey string: 89103` on `NavigationMeshInfoMaps\Null.yaml`, a Mutagen bug on a
   null-FormKey `NAVI` record. Harmless for a lookup-only decompile; it would matter only if you
   tried to rebuild the plugin. `[verified]`

## 0. Shape of the two plugins

| | records | notes |
|---|---:|---|
| `Skyrim.esm` (Enderal's) | **86,636** | 182.9 MB. Author header still `mcarofano`; content is Enderal's |
| `Enderal - Forgotten Stories.esm` | **13,868** | 10.3 MB. Author `Niseam`, desc `Enderal: Forgotten Stories (Special Edition) 2.0.12.4`. Flags `Master`, `Localized`. Masters: `Skyrim.esm`, `Update.esm` |
| ↳ of which new | 10,210 | |
| ↳ of which overrides | 3,658 | 3,656 of `Skyrim.esm`, 2 of `Update.esm` |
| vanilla `Skyrim.esm`, for scale | 133,907 | `reference/Base/01Skyrim/` |

Enderal's master is **smaller than vanilla's by 47,271 records**. That is the whole story in one
number: this is not a patch that overrides the scaling machinery, it is a rebuild in which most of
the machinery **does not exist as a record at all**. `[verified]`

## 1. The machinery census

Every lever `CLAUDE.md`'s "vanilla scaling machinery" table names, counted in both plugins:

| Lever | vanilla `Skyrim.esm` | Enderal `Skyrim.esm` | Enderal FS | verdict |
|---|---:|---:|---:|---|
| `NPC_` records | 5,118 | 1,816 | 1,052 (435 new) | 2,251 unique actors |
| …with `PcLevelMult` | many | **0** | **0** | **abolished** |
| …with `TemplateFlags` | common | **0** | **0** | **abolished** (652 records still carry a bare `Template:`) |
| `LVLN` leveled actors | 527 | **0** | **0** | **abolished — the folder does not exist** |
| `LVLI` leveled items | 3,075 | 166 | 114 | kept, mostly flat (§4) |
| `ECZN` encounter zones | 280 | **2** | 0 | repurposed (§6) |
| `PlacedNpc` refs | 10,504 † | 5,546 | 1,073 | hand-placed |
| …with a `LevelModifier` | 5,685 † | **0** | **0** | **abolished** |
| `GMST` | 1,584 | 1,645 | 15 | +62 added, 41 changed (§7) |

† vanilla figures from this repo's own earlier census (`CLAUDE.md`, "Placed-actor difficulty"), not
re-derived here. Enderal's placed counts are `Cells` + `Worldspaces` per plugin and are **not**
additive across plugins — an FS cell override replaces the vanilla cell's whole reference list, so
some of FS's 1,073 supersede some of the master's 5,546.

**Zero `PcLevelMult` records in the entire game** — `grep -rl PcLevelMult` over both decompiles
returns 0 files. This is the single most important fact in the document: it is the thing Requiem
never finished (it leaves followers and 114 NPCs scaling) and the thing MLU structurally cannot do
(zones do not reach `PcLevelMult` actors). `[verified]`

## 2. Lever 1 — every actor owns a fixed level

All 2,251 unique `NPC_` records serialize `Configuration.Level` as `NpcLevel` with an explicit
`Level:`. Distribution of the winning record (FS overrides applied last):

| | |
|---|---|
| `L=1` | 808 (35.9%) — townsfolk, quest actors, corpses, critters |
| rungs 1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60 | **1,832 of 2,251 (81.4%)** |
| off-rung levels | 419, thinly spread (L=13 has 2 records, L=21 has 1) |
| ceiling | 60 for ordinary content; then 65 ×2, 70 ×2, 80 ×5, 100 ×1 |
| outlier | `_00E_MQ05Aixon` (`03B8E6:Skyrim.esm`) at **L=2000** — a quest actor made unkillable by level |

The busiest rungs are 30 (206 records), 20 (159), 5 (180), 10 (119), 25 (101). **This is an authored
tier ladder in multiples of five**, not a per-encounter hand-tune: Enderal picked ~13 levels and
assigned nearly every actor in the game to one of them. Compare Ehlnofey's T1–T7 =
4 / 8 / 14 / 21 / 30 / 40 / 50 (`design/tiers.md`) — same idea, coarser, topping out lower.
`[verified]`

### 2.1 The EditorID encodes the tier

Enderal's naming convention puts the level in the record name: `_05E_Bandit05_Range0800` is level 5,
`_20E_Bandit01_Aggressive` is level 20, `_45E_Vatyr01` is level 45. `_00E_` is the generic prefix for
quest/town/unique actors.

**How reliable is it? 896 of 1,161 (77%).** Of the NPCs carrying a `_NNE_` prefix with `NN > 00`,
896 have `Level == NN` and **265 do not**. The drift is usually ±1–5 (`_03E_` records sitting at
L=5, `_17E_` at L=18, `_30E_` at L=35), but a handful are wild: the whole `_01E_Besessener*` family
(the Possessed) is prefixed `_01E_` and sits at **L=30–55**.

The lesson is not "don't do this" — it is that **a naming convention drifts unless it is
generated**. Ehlnofey already uses `_T<n>` suffixes and already generates its records from
`author-*.ps1` scripts; a check that the suffix matches the authored level is a few lines and would
have caught all 265. `[verified]`

## 3. Lever 2 — the leveled-actor system is deleted, not flattened

There is no `LeveledNpcs/` directory in either decompile. Vanilla has 527 `LVLN`; Enderal has none,
so every one of its ~6,000 placed actor references points **directly at an `NPC_` record**. There is
no template chain to trace, no chance-none roll, no "which variant spawned" question. The
`arch-docs` gotcha about following a template chain through `LvlDraugrAmbushWarlock` →
`LCharDraugrWarlockMale` has no analogue here: 652 records carry a `Template:` FormKey but **not one
record in either plugin has a `TemplateFlags:` block**, so nothing is inherited and the level on the
record is always the level in play.

Consequences Enderal accepted in exchange:

- **Encounter variety is authored, not rolled.** Where vanilla writes one `LCharBanditMelee1H`
  reference and lets the engine pick, Enderal writes out `_10E_Bandit01…_09Ranged` as separate
  records and places them individually — hence ~9 numbered variants per level band per faction.
- **Repopulation is cell reset only.** `iHoursToRespawnCell` is cut from 240 to **124**, and the
  respawn opt-out is a flag on the placed ref plus the zone in §6.
- **Nothing scales, including downward.** A level-30 desert bandit camp is a level-30 camp at
  character level 5. That is bone 1 in its purest form and it is only survivable because Enderal
  gates the map by quest and geography.

`[verified]` for the record facts; the design consequences are read off the data, `[unverified]` in play.

## 4. What Enderal kept player-gated: shops and spellbooks

`LVLI` is the one place vanilla's player-level machinery survives. **37 of 166** lists in the master
and **18 of 114** in FS still carry entries above level 1. Sorted by what they are:

| Group | Examples | Level set |
|---|---|---|
| **Vendor stock** | `_00ETraderSpellBooksLevelA–D`, `_00ETraderWeapArmA/B`, `_00ETraderCraftingPlans/B/C`, `TraderAlchemyLVL6/14`, `TraderSmithingLVL6/10`, `_00ETraderPotion10/20/30` | e.g. `D` = 30,31,32,34,…,55 |
| **Spellbook drops** | `_00E_SpellBooksLootA/B/C/D`, FS's `_00E_FS_Forbidden_SpellBooks_{Entropy,Psionics,Summons}` | A = 1,4–7 … D = 30–55 |
| **Vanilla leftovers** | `LItemGems`, `LItemGemsSmall`, `LItemJewelryRing/Necklace/Circlet`, `LItemSoulGem*` | vanilla's own ladders, untouched |
| **One authored exception** | FS's `_00E_FS_LItem_MythicItems` | 15, 20, 25, 30, 45, 50, 60 |

The pattern is coherent: **player level gates commerce and spell access, place gates danger.** A
merchant restocking better books as you grow is a progression curve the player controls; a bandit
camp that grows with you is not. That is a defensible carve-out and it is close to what Ehlnofey's
`loot-model.md` already concluded from the other direction.

**One live leak, same one Ehlnofey found in vanilla.** `fSpecialLootMinPCLevelMult` is still at
vanilla **0.6**, and 25 + 10 lists carry the `SpecialLoot` flag. With only two `ECZN` and neither
carrying a level, the zone terms of the boss-chest formula are 0, so the surviving floor is
`0.6 × player level` — pure player scaling. Whether any Enderal boss container actually rolls
through those lists is **`[unverified]`**; the GMST value and the flag counts are `[verified]`.

## 5. The other half — the player's own level curve is authored too

Deleveling the world is only half a fixed-difficulty design; the other half is controlling how fast
the player moves along the ladder. Enderal disables vanilla's progression outright:

| GMST | vanilla | Enderal |
|---|---:|---:|
| `fXPLevelUpBase` | 75 | **999** |
| `fXPLevelUpMult` | 25 | **999** |
| `fSkillUseCurve` | 1.95 | **1E+09** |
| `fXPPerSkillRank` | *(no record)* | **999** (added) |

Skill use effectively never advances a skill, and the XP required per level is set out of reach, so
the vanilla level-up path is dead. Advancement instead runs through a script: the quest
`Levelsystem` (`010AA2:Skyrim.esm`) carries the script `_00E_QuestFunctions` with a large property
block including `_00E_Levelsystem_*` strings, and a `TalentPoints` global (`05BCFA:Skyrim.esm`)
exists alongside ~300 `_00E_Class_*_Talent_*` perks. The record evidence for *disabled vanilla
leveling* is `[verified]`; the description of what replaced it (Enderal's Learning-Point / class
system) is `[community]` — the Papyrus was not decompiled for this read.

**For Ehlnofey this is the uncomfortable one.** A fixed world's fairness depends on the player's
level being where the designer expects when they arrive somewhere, and Ehlnofey's non-goals
explicitly exclude a perk/skill overhaul. Enderal did not consider the two separable.

## 6. Encounter zones survive as a no-respawn marker

Both surviving `ECZN` records are worth quoting whole, because they are so nearly empty:

```yaml
# EncounterZones/_00E_NoRespawn - 046AEC_Skyrim.esm.yaml
FormKey: 046AEC:Skyrim.esm
EditorID: _00E_NoRespawn
Version2: 1
Flags:
- NeverResets
```

```yaml
# EncounterZones/NoZoneZone - 00001E_Skyrim.esm.yaml
FormKey: 00001E:Skyrim.esm
EditorID: NoZoneZone
```

No `MinLevel`, no `MaxLevel`, no `Location`. `_00E_NoRespawn` is referenced by 3 cells in the master
and by cells and one placed ref in FS. `NoZoneZone` is vanilla's null zone, kept as a form.

That is the **third independent data point** on encounter zones, and all three agree that a zone is
only worth something if the leveled-list machinery is still there for it to clamp:

| Mod | `ECZN` | used for |
|---|---:|---|
| Requiem | 8 | nothing level-related — its `LVLN` are already flat |
| MorrowLoot Ultimate | 360 | **the entire difficulty map** (324 with a real band) |
| **Enderal** | **2** | **a respawn flag** |

Ehlnofey reached the same conclusion by a different route in `design/requiem-method.md` (zones
govern 0.3% of the outdoors and cannot reach worn gear). Enderal is confirmation from a shipped
game. `[verified]`

## 7. GMST changes worth knowing

62 added, 41 changed, 1 vanilla setting absent. The level-relevant ones:

- **XP/leveling** — the four in §5.
- **`fLeveledActorMult*` left at vanilla 0.33 / 0.67 / 1 / 1.25.** They are inert: nothing carries a
  `LevelModifier` and nothing resolves through an `LVLN`. Contrast MLU, which retunes them to
  0.7/0.9/1.1/1.3, and Ehlnofey, which uses 0.70/0.85/1.00/1.25 (`design/tiers.md` §4).
- **Difficulty multipliers are *added*, not overridden** — `fDiffMultHPToPC{VE,E,N,H,VH,L}` and
  `fDiffMultHPByPC{…}` have **no record in vanilla `Skyrim.esm`** and Enderal creates them
  (`ToPCL = 3`, `ToPCVH = 1.55`, `ByPCVH = 0.9`). This is a second confirmation of the
  `CLAUDE.md` gotcha first found in MLU: *absent from `reference/Base` does not mean not tunable.*
  Enderal's difficulty slider therefore does its work purely through damage multipliers — the only
  player-relative knob left in the game. `[verified]`
- **`iHoursToRespawnCell` 240 → 124**, `iDeathDropWeaponChance` 100 → 0,
  `iCommon/Greater/GrandSoulActorLevel` 16/28/38 → 14/27/36 (soul-gem thresholds re-aimed at
  Enderal's actual level rungs — a small, easily-missed consequence of moving every actor's level).

The remaining 30-odd changes are combat/sneak/barter/AI-social tuning, out of scope here.

## 8. Legibility: the name ladder

Enderal's bandits, read by level with their English `Name:` values:

| Level | Display name |
|---:|---|
| 1–5 | **Highwayman / Highwaywoman** |
| 10 | **Vagrant** |
| 17–20 | **Marauder** |
| 30 | **Marauder**, **Smuggler** (desert variants) |
| 40 | **Cutthroat**, **Wild Mage** |
| named | Galgart (L7), Kartis / Podrim (L33) |

This is **exactly the mechanism `CLAUDE.md` calls the load-bearing one for bone 2** — a lore-ordered,
player-facing name ladder aligned with power, the same shape as Draugr → Restless → Wight → Scourge
→ Deathlord. Enderal is independent evidence that a fully deleveled world remains readable when the
names carry the tier.

**And it is evidence of the failure mode too.** The ladder is not clean: `_10E_Bandit02_Aggressive`
displays "Highwaywoman" at L=10, sharing a name with the L=5 band, while
`_20E_Bandit08Ranged_Aggressive` displays "Vagrant" at L=20, sharing a name with the L=10 band. A
player reading nameplates in Enderal gets the tier approximately right and occasionally wrong —
which is precisely the naming test in `design/archetype-tiers.md` §3.1.1 that four of Ehlnofey's
boss families currently fail. A shipped, well-regarded game fails it in places too; that is context
for how much the four open families are worth, not permission to skip them. `[verified]`

## 9. What Ehlnofey can and cannot take

**Cannot take — the method itself.** Enderal deleted 527 `LVLN` and 278 `ECZN` and rewrote 5,118
`NPC_` down to 1,816 because it *replaced the master*. It never had to keep a single vanilla
placement working. Ehlnofey is a plugin loaded on top of Bethesda's `Skyrim.esm`: every vanilla
`PlacedNpc` that points at `LCharBanditMelee1H` still points at it, so the list must exist and must
resolve. Flattening is the only move available; deletion is not. **This is the reason Ehlnofey's
architecture is Requiem's and not Enderal's**, and the reason should be stated that way rather than
as a preference.

**Can take, and should:**

1. **The existence proof.** A fully deleveled Skyrim-engine RPG — 0 `PcLevelMult`, 0 `LVLN` — ships,
   is popular, and is playable. Bone 1 is not theoretical. Where Ehlnofey currently has 65 follower
   + 114 unreached `PcLevelMult` NPCs owed (`CLAUDE.md`, "Owed next"), Enderal's answer is that the
   count should be zero and that reaching zero is affordable.
2. **The rung ladder.** ~81% of Enderal's actors sit on 13 authored levels. Ehlnofey's T1–T7 is the
   same instinct with 7 rungs. Enderal's ceiling of 60 (vs Ehlnofey's 50) and its dense low end
   (L=5 and L=10 hold 299 actors between them) are a usable sanity check on the calibration.
3. **The tier-in-the-EditorID convention** — cheap, greppable, and self-documenting. Take it
   **with the generator check Enderal lacks**: 265 of its 1,161 prefixed records disagree with their
   own name.
4. **The commerce carve-out.** Keeping player-level gating on vendor stock and spellbooks while
   fixing everything about danger is a coherent line, and Enderal draws it in exactly one record
   type. If Ehlnofey ever wants an explicit bone-3 exception, this is the precedent and the shape.
5. **The zone verdict, third time confirmed.** `ECZN` is worth 2 records to a mod that has already
   flattened its actor lists.
6. **The uncomfortable one.** Enderal did not think a fixed world could work without also authoring
   the player's level curve. Ehlnofey's non-goals rule out a progression overhaul. That is a real
   tension and it belongs in `design/`, not in a footnote — the fixed world is only fair if the
   player arrives at roughly the level the designer assumed, and vanilla Skyrim's curve is driven by
   skill use, which is driven by how much the player fights, which a deleveled world changes.

## 10. Limits of this read

- **Records only. Nothing was launched.** Guardrail 6 applies in full: everything here is what the
  plugins *say*, not what the game *does*.
- **No Papyrus.** `_00E_QuestFunctions` and the rest of the level system were not extracted or
  decompiled. Any statement about how the player actually levels is `[community]`.
- **673 of 1,816 master NPCs serialize no `Name:` value**, while 1,143 do. Whether those are
  genuinely nameless or externalized to `.STRINGS` was not determined — relevant only if someone
  wants a complete name ladder rather than the sampled one in §8. `[unverified]`
- **Placed-actor counts are per plugin and overlap.** See the footnote on §1's table.
- **Enderal is not Skyrim.** Its world, quest gating and geography differ entirely, so nothing here
  transfers as a *number*. It transfers as a demonstration of what the levers do when pushed all the
  way.
