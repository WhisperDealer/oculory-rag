---
id: "mods/requiem/bash-tags"
title: "Bash tags — what core/BashTags/Requiem.txt is for"
slug: "bash-tags"
section: "mods/requiem"
game: "skyrim"
kind: "research"
project: null
mod: "requiem"
tags: ["skyrim", "requiem", "deleveling", "third-party-mod", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/prior-art/requiem/bash-tags.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 5, "unverified": 0, "upstream": 0, "verified": 2}
lines: 77
content_sha256: "5457ba8e73cabad2ab2fd77a163ef8fa2c6a4384e1e8f5b3fb962d8a805955ea"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Bash tags — what `core/BashTags/Requiem.txt` is for

## What they are

**Bash tags are instructions to Wrye Bash's "Bashed Patch" builder.** They are not read by Skyrim,
not by SKSE, and not by the Reqtificator. They exist purely to tell one specific tool — Wrye Bash —
*which parts of this plugin's records it should carry forward* when it merges a load order into a
single conflict-resolution patch. `[community]`

The problem they solve is Bethesda's record-level conflict rule: **the last plugin to load wins the
whole record**, not just the fields it meant to change. If Requiem sets a bandit's stats and a
second mod changes the same bandit's outfit, whichever loads last silently discards the other's
work. A Bashed Patch rebuilds the record field-group by field-group, and the tags say which groups
to take from where. `[community]`

Historically tags were embedded in the plugin header description. The modern mechanism — the one
Requiem uses — is a **loose `BashTags/<PluginName>.txt` file** shipped inside the mod, one tag per
line. Wrye Bash picks it up automatically, so the author can change tags without touching the
plugin. `[community]`

## What Requiem asks for

35 tags (`reference/mods/Requiem/core/BashTags/Requiem.txt`), grouped by what they protect:

| Group | Tags | Protects |
|---|---|---|
| **Actor core** | `Actors.ACBS`, `Actors.AIData`, `Actors.Stats`, `Actors.RecordFlags`, `Actors.CombatStyle`, `Actors.DeathItem` | The `NPC_` stat block, AI data, combat style, death item |
| **Capability** | `Actors.Perks.Add`, `Actors.Perks.Remove`, `Actors.Spells`, `Actors.SpellsForceAdd` | The perks and spells the Reqtificator's rules assign |
| **Identity** | `NPC.Class`, `NPC.Race`, `NPC.AttackRace`, `NPC.CrimeFaction`, `NPC.DefaultOutfit`, `Names`, `Text` | Class/race/name/description |
| **Inventory & outfits** | `Invent.Add`, `Invent.Change`, `Invent.Remove`, `Outfits.Add`, `Outfits.Remove` | Who carries what |
| **Social graph** | `Factions`, `Relations.Add`, `Relations.Change`, `Relations.Remove` | Faction membership and inter-faction relations |
| **Items & magic** | `Stats`, `Keywords`, `EffectStats`, `EnchantmentStats`, `SpellStats` | Weapon/armor stats, keywords, magic effect and enchantment numbers |
| **Races** | `R.Skills`, `R.Stats`, `R.Description`, `R.ChangeSpells` | The `RACE` record edits |
| **Cells** | `C.Encounter` | **The cell → encounter-zone assignment** |

### Two of these are directly informative

**`Actors.ACBS` is the level tag.** The ACBS subrecord is the actor's base configuration block — it
carries the flags, magicka/stamina offsets, speed, disposition **and the level** (both the fixed
level and the `PcLevelMult` / calc-min / calc-max triple). By tagging it, Requiem is telling Wrye
Bash: *whatever else another mod does to this NPC, keep my level*. It is the Bashed-Patch expression
of the deleveling itself. `[community]`

**`Delev` and `Relev` are deliberately absent.** Those are Wrye Bash's leveled-list tags (delete-
and re-level entries), and they are the obvious things a deleveling mod would want. Requiem asks for
neither — verified, zero matches in the file. Instead it does leveled-list merging **itself**, in
the Reqtificator (see [`reqtificator.md`](reqtificator.md)), and actively treats a Bashed Patch that
merged leveled lists as a *problem*:

> `Changelog.md:1467` — *"Ingame Bashed Patch check detects if the Leveled List option has been used."*
> `Changelog.md:1457` — *"Detecting if a Bashed Patch was used to merge leveled lists is implemented without the usage of `Game.GetFormFromFile`."*

Requiem ships an in-game check that detects the conflict and warns the player. **Two tools both
merging leveled lists is a conflict, not a redundancy** — Requiem picked its own merger and told
Wrye Bash to stay out. `[verified]`

## Does Ehlnofey need one?

**Not yet — and possibly never, depending on the Phase 3 decision.**

- Bash tags are only meaningful for a plugin that **overrides records**. Under implementation option
  **B** (SkyPatcher rules) there are few or no overrides, so there is nothing to tag.
- Under option **A** or the hybrid, a `BashTags/Ehlnofey.txt` becomes worth shipping, and Requiem's
  file is a good starting template. The minimum for a deleveler is **`Actors.ACBS`** (keeps our
  levels) plus **`Actors.Stats`**; add `C.Encounter` only if we end up assigning encounter zones.
- **Whether to ask for `Delev`/`Relev` is a real decision, not a default.** If Ehlnofey flattens
  leveled lists the way Requiem does, letting Wrye Bash re-level them afterwards would undo the
  entire mod. Requiem's answer — refuse the tags, own the merge — is the safe one, but it is also
  what forced them to build and maintain a merger.

This is a Phase 3 item. Record the decision in `arch-docs/design/implementation-strategy.md`; do not
ship a tags file before then.

> **Caveat.** Everything here about Wrye Bash's *behaviour* is `[community]` — established modding
> knowledge, not re-tested in this workspace. The **contents** of Requiem's tag file, and the
> absence of `Delev`/`Relev`, are `[verified]`. If Ehlnofey ends up depending on a specific tag's
> semantics, confirm it against Wrye Bash's own documentation first.
