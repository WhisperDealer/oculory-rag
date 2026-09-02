---
id: "skyrim/world/unique-enemies"
title: "Unique enemies"
slug: "unique-enemies"
section: "skyrim/world"
game: "skyrim"
kind: "world"
project: null
mod: null
tags: ["skyrim", "world-research", "vanilla", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/world/unique-enemies.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 4, "unverified": 4, "upstream": 0, "verified": 11}
lines: 335
content_sha256: "893282abeab4140b264e0c1e53a47aeff671d697c8d73c8ffa4c2f58d3010c07"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Unique enemies

**Phase 1, supplementary.** Every named boss and every unique enemy race in `Skyrim.esm`,
`Dawnguard.esm` and `Dragonborn.esm`, with the record that actually owns its level.

`enemy-taxonomy.md` covers the *generic* archetypes — the leveled ladders that produce most of the
world's hostiles. This document covers the other end: the hand-placed, named and one-off enemies that
a deleveling pass has to treat individually because no list governs them.

Confidence marks: `[verified]` = read in `reference/`, `[community]` = established modding knowledge
not re-tested here, `[unverified]` = plausible, unchecked.

---

## 1. Definition and method

An NPC is treated as a **unique enemy** here if it is hostile and meets at least one of:

- **U** — carries the `Unique` flag in `Configuration.Flags`
- **B** — is the hand-authored `Boss` of a dungeon (the `LocationRefType: Boss` target, and not a
  generic `Lvl*` / `Enc*` wrapper)
- **R** — uses a **race** carried by ≤2 NPC records in its plugin

Levels were resolved by walking the full chain — `NPC_ → Template (NPC_) → Template (LVLN)` — honouring
`TemplateFlags: Stats` at every hop. **This matters enormously**, and §2 explains why.

> **DLC display names are not in the decompile.** As recorded in CLAUDE.md, `Dawnguard.esm` and
> `Dragonborn.esm` serialize `Name:` with no `Values:` block — the strings live in external
> `.STRINGS` files. DLC entries below are therefore identified by **EditorID**, which is
> unambiguous. Where a well-known display name is given for a DLC record it is marked `[community]`.
> `Skyrim.esm` names *do* come through and are `[verified]`.

---

## 2. The headline: most "unique" bosses are not unique records

Resolving the full template chain splits Skyrim's named bosses three ways, and the largest group is
the surprising one. `[verified]`

### 2.1 Named, but fully leveled — the name is the only unique thing

These carry a proper name and a hand-placed reference, but `TemplateFlags: Stats` sends their entire
stat block down a `Lvl*` wrapper into a **leveled NPC list**. They have **no fixed level at all** and
scale exactly like the generic mob they are drawn from.

| Boss | Resolves to | Effective ladder (`enemy-taxonomy.md`) |
|---|---|---|
| **Jyrik Gauldurson** | `LCharDraugrWarlockMale` | 6 / 13 / 21 |
| **Sigdis Gauldurson** | `LCharDraugrMissileMale` | 1 / 6 / 13 / 21 / 30 / 40 |
| **Red Eagle** | `LCharDraugrBoss` | 7 / 15 / 24 / 34 / 45 / 50 |
| **Curalmil** | `LCharDraugrBoss` | as above |
| **Kvenel the Tongue** (`DunVolunruudBoss`) | `LCharDraugrMeleeHelmet1HMale` | draugr ladder |
| **Arondil** | `LCharWarlockNecroBossMaleElfHaughty` | warlock-boss ladder |
| **Vals Veran** | `LCharWarlockNecroBossMaleCondescending` | warlock-boss ladder |
| **Sild the Warlock** | `LCharWarlockBossFire` | 7 / 7 / 7 / 14 / 21 / 30 / 40 |
| **Kornalus** | `LCharWarlockBossStormMaleElfHaughy` *(sic)* | warlock-boss ladder |
| **Malkoran** (`DA03Wizard`) | `LCharWarlockBossConjurer` | warlock-boss ladder |
| **Ghunzul** | `LCharBanditBossOrcM` | bandit-boss ladder |
| **Captain Hargar** | `LCharBanditMelee2HBerserk` | 1 / 5 / 9 / 0 / 19 / 25 |
| **Sinding** | `LCharWerewolfBoss` | werewolf ladder |
| **Movarth** | `LCharVampireBoss` | 14 / 14 / 14 / 23 / 31 / 42 / 53 |
| **Northwatch Interrogator** | `LCharThalmorMagicBoss` | 14 / 23 / 32 / 40 / 50 |
| Traitor's Post boss | `LCharBanditBossEvenTonedM` | bandit-boss ladder |
| Lost Knife boss | `LCharBanditMelee2H` | bandit ladder |
| Cragslane "Butcher" | `LCharBanditMelee2HBerserk` | bandit ladder |
| Southfringe boss | `LCharWarlockNecromancer` | 1 / 6 / 12 / 19 / 27 / 36 / 46 |
| Talking Stone giant | `LCharGiant` | fixed 32 |
| Bloodlet Throne boss | `LCharVampireBoss` | vampire-boss ladder |

**This is the single most important finding in this document.** Under vanilla it is invisible —
everything scales, so a "named boss" feels bespoke. Under Ehlnofey, whatever you do to
`LCharDraugrWarlockMale` you also do to Jyrik Gauldurson. Named bosses are **not** automatically
protected from a leveled-list edit, and conversely you cannot hand-tune one without either
(a) retargeting its wrapper's `Template`, or (b) giving it a real static level.

Option (a) is the cheap lever already identified in `dungeons.md` §1 — retarget the wrapper, get a
hand-set boss, touch no NPC record.

### 2.2 Genuinely static

| Boss | Level | Notes |
|---|---|---|
| **Vokun** (`Ianusu`), **Otar the Mad**, **Hevnoraak**, **Nahkriin**, **Rahgot**, **Krosis**, **Volsung**, **Morokei** | **50** | all eight dragon priests — §4 |
| **Vulthuryol** | 50 | the Blackreach dragon |
| **Elenwen** | 30 | Thalmor Embassy |
| **Malkoran's Shade** | 26 | |
| **Skeletal Dragon** (Labyrinthian) | 20 | on `UndeadDragonRace` |
| **Drascua**, **Moira**, **Melka** | 20 | the three named hagravens, all at the hagraven base level |
| **Kyr** (Frostmere Crypt) | **1** | genuinely level 1; relies entirely on the zone floor |
| **Emperor Titus Mede II** | **1** | a scripted assassination target, not a fight |

### 2.3 Player-scaled (`PcLevelMult`)

| Boss | Rule |
|---|---|
| **Alduin** | ×1.2 [10–100] |
| **Mercer Frey** | ×1.2 [10–50] |
| **Lu'ah Al-Skaven** | ×1 [8–50] |
| **Ancano** | ×1 [15–50] |
| **Rulindil** | ×1 [8–40] |
| **Linwe** | ×1 [10–50] |
| **Astrid** | ×1 [5–…] |
| **Queen Potema** | ×1 |
| **Potema's Remains** | ×1 [7–50] |

Every questline's final antagonist is in this group. That is consistent with
`enemy-taxonomy.md` §2.6: the enemies the player is *guaranteed* to meet are the ones Bethesda scaled.

---

## 3. Named dragons — mostly not records at all

Only **five** dragons in `Skyrim.esm` exist as their own named NPC records `[verified]`:

| Record | Name | Level |
|---|---|---|
| `AlduinBase` | Alduin | `PcLevelMult` ×1.2 [10–100] |
| `BlackreachDragon` | Vulthuryol | static 50 |
| `Paarthurnax` | Paarthurnax | static 10 |
| `Odahviing` | Odahviing | static 1 (templated) |
| `dunLabyrinthianUndeadDragon` | Skeletal Dragon | static 20 |

**Mirmulnir, Sahloknir, Vuljotnaak, Nahagliiv, Viinturuth, Krosulhah, Naaslaarum and Voslaarum have no
NPC record.** They are generic `EncDragon0n` actors whose names are applied at the *reference* level.
`[verified]` — searching every NPC record's English `Name:` for those strings returns nothing.

This is the same pattern as **Vahlok** in Dragonborn (`enemy-taxonomy.md` §2.2), and it means a rule
keyed on "named dragons" finds five, not thirteen. The generic dragon ladder is what actually governs
them: `LCharDragonAny` at gates 1/18/27/36/45 → levels 10/20/30/40/50.

---

## 4. The eight dragon priests

All on `DragonPriestRace` (0131EF), all **static level 50**, all inheriting via `TemplateFlags: Stats`
from a generic `EncDragonPriestFire/Frost/Shock` template. `[verified]`

| Name | EditorID | Dungeon |
|---|---|---|
| Rahgot | `DunForelhostDragonPriestRahgot` | Forelhost |
| Krosis | `dunShearpointKrosisDragonPriest` | Shearpoint |
| Morokei | `MG07LabyrinthianDragonPriest` | Labyrinthian |
| Volsung | `dunVolskyggeDragonPriest01` | Volskygge |
| Otar the Mad | `dunRagnOtar` | Ragnvald |
| Hevnoraak | `dunValthumeHevnoraak` | Valthume |
| Nahkriin | `dunSkuldafnNahkriin` | Skuldafn |
| **Vokun** | **`Ianusu`** | High Gate Ruins |

Only four have "Priest" in the EditorID, and Vokun's is `Ianusu` — enumerate this set by display
**name**, never by EditorID. `[verified]`

The DLC priests break the pattern entirely — Ahzidal and Dukaan at **60**, Zahkriisos on
`PcLevelMult`, Vahlok a generic respawning record. See `enemy-taxonomy.md` §2.2.

---

## 5. Unique enemy races — base game

Races carried by ≤2 NPC records, filtered to hostiles `[verified]`:

| Race | Enemy | Level |
|---|---|---|
| `ChaurusReaperRace` | Chaurus Reaper | 20 |
| `ChaurusRace` | Chaurus | 12 |
| `SprigganMatronRace` | Spriggan Matron | 18 |
| `SprigganSwarmRace` | Spriggan Swarm | 1 |
| `WispRace` | Wisp | 1 |
| `WispShadeRace` | Shade | 5 |
| `WitchlightRace` | Witchlight | — |
| `UndeadDragonRace` | Skeletal Dragon | 20 |
| `SkeletonNecroPriestRace` | *(necro priest skeleton)* | — |
| `SlaughterfishRace` | Slaughterfish | 1 |
| `SkeeverWhiteRace` | White Skeever | — |
| `C00GiantOutsideWhiterunRace` | the Companions-intro giant | `PcLevelMult` ×1 [10–…] |
| `MG07DogRace` | Spectral Warhound | `PcLevelMult` ×0.25 [5–30] |
| `DA03BarbasDogRace` | Barbas | *(not hostile)* |
| `NordRaceAstrid` | Astrid | `PcLevelMult` ×1 |
| `WerewolfBeastRace` | werewolves | 1 → 38 by tier |

`InvisibleRace` and `ManakinRace` are technical (invisible actors, the "Ghost Axe", mannequins), not
enemies.

---

## 6. Dawnguard

### 6.1 Named uniques

| EditorID | Level rule | Notes |
|---|---|---|
| `DLC01SoulCairnReaper` | **`PcLevelMult` ×1.5 [10–100]** | the steepest multiplier in the game |
| `DLC1AlthadanVyrthur` | ×1.2 [15–75] | *Arch-Curate Vyrthur* `[community]` |
| `DLC1Harkon` | ×1.2 [10–60] | mortal form |
| `DLC1HarkonCombat` / `…Magic` / `…Melee` | **×1.4 [10–60]** | Vampire Lord form — a *separate* level rule; deleveling Harkon means editing both |
| `DLC1Durnehviir` | ×1 [10–70] | on `DLC1UndeadDragonRace` |
| `DLC01SoulCairnKeeper2H` | ×1 [10–80] | |
| `DLC01SoulCairnKeeperBowArrow` / `…Shield` | ×1.2 [10–80] | |
| `DLC1LD_Forgemaster03` | ×1 [36–60] | Aetherium Forge |
| `DLC1Orthjolf`, `DLC1Vingalmo`, `DLC1Malkus`, `DLC1Namasur`, `DLC1Ronthil` | ×1 | Volkihar court |

### 6.2 New enemy races

| Race | NPCs and levels |
|---|---|
| `DLC1GargoyleRace` | Gargoyle 25 |
| `DLC1GargoyleVariantGreenRace` | Gargoyle (small) 13 |
| `DLC1GargoyleVariantBossRace` | **Gargoyle Sentinel 43** |
| `DLC1ChaurusHunterRace` | Fledgling 16 · Hunter 32 · Ranged 32 |
| `DLC1TrollRaceArmored` / `…FrostRaceArmored` | Armored Troll 14 · Armored Frost Troll 22 |
| `SprigganEarthMotherRace` | Spriggan Earth Mother 30 |
| `DLC1UndeadDragonRace` | Durnehviir ×1 [10–70] · summon 20 |
| `DLC1DeathHoundRace` | Death Hound 5 |
| `DLC1VampireBeastRace` | Harkon's Vampire Lord form ×1.4 |
| `DLC1SoulCairnKeeperRace` | the three Keepers, ×1–1.2 [10–80] |
| `DLC1BlackSkeletonRace` | Boneman |
| `DLC1SoulCairnSkeletonArmorRace` | Wrathman (summon 30) |
| `DLC1SoulCairnSkeletonNecroRace` | Mistman (summon 13) |
| `DLC1SoulCairnSoulWispRace` | Soul Wisp 1 |
| `DLC1LD_ForgemasterRace` | Forgemaster 24 / 30 / ×1 [36–60] |
| `FalmerFrozenVampRace` | frozen Falmer, **banded 1 / 10 / 20 / 30 / 40** |
| `DLC1_BF_ChaurusRace` | frozen chaurus, **banded 10 / 20 / 30 / 40 / 50** |
| `DLC1SabreCatGlowRace` | Vale Sabre Cat 6 |
| `DLC1GlowingDeerRace` | Vale Deer 1 |
| *not enemies* | `SnowElfRace`, `DLC1HuskyBareRace`, `DLC1NordRace` |

Note the **`_BF_` (Boneyard/Forgotten Vale) records use explicit 10-level bands** — the same
five-band structure as `DLC1_BF_DunTempleQST` in `progression.md` §6. It is the only place in the
game data where a fixed ladder in round numbers was authored deliberately, and it is worth reading
before Phase 3 designs its tiers. `[verified]`

`DLC1FrostGiant` — static **50** — is the strongest non-boss creature in Dawnguard.

---

## 7. Dragonborn

### 7.1 Named uniques

| EditorID | Level rule | Notes |
|---|---|---|
| **`DLC2dunKarstaag`** | **static 90** | **the highest-level NPC in the entire game** |
| **`DLC2EbonyWarrior`** | **static 80** | highest-level *humanoid* |
| `DLC2AcolyteAhzidal` | static 60 | |
| `DLC2AcolyteDukaan` | static 60 | |
| `DLC2AcolyteZahkriisos` | `PcLevelMult` ×1 [25–60] | the only scaled dragon priest |
| `DLC2SV01DragonPriestBoss` | static 50 | Vahlok — a *generic respawning* record |
| `DLC2MiraakDragon` | static 58 | |
| `DLC2Miraak` | ×1 **[35–200]** | highest `CalcMaxLevel` in the game |
| `DLC2MiraakMQ06` | ×1.1 [35–150] | final-fight record |
| `DLC2dunHaknir` | ×1.25 [40–75] | *Haknir Death-Brand* `[community]` |
| `DLC2GeneralCarius` | ×1.5 [25–…] | Fort Frostmoth |
| `DLC2Ildari` | ×1 [13–70] | |
| `DLC2Mogrul` | static 30 | |
| `dlc2DBAncientDragonborn` | static 25 | |

### 7.2 New enemy races

| Race | NPCs and levels |
|---|---|
| `DLC2LurkerRace` | **Lurker 24 / 34 / 44 / 54** |
| `DLC2SeekerRace` | **Seeker 21 / 32 / 42** |
| `DLC2AshSpawnRace` | Ash Spawn 20 / 30 / 40 |
| `DLC2RieklingRace` | Riekling 6 / 11 / 16 / 23 |
| `DLC2MountedRieklingRace` | Mounted Riekling 20 / 25 / 32 / 40 |
| `DLC2NetchRace` | Bull Netch 36 · **Betty Netch 40** |
| `DLC2NetchCalfRace` | Netch Calf 25 |
| `DLC2WerebearBeastRace` | Werebear 25 |
| `DLC2HulkingDraugrRace` | Hulking Draugr 26 |
| `DLC2AshHopperRace` | Ash Hopper 4 |
| `dlc2AshGuardianRace` | Ash Guardian 30 |
| `DLC2DwarvenBallistaRace` | Dwarven Ballista 20 / 28 / 33 |
| `DLC2SprigganBurntRace` | Burnt Spriggan 28 |
| `DLC2GhostFrostGiantRace` | **Karstaag 90** · Frost Giant 32 |
| `DLC2AcolyteDragonPriestRace` | the three Acolytes |
| `DLC2MiraakRace` | Miraak (final fight) |
| `dlc2SpectralDragonRace` | Fire Wyrm 11 · Spectral Dragon 9 |
| `DLC2dunKarstaagIceWraithRace` | Karstaag's ice wraiths 9 |
| `DLC2ExpSpiderBaseRace` | the albino/elemental spiders, 5–12 |

---

## 8. The level extremes

Highest fixed levels in the game, all sources `[verified]`:

| Level | Enemy |
|---|---|
| **90** | Karstaag (`DLC2dunKarstaag`) |
| **80** | Ebony Warrior (`DLC2EbonyWarrior`) |
| 60 | Ahzidal, Dukaan |
| 58 | Miraak's dragon |
| 54 | Lurker (tier 4) |
| 50 | all 8 dragon priests · Vulthuryol · Dawnguard Frost Giant · top draugr boss |
| 43 | Gargoyle Sentinel |
| 42 | Seeker (tier 3) |
| 40 | Ash Spawn (tier 3) · Betty Netch · Mounted Riekling (tier 4) |

Highest `CalcMaxLevel` on a `PcLevelMult` enemy: **Miraak at 200**, then Alduin at 100 and the Soul
Cairn Reaper at 100 (×1.5).

Note that **Skyrim's own ceiling is 50** — everything above it is DLC. A tier ladder that stops at 50
covers the base game entirely; Solstheim and the Soul Cairn need the range extended.

---

## 9. What this means for Ehlnofey

1. **"Named boss" is not a category the data supports.** 21 of Skyrim's named bosses are leveled
   wrappers with a name attached; only ~13 have a genuine static level. Any rule that assumes named
   bosses are hand-tuned is wrong.
2. **The wrapper retarget is the lever.** Because these bosses inherit through
   `Lvl* → LVLN`, changing the wrapper's `Template` per boss gives hand-set difficulty without
   editing a single NPC record — the same lever `dungeons.md` §1 identified for dungeon bosses.
3. **Two bosses are literally level 1** — Kyr and Titus Mede II. Both survive only because vanilla
   zones are floors. Under a capped world they need explicit levels or they become jokes.
4. **Named dragons are five records, not thirteen.** Handle the rest through `LCharDragonAny`.
5. **Extend the tier ladder past 50 for DLC**, or accept that Karstaag (90) and the Ebony Warrior (80)
   sit outside it as documented exceptions.
6. **The `_BF_` banded records are prior art.** Dawnguard's Forgotten Vale enemies use explicit
   10-level bands (1/10/20/30/40, 10/20/30/40/50) — the only deliberately-authored fixed ladder in
   the game. Read them before inventing `design/tiers.md`.

## 10. Open questions

1. **Which of the 21 leveled-name bosses are *meant* to be bespoke?** Jyrik and Sigdis Gauldurson are
   quest-critical Gauldur brothers; Cragslane's "Butcher" is scenery. Needs a curation pass in Phase 3,
   not a blanket rule. `[unverified]`
2. **Do the `Lvl*` wrappers accept a retargeted `Template` cleanly**, or does the name/reference
   binding break? This is the cheapest implementation lever found so far and it is untested.
   `[unverified]`
3. **Are there named bosses this method missed** — hostile uniques with no `Unique` flag, no `Boss`
   ref, and a common race? The three criteria are deliberately broad but not exhaustive. `[unverified]`
4. **What are the DLC display names?** Not recoverable from the decompile (§1). If Phase 3 needs them
   for documentation, they must come from the `.STRINGS` files or the CK. `[verified]` that they are
   absent here.
