---
id: "skyrim/world/factions"
title: "Factions"
slug: "factions"
section: "skyrim/world"
game: "skyrim"
kind: "world"
project: null
mod: null
tags: ["skyrim", "world-research", "vanilla", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/world/factions.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: "Phase 1, document 3"
confidence: {"author": 0, "community": 2, "unverified": 6, "upstream": 0, "verified": 23}
lines: 321
content_sha256: "e148bcc0fb639f523169e266784684190551040bc39b78851e6377bbd0e67ec1"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
unique_title: "Factions (skyrim/world)"
---

# Factions

**Phase 1, document 3.** What `FACT` records actually control, which ones matter to a deleveling
mod, and — the question that decides Phase 2 — **whether faction membership is a reliable key for
distributing rules to NPCs**.

Read `overview.md` and `enemy-taxonomy.md` first. This document answers "who is this NPC, and can I
select them by it"; the taxonomy answers "what level are they".

Confidence marks: `[verified]` = read in `reference/`, `[community]` = established modding knowledge
not re-tested here, `[unverified]` = plausible, unchecked.

---

## 1. Why this matters

Implementation option **B** in CLAUDE.md — SkyPatcher INI rules and/or SPID distribution — selects
NPCs by *filter*, and faction is the primary filter both engines expose. `[community]` If faction
membership does not cleanly identify an archetype, option B collapses and the choice narrows to A
(plugin overrides) or C (generated patch). So the load-bearing questions are:

1. Does every member of an archetype actually carry its faction?
2. Does the `TemplateFlags: Factions` inheritance from `enemy-taxonomy.md` §1 break static reads?
3. Are factions granular enough to separate species, or only "creature vs humanoid"?

**All three answer favourably.** Details in §4–§5.

---

## 2. Census

1,084 `FACT` records in `Skyrim.esm`, but the great majority are bookkeeping. Rough functional split
by EditorID convention `[verified]`:

| Category | Count |
|---|---|
| Combat, creature and unclassified | 386 |
| Quest / radiant scripting (`DA*`, `MS*`, `MQ*`, `TG*`, `DB*`, `MG*`, `WE*`, `WI*`, `C0*`, `T0*`) | 259 |
| Services / vendor (`Services*`) | 135 |
| Civil War (`CW*`) | 67 |
| Per-dungeon (`dun*`) | 59 |
| Town / guard | 54 |
| Crime | 53 |
| Occupation (`Job*`) | 48 |
| Player-side | 23 |

DLC adds 82 (Dawnguard), 102 (Dragonborn), 141 (Hearthfire — almost all
Hearthfire-house ownership bookkeeping), 4 (Update). `[verified]`

### Record shape

```yaml
# BanditFaction - 01BCC0
Relations:
- Target: 109ACF:Skyrim.esm
  Reaction: Ally
- Target: 0330B1:Skyrim.esm        # no Reaction: line == Neutral (Mutagen omits defaults)
Flags:
- HiddenFromPC
- CanBeOwner
CrimeValues:
  Arrest: True
  AttackOnSight: True
VendorValues: {}
```

Field frequency across all 1,084 `[verified]`: `CrimeValues` 1,083 · `VendorValues` 996 · `Flags` 778
· `Name` 435 · `Relations` 388 · `VendorLocation` 150 · `VendorBuySellList` 149 ·
`MerchantContainer` 145 · `SharedCrimeFactionList` 48 · `Conditions` 36 · `Ranks` **23**.

Flag census `[verified]`: `CanBeOwner` 372 · `HiddenFromPC` 340 · `Vendor` 145 · `TrackCrime` 58 ·
`IgnoreTrespass`/`IgnoreStealing`/`IgnoreMurder`/`IgnoreAssault` 40 each · `IgnorePickpocket` 37 ·
`DoNotReportCrimesAgainstMembers` 31 · `IgnoreWerewolf` 24 · `CrimeGoldUseDefaults` 13 ·
`SpecialCombat` 11.

Relation reactions across all 388 factions that have any `[verified]`: **Friend 348 · Ally 317 ·
Enemy 302 · Neutral 69** (explicit; absent `Reaction:` is also Neutral).

Only **23 factions have `Ranks`**, and none of them is a combat archetype — they are the joinable
guilds (Companions 4, College of Winterhold 7, Thieves Guild 2, Arena 5) and a handful of quest
factions. `[verified]` **Rank is not a usable tier axis for Ehlnofey.**

> ### `Arrest` and `AttackOnSight` are not hostility markers
> 1,055 of 1,084 factions have `Arrest: True` and **1,075 have `AttackOnSight: True`** — including
> `ServicesWhiterunBanneredMare` and `TownWhiterunFaction`. These are the CK Crime-tab settings
> describing how a faction responds to crimes *against it*, and they are set near-universally.
> `[verified]` They carry no signal about whether a faction fights the player. Anything filtering on
> them will match essentially the whole game.

---

## 3. Hostility to the player is AI aggression, not faction relations

This is the finding that most changes how to read the world.

Only **60 factions** carry `Reaction: Enemy` toward `PlayerFaction` (000DB1), and they are almost
entirely quest scripting — `DA*PlayerEnemyFaction`, `TG07ValdFactionHatesPlayer`,
`WIPlayerEnemyFaction`, `MQ304AlduinFaction`, and so on. `[verified]`

**Not one of the generic hostile archetypes is on that list.** `BanditFaction`, `DraugrFaction`,
`FalmerFaction`, `ForswornFaction`, `WarlockFaction`, `VampireFaction`, `ThalmorFaction`,
`HagravenFaction` — all Neutral to the player at the record level. The only two generic combat
factions that *are* Enemy to `PlayerFaction` are:

- **`DragonFaction`** (032D9C) — Enemy to the player *and* to almost everyone else (see §5)
- **`SilverHandFaction`** (0AA0A4) — Enemy to `PlayerFaction` and `CompanionsFaction`

So what makes a bandit attack? **`AIData.Aggression`.** Census over all 5,118 NPCs `[verified]`:

| Aggression | NPCs | On `Enc*` archetype NPCs |
|---|---|---|
| `VeryAggressive` | 1,889 | **1,537** |
| `Aggressive` | 739 | 145 |
| `Frenzied` | 2 | 0 |
| *absent* (inherited via `TemplateFlags: AIData`, or the default `Unaggressive`) | 2,488 | 81 |

**87% of `Enc*` archetype NPCs are `VeryAggressive`.** That, not a faction relation, is why they
attack on sight; the faction graph exists to decide who they *don't* attack.

Two consequences for Ehlnofey:

- **Bone 2 ("danger is legible") has no faction-level lever.** You cannot make a region's enemies
  hostile-on-approach by editing relations, because they already attack everything they don't
  recognise. Legibility has to come from geography, visual tier, lore and dialogue.
- **A "make X non-hostile" exception is an `AIData` edit**, and `AIData` is itself frequently
  inherited through the template chain — so it lands on the template, not the visible NPC.
  `[verified]`

---

## 4. Faction membership is a reliable key

The worry from `enemy-taxonomy.md` §1 was that `TemplateFlags: Factions` makes an NPC's own
`Factions:` list inert, so a static read would report the wrong membership.

Measured across all 5,118 NPCs by resolving the template chain wherever the flag is set `[verified]`:

| | Count |
|---|---|
| NPCs with `Factions` in `TemplateFlags` **and** a `Template` — own list is inert | **2,921** |
| …of those, where the resolved list actually **differs** from the local one | **1** |

The single divergence is `dunShadowgreenLvlSprigganAmbushHoldPositionCustom011024` (085553), which
declares three factions locally but inherits an empty list from its template.

**So reading an NPC's own `Factions:` list gives the correct answer 5,117 times out of 5,118.**
Bethesda kept the local copies in sync. A faction-based distribution filter is safe — and at runtime
the question is moot anyway, since SPID/SkyPatcher see the resolved actor. `[verified]` for the
static data, `[unverified]` for the runtime claim.

### Granularity: species factions do exist

The species factions have small member counts (Chaurus 3, Spriggan 5, Ice Wraith 6), which looks
alarming until you remember from the taxonomy that creatures have very few NPC records each. The
memberships are real and layered `[verified]`:

```
EncWolf      → CreatureFaction, PredatorFaction, SprigganPredatorFaction, WolfFaction
EncBear      → CreatureFaction, PredatorFaction, SprigganPredatorFaction, BearFaction
EncTroll     → CreatureFaction, TrollFaction
EncGiant01   → CreatureFaction, GiantFaction
EncSkeever   → CreatureFaction, PreyFaction, SkeeverFaction
EncChaurus   → CreatureFaction, PredatorFaction, ChaurusFaction
```

Three usable tiers of granularity: **`CreatureFaction`** (creature vs humanoid, 660 members),
**`PredatorFaction` / `PreyFaction`** (53 / 69 — the threat axis), and the **species faction**. That
is enough to write per-species rules without touching race records.

### Factionless NPCs

1,036 NPCs resolve to no faction at all. Composition `[verified]`: **370 `Lvl*` wrapper records** (the
placed-boss wrappers from `dungeons.md` §1, which delegate everything to a leveled list), ~180 race
preset records (20 per playable race), 35 `AudioTemplate*`, 22 `Treas*` corpses, and assorted test
records. **None is a real spawned combatant** — the `Lvl*` wrappers resolve at runtime to an LVLN leaf
that does carry factions. Statically confusing, functionally harmless.

---

## 5. The combat factions

Member counts are NPC records in `Skyrim.esm` carrying the faction. `[verified]`

| Faction | FormKey | Members | Notes |
|---|---|---|---|
| `CreatureFaction` | 000013 | 660 | the creature/humanoid divide |
| `BanditFaction` | 01BCC0 | 413 | largest humanoid faction |
| `WarlockFaction` | 026724 | 365 | incl. all elemental variants |
| `DraugrFaction` | 02430D | 350 | |
| `ForswornFaction` | 043599 | 168 | Reach-locked |
| `NecromancerFaction` | 034B74 | 87 | Ally of `WarlockFaction` |
| `VampireFaction` | 027242 | 86 | **overridden by Dawnguard** |
| `ThalmorFaction` | 039F26 | 76 | |
| `PreyFaction` | 02E894 | 69 | |
| `PredatorFaction` | 02E893 | 53 | |
| `SkeletonFaction` | 02D1DF | 48 | |
| `HagravenFaction` | 04359E | 48 | the hub of the Reach cluster |
| `DragonFaction` | 032D9C | 44 | hostile to nearly everything |
| `FalmerFaction` | 02997E | 38 | |
| `DwarvenAutomatonFaction` | 043598 | 28 | **only relation is Ally-self** |
| `WolfFaction` | 03E691 | 23 | |
| `DaedraFaction` | 02B0E5 | 22 | **only relation is Friend-self** |
| `SpiderFaction` | 02997F | 21 | |
| `DremoraFaction` | 043597 | 20 | |
| `WerewolfFaction` | 043594 | 15 | |
| `DragonPriestFaction` | 106643 | 15 | Ally `DraugrFaction` |
| `SilverHandFaction` | 0AA0A4 | 14 | Enemy `PlayerFaction` + `CompanionsFaction` |
| `GiantFaction` | 04359A | 9 | Ally `MammothFaction` |
| `TrollFaction` | 0435A1 | 9 | |
| `BearFaction` | 0FBBF3 | 7 | **only relation is Ally-self** |
| `SkeeverFaction` | 0330B1 | 6 | |
| `IceWraithFaction` | 0435A0 | 6 | |
| `SprigganFaction` | 03E094 | 5 | |
| `WispFaction` | 03E096 | 4 | |
| `ChaurusFaction` | 03C9A8 | 3 | |

### The alliance clusters

Reading the `Relations` graph, vanilla's hostile factions form four loose blocs `[verified]`:

**Undead / necromantic** — the densest cluster.
`DraugrFaction` ⇄ `SkeletonFaction` ⇄ `NecromancerFaction` ⇄ `WarlockFaction` (Ally),
`DraugrFaction` → `DragonPriestFaction` (Ally), `VampireFaction` ⇄ `DraugrFaction`/`SkeletonFaction`
(Friend), `WarlockFaction` → all three Atronach factions (Friend).

**Reach / witch** — hubbed on `HagravenFaction`, which is Friend to `ForswornFaction`, `TrollFaction`,
`IceWraithFaction`, `SpiderFaction`, `DremoraFaction`, `ChaurusFaction`, `WispFaction` and
`SkeeverFaction`, and **Enemy to `SprigganFaction`**. `ForswornFaction` is Friend to `HagravenFaction`
and `GoatFaction`, Ally to `ForswornDogFaction`.

**Falmer / deep** — `FalmerFaction` Ally `ChaurusFaction` and `WispFaction`, Friend `SpiderFaction`
and `SkeeverFaction`.

**Wilderness** — `PredatorFaction` Enemy `PreyFaction`; `PreyFaction` Enemy `HunterFaction`;
`WolfFaction` Friend `WerewolfFaction`/`VampireFaction`, Ally `PlayerWerewolfFaction`.

`DragonFaction` sits outside all of them: **Enemy to `PlayerFaction`, `DraugrFaction`,
`FalmerFaction`, `GiantFaction`, `NecromancerFaction`, `SilverHandFaction`, `ThalmorFaction`,
`ForswornFaction`, `WarlockFaction`, `VampireFaction`, `BanditFaction`, `IsGuardFaction`,
`CaravanGuard` and `BladesRecruitsFaction`** — Friend only to `DragonPriestFaction`, Neutral to
predators and prey. A dragon attacking a bandit camp is authored behaviour, not emergent. `[verified]`

Three factions are **isolates** with no outward relations at all — `DwarvenAutomatonFaction` (Ally
self), `BearFaction` (Ally self), `DaedraFaction` (Friend self). Automatons and bears fight everything
that isn't their own kind. `[verified]`

**`dunPrisonerFaction` and `CaptiveFaction` appear as Friend in almost every hostile faction's
relation list** — that is how vanilla stops dungeon captives being killed by their captors before the
player arrives. Do not prune these as noise when editing relations. `[verified]`

---

## 6. DLC

**Dawnguard** (82 factions) **overrides two `Skyrim.esm` records** — `VampireFaction` (027242) and
`VampireThrallFaction` (02EB13) — which appear as `… - <FormID>_Skyrim.esm.yaml` inside
`reference/Base/03Dawnguard/Factions/`. `[verified]` Same master-order problem as the leveled lists in
`enemy-taxonomy.md` §2.7: an Ehlnofey override of those must load after Dawnguard and take it as a
master.

New Dawnguard combat factions: `DLC1VampireFaction`, `DLC1DawnguardFaction`, `DLC1HunterFaction`,
`DLC1VampireCrimeFaction`, plus a large radiant-disguise set (`DLC1RadiantDisguisedHunterFaction*`,
`DLC1RadiantDisguisedVampireFaction*`) and the player-state factions `DLC1PlayerTurnedVampire` /
`DLC1PlayerVampireLordFaction`.

**Dragonborn** (102 factions) adds no overrides of vanilla combat factions and introduces a clean new
set: `DLC2AshSpawnFaction`, `DLC2RieklingFaction`, `DLC2ThirskRieklingFaction`, `DLC2SeekerFaction`,
`DLC2BenthicLurkerFaction`, `DLC2CultistFaction`, `DLC2MiraakFaction`, `DLC2TribalWerebearFaction`,
`DLC2HunterFaction`. `[verified]` Solstheim's archetypes are cleanly separable by faction — consistent
with its better-structured encounter zones (`dungeons.md` §3).

---

## 7. What this gives Phase 2 and 3

1. **Option B is not blocked by faction data.** Membership is reliable (5,117/5,118), granular enough
   for per-species rules, and stable across the template chain. Whether SkyPatcher and SPID can
   *express* the rules Ehlnofey needs is still `[unverified]` and remains the Phase 2 deliverable —
   but the selector side is sound.
2. **Faction is the right join key between `enemy-taxonomy.md` and a rule file.** Every class-A
   archetype has exactly one identifying faction with a three-digit member count.
3. **Rank is not a tier axis** — only 23 factions have ranks and none is a combat archetype.
4. **Do not touch `Relations` to change difficulty.** Hostility to the player is `AIData.Aggression`;
   relations only decide who fights whom. Editing them risks breaking the captive/prisoner protection
   that runs through every hostile faction.
5. **Dawnguard's two faction overrides** join its leveled-list overrides on the master-order list for
   `implementation-strategy.md`.

## 8. Open questions

1. **What exactly can SPID and SkyPatcher filter on** — faction only, or faction + keyword + race +
   level + editor-ID pattern? This determines whether the three-tier granularity in §4 is reachable.
   `[unverified]`, Phase 2.
2. **Does a runtime distributor see the resolved actor or the template?** Assumed resolved; matters
   for the 2,921 template-inheriting NPCs. `[unverified]`
3. **Are the 370 `Lvl*` wrappers targetable at all** by a faction filter, given they carry no
   factions until the leveled list resolves? `[unverified]` — relevant because they are exactly the
   dungeon bosses.

---

## 9. Method note — a hazard that produced wrong data here

Building the relation matrix, an `awk` lookup of the form:

```awk
awk -F'\t' -v i="02E893" '$1==i { ... }'      # WRONG
```

matched **eight** rows instead of one. `awk` treats a `-v` assignment as a *strnum*, so `02E893` is
parsed as scientific notation — `2 × 10^893`, which overflows to `+inf`. Every other FormID of the
same shape (`02E894`, `04E852`, …) also becomes `+inf`, and `+inf == +inf`. The truncating case is
just as bad: `0130DB` numifies to `130`, colliding with `0130E2` and the rest of the `LocType*` block.

```awk
awk -F'\t' -v i="02E893" '$1""==i"" { ... }'  # correct — forces string comparison
```

**Hex FormIDs must never be compared numerically.** Force string context with `""`, or use them as
array subscripts (always strings) — which is why the `dungeons.md` join, built entirely on
associative arrays, was unaffected. `[verified]`
