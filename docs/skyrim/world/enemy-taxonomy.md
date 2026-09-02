---
id: "skyrim/world/enemy-taxonomy"
title: "Enemy taxonomy"
slug: "enemy-taxonomy"
section: "skyrim/world"
game: "skyrim"
kind: "world"
project: null
mod: null
tags: ["skyrim", "world-research", "vanilla", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/world/enemy-taxonomy.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: "Phase 1, document 1"
confidence: {"author": 0, "community": 4, "unverified": 7, "upstream": 0, "verified": 38}
lines: 507
content_sha256: "807d67d6e70dd0b49c306dc2df51be1bbef96de050694e5e26a34ce1ceed2e07"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Enemy taxonomy

**Phase 1, document 1.** Every hostile archetype in the base game and the three DLC, with the record
chain that owns its level and the exact vanilla scaling behaviour, cited from `reference/`.

This document does **not** assign Ehlnofey tiers — that is Phase 3 (`design/tiers.md`). What it gives
Phase 3 is the raw ladder each archetype already has, so tier assignment is a mapping exercise rather
than an invention.

Read `overview.md` first. Confidence marks: `[verified]` = read in `reference/`, `[community]` =
established modding knowledge not re-tested here, `[unverified]` = plausible, unchecked.

Method: every ladder below was produced by following `LVLN → sublist → NPC_ → Template` down to the
record that actually owns the level, honouring `TemplateFlags: Stats`. The tracer scripts are
disposable; the numbers are the deliverable.

---

## 1. How to read a ladder

Vanilla expresses "this enemy scales" in exactly one place: a level-gated `LVLN`. The NPC records
behind it carry **static** levels. `[verified]`

```
LCharBanditMelee1H (039CFC)                 ← the list a spawn point points at
  gate 1   → SubCharBandit01Melee1H  → L=1     ← six fixed bandits,
  gate 5   → SubCharBandit02Melee1H  → L=5        selected by player level
  gate 9   → SubCharBandit03Melee1H  → L=9
  gate 14  → SubCharBandit04Melee1H  → L=0  (see note)
  gate 19  → SubCharBandit05Melee1H  → L=19
  gate 25  → SubCharBandit06Melee1H  → L=25
```

**`gate N`** = the `Entries[].Data.Level` value: the player level at which this entry becomes a
candidate. **`L=n`** = the static `NPC_.Configuration.Level.Level` on whichever record owns it.

### The one flag that decides everything

`LVLN.Flags: CalculateFromAllLevelsLessThanOrEqualPlayer` `[community]`:

| Flag | Candidate set at player level P | Effect |
|---|---|---|
| **ON** | *all* entries with gate ≤ P | a camp contains a **mix** of tiers; the low tiers never stop appearing |
| **OFF** | only entries at the *highest* gate ≤ P | always the **top** tier the player has unlocked |

The record data corroborates this reading rather than proving it: the lists that must produce variety
carry the flag with **one entry per gate** (`LCharBanditMelee1H`), while the boss lists omit it and
carry **two entries per gate** (`LCharDraugrBoss` pairs 1H/2H at gates 13/21/30/40/50) — pairing being
the only way to get randomness inside a single top tier once the flag is off. `[verified]` for the
record shapes, `[community]` for the semantics. **Confirm in-game before designing on it** — the
whole meaning of "flatten a leveled list" depends on which way round this is.

Vanilla is inconsistent about the flag even within one family: `LCharBanditMelee1H`, `Melee2H`,
`Missile`, `Melee1HTank` and `Melee2HBerserk` all carry it, but `LCharBanditWizard` (01E771) has **no
`Flags:` block at all**, as do `LCharFalmerMissile`, `LCharFalmerShaman`, `LCharFalmerBoss`,
`LCharDraugrWarlockMale`, `LCharDwarvenAutomaton`, `LCharDremoraMelee`, `LCharGhostWizard`,
`LCharChaurus`, `LCharBearAll`, `LCharSabrecat`, `LCharGiant`, `LCharMudcrab`, `LCharWerewolf`,
`LCharBearPlainsForestHills`, `LCharDeer` and `LCharWarlockBossFire`. `[verified]` Ehlnofey must not
assume the flag is uniformly set.

Quantified: **97 of 527 `LVLN` have no `Flags:` block at all**, and of the 430 that do, 415 carry
`CalculateFromAllLevelsLessThanOrEqualPlayer` and 430 carry `CalculateForEachItemInCount`. On the loot
side, **553 of 3,075 `LVLI` have no flags**; 1,959 carry the calculate-from-all flag, 280 `UseAll` and
86 `SpecialLoot`. `[verified]`

### Reading the `L=0` entries

`SubCharBandit04*` resolves to `EncBandit04TemplateMelee` (01E60D), which serializes as
`Level: {MutagenObjectType: NpcLevel}` with **no** `Level:` line and a vestigial `CalcMinLevel: 14`.
Mutagen omits default-valued scalars, so that is level **0**, not 14 — a genuine vanilla bug where a
record was switched from `PcLevelMult` to `NpcLevel` and the level was never set. It affects the
1H, 2H, 1HTank and 2HBerserk tier-4 melee bandits (the Missile and Magic tier-4s are correctly
`L=14`). `[verified]` Ehlnofey should fix these to 14 regardless of what else it does.

---

## 2. Master table — scaling behaviour by archetype

`Ladder` = the player-level gates on the archetype's primary `LVLN`. `Levels` = the static levels
behind those gates. Every row `[verified]` against the cited FormKey.

### 2.1 Humanoid factions — level-gated LVLN, static NPCs

| Archetype | Primary list | Ladder (gates) | Levels | Boss list | Boss levels |
|---|---|---|---|---|---|
| **Bandit** | `LCharBanditMelee1H` 039CFC | 1 / 5 / 9 / 14 / 19 / 25 | 1 / 5 / 9 / **0** / 19 / 25 | `LCharBanditBoss` 03DF16 | 6 / 6 / 6 / 10 / 16 / 21 / 28 @ gates 1/5/9/14/19/25/29 |
| Bandit (missile) | `LCharBanditMissile` 01E770 | 1 / 5 / 9 / 14 / 19 / 25 | 1 / 5 / 9 / 14 / 19 / 25 | | |
| Bandit (wizard) | `LCharBanditWizard` 01E771 *(no flags)* | 1 / 5 / 9 / 14 / 19 / 24 | 1 / 5 / 9 / 14 / 19 / 25 | | |
| Orc (stronghold) | `LCharOrcMelee` 01E780 | 1 / 5 / 9 / 14 / 19 / 25 | reuses the **bandit** tier NPCs (`EncBandit0nMelee1HOrcM`) | | |
| **Forsworn** | `LCharForswornMelee1H` 01E792 | 1 / 6 / 14 / 24 / 34 | 1 / 6 / 14 / 24 / 34 | `LCharForswornBossMelee1H` 0442F2 | 7 / 7 / 7 / 16 / 27 / 38 / 51 @ 1/6/14/24/34/46/58 |
| Forsworn (shaman) | `LCharForswornShaman` 01E795 | 1 / 6 / 14 / 24 / 34 | 1 / 6 / 14 / 24 / 34 | `LCharForswornBossShaman` 0442FD | same as above |
| **Warlock** (Fire/Ice/Storm/Necro/Conjurer) | `LCharWarlockFire` 01E7D1 &c. | 1 / 6 / 12 / 19 / 27 / 36 / 46 | 1 / 6 / 12 / 19 / 27 / 36 / 46 | `LCharWarlockBossFire` 0E1018 *(no flags)* | 7 / 7 / 7 / 14 / 21 / 30 / 40 |
| **Thalmor** | `LCharThalmorMelee1H` 02B129 | 1 / 12 / 20 / 28 / 36 | 4 / 12 / 20 / 28 / 36 | `LCharThalmorMagicBoss` 07DCA9 | 14 / 14 / 14 / 23 / 32 / 40 / 50 |
| Thalmor (magic) | `LCharThalmorMagic` 02B128 | 1 / 12 / 20 / 28 / 36 / 44 | 4 / 12 / 20 / 28 / 36 / 44 | | |
| **Alik'r** | `LCharAlikrMelee1H` 06766F | 1 / 6 / 14 / 24 / 34 / 44 | 1 / 6 / 14 / 24 / 34 / 44 | — | |
| **Vampire** | `LCharVampire` 033973 | 1 / 6 / 12 / 20 / 28 / 38 / 48 | 1 / 6 / 12 / 20 / 28 / 38 / 48 | `LCharVampireBoss` 0339A9 | 14 / 14 / 14 / 23 / 31 / 42 / 53 |
| **Werewolf** (Silver Hand quarry) | `LCharWerewolf` 01E791 *(no flags)* | 1 / 6 / 12 / 20 / 28 / 38 | 1 / 6 / 12 / 20 / 28 / 38 | — | |
| **Penitus Oculatus** | `LCharPenitusOculatus` 07D99F | 1 / 8 / 16 / 26 / 36 / 46 | 1 / 4 / 8 / 13 / 18 / 23 | — | |
| **Ghost** (draugr-adjacent) | `LCharGhostWizard` 104B62 *(no flags)* | 1 / 5 / 9 / 14 / 19 / 24 | 1 / 5 / 9 / 14 / 19 / 25 | — | |
| **Witch** | `LCharWitchAny` 074F9D | 1 / 16 | 4 / 8 | — | |
| **Vigilant of Stendarr** | `LCharVigilantOfStendarr` 0BFB53 | **1 only** | **5** | — | |

Two rows deserve flagging:

- **Vigilants of Stendarr do not scale at all.** Every entry sits at gate 1 and resolves to level 5.
  They are the one vanilla humanoid faction that already satisfies bone 1, and they are the reason
  Vigilant camps feel trivially easy at high level. A useful precedent, not a bug to fix. `[verified]`
- **Penitus Oculatus ladder is inverted relative to its gates** — gates reach 46 but the top tier is
  only level 23. They get *proportionally weaker* as the player levels. `[verified]`

### 2.2 Draugr — the deepest ladder in the game

| List | Ladder (gates) | Levels |
|---|---|---|
| `LCharDraugrMelee1HMale` 055936 | 1 / 6 / 13 / 21 / 30 / 40 | 1 / 6 / 13 / 21 / 30 / 30 |
| `LCharDraugrMelee2HMale` 01E772 | 1 / 6 / 13 / 21 / 30 / 40 | 1 / 6 / 13 / 21 / 30 / 30 |
| `LCharDraugrMissileMale` 0A6844 | 1 / 6 / 13 / 21 / 30 / 40 | 1 / 6 / 13 / 21 / 30 / 40 |
| `LCharDraugrWarlockMale` 0BF7BB *(no flags)* | 1 / 13 / 21 | 6 / 13 / 21 |
| `LCharDraugrBoss` 042480 *(no flags)* | 1 / 6 / 13 / 21 / 30 / 40 / 50 / 60 | 7 / 7 / 15 / 24 / 34 / 45 / 50 |
| `LCharDraugrBossNoDragonPriest` 0DD9D8 | 1 / 6 / 13 / 21 / 30 | 7 / 15 / 24 / 34 / 45 |

The gate-40 "Ebony" tier on the 1H/2H melee lists resolves to a level-**30** record, not 40 — the
Ebony draugr are a *gear* upgrade at the same level, while the Missile list's gate-40 entry correctly
resolves to 40. `[verified]` Another vanilla inconsistency to normalise.

`LCharDraugrBoss` gate 60 leads to `LCharDraugr05BossWithDragonPriest`, which is how a Dragon Priest
gets attached to a top-tier crypt boss. `[verified]`

**Dragon Priests** are flat: `EncDragonPriest` (023A93) and all seven generic variants are **level
50**, and so are **all eight** named ones. Every named priest carries `Stats` in `TemplateFlags`, so
its own `Level: 50` is inert and it inherits 50 from its generic template anyway. `[verified]`

| Name | EditorID | FormKey | Template | Dungeon |
|---|---|---|---|---|
| Rahgot | `DunForelhostDragonPriestRahgot` | 035351 | 02025A | Forelhost |
| Krosis | `dunShearpointKrosisDragonPriest` | 100767 | 02025B | Shearpoint |
| Morokei | `MG07LabyrinthianDragonPriest` | 0F496C | 02025C | Labyrinthian |
| Volsung | `dunVolskyggeDragonPriest01` | 041930 | 0480B9 | Volskygge |
| Otar | `dunRagnOtar` | 03763A | 08A1C9 | Ragnvald |
| Hevnoraak | `dunValthumeHevnoraak` | 04D6E7 | 08A1C9 | Valthume |
| Nahkriin | `dunSkuldafnNahkriin` | 0F849B | 023A93 | Skuldafn |
| **Vokun** | **`Ianusu`** | 0327C2 | 023A93 | High Gate Ruins |

**Vokun's EditorID is `Ianusu`** — it contains neither "Vokun" nor "DragonPriest", and `dunRagnOtar`,
`dunSkuldafnNahkriin` and `dunValthumeHevnoraak` likewise do not contain "Priest". Searching NPC
EditorIDs for `priest` finds only four of the eight. To enumerate a named-boss set reliably, match on
the **English `Name:` string**, not the EditorID. `[verified]`

#### Dragonborn's four priests break the pattern

Solstheim's dragon priests are **not** built like Skyrim's. None of them is a level-50 record
templated on `EncDragonPriest`, and one of them is not a unique record at all. `[verified]`

| Name | EditorID | FormKey | Level | Health | Race | Class |
|---|---|---|---|---|---|---|
| **Ahzidal** | `DLC2AcolyteAhzidal` | 0248E9 | **static 60** (`Unique`) | 2000 | `DLC2AcolyteDragonPriestRace` | `EncClassDragonPriest` |
| **Dukaan** | `DLC2AcolyteDukaan` | 0248E1 | **static 60** | 2000 | `DLC2AcolyteDragonPriestRace` | `EncClassDragonPriest` |
| **Zahkriisos** | `DLC2AcolyteZahkriisos` | 0248E8 | **`PcLevelMult` ×1, [25–60]** | 1650 | `DLC2AcolyteDragonPriestRace` | `EncClassDragonPriest` |
| **Vahlok** | `DLC2SV01DragonPriestBoss` | 01CAD5 | **static 50**, `Respawn` | 1490 | `DragonPriestRace` | `EncClassDragonPriest` |

Three things worth carrying into Phase 3:

- **Zahkriisos is the only player-scaled dragon priest in the game.** His two Acolyte siblings are
  fixed at 60; he alone is `PcLevelMult`. There is no design reason visible in the records — it looks
  like an oversight, and it is exactly the kind of inconsistency Ehlnofey exists to remove. `[verified]`
- **Vahlok is not a unique NPC.** Vahlok's Tomb's boss is `DLC2SV01DragonPriestBoss`, a *generic*,
  **respawning** record templated on `EncDragonPriestFire` (02025A) with `TemplateFlags: Stats` — so
  its level 50 is inherited, not authored. His name is applied at the reference level. Consequently
  `DLC2VahloksTombLocation` (0142BA) carries `LocTypeDraugrCrypt`, **not** `LocTypeDragonPriestLair`,
  and has **no `Boss` LocationRefType at all**. Any rule keyed on "dragon priest lair" misses it.
  `[verified]`
- **Ahzidal and Dukaan at level 60 are the highest fixed-level humanoids in the game** — above every
  Skyrim priest (50) and above the top draugr boss (50). Solstheim's ceiling is genuinely higher, which
  matches its encounter-zone gradient (`dungeons.md` §3).

Only **four** Dragonborn NPCs use `EncClassDragonPriest` (the three Acolytes, plus the generic boss;
`TestDLC2Lurker` is a leftover test record). `[verified]`

#### Miraak and Harkon — the two DLC final bosses

Both are `PcLevelMult`, i.e. **scaling class D**, alongside Alduin. All three of the game's
narrative-ending bosses scale with the player. `[verified]`

| Record | FormKey | Level rule | Race | Class | CombatStyle |
|---|---|---|---|---|---|
| `DLC2Miraak` (base) | 017F7D | `PcLevelMult` ×1, **[35–200]** | `NordRace` | **`EncClassDremoraMelee`** (017008) | *(none)* |
| `DLC2MiraakMQ06` (final fight) | 01FB98 | `PcLevelMult` **×1.1**, [35–150] | `DLC2MiraakRace` | `DLC2EncClassMiraak` | `DLC2csMiraakMagic` |
| `DLC2MiraakDragon` | 023F7B | static **58**, on `DLC2EncDragon06Frost` | `DragonRace` | `EncClassDragon` | `csDragon` |
| `DLC1Harkon` (base) | 003BA7 | `PcLevelMult` **×1.2**, [10–60] | `NordRace` | `EncClassVampire` (02E00F) | `DLC1HarkonMagic` |
| `DLC1HarkonCombat` (vampire lord) | 01A93D | `PcLevelMult` **×1.4**, [10–60] | `DLC1VampireBeastRace` | `EncClassVampire` | `DLC1HarkonMagic` |

- **Miraak is classed as a Dremora.** His base record uses `EncClassDremoraMelee` — a Daedra melee
  class on a Nord — presumably because Apocrypha had no class of its own; the final-fight record
  switches to a bespoke `DLC2EncClassMiraak`. `[verified]`
- **Miraak's `CalcMaxLevel` is 200**, the highest in the game by a wide margin (Alduin 100, Harkon
  60). At `×1` that is effectively uncapped. `[verified]`
- **Harkon has two multipliers**: ×1.2 in mortal form, **×1.4** in Vampire Lord form via
  `DLC1HarkonCombat`, which templates off the base record but overrides `AIData`/`DefPackList`/
  `AttackData` only — the level rule is authored separately on each. Deleveling Harkon means editing
  **both**. `[verified]`
- **Harkon is `EncClassVampire`** — the same generic class as any dungeon vampire; his threat is
  entirely in his perks, spells and the `DLC1HarkonMagic` combat style, not in his class.

For Ehlnofey these three (Alduin ×1.2 [10–100], Miraak ×1/×1.1 [35–200], Harkon ×1.2/×1.4 [10–60])
are the clearest candidates for a **documented exception** to bone 1: they are the only enemies the
player is guaranteed to meet at the end of a questline rather than by wandering into a place. Decide
them explicitly in `design/`, not by default.

### 2.3 Creatures and animals — species substitution, not level scaling

Every creature has a **fixed static level**. What the player's level changes is *which species*
spawns. This is a categorically different mechanism from the humanoid ladders and needs a different
fix. `[verified]`

Static creature levels:

| Creature | L | | Creature | L | | Creature | L |
|---|---|---|---|---|---|---|---|
| Skeever | 1 | | Sabre Cat | 6 | | Hagraven | 20 |
| Skeleton | 1 | | Ice Wraith | 9 | | Chaurus Reaper | 20 |
| Slaughterfish | 1 | | Frostbite Spider (large) | 6 | | Frost Troll | 22 |
| Mudcrab | 1 | | Spriggan | 8 | | Wispmother | 28 |
| Deer / Elk | 1 | | Sabre Cat (snow) | 11 | | Storm Atronach | 30 |
| Wisp | 1 | | Bear | 12 | | Giant | 32 |
| Wolf | 2 | | Chaurus | 12 | | Mammoth (wild) | 38 |
| Fox | 2 | | Troll | 14 | | | |
| Horker | 3 | | Frostbite Spider (giant) | 14 | | | |
| Flame Atronach | 5 | | Frost Atronach | 16 | | | |
| Ice Wolf | 6 | | Bear (cave) | 16 | | | |
| Frostbite Spider | 1 | | Spriggan Matron | 18 | | Bear (snow) | 20 |

The substitution ladders:

| List | Ladder | Species sequence |
|---|---|---|
| `LCharFrostbiteSpider` 01E77C | 1 / 6 / 14 | Spider → Large → Giant |
| `LCharBearAll` 042266 *(no flags)* | 1 / 16 / 20 | Bear → Cave → Snow |
| `LCharBearPlainsForestHills` 01E796 *(no flags)* | 1 / 16 | Bear → Cave |
| `LCharSabrecat` 0FE2D5 *(no flags)* | 1 / 11 | Sabre Cat → Snowy |
| `LCharChaurus` 01FA27 *(no flags)* | 1 / 20 | Chaurus → Reaper |
| `LCharSpriggan` 10EC84 | 1 / 18 | Spriggan → Matron |
| `LCharAtronach` 01E77A | 1 / 20 / 30 | Flame → Frost → Storm |
| `LCharMudcrab` 02183E *(no flags)* | 1 / 5 / 10 / 15 | Medium → Large → Giant |
| `LCharCustomIceWraithFrostTroll` 106386 | 1 / 22 | Ice Wraith → Frost Troll |
| `LCharGiant` 030529 *(no flags)* | **1 only** | Giant (L=32) — **does not scale** |
| `LCharWolf` 0B83C2 | **1 only** | Wolf (L=2) — **does not scale** |
| `LCharSkeletonMeleeMixed` 02D2D4 | **1 only** | Skeleton (L=1) — **does not scale** |
| `LCharDeer` 0ABEDC / `LCharElk` 0DB2AC | **1 only** | L=1 — **do not scale** |

The **ambient wilderness lists** are the interesting case — they are long, fine-grained species
ramps rather than tier ladders:

```
LCharAnimalForestPredator (042297)
  gate 1        EncSkeever L=1, EncWolf L=2 ×4
  gate 6–10     EncFrostbiteSpiderLarge L=6
  gate 12–14    EncBear L=12
  gate 14–16    EncTroll L=14
  gate 16–35    EncBearCave L=16          ← ceiling: nothing above level 16 exists on this list

LCharAnimalMountainSnowPredator (04229D)
  gate 1        EncWolf L=2
  gate 6–9      EncWolfIce L=6
  gate 11–12    EncSabreCatSnow L=11
  gate 12–15    EncIceWraith L=9
  gate 20–22    EncBearSnow L=20
  gate 28–35    EncTrollFrost L=22        ← ceiling: 22
```

Both lists carry the flag, so at high level the whole ramp stays in play as a mix. Note the
**effective ceiling**: no matter how high the player gets, forest predators top out at a level-16
cave bear and mountain predators at a level-22 frost troll. **Skyrim's wilderness is already
delevelled above ~level 20** — the danger gradient Ehlnofey wants for the overworld largely exists,
it just stops mattering because the player outgrows it. `[verified]`

### 2.4 Falmer, Dwemer automatons, Daedra

| Archetype | List | Ladder | Levels |
|---|---|---|---|
| **Falmer** (melee) | `LCharFalmerMelee` 01E77D | 1 / 15 / 22 / 30 / 38 | 9 / 15 / 22 / 30 / 38 |
| Falmer (missile) | `LCharFalmerMissile` 01E77E *(no flags)* | 1 / 15 / 22 / 30 / 38 | 9 / 15 / 22 / 30 / 38 |
| Falmer (shaman) | `LCharFalmerShaman` 01E77F *(no flags)* | 1 / 15 / 22 / 30 / 38 | **5 / 8 / 14 / 19 / 25** |
| Falmer (boss) | `LCharFalmerBoss` 05238F *(no flags)* | 1 / 15 / 22 / 38 / 46 / 54 | 18 / 18 / 18 / 26 / 35 / 44 |
| **Dwarven** (mixed) | `LCharDwarvenAutomaton` 01E783 *(no flags)* | 1 / 16 / 20 / 22 / 26 / 32 / 38 | 6 / 12 / 16 / 16 / 24 / 30 / 36 |
| Dwarven Spider | `LCharDwarvenSpider` 10EC90 | 1 / 16 / 22 | 6 / 12 / 16 |
| Dwarven Sphere | `LCharDwarvenSphere` 10EC8F | 1 / 26 / 32 | 16 / 24 / 30 |
| Dwarven Centurion | `LCharDwarvenCenturion` 10FCE5 | 1 / 26 / 32 | **24** / 30 / 36 |
| **Dremora** | `LCharDremoraMelee` 01E79B *(no flags)* | 1 / 12 / 19 / 27 / 36 / 46 | 6 / 12 / 19 / 27 / 36 / 46 |

**Falmer shamans are badly under-levelled relative to their gates** — the tier that unlocks at player
level 38 is a level-25 NPC, while the melee Falmer beside it is level 38. `[verified]` This is a
concrete example of the "capability, not level" problem: a shaman's threat comes from its spell list,
so Bethesda kept its level low. Deleveling naively by number would make Falmer hives incoherent.

**Dwarven Centurions never appear below level 24** and the mixed list only offers one at gate 38 —
which is why Dwemer ruins feel flat early and lethal late. `[verified]`

### 2.5 Dragons

| List | Ladder | Levels |
|---|---|---|
| `LCharDragonAny` 05EACF | 1 / 18 / 27 / 36 / 45 | 10 / 20 / 30 / 40 / 50 (Fire and Frost variants at each gate) |
| `DLC2LCharDragonAny` (Dragonborn) 036135 | 1 / 18 / 27 / 36 / 45 / **55** | …/ **58** (`DLC2EncDragon06*`) |

Named dragons `[verified]`:

| Dragon | Level |
|---|---|
| **Alduin** (`AlduinBase` 08E4F1) | **`PcLevelMult` ×1.2, clamped [10–100]** — the only fully player-scaled boss in the game |
| Paarthurnax (03C57C) | static 10, `CalcMaxLevel: 100` |
| Odahviing (045920) | static 1 with `TemplateFlags: Stats` → inherits from template 0FEA9A |

Alduin's `×1.2` is worth an explicit design decision: under a strict reading of bone 1 he should be
fixed, but he is also the one enemy the player is *guaranteed* to fight last. Record the exception in
`design/` rather than letting it happen by default.

### 2.6 Guards, soldiers and world encounters — the `PcLevelMult` cluster

These are the 454 NPCs that genuinely compute their level from the player's. `[verified]`

| Archetype | List | Level rule |
|---|---|---|
| Imperial / Stormcloak **guards** | `LCharGuardImperial` 0E7B2C, `LCharGuardSons` | `PcLevelMult ×1`, clamped **[20–50]** |
| Imperial / Stormcloak **soldiers** | `LCharSoldierImperial` 01FC5B, `LCharSoldierSons` | `PcLevelMult ×0.25`, clamped **[1–50]** |
| **Hunters** | `LCharHunter` 073FC2 | `PcLevelMult ×0.5`, clamped **[5–15]** |
| **Nightingales** | `LCharNightingaleMelee` 0E0CE2 | `PcLevelMult ×1`, clamped **[15–45]** |
| `WE*` world encounters | `WEAdventurer*`, `WEThief*`, `WEAssassin*`, `WEFarmer*` SubChar lists | `PcLevelMult`, various |

Every entry on these lists sits at **gate 1** — there is no tier ladder, because the multiplier does
the work. Deleveling them means rewriting `Configuration.Level` on each NPC, not editing a list.
Guards at `[20–50]` are why city guards remain a credible threat at any level; the same clamp is why
a level-5 player finds them unkillable.

### 2.7 DLC additions

**Dawnguard** `[verified]`:

| Archetype | List | Ladder | Levels |
|---|---|---|---|
| Gargoyle | `LCharGargoyle` 017704 | 1 / 25 / 43 | 13 / 25 / 43 |
| Chaurus Hunter | `DLC1LCharChaurusHunter` 0029A2 *(no flags)* | 1 / 32 | 16 / 32 |
| Armored Troll | `DLC1LCharTrollArmored` 00D0BB | 1 / 20 | 14 / 22 |
| Dawnguard (faction) | `LCharDawnguardMelee1H` 014281 | 1 / 5 / 9 / 14 / 19 / 25 | 1 / 5 / 9 / 14 / 19 / 25 |
| Death Hound | `LCharVampireWolf` 008D75 | 1 only | 5 |
| Vampire (extended) | **overrides** `LCharVampire` 033973 | adds gate **60** → `DLC1LCharVampire07` (L=60) | |

**Dragonborn** `[verified]`:

| Archetype | List | Ladder | Levels |
|---|---|---|---|
| Riekling | `DLC2LCharRieklingMelee` 01B653 | 1 / 8 / 15 / 32 | 6 / 11 / 16 / 23 |
| Ash Spawn | `DLC2LCharAshSpawnAll` 0322BD | 1 only | **20** — does not scale |
| Cultist | `DLC2LCharCultist` 030CDC | 1 / 18 / 19 / 27 / 36 / 46 | 12 / 19 / 19 / 27 / 36 / 46 |
| Seeker | `DLC2LCharSeeker` 028E87 | 1 / 32 / 42 | 21 / 32 / 42 |
| Lurker | `DLC2LCharLurker` 01B64D *(no flags)* | 1 / 35 / 45 / 55 | 24 / 34 / 44 / 54 |
| Bandit (Solstheim) | `DLC2LCharBanditMelee1H` 01E8A9 | 1 / 5 / 9 / 14 / 19 / 25 | 1 / 5 / 9 / 14 / 19 / 25 — parallel to vanilla, **separate records** |

**Compatibility fact worth acting on:** Dawnguard *overrides* the vanilla `LCharVampire*`,
`LCharFalmer*`, `LCharChaurus`, `LCharDragonAny`, `LCharSpriggan` and `LCharVampireBoss` records —
they appear as `… - <FormID>_Skyrim.esm.yaml` files inside `reference/Base/03Dawnguard/LeveledNpcs/`.
`[verified]` Any Ehlnofey override of those records must therefore load after Dawnguard and take it as
a master, or the DLC will win. This is a direct input to the DLC-master decision in
`implementation-strategy.md`.

Dragonborn keeps a **parallel** bandit tree (`DLC2SubCharBandit01–06`) rather than overriding
vanilla's, so Solstheim bandits are a second, independent set of records to delevel. `[verified]`

---

## 3. Capability, not level

Level is not where an archetype's threat lives. Comparing the bandit melee templates `[verified]`:

| | Health | Stamina | Perks |
|---|---|---|---|
| `EncBandit01TemplateMelee` (L=1) | 35 | 70 | 1 — `crNerfDamage05` |
| `EncBandit03TemplateMelee` (L=9) | 238 | 107 | 9 — `FightingStance`, `ChampionsStance`, `crExtraDamage015`, `Bladesman30`, `HackAndSlash30`, `DeepWounds30`, `Limbsplitter30`, `CustomFit`, `TowerOfStrength` |
| `EncBandit06TemplateMelee` (L=25) | 489 | 246 | 11 — the `…60` perk ranks plus `DevastatingBlow`, `DeadlyBash`, `crExtraDamage025` |

A tier-1 bandit carries a perk that *reduces* its damage; a tier-6 carries two that increase it, on
top of 14× the health. The perk suffixes (`30`, `60`) are skill-rank gates, so the capability ladder
is a genuine third axis alongside level and gear.

**Consequence for Ehlnofey:** "set every bandit to level 12" would produce a world where every bandit
also has the tier-3 perk set, because level and perk set are welded together in the same record. A
fixed world still needs *variety* of capability — which argues for keeping the six tier records and
choosing between them **by place** instead of by player level. That is the cheapest form of the
design, and it preserves everything Bethesda already tuned. `[verified] reasoning from record data`

Combat style is a fourth axis and is **not** monotonic with tier: tiers 1 and 6 share `03BE1B` while
tier 3 uses `068849`. `[verified]` 145 CSTY records exist; mapping them is out of scope here.

---

## 4. Gear is a separate, independent level track

All six bandit melee tiers share **one** outfit, `BanditArmorMeleeShield20Outfit` (0C0197). Its four
entries are leveled item lists — `LItemBanditBoots` (037C23), `LItemBanditCuirass` (037C22),
`LItemBanditGauntlets50` (037C25), `LItemBanditShield20` (0C0196) — and every one of them carries
`CalculateFromAllLevelsLessThanOrEqualPlayer` with its own player-level gates (boots at 1/6/7/…,
shield at 1/12/13/14/15/…). `[verified]`

**So fixing an NPC's tier does not fix its equipment.** A level-1 bandit in a level-40 game still
rolls its armour off a player-gated list. Deleveling actors and deleveling gear are two separate
jobs, and the gear job is the larger one (§6 of `overview.md`: 1,959 of 3,075 LVLI are player-gated).
This belongs in `design/loot-model.md`, but it is an enemy-taxonomy fact: **the archetype tables above
describe only half of what makes an enemy dangerous.**

---

## 5. Placed-reference difficulty — vanilla's hand-tuning layer

`PlacedNpc` (ACHR) records carry an optional `LevelModifier` field. Census `[verified]`:

| `LevelModifier` | Interior cells | All cells + worldspaces | GMST multiplier |
|---|---|---|---|
| `Easy` | 1,482 | 3,520 | `fLeveledActorMultEasy` = 0.33 |
| `Medium` | 655 | 1,393 | `fLeveledActorMultMedium` = 0.67 |
| `Hard` | 258 | 554 | `fLeveledActorMultHard` = 1 |
| `VeryHard` | 129 | 218 | `fLeveledActorMultVeryHard` = 1.25 |
| *(none)* | 1,928 | 4,819 | — |
| **total `PlacedNpc`** | **4,452** | **10,504** | |

> **Do not count this field with grep.** A plain `grep -c 'LevelModifier:'` over `Cells/` returns
> 2,739 rather than the true 2,524, because **215 `PlacedObject` records also carry the field** — and
> they are all *markers* (`PatrolIdleMarker` ×137, `XMarker`, `XMarkerHeading`, `GuardMarker`,
> `WallLeanMarker`), where it does nothing. Filter by record type. `[verified]`

Example — `DA09DragonPriestRef` (029D87) in `KilkreathRuins03`:

```yaml
- MutagenObjectType: PlacedNpc
  FormKey: 029D87:Skyrim.esm
  EditorID: DA09DragonPriestRef
  Base: 09CB66:Skyrim.esm
  LevelModifier: VeryHard
```

This resolves CLAUDE.md's `[unverified]` on placed-actor difficulty: it is real, it is used on **57% of
interior placed actors (54% game-wide)**, and it multiplies against the encounter zone's level rather than the
player's. `[verified]` for the field and the census; the exact arithmetic (whether it scales the zone
level, the actor's own level, or both) is `[unverified]` and should be tested alongside the `MaxLevel`
question from `overview.md`.

If `MaxLevel` clamps a zone and `LevelModifier` tunes individual refs within it, then **vanilla
already contains the entire mechanism Ehlnofey needs** — a fixed per-place level plus per-boss
deviation — and Phase 3's job is to populate it rather than build anything.

---

## 6. Scaling-behaviour classes

The taxonomy that actually matters for Phase 3, because each class needs a different edit:

| Class | Mechanism | Archetypes | Ehlnofey's edit |
|---|---|---|---|
| **A. Tier ladder** | level-gated `LVLN` over static NPCs | Bandit, Forsworn, Warlock, Thalmor, Alik'r, Vampire, Draugr, Falmer, Dremora, Werewolf, Ghost, Penitus, Riekling, Cultist, Seeker, Lurker, Gargoyle | choose the tier **by place**; edit ~1 list per archetype-role |
| **B. Species substitution** | level-gated `LVLN` over different creature records | Bear, Sabre Cat, Spider, Chaurus, Spriggan, Atronach, Mudcrab, Dwarven, the ambient `LCharAnimal*` lists | pin the species to the region; the levels are already fixed |
| **C. Already fixed** | single-gate `LVLN` or a flat static level | Vigilant of Stendarr (5), Giant (32), Wolf (2), Skeleton (1), Deer/Elk (1), Ash Spawn (20), Dragon Priest (50), Death Hound (5) | **nothing** — verify and leave alone |
| **D. `PcLevelMult`** | multiplier + calc clamp on the NPC record | guards [20–50], soldiers ×0.25, hunters ×0.5 [5–15], Nightingales [15–45], `WE*` encounters, and **all three final bosses** — Alduin ×1.2 [10–100], Miraak ×1/×1.1 [35–200], Harkon ×1.2/×1.4 [10–60], plus Zahkriisos ×1 [25–60] | rewrite `Configuration.Level` per record (~454 in `Skyrim.esm`) |
| **E. Gear track** | player-gated `LVLI` behind a shared outfit | *all* of the above | separate pass — `design/loot-model.md` |
| **F. Placed-ref tuning** | `LevelModifier` on ACHR | 5,685 placed refs (2,524 interior) | preserve; probably extend |

Classes A and B are cheap and list-shaped. Class D is the one that needs per-record edits. Class C is
free. **The dominant cost is E, not the actors at all.**

---

## 7. Open questions for Phase 2/3

Ranked by how much they change the design:

1. **Does `ECZN.MaxLevel` clamp a class-A LVLN selection, or only class-D `PcLevelMult` actors?**
   If it clamps both, class A needs almost no edits — the zone cap does the work. `[unverified]`
2. **Exact semantics of `CalculateFromAllLevelsLessThanOrEqualPlayer`** (§1). Everything about
   "flattening a list" depends on it, and vanilla sets it inconsistently. `[community]`
3. **How does `LevelModifier` compose with the zone level?** Multiplier on the zone level, on the
   actor's level, or a tier offset? `[unverified]`
4. **Do the class-B ambient lists respect encounter zones at all**, given most of their spawns are
   exterior and ~80 of the 280 ECZN are non-dungeon? `[unverified]`
5. **Creature levels are set per race-record chain, not per place.** Can a region-specific creature
   difficulty be expressed without duplicating creature records per region? `[unverified]`
6. **Which of the vanilla inconsistencies are bugs to fix vs. intent to preserve** — tier-4 bandit
   `L=0`, the gate-40 draugr resolving to L=30, Falmer shamans capping at 25, Penitus getting
   relatively weaker with level. Fix the first two; the last two are capability-driven and should be
   left until `design/tiers.md` decides what a tier means numerically.

---

## 8. Records to cite later

The primary-source FormKeys behind this document, for `design/` to reference without re-deriving:

| FormKey | Record | Why it matters |
|---|---|---|
| `039CFC:Skyrim.esm` | `LCharBanditMelee1H` | canonical class-A ladder |
| `03DF16:Skyrim.esm` | `LCharBanditBoss` | canonical boss ladder (flag off) |
| `01E60D:Skyrim.esm` | `EncBandit04TemplateMelee` | the `L=0` vanilla bug |
| `042480:Skyrim.esm` | `LCharDraugrBoss` | deepest ladder; dragon-priest attachment |
| `01E77F:Skyrim.esm` | `LCharFalmerShaman` | capability-vs-level counterexample |
| `0BFB53:Skyrim.esm` | `LCharVigilantOfStendarr` | vanilla's only fully fixed humanoid faction |
| `042297:Skyrim.esm` | `LCharAnimalForestPredator` | canonical class-B ambient ramp |
| `0E7B2C:Skyrim.esm` | `LCharGuardImperial` | canonical class-D `PcLevelMult` cluster |
| `08E4F1:Skyrim.esm` | `AlduinBase` | the one scaled boss |
| `0C0197:Skyrim.esm` | `BanditArmorMeleeShield20Outfit` | proof the gear track is independent |
| `029D87:Skyrim.esm` | `DA09DragonPriestRef` | `LevelModifier: VeryHard` example |
| `033973:Skyrim.esm` | `LCharVampire` | overridden by Dawnguard — the master-list problem |
