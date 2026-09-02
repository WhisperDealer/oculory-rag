---
id: "skyrim/world/progression"
title: "Progression"
slug: "progression"
section: "skyrim/world"
game: "skyrim"
kind: "world"
project: null
mod: null
tags: ["skyrim", "world-research", "vanilla", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/world/progression.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: "Phase 1, document 5"
confidence: {"author": 0, "community": 2, "unverified": 7, "upstream": 0, "verified": 14}
lines: 223
content_sha256: "55b79d88431e5ae543b6847aa87f768119b961332faaaae42e99db1ecc949ae4"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Progression

**Phase 1, document 5.** The routes a player actually takes through Skyrim, and what — if anything —
gates them.

`regions.md` §2 found a weak radial difficulty gradient outward from Helgen and flagged an assumption
underneath it: *does the player actually traverse the map radially?* This document tests that, and
answers the broader question Phase 3 needs — **in a world that no longer scales, what stops a level-1
character walking into a level-40 dungeon?**

The short answer is **almost nothing**, and that makes bone 2 (*danger is legible*) the load-bearing
design problem for the whole mod.

Confidence marks: `[verified]` = read in `reference/`, `[community]` = established modding knowledge
not re-tested here, `[unverified]` = plausible, unchecked.

---

## 1. What "content" consists of

1,811 `QUST` records in `Skyrim.esm`. By `Type` `[verified]`:

| Type | Count | | Type | Count |
|---|---|---|---|---|
| Misc | 282 | | ThievesGuild | 29 |
| CivilWar | 47 | | SideQuest | 27 |
| MainQuest | 44 | | MageGuild | 24 |
| DarkBrotherhood | 40 | | Daedric | 16 |
| CompanionQuests | 31 | | *(untyped)* | ~1,270 |

The untyped bulk is dialogue scaffolding, radiant scripting and world-interaction quests (`WE*`
world encounters, `WI*` world interactions, `Favor*`, `BQ*` bounties, `DialogueX` topics).

---

## 2. Level gating is almost entirely absent

Searching every quest for a condition of the form `GetLevelConditionData` run on `PlayerRef`
(000014) yields **30 conditions across all 1,811 quests**. `[verified]`

Every one of them is on ambient or radiant content:

| Gate | Quests |
|---|---|
| ≥ 4 | `WERoad01` |
| ≥ 5 | `WE15`, `WE18`, `WE20`, `WE24`, `WEDLVigilOfStendarr01`, `…02`, `WEJS26`, `WEJS28`, `WERoad06`, `WICastMagic01`, `WIChangeLocation05` |
| ≥ 8 / < 8 | `WE100` (both branches), `WE34` |
| ≥ 10 | `BQ04`, `Favor109`, `WEJS14`, `WEJS15`, `WEJS20`, `WIChangeLocation09` |
| ≥ 15 | `WE31` |
| ≥ 20 | `BQ03`, `Favor157` |
| ≥ 22 | `Favor153` |
| via global | `WE13` (`LevelGateTrollCave`), `WEDL10` + `WEJS16` (`LevelGateSpriggan`), `WEJS19` + `WEJS22` (`LevelGateIceWraith`) |

> **Not one questline is level-gated.** No main quest, no Companions, College, Thieves Guild, Dark
> Brotherhood, Civil War or Daedric quest carries a player-level condition. The single hit carrying
> `Type: MainQuest` is `WIChangeLocation05`, a radiant world-interaction quest that inherits the type
> — not part of the MQ chain. `[verified]`

Skyrim gates content by **quest stage** and by **going there**, never by level. The player is free to
attempt anything from the moment Helgen ends.

### The `LevelGate*` globals

Bethesda's one systematic attempt at level-gating is a set of twelve globals, and they gate
**creature spawns in world encounters**, not quests `[verified]`:

| Global | Value | Creature's own static level (`enemy-taxonomy.md` §2.3) |
|---|---|---|
| `LevelGateSpriggan` | 8 | 8 ✓ |
| `LevelGateIceWraith` | 10 | 9 |
| `LevelGateBear` | 12 | 12 ✓ |
| `LevelGateTrollCave` | 12 | 14 |
| `LevelGateWisp` / `LevelGateWispMother` | 15 | 1 / 28 |
| `LevelGateBearCave` | 16 | 16 ✓ |
| `LevelGateTrollFrost` | 18 | 22 |
| `LevelGateBearSnow` | 20 | 20 ✓ |
| `LevelGateFalmer` | 20 | 15–38 by tier |
| `LevelGateHagraven` | 20 | 20 ✓ |
| `LevelGateGiant` | 24 | 32 |

Five match the creature's level exactly; the rest sit below it. The intent is legible: *do not throw
this creature at a player who cannot yet handle it.*

**This is a direct conflict with bone 1.** Gating a spawn on player level *is* the world scaling to
the player — just at the coarsest possible granularity. Ehlnofey has to decide explicitly whether
these twelve globals are (a) deleted, making the wilderness genuinely fixed and occasionally lethal,
or (b) kept as an acknowledged exception in service of bone 2. **This belongs in `design/` as a named
decision, not left to default.** `[verified]` for the data, the tension is a design call.

---

## 3. Geographic gating: there is none

The carriage system is the decisive fact. Five drivers — Whiterun, Solitude, Markarth, Riften,
Windhelm — offer **19 destinations** `[verified]`:

> Darkwater Crossing · Dawnstar · Dragon Bridge · Falkreath · Ivarstead · Karthwasten · Kynesgrove ·
> Markarth · Morthal · Old Hroldan · Riften · Riverwood · Rorikstead · Shor's Stone · Solitude ·
> Stonehills · Whiterun · Windhelm · Winterhold

Checking the conditions on every carriage destination topic, the **only** condition types present are
`GetGold`, `GetSitting`, `GetGlobalValue`, `GetActorValue` and `GetIsAliasRef`. `[verified]`

**There is no `GetLevel` condition, no `GetStage` condition and no discovery requirement anywhere in
the carriage system.** The fare is two globals: `CarriageCost` = **20** gold, `CarriageCostSmall` =
**50**. `[verified]`

So a character who has just walked out of Helgen can pay 20 gold and be set down outside Markarth —
capital of **the Reach, the highest-level hold in the game** (mean `MinLevel` 12.6, `regions.md` §3) —
without meeting a single condition beyond having the coin.

**This kills the radial-progression assumption.** The `r = +0.25` correlation between distance from
Helgen and dungeon level in `regions.md` §2 describes where Bethesda *placed* things, not the order in
which a player *encounters* them. Treat the radial spine as a **design aesthetic worth preserving**,
not as a mechanism that gates anything.

Fast travel compounds this, though it does require prior discovery. `[community]`

---

## 4. The main quest's own difficulty curve is non-monotonic

The MQ chain, with the `ECZN.MinLevel` of each dungeon it sends you to `[verified]`:

| Quest | Name | Dungeon | Zone MinLevel |
|---|---|---|---|
| MQ101 | Unbound | Helgen | *(no zone)* |
| MQ102 | Before the Storm | Riverwood → Whiterun | — |
| **MQ103** | **Bleak Falls Barrow** | Bleak Falls Barrow | **6, capped 20** |
| MQ104 | Dragon Rising | Western Watchtower | — |
| MQ105 | The Way of the Voice | Ustengrav | 6 (`NeverResets`) |
| MQ106 | A Blade in the Dark | Kynesgrove | — |
| MQ201 | Diplomatic Immunity | Thalmor Embassy | **2** (`NeverResets`) |
| MQ203 | Alduin's Wall | Karthspire / Sky Haven | *(no zone)* |
| **MQ205** | **Elder Knowledge** | Alftand → Blackreach | **16 → 18** |
| MQ301 | The Fallen | Dragonsreach | — |
| **MQ303** | **The World-Eater's Eyrie** | Skuldafn | **10** |
| MQ304–305 | Sovngarde / Dragonslayer | Sovngarde | *(no zone)* |

The curve runs **6 → 6 → 2 → 16 → 18 → 10**. The Thalmor Embassy, a mid-game infiltration, is the
*lowest*-levelled zone in the sequence. Skuldafn, the penultimate dungeon of the entire game, sits at
**MinLevel 10** — six levels below Alftand, which you visit earlier.

Because vanilla zones are floors with no ceiling (`overview.md` §3), this never shows: everything
scales up to the player, so the ordering is invisible. **Under Ehlnofey it becomes visible
immediately**, and Skuldafn at 10 would be a trivial anticlimax. The main-quest sequence needs an
explicit pass in `design/difficulty-map.md` — it cannot inherit vanilla's numbers.

---

## 5. The one place vanilla does gate: the opening corridor

The four capped zones in the entire base game (`dungeons.md` §2) are all on the Helgen → Riverwood →
Whiterun path `[verified]`:

| Zone | Range |
|---|---|
| `BleakFallsBarrowZone` | 6–**20** |
| `EmbershardMineZone` | 6–**10** |
| `HaltedStreamCampZone` | 6–**10** |
| `WhiteRiverWatchZone` | 6–**10** |

Bethesda capped exactly the places a new character stumbles into before they can survive them, and
nowhere else. This is the vanilla precedent for what Ehlnofey wants to do to all 280 zones — and it
is also the shape of the answer to "what protects a new player in a fixed world": **a bounded tutorial
corridor**, not a global rule.

---

## 6. DLC entry

Neither `DLC1Init` (Dawnguard) nor `DLC2Init` / `DLC2MQ01` (Dragonborn) carries a player-level
condition. `[verified]` Both are triggered by quest-stage and location conditions. Their level gates
sit, as in the base game, only on world encounters:

| DLC | Level-gated quests |
|---|---|
| Dawnguard | `DLC1WE03` ≥10 · `DLC1_WESC05` ≥10/≥20 · `DLC1WEJS05` ≥14 · `DLC1_WESC02` >15 · `DLC1WEJS06` ≥18 · `DLC1EclipseAttack1/3/6` ≥20 |
| Dragonborn | `DLC2WE04` (`LevelGateIceWraith`) · `DLC2WE09` ≥25 |

One genuine outlier: **`DLC1_BF_DunTempleQST`** (the Forgotten Vale temple) carries a banded ladder of
level conditions — `1 / <10 / ≥10 / <20 / ≥20 / <30 / ≥30 / <40 / ≥40` — the only scripted
five-band difficulty structure found anywhere in the game data. `[verified]` Worth reading before
Phase 3 designs its own band system; `[unverified]` what it actually switches.

**Solstheim has no level gate at all.** A level-1 character can board the boat at Windhelm and land in
a region whose zones run 6–40 (`regions.md` §4.3). `[verified]`

---

## 7. What this means for Ehlnofey

1. **Nothing gates the world but the player's own judgement.** No level conditions on questlines, no
   geographic barriers, 20 gold to any hold capital. In vanilla this is invisible because the world
   scales; under a fixed world it is the central design problem.
2. **Bone 2 is the load-bearing bone.** Legibility is not a nice-to-have — it is the *only* protection
   a player has. And `factions.md` §3 already established there is no faction-level lever for it, so
   the signals must be: **tileset and visual tier** (`regions.md` §3), **geography and lore**, **NPC
   dialogue and rumour**, and **explicit warnings**.
3. **The twelve `LevelGate*` globals are a bone-1 violation that already exists.** Decide them
   explicitly: delete for purity, or keep as a documented exception.
4. **The main quest needs hand-authored levels.** Its vanilla sequence is 6 → 6 → 2 → 16 → 18 → 10 and
   will read as broken the moment zones acquire ceilings.
5. **The opening corridor is the model for player protection** — a small bounded set of capped zones
   on the path the player must walk, not a global mechanism.
6. **Do not build on the radial spine as a gate.** Keep it as an aesthetic (harder types further out,
   per `regions.md` §2) but assume the player can and will arrive anywhere immediately.

## 8. Open questions

1. **What does `DLC1_BF_DunTempleQST`'s five-band ladder actually switch** — spawns, loot, or a
   script variable? It is the only banded structure in the game and may be a usable pattern.
   `[unverified]`
2. **Is there any non-quest gating** — locked doors requiring quest items, one-way descents, or
   navmesh isolation — that effectively walls off high-tier content? Not surveyed here. `[unverified]`
3. **Do map markers start visible for undiscovered locations**, and can the player fast-travel to a
   hold capital before ever visiting? Carriage makes this partly moot, but it affects how quickly the
   far holds open up. `[unverified]`
4. **What does the player's actual level curve look like** against these zones — how fast does a
   normal character reach level 20? Without that, "fixed level 24" has no calibration. This is an
   in-game measurement, not a record read. `[unverified]`
5. **Does the Civil War questline drag the player across holds** in an order that conflicts with a
   regional gradient? 47 `CivilWar` quests touch every hold. `[unverified]`
