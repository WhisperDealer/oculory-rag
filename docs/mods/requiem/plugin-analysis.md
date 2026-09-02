---
id: "mods/requiem/plugin-analysis"
title: "Requiem.esp — what it actually does to levels"
slug: "plugin-analysis"
section: "mods/requiem"
game: "skyrim"
kind: "research"
project: null
mod: "requiem"
tags: ["skyrim", "requiem", "deleveling", "third-party-mod", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/prior-art/requiem/plugin-analysis.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 0, "unverified": 1, "upstream": 0, "verified": 16}
lines: 223
content_sha256: "b825e0de0492d43060e2101e38c783487bdd03133661e0b3578576ec88c61433"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Requiem.esp — what it actually does to levels

Measured against `reference/mods/RequiemYaml/` (Spriggit decompile of Requiem 6.0.2) and
`reference/Base/` (Skyrim.esm + Update.esm + the three DLC). Every number below was counted by
parsing records, not by grepping lines — per the `CLAUDE.md` census rule.

## 0. Shape of the plugin

| Metric | Value |
|---|---|
| Total records | **26,620** |
| New records (`…:Requiem.esp`) | 7,854 |
| Override records | **18,766** |
| Spriggit YAML on disk | **108 MB** |
| Masters | Skyrim, Update, Dawnguard, HearthFires, Dragonborn, **USSEP**, + 4 Creation Club plugins |

`reference/mods/RequiemYaml/RecordData.yaml`. The header description is
`Version: 6.0.2` plus `{{Smash:Requiem}}` — a **Mator Smash** tag, not a ReqTag. `[verified]`

Top record types by count: Weapons 4,340 · LeveledItems 3,433 · Armors 3,106 · Npcs 2,702 ·
ConstructibleObjects 2,263 · MagicEffects 2,050 · Spells 1,809 · Perks 599 · **LeveledNpcs 571** ·
GameSettings 419 · **EncounterZones 8**.

That distribution is itself the headline: Requiem is overwhelmingly an *item and capability* mod.
Levels are a small fraction of the record volume.

## 1. NPC levels — the smaller half of the job

`Configuration.Level` is a discriminated union (`NpcLevel` with `Level:`, or `PcLevelMult` with
`LevelMult:` + `CalcMinLevel`/`CalcMaxLevel`). Counting Requiem's 2,702 `NPC_` overrides against the
winning vanilla record:

| Transition | Count |
|---|---|
| Vanilla `NpcLevel` → Requiem `NpcLevel` (already fixed) | **2,028** |
| Vanilla `PcLevelMult` → Requiem `NpcLevel` (**deleveled**) | **261** |
| Vanilla `PcLevelMult` → Requiem `PcLevelMult` (**left scaling**) | **68** |
| New to Requiem (339 `Requiem.esp` + 6 `ccbgssse001-fish.esm`) | 345 |

**The important number is 2,028.** Three quarters of the NPCs Requiem touches were *already*
fixed-level in vanilla — it is editing their stats and perks, not their level type. Only 261 records
are a level-type conversion. `[verified]`

### 1a. What Requiem deliberately leaves scaling

The 68 retained `PcLevelMult` records are, with a handful of exceptions, **the player's allies**:

- All 6 Hirelings (Belrand, Jenassa, Marcurio, Stenvar, Vorstag, Erik) — `x1 [10–40]`
- The Housecarls, including the HearthFire ones — `x1 [10–50]`
- The Companions (Aela, Farkas, Vilkas, Athis, Njada, Ria, Torvar)
- The standard follower roster (Faendal, Sven, Golldir, Annekke, Benor, Cosnach, Borgakh,
  Ghorbash, Lob, Ogol, Jzargo, Derkeethus, …)
- The Dawnguard followers (Agmaer, Beleval, Celann, Durak, Ingjard, Florentius)
- Plus a few template/ghost records (`DLC1EncVampireTemplate*`, the Kilkreath ghosts)

This is a **deliberate design rule, not an oversight**: a fixed-level follower is either useless at
level 40 or carries you at level 5. Requiem delevels the world and lets your companions grow with
you. `[verified]` — inferred from the membership of the set, which is unambiguous; Requiem publishes
no statement of the rule, so the *rationale* is `[unverified]`.

### 1b. What Requiem simply does not reach

**273 vanilla `PcLevelMult` NPCs are never overridden by Requiem.** Of those, 159 template their
`Stats` — so their own level field is inert anyway and the real level lives on the template. That
leaves **114 NPCs with live, untouched player-scaling**.

Those 114 are overwhelmingly quest one-offs and non-combatants: the Cidhna Mine prisoners (Braig,
Duach, Uraccen), the HearthFire bards, merchants (Elrindir, Glover Mallory, Niranye), the Dark
Brotherhood torture victims, the Sovngarde `MQ304LostSoul*` ghosts, corpses. A residue of genuine
combatants survives — `Estormo`, `Rulindil`, `Vald`, `dunIronbindBeemJa`, `MS06NecromancerLeader`,
and the `WEAdventurer*` world-encounter adventurers. `[verified]`

**Requiem is not a 100% deleveler, and after 13 years of development it still isn't.** It delevels
the systemic archetypes exhaustively and lets quest-specific one-offs slide. `[verified]`

### 1c. The ladder Requiem builds

Of the 2,633 fixed-level records, 979 own their level outright (the rest inherit via `TemplateFlags:
Stats`). The distribution runs far wider than vanilla's 1–50:

```
  0–4  187 │ 25–29  74 │ 50–54  77 │ 75–79  23
  5–9   76 │ 30–34  94 │ 55–59  24 │ 80–84  14
 10–14  89 │ 35–39  73 │ 60–64  22 │ 100+    7
 15–24 106 │ 40–49  86 │ 65–74  14 │
```

The top of the ladder is explicitly hierarchical and lore-ordered:

| Level | Who |
|---|---|
| 999 | `SummonAtronach*ThrallPotent` (a sentinel, not a real tier) |
| 250 | Alduin |
| 200 | Haknir Death-Brand |
| 150 | Ebony Warrior, Karstaag |
| 120 | Miraak, the named Dragon Priests |
| 100 | Durnehviir, Tsun, Soul Cairn Reaper, the undead dragon |
| 80 | Harkon, Isran, Ancano, Orchendor, Frost Giant, Soul Cairn Keepers |
| 77–79 | `EncDragon02Fire` / `EncDragon03Frost` |

Compare vanilla, where `AlduinBase` (`08E4F1:Skyrim.esm`) is `PcLevelMult ×1.2 [10–100]` — the only
fully player-scaled boss. Requiem pins him at **250**. `[verified]`

## 2. Leveled NPC lists — this is where deleveling actually happens

**The finding that reframes the whole problem.** Take the draugr ladder. Vanilla
`EncDraugr01/02/03…` NPC records are *already* `NpcLevel` — L=1, L=6, L=13 — and Requiem leaves
almost all of them unchanged. Vanilla's scaling for draugr does not live on the NPC at all. It lives
in the list that picks which draugr spawns.

`LCharDraugrBoss` (`042480:Skyrim.esm`) — vanilla has **13 entries across 7 gate levels**:

```yaml
- Data: {Level: 1,  Reference: 0DDD57:Skyrim.esm, Count: 1}
- Data: {Level: 6,  Reference: 0DDD58:Skyrim.esm, Count: 1}
- Data: {Level: 13, Reference: 0DDD58:Skyrim.esm, Count: 1}
  …
- Data: {Level: 60, Reference: 042482:Skyrim.esm, Count: 1}   # dragon priest
```

Requiem's override is **one entry**:

```yaml
Flags: [CalculateForEachItemInCount]
Entries:
- Data: {Level: 1, Reference: 0DDD5D:Skyrim.esm, Count: 1}
```

The draugr boss is now always the same tier, at any player level.
(`reference/mods/RequiemYaml/LeveledNpcs/LCharDraugrBoss - 042480_Skyrim.esm.yaml`) `[verified]`

### Across all 571 LVLN records

| Measure | Value |
|---|---|
| Overrides of vanilla lists | 328 |
| …with a **single** gate level | **328 / 328 (100%)** |
| Vanilla lists among them that *were* level-gated | 253 |
| …flattened to a single gate | **253 / 253 (100%)** |
| Total entries: vanilla → Requiem | 2,379 → 1,941 (**81.6%**) |
| New Requiem lists | 243 (191 single-gate) |
| Lists gated at `Level: 1` | 518 of 571 |

**Flatten the gate, keep the pool.** Entry count barely drops — 342 of 571 lists still hold 4+
entries. With every entry at level 1 and `CalculateFromAllLevelsLessThanOrEqualPlayer` set, all
entries are always eligible, so the list becomes a **uniform random draw over variants** instead of
a level ladder. Variety survives; progression dies. `[verified]`

The ~53 lists whose only gate sits above level 1 are nearly all Reqtificator-generated
`REQ_LChar_VoiceSpawns_*` variation lists, not deliberate player-level gates.

## 3. Leveled item lists — same technique, two extra tricks

| Measure | Value |
|---|---|
| Overrides of vanilla `LVLI` | 2,125 |
| …single-gate | 2,034 (**95.7%**) |
| Vanilla ones that *were* gated → flattened | 1,556 / 1,638 (**95.0%**) |
| New Requiem `LVLI` | 1,308 |

The 77 that keep gating are **93.5% `REQ_NULL_`-prefixed** — see below. Only **5 live lists** retain
any player-level gating at all, each with just two gates
(`LItemWeaponDwarvenBattleAxe`, `LItemWeaponDwarvenMace`, and three `SublistEnch*`). `[verified]`

### `REQ_NULL_` — neutralise, don't delete

Requiem renames records it has disconnected from the world to `REQ_NULL_*` rather than deleting
them (deleting would break every reference). Counts: 197 LeveledItems, 159 Npcs, 98 Armors, 85
Weapons, 63 LeveledNpcs. Their internal structure is left as-is because nothing reads them any more
— which is why almost all the "still gated" lists are `REQ_NULL_`. `[verified]`

### `Level: 9999` — disable an entry in place

`LItemWeaponDwarvenBattleAxe` (`0F4C84:Skyrim.esm`) keeps one entry at `Level: 1` and pushes two
others to `Level: 9999`, unreachable in a game capped far below that. The entry stays in the record
(so the diff and any dependent merge still see it) but can never roll. `[verified]`

## 4. Encounter zones — the negative result

**`CLAUDE.md` calls `ECZN` "probably the single most important record type for this mod". Requiem
disagrees.**

Vanilla ships 358 encounter zones (280 Skyrim + 2 Update + 19 Dawnguard + 57 Dragonborn).
Requiem ships **8**:

- 7 × `DLC2Book0[1-7]DungeonZone` (Apocrypha) — **identical to vanilla**, `MinLevel: 25`,
  `Flags: [NeverResets]`. Verified field-by-field against
  `reference/Base/05Dragonborn/EncounterZones/DLC2Book01DungeonZone - 0142B3_Dragonborn.esm.yaml`.
  These are ITMs, not edits.
- 1 × `REQ_Whiterun_HallOfTheDeadCatacombs` — a new zone with only `Flags: [NeverResets]`.

Not one of them sets a level for deleveling purposes. `[verified]`

The Reqtificator's *runtime* `ECZN` transformer confirms the intent — it is called
`OpenCombatBoundaries` and does exactly one thing:

```csharp
var result = input.Modify(record => record.Flags |= EncounterZone.Flag.DisableCombatBoundary);
```

(`core/Source/Reqtificator/Reqtificator/Transformers/EncounterZones/OpenCombatBoundaries.cs`) — it
lets enemies pursue you past the zone edge. Levels are never touched. `[verified]`

**Why this makes sense:** an `ECZN` min/max only *clamps* the level the leveled-list machinery
computes. Once every list is flat, there is nothing left to clamp. Encounter zones are a lever on
scaling, and Requiem removed scaling instead of tuning it.

## 5. Globals and game settings

- **The 12 vanilla `LevelGate*` `GLOB` records are untouched.** `LevelGateSpriggan`,
  `LevelGateGiant`, `LevelGateFalmer`, `LevelGateBear*`, `LevelGateTroll*`, `LevelGateHagraven`,
  `LevelGateIceWraith`, `LevelGateWisp*` all keep their vanilla values. Requiem's `Globals/` folder
  contains no `LevelGate*` record. Vanilla's one systematic player-level spawn gate survives.
  `[verified]`
- **Every difficulty multiplier is flattened to 1.0.** All ten `fDiffMultHPByPC*` /
  `fDiffMultHPToPC*` settings and both `fDiffMultXP*` settings are set to `1`. The difficulty slider
  no longer scales damage in either direction. `[verified]`
- **`fLeveledActorMult*` is left at vanilla** (Easy 0.33 / Medium 0.67 / Hard 1 / VeryHard 1.25).
  Requiem overrides none of them, so vanilla's per-placed-actor `LevelModifier` hand-tuning layer —
  the one `CLAUDE.md` measured on 5,685 of 10,504 placed actors — stays fully live. `[verified]`

That last pair is a coherent statement: **difficulty should come from the world's fixed structure
and from the designer's per-spawn tuning, never from a menu slider.**
