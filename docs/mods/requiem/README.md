---
id: "mods/requiem/README"
title: "Requiem — prior art index"
slug: "README"
section: "mods/requiem"
game: "skyrim"
kind: "research"
project: null
mod: "requiem"
tags: ["skyrim", "requiem", "deleveling", "third-party-mod", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/prior-art/requiem/README.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 0, "unverified": 0, "upstream": 0, "verified": 5}
lines: 52
content_sha256: "765607455be1336926818926a7c6bafb66079bd71e851c9207f3d303b0ed9319"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Requiem — prior art index

**Subject:** Requiem — The Roleplaying Overhaul, **v6.0.2** (Feb 2025 build).
**Phase:** 2 (prior art & method). **Status:** plugin + patcher read; no in-game testing done.

Requiem is the reference implementation of a deleveled Skyrim, and the closest existing thing to
what Ehlnofey is trying to be. This folder records **how it actually works**, read from its own
plugin and its own patcher source — not from its Nexus description.

| Doc | What it covers |
|---|---|
| [`plugin-analysis.md`](plugin-analysis.md) | What `Requiem.esp` does to levels, leveled lists, encounter zones and GMSTs — measured, with counts |
| [`reqtificator.md`](reqtificator.md) | The Reqtificator patcher: architecture, transformer pipeline, rules engine, ReqTags, compatibility model |
| [`bash-tags.md`](bash-tags.md) | What `core/BashTags/Requiem.txt` is for, and whether Ehlnofey needs one |
| [`lessons-for-ehlnofey.md`](lessons-for-ehlnofey.md) | The verdict: what to copy, what to avoid, and what it means for the Phase 3 strategy decision |

## The five findings that matter most

1. **Deleveling happens in the leveled lists, not on the NPC records.** Of the 328 vanilla `LVLN`
   lists Requiem overrides, **100% are flattened to a single gate level**, 518 of 571 to `Level: 1`.
   Most enemy `NPC_` records were *already* fixed-level in vanilla. `[verified]`
2. **Requiem does not use encounter zones for deleveling — at all.** It ships **8** `ECZN` records
   against vanilla's 358; 7 are byte-identical to vanilla and 1 is new. This directly contradicts
   the working assumption in `CLAUDE.md`. `[verified]`
3. **Enemies get fixed levels; allies keep scaling.** 261 vanilla `PcLevelMult` NPCs became fixed;
   the 68 left scaling are almost entirely followers, housecarls and hirelings. `[verified]`
4. **Flatten the gate, keep the pool.** Flattened lists keep 4+ entries at the same level, so
   variety survives while progression dies. Entry count only fell to 81.6% of vanilla. `[verified]`
5. **The override approach costs 108 MB of YAML.** 26,620 records, 18,766 of them overrides. That is
   the single strongest argument against Ehlnofey's implementation option A. `[verified]`

## Reproducing the evidence

The decompile these docs cite is **gitignored** and must be regenerated locally:

```powershell
. ".claude/config/tools.ps1"
& (Assert-Tool $Tools.spriggitCli 'spriggitCli') serialize `
  --InputPath   "reference/mods/Requiem/plugin/Requiem.esp" `
  --OutputPath  "reference/mods/RequiemYaml" `
  --GameRelease $Tools.spriggit.gameRelease `
  --PackageName $Tools.spriggit.packageName `
  --PackageVersion $Tools.spriggit.packageVersion
```

Paths cited as `reference/mods/RequiemYaml/…` come from that output. Paths cited as
`reference/mods/Requiem/core/…` are shipped files in the downloaded mod, including the
Reqtificator's **full C# source** under `core/Source/Reqtificator/`.

> **Scope note.** `fomod/options/esp/` holds four cosmetic toggles (message and sound tweaks) and
> `plugin/Requiem - Creation Club.esp` covers CC content. Neither is part of the deleveling system;
> they are not analysed here.
