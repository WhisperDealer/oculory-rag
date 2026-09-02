---
id: "mods/requiem/lessons-for-ehlnofey"
title: "What Ehlnofey should take from Requiem"
slug: "lessons-for-ehlnofey"
section: "mods/requiem"
game: "skyrim"
kind: "research"
project: null
mod: "requiem"
tags: ["skyrim", "requiem", "deleveling", "third-party-mod", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/prior-art/requiem/lessons-for-ehlnofey.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 0, "unverified": 1, "upstream": 0, "verified": 2}
lines: 154
content_sha256: "0c71666828b36b05f9b7a77984cff5f4de3f84a8b1aca550bcc502e288a366b5"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# What Ehlnofey should take from Requiem

Conclusions from [`plugin-analysis.md`](plugin-analysis.md), [`reqtificator.md`](reqtificator.md)
and [`bash-tags.md`](bash-tags.md). Requiem is prior art for the *problem*, not a template for the
*product* — it is a total overhaul and Ehlnofey explicitly is not.

## 1. The single biggest correction to our assumptions

> `CLAUDE.md`: *"`ECZN` — **Probably the single most important record type for this mod**: a fixed
> per-dungeon level is literally the 'fixed law' the design asks for."*

**Requiem ships 8 encounter zones out of vanilla's 358, and none of them for levelling.** `[verified]`

The reasoning is sound once you see it: an encounter zone's min/max **clamps** the level that the
leveled-list machinery computes. It is a lever *on* scaling. If you flatten the lists, there is
nothing left to clamp — the zone becomes inert. Requiem removed the scaling rather than bounding it.

This does not kill the idea. A fixed per-dungeon level is still the most natural expression of bone
1, and it is genuinely how a designer thinks. But **`ECZN` cannot be the primary mechanism *in a
Requiem-style design***: it constrains a computation Requiem deleted.

> **Resolved by [`../morrowloot.md`](../morrowloot/morrowloot.md).** MorrowLoot Ultimate ships **360** encounter
> zones, **324 with a real level band**, and uses them as its entire difficulty map — because it
> *keeps* the leveled-list machinery Requiem flattened. Zones are inert in one architecture and
> load-bearing in the other. **The `ECZN` question and the `LVLN` question are a single decision.**
> Requiem's 8 zones are evidence about Requiem's architecture, not about encounter zones.

## 2. Delevel the lists, not the NPCs

Vanilla's enemy `NPC_` records are already mostly fixed-level — 2,028 of the 2,702 Requiem touches
were `NpcLevel` before Requiem got to them. The scaling lives in the **`LVLN` gate levels** that
choose *which* fixed-level variant spawns.

`LCharDraugrBoss` went from 13 entries across 7 gates to **one entry at `Level: 1`**.

**Implication for scope:** the deleveling core of Ehlnofey is a few hundred leveled lists, not
thousands of NPC records. That is a dramatically smaller job than "delevel every NPC" implies, and
it is the first thing to size in Phase 3.

## 3. Flatten the gate, keep the pool

Requiem's flattened lists keep their entries — 342 of 571 still hold 4+ — all at the same gate
level, with `CalculateFromAllLevelsLessThanOrEqualPlayer` set. The list stops being a ladder and
becomes a **uniform random draw**. Total entry count only fell to 81.6% of vanilla.

Adopt this. Deleting entries throws away variety that has nothing to do with player level.

**And budget for the consequence:** once a list is flat, every draw is mechanically identical.
Requiem had to build a whole actor-variation generator to put variety back. Deleveling costs
variety; plan how to pay it back, or accept a flatter world.

## 4. Three transferable record techniques

| Technique | What it does | Use it for |
|---|---|---|
| **`_CLI_` weight unrolling** | `Count` reinterpreted as a weight; one entry with `Count: 5` unrolls to five entries | Weighted random selection in a flat list — Skyrim has no weight field. The obvious fix for "everything is equally likely now" |
| **`Level: 9999`** | Entry stays in the record but can never roll | Disabling an entry without deleting it, so diffs and merges still see it |
| **`REQ_NULL_` rename** | Orphaned records renamed, not deleted | Retiring a record safely — deletion breaks every reference to it |

The `_CLI_` unrolling needs a patcher to expand it. `9999` and the rename are pure record
conventions and work in a hand-authored plugin today. Adopt an `EHL_NULL_` convention now.

## 5. Fixed for enemies, scaled for allies

Requiem converted 261 NPCs to fixed levels and left 68 scaling — and the 68 are almost entirely
**followers, housecarls and hirelings**.

This is a genuine exception to bone 1 (*the world does not scale*), and a well-motivated one: a
fixed-level companion is useless at level 40 and carries you at level 5. Bone 1 is about **the
world**, and your follower is not the world.

**Action:** record this in `arch-docs/design/` as an explicit, argued exception rather than letting
it happen by accident. Requiem never wrote its rule down, which is why it reads as an oversight
until you list the set.

## 6. Difficulty comes from the world, not a slider

Requiem sets **all ten `fDiffMultHPBy/ToPC*` and both `fDiffMultXP*` game settings to 1.0** — the
difficulty slider no longer scales damage — while leaving `fLeveledActorMult*` at vanilla, so the
per-placed-actor Easy/Medium/Hard/VeryHard tuning on 5,685 placed actors stays live.

That pairing is exactly Ehlnofey's thesis in two record edits, and it is cheap. Strong candidate for
the design spec. Note the honest cost: it removes the player's only difficulty control, which for a
mod that is *not* a total overhaul may be a step too far. Decide deliberately.

## 7. Vanilla's `LevelGate*` globals survive

Requiem overrides **none** of the 12 `LevelGate*` globals — vanilla's only systematic player-level
spawn gate (spriggans at 8, giants at 24, …) is still live in the most famous deleveling mod.

`CLAUDE.md` already flags these as "a bone-1 violation that already exists". Requiem's precedent is
to leave them alone. Ehlnofey should still decide explicitly — but note that "the deleveling mod
everyone uses ships with these intact" is evidence they are not urgent.

## 8. The strategy decision — what this evidence actually says

Phase 3's open question is A (plugin overrides) vs B (runtime rules) vs C (generated patch).

**Requiem is a fully-committed option A, and the cost is now measured:**

| | |
|---|---|
| Records in `Requiem.esp` | **26,620** (18,766 overrides) |
| Spriggit YAML on disk | **108 MB** |
| Masters required | 5 game plugins + **USSEP** + 4 Creation Club plugins |
| Compatibility | requires a **bespoke patcher** and a per-mod patch ecosystem |

108 MB of generated YAML is not reviewable, and `CLAUDE.md` already names diff volume as "the thing
most likely to make this project unmaintainable". **This is the strongest evidence yet against
option A at Requiem's scale.**

But read the cost honestly before over-correcting:

- Requiem's volume is mostly **items and capability** — 4,340 weapons, 3,433 leveled items, 3,106
  armors, 2,263 crafting recipes, 2,050 magic effects, 599 perks. Ehlnofey's non-goals exclude
  nearly all of that.
- The **deleveling proper** is ~330 `LVLN` overrides, ~2,100 `LVLI` overrides, ~260 NPC level
  conversions, ~12 GMSTs. At Spriggit's observed density that is a few MB, not 108 — a **plausible
  hand-authored plugin**.
- Requiem's `Requiem.esp` is a hard master for USSEP and four CC plugins. Ehlnofey should treat
  every added master as a cost, per the naming conventions already fixed in `CLAUDE.md`.

**Working conclusion for Phase 3:** the hybrid already sketched in `CLAUDE.md` survives contact with
the evidence, but with its centre of gravity moved. The hand-authored core should be **the flattened
leveled lists** — the smallest set of records that delivers bone 1 — not the encounter zones.

> **Updated after [`../skypatcher.md`](../skypatcher/skypatcher.md).** The per-NPC and per-item distribution
> goes to **SkyPatcher rules** — it can express all of this, and the generated-patch option
> (Synthesis) has since been ruled out for this mod. The plugin half shrinks to the `GMST`s and any
> new records rules need to point at.

## 9. Two process lessons

- **Ship the patcher's source.** Requiem shipping 5,360 lines of C# is why this analysis is
  `[verified]` rather than `[unverified]`. Whatever Ehlnofey builds, the rules should be readable.
- **Deleveling is curation, not an algorithm.** `Changelog.md` is 2,491 lines, with individual
  entries like *"Delevels Fjola, Umana and Sulla Trebatius"* and *"Delevel enchanted imperial
  swords"* — one-off manual fixes across years. Requiem *still* leaves 114 NPCs with live
  player-scaling. Plan for a long tail and a coverage-audit script; do not plan for a clean sweep.

## Open questions this raised — all now closed

Phase 2 is complete; these are kept as a record of how they resolved.

1. ~~If not `ECZN`, what gives a *place* a fixed difficulty?~~ **`ECZN` does** — in an MLU-style
   architecture that keeps the leveled-list machinery ([`../morrowloot.md`](../morrowloot/morrowloot.md) §2).
   SkyPatcher can set the bands, but **cannot** filter zones by location keyword, so a difficulty
   map must enumerate zones ([`../skypatcher.md`](../skypatcher/skypatcher.md) §5.3).
2. ~~Can SkyPatcher flatten a leveled list?~~ **Yes** — `clear=true` + `addToLLs=form~level~count`
   ([`../skypatcher.md`](../skypatcher/skypatcher.md) §4.2). Option B *can* do the core job, so the hybrid is
   a choice rather than a forced move.
3. ~~Does Synthesis offer stable FormID persistence?~~ **Moot** — Synthesis was ruled out for this
   mod. The underlying concern still applies to whatever *does* create new records: FormIDs must
   stay stable across regeneration or saves break.
