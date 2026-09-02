---
id: "projects/ehlnofey/design/loot-model"
title: "Loot model — reward follows place"
slug: "loot-model"
section: "projects/ehlnofey/design"
game: "skyrim"
kind: "design"
project: "ehlnofey"
mod: null
tags: ["ehlnofey", "deleveling", "design", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/design/loot-model.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: "Phase 3, document 4"
confidence: {"author": 0, "community": 3, "unverified": 4, "upstream": 0, "verified": 8}
lines: 274
content_sha256: "fcd1bc8d3c04160631ab1f86c056e57780da159d5d3e2feb2b75758ded69b9d2"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Loot model — reward follows place

**Phase 3, document 4.** What the player finds, where, and what leaves the leveled lists.

Bone 3: *good loot exists because of **where** it is — a Nordic tomb, a Dwemer ruin, a dragon's hoard,
a named boss — never because the player happened to be level 40.*

Read `tiers.md` and `difficulty-map.md` first. Confidence marks as elsewhere.

---

## 1. The headline: the tier ladder *is* the material ladder

`engine-behaviour.md` §3 established that leveled-item lists resolved inside a zone's cells draw
against the **zone level**, the same input as the actors. So once `difficulty-map.md` fixes a zone at
`N`, the loot in it is fixed too — with no list edits at all.

The question is whether the resulting distribution is any *good*. It is, and by a margin that was not
designed for. Vanilla's canonical weapon ladder, `LItemWeaponSwordBest` (`0571AA:Skyrim.esm`),
resolved at each tier's zone level `[verified]`:

| Tier | `N` | gate hit | Material |
|---|---|---|---|
| T1 | 4 | 1 | **Steel** |
| T2 | 8 | 6 | **Orcish** |
| T3 | 14 | 12 | **Dwarven** |
| T4 | 21 | 19 | **Elven** |
| T5 | 30 | 27 | **Glass** |
| T6 | 40 | 36 | **Ebony** |
| T7 | 50 | 46 | **Daedric** |

**Seven tiers, seven materials, one rung each, no collisions.** The tier ladder was derived from the
draugr *actor* gates (`tiers.md` §3) with no reference to loot, and it lands exactly on the vanilla
material ladder. That is a strong independent check on the ladder — Bethesda spaced its gear gates
and its actor gates on the same underlying curve, and Ehlnofey inherits both by choosing one.

This is not one lucky list. Across the **162** multi-rung gear lists in `Skyrim.esm`, **89 select six
or seven distinct rungs** over T1–T7, and every core `…Best` / `…Special` list hits all seven
`[verified]`:

| List | Gates | T1 → T7 selects |
|---|---|---|
| `LItemArmorCuirassLightBest` | 1, 6, 12, 19, 27, 36, 46 | 1 · 6 · 12 · 19 · 27 · 36 · 46 |
| `LItemArmorCuirassHeavyBest` | 1, 6, 12, 18, 25, 32, 40, 48 | 1 · 6 · 12 · 18 · 25 · 40 · 48 |
| `LItemArmorBootsLightBest` | 1, 6, 12, 19, 36, 46 | 1 · 6 · 12 · 19 · 19 · 36 · 46 |
| `LItemArmorGauntletsHeavy` | 1, 6…9, 12, 18, 25, 32, 40, 48 | 1 · 8 · 12 · 18 · 25 · 40 · 48 |

The exception is the `…Town` family (`LItemArmorCuirassLightTown` and kin), which uses dense low gates
(1, 4, 5, 6, 7, 12…15, 18…21) and saturates by T4. Those are civilian clothing lists for settlement
NPCs and it does not matter that they flatten out.

> **The consequence is large and it is a cost saving.** MorrowLoot Ultimate had to truncate 400 of its
> 473 overridden lists (`morrowloot.md` §3) to keep Daedric out of the random economy. **Ehlnofey does
> not**, because MLU's zones still scaled inside a `[38–53]` band while Ehlnofey's do not. Under a
> fixed world the level gate on a leveled list stops being a *player* gate and becomes a **place**
> gate automatically. Bone 3 is satisfied by the difficulty map, not by a loot pass.

### What that means concretely

Daedric (gate 46) requires a lookup level ≥ 46. From `difficulty-map.md`:

| Source of a ≥46 lookup | Where |
|---|---|
| T7 container (`N` = 50) | **1 zone** — Castle Volkihar |
| T6 `VeryHard` placed actor (40 × 1.25 = 50) | 14 zones, boss placements only |

So Daedric weapons and armour leave the random economy **without a single list being edited** —
reachable in essentially two places, both apex, both bosses. Ebony (gate 36) becomes a T6 material,
Glass (27) a T5 material. That is precisely the distribution MLU spent 746 records buying.

---

## 2. The three loot tracks

Not all loot resolves the same way, and only the first is settled by the difficulty map.

| Track | What | Resolves against | Status |
|---|---|---|---|
| **A. Zone loot** | chests, urns, sacks, boss chests in a zone's cells | **the zone level** `[community]`, now with primary-source support (§4) | ✅ **done** by `difficulty-map.md` — no work |
| **B. NPC gear** | outfits and inventories on the actors themselves | **contested — see §3** | ⚠️ **the open question** |
| **C. Hand-placed uniques** | named artefacts on pedestals and in bosses' hands | nothing — they are static | ✅ already bone-3 compliant; §5 |

### The real size of the list job

`overview.md` §6 and `enemy-taxonomy.md` §4 both frame the loot job as *"1,959 of 3,075 `LVLI` are
player-gated"*. That figure is the count of lists carrying
`CalculateFromAllLevelsLessThanOrEqualPlayer`, and **the flag count is not the gate count**. Census
`[verified]` over `reference/Base/01Skyrim/LeveledItems/`:

| Measure | Count |
|---|---|
| `LVLI` records total | 3,075 |
| carrying `CalculateForEachItemInCount` | 2,174 |
| carrying `CalculateFromAllLevelsLessThanOrEqualPlayer` | 1,959 |
| carrying `UseAll` | 280 |
| carrying `SpecialLoot` | 86 |
| **with any entry gated above level 1** | **1,382** |
| **with more than one distinct entry level (a real ladder)** | **1,378** |

**1,693 lists — 55% — are flat variety pools with no level gating whatsoever**, carrying the
calculate-from-all flag over entries that are all level 1. `LItemBanditCuirass` (`037C22`) is *not*
one of them (it gates at 1/6/7/8/9/19…28, as `enemy-taxonomy.md` §4 says), but a majority of the
corpus is.

So the *upper bound* on the leveled-item job is **1,378 lists, not 1,959 or 3,075** — and §1 argues the
realistic figure is far lower still, because the fixed zones already re-key those gates to place.

---

## 3. The open question: what level does NPC gear resolve at?

**Two documents in this repo contradict each other, and the answer changes the size of the mod.**

| Source | Claim |
|---|---|
| `engine-behaviour.md` §3 | *"NPC gear is not zone-loot: outfit/inventory lists resolve against **the NPC's own level**… so a zone band affects gear only via the level of the actor the LVLN picked."* |
| `enemy-taxonomy.md` §4 | *"**fixing an NPC's tier does not fix its equipment.** A level-1 bandit in a level-40 game still rolls its armour off a player-gated list."* |

They cannot both be right, and neither is `[verified]` — both are reasoning from record shape, which
cannot show the resolution level.

| If gear resolves at… | Then | Job size |
|---|---|---|
| **the NPC's own level** (the `[community]` consensus, and what `engine-behaviour.md` asserts) | the tier already fixes gear, because the tier fixed the NPC. A T2 zone spawns an Outlaw (L=5) who rolls his cuirass at 5 → the gate-1 rung. **Nothing to do.** | **~0 lists** |
| **the player's level** (what `enemy-taxonomy.md` asserts) | every one of the 1,378 gated lists is a live bone-1 leak, and a level-50 character strips Daedric off a level-5 Outlaw in a T1 camp. | **~1,378 lists** |

**Recommendation: treat it as the third in-game test**, alongside the two in `engine-behaviour.md` §7,
and run all three in one visit. It is as cheap as the others — kill a low-tier bandit at a high player
level and read what he was wearing.

**Working assumption for the rest of this document: gear resolves at the NPC's level.** It is the
established community understanding, it is what the record design implies (six bandit tiers sharing
one outfit only makes sense if the *actor* discriminates), and it is what `engine-behaviour.md`
concluded from the wider read. **Marked `[community]`, and the whole of §6's cost estimate is
contingent on it.**

---

## 4. Special loot, and a bone-1 leak worth closing

`engine-behaviour.md` §3 (revised): the engine ships three settings that name the zone level as the
operand for boss-chest "special loot" `[verified]` in
`reference/Base/01Skyrim/GameSettings/`:

| GMST | FormKey | Vanilla | **Ehlnofey** |
|---|---|---|---|
| `fSpecialLootMinZoneLevelMult` | `10FEDD:Skyrim.esm` | 0.4 | **0.4** *(keep)* |
| `fSpecialLootMaxZoneLevelMult` | `10FEDF:Skyrim.esm` | 1.0 | **1.0** *(keep)* |
| `fSpecialLootMinPCLevelMult` | `10FEDE:Skyrim.esm` | **0.6** | **0** ⟵ **change** |

**Keep the two zone multipliers.** A special-loot roll spanning 0.4×`N` to 1.0×`N` is a *good* fit for
bone 3: it sits inside the tier, so a boss chest is the best thing in its dungeon and never better
than its dungeon. 86 lists carry the `SpecialLoot` flag.

**Zero `fSpecialLootMinPCLevelMult`.** It is a floor tied to **0.6 × the player's level**, independent
of the zone — the last piece of player-relative loot scaling in the engine's own settings. Left at
0.6, a level-50 character looting a fixed T1 chest still rolls special loot against level 30, which is
bone 1 violated in the one place the mod is most likely to be judged: the reward.

`[verified]` that the settings exist and their values; `[unverified]` that zeroing the PC floor has no
unwanted side effect — worth watching in the same test visit, since a zero could conceivably degrade
to "no special loot" rather than "zone-only special loot". **If it does, the fallback is to leave it
at 0.6 and accept a documented exception**, since the alternative is losing boss chests entirely.

---

## 5. What Ehlnofey still chooses to do

§1 removes the *need* for a truncation pass. Three things remain genuine decisions rather than
consequences.

### 5.1 Hand-placed uniques — leave them, and protect them

`dungeons.md` and `unique-enemies.md` establish that Skyrim's named artefacts are hand-placed static
records. They are already the purest expression of bone 3 and **need no edits at all**.

What they need is protection: `morrowloot.md` §8.6 — ***bone 3 is undone by a respawning vault.*** If
a zone holding fixed reward resets, the reward farms. MLU's answer was 15 new `MLU_*ZoneNR` zones, 13
of them `NeverResets`.

Ehlnofey's position is better than MLU's by accident: **91 of the 355 zones already carry
`NeverResets`** `[verified]`, and `difficulty-map.md` §5 requires flags be preserved exactly. So the
protection is largely already in place and the job is an audit — *does any T5/T6/T7 zone holding a
unique reset?* — not an authoring pass. **Deferred to Phase 4**, as it needs the per-zone container
contents, which no Phase 1 document indexed.

### 5.2 Smithing — the back door

MLU found that capping the drop economy is pointless if crafting reintroduces the same gear, and
added **new** GMSTs `fSmithingArmorMax` / `fSmithingWeaponMax` = 6 (`005901`/`005902:MLU.esp`) —
records that **do not exist in the base game at all** (CLAUDE.md's "GMSTs can be *added*" gotcha).

**Ehlnofey's verdict: do not do this.** It is out of scope by the mod's own non-goals — *"not a
perk/skill overhaul"* — and the case is weaker here than for MLU: MLU had to suppress a *drop*
economy it could not otherwise control, whereas Ehlnofey's materials are already place-gated (§1). A
player who grinds Smithing to make Daedric armour has earned it through a system Ehlnofey does not
touch, and that is a different complaint from "the world scaled to me".

**Recorded as a deliberate non-decision.** If playtest shows crafting trivialises the tier ladder, it
is two new records to revisit.

### 5.3 Merchants and quest rewards

Not surveyed by any Phase 1 document, and **out of scope for Phase 3**. Merchant chests and quest
reward lists (`LItemArmorCuirassHeavyReward`, gates 1/12/18/25/32) resolve outside any dungeon zone,
so they are neither zone-fixed nor covered here. Flagged in §7; they are a real hole in the same way
the overworld is (`difficulty-map.md` §4.1), and for the same reason — **no encounter zone, no tier**.

---

## 6. Implementation

Under §3's working assumption, the loot model costs **one record**:

| Change | Records | Reachable by |
|---|---|---|
| `fSpecialLootMinPCLevelMult` → 0 | **1 `GMST`** | **plugin only** — SkyPatcher has no GMST module (`skypatcher.md` §5.1) |
| everything else in §1 | **0** | consequence of `difficulty-map.md` |

If the §3 test goes the other way, the fallback is MLU's technique expressed as rules rather than
overrides — `skypatcher.md` §4.2 confirms both operations exist and that the level predicate does the
tier work, so the pass is a handful of lines rather than 400 records:

```ini
; drop every entry gated above the tier a list should serve
filterByLLs=Skyrim.esm|571AA:removeFromLLs=Skyrim.esm|139B1~>30~none
; or by material, which is what "no Daedric in the random economy" actually means
removeObjectsByKeyword=<DaedricMaterial keyword>
```

Two `skypatcher.md` traps that apply directly and both **fail silently**:

1. `calcForLevelAndEachItem=true` is **not** the parsed spelling — it is `calcLevelAndEachItem`
   (§3.4). The documented form matches no regex and the flag is never set.
2. The flag setters **assign, they do not OR** — `curobj->llFlags = <flag>` replaces the whole byte,
   so two flag directives on one line silently drop the first (§4.2).

**Bash tags.** `morrowloot.md` §6 is decisive and it applies here: a mod that *truncates* lists can
declare `Delev`/`Relev` and delegate compatibility to Wrye Bash, while a mod that *replaces* them must
build its own patcher. Ehlnofey does neither by default — it edits **no** leveled item lists — so it
inherits the best case: nothing to merge, nothing to conflict. **If §3 forces the fallback, declare
`Delev`/`Relev`** and keep the operations to removal so the tags remain honest.

---

## 7. Open questions

1. **What level does NPC gear resolve at?** (§3) The one question that decides whether this document
   describes a 1-record job or a 1,378-list one. Run it with `engine-behaviour.md` §7's two.
2. **Does zeroing `fSpecialLootMinPCLevelMult` disable special loot rather than zone-lock it?** (§4)
   Cheap to observe in the same visit. `[unverified]`
3. **Merchants and quest rewards** (§5.3) — outside any zone, therefore untiered. Same structural hole
   as the overworld. Not surveyed.
4. **Do the 1,693 flat lists need anything?** They have no level gates, so they are already
   place-neutral variety pools. Probably nothing — but they are 55% of the corpus and nobody has
   looked at what is *in* them. `[unverified]`
5. **The `NeverResets` audit** (§5.1) — deferred to Phase 4; needs per-zone container contents.
6. **Is a seven-material ladder too generous at the top?** §1 gives every T6 zone Ebony as its
   *standard* material. Vanilla reached Ebony only in the late game; 14 zones now do so permanently.
   That is bone 3 working as designed, but it is the loot-side equivalent of `tiers.md` §9's
   calibration question and moves with the same lever. `[unverified]`

---

## Sources

Computed here from `reference/` (`[verified]`): `reference/Base/01Skyrim/LeveledItems/` (3,075
records — flag census, gate census, the 162 multi-rung gear lists) ·
`reference/Base/01Skyrim/GameSettings/fSpecialLoot*` · `reference/Base/01Skyrim/Weapons/` (material
names behind `LItemWeaponSwordBest`).

Design inputs: `design/tiers.md` §§3–6 · `design/difficulty-map.md` §§1–2 ·
`design/engine-behaviour.md` §3 · `prior-art/morrowloot.md` §§3, 6, 8 · `prior-art/skypatcher.md`
§§3.4, 4.2, 5 · `world/enemy-taxonomy.md` §4 · `world/overview.md` §6.
