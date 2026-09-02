---
id: "projects/ehlnofey/design/tiers"
title: "Tiers — the fixed ladder"
slug: "tiers"
section: "projects/ehlnofey/design"
game: "skyrim"
kind: "design"
project: "ehlnofey"
mod: null
tags: ["ehlnofey", "deleveling", "design", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/design/tiers.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: "Phase 3, document 2"
confidence: {"author": 0, "community": 2, "unverified": 7, "upstream": 0, "verified": 19}
lines: 530
content_sha256: "94cead0ec9776db7a336f1055f5df30b5078432946ec130ba32679167f13f79c"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Tiers — the fixed ladder

**Phase 3, document 2.** The ladder every place and every enemy in Ehlnofey is assigned to, what each
rung means numerically, and what it actually spawns.

Read `engine-behaviour.md` first — this document is built directly on its five answers and does not
re-derive them. Inputs: `world/enemy-taxonomy.md` (the archetype ladders), `world/lore-constraints.md`
(the tier *names*), `world/dungeons.md` §2 (vanilla's type→level ladder), `prior-art/morrowloot.md`.

Confidence marks as elsewhere: `[verified]` = read in `reference/` or computed from it, `[community]`
= established knowledge not re-tested here, `[unverified]` = plausible, unchecked.

---

## 1. What a tier is

A tier is **one number, `N`**, written into an encounter zone as `MinLevel = MaxLevel = N`. Everything
else follows from the engine:

```
ECZN.MinLevel = MaxLevel = N
        │
        ├─ zoneLevel = clamp(playerLevel, N, N) = N            ← for every player level, forever
        │
        └─ per placed actor, list lookup level = N × LevelModifier
             Easy 0.70 · Medium 0.85 · Hard 1.00 · VeryHard 1.25
                       │
                       └─ highest LVLN gate ≤ lookup  →  the actual NPC record and its static level
```

So a tier assignment is **not** "these enemies are level N". It is *"this place resolves its leveled
lists at N"*, and what that produces differs per archetype — a T4 bandit camp yields level-19
Plunderers while a T4 Falmer hive yields level-15 Skulkers. §5 tabulates all of it.

Three consequences worth stating plainly, all from `engine-behaviour.md`:

1. **The tier is computed once, on first entry, and stored in the save** (§0.3). Tiers apply fully on
   a new game; on an existing save they reach only unvisited or since-reset zones.
2. **The tier does not reach `PcLevelMult` actors** (§1). Guards, soldiers, hunters, Nightingales and
   all three final bosses ignore it entirely and need per-NPC fixing — §7.
3. **The tier does reach loot** generated in the zone's cells (§3), which is why `loot-model.md` keys
   off this same ladder rather than defining its own.

---

## 2. The finding that sets the ladder's range

> **Vanilla's encounter-zone floors cannot be ratified as fixed levels. Freezing them would delete
> the top half of the game.**

`dungeons.md` §5.1 recommended that `tiers.md` "ratify" vanilla's type ladder (2/6/8/14/16/18/24)
rather than invent one. That recommendation was made before `engine-behaviour.md` established the
clamp semantics, and under `Min == Max` it is **wrong**. The census, `[verified]` over
`reference/Base/*/EncounterZones/`:

| Plugin | Zones | `MinLevel` distribution | Max |
|---|---|---|---|
| `Skyrim.esm` | 280 | 0×2, 1×2, **2×36**, 5×7, **6×129**, **8×38**, 10×5, 12×12, 14×19, 16×6, 18×15, 24×9 | **24** |
| `Dawnguard.esm` | 19 | 0×4, 6×2, 10×3, 13×3, 15×1, 16×1, 18×5 | 18 |
| `Dragonborn.esm` | 57 | 0×2, 6×8, 10×23, 20×4, 25×14, 30×5, **40×1** | **40** |

**73% of Skyrim's zones sit at level ≤ 8** (203 of 280), 46% at exactly 6, and **nothing in Skyrim
proper exceeds 24**. Now set that against what the content ladders actually contain
(`enemy-taxonomy.md` §2):

| Archetype | Top rung vanilla ships | Reachable if zones freeze at ≤24? |
|---|---|---|
| Draugr Deathlord | gate 30 | **no** |
| Draugr boss (top) | gate 50, gate 60 w/ Dragon Priest | **no** |
| Dremora Valkynaz | gate 46 | **no** |
| Volkihar / Volkihar Master | gate 48 / 53 (60 w/ Dawnguard) | **no** |
| Falmer Shadowmaster | gate 38 | **no** |
| Arch Conjurer | gate 46 | **no** |
| Ancient Dragon | gate 45 | **no** |
| Forsworn Ravager / Warlord | gate 34 / 46 | **no** |

Vanilla reached those rungs **exclusively through player level** — the zone floor never mattered
because the player always climbed past it. Remove the climb and every rung above ~25 becomes dead
content: records that exist in the plugin and can never spawn anywhere. That is a strictly worse
world than vanilla, and it is the failure mode a naive "freeze the numbers" pass walks into.

**The prior art agrees.** MorrowLoot Ultimate — the one shipped mod that made encounter zones its
difficulty map — did not ratify vanilla's floors either. `[verified]` over
`reference/mods/MLUYaml/EncounterZones/` (360 zones):

- vanilla's `MinLevel` range 0–24 becomes MLU's **5–64**, median ≈ 27
- only 6 of 360 zones sit below level 10; MLU **raises the floor** as hard as it raises the ceiling
- its most common band is **30–40** (31 zones), and it uses bands up to 50–65

So MLU roughly **quintupled the floor and tripled the ceiling** of vanilla's zone ladder. Ehlnofey
must stretch too. The open question is not *whether* but *how far*, and §9 says that honestly.

MLU also declines to go zero-width: 357 of its 360 zones keep a `+10` (low) to `+15` (high) band, and
only three are `Min == Max` (`engine-behaviour.md` §2). **Ehlnofey is taking a stricter reading of
bone 1 than MLU did** — that is a deliberate difference, not an oversight, and it is the single
biggest untested assumption in this document.

---

## 3. The ladder

**Seven rungs.** T1–T6 are the working ladder; T7 is a capstone used by name only.

| Tier | `N` | Step | Identity | Typical content |
|---|---|---|---|---|
| **T1** | **4** | — | *Nuisance.* Wildlife, drifters, the tutorial corridor. | animal dens, the weakest bandit camps |
| **T2** | **8** | +4 | *Local trouble.* A problem for a village, not a Thane. | bandit camps, shipwrecks, minor caves |
| **T3** | **14** | +6 | *Established threat.* Organised, armed, dug in. | forts, Forsworn camps, ordinary crypts |
| **T4** | **21** | +7 | *Serious.* The point where an unprepared character dies. | Dwemer ruins, Falmer hives, hagraven nests |
| **T5** | **30** | +9 | *Deep.* Named bosses, word walls, the deeper barrows. | Dragon Priest lairs, deep Nordic ruins |
| **T6** | **40** | +10 | *Apex.* The top of what the province holds. | Solstheim's peak, Apocrypha, Volkihar's court |
| **T7** | **50** | +10 | *Capstone.* Not a band — a short named list. | see §8 |

### Why these numbers

- **The steps are the draugr ladder.** Vanilla's deepest and most lore-anchored ladder gates at
  1 / 6 / 13 / 21 / 30 / 40 (`enemy-taxonomy.md` §2.2). T4, T5 and T6 are *exactly* those gates; T1–T3
  lift the bottom three rungs (1→4, 6→8, 13→14) to buy internal texture that a zone level of 1 cannot
  have — at `N=1`, Easy and VeryHard both resolve to gate 1 and the dungeon is uniform.
- **Steps widen with height** (+4, +6, +7, +9, +10), matching how every vanilla ladder is spaced. A
  rung is roughly a constant *ratio*, not a constant number of levels.
- **T6 = 40 is the top of the shipped world**, not an invention: `DLC2GyldenhulBarrowZone` is a
  vanilla `MinLevel: 40`. `[verified]`
- **T7 = 50 exists to unlock three specific things** and nothing else — the gate-50 and gate-60 rungs
  of `LCharDraugrBoss` (including Dragon Priest attachment), Dawnguard's gate-60 vampire, and the
  Forsworn boss's gate-58. At `N=50`, VeryHard resolves at 62.5 and reaches all of them. Used
  anywhere else it is indistinguishable from T6 (§5).

### What is *not* in the ladder

There is no T0. The lowest meaningful rung is T1, and below it the distinction stops existing: the
creature lists that populate trivial places are **class B/C** (`enemy-taxonomy.md` §6) — their levels
are fixed on the creature record and the zone level only chooses the *species*. A wolf is level 2 in
a T1 den and level 2 in a T6 barrow.

---

## 4. The `LevelModifier` decision

`LevelModifier` is vanilla's hand-placed per-actor texture, on **5,685 of 10,504 placed refs**
(`dungeons.md` §2). Under a fixed zone it stops being a scaling artefact and becomes Ehlnofey's
**only** intra-dungeon gradient — the difference between the entry corridor and the boss room.

`engine-behaviour.md` §4: the four values are the `fLeveledActorMult*` GMSTs, applied to the resolved
zone level as the list-lookup level. The prior art disagrees on them, `[verified]` from
`reference/Base/01Skyrim/GameSettings/` and `reference/mods/MLUYaml/GameSettings/`:

| GMST | FormKey | Vanilla | MLU | **Ehlnofey** |
|---|---|---|---|---|
| `fLeveledActorMultEasy` | `01A1D9:Skyrim.esm` | 0.33 | 0.70 | **0.70** |
| `fLeveledActorMultMedium` | `01A1DB:Skyrim.esm` | 0.67 | 0.90 | **0.85** |
| `fLeveledActorMultHard` | `01A1DA:Skyrim.esm` | 1.00 | **1.10** | **1.00** *(unchanged)* |
| `fLeveledActorMultVeryHard` | `023C0B:Skyrim.esm` | 1.25 | 1.30 | **1.25** *(unchanged)* |

> **Correction to CLAUDE.md.** The machinery table records MLU as compressing "to 0.7–1.3". The
> endpoints are right but the interior is not: MLU's Hard is **1.1**, not 1.0. MLU therefore pushes
> *every* Hard-tagged actor one notch above its zone's nominal level. No doc in this repo recorded
> that. `[verified]`

**Three decisions, with reasons:**

1. **Easy 0.33 → 0.70.** Vanilla's Easy is unusable in a fixed world. Easy is the **modal**
   placement — 1,482 of 4,452 interior placed refs, 33% — so whatever it resolves to *is* substantially
   the dungeon's identity. At 0.33 a T5 crypt's most common enemy is a level-6 Restless Draugr, four
   rungs below the tier, and the tier's identity collapses. §6 tabulates the difference.
2. **Hard stays 1.00.** This is where Ehlnofey departs from MLU, deliberately. With Hard = 1.0 the
   zone's number *is* the level in the room, exactly — "a T5 crypt is a level-30 crypt" is true rather
   than approximately true. Under bone 2 that identity is worth more than the extra notch of
   difficulty MLU's 1.1 buys, and it makes every table in this document exact rather than indicative.
3. **VeryHard stays 1.25.** VeryHard is overwhelmingly how vanilla marks a *boss* ref
   (`dungeons.md` §2), and 1.25 is what Bethesda tuned those placements against. It is also what makes
   the ladder work: VeryHard at 1.25 is precisely how each tier reaches the boss rung above its
   rank-and-file (§5, table C). Changing it would require re-tuning 218 boss placements to no benefit.

**Cost: two GMST overrides.** Not four. This is the cheapest possible expression of the intra-dungeon
gradient and it is one of the handful of things a rule engine cannot do (`skypatcher.md` §5), so it
lands in the plugin half of the hybrid.

### The unresolved `None` case

**43% of interior placed refs carry no `LevelModifier` at all** (1,928 of 4,452). The CK wiki
documents the unmodified case as resolving against *the player's level* — which, taken literally,
would appear to mean nearly half of every dungeon's population ignores the tier completely and
Ehlnofey's whole architecture leaks. `engine-behaviour.md` §4 flags this `[unverified]` and §7 makes
it one of the two remaining in-game tests.

Confirming here that **the engine exposes no setting for it**: `[verified]` — the GameSettings folder
contains `fLeveledActorMultEasy/Medium/Hard/VeryHard` and no `…None`. So if the literal reading holds
there is no cheap global fix.

> **Revised — the contingency is 9 records, not ~1,928.** The paragraph above counts unmodified
> placed refs without asking whether the engine can *do* anything with a modifier on them.
> `LevelModifier` multiplies the **leveled-list lookup level** (`engine-behaviour.md` §4), so it is
> inert unless the ref's base resolves through its template chain to an `LVLN`: a fixed-level `NPC_`
> has no lookup to modify, and a `PcLevelMult` actor ignores zones outright (§1) and belongs to the
> rules half regardless. Census over all 291 zoned interior cells of `Skyrim.esm` `[verified]`: of
> **2,147** placed refs backed by a leveled ladder, **2,138 already carry a modifier and 9 do not**.
> The other 1,097 unmodified refs are 1,014 fixed-level corpses/skeletons/skeevers/quest NPCs and 83
> `PcLevelMult` actors. Method, the full list of nine, and the scope caveat (base-game interiors
> only) are in `probe-test-protocol.md` §4; the correction is folded into
> `implementation-strategy.md` §7.1.

| If the test shows… | Then |
|---|---|
| **None ≙ Hard (×1.0)** — the natural reading | nothing to do. The ladder works as written. |
| **None ≙ player level** — the literal reading | **9** interior placed refs need an explicit `LevelModifier` written onto them (`Ustengrav01` ×4, `WolfSkullCave02` ×4, `SnaplegCave01` ×1). Still a `PlacedNpc` edit inside `Cells/`, which **SkyPatcher cannot reach** — but 9 records against a ~376-record plugin does not move the architecture. |

**Run it anyway** — it is one console command in one dungeon, and it settles the semantics for any ref
Ehlnofey places itself. But it no longer needs to run *before* the difficulty map, and it is no longer
the project's highest-value test: that is now the **gear-resolution** test (`loot-model.md` §3), which
is still worth up to 1,378 `LVLI`.

---

## 5. What each tier actually spawns

Computed by resolving each archetype's `LVLN` gates (`enemy-taxonomy.md` §2, every ladder
`[verified]` against its cited FormKey) at each tier's lookup level. Names from `lore-constraints.md`
§1 — under a fixed world these are the **UI**, and keeping them aligned with power is a hard
constraint.

### A. The rank-and-file rung — `Hard`, ×1.00

| Archetype | T1=4 | T2=8 | T3=14 | T4=21 | T5=30 | T6=40 | T7=50 |
|---|---|---|---|---|---|---|---|
| **Bandit** (melee 1H) | Bandit 1 | Outlaw 5 | Highwayman 14\* | Plunderer 19 | Marauder 25 | *(sat.)* | *(sat.)* |
| **Draugr** (melee) | Draugr 1 | Restless 6 | Wight 13 | Scourge 21 | Deathlord 30 | *(gear only)* | *(gear only)* |
| **Forsworn** | Forsworn 1 | Forager 6 | Looter 14 | Looter 14 | Pillager 24 | Ravager 34 | *(sat.)* |
| **Warlock / Conjurer** | Wizard 1 | Apprentice 6 | Adept 12 | Conjurer 19 | Ascendant 27 | Master 36 | Arch 46 |
| **Dremora** | Churl 6 | Churl 6 | Caitiff 12 | Kynval 19 | Kynreeve 27 | Markynaz 36 | Valkynaz 46 |
| **Vampire** | Fledgling 1 | Vampire 6 | Blooded 12 | Mistwalker 20 | Nightstalker 28 | Ancient 38 | Volkihar 48 |
| **Falmer** | Falmer 9 | Falmer 9 | Falmer 9 | Skulker 15 | Nightprowler 30 | Shadowmaster 38 | *(sat.)* |
| **Thalmor** | 4 | 4 | 12 | 20 | 28 | 36 | *(sat.)* |
| **Dwarven automaton** | Spider 6 | Spider 6 | Spider 6 | Sphere 16 | Sphere 24 | Centurion 36 | *(sat.)* |
| **Dragon** | Dragon 10 | Dragon 10 | Dragon 10 | Blood 20 | Frost 30 | Elder 40 | Ancient 50 |

\* after fixing the vanilla `L=0` bug on `EncBandit04TemplateMelee` (`01E60D`) — see §10.
*(sat.)* = saturated: the ladder has no higher rung, so the tier buys nothing over the one before it.

### B. The internal gradient — full modifier spread, Ehlnofey multipliers

**Draugr** — the spine

| Tier | Easy 0.70 | Medium 0.85 | Hard 1.00 | VeryHard 1.25 |
|---|---|---|---|---|
| T1=4 | Draugr 1 | Draugr 1 | Draugr 1 | Draugr 1 |
| T2=8 | Draugr 1 | Restless 6 | Restless 6 | Restless 6 |
| T3=14 | Restless 6 | Restless 6 | **Wight 13** | Wight 13 |
| T4=21 | Wight 13 | Wight 13 | **Scourge 21** | Scourge 21 |
| T5=30 | Scourge 21 | Scourge 21 | **Deathlord 30** | Deathlord 30 |
| T6=40 | Scourge 21 | Deathlord 30 | **Deathlord (ebony) 30** | Deathlord (ebony) 30 |
| T7=50 | Deathlord 30 | Deathlord (ebony) 30 | Deathlord (ebony) 30 | Deathlord (ebony) 30 |

**Dremora** — the lore calibration reference (`lore-constraints.md` §5.2)

| Tier | Easy | Medium | Hard | VeryHard |
|---|---|---|---|---|
| T3=14 | Churl 6 | Churl 6 | **Caitiff 12** | Caitiff 12 |
| T4=21 | Caitiff 12 | Caitiff 12 | **Kynval 19** | Kynval 19 |
| T5=30 | Kynval 19 | Kynval 19 | **Kynreeve 27** | Markynaz 36 |
| T6=40 | Kynreeve 27 | Kynreeve 27 | **Markynaz 36** | Valkynaz 46 |
| T7=50 | Kynreeve 27 | Markynaz 36 | **Valkynaz 46** | Valkynaz 46 |

The six-caste ladder maps onto T2–T7 one rung per tier with the Valkynaz rare at the top — which is
exactly what *Varieties of Daedra* describes. **The tier system passes lore-constraints' §5.2 test.**

**Vampire** — the deepest ladder, and the one that justifies T7

| Tier | Easy | Medium | Hard | VeryHard |
|---|---|---|---|---|
| T5=30 | Mistwalker 20 | Mistwalker 20 | **Nightstalker 28** | Nightstalker 28 |
| T6=40 | Nightstalker 28 | Nightstalker 28 | **Ancient 38** | Volkihar 48 |
| T7=50 | Nightstalker 28 | Ancient 38 | **Volkihar 48** | Volkihar (DG) 60 |

**Falmer** and **Dwarven automatons** are flat below T4 (their ladders' second gates are 15 and 16),
which is why they cannot occupy a low tier — see §6.

### C. What the boss ref reaches — `VeryHard`, ×1.25

The design property that makes the ladder work: a tier's VeryHard placement lands one rung *above* its
rank-and-file, so a boss reads as a boss without any record edit.

| Boss list | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
|---|---|---|---|---|---|---|---|
| Bandit boss | 6 | 6 | 10 | 21 | 28 | 28 | 28 |
| **Draugr boss** | 7 | 7 | 15 | 24 | 34 | **50** | **50 + Dragon Priest** |
| Forsworn boss | 7 | 7 | 7 | 16 | 27 | 38 | **51** |
| Vampire | 1 | 6 | 12 | 20 | 28 | **48** | **60** |
| Dragon | 10 | 10 | 10 | 20 | 40 | 50 | 50 |

T6 and T7 are where the game's top content finally becomes reachable — and it is reachable **only**
through a VeryHard placement in a T6/T7 zone. That is the entire justification for the capstone rung.

---

## 6. Archetype home bands

Falling straight out of table A: each archetype has a range of tiers over which its ladder actually
*differentiates*. Outside it, a tier assignment buys nothing.

| Archetype | Home band | Why bounded |
|---|---|---|
| Animals / ambient | **T1–T2** | class B/C — levels fixed on the record; tier only picks species |
| **Bandit** | **T1–T5** | saturates at Marauder (gate 25). A T6 bandit camp is a T5 bandit camp. |
| **Forsworn** | **T1–T6** | melee list tops at Ravager (gate 34) |
| **Draugr** | **T2–T6** | levels cap at 30; T6 adds ebony *gear* at the same level |
| **Vampire** | **T2–T7** | deepest ladder in the game (gate 60 with Dawnguard) |
| **Warlock / Conjurer** | **T1–T7** | the only ladder that differentiates across the whole range |
| **Dremora** | **T3–T7** | second gate is 12 |
| **Thalmor** | **T3–T6** | second gate is 12; tops at 36 |
| **Falmer** | **T4–T6** | second gate is **15** — flat below T4 |
| **Dwarven automaton** | **T4–T6** | second gate is **16** — flat below T4 |
| **Dragon** | **T4–T7** | second gate is 18 |
| **Dragon Priest** | *(any)* | class C, fixed 50 (Solstheim's Acolytes 60) — ignores the tier entirely |

**This independently reproduces Bethesda's own floors.** `dungeons.md` §2 found vanilla assigns
FalmerHive 18, DwarvenAutomatons 16, DragonLair 10, DragonPriestLair 24 — precisely the archetypes
whose ladders do not differentiate below ~15. Bethesda's zone floors encode the same structural fact
this table derives from the ladders. That is a strong consistency check on both.

**Direct instruction to `difficulty-map.md`:** never assign a dungeon a tier outside its archetype's
home band. A T6 bandit camp and a T2 Dwemer ruin are both no-ops — the records will not notice.

---

## 7. Class D — the actors the tier cannot reach

`engine-behaviour.md` §1: `PcLevelMult` actors compute against the **raw player level** and ignore the
zone. They are the ~454 records in `Skyrim.esm` that genuinely scale (`enemy-taxonomy.md` §2.6), and
without fixing them bone 1 fails no matter how good the zone map is.

Each becomes a **fixed level chosen from the ladder**, not a place assignment — these actors move
around, so they get one number each:

| Cluster | Vanilla | **Ehlnofey** | Reasoning |
|---|---|---|---|
| City **guards** (`LCharGuardImperial` `0E7B2C` &c.) | ×1, [20–50] | **21 (T4)** | Guards should beat a competent bandit and lose to a Deathlord. Vanilla's [20–50] is why they are unkillable at level 5 and trivial at 50; 21 is the bottom of that band, made honest. |
| Imperial / Stormcloak **soldiers** | ×0.25, [1–50] | **14 (T3)** | Rank-and-file line troops. Below their own guards, which matches the Civil War's fiction. |
| **Hunters** (`LCharHunter` `073FC2`) | ×0.5, [5–15] | **8 (T2)** | Civilians with bows. Vanilla's band already says this. |
| **Nightingales** (`LCharNightingaleMelee` `0E0CE2`) | ×1, [15–45] | **30 (T5)** | Agents of Nocturnal; must read as elite. |
| `WE*` world encounters | various | **per encounter, T1–T3** | Roadside content. `difficulty-map.md` assigns; default T2. |
| **Zahkriisos** (`0248E8:Dragonborn.esm`) | ×1, [25–60] | **60** | The only player-scaled Dragon Priest, and `enemy-taxonomy.md` §2.2 calls it an oversight. 60 matches his fixed siblings Ahzidal and Dukaan exactly. |

**Lever:** SkyPatcher `filterByPCLevelMult` + `level` — precisely what that filter exists for
(`skypatcher.md`). No plugin records required for any row above except where a DLC master is already
taken. This is the strongest single argument for the hybrid: the one thing zones structurally cannot
do is the one thing the rule engine does natively.

---

## 8. Bone-1 exceptions, decided

Bone 1 admits no scaling. Three enemies have a real claim to an exception, and CLAUDE.md requires the
decision be made explicitly rather than by default (`enemy-taxonomy.md` §2.2, §2.5).

**Verdict: no exceptions. All three are fixed.** The argument for exempting them — that they are met
at the end of a questline rather than by wandering — is an argument about *pacing*, and pacing is what
bone 2 handles (a questline is the most legible warning in the game). Granting the exception would
also mean the mod's three most memorable fights are the only ones that still scale, which inverts the
thesis at exactly the moment a player would notice.

| Boss | Vanilla | **Ehlnofey** | Constraint satisfied |
|---|---|---|---|
| **Alduin** (`08E4F1:Skyrim.esm`) | `PcLevelMult` ×1.2, [10–100] | **60** | Must outrank every dragon; the ladder tops at Ancient 50 (`lore-constraints.md` §3). |
| **Harkon** (`003BA7:Dawnguard.esm`) | ×1.2, [10–60] | **55** | Must sit above his own court. The Volkihar ladder reaches 48, its boss rung 53 — so 55 is the floor, not a preference. |
| **Harkon, Vampire Lord** (`01A93D:Dawnguard.esm`) | ×1.4, [10–60] | **60** | A separate record with its own level rule; **both must be edited** or the transformation is a downgrade. |
| **Miraak, final** (`01FB98:Dragonborn.esm`) | ×1.1, [35–150] | **65** | Must exceed Solstheim's fixed ceiling — Ahzidal and Dukaan at 60 are the highest fixed humanoids in the game. |
| **Miraak, base** (`017F7D:Dragonborn.esm`) | ×1, [35–200] | **65** | Same record family; `CalcMaxLevel: 200` is the highest in the game and pure scaling. |

The three absolute numbers (60 / 55–60 / 65) are **capstone values, not ladder rungs**, and they are
the most playtest-sensitive figures in this document — see §9.

### The twelve `LevelGate*` globals

`progression.md` §2: vanilla's only systematic level gate, withholding twelve *creature* types from
world encounters until the player is roughly their level (Spriggan 8 … Giant 24).

**Verdict: neutralise them** (set each to 1). They are a bone-1 violation by construction — gating a
spawn on player level *is* the world scaling to the player. The wilderness they protect is already
effectively deleveled above ~level 20 anyway (`enemy-taxonomy.md` §2.3: forest predators ceiling at a
level-16 cave bear, mountain predators at a level-22 frost troll), so the gates mostly shape the first
twenty levels and then stop mattering.

`lore-constraints.md` §4.4 attaches a condition to this and it is binding: **removing the gates
obliges the geography to carry the warning instead.** Frost trolls belong on mountains, and the player
must be able to see the mountain. That obligation is discharged in `difficulty-map.md`, not here.

> **Caveat — this does not by itself fix the overworld.** Neutralising the globals stops *one*
> scaling mechanism; the ambient lists themselves (`LCharAnimalForestPredator` `042297` and kin) still
> carry player-level gates, and most of the overworld has **no encounter zone at all** to clamp them
> (`dungeons.md` §2: 28 dungeons unzoned, and open wilderness is largely unzoned by design). So for
> exteriors "tier" is currently **undefined**, and zone-based tiering cannot reach them. This is a real
> hole in the architecture, it is not solved in this document, and it must be closed in
> `difficulty-map.md` — the candidates being (a) author wilderness zones, (b) flatten the ambient
> lists so they no longer scale, or (c) accept a scaling overworld as a documented exception.
> `[verified]` that the hole exists; `[unverified]` which fix is cheapest.
>
> **CLOSED 2026-07-29 — the answer is (a) and (b) together, and it is cheap.**
> `implementation-strategy.md` §6 scanned Tamriel: the 3,512 unzoned leveled refs resolve to **88
> lists, 23 already flat**, so the job is **65 lists**, not 12,148 cells. Wildlife takes (b) and keeps
> its regional variation for free — vanilla already ships biome-split lists. Humanoid lists cannot
> take (b) (they are shared with the dungeons this document tiers), so their **238** cells take (a),
> which SkyPatcher can do because `cell/encounterZone=` *adds* a zone where none exists.

---

## 9. Calibration — what is derived and what is a guess

An honest split, because the two halves have very different confidence:

**Derived from the data, and defensible as written:**

- the ladder's **shape** — seven rungs at widening intervals, taken from the draugr gates
- every entry in §5 — arithmetic over `[verified]` ladders
- the **home bands** in §6 — a property of the `LVLN` records, cross-checked against Bethesda's floors
- the multiplier decision in §4 — one value from shipped prior art, three from vanilla
- that vanilla's floors must be stretched (§2) — census plus MLU's shipped counter-example

**Not derived — a calibration guess:**

- the ladder's **absolute offset**. Whether T5 should be 30 or 26 or 34 depends on how fast a real
  character levels through the mod's economy, and `progression.md` §8.4 flags this precisely: *"how
  fast does a normal character reach level 20? Without that, 'fixed level 24' has no calibration. This
  is an in-game measurement, not a record read."* `[unverified]`

The mitigation is structural: **the offset is one number.** Because every tier is defined against the
same ladder, shifting the world's difficulty is re-issuing the seven values in §3, and §5's tables
regenerate from the same script. Nothing downstream — the difficulty map, the loot model, the home
bands — has to be re-derived if the offset moves. Author the map in **tiers**, never in raw levels,
and this stays true.

The three capstone bosses in §8 are the exception: those are absolute numbers pinned to lore
constraints, and they move only if the lore constraint moves.

---

## 10. Vanilla defects this ladder assumes are fixed

`enemy-taxonomy.md` §7.6 asked which vanilla inconsistencies are bugs and which are intent. The tier
tables above are computed **assuming the first two are fixed**:

| Defect | Verdict | Action |
|---|---|---|
| `EncBandit04TemplateMelee` (`01E60D`) serializes at level **0** — a record switched from `PcLevelMult` to `NpcLevel` with the level never set. Affects the tier-4 1H/2H/1HTank/2HBerserk bandits. `[verified]` | **bug** | set to **14**, matching its gate and its correctly-levelled Missile/Magic siblings |
| Gate-40 draugr on the 1H/2H melee lists resolve to a level-**30** record while the Missile list's gate-40 correctly resolves to 40. `[verified]` | **intent** | leave. It is a *gear* tier (ebony) at the same level — legitimate, and table B labels it as such |
| Falmer shamans cap at 25 while melee Falmer reach 38. `[verified]` | **capability, not level** | leave for now. `lore-constraints.md` §3 permits closing it; doing so is a capability edit, not a tier edit |
| Penitus Oculatus gates reach 46 but levels top at 23 — they get relatively *weaker* as the player levels. `[verified]` | **moot** | the ladder removes player level from the equation; assign them a tier and the inversion disappears |
| `EncDremoraMelee06` is named "Valynaz" (missing k). `[verified]` | typo | fix if the record is touched — these names are the UI |

---

## 11. What this hands to the next documents

**`difficulty-map.md`:**
1. Assign every zone one of **T1–T7**, never a raw level. §9 explains why that indirection matters.
2. Respect the **home bands** (§6). A tier outside an archetype's band is a no-op.
3. `dungeons.md` §4 already has all 226 rows with type, zone and boss — this is filling a column.
4. Three things §8 hands over unfinished: the geographic legibility obligation left by the
   `LevelGate*` removal, the **unzoned overworld**, and the main quest's non-monotonic sequence
   (`progression.md` §4: vanilla runs 6 → 6 → 2 → 16 → 18 → 10 and will read as broken the moment
   zones acquire ceilings — Skuldafn at T2 is an anticlimax; it wants T5+).
5. The tutorial corridor is the one place a **band** rather than a point may be justified
   (`progression.md` §5) — vanilla capped exactly those four zones and nowhere else.

**`loot-model.md`:**
1. Loot resolves at the same zone level (`engine-behaviour.md` §3), so **the tier is the loot tier**.
   No second ladder.
2. `[verified]` here and new: the engine ships **`fSpecialLootMinZoneLevelMult` = 0.4**,
   **`fSpecialLootMaxZoneLevelMult` = 1.0** and **`fSpecialLootMinPCLevelMult` = 0.6**
   (`10FEDD` / `10FEDF` / `10FEDE`). Two things follow. First, the *names* are in-repo primary-source
   evidence that boss-chest special loot is computed **from the zone level** — which materially
   strengthens `engine-behaviour.md` §3, its shakiest answer, and it also contradicts UESP's "up to
   twice the level minus one". Second, **`fSpecialLootMinPCLevelMult` = 0.6 is a live bone-1 leak**:
   special loot has a floor at 0.6 × *player* level regardless of the zone, so a level-50 character
   looting a T2 chest still rolls against level 30. It is a GMST, so closing it costs one record.
3. NPC gear is an independent track (`enemy-taxonomy.md` §4) and the tier does **not** reach it.
   That remains the largest single job in the mod: 1,959 of 3,075 `LVLI` are player-gated.

**`implementation-strategy.md`:**
1. The plugin half now has a concrete floor: **2 `LevelModifier` GMSTs** (§4) + **1 special-loot
   GMST** (above) + **12 `LevelGate*` globals** (§8) + the capstone boss records (§8) + the
   `01E60D` bug fix (§10). That is ~20 records — comfortably ESL range, consistent with the working
   recommendation.
2. Everything else in this document — zone bands, class-D levels, list edits — is expressible as
   SkyPatcher rules.
3. ~~**The §4 `None` test can move a large slice of work into the plugin half.**~~ **Revised:** the
   worst case is 9 placed-ref overrides (§4), which does not move the cost estimate. The test that
   still can is **gear resolution** (`loot-model.md` §3) — up to 1,378 `LVLI`.

---

## 12. Open questions

1. **`LevelModifier: None`** (§4) — still open, but **downgraded**: one console check, deciding
   whether **9** placed refs need editing, not ~1,928. See the revision note in §4 and
   `implementation-strategy.md` §7.1. The highest-value unresolved question is now gear resolution
   (`loot-model.md` §3).
2. **The absolute offset** (§9) — needs a real playthrough, not a record read. `[unverified]`
3. ~~**The unzoned overworld** (§8) — structural, unsolved.~~ **CLOSED 2026-07-29** —
   `implementation-strategy.md` §6: 65 lists to flatten, 238 cells to zone, ~7 new `ECZN`.
4. **Is `Min == Max` right, or should Ehlnofey band like MLU?** MLU chose `+10`/`+15` for 357 of 360
   zones. Zero-width is the stricter reading of bone 1 and the whole point of the mod, but it is the
   biggest untested assumption here. `engine-behaviour.md` §2 establishes it *works*; it does not
   establish it *feels right*. `[unverified]`
5. **Cross-archetype legibility** (`lore-constraints.md` §6.1) — the names order power *within* an
   archetype, and the tier system inherits that. A player still has no way to know whether a Draugr
   Scourge outranks a Forsworn Ravager. §5 table A is the answer for a *designer*; the player needs
   something visible. Unsolved, and it belongs to bone 2. `[unverified]`
6. **Does `CalculateFromAllLevelsLessThanOrEqualPlayer` need setting per list?**
   `engine-behaviour.md` §6 settled the semantics: without the flag a list yields only the top
   eligible rung, with it any rung up to the lookup level. **Every table in §5 assumes the flag is
   OFF** (top rung only). 97 of 527 `LVLN` have no flags block and 415 of the remaining 430 carry it
   (`enemy-taxonomy.md` §1) — so for most lists the tables above describe the *top* of a mix, not the
   only occupant. Whether Ehlnofey normalises the flag is a per-list decision it must make
   deliberately rather than inherit. `[verified]` for the counts, `[community]` for the semantics.

---

## Sources

Computed in this document from `reference/` (`[verified]`):
`reference/Base/*/EncounterZones/` (356 zones, §2 census) ·
`reference/Base/01Skyrim/GameSettings/fLeveledActorMult*`, `fSpecialLoot*` ·
`reference/mods/MLUYaml/EncounterZones/` (360 zones, band distribution) ·
`reference/mods/MLUYaml/GameSettings/fLeveledActorMult*`.

Derived from Phase 1/2 documents, which carry their own citations:
`world/enemy-taxonomy.md` §§1–2, 4, 6, 7 · `world/lore-constraints.md` §§1, 3–5 ·
`world/dungeons.md` §2 · `world/progression.md` §§2, 4, 5, 8 · `world/regions.md` §4 ·
`prior-art/morrowloot.md` · `prior-art/skypatcher.md` · `design/engine-behaviour.md` §§0–4, 6.
