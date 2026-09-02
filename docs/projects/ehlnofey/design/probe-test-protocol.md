---
id: "projects/ehlnofey/design/probe-test-protocol"
title: "Probe test protocol — the three gating in-game tests"
slug: "probe-test-protocol"
section: "projects/ehlnofey/design"
game: "skyrim"
kind: "design"
project: "ehlnofey"
mod: null
tags: ["ehlnofey", "deleveling", "design", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/design/probe-test-protocol.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 0, "unverified": 1, "upstream": 0, "verified": 10}
lines: 434
content_sha256: "0c5603917b33cb1d3fd3c4de37ab74dbf2ac9744abb082a14f86bf02c6167989"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Probe test protocol — the three gating in-game tests

`implementation-strategy.md` §9 step 1: *"Run the three tests. They can move a lot of work; do not
author against an assumption."* This document is the instrument and the script for that.

**The instrument is `src/EhlnofeyProbe/EhlnofeyProbeESP/` → `EhlnofeyProbe.esp`** — 4 records, all
overrides of `Skyrim.esm`, no new FormIDs, ESL-flagged. It is a **throwaway**: it is deliberately
not in `build/manifest.json`, and Phase 4 deletes it alongside `src/ExampleMod/`.

---

## 1. What the probe contains

| Record | FormKey | Vanilla | Probe | Why |
|---|---|---|---|---|
| `SwindlersDenZone` | `03EBE7:Skyrim.esm` | Min 6, no Max | **30 / 30** (T5) | Site A — low player, **high** zone |
| `UstengravZone` | `03EC83:Skyrim.esm` | Min 6, no Max, `NeverResets` | **4 / 4** (T1) | Site B — high player, **low** zone |
| `BleakFallsBarrowZone` | `038AB1:Skyrim.esm` | Min 6, Max 20 | **4 / 4** (T1) | Site C — loot A/B (this zone *does* reset) |
| `fSpecialLootMinPCLevelMult` | `10FEDE:Skyrim.esm` | 0.6 | **0** | Test 3 |

Levels are T1 and T5 from `tiers.md` (4 / 8 / 14 / 21 / 30 / 40 / 50).

**Deliberately *not* in the probe: the four `fLeveledActorMult*` GMSTs.** `tiers.md` §4 sets them to
0.70 / 0.85 / 1.00 / 1.25, but the probe leaves vanilla's **0.33 / 0.67 / 1.00 / 1.25** in place so
the tests measure *engine behaviour*, not Ehlnofey's tuning. Every predicted number below assumes
vanilla multipliers.

### Build it

```powershell
& $Tools.spriggitCli deserialize `
    --InputPath      "src/EhlnofeyProbe/EhlnofeyProbeESP" `
    --OutputPath     "dist/EhlnofeyProbe/EhlnofeyProbe.esp" `
    --PackageName    "Spriggit.Yaml.Skyrim" `
    --PackageVersion "0.40.0"
```

Then deploy with the `mod-deploy` skill, enable it **last** in the load order, and confirm it is
actually loaded before anything else (§2 step 0 — guardrail 5).

The YAML in `src/` **is** Spriggit's own canonical output, so a re-serialize round-trips on content.
Verify with `diff -r --strip-trailing-cr` — a plain `diff -r` reports every line changed, because
Spriggit writes CRLF and `.gitattributes` stores LF (see CLAUDE.md's gotchas).

---

## 2. The session

All three tests are one session, three `coc`s. Console commands are in `monospace`.

### Step 0 — prove the plugin is loaded (do not skip)

```
getgs fSpecialLootMinPCLevelMult
```

**Expect `0.00`.** If it returns `0.60`, the plugin is not loaded and *every* result below is a
vanilla reading that looks like a real answer. This is guardrail 5 in one line: rule out "never
loaded" before debugging "loaded but broken".

### Zone caching — why this needs a new game

`engine-behaviour.md` §0.3: a zone's level is computed on **first visit**, stored in the save, and
never recalculated until the zone resets. So:

- **Start a new game for each run.** From the main menu, `coc` skips character creation.
- **Ustengrav is `NeverResets`** — one save gets you exactly one Ustengrav reading, forever.
- Reach a *neutral* cell first, set the player level, and only then `coc` into the test dungeon.
  The zone attaches on that load, and it must attach at the level you intend.

---

## Test 1 — does `LevelModifier: None` honour the zone, or the player?

**Site: Ustengrav01. Player level 45, zone pinned to 4.**

```
coc WhiterunBanneredMare
player.setlevel 45
player.getlevel          ; confirm it took
coc Ustengrav01
```

Ustengrav01 is **the only cell in the base game with unmodified leveled humanoids** (§4). Four
bandits, no `LevelModifier`:

| Ref | `prid` | Base chain |
|---|---|---|
| `02137C` | `prid 0002137C` | `LvlBanditMelee2H` → `LCharBanditMelee2H` |
| `02137D` | `prid 0002137D` | `LvlBanditMeleeAny` → `LCharBanditMeleeAny` |
| `02137E` | `prid 0002137E` | `LvlBanditMissile` → `LCharBanditMissile` |
| `0213C6` | `prid 000213C6` | `LvlBanditMelee1H` → `LCharBanditMelee1H` |

Both bandit ladders are rungs at **L1 / L5 / L9 / L14 / L19 / L25**
(`LCharBanditMelee2H`, `LCharBanditMelee1H`), so the two outcomes are not subtle:

| If unmodified refs use… | Lookup level | Rung selected | You see |
|---|---|---|---|
| **the zone** (None ≙ Hard ×1.0) | 4 | **L1** | a plain *Bandit*, fur/hide, iron weapon, `getlevel` ≈ 1 |
| **the player** (docs read literally) | 45 | **L25** | a *Bandit Chief*-tier actor, high-tier gear, `getlevel` ≥ 25 |

```
prid 0002137C
enable
moveto player
getlevel
```

> **All four bandits are enable-parented to `07126E` = `MQ105EnableDungeonMarker`** `[verified]` —
> the main-quest marker for *The Horn of Jurgen Windcaller*. On a fresh `coc` with MQ105 unstarted
> their enable state is **`[unverified]`**, and if they are off, the cell simply looks empty and the
> test reads as a failure for the wrong reason. Hence the explicit `enable` + `moveto player` above:
> it works either way. This is also *why* these nine refs are unmodified — every one of the nine is
> quest-placed content, which is the population vanilla never hand-tuned.

Compare against a modifier-tagged neighbour in the same cell, e.g. `0235FF` (Medium, draugr —
0.67 × 4 ≈ 2) or `023600` (Easy, draugr). If the bandits read ~25 while the draugr read ~1–2, the
documentation is literal and unmodified refs ignore the zone.

**Verdict to record:** `None` ≙ zone / `None` ≙ player.

> **But read §4 first.** This test was originally sized as *"the single highest-value test in the
> project"*, on the grounds that a bad result forces explicit modifiers onto ~1,928 interior refs and
> roughly sextuples the plugin. **That estimate does not survive a census** — the real exposure is
> **9 records**, and `implementation-strategy.md` §7.1 now carries the correction. Run the test
> anyway (it is free, and it settles the semantics for anything Ehlnofey places itself), but it is no
> longer the thing the schedule hangs on. **Test 2 is the one to run first.**

---

## Test 2 — what level does NPC gear resolve at?

**Site: Swindler's Den. Player level 5, zone pinned to 30.**

This is the *upward* direction, and it is the clean one: any gear better than a level-5 character
could otherwise meet must have come from the zone, not the player.

```
coc WhiterunBanneredMare
player.setlevel 5
coc SwindlersDen01
```

Swindler's Den holds **22 modifier-tagged leveled bandits** — the densest such cell in the game, and
the only one carrying all four modifier classes. Predicted lookup levels at zone 30 with vanilla
multipliers:

| Modifier | Lookup | Rung (ladder 1/5/9/14/19/25) | Example ref | `getlevel` |
|---|---|---|---|---|
| Easy ×0.33 | 9 | **L9**, but Easy draws from *all* rungs ≤ 9, so L1/L5/L9 mixed | `042467` `LvlBanditMelee1H` | 1, 5 or **9** |
| Medium ×0.67 | 20 | **L19**, uniform across all Medium refs | `04244C` `LvlBanditMeleeAny` | **19** |
| Hard ×1.00 | 30 | **L25** | `04246A` `LvlBanditMissile` | **25** |
| Very Hard ×1.25 | 37 | `LCharBanditBoss` has an extra **L29** rung | `042469` `LvlBanditBoss` | **29** |

The rungs are nested `SubCharBandit0N*` lists resolving to `EncBandit0N*` NPCs, whose templates carry
**fixed** levels — `EncBandit01…06Template* = 1 / 5 / 9 / 14 / 19 / 25` `[verified]`. So `getlevel`
returns those numbers exactly; the tier index is legible in the EditorID (`EncBandit06…` = top rung).

> **One expected anomaly.** `EncBandit04TemplateMelee` (`01E60D`) is the vanilla `L=0` bug already
> recorded in CLAUDE.md — Ehlnofey sets it to 14. If a *melee* bandit that should be rung L14 reads
> level 0 or 1, that is the known bug, **not** a probe failure. None of the modifiers above land on
> rung L14 at zone 30, so it should not appear in this test.

Kill the Hard ref (`prid 0004246A`) and read what it was wearing:

- **Gear matches a level-25 bandit** (banded iron / scaled / dwarven-ish tier) → outfit lists resolve
  at **the NPC's own level**. `loot-model.md`'s working assumption holds and **no truncation pass is
  needed** — ~0 lists to edit.
- **Gear matches a level-5 character** (fur, hide, iron) → outfit lists resolve at **the player's
  level**. All **1,378** gated `LVLI` become live bone-1 leaks and the rules half grows from a
  handful of lines to a real job (`removeFromLLs`).

`getlevel` on the same ref cross-checks that the actor itself came in at the zone level — if the
actor is level 5, the zone never applied and the gear reading is meaningless.

**Verdict to record:** gear ≙ NPC level / gear ≙ player level.

---

## Test 3 — does zeroing `fSpecialLootMinPCLevelMult` zone-lock special loot, or kill it?

**Site: Bleak Falls Barrow. Player level 45, zone pinned to 4.** Use this dungeon rather than
Ustengrav: it resets normally, so the A/B is repeatable.

The three settings (`loot-model.md` §4) make the boss-chest special-loot roll:

- zone floor `0.4 × zoneLevel` = 1.6, zone ceiling `1.0 × zoneLevel` = 4
- **PC floor `0.6 × playerLevel` = 27** ← the leak

`BleakFallsBarrow02` holds a `TreasDraugrChestBoss` (`020671:Skyrim.esm`), which reaches the 88
`SpecialLoot`-flagged lists through its sublists.

**Run A — vanilla baseline.** New game, then:

```
coc WhiterunBanneredMare
setgs fSpecialLootMinPCLevelMult 0.6
player.setlevel 45
coc BleakFallsBarrow02
```

Open the boss chest. With the PC floor active the roll lands near **27** — expect genuinely good
gear in a zone pinned to level 4. *That is the bug being fixed*, and seeing it is the point of run A.

**Run B — the probe's value.** New game, do **not** touch `setgs` (the plugin already ships 0):

```
coc WhiterunBanneredMare
player.setlevel 45
coc BleakFallsBarrow02
```

| Chest contents | Meaning |
|---|---|
| Low-tier but **non-empty** — appropriate to a level-4 dungeon | **The change works.** Zone-locked special loot. Ship `0`. |
| **Empty**, or no special-loot item at all | Zero degrades to "no special loot" rather than "zone-only". **Revert to 0.6** and record a documented bone-1 exception, per `loot-model.md` §4 — losing boss chests is worse than the leak. |

Contents are rolled when the container is first loaded, so each arm needs its own first visit. That
is why this test uses a resetting zone and two fresh games.

**Verdict to record:** `0` works / `0` disables special loot.

---

## 4. A census that changes test 1's stakes

Run while selecting the probe site, over all **291 zoned interior cells** of `Skyrim.esm`
(`reference/Base/01Skyrim/Cells/`), resolving every `PlacedNpc`'s base through its template chain to
a terminal class. `[verified]`

| Base resolves to | no `LevelModifier` | modifier set | total |
|---|---|---|---|
| **`LVLN`** (a leveled ladder) | **9** | 2,138 | 2,147 |
| `NPC_` with a fixed level | 1,014 | 190 | 1,204 |
| `NPC_` with `PcLevelMult` | 83 | 45 | 128 |
| | **1,106** | 2,373 | **3,479** |

**`LevelModifier` only does anything when the placed ref's base resolves to a leveled list** — it is
a multiplier on the *list lookup level* (`engine-behaviour.md` §4). For a fixed-level NPC there is no
lookup to modify, and a `PcLevelMult` actor ignores zones entirely (§1) and is already the rules
half's job.

So the population at risk from a bad test-1 result is **9 records, not ~1,928**. The larger figure
counted unmodified placed refs without asking whether they had a leveled list behind them; 1,014 of
them are fixed-level corpses, skeletons, skeevers and quest NPCs, and 83 are `PcLevelMult`.

All 9:

| Cell | Zone | Refs |
|---|---|---|
| `Ustengrav01` | `03EC83` | `02137C` `02137D` `02137E` `0213C6` — the four bandits above |
| `WolfSkullCave02` | `03EC8E` | `09DA1F` `09DA20` `09DA21` `09DA22` — `MS06NecromancerCultist1–4` |
| `SnaplegCave01` | `03EC73` | `0694D1` — `LvlDeer` |

Even in the worst case the fix is 9 placed-ref overrides, or simply accepting them.

**Scope of the census:** `Skyrim.esm` interiors only. `Worldspaces/` and the DLC are not covered, and
per CLAUDE.md's DLC trap (b) they must be checked separately rather than extrapolated.

**This supersedes the sizing of the `LevelModifier` test across the Phase 3 design docs** — the claim
that a bad result forces ~1,928 placed-ref edits and "roughly *sextuples* the plugin". All four
affected documents now carry the correction:

| Document | What changed |
|---|---|
| `implementation-strategy.md` | new **§7.1** holds the correction in full; §7's table row, §5.2 and §9 step 1 adjusted to match |
| `tiers.md` | §4 *"The unresolved `None` case"* gains a revision note and a rewritten contingency table; §11 item 3 and §12 item 1 downgraded |
| `engine-behaviour.md` | §7 item 1 gains a revision note; §4 implication 2's "second bone-1 leak" scoped to nine records |
| `CLAUDE.md` | *Current phase* no longer says two tests can move work across the plugin/rules line |

`enemy-taxonomy.md` §5's raw count of 1,928 unmodified interior refs is **correct as a count** and is
left alone — it is the inference drawn from it, not the census, that was wrong.

**The consistent verdict across all of them:** the `None` test is still open and still worth running,
but it is routine. The test that can still move a large amount of work is **gear resolution**
(test 2), and it should be run first.

---

## 5. Results — run 2026-07-28, all `[verified]` in-game

| Test | Verdict |
|---|---|
| 1 — `LevelModifier: None` | **Honours the zone.** None ≙ Hard ×1.0. Nothing to do — not even the 9 |
| 2a — actor levels under a zone clamp | **Works exactly as designed.** Every modifier class landed on its predicted rung |
| 2b — NPC **gear** resolution | **Resolves at the PLAYER's level.** The working assumption was wrong — see §6 |
| 3 — `fSpecialLootMinPCLevelMult` = 0 | **Zone-locks, does not disable.** Ship `0` |

**Test 1** — Ustengrav pinned to 4. The four unmodified `MQ105`-parented bandits read low at player
45 *and* at player 5. The player-45 arm is the discriminating one: zone-bound. The CK wiki's "None →
the player's level" wording is sloppy, not literal. `tiers.md` §4's contingency table and
`engine-behaviour.md` §4 implication 2 are both resolved in the cheap direction.

**Test 2a** — Swindler's Den pinned to 30, observed at player 5 and player 45, **identical both
times**. Levels seen: **1 / 5 / 9 / 19 / 28**, against predicted Easy → 1, 5 or 9 · Medium → 19 ·
Very Hard → 28. (The protocol predicted 29 for the boss: 29 is the *rung gate*, the
`EncBandit06Boss1H*` NPCs carry a fixed **`L=28`**. Corrected above.) **This is the mod's whole
thesis working**: a level-5 character and a level-45 character met the same fixed dungeon.

**Test 3** — Bleak Falls Barrow pinned to 4, player 45. Vanilla arm (`setgs … 0.6`) produced a
**glass dagger** — a T5 material out of a T1 dungeon, the bone-1 leak in its purest form. Probe arm
(`0`) produced a few items and one low-tier enchanted piece, **identical at player 1 and player 45**.
Zeroing the PC floor zone-locks special loot rather than disabling it. The feared "empty chest"
failure mode did not occur.

---

## 6. The one failure: gear resolves at the player's level

**Observation** `[verified]`: the Swindler's Den bandit chief was **level 28 in both runs**, but wore
**iron at player level 5 and Nordic at player level 45**.

The three candidate operands are fully separated by that single observation:

| If gear resolved at… | Value in both runs | Predicted gear | Matches? |
|---|---|---|---|
| the **NPC's** level | 28 / 28 | identical | ✗ |
| the **zone** level | 30 / 30 | identical | ✗ |
| the **player's** level | 5 / 45 | **different** | **✓** |

Only player level varied between the runs, so it is the only operand that can explain the change.

**Consequences:**

1. **`enemy-taxonomy.md` §4 was right and `engine-behaviour.md` §3 was wrong.** §3 asserted
   *"outfit/inventory lists resolve against the NPC's own level"*; §4 asserted *"fixing an NPC's tier
   does not fix its equipment"*. `loot-model.md` §3 flagged the contradiction, adopted §3's reading as
   its working assumption, and marked the whole of §6's cost estimate contingent on it. **That
   contingency has now failed.**
2. **`loot-model.md`'s headline claim does not survive.** §1's *"the tier ladder IS the material
   ladder… no truncation pass needed"* depends on the zone tier reaching gear through the actor. It
   does not. Bone 3 does **not** fall out of the difficulty map for free.
3. **MorrowLoot Ultimate's truncation pass was necessary after all.** Phase 3 concluded MLU's
   ~400-list edit was redundant; MLU does both the `ECZN` clamp *and* the list truncation, and this
   result says that is why. Phase 2's reading of MLU stands; Phase 3's inference from it does not.
4. **Scope moves.** Up to **1,378** player-gated `LVLI` are live bone-1 leaks. SkyPatcher can reach
   them (`removeFromLLs`), so it lands in the rules half — but that half stops being "tens of lines"
   and becomes the largest single job in the mod.

### 6.1 Second run — the mechanism, traced end to end

Second observation `[verified]`: the same chief kept **one constant item** across both player levels
(a dagger) while **every other slot moved** — iron boots/cuirass/gauntlets → Nordic, iron axe →
dwarven sword.

That splits the inventory cleanly, and the records explain it exactly:

| Source on `EncBandit06Boss1H*` | Shape | Behaviour |
|---|---|---|
| `Items:` → `ElvenDagger` (`01398E` = Orcish on the Imperial-M variant) | **flat, non-leveled form** | **constant** ✓ |
| `Items:` → `LItemBanditBossWeapon1H` (`03DF1C`) | leveled but **all entries `Level: 1`** — picks the *type* | random axe/sword/mace ✓ |
| ↳ `LItemBanditBossSword` / `…Mace` / `…WarAxe` | **gated 1 / 6 / 9 / 12 / 19 / 27 / 36** | material tracks player ✓ |
| the outfit's armour lists | gated the same way | iron → Nordic ✓ |

**9 of the 10 `EncBandit06Boss*` variants carry a flat `ElvenDagger`** in `Items:` `[verified]` —
the constant item was not a fluke of one actor.

The sword ladder resolves to **Steel 1 · Orcish 6 · Dwarven 12 · Elven 19 · Glass 27 · Ebony 36**
`[verified]`. Two things follow:

1. **`loot-model.md` §1's material ladder was correct.** T1–T7 really do land on
   Steel/Orcish/Dwarven/Elven/Glass/Ebony/Daedric, one rung each. The error was never the ladder —
   it is that the ladder is **indexed by player level**, and there is no zone hook on it at all.
2. **`CalculateFromAllLevelsLessThanOrEqualPlayer` is set on these lists**, so every rung ≤ the
   player's level is eligible and one is picked uniformly. That is why player 5 gave iron (only the
   bottom rung was eligible) and player 45 gave *dwarven* rather than the top rung (everything was
   eligible). It also means the fix is **truncation** — deleting rungs above a cap — which is
   precisely MLU's method and precisely what SkyPatcher's `removeFromLLs` does.

### 6.2 Correction — gear *can* follow the place, transitively

An earlier draft of this section concluded that random worn gear **"cannot be made to follow the
place"** and could "only be capped, not redirected". **That is wrong** and is retracted here.

It is true that the *list* has no zone operand — nothing about `LItemBanditCuirass` can be made to
consult an `ECZN`. But gear does not need to reach the zone directly, because **the zone already
picks the actor, and the actor picks the gear**:

```
zone level  →  LVLN rung  →  EncBandit0N  →  DefaultOutfit  →  material list  →  item
   fixed        fixed         fixed          ← the only player-gated hop is here
```

Everything left of the outfit is already deterministic and already verified (test 2a). If the list at
the end is **flat**, the whole chain is deterministic and player level drops out entirely.

**What actually blocks it in vanilla is sharing, not the engine.** `EncBandit01Melee1HNordM`,
`EncBandit03…` and `EncBandit06…` all point at the **same** `DefaultOutfit: 0C0197`
(`BanditArmorMeleeShield20Outfit`), shared by **90 NPCs** `[verified]`. Vanilla makes tier-1 and
tier-6 bandits differ by letting one player-gated list serve both. De-share that and the tiers
separate permanently.

Its four lists `[verified]`:

| List | FormKey | Gates |
|---|---|---|
| `LItemBanditCuirass` | `037C22` | 1, 6, 7, 8, 9, 19, 20, 21, 22, 25, 26, 27, 28 |
| `LItemBanditBoots` | `037C23` | same |
| `LItemBanditGauntlets50` | `037C25` | same |
| `LItemBanditShield20` | `0C0196` | 1, 12, 13, 14, 15 |
| `LItemBanditWeapon1H` | `037C1B` | **flat already** — picks type, not material |

### 6.3 The three instruments, cheapest first

| # | Instrument | Result | Cost |
|---|---|---|---|
| **1** | **Truncate the shared lists** — `removeFromLLs=<list>~><N>~none` | one gear ceiling for the whole archetype, everywhere, at any player level | **~5 SkyPatcher lines.** No new records |
| **2** | **Per-tier outfits** — new flat lists + new outfits, repoint each `EncBandit0N*` | gear follows the **place**, via the actor. Full bone 3 | new records + ~90 NPC repoints *per outfit family*; whether SkyPatcher can set `DefaultOutfit` is **unchecked** (it can `filterBy` outfit and `formsToReplace` within one) |
| **3** | **Literal forms in `Items:`** — the `ElvenDagger` pattern | absolute, unconditional guarantee on one actor | 1 record each; only sane for signature NPCs |

Note truncation does **not** cost variety: the gates cluster (1 / 6–9 / 19–22 / 25–28), so keeping
everything `≤ 9` still leaves iron *and* steel variants in the pool. Flat ≠ single item.

**Recommendation for `loot-model.md`:** instrument 1 as the global floor-and-ceiling (cheap, immediate,
kills the bone-1 leak), instrument 2 for the two or three archetypes whose tier spread the player
actually reads — bandits and draugr — and instrument 3 for named bosses. Instrument 2 is what makes
bone 3 true rather than merely capped, and it reopens the ESL question, since per-tier lists and
outfits are the mod's **first new records**.

**Still open:** whether hand-placed unique gear is unaffected (it should be — `ElvenDagger` is the
proof of shape), and whether SkyPatcher's `npc/` module can set `DefaultOutfit`. Both are
`loot-model.md` questions, not further in-game tests.

This does **not** touch tests 1, 2a or 3, all of which passed. The places are fixed; it is the gear
on the actors standing in them that still scales.

---

## Sources

`design/engine-behaviour.md` §0.3, §1, §3, §4, §7 · `design/tiers.md` §4 · `design/loot-model.md`
§3, §4 · `design/implementation-strategy.md` §7, §9 · `reference/Base/01Skyrim/EncounterZones/` ·
`reference/Base/01Skyrim/Cells/` · `reference/Base/01Skyrim/LeveledNpcs/` ·
`reference/Base/01Skyrim/GameSettings/`
