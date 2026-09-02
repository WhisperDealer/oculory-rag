---
id: "mods/requiem/reqtificator"
title: "The Reqtificator — Requiem's patcher"
slug: "reqtificator"
section: "mods/requiem"
game: "skyrim"
kind: "research"
project: null
mod: "requiem"
tags: ["skyrim", "requiem", "deleveling", "third-party-mod", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/prior-art/requiem/reqtificator.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 0, "unverified": 0, "upstream": 0, "verified": 7}
lines: 204
content_sha256: "eeb9deb76d1362c45678badf8ca004e18812ed5ab6ff0d31c250378855bb55dc"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# The Reqtificator — Requiem's patcher

Source read at `reference/mods/Requiem/core/Source/Reqtificator/Reqtificator/` — Requiem ships the
**full C# source**, ~5,360 lines across 79 files. Nothing here is inferred from behaviour.

## Why this matters to Ehlnofey

The Reqtificator is **built on Mutagen** (`Mutagen.Bethesda.Skyrim.dll` in `core/Reqtificator/app/`)
— the same library Spriggit uses — and is a WPF desktop app that generates a patch on the user's
install.

> **Scope note.** Ehlnofey has since **ruled out a generated-patch approach** (the old option C), so
> this is no longer a template to copy wholesale. It stays worth reading for two things that carry
> over to *any* implementation: the **rules engine** and its condition vocabulary, and the
> **template-chain resolver**, which is the algorithm `CLAUDE.md` says this workspace needs.

## Architecture

`MainLogicExecutor.GeneratePatch()` builds one output plugin by running a **transformer pipeline**
over the winning override of every record of a given type:

```
for each record type:  loadOrder.PriorityOrder.<Type>().WinningContextOverrides()
                       └─► Transformer.AndThen(Transformer)…  ─►  patch.WithRecords(result)
```

Order and content of the pipeline (percentages are its own progress reporting):

| % | Stage | Transformers applied |
|---|---|---|
| 5 | Ammo | `AmmunitionTransformer` |
| 10 | Encounter Zones | `OpenCombatBoundaries` |
| 15/20 | Doors, Containers | `CustomLockpicking<T>` |
| 25 | **Leveled Items** | `CompactLeveledListUnrolling` → `LeveledListMerging` → `TemperedItemGeneration` |
| 30 | **Leveled Characters** | `CompactLeveledListUnrolling` → `LeveledListMerging` |
| 35 | Armors | `ArmorTypeKeyword` → `ArmorRatingScaling` → `ArmorKeywordsFromRules` |
| 40 | Weapons | `WeaponDamageScaling` → `MeleeRange` → `CriticalDamage` → `NpcAmmunitionUsage` → `RangedSpeed` → `WeaponKeywordsFromRules` |
| 45 | **Actors** | `ForwardDataFromTemplate` → `ActorGlobalPerks` → `ActorPerksFromRules` → `ActorSpellsFromRules` → `PlayerChanges` |
| 50 | Races | `ForwardDataFromTemplate` → `CustomRacePatching` |
| 55 | **Actor Variations** | `ActorVariationsGenerator` |

`Transformer<T,TI,TGetter>` is a tiny composable interface with `.AndThen()`; each returns a
`TransformationResult` that tracks whether the record was actually modified, so unmodified records
never enter the patch. That is a clean design worth copying — it is what stops a generated patch
from being full of ITMs.

New records get FormIDs from a **`TextFileFormKeyAllocator`** persisted to
`Documents/My Games/Skyrim Special Edition/Requiem/FormPersistence.txt`, so a regenerated patch
keeps the same FormIDs across runs — **existing saves don't break.** `[verified]`

> Note the comment in the source: *"unfortunately, we must add the new records directly to the
> plugin to avoid broken formId links"* — generated actor variations are written into
> `Requiem.esp`'s own space, not the patch. A generated-patch design still has to think about which
> plugin owns new records.

## The rules engine

Perks, spells and keywords are **not hardcoded** — they are assigned by rules in HOCON config files
under `core/Reqtificator/Data/`:

| File | Lines | Purpose |
|---|---|---|
| `ActorAssignmentRules_Requiem.esp.conf` | 544 | perks + spells → NPCs |
| `ArmorKeywordAssignments_Requiem.esp.conf` | 271 | keywords → armor |
| `WeaponKeywordAssignments_Requiem.esp.conf` | 56 | keywords → weapons |

The file is split into a **constants section** (named FormKeys — `races.creatures.spriggan =
"013204 Skyrim.esm"`) and **`feature_*` rule trees** that reference them by HOCON substitution.

Rules nest, and **conditions accumulate down the tree**: `AssignmentRule.GetAssignmentsWithSource`
only recurses into subnodes if the parent's own conditions all pass. So the outer node's
`keywords_none` acts as a blanket exclusion for everything beneath it:

```hocon
feature_racialTraits {
  keywords_none = [${keywords.doNotInheritTraits}]     # global opt-out for the whole tree

  creatures {
    spriggan {
      race_any     = [${races.creatures.spriggan}]
      perks_assign = [${racialTraits.creatures.spriggan.perks}]
    }
    …
  }
}
```

Available conditions — the complete set, from `AssignmentsFromRules.cs`:

| Condition | Applies to |
|---|---|
| `keywords_all` / `keywords_any` / `keywords_none` | NPCs, armor, weapons |
| `race_any` / `race_none` | NPCs only |

Assignments: `perks_assign`, `spells_assign`, `keywords_assign`. **That is the entire vocabulary** —
there is no level condition, no faction condition, no location or encounter-zone condition, and no
way to *set* a level. The rules engine handles **capability**, never **level**. Levels are
hand-authored in the plugin. `[verified]`

### The template-chain resolver

`Rules/ActorInheritanceGraphParser.cs` is a working implementation of exactly the resolver
`CLAUDE.md` says this workspace needs. `FindAllTemplates` walks the template chain **per flag** and:

- resolves each `TemplateFlag` independently, stopping at whichever ancestor actually owns it
  (`flagsToResolve = flagsToFollow.Where(f => actor.Configuration.TemplateFlags.HasFlag(f))`);
- treats **`ILeveledNpcGetter` as a branch point** — it recurses into *every* entry and yields
  multiple results, rather than reporting a single level. This is the "template is an `LVLN`"
  terminal case our gotchas list flags;
- throws `CircularInheritanceException` on a cycle, tracking the chain;
- throws `MissingTemplateException` rather than silently returning a default.

If Ehlnofey builds a resolver, this is the shape to copy. `[verified]`

## Compact leveled lists (`_CLI_`) — weighted random in a flat list

Skyrim's leveled lists have no weight field: every eligible entry is equally likely. Requiem works
around that with a naming convention. A list whose EditorID matches `^[a-zA-Z0-9]+_CLI_` is a
**compact leveled list**, in which `Count` is reinterpreted as a **weight**. Before the list is
used, the patcher unrolls it:

```csharp
return input.Entries!
    .Where(e => e.Data is not null)
    .SelectMany(e => {
        var newEntry = e.DeepCopy();
        newEntry.Data!.Count = 1;
        return Enumerable.Repeat(newEntry, e.Data!.Count);   // Count copies, each Count=1
    })
```

(`Transformers/LeveledItems/CompactLeveledItemUnroller.cs`) — one entry with `Count: 5` becomes five
identical entries, so the engine's uniform draw becomes a 5× weighted draw. The authored record
stays small and readable; the shipped one is expanded. `[verified]`

**This is directly reusable by Ehlnofey** and is the answer to an obvious problem: once you flatten
a list to a single gate level, every variant becomes equally common, which is rarely what you want.

## Actor variations (`_MUTATE_`) — variety without hand-authoring

`ActorVariationsGenerator` matches lists named `^[^_]+_LChar_(?:Variations|VoiceSpawns)_` and
computes a **cross product of a "skill template" NPC and a "look template" list**, generating one
merged NPC per pair via `ActorCopyTools.MergeVisualAndSkillTemplates`. This is what produces the 339
new `NPC_` and 243 new `LVLN` records in the shipped plugin, and the
`REQ_LChar_VoiceSpawns_Guard_Whiterun_GuardMale`-style lists.

The purpose is worth noting for bone 2 (*danger is legible*): once a list is flat, every bandit is
mechanically the same, so Requiem restores **visual and voice** variety to compensate. Deleveling
costs you variety, and you have to pay it back somewhere. `[verified]`

## ReqTags — opt-in compatibility for third parties

Other mod authors opt in to patcher features by putting a tag in their **plugin header
description** (`Configuration/ReqTagParser.cs`):

```
<<REQ:UNROLL; REQ:TEMPER; REQ:MUTATE>>
```

| Tag | Enables |
|---|---|
| `REQ:UNROLL` | `_CLI_` compact-leveled-list unrolling for that mod's records |
| `REQ:TEMPER` | automatic tempered-item generation |
| `REQ:MUTATE` | actor-variation generation |

Parsed by regex from `mod.ModHeader.Description`, with a deprecation path for the older
`REQ:"name";` prefix form. Requiem itself is added to every feature set in code rather than by tag.

This is an elegant, zero-infrastructure extension point: **no registry, no per-mod config file, no
patch to ship — the third-party author declares intent in a field they already control.** `[verified]`

## Leveled list merging — the compatibility story

`LeveledListMerging.cs` is Requiem's answer to "two mods edited the same leveled list". For each
record it collects all contexts from mods that have Requiem as a master, computes an
add/delete/modify diff of each against Requiem's own version, and replays the changes onto the
Requiem base. It deliberately **skips a candidate whose own masters include another candidate**
(that override already saw the earlier one, so replaying it would double-apply):

```csharp
var toMerge = mergeCandidates.Where(c => c.ModKey == Requiem ||
    mergeCandidates.All(other => _invertedMasterMap[c.ModKey].ContainsNot(other.ModKey))).ToList();
```

The changelog records the hard-won constraints: merged lists are **truncated at 255 entries** to
avoid an arithmetic overflow (`Changelog.md:465`), and priority-override formlists were removed
entirely as unworkable (`:1442`).

**The cost of this feature is the whole architecture.** Merging only works because Requiem owns a
base version of every list to diff against — which is exactly why `Requiem.esp` carries 18,766
override records. A rule-based mod with no base records has nothing to merge.

## What the Reqtificator does *not* do

Worth stating plainly, because the name suggests more than it delivers:

- **It never sets or changes an NPC's level.** No transformer writes `Configuration.Level`.
- **It never changes encounter-zone levels.** Only the combat-boundary flag.
- **It never flattens a leveled list.** Flattening is hand-authored in `Requiem.esp`; the patcher
  only unrolls `_CLI_` weights and merges third-party edits.

**The deleveling is in the plugin. The patcher exists for compatibility and for capability
(perks/spells/keywords/stats) — not for deleveling.** That is the single most important thing to
understand before treating the Reqtificator as a model for Ehlnofey's option C. `[verified]`
