---
id: "skyrim/reference/engine-behaviour"
title: "Engine behaviour — the five questions that gated Phase 3"
slug: "engine-behaviour"
section: "skyrim/reference"
game: "skyrim"
kind: "reference"
project: null
mod: null
tags: ["skyrim", "engine", "creation-kit", "encounter-zones", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/design/engine-behaviour.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 11, "unverified": 2, "upstream": 0, "verified": 12}
lines: 258
content_sha256: "89e3e5ac3af5e804b0c3261aff5809ce51bd92d4876394a551f5cc99bb919681"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Engine behaviour — the five questions that gated Phase 3

> Researched 2026-07-28, before any design doc was written, because every candidate architecture
> hinged on them. Sources are (a) read source code and records in `reference/` → `[verified]`,
> (b) official Creation Kit documentation and convergent community/RE evidence → `[community]`,
> with the provenance named each time. Confidence marks follow the workspace convention; nothing
> below has been upgraded past what its evidence supports.
>
> **Net result: only two cheap in-game checks remain** (see §7). Everything else is settled enough
> to write `tiers.md`, `difficulty-map.md`, `loot-model.md` and `implementation-strategy.md`.

## 0. The zone-level model (background for everything below)

The engine's actual model, assembled from the CK wiki, the CommonLibSSE reverse-engineered headers,
and the mods that exist purely to work around it:

1. **Static data** (`BGSEncounterZone::data`, what the ECZN record ships): `minLevel` (int8),
   `maxLevel` (int8, **0 = uncapped**), flags (`NeverResets`, `MatchPCBelowMinimumLevel`,
   `DisableCombatBoundary`), owner, location. `[community]` — CommonLibSSE-NG
   `BGSEncounterZone.h`, field-for-field.
2. **Runtime data** (`BGSEncounterZone::gameData`): `attachTime`, `detachTime`, `resetTime`, and a
   computed **`zoneLevel`** (uint16). `BGSEncounterZone` overrides `SaveGame`/`LoadGame`, i.e. this
   runtime state is **written into the save file**. `[community]` — same header.
3. **The zone level is computed once, on the first load of any of the zone's cells**, as the
   player's level clamped into `[minLevel, maxLevel]` (`maxLevel` 0 = no cap;
   `MatchPCBelowMinimumLevel` lets it follow the player *below* the min). It is then **stored and
   never recalculated** until the zone resets — and `NeverResets` zones never reset, so their level
   is frozen for the whole playthrough. `[community]` — CK wiki "Encounter Zone"; the entire premise
   of *Encounter Zones Unlocked SE* (Nexus 19608), an SKSE dll that exists solely to force
   recalculation.
4. That stored `zoneLevel` is then the level input for content generation in the zone's cells —
   with one big exception (§1).

The CK wiki's one-sentence summary: *"an Encounter Zone dictates how Leveled Lists are generated."*

## 1. Does the ECZN clamp govern LVLN selection, or only `PcLevelMult` actors?

**Answer: it governs leveled-*list* selection (class A), and it does NOT govern directly-computed
`PcLevelMult` actor levels (class D). This is the opposite of what `morrowloot.md` §9.1 assumed.**

- **LVLN selection uses the zone level — official CK documentation.** CK wiki *LeveledCharacter →
  Leveled Character References*: "When the player enters a location, the game checks the player's
  level against the Encounter Zone's Min and Max levels, then resolves a level for the space. It
  then determines which leveled actors should be generated from each leveled list." `[community]`
  (Bethesda's own docs, not tested in this workspace).
- **`PcLevelMult` actors ignore the zone.** An NPC whose `Configuration.Level` is `PcLevelMult`
  computes `playerLevel × mult` clamped to `[CalcMinLevel, CalcMaxLevel]` against the **raw player
  level**, not the zone level. Evidence: the mod *Enemies Respect Encounter Zones* (Nexus 78847)
  exists specifically to fix this — its description states that in vanilla "some NPCs use level
  scaling, which uses the player level, ignoring the encounter zone", while enemy *type* selection
  respects the zone. Corroborated by community discussion around EZ overhauls. `[community]`,
  two independent sources.

**Design consequence.** The two levers split cleanly by actor class (`enemy-taxonomy.md` §6):

| Class | Zone clamps it? | Ehlnofey's lever |
|---|---|---|
| A — LVLN ladder spawns (bandits, draugr, …) | **Yes** — selection runs at zone level | `ECZN` bands do the work; ladder edits optional |
| D — `PcLevelMult` actors (guards ×1 [20–50], Alduin ×1.2, followers, 114 Requiem stragglers) | **No** | Must be fixed per-NPC — SkyPatcher `filterByPCLevelMult` + `level`, exactly what it's built for |

This *strengthens* the hybrid recommendation: zones cannot deliver bone 1 alone even in principle,
and the piece they miss is precisely the piece SkyPatcher's NPC patcher reaches. MLU's residual
scaling (the `[38–53]`-still-moves problem) is now explained mechanically rather than observed.

## 2. What happens at `MinLevel == MaxLevel`?

**Answer: it degenerates cleanly to a fixed zone level — and it is NOT un-taken prior art.
MorrowLoot Ultimate ships three such zones.** `[verified]` from `reference/mods/MLUYaml/`:

| Zone | Band | Note |
|---|---|---|
| `ColdRockPassZone` (`0BC0A4:Skyrim.esm`) | **22–22** | vanilla was min 8, uncapped |
| `ShrineofBoethiahZone` (`0F5BA8:Skyrim.esm`) | **30–30** | |
| `MLU_MQ301` (`1D6A71:MLU.esp`) | **40–40** | a *new* ECZN record MLU adds |

MLU is a decade old and very widely used; no community reports of these three zones misbehaving
were found. Arithmetically, `clamp(playerLevel, N, N) = N` for every player level, so the
documented calculation has no edge case to hit. `[community]` for the formula, `[verified]` for the
prior art. A one-visit in-game sanity check (§7) remains cheap and worth doing, but the risk has
collapsed.

**Three authoring constraints,** all `[verified]` from records/headers:

1. `MaxLevel: 0` means **uncapped**, not "level 0" — a fixed band must use `min = max = N`, `N ≥ 1`.
2. Do **not** set `MatchPcBelowMinimumLevel` on a fixed zone (it re-opens the bottom of the band).
   Exactly one vanilla zone uses it: `WinterholdCollegeMiddenZone` (`10D415`, band 6–30).
3. Both fields are **int8** — the ceiling is 127. (SkyPatcher enforces the same bound in
   `encounterzone.cpp`.)

Vanilla precedent for banding at all is thinner than CLAUDE.md recorded: **six** zones ship a
`MaxLevel` (not 5) — BleakFallsBarrow 6–20, EmbershardMine 6–10, HaltedStreamCamp 6–10,
WhiteRiverWatch 6–10, WinterholdCollegeMidden 6–30, and `DLC2DremoraShopZone` 0–99. `[verified]`

## 3. Does the zone clamp reach loot, or only actors?

**Answer: yes for leveled-item lists resolved inside the zone's cells — actors and loot draw from
the same zone level — with one deliberate leak (boss-chest "special loot") and one independent
track (NPC gear).**

- **Primary-source evidence, found 2026-07-28 while writing `tiers.md`: the engine ships three
  game settings that name the zone level as the operand for special loot.** `[verified]` in
  `reference/Base/01Skyrim/GameSettings/`:

  | GMST | FormKey | Value |
  |---|---|---|
  | `fSpecialLootMinZoneLevelMult` | `10FEDD:Skyrim.esm` | **0.4** |
  | `fSpecialLootMaxZoneLevelMult` | `10FEDF:Skyrim.esm` | **1.0** |
  | `fSpecialLootMinPCLevelMult` | `10FEDE:Skyrim.esm` | **0.6** |

  There is no in-repo *documentation* of the formula, but the existence and naming of
  `…ZoneLevelMult` settings is direct record-level evidence that loot generation reads the zone
  level — which is what UESP asserted and could not verify. This upgrades the answer from
  "three convergent secondary sources" to "secondary sources plus a primary-source mechanism", and
  it **retires the UESP "up to twice the level minus one" figure**, which no shipped setting
  supports. Still `[community]` for the exact arithmetic; no longer the weakest of the five.
- **Two things follow for `loot-model.md`.** First, the special-loot roll appears to span
  **0.4 × zoneLevel to 1.0 × zoneLevel**, i.e. *below* the band rather than above it — the opposite
  of the "jackpot tail" this section previously assumed. Second, and more important:
  **`fSpecialLootMinPCLevelMult` = 0.6 is a live bone-1 leak** — a floor tied to 0.6 × **player**
  level, independent of the zone. A level-50 character looting a fixed T2 chest still rolls against
  level 30. It is a GMST, so closing it costs exactly one record. `[verified]` that the setting
  exists and its value; `[unverified]` that zeroing it has no unwanted side effect.
- **NPC gear is not zone-loot**: outfit/inventory lists resolve against the NPC's own level (the
  independent gear track already proven by `BanditArmorMeleeShield20Outfit`, taxonomy §8), so a
  zone band affects gear only *via* the level of the actor the LVLN picked.
- **Why MLU still truncates LVLI**: a clamp bounds what a *place* generates; it cannot remove an
  item from the *game*. MLU's glass/ebony/daedric cuts are a distribution decision (nothing
  generates them anywhere), which only list surgery — or SkyPatcher `leveledList` rules — can
  express. The two mechanisms are complements, not alternatives. `[verified]` for what MLU does;
  the inference in `morrowloot.md` §9.2 ("hints the clamp does not govern item lists") is hereby
  **retired** — the truncation is explained by reach, not by the clamp's scope.

## 4. How does `LevelModifier` compose with the zone level?

**Answer: it is a multiplier on the *resolved zone level*, applied as the lookup level into the
placed reference's leveled list — not a multiplier on the actor's own level, and not an offset.**
CK wiki *LeveledCharacter → Leveled Character References*, `[community]` (official docs):

| Modifier | List lookup level | Selection rule |
|---|---|---|
| Easy | 0.33 × zoneLevel | from **all** entries at or below it (each Easy ref may differ) |
| Medium | 0.67 × zoneLevel | closest-not-exceeding (all Medium refs in the space identical) |
| Hard | 1.00 × zoneLevel | closest-not-exceeding |
| Very Hard | 1.25 × zoneLevel | closest-not-exceeding, **plus a bump rule**: if the result equals the Hard result, take the next-higher list entry regardless of its level |
| *None* | *documented as the player's level* | closest-not-exceeding |

Multipliers are the `fLeveledActorMult*` GMSTs — `[verified]` in
`reference/Base/01Skyrim/GameSettings/`: Easy `01A1D9` = 0.33, Medium `01A1DB` = 0.67, Hard
`01A1DA` = 1.0, VeryHard `023C0B` = 1.25.

Two implications:

1. **In a fixed-band zone, `LevelModifier` becomes Ehlnofey's within-dungeon texture.** With
   `zoneLevel` pinned at N, Easy/Medium/Hard/VeryHard rooms sit at fixed fractions of N forever —
   vanilla's 5,685 hand-placed modifiers keep doing their job with no edits, which is what "keep
   it" (CLAUDE.md machinery table) buys. The Requiem-vs-MLU multiplier question (leave at
   0.33–1.25 vs compress to 0.7–1.3) is now precisely: *how much intra-dungeon spread does a tier
   allow?* — a `tiers.md` decision with a known operand.
2. **The "None" row is an anomaly worth one console check** (§7): taken literally, unmodified refs
   resolve against the raw *player* level even inside a zone. The wording may simply be sloppy
   (None ≙ Hard ×1.0 is the natural reading of the engine doing one code path); no secondary source
   distinguishes them. `[unverified]` either way — cheap to test alongside §7's other checks.

   Note the blast radius is **small**, because this row only bites where there is a leveled list to
   look up. Of the ~46% of placed actors carrying no modifier, all but **9** are fixed-level or
   `PcLevelMult` and are unaffected either way — see §7 item 1 and `probe-test-protocol.md` §4. This
   is a *second bone-1 leak* only in the narrow sense of nine records.

## 5. SkyPatcher ECZN patching — timing and persistence

**Answer: rules apply once per launch at `kDataLoaded`, before the main menu and before any save
is loaded, by writing the form's static data in memory — indistinguishable thereafter from values
the plugin shipped. Nothing SkyPatcher does persists in the save; but the engine's own
`zoneLevel` cache (§0.3) does, and it gates *any* zone edit, plugin or runtime, identically.**
All `[verified]` from `reference/mods/SkyPatcherSrc/`:

- `main.cpp:1654–1661`: `ENCOUNTERZONE::readConfig(...\SkyPatcher\encounterzone\)` runs in the
  `kDataLoaded` handler, gated by `iEnableEncounterZonePatching` in `SkyPatcher.ini`. `kDataLoaded`
  fires once at launch after all plugins load — before the main menu, therefore before any
  save/new-game exists.
- `encounterzone.cpp:229–345` (`patch()`): writes `BGSEncounterZone::data.minLevel` /
  `data.maxLevel` (int8-range-checked) and can set/clear `data.location`. It touches **static
  data only** — never `gameData`, never the stored `zoneLevel`.
- SkyPatcher's SKSE co-save (`main.cpp` `SaveCallback`/`LoadCallback`) serializes exactly one
  record type, `'STYL'` (NPC visual styles). No zone state whatsoever.

**Consequences:**

1. **The "already cached by then?" worry from `skypatcher.md` OQ1 is resolved in the good
   direction**: at `kDataLoaded` no save is loaded and no zone has attached, so every zone-level
   calculation in the session happens *after* the patch. Timing is not a failure mode.
2. **Save-game behaviour is an engine property, not a SkyPatcher one** — and it is the same for
   option A and option B. On an existing save, any zone the player has already visited keeps its
   stored `zoneLevel` until the zone resets; the 41 `NeverResets` zones keep it forever
   (`dungeons.md` §6.5 answered: on an old save, Ehlnofey's bands apply only to unvisited or
   since-reset zones). On a new game, coverage is total. Options: ship as new-game-recommended
   (MLU's de-facto stance), or take *Encounter Zones Unlocked SE* as an optional companion that
   forces recalculation.
3. One SkyPatcher-specific residue: rules re-apply every launch, so **removing** an INI cleanly
   reverts unvisited zones — better uninstall behaviour than a plugin, with the same §0.3 caveat
   for visited ones.

## 6. Bonus: `CalculateFromAllLevelsLessThanOrEqualPlayer` (taxonomy §7.2)

Settled by the same two pages, `[community]`: **without** the flag, a list is consulted at level L
by taking only the entries at the *highest* entry-level ≤ L (uniform pick among ties; lower-level
entries are ignored). **With** the flag, every entry with level ≤ L is eligible (then Chance None
etc. apply). So flattening a ladder list without the flag yields "always the top eligible tier",
while setting it yields "any tier up to L" — vanilla's inconsistent usage (taxonomy §1) is a per-
list decision Ehlnofey inherits and must set deliberately when it edits a list.

## 7. What actually still needs an in-game test

The five-question test session shrinks to **one short probe visit**, best run when the first
records exist anyway:

1. **The "None" modifier ambiguity** (§4). `GetLevel` on an unmodified placed ref vs a `Hard` ref, at
   a player level far from N. It decides whether placed refs with no modifier honour the zone or
   ignore it.

   > **Revised — this was written as "the highest-value test in the project", sized at ~1,928
   > interior refs. The real exposure is 9.** `LevelModifier` multiplies the *leveled-list lookup
   > level* (§4), so it is inert unless the ref's base resolves through its template chain to an
   > `LVLN` — a fixed-level `NPC_` has no lookup to modify, and a `PcLevelMult` actor ignores zones
   > outright (§1). Census over all 291 zoned interior cells of `Skyrim.esm` `[verified]`: **2,147**
   > refs are leveled-ladder-backed, of which **2,138 already carry a modifier and 9 do not**; the
   > remaining 1,097 unmodified refs are 1,014 fixed-level and 83 `PcLevelMult`. Method and the full
   > list of nine: `probe-test-protocol.md` §4. Correction folded into
   > `implementation-strategy.md` §7.1 and `tiers.md` §4.
   >
   > Still worth running — it is free and it fixes the semantics for anything Ehlnofey places itself
   > — but **test 2 below is now the one to run first.**
2. **Loot check** (§3): fix a zone at N, confirm chest contents roll at N, not player level. The
   `fSpecialLoot*ZoneLevelMult` settings found since largely answer the *mechanism*; what remains
   worth observing is the **`fSpecialLootMinPCLevelMult` = 0.6 floor**, i.e. whether a high-level
   character does in fact pull better special loot from a low fixed zone.
3. *(Optional, belt-and-braces)* min == max sanity per §2 — observable for free during 1 and 2.

All three are one dungeon visit at a mismatched player level.

Everything else — clamp scope, `PcLevelMult` exemption, zero-width bands, `LevelModifier`
composition, SkyPatcher timing/persistence — is settled at the confidence marked above.

## Sources

In-repo (`[verified]`): `reference/mods/SkyPatcherSrc/main.cpp`, `encounterzone.cpp` ·
`reference/mods/MLUYaml/EncounterZones/` · `reference/Base/*/EncounterZones/` ·
`reference/Base/01Skyrim/GameSettings/fLeveledActorMult*` · `…/fSpecialLoot*` (added 2026-07-28).

External (`[community]`):
- [CK wiki: Encounter Zone](https://ck.uesp.net/wiki/Encounter_Zone) — zone dialog semantics, min/max/flags, worked examples
- [CK wiki: LeveledCharacter](https://ck.uesp.net/wiki/LeveledCharacter) — zone-level resolution "for the space", LevelModifier table, VeryHard bump, All-Levels flag
- [UESP: Skyrim:Leveled Lists](https://en.uesp.net/wiki/Skyrim:Leveled_Lists) — list request model, flags, "possibly modified by the level of the encounter zone"
- [UESP: Skyrim:Dungeons](https://en.uesp.net/wiki/Skyrim:Dungeons) — §Levels (enemies *and* loot; carries a verify-needed tag), special loot
- [CommonLibSSE-NG `BGSEncounterZone.h`](https://github.com/CharmedBaryon/CommonLibSSE-NG/blob/main/include/RE/B/BGSEncounterZone.h) — RE'd struct layout: `data` vs `gameData.zoneLevel`, `SaveGame`/`LoadGame`
- [Encounter Zones Unlocked SE (Nexus 19608)](https://www.nexusmods.com/skyrimspecialedition/mods/19608) — zone level frozen on first visit, stored in save ([LE original](https://www.nexusmods.com/skyrim/mods/84924))
- [Enemies Respect Encounter Zones (Nexus 78847)](https://www.nexusmods.com/skyrimspecialedition/mods/78847) — vanilla `PcLevelMult` scaling ignores the zone
- [Arena — An Encounter Zone Overhaul (Nexus 33487)](https://www.nexusmods.com/skyrimspecialedition/mods/33487) — large-scale precedent for zone-banding as the difficulty map
