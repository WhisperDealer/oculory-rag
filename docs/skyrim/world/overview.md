---
id: "skyrim/world/overview"
title: "Base game — bird's-eye overview"
slug: "overview"
section: "skyrim/world"
game: "skyrim"
kind: "world"
project: null
mod: null
tags: ["skyrim", "world-research", "vanilla", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/world/overview.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: "Phase 1, document 0"
confidence: {"author": 0, "community": 2, "unverified": 3, "upstream": 0, "verified": 27}
lines: 355
content_sha256: "40c3bb4d5411ddac3c99507a74355fc41320638553cbece02ab55d9586a7137c"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Base game — bird's-eye overview

**Phase 1, document 0.** The map before the territory: what kinds of things Skyrim's world is made
of, how many of each there are, and which record types own them. Deliberately shallow — the
per-archetype and per-dungeon tables are `enemy-taxonomy.md`, `dungeons.md` and `factions.md`.

All counts are file counts in the Spriggit decompiles under `reference/Base/`, taken 2026-07-26.
Confidence marks follow `skyrim-record-patterns.md`: `[verified]` = read in `reference/`,
`[community]` = established modding knowledge not re-tested here, `[unverified]` = plausible, unchecked.

---

## 1. Scale of the thing

Record counts in `reference/Base/01Skyrim/` (`Skyrim.esm`), the records Ehlnofey cares about. `[verified]`

| Record type | Folder | Count | Relevance |
|---|---|---|---|
| NPC_ | `Npcs/` | 5,118 | every actor, unique and generic |
| LVLN | `LeveledNpcs/` | 527 | **who spawns** — the main scaling layer |
| LVLI | `LeveledItems/` | 3,075 | **what drops** — the loot scaling layer |
| ECZN | `EncounterZones/` | 280 | per-location level floor |
| LCTN | `Locations/` | 638 | the place-graph; carries the type keywords |
| FACT | `Factions/` | 1,084 | mostly services/crime; ~60 are combat factions |
| RACE | `Races/` | 99 | 10 playable + vampire/child variants + every creature |
| CLAS | `Classes/` | 138 | 45 `EncClass*` are the combat ones |
| CSTY | `CombatStyles/` | 145 | the "capability" lever |
| PERK | `Perks/` | 375 | ditto |
| SPEL | `Spells/` | 827 | ditto |
| KYWD | `Keywords/` | 825 | includes the 52 `LocType*`/`LocSet*` |
| OTFT | `Outfits/` | 481 | gear-by-archetype, feeds off LVLI |
| QUST | `Quests/` | 1,811 | gating and progression |

DLC deltas `[verified]`:

| | Npcs | LVLN | LVLI | ECZN | LCTN | FACT |
|---|---|---|---|---|---|---|
| `Update.esm` | 19 | 3 | 8 | 2 | 9 | 4 |
| `Dawnguard.esm` | 609 | 91 | 109 | 19 | 58 | 82 |
| `HearthFires.esm` | 42 | – | 22 | – | 22 | 141 |
| `Dragonborn.esm` | 709 | 60 | 632 | 57 | 98 | 102 |

Dragonborn's 632 LVLI is the standout — Solstheim brings its own parallel loot economy, so a
deleveling pass that only touches `Skyrim.esm` leaves a large hole. `[verified]`

---

## 2. How vanilla actually scales — the four layers

This is the finding that matters most, and it is not what the CLAUDE.md summary assumed. Traced end
to end on bandits; spot-shape confirmed on draugr/Forsworn/warlocks. `[verified]`

### The chain

```
LVLN LCharBanditMelee1H (039CFC)      ← level-gated: entries at 1, 5, 9, 14, 19, 25
  └─ LVLN SubCharBandit03Melee1H (039D28)   ← unleveled: picks race/sex variant
       └─ NPC_ EncBandit01Melee1HImperialF (039CF7)   ← Level: 1  (static)
            └─ NPC_ EncBandit01TemplateMelee (039CFD) ← Level: 1  (static), TemplateFlags: Stats
                 └─ NPC_ EncBandit00Template (039CF4) ← the root
```

`reference/Base/01Skyrim/LeveledNpcs/LCharBanditMelee1H - 039CFC_Skyrim.esm.yaml`:

```yaml
Flags:
- CalculateFromAllLevelsLessThanOrEqualPlayer
- CalculateForEachItemInCount
Entries:
- Data: {Level: 1,  Reference: 039D26}   # SubCharBandit01Melee1H
- Data: {Level: 5,  Reference: 039D27}   # SubCharBandit02Melee1H
- Data: {Level: 9,  Reference: 039D28}   # …03
- Data: {Level: 14, Reference: 039D29}   # …04
- Data: {Level: 19, Reference: 039D2A}   # …05
- Data: {Level: 25, Reference: 039D2B}   # …06
```

And the tier templates carry matching **static** levels — 1 / 5 / 9 / 14 / 19 / 25 across
`EncBandit01TemplateMelee` … `EncBandit06TemplateMelee`.

**So: a generic bandit's level is not computed from the player at all. The player's level selects
which of six fixed bandits spawns.** The scaling lives in the LVLN's level gates, not in the NPC
record. `[verified]`

The `CalculateFromAllLevelsLessThanOrEqualPlayer` flag decides *how* the gates are read: with the flag
**on**, every entry gated ≤ player level is a candidate (a camp holds a mix of tiers); with it **off**,
only the highest gate ≤ player level is (always the top tier unlocked). Vanilla sets it inconsistently
even within one family. See `enemy-taxonomy.md` §1 — the semantics are `[community]` and are the second
most important thing to confirm in-game.

That is a big deal for implementation cost: deleveling generic humanoid enemies is roughly *one edit
per LVLN* (527 of them, of which far fewer are combat-relevant), not 5,118 NPC edits.

### The four layers, ranked by leverage

| # | Layer | Record | What it does | Ehlnofey's likely move |
|---|---|---|---|---|
| 1 | **Variant selection** | `LVLN` level gates (+ the `CalculateFromAllLevels…` flag) | Player level picks the tier that spawns | Flatten to one tier per place, or split per-tier lists |
| 2 | **Level floor** | `ECZN.MinLevel` | Raises actors in that location to at least N | Becomes the *authoritative* fixed level (see §3) |
| 3 | **Per-NPC level** | `NPC_.Configuration.Level` | Either `NpcLevel` (static) or `PcLevelMult` (multiplier + calc min/max) | Convert the 454 `PcLevelMult` records to static |
| 4 | **Loot** | `LVLI` + same flag | Player level picks gear tier | Same treatment as layer 1 |

Layer-3 census across `Skyrim.esm` NPCs `[verified]`:

- `NpcLevel` (static): **4,664**
- `PcLevelMult` (player-relative): **454**

The 454 are heavily concentrated in **guards and Civil War soldiers** (`EncGuardImperialM*`,
`EncGuardSons*`, `EncSoldier*`) and in **world-encounter actors** (`WEAdventurer*`, `WEThief*`,
`WEAssassin*`, `WEFarmer*`). Example — `EncGuardImperialM01MaleNordCommander` (0AA8D4):

```yaml
Level:
  MutagenObjectType: PcLevelMult
  LevelMult: 1
CalcMinLevel: 20
CalcMaxLevel: 50
```

Dungeon enemies mostly do **not** use `PcLevelMult`; they use static levels behind level-gated LVLNs.
So the two halves of the world scale by different mechanisms and need different fixes. `[verified]`

### Global knobs

`reference/Base/01Skyrim/GameSettings/` `[verified]`:

| GMST | Value | Note |
|---|---|---|
| `fLevelScalingMult` | 1 | blanket scaling multiplier |
| `iCalcLevelAdjustUp` / `…Down` | 0 / 0 | global offsets, unused by vanilla |
| `fLeveledActorMultEasy/Medium/Hard/VeryHard` | 0.33 / 0.67 / 1 / 1.25 | difficulty-slider multipliers |
| `fSpecialLootMinPCLevelMult` | 0.6 | `SpecialLoot`-flagged LVLI use PC level × 0.6 as the floor |
| `fSpecialLootMinZoneLevelMult` / `MaxZoneLevelMult` | 0.4 / 1 | …bounded by the encounter zone level |

The `fSpecialLoot*` trio is the direct wiring between **encounter zone level and loot quality** — the
"reward follows place" bone already has a vanilla hook, currently mixed 60/40 with player level. 86
LVLI carry the `SpecialLoot` flag. `[verified]`

---

## 3. Encounter zones — the biggest surprise

280 ECZN records. Field census across all of them `[verified]`:

| Field | Present in |
|---|---|
| `MinLevel` | 278 / 280 |
| `MaxLevel` | **5 / 280** |
| `Flags` | 62 (61 × `NeverResets`, 1 × `MatchPcBelowMinimumLevel`, 1 × `DisableCombatBoundary`) |
| `Location` | 270 |
| `Rank` | 6 (all `255` = none) |
| `Owner` | 1 |

`MinLevel` distribution — the whole vanilla difficulty gradient, in eleven values:

| MinLevel | Zones | | MinLevel | Zones |
|---|---|---|---|---|
| 1 | 2 | | 12 | 12 |
| 2 | 36 | | 14 | 19 |
| 5 | 7 | | 16 | 6 |
| **6** | **129** | | 18 | 15 |
| 8 | 38 | | 24 | 9 |
| 10 | 5 | | | |

**Vanilla encounter zones are a floor and nothing else.** 129 of 280 sit at the same value (6), and
only five zones have any ceiling at all. A player at level 50 walking into a MinLevel-6 zone meets
level-50 content, because nothing caps it.

Examples `[verified]`:

```yaml
# BleakFallsBarrowZone - 038AB1  (one of the 5 with a cap)
Location: 018EE9:Skyrim.esm    # BleakFallsBarrowLocation
MinLevel: 6
MaxLevel: 20

# AlftandZone - 03EBE6  (typical — no cap)
Location: 018EE1:Skyrim.esm
MinLevel: 16
```

For Ehlnofey this is close to ideal: the record type that should carry a fixed per-place level
already exists, is already wired to 270 locations, and is 95% unused. **Setting `MaxLevel` on all 280
zones is a ~280-record edit that delivers the first bone almost by itself.** That makes ECZN the
cheapest high-leverage target in the game and it should be Phase 3's first proposal. `[verified]`
Whether `MaxLevel` alone actually clamps a `CalculateFromAllLevelsLessThanOrEqualPlayer` LVLN pick,
or only clamps `PcLevelMult` actors, is `[unverified]` and is the single most important thing to test.

---

## 4. Places — what kinds of dungeon exist

Skyrim's place-graph is `LCTN` records tagged with `LocType*` / `LocSet*` keywords. `LocSet*` is the
*tileset* (what it looks like), `LocType*` is the *kind* (what's in it). Census by counting
Locations referencing each keyword `[verified]`:

> **Scope: `Skyrim.esm` only.** The DLC do not extend this cleanly — Dawnguard's new-world locations
> (Soul Cairn, Forgotten Vale, Darkfall, Castle Volkihar) and *all* of Apocrypha carry **no keywords
> at all**, so they appear in no row below. Dragonborn adds 38 tagged dungeons and a tenth
> `LocTypeHold`. See `regions.md` §4.

**Hostile place types** — this is effectively the dungeon list:

| Type | Count | | Type | Count |
|---|---|---|---|---|
| LocTypeDungeon | 202 | | LocTypeDragonLair | 10 |
| LocTypeClearable | 199 | | LocTypeForswornCamp | 9 |
| LocTypeBanditCamp | 31 | | LocTypeDwarvenAutomatons | 9 |
| LocTypeDraugrCrypt | 22 | | LocTypeVampireLair | 8 |
| LocTypeMine | 18 | | LocTypeSprigganGrove | 8 |
| LocTypeWarlockLair | 18 | | LocTypeDragonPriestLair | 8 |
| LocTypeMilitaryFort | 17 | | LocTypeShipwreck | 7 |
| LocTypeAnimalDen | 17 | | LocTypeCemetery | 6 |
| LocTypeMilitaryCamp | 16 | | LocTypeOrcStronghold | 4 |
| LocTypeFalmerHive | 14 | | LocTypeWerewolfLair | 2 |
| LocTypeHagravenNest | 13 | | | |
| LocTypeGiantCamp | 12 | | | |

**Tilesets:** `LocSetCave` 63, `LocSetNordicRuin` 37, `LocSetMilitaryCamp` 16, `LocSetCaveIce` 15,
`LocSetDwarvenRuin` 10, `LocSetMilitaryFort` 8, `LocSetOutdoor` 0.

**Civilised place types:** `LocTypeDwelling` 233, `LocTypeHouse` 117, `LocTypeHabitation` 50,
`LocTypeStore` 27, `LocTypeSettlement` 27, `LocTypeInn` 20, `LocTypeFarm` 17, `LocTypeTown` 12,
`LocTypeGuild` 11, `LocTypeCastle` 10, `LocTypeTemple` 10, `LocTypeHold` 9, `LocTypeCity` 5.

The working number for "dungeons Ehlnofey must assign a tier to" is **~200** (`LocTypeDungeon`), and
`LocTypeClearable` (199) is almost the same set — clearable is the good proxy for "has a boss and a
reward". Against 280 encounter zones, that's roughly one zone per dungeon plus ~80 for exteriors and
special cases. `[verified]`

**Geography:** 9 holds (`LocTypeHold` → Eastmarch, Falkreath, Haafingar, Hjaalmarch, Pale, Reach,
Rift, Whiterun, Winterhold), inside the `Tamriel` worldspace (`00003C`), plus ~90 small interior
worldspaces (Blackreach, Alftand, Labyrinthian, Skuldafn, the city worlds…). Note that `REGN` records
(317 of them) are **landscape and audio regions**, not difficulty regions — names like
`AlexTundraSnow07`, `AudioIntDungeonCave01`. They are not a lever. `[verified]`

---

## 5. Who lives there — enemy archetypes

Generic hostiles are the `Enc*` NPC family. Census by prefix over `Skyrim.esm` `[verified]`:

| Family | NPC records | Notes |
|---|---|---|
| Bandit | 315 | 6 tiers × role × race × sex — the biggest family by far |
| Draugr | 292 | the dungeon backbone |
| Forsworn | 166 | Reach-locked |
| Warlock | 66 + 360 elemental variants (`Fire/Ice/Storm/Necro/Atro`) | |
| Vampire | 72 | plus Dawnguard's 609 NPCs |
| Alik'r | 61 | Redguard mercenaries, exterior |
| Thalmor | 58 | |
| Vigilant of Stendarr | 37 | |
| Falmer | 36 | |
| Dragon | 19 (+2 snow) | |
| Penitus Oculatus | 13 | |
| Werewolf | 11 | Silver Hand-adjacent |
| Guards / CW soldiers | 40 | the `PcLevelMult` cluster |
| Skeleton | 16 | incl. `SkeletonNecro` |
| Frostbite Spider | 10 | |
| Witch | 30 (elemental variants) | |
| Dragon Priest | 8 | |
| Dremora | 18 | |
| Dwarven automatons | 14 (Centurion 6, Spider 4, Sphere 4) | |
| Hagraven, Giant, Sabre Cat, Troll, Ice Wraith, Mammoth, Wolf, Bear, Hunter, Nightingale, Orc Hunter | 2–6 each | |

**Combat classes** — 45 of the 138 CLAS records are `EncClass*`, and they are the clean archetype
axis. Roles repeat as `Melee` / `Missile` / `Wizard`(or `Shaman`/`Magic`) across factions:
Bandit, Forsworn, Thalmor, Alik'r, Draugr, Falmer, Dremora, Dwarven (Centurion/Sphere/Spider),
Vampire, Werewolf (+Mage/+Boss), Atronach (Flame/Frost/Storm), Dragon, DragonPriest, Giant,
Hagraven, Chaurus, FrostbiteSpider, IceWraith, Horker, Mammoth, MudCrab, Bear, AnimalPredator,
AnimalPrey, PenitusOculatus, Horse. `[verified]`

The other 93 classes are non-combat: 45 `Trainer*`, 7 `Vendor*`, plus Bard/Beggar/Citizen/Farmer/
Miner/Lumberjack/Priest/Prisoner/Child and the 12 generic `Combat*` classes used by unique NPCs
(CombatWarrior1H, CombatMageDestruction, CombatNightblade, …). `[verified]`

**Races** — 99 RACE records: 10 playable (Nord, Imperial, Breton, Redguard, Dark/High/Wood Elf, Orc,
Khajiit, Argonian) each with a `…Vampire` variant and four with a `…Child` variant; the rest are
creatures — Draugr (+`DraugrMagic`), Falmer, Chaurus (+Reaper), Dwarven (Centurion/Sphere/Spider),
Dragon (+Alduin, +Undead), DragonPriest, Dremora, Atronach ×3, Giant, Mammoth, Hagraven, Spriggan
(+Matron/Swarm), Troll (+Frost), Bear ×3, SabreCat ×2, Wolf, Skeever ×2, Frostbite Spider ×3,
Horker, Slaughterfish, Mudcrab, Ice Wraith, Wisp/WispShade/Witchlight, Werewolf, Skeleton ×3, plus
domestic and prey animals. `[verified]`

Race matters to Ehlnofey mainly as the **creature identity** axis: creature difficulty is set on the
race's own NPC/LVLN chain rather than on any hold or faction, so creatures need a separate tiering
rule from humanoids. `[unverified]` — needs the same trace §2 did for bandits.

**Factions** — 1,084 FACT, but the great majority are bookkeeping: 135 `Services*`, 48 `Job*`,
~200 town/hold-specific, 39 `Town*`, 17 `Crime*`. The combat-relevant set is roughly 60:
Bandit, Forsworn, Falmer, Draugr, Vampire, Dragon, DragonPriest, Thalmor, Dremora/Daedra,
Warlock/Necromancer, Silver Hand, Werewolf, Giant, Hagraven, Spriggan, Skeleton, Chaurus, Spider,
DwarvenAutomaton, IceWraith, Wisp, Troll, Bear, Wolf, SabreCat, Predator/Prey/Creature, plus
per-dungeon `dun*` factions (52) that mostly exist for scripted allegiance, not difficulty.
`[verified]`

---

## 6. Loot — what the LVLI layer looks like

3,075 LVLI in `Skyrim.esm`. Flag census `[verified]`:

- `CalculateFromAllLevelsLessThanOrEqualPlayer`: 1,959
- `CalculateForEachItemInCount`: 2,174
- `UseAll`: 280
- `SpecialLoot`: 86

By prefix: `LItemEnch*` 360 (enchanted gear by tier — the main power curve), `LItemPotion` 89,
`LItemArmor` 81, `LItemWeapon` 64, `LItemPoison` 64, `LItemFood` 62, `LItemSpell` 59, `LItemStaff` 38,
plus faction hoards `LItemBandit` 38, `LItemSoldier` 37, `LItemDraugr` 33, `LItemForsworn` 22,
`LItemVampire` 20, `LItemOrc` 14, `LItemWerewolf` 10. Creature drops are `DeathItem*` LVLI hung off
the NPC's `DeathItem` field. `[verified]`

Same story as actors: **1,959 of 3,075 lists gate on player level**, so the loot side is the larger
of the two edit surfaces and `LItemEnch*` is where the "reward follows place" bone will be won or lost.

---

## 7. What this implies for the phase plan

Not decisions — observations to carry into `enemy-taxonomy.md`, `dungeons.md` and Phase 3.

1. **ECZN is the cheapest big win.** 280 records, already location-wired, `MaxLevel` almost entirely
   unused. Confirm in-game that `MaxLevel` clamps LVLN selection before building a design on it.
2. **The edit surface is smaller than CLAUDE.md feared.** The scaling lives in ~500 LVLN + ~2,000
   LVLI + 280 ECZN + 454 `PcLevelMult` NPCs, not in 5,118 NPC records. That is order 3,000 records,
   not tens of thousands — which materially improves option A (plugin overrides) versus the working
   hybrid recommendation. Revisit in `implementation-strategy.md`.
3. **Two different scaling mechanisms** — dungeon enemies via level-gated LVLN, guards/soldiers/world
   encounters via `PcLevelMult` — need two different fixes.
4. **Solstheim is a second economy.** 632 Dragonborn LVLI. Decide DLC scope early; it changes the
   master list.
5. **The tier ladder already exists in vanilla**: 1 / 5 / 9 / 14 / 19 / 25 is the repeated LVLN gate
   spacing. `design/tiers.md` should start from that spacing rather than invent one, so that a fixed
   assignment maps cleanly onto the six variant records that already exist per archetype.
6. **`LocTypeClearable` (199) is the natural unit of assignment** for `difficulty-map.md` — it is
   almost exactly the set of places with a boss and a reward.

---

## 8. Reading the YAML — gotchas found while writing this

- **Mutagen omits default-valued scalars.** `EncBandit04TemplateMelee` (01E60D) serializes as
  `Level: {MutagenObjectType: NpcLevel}` with no `Level:` value — that is level **0**, not "unset",
  and it still carries a vestigial `CalcMinLevel: 14`. An absent field means the default, so never
  read absence as "not configured". `[verified]`
- **The union field for NPC level is `Configuration.Level`,** discriminated by `MutagenObjectType`:
  `NpcLevel` (with `Level:`) or `PcLevelMult` (with `LevelMult:`, plus sibling `CalcMinLevel` /
  `CalcMaxLevel` on `Configuration`). Those are the confirmed Spriggit field names. `[verified]`
- **`TemplateFlags` decides what the visible NPC actually owns.** `EncBandit01Melee1HImperialF` lists
  `Stats` among its template flags, so its own `Level: 1` is inert — the template's value wins. Always
  read `TemplateFlags` before believing a stat on an NPC record. `[verified]`
- **Repo-wide `grep -rl` over `reference/` times out** (>2 min). The decompiles are large; match on
  *filenames* instead — Spriggit names every file `<EditorID> - <FormID>_<master>.yaml`, so
  `ls Npcs | grep 039D26` resolves a FormKey instantly. `[verified]`
