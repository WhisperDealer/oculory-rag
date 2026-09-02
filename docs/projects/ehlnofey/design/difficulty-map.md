---
id: "projects/ehlnofey/design/difficulty-map"
title: "Difficulty map — every zone, assigned"
slug: "difficulty-map"
section: "projects/ehlnofey/design"
game: "skyrim"
kind: "design"
project: "ehlnofey"
mod: null
tags: ["ehlnofey", "deleveling", "design", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/design/difficulty-map.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: "Phase 3, document 3"
confidence: {"author": 0, "community": 0, "unverified": 1, "upstream": 0, "verified": 6}
lines: 805
content_sha256: "ec8c7189ab2618d81f02e6862399001d39be3032c1bba05f8a1f5104f25c7c11"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Difficulty map — every zone, assigned

**Phase 3, document 3.** The tier assignment for all **355 encounter zones** in `Skyrim.esm`,
`Update.esm`, `Dawnguard.esm` and `Dragonborn.esm`. This is the record-level spec: §7's tables are
the deliverable, and nothing downstream needs to re-decide a number.

Read `tiers.md` first — the ladder, the multipliers and the archetype home bands are assumed here and
not restated. `engine-behaviour.md` explains why a zone level does what it does.

**Scope decision (taken 2026-07-28):** Skyrim + Dawnguard + Dragonborn. Hearthfire is excluded — it
defines no worldspace, no region, no dungeon and no encounter zone (`regions.md` §4.1), so adding it
as a master would buy nothing. **Masters: `Skyrim.esm`, `Update.esm`, `Dawnguard.esm`,
`Dragonborn.esm`.**

**Zone-width decision (taken 2026-07-28):** zero-width everywhere. Every zone below is
`MinLevel == MaxLevel == N`, with no banded exceptions — including the tutorial corridor, where
protection comes from a *low tier* rather than from a ceiling (§4.1).

Confidence: the record data is `[verified]`; the **assignments themselves are design judgement**, and
the calibration caveat in `tiers.md` §9 applies to all of them.

---

## 1. The rule, not the list

226 dungeons hand-numbered would be unreviewable and unmaintainable. `regions.md` §5.1 argued for the
alternative and this document takes it:

> Express the gradient as **type placement**, and let region act as a **clamp** — not as a per-dungeon
> number. "The Reach contains no tier-1 content" is cheaper, more legible and more lore-defensible
> than 226 assignments.

So every zone gets its tier from a four-step pipeline, and the tables in §7 record which step decided
each one:

```
  1. TYPE        LocType* keyword          →  base tier        (195 zones)
  2. BUMP        +1 if the location holds a word wall           (18 zones bumped)
  3. REGION      clamp into the hold's [floor, ceiling]         (18 zones clamped)
  4. EXPLICIT    a named override wins outright                 (44 zones)

  fallback: no LocType keyword  →  derived from the vanilla MinLevel   (104 zones)
```

Auditable, re-runnable, and the whole map regenerates if `tiers.md` §9's offset ever moves.

### 1.1 Type → base tier

Ordered as vanilla orders them (`dungeons.md` §2 found type predicts level in ~85% of cases and hold
predicts nothing), then mapped onto the ladder within each archetype's **home band** (`tiers.md` §6).

| `LocType*` | vanilla dominant `MinLevel` | **base tier** | Note |
|---|---|---|---|
| `AnimalDen` | 2 | **T1** | creatures are class B/C — the tier picks *species* and governs loot, not threat |
| `GiantCamp` | 2 | **T1** | giants are a flat level 32 regardless of tier; the tier is nearly inert here |
| `BanditCamp` | 6 | **T2** | home band T1–T5 |
| `Shipwreck` | 6 | **T2** | |
| `SprigganGrove` | 8 | **T2** | spriggans 8 / matrons 18, fixed |
| `Mine`, `OrcStronghold` | 6 | **T2** | orcs reuse the bandit tier records |
| `DraugrCrypt` | 6 | **T3** | home band T2–T6; the word-wall bump is what spreads these |
| `VampireLair` | 6 | **T3** | home band T2–T7 |
| `WarlockLair` | 8 | **T3** | the only ladder that differentiates T1–T7 |
| `MilitaryFort` | 6 | **T3** | |
| `WerewolfLair`, `WerebearLair` | 6 | **T3** | |
| `DragonLair` | 10 | **T4** | ladder is flat below T4 |
| `ForswornCamp` | 14 | **T4** | |
| `HagravenNest` | 14 | **T4** | hagravens are a fixed 20 |
| `DwarvenAutomatons` | 16 | **T4** | ladder is flat below T4 |
| `FalmerHive` | 18 | **T5** | ladder is flat below T4; 18 is already near the top of vanilla |
| `DragonPriestLair` | 24 | **T5** | the priest is a fixed 50 either way; the tier sets the crypt around him |
| *settlement types* (`Town`, `Dwelling`, `House`, `Store`, `Jail`, `Guild`, `Temple`, `Ship`, …) | — | **T2** | 12 zones. Guards are class D and now carry a fixed level (`tiers.md` §7), so these matter mostly for loot |

Multi-type locations take the **highest** of their types — Irkngthand is `DwarvenAutomatons` *and*
`FalmerHive`, so it resolves at T5.

### 1.2 The word-wall bump

`+1 tier (capped at T6) if the location carries a `LocationWordWall` reference.` 31 locations carry
one `[verified]`; **18 zones actually move**, the rest being already at T6+ or settled by an explicit
override.

This is the one per-dungeon differentiator, and it was chosen because it is the only signal that is
both **visible to the player** (bone 2 — `regions.md` §5.3: *tie tiers to things that are visible*)
and **not collinear with the type**. It is what promotes Angarvunde, Silverdrift Lair, Dead Men's
Respite, Hag's End and Ironbind Barrow above the ordinary run of crypts.

> **A rejected rule, recorded so it is not re-proposed.** The first draft also bumped on an *ancient
> tileset* (`LocSetNordicRuin` / `LocSetDwarvenRuin`). It was dropped after the spot-check showed it
> is **collinear with the type keyword** — essentially every `DraugrCrypt` is a `NordicRuin` and every
> `DwarvenAutomatons` a `DwarvenRuin` — so it did not differentiate anything, it just relabelled
> `DraugrCrypt` from T3 to T4 across the board. If that is the intent, change the type table; do not
> launder it through a bump. `[verified]` from the assignment run.

### 1.3 Region clamps

Region is a **floor and a ceiling**, never a shift. Only **18 of 355** zones are actually clamped —
the type signal is left to do the work almost everywhere, which is the intended balance.

| Hold | Floor | Ceiling | Why |
|---|---|---|---|
| **Whiterun** | T1 | **T4** | The tutorial hold, by composition: bandit camps, animal dens and giant camps are 12 of its 21 dungeons, and it has no draugr crypt, no dragon lair, no Dwemer ruin and no Dragon Priest lair (`regions.md` §3). *"Whiterun must stay soft."* |
| Falkreath | T1 | T5 | softest and most varied hold, mean level 5.9 |
| the Rift | T1 | T5 | bandit country |
| Eastmarch | T1 | T5 | bandit country |
| Hjaalmarch | T1 | T5 | |
| Haafingar | T1 | T5 | |
| the Pale | **T2** | T5 | the undead hold — `DraugrCrypt` ×5 plus `NordicRuin` ×5 |
| Winterhold | **T2** | T6 | the Falmer/ice hold — `FalmerHive` ×4, `CaveIce` ×6, joint-highest vanilla mean |
| **the Reach** | **T3** | T6 | The one hold with a real identity: 15 of 31 dungeons are Forsworn camps or hagraven nests, highest vanilla mean (12.6), most word walls (7), most `NeverResets` (9). `regions.md` §5.4 nominates it as the pilot region, and the T3 floor is the concrete form of *"the Reach contains no tier-1 content."* |
| **Solstheim** | T2 | T6 | A tenth `LocTypeHold` (`016E2A:Dragonborn.esm`), not an optional extra. Already the best-graded region in the game (6→40, mean 14.9) and `lore-constraints.md` §5.5 supports its higher ceiling as a *fictional* difference, not an inconsistency to normalise away. |

**Hold membership vs map position** — `regions.md` §6.1 required an explicit decision. **This map keys
on hold membership** (the `ParentLocation` chain), because that is what the game's own systems read,
and because it is the axis a rule engine can filter on. The known consequence is that **Bleak Falls
Barrow is parented to Falkreath, not Whiterun** (`dungeons.md` §2), along with several other
Whiterun-adjacent sites. That is why Bleak Falls appears in the Falkreath table below, and it is why
it also carries an **explicit** override — the clamp would not have caught it.

### 1.4 The fallback

**104 zones have no `LocType*` keyword** on their location (68 have a location with no type; 20 have
no resolvable `Location` at all; the rest are settlement-typed). For these the tier is derived from
the vanilla `MinLevel`:

| vanilla `MinLevel` | ≤2 | 5–6 | 8–10 | 12–16 | 18–25 | ≥30 |
|---|---|---|---|---|---|---|
| tier | T1 | T2 | T3 | T4 | T5 | T6 |

This is the weakest part of the map and it is a large slice of it. Most of these zones are small
unnamed POIs — shacks, towers, camps — where the vanilla floor is a reasonable statement of intent.
The ones that are *not* small (the Soul Cairn, the Forgotten Vale, Castle Volkihar, Apocrypha) are all
handled by explicit override instead, precisely because the fallback would have mis-served them.

---

## 2. The result

| | vanilla | **Ehlnofey** |
|---|---|---|
| distinct zone levels | 18 | **7** |
| zones at level ≤ 8 | 229 of 355 (65%) | **157 (44%)** |
| zones at level ≥ 21 | **29 (8%)** | **105 (30%)** |
| highest level | 40 (one zone) | **50** |
| zones raised / lowered / unchanged | — | **316 / 28 / 11** |
| mean level | 9.4 | **14.8** |

| Tier | `N` | Zones | Share |
|---|---|---|---|
| T1 | 4 | 36 | 10% |
| **T2** | **8** | **121** | **34%** |
| T3 | 14 | 93 | 26% |
| T4 | 21 | 51 | 14% |
| T5 | 30 | 39 | 11% |
| T6 | 40 | 14 | 4% |
| T7 | 50 | **1** | 0.3% |

**On the T2 lump.** A third of the world at one tier looks like a failure to differentiate, and it was
worth checking rather than assuming. It is not: vanilla is *more* concentrated (229 of 355 at ≤8
against our 157) and, decisively, vanilla has almost **no tail at all** — **29** zones at ≥21 against
our **105**, a 3.6× increase in the amount of the world that is genuinely dangerous.
Skyrim genuinely is mostly small camps and caves; the shape of the curve is right and the fix Ehlnofey
makes is to the *top* of it, not the middle. The mode sitting at "local trouble" is also a legibility
asset: the player learns that an ordinary cave means T2, and the exceptions read as exceptions.

**On T7.** It is used **once** — Castle Volkihar. That is worth stating plainly rather than padding
the list to justify the rung: once the named bosses carry fixed levels (`tiers.md` §8), T7's only
remaining job is unlocking the gate-60 vampire rung for Harkon's court. If a later pass finds no
second use, T7 is honestly a special case rather than a tier, and collapsing it into T6 plus a
per-record fix would be the simpler design. Recorded as an open question (§6.2), not resolved here.

---

## 3. Sequenced content — where the rules had to be overridden

44 zones are assigned explicitly. Three groups matter enough to justify themselves.

### 3.1 The main quest

`progression.md` §4's finding is the sharpest problem in the game data: the MQ dungeon sequence runs
**6 → 6 → 2 → 16 → 18 → 10**, and Skuldafn — the penultimate dungeon of the entire game — sits at
`MinLevel` **10**, six levels below Alftand which you visit earlier. In vanilla this is invisible
because everything scales up to the player. **Under a fixed world it becomes visible immediately**,
and Skuldafn would be a trivial anticlimax.

| Quest | Dungeon | vanilla | **Ehlnofey** |
|---|---|---|---|
| MQ103 | Bleak Falls Barrow | 6 (capped 20) | **T2** (8) |
| MQ105 | Ustengrav | 6 | **T3** (14) |
| MQ201 | Thalmor Embassy | 2 | **T3** (14) |
| MQ205 | Alftand | 16 | **T4** (21) |
| MQ205 | Blackreach | 18 | **T5** (30) |
| **MQ303** | **Skuldafn** | **10** | **T6** (40) |

Now monotonic: **8 → 14 → 14 → 21 → 30 → 40.** This is the single most consequential set of
overrides in the document.

### 3.2 The tutorial corridor

`progression.md` §5: the only four capped zones in the base game are all on the Helgen → Riverwood →
Whiterun path. Bethesda capped exactly the places a new character stumbles into and nowhere else.

Because the zone-width decision is **zero-width everywhere**, that protection cannot be reproduced as
a ceiling. It is reproduced as a **low tier** instead:

| Zone | vanilla | **Ehlnofey** |
|---|---|---|
| `EmbershardMineZone` | 6–10 | **T1** (4) |
| `HaltedStreamCampZone` | 6–10 | **T1** (4) |
| `WhiteRiverWatchZone` | 6–10 | **T1** (4) |
| `BleakFallsBarrowZone` | 6–20 | **T2** (8) |

The two designs are not equivalent and the difference should be understood. Vanilla's cap protects a
*low-level* player while still rewarding a high-level one; a fixed T1 protects the new player and
makes the place permanently trivial. That is the deliberate consequence of bone 1, and the corridor is
where a player will feel it first — so it is also the first thing to check in playtest.

### 3.3 The untagged regions

`regions.md` §4.2 called this "the single most actionable DLC finding": **9 of Dawnguard's 19 zones
have no `Location` field at all**, and Dawnguard's new-world locations plus *all* of Apocrypha carry
**no keywords whatsoever**. Any rule walking `ECZN.Location → LCTN → keywords` silently skips the Soul
Cairn, Darkfall, Castle Volkihar and most of the Forgotten Vale.

**Resolution: name their zones explicitly.** Not by adding keywords via override (more records, and it
changes vanilla locations other mods read), and not by excluding them. Every one is in the explicit
list:

| Region | Zones | **Tier** |
|---|---|---|
| Dimhollow Crypt | `DLC1DimhollowCryptZone` | T3 |
| Darkfall Cave → Passage | `DLC1DarkfallCaveZone` → `…PassageZone` | T4 → T5 |
| Soul Cairn | `DLC1_SoulCairnZone` | T5 |
| Forgotten Vale | `DLC1FalmerValleyZone`, `DLC1zFalmerValley01–03Zone` | T5 |
| Forgotten Vale temple | `DLC1FalmerValleyTempleZone` | T6 |
| **Castle Volkihar** | `DLC1_VCDungeonZone` | **T7** |
| Apocrypha (7 Black Books) | `DLC2Book01–07DungeonZone`, `DLC2MiscBookLevel1Zone` | **T6, flat** |

Apocrypha stays **flat** on purpose: `lore-constraints.md` §3 — *"it is one realm, entered by one
means, and Mora's servants have no reason to be graded by which book you opened."* Ehlnofey keeps it
flat and only picks the height, moving it from vanilla's 25 to T6.

---

## 4. What this document does **not** cover

Three gaps, stated plainly rather than buried.

### 4.1 The overworld is not mapped, and cannot be by this mechanism

> **Superseded 2026-07-29 — it can be, and `implementation-strategy.md` §6 now maps it.** The
> recommendation below picks (b) alone on the grounds that (a) is "plausible, untested"; a scan of
> the Tamriel worldspace since shows the real answer is **(a) and (b) together**, split by
> population. Wildlife takes (b) *per biome list*, so regional variation survives — the "point
> regions at different variants" hope in the (b) row turns out to need no new variants at all,
> because vanilla already ships them. The ~250 humanoid refs cannot take (b) (their lists are the
> ones §7 tiers), so their **238** cells take (a) — **~7 new `ECZN` and ~7 rule lines**, not the
> open-ended cost assumed here. Read §6 of the implementation strategy, not this section.

`tiers.md` §8 flagged it and it is unresolved here. Most of Skyrim's wilderness has **no encounter
zone**, so there is nothing to write a tier into — and the ambient creature lists
(`LCharAnimalForestPredator` `042297` and kin) still carry player-level gates. Neutralising the twelve
`LevelGate*` globals stops one scaling mechanism; it does not stop that one.

**For exteriors, "tier" remains undefined.** The three candidates, unchanged from `tiers.md`:

| Option | Cost | Verdict |
|---|---|---|
| **(a)** author new wilderness `ECZN` covering the hold exteriors | new records + they must be attached to cells/locations; SkyPatcher cannot create records | plausible, untested |
| **(b)** flatten the ambient `LCharAnimal*` lists so they stop scaling, and point regions at different variants | SkyPatcher `leveledList` rules reach this natively; no new zones needed | **most promising** |
| **(c)** accept a scaling overworld as a documented bone-1 exception | free | honest, but it is a large exception |

**Recommendation: (b)**, decided in `implementation-strategy.md` with the rule syntax in front of us.
Note the mitigating fact from `enemy-taxonomy.md` §2.3 — the ambient lists already have hard ceilings
(forest predators top out at a level-16 cave bear, mountain predators at a level-22 frost troll), so
**Skyrim's wilderness is already effectively deleveled above ~level 20**. The gap is real but it is
bounded, and it is worst in the first twenty levels.

### 4.2 The 8 unzoned dragon lairs

`dungeons.md` §2: 28 dungeons have no encounter zone, including **8 of the 10 exterior dragon lairs**
(Bonestrewn Crest, Ancient's Ascent, Eldersblood Peak, Shearpoint, Autumnwatch Tower, Lost Tongue
Overlook, Northwind Summit, Dragontooth Crater) plus Orphan Rock, Bard's Leap Summit, Karthspire and
Volskygge. They have no level floor and cannot be tiered by this map.

Their difficulty is entirely `LCharDragonAny` plus the placed `LevelModifier` — and every one of those
lairs places its dragon at `Hard`. Under a fixed world with no zone, `Hard` resolves against the
**player's level**, so the dragon lairs would scale exactly as they do today. Options are the same
(a)/(b)/(c) as §4.1; the cheapest is to fix `LCharDragonAny` selection directly rather than to author
12 zones.

### 4.3 Named bosses other than the three finals

`tiers.md` §8 fixed Alduin, Harkon and Miraak. The other named bosses — Jyrik Gauldurson, Sigdis
Gauldurson, Vals Veran, Linwe, Luah Al-Skaven, Ghunzul, Drascua, Red Eagle and the eight Dragon
Priests — are **not** individually assigned here. Most need nothing: `unique-enemies.md` and
`enemy-taxonomy.md` §2.2 established that the priests are a fixed 50 and that 21 named bosses have no
fixed level at all because they template down to a leveled list, which this map's tier already drives.

The remaining lever, and it is a good one, is `dungeons.md` §1: **a dungeon's boss is a `Lvl*` wrapper
NPC that defers to a leveled list, so retargeting the wrapper's `Template` per dungeon hand-sets a
boss with no NPC record edits.** That is worth doing for a short list of landmark dungeons and belongs
in `implementation-strategy.md`, which owns the cost question.

---

## 5. Applying it

Every row in §7 is a two-field edit to one `ECZN`:

```yaml
# Ehlnofey sets both fields; nothing else on the record changes.
MinLevel: 21
MaxLevel: 21
```

Three authoring constraints, all from `engine-behaviour.md` §2 and binding on every row:

1. `MaxLevel: 0` means **uncapped**, not level 0. A fixed zone must write `N` into *both* fields.
2. Do **not** set `MatchPcBelowMinimumLevel` — it re-opens the bottom of the band. One vanilla zone
   uses it (`WinterholdCollegeMiddenZone` `10D415`); clear it there.
3. Both fields are **int8**, ceiling 127. T7 = 50 is comfortably inside it.

**Preserve `Flags` exactly.** 91 of the 355 zones carry `NeverResets` and one carries
`DisableCombatBoundary` `[verified]`. These are mostly quest-critical, and `dungeons.md` §2 warns that
a deleveling pass must not change respawn behaviour by accident. A tier edit touches `MinLevel` and
`MaxLevel` and nothing else.

**Load order.** `Update.esm` overrides `FolgunthurZone` (`03EC17`) and `GeirmundsHallZone` (`03EC26`);
`Dawnguard.esm` overrides `BthalftZone` (`0D5670`) — all three under their original `Skyrim.esm`
FormKeys. That is why 358 zone *records* resolve to **355 unique FormKeys**. Ehlnofey must load after
all of them and win, per CLAUDE.md's last-wins rule. `[verified]`

**Save-game behaviour** (`engine-behaviour.md` §5.2) is an engine property, identical for a plugin and
for a SkyPatcher rule: on an existing save, a zone the player has already entered keeps its stored
`zoneLevel` until it resets, and the 91 `NeverResets` zones keep it forever. **New game recommended**
— the same de-facto stance MLU takes.

---

## 6. Open questions

1. **Calibration** (`tiers.md` §9) — the offset is a playtest parameter. Because every row here is a
   *tier* and not a level, re-calibrating is re-issuing seven numbers, not re-auditing 355 rows.
2. **Is T7 a tier or a special case?** One zone uses it (§2). If no second use appears, fold it into
   T6 and fix Harkon's court per-record.
3. ~~**The overworld** (§4.1) and **the unzoned dragon lairs** (§4.2) — both unsolved.~~ **The
   overworld is CLOSED** (`implementation-strategy.md` §6): 65 lists, 238 cells, ~7 new `ECZN`, and
   it needs *both* a non-zone mechanism (wildlife) and zones after all (humanoids). The **dragon
   lairs** remain open — `LCharDragonAny` is 11 overworld refs plus the 8 lairs, one decision.
4. **The fallback bucket is 104 zones (29%)** derived from vanilla floors rather than from a type
   signal (§1.4). It is the lowest-confidence third of the map and would repay a manual pass, most
   cheaply by adding `LocType*` keywords to the locations that deserve them.
5. **Does the Civil War questline drag the player across holds in an order that conflicts with the
   regional clamps?** 47 `CivilWar` quests touch every hold (`progression.md` §8.5). Unchecked.
   `[unverified]`
6. **Whiterun's T4 ceiling costs Shimmermist Cave** — a `FalmerHive` that would otherwise be T5, and
   the weakest Falmer hive in the game as a result. Defensible (it is the tutorial hold) but it is the
   clamp doing something visible, and it is the first place to look if Whiterun feels wrong.

---

## 7. The map

Sorted by tier descending within each hold, so the apex of each region reads first. **`van. Min`** is
the vanilla `ECZN.MinLevel` (— = absent). **`N`** is the value written to *both* `MinLevel` and
`MaxLevel`. **Rule** records which pipeline step decided the row (§1).

> **Generated — do not hand-edit between the markers.** `arch-docs/design/build-difficulty-map.py`
> rebuilds this block from `reference/`; it holds the ladder, the type table, the region clamps and
> the explicit list as data. Change a rule there and re-run:
>
> ```
> python arch-docs/design/build-difficulty-map.py          # rewrite the tables
> python arch-docs/design/build-difficulty-map.py --check  # distribution only, no write
> ```
>
> This is what makes `tiers.md` §9's promise real: re-calibrating the world is editing the seven
> numbers in `TIER` and re-running, not re-auditing 355 rows. It needs `reference/`, which is
> gitignored, so it cannot run in CI.

<!-- BEGIN GENERATED TABLES -->

#### Whiterun  — 28 zones · T1×10 · T2×8 · T3×5 · T4×5

| Encounter zone | FormKey | van. Min | **Tier** | `N` | Rule |
|---|---|---|---|---|---|
| `DrelasCottageZone` | `0E66AC:Skyrim.esm` | 12 | **T4** | 21 | no LocType - fallback from vanilla min 12 |
| `LundsHutZone` | `0E66A6:Skyrim.esm` | 12 | **T4** | 21 | no LocType - fallback from vanilla min 12 |
| `RannveigsFastZone` | `03EC58:Skyrim.esm` | 8 | **T4** | 21 | WarlockLair +word wall |
| `SerpentsBluffRedoubtZone` | `03EC89:Skyrim.esm` | 14 | **T4** | 21 | ForswornCamp + HagravenNest |
| `ShimmermistCaveZone` | `03EC65:Skyrim.esm` | 18 | **T4** | 21 | FalmerHive → region ceiling 4 |
| `BrokenFangCaveZone` | `03EBF5:Skyrim.esm` | 6 | **T3** | 14 | VampireLair + MilitaryFort |
| `DLC1MolderingRuinsZone` | `003CFC:Dawnguard.esm` | — | **T3** | 14 |  |
| `FellglowKeepZone` | `03EC15:Skyrim.esm` | 8 | **T3** | 14 | WarlockLair |
| `HighHrothgarZone` | `03EC35:Skyrim.esm` | 8 | **T3** | 14 | no LocType - fallback from vanilla min 8 |
| `ThroatoftheWorldZone` | `03EC7F:Skyrim.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `DoomstoneRitualZone` | `0D5685:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `HamvirsRestZone` | `0EF0A3:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `HonningbrewMeaderyZone` | `03EC3B:Skyrim.esm` | 8 | **T2** | 8 | settlement (Dwelling House) |
| `RedoransRetreatZone` | `03EC5C:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `SilentMoonsCampZone` | `03EC6F:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `SwindlersDenZone` | `03EBE7:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `ValtheimKeepZone` | `03EC85:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `WhitewatchTowerZone` | `0E66A1:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `BleakwindBasinZone` | `03EBEF:Skyrim.esm` | 2 | **T1** | 4 | GiantCamp |
| `ColdRockPassZone` | `0BC0A4:Skyrim.esm` | 8 | **T1** | 4 | AnimalDen |
| `CrabbersShantyZone` | `0E66AA:Skyrim.esm` | 2 | **T1** | 4 | no LocType - fallback from vanilla min 2 |
| `GoldunRockZone` | `03EC2E:Skyrim.esm` | 2 | **T1** | 4 | GiantCamp |
| `GraywinterWatchZone` | `03EC2C:Skyrim.esm` | 2 | **T1** | 4 | AnimalDen |
| `GreenspringHollowZone` | `03EC3D:Skyrim.esm` | 2 | **T1** | 4 | AnimalDen |
| `GuldunRockZone` | `0B8AA2:Skyrim.esm` | 24 | **T1** | 4 | GiantCamp |
| `HaltedStreamCampZone` | `03EC32:Skyrim.esm` | 6 | **T1** | 4 | tutorial corridor |
| `SleepingTreeCampZone` | `03EC72:Skyrim.esm` | 2 | **T1** | 4 | GiantCamp |
| `WhiteRiverWatchZone` | `03EC8B:Skyrim.esm` | 6 | **T1** | 4 | tutorial corridor |

#### Falkreath  — 38 zones · T1×6 · T2×15 · T3×12 · T4×4 · T5×1

| Encounter zone | FormKey | van. Min | **Tier** | `N` | Rule |
|---|---|---|---|---|---|
| `LostEchoCaveZone` | `03EC44:Skyrim.esm` | 8 | **T5** | 30 | FalmerHive |
| `AngisCampZone` | `0F5BA3:Skyrim.esm` | 12 | **T4** | 21 | no LocType - fallback from vanilla min 12 |
| `DLC1ArkngthamzZone` | `005824:Dawnguard.esm` | 16 | **T4** | 21 | Dwemer |
| `GlenmorilCovenZone` | `03EC28:Skyrim.esm` | 14 | **T4** | 21 | HagravenNest |
| `ShriekwindBastionZone` | `0A0E3C:Skyrim.esm` | 6 | **T4** | 21 | VampireLair +word wall |
| `BloatedMansGrottoZone` | `03EBF2:Skyrim.esm` | 6 | **T3** | 14 | WerewolfLair |
| `BloodletThroneZone` | `016F87:Skyrim.esm` | 6 | **T3** | 14 | VampireLair + MilitaryFort |
| `BrittleshinPassZone` | `03EC37:Skyrim.esm` | 2 | **T3** | 14 | WarlockLair |
| `E3DemoBleakFallsBarrowZone` | `0998BF:Skyrim.esm` | 6 | **T3** | 14 | DraugrCrypt |
| `FalkreathWatchtowerZone` | `0478DD:Skyrim.esm` | 6 | **T3** | 14 | WarlockLair |
| `HaemarsShameZone` | `052541:Skyrim.esm` | 6 | **T3** | 14 | VampireLair |
| `HalldirsCairnZone` | `03EC31:Skyrim.esm` | 6 | **T3** | 14 | DraugrCrypt |
| `HuntersRestZone` | `0F52B1:Skyrim.esm` | 8 | **T3** | 14 | no LocType - fallback from vanilla min 8 |
| `IlinaltasDeepZone` | `03EC3C:Skyrim.esm` | 8 | **T3** | 14 | WarlockLair |
| `SouthfringeSanctumZone` | `03EC92:Skyrim.esm` | 6 | **T3** | 14 | WarlockLair |
| `SunderstoneGorgeZone` | `061ADA:Skyrim.esm` | 2 | **T3** | 14 | WarlockLair |
| `TwilightSepulcherZone` | `03EBF3:Skyrim.esm` | 8 | **T3** | 14 | no LocType - fallback from vanilla min 8 |
| `AnisesCabinZone` | `0D9546:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `BannermistZone` | `04786A:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `BilegulchMineZone` | `0A3859:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp + Mine |
| `BleakFallsBarrowZone` | `038AB1:Skyrim.esm` | 6 | **T2** | 8 | tutorial corridor / MQ103 |
| `CrackedTuskKeepZone` | `0A3857:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `DarkBrotherhoodSancZone` | `03EC06:Skyrim.esm` | 8 | **T2** | 8 | settlement (Town Dwelling) |
| `DoomstoneLadyZone` | `0D5689:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `EvergreenGroveZone` | `03EC13:Skyrim.esm` | 8 | **T2** | 8 | SprigganGrove |
| `HelgenZone` | `0F94A6:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `KnifepointRidgeZone` | `08E1B8:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `MossMotherCavernZone` | `03EC4A:Skyrim.esm` | 8 | **T2** | 8 | SprigganGrove |
| `PeaksShadeTowerZone` | `047884:Skyrim.esm` | 6 | **T2** | 8 | SprigganGrove |
| `PinewatchZone` | `03EC52:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `RoadsideRuinsZone` | `04787F:Skyrim.esm` | 6 | **T2** | 8 | SprigganGrove |
| `SkyboundWatchZone` | `04B677:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `BonechillPassageZone` | `0FDA47:Skyrim.esm` | 2 | **T1** | 4 | AnimalDen |
| `DarkshadeCopseZone` | `03EC08:Skyrim.esm` | 6 | **T1** | 4 | AnimalDen |
| `EmbershardMineZone` | `0D9545:Skyrim.esm` | 6 | **T1** | 4 | tutorial corridor |
| `GreywaterGrottoZone` | `03EC2D:Skyrim.esm` | 2 | **T1** | 4 | AnimalDen |
| `SecundasShelfZone` | `03EC62:Skyrim.esm` | 2 | **T1** | 4 | GiantCamp |
| `WarehouseZone` | `0E9DA8:Skyrim.esm` | 1 | **T1** | 4 | no LocType - fallback from vanilla min 1 |

#### the Rift  — 38 zones · T1×6 · T2×16 · T3×7 · T4×5 · T5×4

| Encounter zone | FormKey | van. Min | **Tier** | `N` | Rule |
|---|---|---|---|---|---|
| `DLC1LDBthalftAetheriumForgeZone` | `005825:Dawnguard.esm` | 15 | **T5** | 30 |  |
| `DarkwaterCavernZone` | `03EC09:Skyrim.esm` | 18 | **T5** | 30 | FalmerHive |
| `ForelhostZone` | `03EC18:Skyrim.esm` | 24 | **T5** | 30 | Rahgot |
| `TolvaldsCaveZone` | `03EC80:Skyrim.esm` | 18 | **T5** | 30 | FalmerHive |
| `AngarvundeZone` | `03EBE8:Skyrim.esm` | 6 | **T4** | 21 | DraugrCrypt +word wall |
| `AvanchnzelZone` | `03EBEB:Skyrim.esm` | 16 | **T4** | 21 | DwarvenAutomatons |
| `DLC1RuunvaldZone` | `007B22:Dawnguard.esm` | 10 | **T4** | 21 |  |
| `NorthwindMineZone` | `0FDBE0:Skyrim.esm` | 12 | **T4** | 21 | no LocType - fallback from vanilla min 12 |
| `ShroudHearthBarrowZone` | `06CCC7:Skyrim.esm` | 6 | **T4** | 21 | DraugrCrypt +word wall |
| `AlchemistsShackZone` | `0D566E:Skyrim.esm` | 8 | **T3** | 14 | no LocType - fallback from vanilla min 8 |
| `ArcwindPointZone` | `0FD686:Skyrim.esm` | 6 | **T3** | 14 | no LocType - fallback from vanilla min 6 +word wall |
| `BoulderfallCaveZone` | `0F52DB:Skyrim.esm` | 6 | **T3** | 14 | WarlockLair |
| `DLC1RedwaterDenZone` | `007779:Dawnguard.esm` | — | **T3** | 14 |  |
| `DarklightTowerZone` | `03EC07:Skyrim.esm` | 8 | **T3** | 14 | WarlockLair |
| `FortGreenwallZone` | `03EC1E:Skyrim.esm` | 6 | **T3** | 14 | MilitaryFort |
| `GeirmundsHallZone` | `03EC26:Skyrim.esm` | 6 | **T3** | 14 | DraugrCrypt |
| `AutumnshadeClearingZone` | `03EBEA:Skyrim.esm` | 14 | **T2** | 8 | SprigganGrove |
| `BrokenHelmHollowZone` | `03EBF6:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `BthalftZone` | `0D5670:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `DoomstoneShadowZone` | `0D5683:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `DoomstoneThiefZone` | `0D5672:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `FaldarsToothZone` | `03EC14:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `FrokisShackZone` | `0D5664:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `GoldenglowFarmZone` | `03EC2B:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `LargashburZone` | `0A3858:Skyrim.esm` | 6 | **T2** | 8 | OrcStronghold |
| `LostProspectMineZone` | `0D566C:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `NilheimZone` | `03EC4E:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `RiftWatchtowerZone` | `0D5666:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `RkundZone` | `0D5668:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `ShorsWatchtowerZone` | `0D566A:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `StendarrsBeaconZone` | `108A5B:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `TrevasWatchZone` | `03EC81:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `ClearspringTarnZone` | `03EC00:Skyrim.esm` | 2 | **T1** | 4 | AnimalDen |
| `CrystaldriftCaveZone` | `03EC05:Skyrim.esm` | 2 | **T1** | 4 | AnimalDen |
| `FallowstoneCaveZone` | `03EC93:Skyrim.esm` | 2 | **T1** | 4 | AnimalDen |
| `GiantsGroveZone` | `0C33AE:Skyrim.esm` | 2 | **T1** | 4 | AnimalDen |
| `HoneystrandCaveZone` | `03EC39:Skyrim.esm` | 2 | **T1** | 4 | AnimalDen |
| `PinepeakCavernZone` | `03EC51:Skyrim.esm` | 2 | **T1** | 4 | AnimalDen |

#### Eastmarch  — 29 zones · T1×6 · T2×9 · T3×8 · T4×4 · T5×1 · T6×1

| Encounter zone | FormKey | van. Min | **Tier** | `N` | Rule |
|---|---|---|---|---|---|
| `SkuldafnZone` | `03EC71:Skyrim.esm` | 10 | **T6** | 40 | MQ303 - vanilla 10 is the anticlimax this fixes |
| `KagrenzelZone` | `0233F2:Skyrim.esm` | 18 | **T5** | 30 | FalmerHive |
| `MzulftZone` | `03EC4C:Skyrim.esm` | 16 | **T4** | 21 | DwarvenAutomatons |
| `ShrineofBoethiahZone` | `0F5BA8:Skyrim.esm` | 12 | **T4** | 21 | no LocType - fallback from vanilla min 12 |
| `SnaplegCaveZone` | `03EC73:Skyrim.esm` | 14 | **T4** | 21 | HagravenNest |
| `WitchmistGroveZone` | `03EC8D:Skyrim.esm` | 14 | **T4** | 21 | HagravenNest |
| `AbandonedPrisonZone` | `0ECF4B:Skyrim.esm` | 6 | **T3** | 14 | MilitaryFort |
| `AnsilvundZone` | `03EBE9:Skyrim.esm` | 8 | **T3** | 14 | WarlockLair |
| `CragwallowSlopeZone` | `03EC03:Skyrim.esm` | 6 | **T3** | 14 | WarlockLair |
| `EldergleamSanctuaryZone` | `03EC12:Skyrim.esm` | 8 | **T3** | 14 | no LocType - fallback from vanilla min 8 |
| `FortAmolZone` | `03EC1A:Skyrim.esm` | 6 | **T3** | 14 | MilitaryFort |
| `MarasEyePondZone` | `0ECF54:Skyrim.esm` | 6 | **T3** | 14 | VampireLair |
| `MistwatchZone` | `03EC47:Skyrim.esm` | 6 | **T3** | 14 | BanditCamp + MilitaryFort |
| `MorvunskarZone` | `03EC48:Skyrim.esm` | 8 | **T3** | 14 | WarlockLair + MilitaryFort |
| `CragslaneCavernZone` | `03EC02:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `DoomstoneAtronachZone` | `0D568A:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `GallowsRockZone` | `03EC25:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `LostKnifeHideoutZone` | `03EC45:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `NarzulburZone` | `0A385A:Skyrim.esm` | 6 | **T2** | 8 | OrcStronghold |
| `RiversideShackZone` | `0ECF4E:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `StonyCreekCaveZone` | `080F29:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `TraitorsPostZone` | `0C2EE8:Skyrim.esm` | 5 | **T2** | 8 | no LocType - fallback from vanilla min 5 |
| `UtteringHillsCampZone` | `03EC84:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `BrokenLimbCampZone` | `0ECF89:Skyrim.esm` | 2 | **T1** | 4 | GiantCamp |
| `CradlecrushRockZone` | `03EC01:Skyrim.esm` | 2 | **T1** | 4 | GiantCamp |
| `CronvangrHallZone` | `03EC04:Skyrim.esm` | 6 | **T1** | 4 | AnimalDen |
| `RefugeesRestZone` | `0EF573:Skyrim.esm` | 2 | **T1** | 4 | AnimalDen |
| `RiverwatchZone` | `03EC5F:Skyrim.esm` | 2 | **T1** | 4 | no LocType - fallback from vanilla min 2 |
| `SteamcragCampZone` | `079FA0:Skyrim.esm` | 2 | **T1** | 4 | GiantCamp |

#### Hjaalmarch  — 20 zones · T1×3 · T2×8 · T3×3 · T4×3 · T5×2 · T6×1

| Encounter zone | FormKey | van. Min | **Tier** | `N` | Rule |
|---|---|---|---|---|---|
| `LabyrinthianZone` | `03EC42:Skyrim.esm` | 24 | **T6** | 40 | Morokei / MG capstone, NeverResets |
| `ChillwindDepthsZone` | `03EBFB:Skyrim.esm` | 18 | **T5** | 30 | FalmerHive |
| `SkybornAltarZone` | `030AB1:Skyrim.esm` | 10 | **T5** | 30 | DragonLair +word wall |
| `DeadMensRespiteZone` | `03EC0B:Skyrim.esm` | 6 | **T4** | 21 | DraugrCrypt +word wall |
| `FolgunthurZone` | `03EC17:Skyrim.esm` | 6 | **T4** | 21 | DraugrCrypt +word wall |
| `MzinchaleftZone` | `03EC49:Skyrim.esm` | 16 | **T4** | 21 | DwarvenAutomatons |
| `FortSnowhawkZone` | `03EC22:Skyrim.esm` | 6 | **T3** | 14 | MilitaryFort |
| `MovarthsLairZone` | `03EC27:Skyrim.esm` | 6 | **T3** | 14 | VampireLair |
| `UstengravZone` | `03EC83:Skyrim.esm` | 6 | **T3** | 14 | MQ105 |
| `DoomstoneApprenticeZone` | `0D5674:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `DoomstoneLordZone` | `0D5688:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `IcerunnerZone` | `03EC66:Skyrim.esm` | 6 | **T2** | 8 | Shipwreck |
| `KjenstagRuinsZone` | `0C2EF2:Skyrim.esm` | 5 | **T2** | 8 | no LocType - fallback from vanilla min 5 |
| `MeekosShackZone` | `0F6F14:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `OrotheimZone` | `0A8286:Skyrim.esm` | 2 | **T2** | 8 | BanditCamp |
| `RobbersGorgeZone` | `03EC63:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `ValkyggZone` | `0EAA61:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `BroodCavernZone` | `03EBF8:Skyrim.esm` | 2 | **T1** | 4 | AnimalDen |
| `StonehillBluffZone` | `03EC7B:Skyrim.esm` | 2 | **T1** | 4 | GiantCamp |
| `TalkingStoneCampZone` | `03EC7E:Skyrim.esm` | 2 | **T1** | 4 | GiantCamp |

#### Haafingar  — 24 zones · T1×1 · T2×10 · T3×10 · T4×1 · T5×2

| Encounter zone | FormKey | van. Min | **Tier** | `N` | Rule |
|---|---|---|---|---|---|
| `KarthspireRedoubtZone` | `03EC94:Skyrim.esm` | 14 | **T5** | 30 | DragonPriestLair +word wall → region ceiling 5 |
| `KilkreathRuinsZone` | `03EC3F:Skyrim.esm` | 24 | **T5** | 30 | Meridia / DA09 |
| `RavenscarHollowZone` | `03EC59:Skyrim.esm` | 14 | **T4** | 21 | HagravenNest |
| `BluePalaceWingZone` | `03EBF4:Skyrim.esm` | 8 | **T3** | 14 | no LocType - fallback from vanilla min 8 |
| `DLC1ForebearsHoldoutZone` | `003581:Dawnguard.esm` | — | **T3** | 14 |  |
| `DaintySloadZone` | `07B919:Skyrim.esm` | 8 | **T3** | 14 | no LocType - fallback from vanilla min 8 |
| `FortHraggstadZone` | `03EC1F:Skyrim.esm` | 6 | **T3** | 14 | MilitaryFort |
| `NorthwatchKeepZone` | `03EC4F:Skyrim.esm` | 12 | **T3** | 14 | WarlockLair |
| `PinemoonCaveZone` | `03EC50:Skyrim.esm` | 6 | **T3** | 14 | VampireLair |
| `PotemasCatacombsZone` | `03EC54:Skyrim.esm` | 6 | **T3** | 14 | VampireLair |
| `RimerockBurrowZone` | `03EC5E:Skyrim.esm` | 6 | **T3** | 14 | WerewolfLair |
| `ThalmorEmbassyZone` | `027F6F:Skyrim.esm` | 2 | **T3** | 14 | MQ201 |
| `WolfskullCaveZone` | `03EC8E:Skyrim.esm` | 8 | **T3** | 14 | WarlockLair |
| `BrokenOarGrottoZone` | `03EBFC:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `ClearpinePondZone` | `03EBFF:Skyrim.esm` | 8 | **T2** | 8 | SprigganGrove |
| `DoomstoneSteedZone` | `0D5682:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `EastEmpireWarehouseZone` | `05FBA6:Skyrim.esm` | 8 | **T2** | 8 | settlement (Dwelling Store) |
| `IronbackHideoutZone` | `0EF545:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `KatariahZone` | `0BBB46:Skyrim.esm` | 6 | **T2** | 8 | settlement (Ship) |
| `OrphansTearZone` | `03EC6C:Skyrim.esm` | 6 | **T2** | 8 | Shipwreck |
| `PinefrostTowerZone` | `0EF0BD:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `ShadowgreenCavernZone` | `03EC64:Skyrim.esm` | 8 | **T2** | 8 | SprigganGrove |
| `WidowsWatchRuinsZone` | `0EF0AA:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `SteepfallBurrowZone` | `03EC79:Skyrim.esm` | 2 | **T1** | 4 | AnimalDen |

#### the Pale  — 23 zones · T2×11 · T3×4 · T4×4 · T5×4

| Encounter zone | FormKey | van. Min | **Tier** | `N` | Rule |
|---|---|---|---|---|---|
| `DuskglowCreviceZone` | `03EC10:Skyrim.esm` | 18 | **T5** | 30 | FalmerHive |
| `HighGateRuinsZone` | `03EC34:Skyrim.esm` | 24 | **T5** | 30 | Vokun |
| `IrkngthandZone` | `03EC3E:Skyrim.esm` | 12 | **T5** | 30 | DwarvenAutomatons + FalmerHive |
| `WeynonStonesZone` | `0BC0AD:Skyrim.esm` | 18 | **T5** | 30 | no LocType - fallback from vanilla min 18 |
| `ForsakenCaveZone` | `03EC19:Skyrim.esm` | 6 | **T4** | 21 | DraugrCrypt +word wall |
| `RaldbtharZone` | `090575:Skyrim.esm` | 12 | **T4** | 21 | DwarvenAutomatons |
| `SilverdriftLairZone` | `03EC70:Skyrim.esm` | 6 | **T4** | 21 | DraugrCrypt +word wall |
| `VolunruudZone` | `03EC88:Skyrim.esm` | 14 | **T4** | 21 | DraugrCrypt +word wall |
| `DLC1DimhollowCryptZone` | `004EE7:Dawnguard.esm` | 6 | **T3** | 14 | DG entry dungeon |
| `HillgrundsTombZone` | `03EC36:Skyrim.esm` | 6 | **T3** | 14 | DraugrCrypt |
| `KorvanjundZone` | `03EC40:Skyrim.esm` | 12 | **T3** | 14 | DraugrCrypt |
| `NightcallerTempleZone` | `03EC7D:Skyrim.esm` | 18 | **T3** | 14 | WarlockLair + MilitaryFort |
| `BlizzardRestZone` | `0A3855:Skyrim.esm` | 2 | **T2** | 8 | GiantCamp → region floor 2 |
| `BrinehammerZone` | `03EC67:Skyrim.esm` | 6 | **T2** | 8 | Shipwreck |
| `BronzeWaterCaveZone` | `046BBC:Skyrim.esm` | 2 | **T2** | 8 | AnimalDen → region floor 2 |
| `DawnstarSanctuaryZone` | `0919A0:Skyrim.esm` | 8 | **T2** | 8 | settlement (Town Dwelling) |
| `FrostmereCryptZone` | `03EC7C:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `HalloftheVigilantZone` | `0C3442:Skyrim.esm` | 5 | **T2** | 8 | no LocType - fallback from vanilla min 5 |
| `RedRoadPassZone` | `03EC5D:Skyrim.esm` | 2 | **T2** | 8 | GiantCamp → region floor 2 |
| `ShroudedGroveZone` | `03EC6D:Skyrim.esm` | 8 | **T2** | 8 | SprigganGrove |
| `TumbleArchPassZone` | `03EC82:Skyrim.esm` | 2 | **T2** | 8 | GiantCamp → region floor 2 |
| `WindwardRuinsZone` | `0C2EEE:Skyrim.esm` | 5 | **T2** | 8 | no LocType - fallback from vanilla min 5 |
| `YorgrimOverlookZone` | `0C3429:Skyrim.esm` | 5 | **T2** | 8 | no LocType - fallback from vanilla min 5 |

#### Winterhold  — 31 zones · T2×16 · T3×8 · T4×2 · T5×5

| Encounter zone | FormKey | van. Min | **Tier** | `N` | Rule |
|---|---|---|---|---|---|
| `BlackreachZone` | `03EBED:Skyrim.esm` | 18 | **T5** | 30 | MQ205 |
| `FrostflowLighthouseZone` | `03EC24:Skyrim.esm` | 18 | **T5** | 30 | FalmerHive |
| `MountAnthorZone` | `03EC4B:Skyrim.esm` | 10 | **T5** | 30 | DragonLair +word wall |
| `SightlessPitZone` | `03EC6E:Skyrim.esm` | 18 | **T5** | 30 | FalmerHive |
| `StillbornCaveZone` | `03EC7A:Skyrim.esm` | 18 | **T5** | 30 | FalmerHive |
| `AlftandZone` | `03EBE6:Skyrim.esm` | 16 | **T4** | 21 | MQ205 |
| `TowerOfMzarkZone` | `10F67D:Skyrim.esm` | 18 | **T4** | 21 | DwarvenAutomatons |
| `DriftshadeSanctuaryZone` | `03EC0D:Skyrim.esm` | 6 | **T3** | 14 | MilitaryFort |
| `FortKastavZone` | `03EC20:Skyrim.esm` | 6 | **T3** | 14 | MilitaryFort |
| `HobsFallCaveZone` | `03EC38:Skyrim.esm` | 8 | **T3** | 14 | WarlockLair |
| `SaarthalZone` | `03EC61:Skyrim.esm` | 6 | **T3** | 14 | DraugrCrypt |
| `SnowVeilSanctumZone` | `03EC74:Skyrim.esm` | 6 | **T3** | 14 | DraugrCrypt |
| `YngolBarrowZone` | `03EC8F:Skyrim.esm` | 6 | **T3** | 14 | DraugrCrypt |
| `YngvildZone` | `03EC90:Skyrim.esm` | 8 | **T3** | 14 | WarlockLair |
| `YsgramorsTombZone` | `03EC91:Skyrim.esm` | 6 | **T3** | 14 | DraugrCrypt |
| `BleakcoastCaveZone` | `03EBEE:Skyrim.esm` | 2 | **T2** | 8 | AnimalDen → region floor 2 |
| `DoomstoneSerpentZone` | `0D5684:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `DoomstoneTowerZone` | `0D5681:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `FortFellhammerZone` | `03EC1D:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp |
| `HelasFollyZone` | `03EC68:Skyrim.esm` | 6 | **T2** | 8 | Shipwreck |
| `JourneymansNookZone` | `0EF54B:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `PilgrimsTrenchZone` | `03EC69:Skyrim.esm` | 6 | **T2** | 8 | Shipwreck |
| `PrideofTelVosZone` | `03EC6A:Skyrim.esm` | 12 | **T2** | 8 | Shipwreck |
| `RockjointIslandZone` | `03EC16:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `SeptimusSignusOutpostZone` | `0D440E:Skyrim.esm` | 2 | **T2** | 8 | no LocType - fallback from vanilla min 2 → region floor 2 |
| `SkytempleRuinsZone` | `0EF0B1:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `SnowpointBeaconZone` | `0C2EF9:Skyrim.esm` | 5 | **T2** | 8 | BanditCamp |
| `WaywardPassZone` | `0C2EFD:Skyrim.esm` | 5 | **T2** | 8 | no LocType - fallback from vanilla min 5 |
| `WhistlingMineZone` | `03EC8A:Skyrim.esm` | 8 | **T2** | 8 | Mine |
| `WinterWarZone` | `03EC6B:Skyrim.esm` | 6 | **T2** | 8 | BanditCamp + Shipwreck |
| `WinterholdCollegeMiddenZone` | `10D415:Skyrim.esm` | 6 | **T2** | 8 | settlement (Dwelling Guild) |

#### the Reach  — 38 zones · T3×16 · T4×15 · T5×7

| Encounter zone | FormKey | van. Min | **Tier** | `N` | Rule |
|---|---|---|---|---|---|
| `DeadCroneRockZone` | `03EC0A:Skyrim.esm` | 14 | **T5** | 30 | HagravenNest +word wall |
| `GloomreachZone` | `03EC2A:Skyrim.esm` | 18 | **T5** | 30 | FalmerHive |
| `HagsEndZone` | `03EC30:Skyrim.esm` | 14 | **T5** | 30 | HagravenNest +word wall |
| `LiarsRetreatZone` | `03EC41:Skyrim.esm` | 18 | **T5** | 30 | FalmerHive |
| `LostValleyRedoubtZone` | `03EC46:Skyrim.esm` | 14 | **T5** | 30 | HagravenNest +word wall |
| `RagnvaldZone` | `03EC57:Skyrim.esm` | 24 | **T5** | 30 | Otar |
| `ValthumeZone` | `03EC86:Skyrim.esm` | 24 | **T5** | 30 | Hevnoraak |
| `BleakwindBluffZone` | `03EBF0:Skyrim.esm` | 2 | **T4** | 21 | HagravenNest |
| `BlindCliffCaveZone` | `03EBF1:Skyrim.esm` | 14 | **T4** | 21 | HagravenNest |
| `BrokenTowerRedoubtZone` | `03EBF7:Skyrim.esm` | 14 | **T4** | 21 | ForswornCamp |
| `BrucasLeapRedoubtZone` | `03EBF9:Skyrim.esm` | 14 | **T4** | 21 | ForswornCamp |
| `BthardamzZone` | `03EBFA:Skyrim.esm` | 16 | **T4** | 21 | DwarvenAutomatons |
| `CradleStoneTowerZone` | `0B23A0:Skyrim.esm` | 8 | **T4** | 21 | HagravenNest |
| `DeepwoodRedoubtZone` | `03EC0C:Skyrim.esm` | 14 | **T4** | 21 | ForswornCamp |
| `DragonBridgeOverlookZone` | `0B2396:Skyrim.esm` | 8 | **T4** | 21 | ForswornCamp |
| `DruadachRedoubtZone` | `03EC0F:Skyrim.esm` | 14 | **T4** | 21 | ForswornCamp |
| `DustmansCairnZone` | `03EC11:Skyrim.esm` | 6 | **T4** | 21 | DraugrCrypt +word wall |
| `HagRockRedoubtZone` | `03EC2F:Skyrim.esm` | 14 | **T4** | 21 | ForswornCamp |
| `NchuandZelZone` | `03EC4D:Skyrim.esm` | 16 | **T4** | 21 | DwarvenAutomatons |
| `RebelsCairnZone` | `0A828A:Skyrim.esm` | 14 | **T4** | 21 | no LocType - fallback from vanilla min 14 |
| `RedEagleRedoubtZone` | `03EC0E:Skyrim.esm` | 14 | **T4** | 21 | ForswornCamp |
| `ShrineofPeryiteZone` | `0F5BA6:Skyrim.esm` | 12 | **T4** | 21 | no LocType - fallback from vanilla min 12 |
| `CidhnaMineZone` | `03EBFD:Skyrim.esm` | 6 | **T3** | 14 | settlement (Jail) → region floor 3 |
| `CliffsideRetreatZone` | `0B238E:Skyrim.esm` | 8 | **T3** | 14 | no LocType - fallback from vanilla min 8 |
| `DeepFolkCrossingZone` | `0B2392:Skyrim.esm` | 8 | **T3** | 14 | no LocType - fallback from vanilla min 8 |
| `DoomstoneLoverZone` | `0D5687:Skyrim.esm` | 6 | **T3** | 14 | no LocType - fallback from vanilla min 6 → region floor 3 |
| `FortSungardZone` | `03EC23:Skyrim.esm` | 6 | **T3** | 14 | MilitaryFort |
| `FourSkullLookoutZone` | `0B23AD:Skyrim.esm` | 8 | **T3** | 14 | BanditCamp → region floor 3 |
| `HarmugstahlZone` | `03EC33:Skyrim.esm` | 8 | **T3** | 14 | WarlockLair |
| `MarkarthAbandonedHouseZone` | `10D0C3:Skyrim.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `MarkarthWizardsQuarters02Zone` | `05CF97:Skyrim.esm` | 6 | **T3** | 14 | settlement (Dwelling) → region floor 3 |
| `MarkarthWizardsQuartersZone` | `05CF96:Skyrim.esm` | 6 | **T3** | 14 | settlement (Dwelling) → region floor 3 |
| `MorKhazgurZone` | `06E2F1:Skyrim.esm` | 6 | **T3** | 14 | OrcStronghold → region floor 3 |
| `PurewaterRunZone` | `03EC55:Skyrim.esm` | 2 | **T3** | 14 | no LocType - fallback from vanilla min 2 → region floor 3 |
| `ReachcliffCaveZone` | `03EC5A:Skyrim.esm` | 6 | **T3** | 14 | DraugrCrypt |
| `ReachwaterRockZone` | `03EC5B:Skyrim.esm` | 6 | **T3** | 14 | DraugrCrypt |
| `ReachwindEyrieZone` | `0B23A6:Skyrim.esm` | 8 | **T3** | 14 | no LocType - fallback from vanilla min 8 |
| `SoljundsSinkholeZone` | `03EC75:Skyrim.esm` | 6 | **T3** | 14 | DraugrCrypt |

#### Solstheim  — 48 zones · T2×19 · T3×17 · T4×5 · T5×3 · T6×4

| Encounter zone | FormKey | van. Min | **Tier** | `N` | Rule |
|---|---|---|---|---|---|
| `DLC2DremoraShopZone` | `01FF29:Dragonborn.esm` | — | **T6** | 40 | Apocrypha |
| `DLC2GyldenhulBarrowZone` | `0142A9:Dragonborn.esm` | 40 | **T6** | 40 | vanilla 40, highest in game |
| `DLC2KolbjornBarrowZone` | `0142BE:Dragonborn.esm` | 30 | **T6** | 40 | Ahzidal, fixed 60 |
| `DLC2TempleOfMiraakZone` | `0142B7:Dragonborn.esm` | 30 | **T6** | 40 | MQ capstone |
| `DLC2AshfallowZone` | `0142D2:Dragonborn.esm` | 25 | **T5** | 30 | no LocType - fallback from vanilla min 25 |
| `DLC2ColdcinderCaveZone` | `03A42E:Dragonborn.esm` | 20 | **T5** | 30 | no LocType - fallback from vanilla min 20 |
| `DLC2FortFrostmothZone` | `014292:Dragonborn.esm` | 20 | **T5** | 30 | no LocType - fallback from vanilla min 20 |
| `DLC2AltarofThrondZone` | `014295:Dragonborn.esm` | 10 | **T4** | 21 | HagravenNest |
| `DLC2FahlbtharzZone` | `0142A1:Dragonborn.esm` | 25 | **T4** | 21 | DwarvenAutomatons |
| `DLC2KagrumezZone` | `0142A3:Dragonborn.esm` | 25 | **T4** | 21 | DwarvenAutomatons |
| `DLC2NchardakZone` | `0142B5:Dragonborn.esm` | 25 | **T4** | 21 | DwarvenAutomatons |
| `DLC2SaeringsWatchZone` | `019D2A:Dragonborn.esm` | 25 | **T4** | 21 | DragonLair |
| `DLC2AbandonedLodgeZone` | `0142CD:Dragonborn.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `DLC2BujoldsRetreatZone` | `0142D7:Dragonborn.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `DLC2FrostmoonCragZone` | `0142D8:Dragonborn.esm` | 10 | **T3** | 14 | WerewolfLair |
| `DLC2HighpointTowerZone` | `0184FD:Dragonborn.esm` | 20 | **T3** | 14 | WarlockLair + MilitaryFort |
| `DLC2HoldingCellBardZone` | `03A4A2:Dragonborn.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `DLC2HrothmundsBarrowZone` | `017BAE:Dragonborn.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `DLC2MoesringPassZone` | `0142DB:Dragonborn.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `DLC2POI13Zone` | `0142D9:Dragonborn.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `DLC2RamshackleTradingPostZone` | `034EE7:Dragonborn.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `DLC2RavenRockMineZone` | `01429B:Dragonborn.esm` | 30 | **T3** | 14 | DraugrCrypt |
| `DLC2SnowcladRuinsZone` | `0247C7:Dragonborn.esm` | 10 | **T3** | 14 | WerebearLair |
| `DLC2StoneBeastZone` | `014297:Dragonborn.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `DLC2StoneEarthZone` | `0142A5:Dragonborn.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `DLC2StoneSunZone` | `0142DD:Dragonborn.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `DLC2StoneWaterZone` | `0142E0:Dragonborn.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `DLC2StoneWindZone` | `0142E1:Dragonborn.esm` | 10 | **T3** | 14 | no LocType - fallback from vanilla min 10 |
| `DLC2VahloksTombZone` | `0142BD:Dragonborn.esm` | 30 | **T3** | 14 | DraugrCrypt |
| `DLC2BenkongerikeZone` | `014299:Dragonborn.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `DLC2BloodskalBarrowBanditZone` | `03A080:Dragonborn.esm` | 10 | **T2** | 8 | BanditCamp |
| `DLC2BristlebackCaveZone` | `032893:Dragonborn.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `DLC2BrodirGroveZone` | `01429D:Dragonborn.esm` | 10 | **T2** | 8 | BanditCamp |
| `DLC2BrokenTuskMineZone` | `033953:Dragonborn.esm` | 6 | **T2** | 8 | Mine |
| `DLC2CastleKarstaagRuinsZone` | `01429F:Dragonborn.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `DLC2DamphallMineZone` | `0296DB:Dragonborn.esm` | 10 | **T2** | 8 | BanditCamp |
| `DLC2FrosselZone` | `0142A7:Dragonborn.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `DLC2GlacialCaveZone` | `0142D1:Dragonborn.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `DLC2HaknirsShoalZone` | `0142CF:Dragonborn.esm` | 10 | **T2** | 8 | BanditCamp |
| `DLC2HeadwatersOfHarstradZone` | `039F99:Dragonborn.esm` | 25 | **T2** | 8 | SprigganGrove |
| `DLC2HorkerIslandZone` | `0142AB:Dragonborn.esm` | 10 | **T2** | 8 | AnimalDen → region floor 2 |
| `DLC2HrodulfsHouseZone` | `0142D0:Dragonborn.esm` | 10 | **T2** | 8 | BanditCamp |
| `DLC2NorthshoreLandingZone` | `0142D4:Dragonborn.esm` | 10 | **T2** | 8 | AnimalDen → region floor 2 |
| `DLC2POI10Zone` | `0142D6:Dragonborn.esm` | 10 | **T2** | 8 | BanditCamp + Shipwreck |
| `DLC2RRTempleTombZone` | `03CFCB:Dragonborn.esm` | 20 | **T2** | 8 | settlement (Dwelling Temple) |
| `DLC2ThirskExteriorZone` | `01E284:Dragonborn.esm` | 6 | **T2** | 8 | settlement (Habitation Settlement) |
| `DLC2ThirskInteriorZone` | `01E11D:Dragonborn.esm` | 6 | **T2** | 8 | settlement (Dwelling) |
| `DLC2WhiteRidgeBarrowZone` | `0142BF:Dragonborn.esm` | 30 | **T2** | 8 | AnimalDen → region floor 2 |

#### Unparented / no hold  — 38 zones · T1×4 · T2×9 · T3×3 · T4×3 · T5×10 · T6×8 · T7×1

| Encounter zone | FormKey | van. Min | **Tier** | `N` | Rule |
|---|---|---|---|---|---|
| `DLC1_VCDungeonZone` | `003580:Dawnguard.esm` | 10 | **T7** | 50 | Castle Volkihar - the only T7; needs the gate-60 vampire rung |
| `DLC1FalmerValleyTempleZone` | `01379D:Dawnguard.esm` | 13 | **T6** | 40 | Vale temple - untagged |
| `DLC2Book01DungeonZone` | `0142B3:Dragonborn.esm` | 25 | **T6** | 40 | Apocrypha - flat |
| `DLC2Book02DungeonZone` | `0142B1:Dragonborn.esm` | 25 | **T6** | 40 | Apocrypha - flat |
| `DLC2Book03DungeonZone` | `0142B2:Dragonborn.esm` | 25 | **T6** | 40 | Apocrypha - flat |
| `DLC2Book04DungeonZone` | `01EE16:Dragonborn.esm` | 25 | **T6** | 40 | Apocrypha - flat |
| `DLC2Book06DungeonZone` | `01EE18:Dragonborn.esm` | 25 | **T6** | 40 | Apocrypha - flat |
| `DLC2Book07DungeonZone` | `01EE19:Dragonborn.esm` | 25 | **T6** | 40 | Apocrypha - flat |
| `DLC2MiscBookLevel1Zone` | `0142AD:Dragonborn.esm` | 25 | **T6** | 40 | Apocrypha - flat (Book05) |
| `DLC1DarkfallPassageZone` | `0162AD:Dawnguard.esm` | 18 | **T5** | 30 | Darkfall - untagged |
| `DLC1FalmerValleyZone` | `012F42:Dawnguard.esm` | 13 | **T5** | 30 | Forgotten Vale - untagged |
| `DLC1GlacialCreviceZone` | `0162AE:Dawnguard.esm` | 18 | **T5** | 30 | untagged |
| `DLC1_SoulCairnZone` | `00643C:Dawnguard.esm` | 13 | **T5** | 30 | Soul Cairn - untagged |
| `DLC1zFalmerValley01Zone` | `0162B1:Dawnguard.esm` | 18 | **T5** | 30 | Vale - untagged |
| `DLC1zFalmerValley02Zone` | `0162B3:Dawnguard.esm` | 18 | **T5** | 30 | Vale - untagged |
| `DLC1zFalmerValley03Zone` | `0162B5:Dawnguard.esm` | 18 | **T5** | 30 | Vale - untagged |
| `DLC2Book05DungeonZone` | `01EE17:Dragonborn.esm` | 25 | **T5** | 30 | no LocType - fallback from vanilla min 25 |
| `SovngardeZone` | `03EC76:Skyrim.esm` | 24 | **T5** | 30 | no LocType - fallback from vanilla min 24 |
| `VolskyggeZone` | `03EC87:Skyrim.esm` | 24 | **T5** | 30 | no LocType - fallback from vanilla min 24 |
| `DLC1DarkfallCaveZone` | `00A879:Dawnguard.esm` | 10 | **T4** | 21 | Darkfall - untagged |
| `GjukarsMonumentZone` | `0E66A2:Skyrim.esm` | 12 | **T4** | 21 | no LocType - fallback from vanilla min 12 |
| `IronbindBarrowZone` | `022F07:Skyrim.esm` | 6 | **T4** | 21 | DraugrCrypt +word wall |
| `GloomboundMineZone` | `03EC29:Skyrim.esm` | 8 | **T3** | 14 | no LocType - fallback from vanilla min 8 |
| `NightingaleHallZone` | `047D27:Skyrim.esm` | 8 | **T3** | 14 | no LocType - fallback from vanilla min 8 |
| `RiftenRatwayZone` | `09FBB9:Skyrim.esm` | 8 | **T3** | 14 | no LocType - fallback from vanilla min 8 |
| `AzurasStarZone` | `03EBEC:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `BrinewaterGrottoZone` | `05F429:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `DLC1_AncestorsGladeZone` | `003582:Dawnguard.esm` | — | **T2** | 8 | non-hostile |
| `DoomstoneMageZone` | `0D5686:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `DoomstoneWarriorZone` | `0D5680:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `DushnikhYalZone` | `0A3856:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `FortDunstadZone` | `03EC1C:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `FortGreymoorZone` | `03EC1B:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `FortNeugradZone` | `03EC21:Skyrim.esm` | 6 | **T2** | 8 | no LocType - fallback from vanilla min 6 |
| `DLC2TelMithrynZone` | `01D751:Dragonborn.esm` | — | **T1** | 4 | no LocType - fallback from vanilla min 0 |
| `NoResetZone` | `0F90B1:Skyrim.esm` | 1 | **T1** | 4 | no LocType - fallback from vanilla min 1 |
| `NoZoneZone` | `00001E:Skyrim.esm` | — | **T1** | 4 | no LocType - fallback from vanilla min 0 |
| `RiverwoodZone` | `018A45:Skyrim.esm` | — | **T1** | 4 | no LocType - fallback from vanilla min 0 |
<!-- END GENERATED TABLES -->

---

## Sources

Computed in this document from `reference/` (`[verified]`):
`reference/Base/*/EncounterZones/` (358 records → 355 FormKeys) ·
`reference/Base/*/Locations/` (763 locations: `Keywords`, `ParentLocation`,
`LocationRefTypeReferencesStatic`) · `reference/Base/*/Keywords/` (1,260 keywords).

Design inputs, which carry their own citations: `design/tiers.md` · `design/engine-behaviour.md` ·
`world/dungeons.md` §§1–3 · `world/regions.md` §§2–5 · `world/progression.md` §§4–5 ·
`world/enemy-taxonomy.md` §2.3, §6 · `world/lore-constraints.md` §3.
