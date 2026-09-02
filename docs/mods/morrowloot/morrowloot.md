---
id: "mods/morrowloot/morrowloot"
title: "MorrowLoot Ultimate (MLU)"
slug: "morrowloot"
section: "mods/morrowloot"
game: "skyrim"
kind: "research"
project: null
mod: "morrowloot"
tags: ["skyrim", "morrowloot", "deleveling", "third-party-mod", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/prior-art/morrowloot.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 3, "unverified": 0, "upstream": 0, "verified": 13}
lines: 284
content_sha256: "9530b5c176a248949786542141079d93f8a0059775fc777159673cbfc87d6917"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# MorrowLoot Ultimate (MLU)

**Subject:** MorrowLoot Ultimate **v2.0a**, by ChocolateNoodle and Mebantiza (Oct 2023 build).
**Phase:** 2 (prior art & method). **Status:** plugin read; no in-game testing done.

MLU is the other pole of deleveling prior art. Requiem and MLU both produce a world that does not
scale to the player — **using opposite levers**. Requiem deletes the scaling machinery; MLU keeps it
and clamps its input per place. Reading them together is what makes either legible.

> **This document resolves the open `ECZN` question** left by
> [`requiem/lessons-for-ehlnofey.md`](../requiem/lessons-for-ehlnofey.md) §1. Requiem's near-total
> avoidance of encounter zones is not evidence that zones don't work — it is a consequence of
> Requiem having already removed the thing zones act on.

## Reproducing the evidence

The decompile is **gitignored** and must be regenerated locally:

```powershell
. ".claude/config/tools.ps1"
& (Assert-Tool $Tools.spriggitCli 'spriggitCli') serialize `
  --InputPath   "reference/mods/morrowloot/download/MLU.esp" `
  --OutputPath  "reference/mods/MLUYaml" `
  --GameRelease $Tools.spriggit.gameRelease `
  --PackageName $Tools.spriggit.packageName `
  --PackageVersion $Tools.spriggit.packageVersion
```

## 0. Shape of the plugin

| Metric | MLU | (Requiem, for scale) |
|---|---|---|
| Total records | **4,751** | 26,620 |
| New records | 830 | 7,854 |
| Overrides | 3,921 | 18,766 |
| Spriggit YAML on disk | **22 MB** | 108 MB |
| **EncounterZones** | **360** | 8 |
| **LeveledNpcs** | **2** | 571 |
| LeveledItems | 746 | 3,433 |
| Npcs | 183 | 2,702 |

Masters are the same demanding set as Requiem's: the five game plugins, **USSEP**, and four Creation
Club plugins. `reference/mods/MLUYaml/RecordData.yaml`. `[verified]`

Those two bolded rows are the whole story. **MLU has 45× Requiem's encounter zones and 1/285th of
its leveled-NPC lists.** They are not variations on one technique; they are different techniques.

MLU also ships new content — 830 new records, 7 Papyrus scripts (the Sunder/Wraithguard receptacle
puzzle, Orgnum, a Black Book), and new meshes/textures. That content is out of scope here; only the
deleveling machinery is analysed.

## 1. The mechanism, in three levers

1. **Clamp each place** to a narrow fixed level band via `ECZN` `MinLevel`/`MaxLevel`.
2. **Truncate the loot lists** so high-tier gear cannot be rolled at all, at any level.
3. **Leave the scaling machinery running** underneath — NPC records and `LVLN` lists stay vanilla.

Lever 3 is what makes lever 1 load-bearing. An encounter zone's min/max **bounds the level the
leveled-spawn machinery computes for that location**; it is a constraint on a calculation. Requiem
deleted the calculation, so its zones became inert. MLU kept the calculation and made the constraint
tight enough to be the answer. `[community]` — the clamp semantics are established modding
knowledge, not re-verified here, and this is the load-bearing assumption of the whole analysis.
**Verify it in-game before Ehlnofey depends on it.**

## 2. Lever 1 — encounter zones as the difficulty map

| Measure | Vanilla | MLU |
|---|---|---|
| Zones with a `MinLevel` | 350 | 360 |
| Zones with a `MaxLevel` | **6** | **324** |
| Zones with **both** (a real band) | **5** | **324** |

MLU overrides 319 vanilla zones and adds 41 of its own. Of the overrides, **289 gained a `MaxLevel`
they did not have** and **309 had their `MinLevel` changed**. `[verified]`

The bands are strikingly regular — this is a designed ladder, not ad-hoc tuning:

| Band width | Zones |
|---|---|
| 10 | **244** |
| 15 | 73 |
| 20 | 4 |
| 0 (single level) | 3 |

### The map itself

Vanilla `MinLevel` → MLU `[Min–Max]`, from `reference/mods/MLUYaml/EncounterZones/`:

| Dungeon | Vanilla | MLU |
|---|---|---|
| Bleak Falls Barrow | 6 (max 20) | **10–20** |
| Dustman's Cairn / Saarthal | 6 | **16–26** |
| Ustengrav / Shrouded Grove | 6–8 | **18–28** |
| Nchuand-Zel | 16 | **24–34** |
| Mzinchaleft / Dimhollow Crypt | 16 / 6 | **28–38** |
| Angarvunde | 6 | **30–40** |
| Alftand | 16 | **38–53** |
| Bthardamz | 16 | **40–55** |
| Blackreach | 18 | **42–57** |
| Labyrinthian | 24 | **47–** |
| Ragnvald, Skuldafn, Valthume, Volskygge | 10–24 | **50–** |
| Forelhost | 24 | **54–** |

Two things to notice. **The top tier has a floor but no ceiling** (`MaxLevel` 0) — the hardest places
stay open-ended. And the shift is uniformly upward: across the 314 comparable zones, MLU **raised
`MinLevel` on 304, lowered it on none**, mean **+17.1 levels**. `[verified]`

MLU also **subdivides places vanilla treated as one**, adding zones like
`MLU_BleakFallsBarrowExtZone` (the exterior, banded separately from the interior) and
`MLU_MzinchaleftExtZone`. 138 cell records are overridden purely to reassign `EncounterZone`.
`[verified]`

### Flags carry design intent too

| Flag | Zones |
|---|---|
| `DisableCombatBoundary` | 150 |
| `NeverResets` | 109 |

The 15 new `MLU_*ZoneNR` zones ("NR" = no respawn) are the ones holding hand-placed unique loot —
13 of 15 carry `NeverResets`, so a cleared vault stays cleared and its contents are not farmable.
Note MLU bakes `DisableCombatBoundary` into records; Requiem applies the identical flag at runtime
through the Reqtificator. Same idea, different delivery. `[verified]`

## 3. Lever 2 — truncate the loot lists, don't flatten them

This is the inverse of Requiem's technique and the mod's namesake idea: **top-tier gear should be a
landmark, not a drop.**

`LItemWeaponSwordBest` (`0571AA:Skyrim.esm`) — vanilla has 7 tiers ending Ebony (36) and Daedric
(46). MLU keeps the *same gate levels* (1, 6, 12, 19, 27) and simply **stops early**, redirecting
the surviving tiers to its own rebalanced records:

```yaml
# MLU                                    # vanilla
- {Level: 1,  Reference: 013989:Skyrim}  - {Level: 1,  Reference: 013989:Skyrim}
- {Level: 6,  Reference: 33925F:MLU}     - {Level: 6,  Reference: 013991:Skyrim}
- {Level: 12, Reference: 339260:MLU}     - {Level: 12, Reference: 013999:Skyrim}
- {Level: 19, Reference: 339261:MLU}     - {Level: 19, Reference: 0139A1:Skyrim}
- {Level: 27, Reference: 3392A6:MLU}     - {Level: 27, Reference: 0139A9:Skyrim}
                                         - {Level: 36, Reference: 0139B1:Skyrim}  ← Ebony, gone
                                         - {Level: 46, Reference: 000F16:Skyrim}  ← Daedric, gone
```

Measured across all 473 `LVLI` overrides of vanilla lists:

| Measure | Value |
|---|---|
| **Top gate lowered (truncated)** | **400 (84.6%)** |
| Top gate unchanged | 68 |
| Top gate raised | 5 |
| Flattened to a single gate | 143 (30.2%) — vs Requiem's 95.7% |
| Total entries: vanilla → MLU | 5,315 → 3,091 (**58.2%**) |

And the decisive test — Daedric/Ebony base items appearing as entries, **within the same 483 lists**
so the comparison is like-for-like:

> **vanilla: 168 entries across 123 lists → MLU: 8 entries across 8 lists.** A ~95% removal. `[verified]`

MLU does *not* delevel these lists. A level-19 player still gets better loot than a level-6 player.
It **caps the ceiling** so the best gear leaves the random economy entirely. That is a different
design goal from bone 1, and worth being honest about: **MLU's loot is still player-level-scaled
within the surviving range.**

Two supporting record techniques:

- New GMSTs `fSmithingArmorMax` / `fSmithingWeaponMax` = 6 (`…_MLU.esp.yaml` — these are *new*
  records; vanilla has no such GMST). Caps crafting so smithing can't reintroduce what the lists no
  longer drop.
- 1,396 `PlacedObject` and 741 `PlacedNpc` records across cells and worldspaces — the hand-placement
  layer, largely new dungeon geometry and containers rather than gear on pedestals. `[verified]`

## 4. What MLU does *not* touch

- **NPC levels — essentially untouched.** Of 183 `NPC_` overrides: 51 stay `PcLevelMult`, 35 stay
  `NpcLevel`, and only **2** convert scaled → fixed (one converts the *other* way). 94 are new
  records. MLU delevels no one; it relies entirely on the zone clamp. `[verified]`
- **Leveled NPC lists — 2 records.** `LCharPenitusOculatus` and one new MLU list. Vanilla's
  level-gated spawn ladders are left completely intact. `[verified]`
- **The 12 `LevelGate*` globals — untouched**, exactly as in Requiem. Both major delevelers ship
  with vanilla's only systematic player-level spawn gate intact. `[verified]`

## 5. `fLeveledActorMult*` — MLU compresses, Requiem preserves

| GMST | Vanilla | MLU |
|---|---|---|
| `fLeveledActorMultEasy` | 0.33 | **0.7** |
| `fLeveledActorMultMedium` | 0.67 | **0.9** |
| `fLeveledActorMultHard` | 1.0 | **1.1** |
| `fLeveledActorMultVeryHard` | 1.25 | **1.3** |

These are the multipliers behind the per-placed-actor `LevelModifier` field that Phase 1 found on
5,685 of 10,504 placed actors. Vanilla spreads them 0.33–1.25 (~3.8×); MLU compresses to 0.7–1.3
(~1.9×). **MLU deliberately weakens vanilla's per-actor variance so the zone band dominates** —
consistent with making the *place* the unit of difficulty. Requiem left these at vanilla, because
its levels come from the actor records instead. `[verified]`

MLU overrides **no** `fDiffMult*` difficulty-slider settings; Requiem flattens all twelve to 1.0.
The difficulty slider still works normally in MLU.

## 6. Bash tags — the exact opposite of Requiem

MLU declares its tags the **old way**, inline in the plugin header description
(`RecordData.yaml`), rather than in a `BashTags/` loose file:

```
v2.0a {{BASH:Delev,Relev,Names,Stats,Keywords,Actors.ACBS,Actors.Factions,
Actors.Perks.Add,Actors.Spells,Actors.Stats,Invent.Add,Invent.Remove,
NPC.DefaultOutfit,Outfits.Add,Outfits.Remove}}
```

**MLU asks for `Delev` and `Relev`; Requiem refuses both.** That is not a stylistic difference — it
follows from the mechanism. MLU's leveled-list work is *entry removal* (`Delev`) and *re-levelling*
(`Relev`), which is precisely what those tags were designed to merge, so a Bashed Patch can combine
MLU's truncation with another mod's additions. Requiem's work is wholesale list replacement, which
no generic merger can reconcile — hence its own bespoke merger and its in-game warning when Wrye
Bash has merged leveled lists.

**A mod that truncates lists can delegate compatibility to Wrye Bash. A mod that replaces them must
build its own patcher.** That is a real, quantifiable cost difference between the two approaches, and
it lands squarely on Ehlnofey's Phase 3 decision. `[verified]` (tag contents; the *behaviour* of
`Delev`/`Relev` is `[community]` — see [`requiem/bash-tags.md`](../requiem/bash-tags.md))

## 7. Requiem vs MLU, side by side

| | **Requiem** | **MorrowLoot Ultimate** |
|---|---|---|
| **Core lever** | Flatten `LVLN` gates | Clamp `ECZN` bands |
| Encounter zones | 8 (none for levels) | **360 (324 banded)** |
| Leveled NPC lists | 571, **100% flattened** | **2** |
| Leveled item lists | 3,433, 95.7% flattened | 746, **84.6% truncated** |
| NPC level conversions | 261 scaled → fixed | **2** |
| Where difficulty lives | On the actor record | **On the place** |
| Vanilla scaling machinery | **Deleted** | **Kept, constrained** |
| `fLeveledActorMult*` | vanilla (variance preserved) | **compressed** (place dominates) |
| Difficulty slider | **neutered** (all `fDiffMult*` = 1) | untouched |
| Compatibility model | bespoke patcher (Reqtificator) | **Wrye Bash `Delev`/`Relev`** |
| Repo cost (Spriggit YAML) | 108 MB / 26,620 records | **22 MB / 4,751 records** |
| Delevels loot? | yes (flattened) | **no — caps it** |
| Delevels enemies? | yes (fixed levels) | **no — bounds them per place** |

Neither is a pure implementation of Ehlnofey's bone 1. Requiem fixes enemy levels but leaves
followers scaling and 114 NPCs untouched. **MLU never fixes anything — it narrows the range.** A
band of `[38–53]` still moves with the player inside that band.

## 8. What Ehlnofey should take from MLU

1. **Encounter zones are viable after all — but only if you keep the scaling machinery.** This is
   the correction to the correction. `ECZN` is inert in a Requiem-style flattened world and
   load-bearing in an MLU-style clamped one. **The `ECZN` question and the `LVLN` question are one
   decision, not two,** and `arch-docs/design/difficulty-map.md` cannot be written before it is made.
2. **`MinLevel == MaxLevel` is the un-taken option.** MLU's 244 width-10 bands are a *narrowing*,
   not a fixing. Three MLU zones already use width 0. Ehlnofey's bone 1 says width 0 everywhere —
   nobody in the prior art has done that, so there is no precedent for how it feels, and no evidence
   it doesn't break. Treat it as the highest-risk, highest-value experiment in Phase 4.
3. **A per-place band is cheap.** 360 `ECZN` records is ~1 MB of YAML — a hand-authorable,
   reviewable, diffable core. Compare 108 MB for Requiem's approach. If the clamp semantics hold,
   **this is the most repo-efficient route to bone 1 found so far.**
4. **Truncation and flattening are separable, and Ehlnofey may want both.** Truncating high-tier
   gear out of the lists serves bone 3 (*reward follows place*) independently of whether the lists
   are flattened. MLU's `LItemWeaponSwordBest` shows the surgical version.
5. **Don't forget `fLeveledActorMult*`.** Whichever lever we pick, four GMSTs decide how much
   vanilla's hand-placed `LevelModifier` layer still matters. Requiem and MLU made *opposite*
   choices here and both were deliberate. Ehlnofey must choose too, not inherit by default.
6. **`NeverResets` on any zone holding fixed reward.** Bone 3 is undone by a respawning vault.
7. **`Delev`/`Relev` are affordable if we truncate rather than replace.** Free compatibility with
   the entire Wrye Bash ecosystem is worth a great deal, and it is only available on the MLU side of
   the fork.

## 9. Open questions carried forward

1. **Verify the `ECZN` clamp semantics in-game.** Everything above rests on "zone min/max bounds the
   computed spawn level". Confirm it applies to both `LVLN`-resolved spawns *and* directly-placed
   `PcLevelMult` actors — MLU's design assumes both, and it is `[community]`, not `[verified]`.
2. **Does a zone clamp reach loot, or only actors?** MLU truncates `LVLI` separately, which hints
   the clamp does *not* govern item lists — but that is inference, not evidence.
3. **What happens at `MinLevel == MaxLevel`?** Does the engine handle a zero-width band cleanly?
   Cheapest possible in-game test, and it gates the whole design.
4. ~~Can SkyPatcher write `ECZN` bands at all?~~ **Answered: yes.**
   [`skypatcher.md`](../skypatcher/skypatcher.md) §4.3 — `minLevel`/`maxLevel` (plus `Add`/`Mult` variants) are
   directly settable, and `cell/encounterZone=` covers MLU's `C.Encounter` work. **MLU's entire
   approach is expressible as runtime rules with zero plugin overrides**, with two caveats: zones
   cannot be filtered by location keyword (they must be enumerated), and MLU's
   `fLeveledActorMult*` compression needs a plugin because SkyPatcher has no `GMST` support.
