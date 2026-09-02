---
id: "projects/ehlnofey/design/requiem-method"
title: "The Requiem method, with Ehlnofey's twists — Phase 4 architecture"
slug: "requiem-method"
section: "projects/ehlnofey/design"
game: "skyrim"
kind: "design"
project: "ehlnofey"
mod: null
tags: ["ehlnofey", "deleveling", "design", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/design/requiem-method.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 1, "unverified": 1, "upstream": 0, "verified": 16}
lines: 587
content_sha256: "3f41e0070c2e4e919105833601bfe4f3f5fb600e079e3e5dbc186752318a4018"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# The Requiem method, with Ehlnofey's twists — Phase 4 architecture

**Status: DECIDED (2026-07-29), on branch `design/requiem-method`.** This supersedes
`implementation-strategy.md` §1's zone-first hybrid. Nothing in `src/` has changed yet.

Read first: `prior-art/requiem/plugin-analysis.md` (what Requiem actually does),
`probe-test-protocol.md` §§5–6 (what we measured in-game), `implementation-strategy.md` §6 (the
overworld census).

---

## 1. The decision

> **Delevel by flattening the leveled lists, as Requiem does — not by clamping encounter zones.**
> Difficulty becomes a property of the **archetype**, fixed once and legible from its name.
> Encounter zones survive in one role only: **container loot**, the one thing they are verified to
> govern and the one place bone 3 still lives.

| Layer | Mechanism | Scales with player? |
|---|---|---|
| **Actors** — who spawns | flatten the 269 gated `LVLN` to fixed rosters | **no** — anywhere, including the overworld |
| **Worn gear** — what they carry | truncate/flatten the outfit-reachable `LVLI` | **no** |
| **Container loot** — chests, urns, hoards | **keep vanilla gating + the 355 zone bands** | **no** — verified, zone-bound |
| **NPC levels** | all `PcLevelMult` → fixed, **followers included** | **no** |

Four moves, one exception, and the exception is the twist that keeps the mod's name honest.

---

## 2. Why — the evidence for the pivot

### 2.1 Encounter zones govern 0.3% of the outdoors

`[verified]`, `implementation-strategy.md` §6.1, full scan of the Tamriel worldspace:

| | count |
|---|---|
| Tamriel exterior cell files | 12,148 |
| …carrying an `EncounterZone` | **40 (0.3%)** |
| unzoned leveled actor refs | **3,512** vs 367 zoned |

A zone-first design governs interiors and almost nothing else. The remedy §6 proposed — flatten 65
lists, bolt zones onto 238 cells — is already half Requiem's method. Doing it everywhere is simpler
than doing it in one population and clamping in the other.

### 2.2 Worn gear scales with the player, and no zone can reach it

The probe separated the two loot tracks and they came back **opposite** `[verified]`:

| Track | Resolves against | Evidence |
|---|---|---|
| **Containers** | **the zone** ✅ | Test 3. Bleak Falls pinned to 4, player 45: vanilla arm gave a **glass dagger**; with `fSpecialLootMinPCLevelMult = 0` the same chest gave low-tier loot, **identical at player 1 and 45** |
| **NPC-worn gear** | **the player** ❌ | Test 2b. The Swindler's Den chief was **level 28 in both runs** but wore **iron at player 5, Nordic at player 45** |

There is no zone operand anywhere on an outfit's material list (`probe-test-protocol.md` §6.1,
mechanism traced end to end). Flattening the list is the only fix, and flattening the list is
Requiem's method.

**This kills `loot-model.md` §1's headline** — *"the tier ladder IS the material ladder, no truncation
pass needed"* — and with it the claim that bone 3 falls out of the difficulty map for free.

### 2.3 What the pivot costs, measured on this branch

Stated plainly, because it is real and it was not free. **Vanilla's dungeon rosters vary by *role*,
not by *tier*.** Census of all `Skyrim.esm` interior cells, resolving `PlacedNpc` bases through the
filename index `[verified]`, this branch:

| | |
|---|---|
| interior cells with placed NPCs | 498 |
| …placing leveled bases | 182 |
| distinct leveled bases in the vocabulary | 207 |
| distinct roster-sets across those 182 cells | **172** |

172 near-unique rosters looks like place topography — but the vocabulary says otherwise. The entire
draugr vocabulary is **role-shaped**: `Melee1H` · `Melee2H` · `Missile` · `Warlock` · `Berserker` ·
`Defender` · `Ambush` · `Boss` · male/female · helmet/no-helmet. There is no `LvlDraugrElite`, no
tier axis at all. **All tier information lives in the `LChar*` gate ladder — precisely what
flattening deletes.**

So under this architecture Bleak Falls Barrow and Volunruud get the same draugr. They differ in
*role mix*, not in danger. That is the price, it is paid knowingly, and §4.1–§4.2 are how it is
partly bought back.

### 2.4 Why the price cannot simply be bought back with rules

The obvious rescue is to fork each list per tier and repoint the placed references. SkyPatcher's
`reference/` module looked like the lever. **It is not, and the reason is in its source.**

`reference.cpp:15–19` exposes exactly three keys — `filterByRefs`, `filterByRefsExcluded`,
`replaceBaseObject`, `disable`. The swap is applied from a `Load3DREFR` hook
(`main.cpp:938–977`) `[verified]`:

```cpp
SKSE::GetTaskInterface()->AddTask([a_this, boundobj]() {
    if (a_this) {
        a_this->SetObjectReference(boundobj);
        a_this->Enable(false);          // ← force-enables the reference
    }
});
```

Two disqualifying problems for mass use:

1. **It force-enables every ref it touches.** Vanilla disables spawns deliberately and re-enables
   them through quest enable-parents — the four Ustengrav bandits in `probe-test-protocol.md` §4 are
   parented to `MQ105EnableDungeonMarker`. Applied to thousands of refs this turns on content the
   player has not unlocked.
2. **It fires at 3D load, not at reference init**, so whether it re-rolls a leveled actor at all is
   `[unverified]` and structurally doubtful — the list is resolved long before.

There is also no filter but the FormID list, so all ~2,147 LVLN-backed interior refs plus 3,512
overworld refs would need enumerating. **Repointing placed refs is therefore a plugin `ACHR` job or
nothing** — thousands of overrides with a heavy conflict surface, which is the option A ceiling this
project has rejected since Phase 2.

Conclusion: **archetype-level difficulty is not a shortcut, it is the architecture.** Plan around it
rather than budgeting to undo it.

### 2.5 What is *not* wrong with the design being replaced

Three of the four gating tests passed, and the parts they validated are kept in §4.1 rather than
discarded:

- **Test 2a passed outright.** Swindler's Den pinned to 30, observed at player 5 **and** 45,
  **identical both times** — levels 1 / 5 / 9 / 19 / 28. `[verified]`
- **Test 1 passed.** `LevelModifier: None` honours the zone. Zero records to fix.
- **Test 3 passed.** Zeroing the PC floor zone-locks special loot instead of disabling it.

---

## 3. The four moves, as Requiem does them

All `[verified]` in `prior-art/requiem/plugin-analysis.md`:

1. **Flatten the `LVLN` gate, keep the pool.** All 328 vanilla lists Requiem overrides become
   single-gate; 518 of 571 gate at `Level: 1`. Entry count only falls to **81.6%** of vanilla, so the
   list stops being a ladder and becomes a uniform random draw over variants.
   `LCharDraugrBoss`: 13 entries across 7 gates → **one entry**.
2. **Same for `LVLI`.** 2,034 of 2,125 overrides single-gate; only **5 live lists** keep any player
   gating at all.
3. **Convert `PcLevelMult` → fixed.** 261 converted. (Requiem retains 68; Ehlnofey does not — §4.3.)
4. **Do not use encounter zones for actors.** 8 records out of 358, none for levelling. Once the
   lists are flat there is nothing left for a zone to clamp.

### 3.1 The job, sized in our own decompile

Base + Dawnguard + Dragonborn, Hearthfire excluded per `difficulty-map.md` scope. "Real gate" = more
than one *distinct* entry `Level` on the record — CLAUDE.md's *count the entries, not the flag* rule.
`[verified]`, this branch:

| | records | **real-gated** | entries | entries in gated lists |
|---|---|---|---|---|
| `LeveledNpcs` | 681 | **269** | 4,022 | 1,836 |
| `LeveledItems` | 3,824 | **1,756** | 25,438 | 13,325 |

**269 `LVLN` is the actor job in full.** The 1,756 `LVLI` is a *ceiling*, not a target — see §5.1.

---

## 4. Ehlnofey's twists

### 4.1 Twist 1 — keep the 355 zones, for container loot only

Requiem drops encounter zones because they are inert once actor lists are flat. **They are not inert
for containers**, and test 3 is our own primary-source proof of it.

So Ehlnofey keeps the zone half of `implementation-strategy.md` §2 exactly as specified — the 355
`MinLevel == MaxLevel` bands from `difficulty-map.md` §7, plus `fSpecialLootMinPCLevelMult = 0` —
and **leaves container leveled-item lists gated**. The result:

```
actors   :  flat list           → fixed by ARCHETYPE, everywhere, no zone needed
worn gear:  flat list           → fixed by ARCHETYPE
containers: gated list + zone   → fixed by PLACE        ← bone 3 lives here
```

Why this is the right asymmetry:

- **It is free.** The zones are already specified and generated; `build-difficulty-map.py` needs no
  change. `difficulty-map.md` stops being dead work.
- **It is verified**, which is more than can be said for any alternative bone-3 mechanism.
- **Containers are where "reward follows place" is actually legible to a player.** A Nordic tomb's
  boss chest is the thing you remember; the exact tier of the third draugr in a corridor is not.
- **The overworld objection does not apply.** Unzoned exterior containers are a rounding error next
  to unzoned exterior *actors*, which this architecture fixes by flattening anyway.

**Consequence to accept:** `fLeveledActorMult*` (Easy/Medium/Hard/VeryHard, `tiers.md` §4) becomes
**inert for actors** — the modifier multiplies a leveled-list lookup level, and flat lists have
nothing to look up. Those two GMST overrides are **dropped from the plugin**. Vanilla's hand-tuning
layer on 5,685 placed actors is a casualty of flattening; that is Requiem's trade too.

### 4.2 Twist 2 — the tier ladder moves from places to archetypes, and the lore already wrote it

`tiers.md`'s **T1–T7 = 4 / 8 / 14 / 21 / 30 / 40 / 50** survives intact. What changes is what it
indexes: **a creature family's rung, not a dungeon's.**

This is the one place the pivot makes the mod *more* legible, not less, and `lore-constraints.md`
already identified the mechanism: **vanilla's display names are a lore-ordered power hierarchy.**

| Family | The ladder vanilla already ships |
|---|---|
| Draugr | Draugr → Restless Draugr → Wight → Scourge → Deathlord |
| Dremora | Churl → Caitiff → Kynval → Kynreeve → Markynaz → Valkynaz |

Under the zone architecture those names were only *correlated* with power — the player met a Wight
because a zone was tier 4. **Under flattening the name becomes the fact.** A Draugr Scourge is
level 30 in Bleak Falls Barrow, in Labyrinthian, and in a random barrow at the edge of the map,
forever. Bone 2 (*danger is legible*) is served by the enemy's name rather than by the dungeon's, and
a name travels with the enemy in a way a zone never did.

**Authoring rule:** every flattened `LVLN` leaf is assigned a tier, and the tier must agree with the
display name of everything in the pool. Where vanilla's ladder has more rungs than the pool needs,
collapse; where a name implies a rung the pool does not hold, the pool is wrong. `lore-constraints.md`
is the arbiter, not convenience.

### 4.3 Twist 3 — followers are deleveled too, at hand-set lore levels

Requiem retains 68 `PcLevelMult` NPCs, almost all followers, housecarls and hirelings. **Ehlnofey does
not take that exception.** Bone 1 applies literally: nothing in the world scales, and a companion is
in the world.

This is a real departure and it has a real consequence — a follower fixed at 30 trivialises the early
game, and one fixed at 15 is dead weight late. **Turn that into the design rather than absorbing it:**

- Set each follower's level from **role and lore**, not from balance. A Whiterun housecarl is a
  competent hold soldier; Aela is a veteran of the Companions; Marcurio is a working mage for hire.
- **Choosing a follower becomes a decision with consequences** — an early-game character genuinely
  benefits from a strong companion, and outgrows them. That is the same "fixed world, legible
  danger" contract applied to allies.
- The roster is small and already enumerated: `prior-art/requiem/plugin-analysis.md` §1a lists the
  68 by name. Use it as the work list, then invert the verdict.

Everything else in the `PcLevelMult` population (~454 actors: guards, soldiers, hunters, Nightingales,
`WE*` adventurers) converts by **SkyPatcher rule**, not by override — `filterByPCLevelMult=true` is a
predicate that also catches NPCs from other mods and future patches, where 454 overrides would only
be a snapshot. That argument from `implementation-strategy.md` §4 is unaffected by the pivot and
stands. The follower set is the part done by hand, because hand-set levels are the point.

### 4.4 Twist 4 — adopt Requiem's three record conventions now

Free, pure record technique, no patcher (`prior-art/requiem/lessons-for-ehlnofey.md` §4):

| Convention | Use |
|---|---|
| **`Level: 9999`** | disable an entry in place. It stays in the record so diffs and merges still see it, but can never roll. Better than deletion for the truncation pass |
| **`EHL_NULL_` rename** | retire a record without deleting it — deletion breaks every reference. Requiem has 197 such `LVLI`, 63 `LVLN` |
| **Weighting by duplicate entries** | Skyrim has no weight field, and a flat pool makes every variant equally likely. Repeat the entry N times to weight it |

The third is not optional here. **Flattening costs variety** — Requiem had to build a whole actor
variation generator to pay it back. Weighting is how a flattened bandit pool stays mostly grunts with
the occasional chief instead of a coin flip. Budget for it in the first archetype, not the last.

> **Note the mechanism, which is easy to get wrong.** Weighting is *literal entry duplication*, not a
> `Count` field: `Count` is how many actors an entry spawns, and `CalculateForEachItemInCount` rolls
> each of them separately. Requiem's `_CLI_` convention writes `Count: 5` as authoring shorthand and
> its **patcher unrolls it into five entries** (`lessons-for-ehlnofey.md` §4). Ehlnofey has no
> patcher, so it writes the duplicates out — costs bytes, needs nothing.

---

## 5. Scope control — the loot job is 202 lists, not 1,756

### 5.1 The reachability census — DONE (2026-07-29, this branch)

Under Twist 1, **container-only lists keep their gates and need no edit.** Only lists reachable from
an **outfit or an NPC `Items:` block** are bone-1 leaks. `arch-docs/design/lvli-reachability.ps1`
measures the split: roots are NPC `Items:` plus `DefaultOutfit`/`SleepingOutfit` → `OTFT Items:`
(actor side) and `CONT Items:` (container side), closed transitively over `LVLI → LVLI` edges, load
order last-wins. All `[verified]`:

| gated `LVLI` (1,754 of 3,817) | count |
|---|---|
| reachable from **both** actors and containers | **986** |
| container-only — **no edit** | 410 |
| actor-only | 181 |
| unreached from either root | 177 |

Taken at face value that says 1,167 lists to fix. **It massively overstates the job**, because the
actor side does not need every *reachable* list rewritten — only the ones an outfit or inventory
points at **directly**. Everything below that is subtree, fixed implicitly once the entry point is
flattened.

**The boundary is 202 lists** `[verified]`:

| | count | treatment |
|---|---|---|
| gated lists an actor references **directly** | **202** | |
| ↳ actor-only — **flatten in place** | **126** | free; no fork, no repointing |
| ↳ also container-reachable — **fork or judge** | **76** | §5.2 |

That is the number the whole loot half was waiting on, and it is closer to the Swindler's Den trace's
five lists than to 1,756. (`probe-test-protocol.md` §6.1: the entire bandit-chief wardrobe ran
through `LItemBanditCuirass` `037C22`, `LItemBanditBoots` `037C23`, `LItemBanditGauntlets50`
`037C25`, `LItemBanditShield20` `0C0196`, plus the already-flat `LItemBanditWeapon1H` `037C1B`.)

### 5.2 The 76 shared lists split three ways, and only one band needs forking

Naming them settles it. Of the 76, **only the generic material ladders actually conflict** — the rest
are already scoped to an archetype or a category, so flattening them in place is correct on *both*
sides. `[verified]`, with the count of NPCs holding a direct reference:

| Band | Lists | NPC refs | Treatment |
|---|---|---|---|
| **Gold** — `LootBanditGold` (303), `LootBanditGoldBoss` (71), `LootCWImperialsGold`, `LootCWSonsGold`, `LootDraugrGold*`, `TGRewardGold` | 7 | **383** | **flatten in place.** A fixed purse and a fixed strongbox are both correct |
| **Consumables & sundries** — potions (168), soul gems (101), `LItemGems`, jewelry, minerals, hunter parts, vendor stock, poisons | ~39 | ~270 | **flatten in place.** Category-scoped, no tier meaning |
| **Material ladders** — `LItemWeaponDagger` (67), `LItemWeaponMace` (52), `LItemArmorShieldHeavy` (19), `LItemArrowsAll` (19), `LItemStaffsAll` (15), `LItemWeaponDaggerBest` (14), `LItemWeaponBow`/`Sword`/`WarAxe`/`Warhammer`/`BattleAxe` + `…Town`/`…Best` variants, `LItemEnchWeapon*`, `LItemArmor*`, `LItemSoldierSons*` | **~30** | **~250** | **FORK.** These carry the entire gear leak |

So the real fork set is **~30 lists**, not 76 — and the residual cost is the **~250 NPC records**
holding a direct `Items:` reference to one of them.

### 5.3 What can and cannot be done by rule — read from source

`[verified]` against `reference/mods/SkyPatcherSrc/npc.cpp`, this branch:

| Need | Verdict |
|---|---|
| Repoint an NPC's **outfit** at a forked list | ✅ `outfitDefault=` (`npc.cpp:138`), `outfitSleep=` (`:140`). **This closes `probe-test-protocol.md` §6.3's open question** — SkyPatcher *can* set `DefaultOutfit`. Only **16 of 605** outfits reference a fork list, so this half is trivial |
| Repoint an NPC's **inventory** (`Items:`) | ❌ **no key exists.** `npc.cpp` has `outfitDefault`, `outfitSleep`, `deathItem` and nothing else item-shaped. The ~250 must be **plugin `NPC_` overrides** |
| Flatten a list | ✅ `leveledList/` `clear` + `addToLLs` + `calcLevelAndEachItem` |

**Do not invert the fork direction.** Forking the *container* side instead — leaving the shared list
flat for actors and giving chests a gated copy — looks cheaper until it is measured: the 76 sit
*below* container sublists, so their upward cone is **521 `LVLI`** and **267 of 571 containers**
reach one. Forking downstream of 521 lists is far worse than 250 NPC overrides. `[verified]`

### 5.4 Two more subtractions

- **The 23 already-flat overworld lists** need nothing — `LCharSoldierImperial`, `LCharSoldierSons`
  (all 943 Civil War refs) and `LCharAmbientCreatures` (623 refs). The single biggest block of
  overworld actors was never a scaling problem `[verified]`.
- **Biome partitioning is already done.** `LCharAnimalForestPredator`, `…MountainSnowPredator`,
  `…CoastSnowPredator`, `LCharAnimalHills`, `LCharMudcrab` (209 refs) and kin already split wildlife
  by biome, so flattening each list *in place* yields fixed **and** regionally varied wildlife with
  zero new records `[verified]`. This is the population where Requiem's method is strictly better
  than the zone architecture, and it retires §6.4's 238-cell bolt-on for the wildlife half outright.

### 5.5 The loot half, costed

| Work | Size |
|---|---|
| Flatten in place — 126 actor-only + ~46 safe shared | **~172 `LVLI` overrides** |
| Fork the material ladders | **~30 new `LVLI`** (first real FormID block) |
| Repoint outfits | 16 — **by rule**, `outfitDefault=` |
| Repoint NPC inventories | **~250 `NPC_` overrides** — plugin only |
| Container-only gated lists | **410 — untouched**, the zone supplies their level |
| Unreached gated lists | 177 — see §8.5 |

**~450 records total for the entire loot half.** Against Requiem's 2,125 `LVLI` overrides and MLU's
400-list truncation pass, that is a small mod — and it is small precisely *because* Twist 1 keeps the
zones, which lets 410 lists keep their gates untouched.

### 5.2 Two more subtractions

- **The 23 already-flat overworld lists** need nothing — `LCharSoldierImperial`, `LCharSoldierSons`
  (all 943 Civil War refs) and `LCharAmbientCreatures` (623 refs). The single biggest block of
  overworld actors was never a scaling problem `[verified]`.
- **Biome partitioning is already done.** `LCharAnimalForestPredator`, `…MountainSnowPredator`,
  `…CoastSnowPredator`, `LCharAnimalHills`, `LCharMudcrab` (209 refs) and kin already split wildlife
  by biome, so flattening each list *in place* yields fixed **and** regionally varied wildlife with
  zero new records `[verified]`. This is the population where Requiem's method is strictly better
  than the zone architecture, and it retires §6.4's 238-cell bolt-on for the wildlife half outright.

---

## 6. Order of work

**Step 1 — the outfit-reachability census.** ✅ **DONE** (§5.1–§5.5). The loot half is ~450 records.

**Step 2 — assign every archetype family its tier** (§4.2). ✅ **DONE** — `archetype-tiers.md`.
~67 lists and ~76 NPC records for the whole actor half. It also closes `lore-constraints.md` §6.1:
the Dremora, Warlock and Vampire ladders each land 1:1 on T1–T7, so the tier number is a real
cross-archetype currency and "is a Draugr Scourge worse than a Forsworn Ravager" becomes answerable.

**Step 3 — delete `src/ExampleMod/` and `src/EhlnofeyProbe/`.** ✅ **DONE.** `build/staging/Example
Mod/fomod/` is **kept deliberately** — CLAUDE.md's FOMOD-image gotcha cites it as the only
confirmed-working worked example, and `build.ps1` iterates `manifest.releases` only, so an unreferenced
staging tree is inert.

**Step 4 — scaffold `Ehlnofey.esp`.** ✅ **DONE.** ESL-flagged, four masters, own FOMOD, own manifest
release. Empty scaffold built clean before any record was added.

**Step 5 — the constants.** ✅ **DONE — 19 records** (not 20; see §7.1 of `archetype-tiers.md`):
`fSpecialLootMinPCLevelMult` → 0, the 12 `LevelGate*` globals → 1, and 6 named capstones converted
from `PcLevelMult` to fixed levels. The two `fLeveledActorMult*` overrides are dropped (§4.1), and
`EncBandit04TemplateMelee` turned out to need no record at all.

Verified four ways: `build.ps1` clean · `build.ps1 -CheckFomod` parity OK · `Test-RecordYaml.ps1`
20 files no issues · **Spriggit round-trip byte-identical on content**. Every FormKey reference was
also machine-checked against the declared master list — all resolve, no HearthFires leak.

**Not verified: the xEdit pass and the launch.** See §9.

### Steps 6–9 were replaced by the extract (2026-07-30)

Scope was cut to **one deliverable: a copy of Requiem with only the deleveling in it**. Steps 6–8 as
written above assumed Ehlnofey would re-derive every flat list from `reference/Base/` by rule — ~962
records of original authoring. It does not have to: Requiem's flat records are overwhelmingly built
from **vanilla FormKeys only**, and an override keeps its defining master's FormKey suffix, so for
most records the job is a file copy. `src/Ehlnofey/extract-requiem.ps1` does it in five buckets.

> **Release note.** Verbatim-copied records make the plugin a derivative of Requiem — fine to build
> and play privately, but publishing needs their permission. Bucket D, the part that most defines
> the mod's character, can't be copied anyway and stays original Ehlnofey work.

**Step 6 — the extract.** ✅ **DONE — 2,845 records.**

| | | |
|---|---:|---|
| **A** copied verbatim | 1,896 | `LVLN`/`LVLI` whose every FormKey is one of our four masters |
| **B** stripped | 173 | `LVLI` that also referenced Requiem-only gear; those entries dropped |
| **C** vanilla flatten | 259 | Requiem never covered it, or B emptied it: vanilla record, `Level` → 1 |
| **D** provisional `LVLN` | 66 | nothing copyable — see below |
| **E** level graft | 437 | vanilla `NPC_` record, Requiem's `Configuration.Level` only |
| *skipped* | 1,900 | not ours: Requiem's own records, HearthFires, Creation Club, USSEP |
| *skipped* | 307 | ITMs |

Closure is the result that made this viable: of every vanilla `LVLN` reachable from Requiem's flat
lists **0 remain player-gated**, and for `LVLI` only 7. Of the **257** gated vanilla `LVLN` in the
whole game Requiem covers **249**. There is no `REQ_NULL_` contamination — 0 entries in live lists
point at a record Requiem neutered.

Deliberately **not** taken: Requiem's perks, spells, magic effects, weapons, armour, crafting and
economy; its 8 encounter zones (none is a level record); its `fDiffMultHP*`/`fDiffMultXP*`
difficulty-slider flattening. Requiem's `HealthOffset` and its dropped `AutoCalcStats` flag are its
capability overhaul, so bucket E takes the level field and nothing else. The ~150 EditorIDs Requiem
renamed into its own taxonomy (`LItemWeaponSword` → `REQ_LI_Loot_Weapon_Sword`) are restored to the
vanilla name; `REQ_NULL_` / `REQ_LEGACY_` / `REQ_BashedPatch_` records are dropped, since
disconnecting a record is not deleveling.

Every entry in every leveled list is now `Level: 1` or the `9999` disable sentinel. Four residual
Requiem gates were flattened for bone 1: `SublistEnchElvenBattleaxeStamina` (25),
`SublistEnchOrcishSwordAbsorbHealth` (11), `SublistEnchOrcishSwordTurn` (11) and
`DLC2LCharDragonAny` (**55** — Requiem gates Solstheim's any-dragon list behind level 55; flattening
it means those dragons are reachable from level 1, which is the design, but it is a judgement call).

Verified: `build.ps1` clean · `Test-RecordYaml.ps1` 2,846 files no issues · **round-trip byte-stable**
· **zero new FormIDs** · masters exactly Skyrim/Update/Dawnguard/Dragonborn. **Not launched.**

**Step 7 — bucket D, the 66 `LVLN` that could not be copied — plus 7 more.** ✅ **DONE — `src/Ehlnofey/author-bucket-d.ps1`.**

Requiem's versions delegate to `REQ_LChar_VoiceSpawns_*` sublists that are Requiem-only **and still
player-gated** (1/2/5/8/9/10), so nothing came across and the extract left a naive vanilla flatten.
That flatten was actively wrong for the biome lists — §4.1.1 shows it inherits the level-35
density-ramp mix (`BearCave ×7` dominant), the most dangerous composition vanilla ever produces.

The rosters are now authored from `archetype-tiers.md` §3.1 / §4 / §4.1 in three shapes, every one a
**filter + weighting of the vanilla record** — no level is ever written onto an actor (rule 1), and
weighting is literal entry duplication (rule 2):

| Shape | Used for | Count |
|---|---|---:|
| `Cap` — keep vanilla's own mix frozen at the tier's reference level (§4.1.2 verbatim) | the 8 flagged biome predator lists, the Vigilant sublists, `LCharVampireCompanionFrost` | 11 |
| `Gates` — explicit per-gate weights (§3.1, §4) | the bandit ladder and bosses, the 3 unflagged ambient lists, the species-substitution lists | 51 |
| `Refs` — explicit per-reference weights, where one gate holds several species | `LCharMudcrab` | 1 |
| *dropped* — already a single gate at 1 in vanilla, so an override would be an ITM (§4.1.3) | `LCharWolf`, `LCharDeer`, `LCharElk`, `LCharSkeletonMeleeMixed`, `LCharBanditMeleeAny`, `SubCharVigilantOfStendarr01`, the 3 prey lists | 9 |

Verified entry-for-entry against the design tables: **all nine biome rosters reproduce
`archetype-tiers.md` §4.1.2 exactly**, `LCharBanditMelee1H` is `Runt ×1 · Outlaw ×4 · Thug ×3 ·
Highwayman ×1`, and the per-voice leaves keep their 1H/2H variant variety inside each weight. Two
table-vs-prose conflicts were resolved and recorded in `archetype-tiers.md` §4.1.2
(`LCharAnimalSnowFields`' out-of-band Ice Wraith; `LCharMudcrab`'s duplicated row).

**Amended 2026-07-30 after the first play report**, which found the Swindler's Den chief rolling
level 6 to 28 — the naive flatten's signature, already gone from the shipped build, but the trail led
to two real defects:

1. **`LCharBanditBoss` and its 9 per-voice siblings are pinned to level 28**, not banded 16/21/28.
   Every rung of that ladder displays the *same* name, so a 75% power swing was invisible — which
   Twist 2 forbids. The naming test and the per-family verdicts are now `archetype-tiers.md` §3.1.1.
   **Four boss families still fail it** (Forsworn, Warlock, Thalmor, Vampire) and are a decision not
   yet taken. Draugr and Falmer pass — their rungs are separately named.
2. **7 lists the extract left as a naive vanilla flatten are now authored** — `LCharBanditOnly`
   `NordM`/`RedguardF`/`OrcM`, `LCharBanditMeleeKhajiitM`, `LCharBanditMissileKhajiitM`,
   `LCharBanditWizardOmit01` (all §3.1's bandit roster) and `LCharOrcMelee` (§3.1's own row:
   Outlaw ×1 · Thug ×3 · Highwayman ×3 · Plunderer ×1). These are 6 of the **8 uncovered `LVLN`**
   §"closure" lists — Requiem never overrode them, so bucket C flattened all six rungs and left
   Plunderer and Marauder reachable in lists §3.1 caps at Highwayman. `LCharGargoyle` and
   `dunClearspringTarnLCharPredator` are the 2 still unaddressed.

**Build order is `author-constants.ps1` → `extract-requiem.ps1` → `author-bucket-d.ps1` →
`author-names.ps1`**, then the round-trip. `bucket-d-provisional.txt` is regenerated by the extract
and is the *input* list, not a to-do.

**Step 7b — `author-names.ps1`** (added 2026-07-30) is the only generator that writes a display name
and nothing else. It exists because the level-1 bandit rung ships nameless and inherits "Bandit" from
the family root; naming it "Bandit Runt" is one `FULL` on **all 44 records in the rung**. It runs
**last** because it writes `NPC_` records the extract also touches.

Naming only the three `EncBandit01Template*` records — the exact slot the other rungs use — was
tried first and **did not work in game**, for reasons still unknown. See `archetype-tiers.md` §3.1
for the evidence that ruled out a stale file and a load-order conflict. Naming all 44 sidesteps the
question entirely.

**Step 8 — launch.** Guardrail 6. Level-1 character, `coc bleakfallsbarrow01`; then
`player.setlevel 40` and enter a *different* uncleared barrow. Same spawns, same loot tier, or the
architecture is not doing what the census says it is.

**Step 9 — followers by hand** (§4.3): the 65 `PcLevelMult` allies Requiem deliberately leaves
scaling and therefore supplies no level for, plus the 114 vanilla `PcLevelMult` NPCs Requiem never
reaches. Then the rule linter (`implementation-strategy.md` §8) if any SkyPatcher rules survive.

> **Re-running the extract.** `extract-requiem.ps1` regenerates from `reference/`, so its output is
> pre-round-trip: Spriggit normalises field order, and collapses the multi-language `Values:` block
> vanilla `NPC_` records carry into a single `Value:`. After any re-run, **deserialize, re-serialize,
> and adopt Spriggit's output as the committed source** — the same rule as CLAUDE.md's field-order
> gotcha. The committed tree is already in that normalised form.

---

## 7. What this supersedes

| Document | Effect |
|---|---|
| `implementation-strategy.md` §1 | ❌ the zone-first hybrid is replaced. §§2.2–2.4, §4, §8 survive |
| `implementation-strategy.md` §2.1 (355 zones) | ✅ **kept**, re-purposed to container loot (§4.1) |
| `implementation-strategy.md` §2.2 (`fLeveledActorMult*`) | ❌ **dropped** — inert once lists are flat |
| `implementation-strategy.md` §6 (overworld) | ⚠️ wildlife half **superseded** by §5.2; humanoid half moot — flattening covers it |
| `loot-model.md` §1 "no truncation pass needed" | ❌ **dead** (§2.2) |
| `difficulty-map.md` §7 (the 355 assignments) | ✅ **kept in full** — now the loot map |
| `tiers.md` T1–T7 ladder | ✅ **kept**, re-indexed from places to archetypes (§4.2) |
| `lessons-for-ehlnofey.md` §5 (ally exception) | ❌ **explicitly rejected** (§4.3) |
| Requiem's `fDiffMult*` → 1.0 | ❌ **not adopted** — removing the player's difficulty slider is out of scope for a mod that is not a combat overhaul |
| CLAUDE.md *Implementation strategy* + *Current phase* | needs rewriting once this lands |

---

## 8. Open risks

1. **Variety collapse.** The measured cost of flattening is that every draw becomes identical.
   Requiem's entry count held at 81.6%, but it also built a generator to restore variation. Twist 4's
   weighting is the mitigation; whether it is sufficient is only answerable in-game at step 7.
2. **Archetype tiering is curation, not an algorithm.** `Changelog.md` is 2,491 lines of one-off
   delevels and Requiem *still* leaves 114 NPCs scaling after thirteen years. Plan for a long tail and
   a coverage-audit script; do not plan for a clean sweep.
3. **Container gating assumes zone-bound resolution holds for ordinary chests**, not just the
   `SpecialLoot`-flagged boss roll that test 3 exercised. `[community]`, worth one cheap confirmation
   at step 6 — open an ordinary urn in a pinned zone at two player levels.
4. **Deleveled followers are untested as a design.** §4.3 argues it is a feature; nobody has played
   it. Revisit after step 9 with actual play, and treat reverting to Requiem's exception as a live
   option rather than a defeat.

### 8.5 The 177 unreached gated lists

Gated `LVLI` that neither an NPC/outfit nor a container references. Sampling them shows what they
are: quest rewards (`LvlQuestReward*`, `DLC2MQ06MiraakRewardMaskL`), death items
(`DLC1DeathItemGargoyle`), dungeon-specific enchanted sets (`dunSilentMoonsLItemEnchSteel*`),
`SublistEnch*` fragments, and unique gear (`LItemWeaponNightingaleSword`, `TGLvlItemNightingaleBoots`).

They are reached from roots this census does not walk — `QUST` reward packages, `FLST` form lists,
`NPC_` death items, and leveled items placed directly as world references. **Most are one-offs where
a fixed level is the right answer anyway**, but the set has not been individually triaged. Triage it
during step 8; it is a read, not a redesign, and `deathItem=` is rule-expressible (`npc.cpp:142`).

---

## 9. Environment blockers found at step 5

Neither is a defect in the mod; both stop guardrail 6 from being satisfied and need the user's input.

1. **`tools.json` points at a game install with no DLC.** `gameDataDir` is
   `claudemoddev/modlist/Game Root/Data`, which holds **only `Skyrim.esm`** — a tooling stub, not a
   playable install. Ehlnofey masters `Update`, `Dawnguard` and `Dragonborn`, so nothing can load it
   there. A full set does exist at `C:/modding/modlists/LoreRim/Stock Game/Data` (all five masters).
   **Decision needed:** repoint `gameDataDir` (and possibly the other `claudemoddev` tool paths) at
   LoreRim, or install the DLC into the stub. Not changed unilaterally — `papyrusCompiler`,
   `creationKit`, `champollion` and the xEdit tools all point into `claudemoddev`, and moving one
   path without the others is how a workspace ends up half-configured.

2. **`SSEEditQuickAutoClean` blocks on a GUI dialog** even with `-autoload`. The same risk applies to
   the *Check for Errors* pass on this build. The run was killed and the staged plugin and its backup
   removed from the LoreRim Data folder. This is why the `xedit-audit` skill was **deleted from the
   workspace** — headless xEdit does not work here, so the skill could never do its job.
   **Consequence: no xEdit audit has ever been run against Ehlnofey.esp.** The substitute checks
   above are strong for *this* slice — every record was copied verbatim from `reference/`, so its
   FormKeys are valid by construction — but they will not stay sufficient once step 8 authors records
   by transformation rather than by copy.

## Sources

`prior-art/requiem/plugin-analysis.md` §§1–5 · `prior-art/requiem/lessons-for-ehlnofey.md` §§2–6 ·
`prior-art/skypatcher.md` §§2, 4.2, 5 · `design/probe-test-protocol.md` §§4, 5, 6, 6.1 (in-game
results) · `design/implementation-strategy.md` §§2, 4, 6, 7.1 · `design/loot-model.md` §§1–4 ·
`design/tiers.md` §4 · `design/difficulty-map.md` §7 · `world/lore-constraints.md` ·
`reference/mods/SkyPatcherSrc/reference.cpp`, `main.cpp:938–977` (§2.4, read this branch) ·
`reference/Base/01Skyrim/Cells/` (§2.3 roster census, run this branch) ·
`reference/Base/{01Skyrim,02Update,03Dawnguard,05Dragonborn}/{LeveledNpcs,LeveledItems}/` (§3.1).
