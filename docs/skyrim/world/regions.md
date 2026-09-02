---
id: "skyrim/world/regions"
title: "Regions"
slug: "regions"
section: "skyrim/world"
game: "skyrim"
kind: "world"
project: null
mod: null
tags: ["skyrim", "world-research", "vanilla", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/world/regions.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: "Phase 1, document 4"
confidence: {"author": 0, "community": 1, "unverified": 6, "upstream": 0, "verified": 29}
lines: 409
content_sha256: "99b12b8c5c77264f8693667259bcb4d72c227d1bc1937d2fe802ba062baff141"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Regions

**Phase 1, document 4.** Skyrim's nine holds and the DLC regions as the records describe them — where
they are, what they are made of, and whether vanilla encodes any spatial danger gradient at all.

§1–§3 cover `Skyrim.esm`; **§4 covers Dawnguard, Hearthfire and Dragonborn**, which turn out to be
structurally different from the base game in ways that matter.

`dungeons.md` established that **dungeon type predicts level and hold does not**. This document asks
the follow-up: is there a *geographic* gradient hiding underneath the hold boundaries, and if not,
what does Ehlnofey have to author to satisfy bone 2 (*danger is legible*)?

Read `overview.md` and `dungeons.md` first. Confidence marks as elsewhere: `[verified]` = read in
`reference/`, `[community]` = established modding knowledge not re-tested, `[unverified]` = plausible,
unchecked.

---

## 1. There is no "region" record — the geography levers

| Candidate | Verdict |
|---|---|
| `REGN` (317 records) | **Not a difficulty lever.** These are landscape and audio regions — `AlexTundraSnow07`, `AudioIntDungeonCave01`, `Brie2npassPineForest03`. Named after the level designers who made them. `[verified]` |
| `LCTN` hold hierarchy | **The usable one.** 9 `Skyrim.esm` locations carry `LocTypeHold` (016771) — **10 with Dragonborn's Solstheim** (§4.3); every other location reaches one through its `ParentLocation` chain. Dawnguard's and Apocrypha's regions carry **no keywords at all** and reach nothing. `[verified]` |
| `WRLD` worldspaces | `Tamriel` (00003C) plus ~90 small interior worldspaces. Not a difficulty axis. `[verified]` |
| `LCTN.WorldspaceCellsStatic.Coordinates` | **Actual map position.** Each location lists the exterior cells it occupies; the centroid is a usable map coordinate. `[verified]` |
| `LocSet*` keywords | Tileset — the *visual* signal a player reads on approach. Relevant to legibility. `[verified]` |

### Method for the coordinates

Every `LCTN` with an exterior presence lists its cells:

```yaml
# BleakFallsBarrowLocation - 018EE9
WorldspaceCellsStatic:
  Coordinates:
  - -3, -13
  - -4, -12
  - -3, -12
  …
```

Taking the mean gives a cell-grid position (1 cell = 4096 game units). Coverage: **344 of 638
locations** have their own cells; falling back to the parent location covers **221 of the 226
dungeons**. Sanity check against the real map `[verified]`:

| Location | Centroid (cell X, Y) |
|---|---|
| Helgen | 3.2, −19.5 |
| Riverwood | 4.5, −10.0 |
| Whiterun | 5.0, −2.6 |
| Bleak Falls Barrow | −1.8, −11.5 |

Helgen far south, Whiterun central, Bleak Falls just west of Riverwood. The coordinates are real.

---

## 2. The central finding: vanilla's gradient is in *placement*, not in levels

Using Helgen (the game's opening) as the origin and measuring straight-line cell distance to each
dungeon, against its `ECZN.MinLevel` — 193 dungeons with both `[verified]`:

```
Pearson r, MinLevel vs distance from Helgen    = +0.251
Pearson r, MinLevel vs distance from Whiterun  = +0.150

dist band (cells)     N   mean MinLevel
        0–10         11        5.3
       10–20         20        5.3
       20–30         42        7.6
       30–40         50        8.1
       40–50         45       10.6
       50–60         23        9.7
```

A weak but clean, monotonic rise out to ~50 cells. Tempting to call that the danger gradient — but
it is a **composition effect**, and controlling for dungeon type dissolves it entirely.

### Within a type, distance predicts nothing

`[verified]`, types with n ≥ 6:

| Type | N | r(distance, MinLevel) |
|---|---|---|
| BanditCamp | 31 | **+0.01** |
| AnimalDen | 17 | **−0.02** |
| ForswornCamp | 8 | −0.04 |
| DraugrCrypt | 21 | −0.14 |
| GiantCamp | 12 | −0.24 |
| HagravenNest | 10 | +0.14 |
| SprigganGrove | 8 | +0.33 |
| FalmerHive | 13 | −0.36 |
| DwarvenAutomatons | 6 | +0.47 |
| WarlockLair | 18 | +0.55 |
| VampireLair | 7 | *(flat — all 7 are MinLevel 6)* |
| DragonPriestLair | 6 | *(flat — all 6 are MinLevel 24)* |

Scattered around zero, and the three largest samples are dead flat.

### Across types, placement tracks difficulty strongly

`[verified]`:

| Type | N | Mean distance from Helgen | Mean MinLevel |
|---|---|---|---|
| VampireLair | 7 | 24.8 | 6.0 |
| GiantCamp | 12 | 26.9 | 3.8 |
| SprigganGrove | 8 | 28.6 | 8.2 |
| AnimalDen | 17 | 30.0 | 2.8 |
| BanditCamp | 31 | 30.4 | 5.9 |
| DraugrCrypt | 21 | 32.9 | 6.7 |
| WarlockLair | 18 | 33.3 | 7.7 |
| DragonLair | 2 | 35.8 | 10.0 |
| HagravenNest | 10 | 38.0 | 12.2 |
| FalmerHive | 13 | 38.5 | 16.8 |
| DwarvenAutomatons | 6 | 38.8 | 15.3 |
| DragonPriestLair | 6 | 42.6 | 24.0 |
| ForswornCamp | 8 | 45.6 | 13.2 |

**r = +0.808 across the 14 types.** `[verified]`

> **The conclusion.** Bethesda did not make distant dungeons harder. They placed the harder *kinds*
> of dungeon further from where the player starts. The spatial difficulty gradient in Skyrim is real,
> and it is composed entirely out of *what sort of place goes where* — never out of a per-dungeon
> number.

This reconciles with `dungeons.md` §2 exactly: hold membership predicts nothing because holds are
large and mixed, but *distance from the start* predicts type, and type predicts level.

**For Ehlnofey this is the most useful thing in Phase 1 so far.** It says the regional gradient bone 2
asks for does not have to be invented against the grain of the game — vanilla already works this way,
just weakly and inconsistently. Ehlnofey's regional design can be expressed as *"which dungeon types
belong in which region"*, which is a far smaller, more legible and more lore-defensible decision than
assigning 226 individual numbers. Carry this into `design/difficulty-map.md`.

---

## 3. The nine holds of Skyrim

Centroids from dungeon coordinates; levels from `ECZN.MinLevel`. `[verified]` Dragonborn adds a tenth
hold — see §4.3.

| Hold | Dungeons | Centroid (X, Y) | Mean level | Max | Word walls | No zone | `NeverResets` |
|---|---|---|---|---|---|---|---|
| **Falkreath** | 34 | −5.5, −15.4 | **5.9** | 14 | 3 | 4 | 4 |
| **Eastmarch** | 25 | 32.8, −2.6 | 7.3 | 18 | 1 | 2 | 2 |
| **Whiterun** | 21 | −1.3, 0.8 | 7.8 | 24 | 1 | 2 | 2 |
| **the Rift** | 30 | 31.3, −20.9 | 7.9 | 24 | 6 | 5 | 4 |
| **Hjaalmarch** | 18 | −9.5, 14.3 | 7.9 | 24 | 4 | 3 | 3 |
| **Haafingar** | 18 | −25.5, 26.6 | 8.2 | 24 | 2 | 2 | 5 |
| **the Pale** | 24 | 11.1, 12.8 | 9.0 | 24 | 5 | 3 | 5 |
| **Winterhold** | 24 | 23.7, 20.7 | 9.0 | 18 | 1 | 2 | 6 |
| **the Reach** | 31 | −31.5, 4.5 | **12.6** | 24 | 7 | 5 | 9 |

Falkreath lowest at 5.9, the Reach highest at 12.6 — a 2× spread across holds, against a 12× spread
*within* most of them. The hold means are a weak signal, exactly as §2 predicts.

### Composition — what each hold is made of

Dungeon types per hold `[verified]`:

| Hold | Type mix |
|---|---|
| **the Reach** | ForswornCamp ×8 · HagravenNest ×7 · DraugrCrypt ×4 · DwarvenAutomatons ×2 · FalmerHive ×2 · DragonPriestLair ×2 · BanditCamp ×1 · DragonLair ×1 · WarlockLair ×1 |
| **Falkreath** | WarlockLair ×5 · BanditCamp ×4 · SprigganGrove ×4 · AnimalDen ×3 · DraugrCrypt ×3 · VampireLair ×3 · HagravenNest ×2 · DragonLair ×1 · FalmerHive ×1 · GiantCamp ×1 |
| **the Rift** | BanditCamp ×6 · AnimalDen ×5 · DragonLair ×3 · DraugrCrypt ×3 · FalmerHive ×2 · WarlockLair ×2 · DwarvenAutomatons ×1 · DragonPriestLair ×1 · SprigganGrove ×1 |
| **Eastmarch** | BanditCamp ×6 · GiantCamp ×3 · WarlockLair ×3 · AnimalDen ×2 · HagravenNest ×2 · one each of DragonLair, DragonPriestLair, DwarvenAutomatons, FalmerHive, MilitaryFort, VampireLair |
| **Winterhold** | FalmerHive ×4 · DraugrCrypt ×4 · BanditCamp ×3 · WarlockLair ×2 · AnimalDen ×1 · DragonLair ×1 · DwarvenAutomatons ×1 · MilitaryFort ×1 |
| **the Pale** | DraugrCrypt ×5 · GiantCamp ×3 · FalmerHive ×2 · AnimalDen ×1 · BanditCamp ×1 · DragonLair ×1 · DragonPriestLair ×1 · DwarvenAutomatons ×1 · SprigganGrove ×1 · WarlockLair ×1 |
| **Whiterun** | BanditCamp ×6 · AnimalDen ×3 · GiantCamp ×3 · WarlockLair ×2 · FalmerHive ×1 · ForswornCamp ×1 · VampireLair ×1 |
| **Hjaalmarch** | BanditCamp ×3 · DragonLair ×2 · DraugrCrypt ×2 · GiantCamp ×2 · AnimalDen ×1 · DragonPriestLair ×1 · DwarvenAutomatons ×1 · FalmerHive ×1 · VampireLair ×1 |
| **Haafingar** | Cave/coastal mix — DragonPriestLair ×2 · SprigganGrove ×2 · VampireLair ×2 · WarlockLair ×2 · AnimalDen ×1 · BanditCamp ×1 · HagravenNest ×1 |

Tilesets (`LocSet*`), the visual identity a player reads on approach `[verified]`:

| Hold | Dominant tilesets |
|---|---|
| Winterhold | **CaveIce ×6** · NordicRuin ×4 · Cave ×1 · DwarvenRuin ×1 |
| the Reach | Cave ×7 · **NordicRuin ×6** · DwarvenRuin ×2 · FortSet ×1 |
| the Rift | Cave ×7 · NordicRuin ×5 · **FortSet ×3** · DwarvenRuin ×1 |
| Falkreath | Cave ×8 · **CaveIce ×4** · NordicRuin ×4 |
| Eastmarch | **Cave ×8** · DwarvenRuin ×2 · NordicRuin ×1 |
| the Pale | NordicRuin ×5 · DwarvenRuin ×2 · CaveIce ×2 · Cave ×1 |
| Hjaalmarch | **NordicRuin ×5** · Cave ×3 · DwarvenRuin ×1 |
| Haafingar | NordicRuin ×4 · Cave ×4 · CaveIce ×1 |
| Whiterun | Cave ×4 · NordicRuin ×2 · CaveIce ×1 |

### Reading the holds

- **the Reach is the one hold with a real identity.** 15 of its 31 dungeons are Forsworn camps or
  hagraven nests — an actual faction homeland — and it has no giant camps, no spriggan groves, no
  vampire lairs, and exactly one bandit camp. It also has the highest mean level (12.6), the most word
  walls (7) and the most `NeverResets` zones (9). **This is the natural pilot region** for any
  Ehlnofey regional scheme: it already reads as a coherent, hostile place. `[verified]`
- **Whiterun is the starter hold and the records say so.** Bandit camps, animal dens and giant camps
  — the three lowest-tier types — are 12 of its 21 dungeons, and it has **no draugr crypt, no dragon
  lair, no Dwemer ruin and no Dragon Priest lair**. `[verified]`
- **Winterhold is the Falmer/ice hold**: FalmerHive ×4 and CaveIce ×6, the highest concentration of
  both. Its mean level (9.0) is joint-highest after the Reach.
- **Falkreath is the most varied and the softest** — ten different types, mean level 5.9, max 14, and
  the only hold with no zone above 14. Partly an artefact of the parenting oddity below.
- **the Pale is the undead hold**: DraugrCrypt ×5 plus NordicRuin ×5.
- **Eastmarch and the Rift are bandit country** — 6 bandit camps each, the most of any hold.

### The parenting caveat carries over

As recorded in `dungeons.md` §2, `ParentLocation` does not always match the visual map — Bleak Falls
Barrow is parented to **Falkreath**, not Whiterun. That is why Falkreath has 34 dungeons (the most)
and an X range of −32..20 spanning most of the map, and why Whiterun shows no draugr crypt despite
Bleak Falls being the game's tutorial crypt. `[verified]`

**The centroids in §3 are computed from real cell coordinates and are therefore correct even where the
hold assignment is not.** Any Ehlnofey regional rule must choose explicitly between:

- **hold membership** (what the game's own systems read — quest targets, map markers, dialogue), or
- **map position** (what the player perceives).

They disagree for a handful of locations near hold borders. Decide it once, in
`design/difficulty-map.md`, and say which.

---

## 4. The DLC regions

Region membership is defined by **worldspace** (`WRLD`) plus the `LCTN` root each location chains up
to. On both axes the three DLC behave very differently from each other. `[verified]`

| DLC | New worldspaces | New region roots | New dungeons |
|---|---|---|---|
| **Hearthfire** | **none** | **none** | **none** |
| **Dawnguard** | 8 | 0 *(untagged locations)* | 7 |
| **Dragonborn** | 2 | 2 (`DLC2SolstheimLocation`, `DLC2ApocryphaLocation`) | 38 |

### 4.1 Hearthfire adds no region at all

`HearthFires.esm` touches only `Tamriel` and the five city worldspaces — **it defines no new
worldspace, no location outside the existing holds, and not one location tagged `LocTypeDungeon` or
`LocTypeClearable`.** Its 22 locations and 141 factions are homestead ownership bookkeeping. `[verified]`

**Hearthfire is out of scope for Ehlnofey's regional design entirely**, and adding it as a master
would buy nothing.

### 4.2 Dawnguard — new places, no region structure

Eight new worldspaces `[verified]`: `DLC01SoulCairn`, `DLC01FalmerValley` (the Forgotten Vale),
`DLC01Boneyard`, `DLC1DarkfallPassageWorld`, `DLC1AncestorsGladeWorld`, `DLC1ForebearsHoldout`,
`DLC1HunterHQWorld` (Fort Dawnguard), `DLC1VampireCastleCourtyard` (Castle Volkihar). It also
**overrides** `Blackreach`, `Tamriel` and the city worldspaces.

But structurally these are not regions:

> **Every one of Dawnguard's new-world locations carries zero keywords.**
> `DLC1SoulCairnLocation`, `DLC1FalmerValleyLocation`, `DLC1DarkfallCaveLocation`,
> `DLC1DarkfallPassageLocation`, `DLC1_AncestorsGladeLocation`, `DLC1GlacialCreviceLocation`,
> `DLC1ForebearsHoldhoutLocation` *(sic)*, `DLC1VampireCastleLocation`, `DLC1HunterHQLocation` and the
> three `DLC1zFalmerValley0nLocation` records have **no `Keywords:` block at all** — not
> `LocTypeDungeon`, not `LocTypeClearable`, not `LocTypeHold`. `[verified]`

And the zones are detached too. **9 of Dawnguard's 19 encounter zones have no `Location:` field
whatsoever** — they are bound to cells directly `[verified]`:

| Zone | MinLevel | Has `Location`? |
|---|---|---|
| `DLC1_SoulCairnZone` | 13 | **no** |
| `DLC1DarkfallCaveZone` | 10 | **no** |
| `DLC1DarkfallPassageZone` | 18 | **no** |
| `DLC1GlacialCreviceZone` | 18 | **no** |
| `DLC1zFalmerValley01Zone` / `02` / `03` | 18 | **no** |
| `DLC1_VCDungeonZone` (Castle Volkihar) | 10 | **no** |
| `DLC1_AncestorsGladeZone` | *(none)* | **no** |
| `DLC1FalmerValleyZone` / `…TempleZone` | 13 | yes |
| `DLC1ArkngthamzZone` | 16 | yes |
| `DLC1LDBthalftAetheriumForgeZone` | 15 | yes |
| `DLC1RuunvaldZone` | 10 | yes |
| `DLC1DimhollowCryptZone` | 6 | yes |
| `DLC1MolderingRuinsZone`, `DLC1RedwaterDenZone`, `DLC1ForebearsHoldoutZone` | *(none)* | yes |
| `BthalftZone` *(vanilla override)* | 6 | yes |

Compare 270 of 280 vanilla zones having a `Location`. **Any Ehlnofey rule that walks
`ECZN.Location → LCTN → keywords` silently skips half of Dawnguard, including the Soul Cairn and most
of the Forgotten Vale.** This is the single most actionable DLC finding in this document.

Of Dawnguard's 20 dungeon-tagged locations, **only 7 are new** — Arkngthamz, the Aetherium Forge,
Dimhollow Crypt, Ruunvald, Moldering Ruins, Redwater Den and the radiant Falmer dungeon. The other 13
are **overrides of vanilla locations** (Bleak Falls Barrow, Arcwind Point, Reachcliff Cave, Red Eagle
Redoubt, Shimmermist Cave, Swindler's Den, Mzinchaleft, Honeystrand Cave, Deep Folk Crossing,
Bthalft, Traitor's Post, Hall of the Vigilant, and a Rift military camp) that Dawnguard re-tagged for
its radiant vampire/Dawnguard hooks. `[verified]` Those 13 join the master-order list already growing
in `enemy-taxonomy.md` §2.7 and `factions.md` §6.

**Effective level bands** for the Dawnguard regions: Dimhollow 6 · Ruunvald / Darkfall Cave / Castle
Volkihar 10 · Soul Cairn / Forgotten Vale 13 · Aetherium Forge 15 · Arkngthamz 16 · Darkfall Passage /
Glacial Crevice / the three Forgotten Vale sub-zones 18. No Dawnguard zone has a `MaxLevel`.

### 4.3 Dragonborn — Solstheim is a tenth hold

`DLC2SolstheimLocation` (016E2A) is a **root location carrying `LocTypeHold` (016771:Skyrim.esm)**,
exactly like Skyrim's nine. `[verified]` So the correct count for any hold-keyed rule is **ten holds,
not nine** — and a rule written against `Skyrim.esm` alone will silently exclude all of Solstheim.

79 locations chain up to it, 47 with an encounter zone, spanning **MinLevel 6 → 40, mean 14.9** —
against a Skyrim-wide hold mean of 5.9–12.6. Solstheim is both harder and better graded than any
Skyrim hold. Its coordinates live in `DLC2SolstheimWorld`, roughly cell (4..21, 2..22).

Only **1 of Dragonborn's 57 zones lacks a `Location`** (`DLC2TelMithrynZone`) — structurally the
cleanest of the three DLC and cleaner than the base game in this respect. `[verified]`

#### The abandoned region layer

Dragonborn declares three sub-hold region locations — `DLC2RegionAshlandLocation` (01E7DB),
`DLC2RegionGlacierLocation` (01E7DD), `DLC2RegionNorthLocation` (01E7DC) — each parented to
`DLC2SolstheimLocation`, each with no keywords and no cells.

**Nothing uses them.** No location has any of the three as its `ParentLocation`; no quest, faction,
keyword or cell references them. Every one of Solstheim's 79 locations parents *directly* to
`DLC2SolstheimLocation`, flat. `[verified]`

> This is the closest thing to a precedent Ehlnofey has. Bethesda started building exactly the
> sub-hold region layer bone 2 calls for — Ashland / Glacier / North, a climate-and-terrain
> subdivision of a landmass — created the records, and never populated them. The mechanism is
> `LCTN.ParentLocation`, it costs three records per region, and it is already proven to serialize.
> `design/difficulty-map.md` should consider adopting this shape rather than inventing one.

#### Apocrypha

`DLC2ApocryphaLocation` (016E2B) is a second root — **no parent, no keywords, no cells**, in its own
`DLC2ApocryphaWorld`. Nine locations chain to it: Miraak's Tower, one island, and the seven Black
Book dungeons. `[verified]`

| Black Book zone | MinLevel |
|---|---|
| `DLC2Book01DungeonZone` … `DLC2Book07DungeonZone` (Book05 uses `DLC2MiscBookLevel1Zone`) | **25** — all seven identical |
| `DLC2DremoraShopZone` | *(none)*, `MaxLevel: 99` |

Apocrypha is a **flat tier-25 plane** with no internal gradient, reachable from level 1 via any Black
Book. Because it carries no `LocTypeHold` and no `LocType*` at all, it is invisible to both
hold-keyed and type-keyed rules — the same blind spot as Dawnguard's regions, and it must be named
explicitly.

### 4.4 DLC summary for Ehlnofey

| Region | Root `LCTN` | Tagged? | Level band |
|---|---|---|---|
| **Solstheim** | `DLC2SolstheimLocation` 016E2A | `LocTypeHold` | 6 → 40 (mean 14.9) |
| — Ashland / Glacier / North | 01E7DB / 01E7DD / 01E7DC | none — **declared, unused** | — |
| **Apocrypha** | `DLC2ApocryphaLocation` 016E2B | **none** | flat 25 |
| **Soul Cairn** | `DLC1SoulCairnLocation` | **none** | 13 (zone has no `Location`) |
| **Forgotten Vale** | `DLC1FalmerValleyLocation` + 3 sub | **none** | 13 / 18 |
| **Darkfall Cave → Passage** | `DLC1DarkfallCave/PassageLocation` | **none** | 10 → 18 |
| **Castle Volkihar** | `DLC1VampireCastleLocation` | **none** | 10 |
| **Fort Dawnguard** | `DLC1HunterHQLocation` | **none** | — |
| **Ancestor's Glade / Forebears' Holdout / Glacial Crevice** | untagged | **none** | — / — / 18 |
| **Hearthfire** | — | — | **adds nothing** |

---

## 5. What Ehlnofey has to author

1. **Express the regional gradient as type placement, not per-dungeon numbers.** Vanilla already does
   this at r = +0.81; Ehlnofey's job is to sharpen it, not replace it. A rule of the form "the Reach
   contains no tier-1 content" is cheaper, more legible and more lore-defensible than 226 assignments.
2. **The existing radial shape is a usable spine.** 0–20 cells from Helgen averages 5.3; 40–50
   averages 10.6. Ehlnofey can keep that shape and simply widen the range and remove the exceptions.
3. **Legibility has to come from tileset, faction and geography** — `factions.md` §3 established there
   is no faction-level lever for hostility, and `enemy-taxonomy.md` showed level is invisible to the
   player. The `LocSet*` table above is the signal the player actually reads on approach: an ice cave
   in Winterhold *looks* different from a bandit fort in the Rift. Tie tiers to things that are
   visible.
4. **The Reach is the pilot.** Highest mean level, strongest factional identity, most word walls, most
   never-reset zones, and a clean type profile. If a regional tier works there it will work anywhere.
5. **Whiterun must stay soft.** It is the tutorial hold by composition, and the four capped zones from
   `dungeons.md` §2 (Bleak Falls, Embershard, Halted Stream, White River Watch) are all on the
   Riverwood–Whiterun path. Whatever Ehlnofey does, that corridor is where a new character learns the
   rules.

## 6. Open questions

1. **Hold membership vs map position** — which does `difficulty-map.md` key on? They disagree near
   borders and the disagreement is not random (see §3). Needs a decision, not a default.
2. **Do the 8 unzoned exterior dragon lairs need regional treatment at all**, given they have no
   `ECZN` to carry a level? `[unverified]`, shared with `dungeons.md` §6.
3. **Does the player actually traverse the map radially?** The r = +0.25 assumes distance-from-Helgen
   is a proxy for progression order. Carriages, the main quest and fast travel all break that.
   `progression.md` should test it against the real routes before `difficulty-map.md` leans on the
   radial spine. `[unverified]`
4. **Solstheim is a tenth hold in the record data** (§4.3), not an optional extra — any hold-keyed
   rule written against `Skyrim.esm` alone silently excludes it. Whether Ehlnofey *covers* it is still
   a scope decision for `implementation-strategy.md`, but "nine holds" is factually wrong as a filter.
5. **How should the untagged regions be reached?** The Soul Cairn, Forgotten Vale, Darkfall, Castle
   Volkihar and all of Apocrypha carry no `LocType*` keywords, and 9 of Dawnguard's 19 zones carry no
   `Location` either (§4.2). A rule walking `ECZN.Location → LCTN → keywords` misses them entirely.
   Options are naming their zones explicitly, adding keywords via override, or excluding them —
   decide in `design/difficulty-map.md`. `[verified]` that they are unreachable this way;
   `[unverified]` which fix is cheapest.
6. **Should Ehlnofey populate Dragonborn's abandoned `DLC2Region*` layer** (§4.3) or define its own
   sub-hold regions? Bethesda's stub proves the `LCTN.ParentLocation` shape works and costs three
   records per region. `[unverified]` whether re-parenting existing locations is safe.

---

## 7. Method note

All coordinates here are **cell-grid means from `WorldspaceCellsStatic.Coordinates`**, not from
`WorldLocationMarkerRef` (which would require resolving placed-object positions across every
worldspace file — expensive and unnecessary at this resolution). One cell = 4096 units. Distances are
straight-line in cells and ignore terrain, which for a mountainous province systematically
under-states real travel cost — the Reach in particular is much further "away" in practice than its
centroid suggests. Treat the r values as lower bounds on any true relationship with travel effort.
`[verified]` for the arithmetic, `[unverified]` for the travel-cost interpretation.
