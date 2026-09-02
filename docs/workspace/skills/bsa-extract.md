---
id: "workspace/skills/bsa-extract"
title: "Extract from a .bsa / .ba2 archive (bsab.exe)"
slug: "bsa-extract"
section: "workspace/skills"
game: "both"
kind: "workspace"
project: null
mod: null
tags: ["skill", "spriggit-workspace", "tooling", "source:oculory"]
source_repo: "oculory"
source_path: ".claude/skills/bsa-extract/SKILL.md"
source_branch: "main"
source_commit: "fc60a29569efb8c11241963b4cda83855f9c549b"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 0, "unverified": 0, "upstream": 0, "verified": 0}
lines: 45
content_sha256: "db751f3a30d9a493e5f682c35287e40abeee2f1780f92798a1ecbde4d701d99b"
synced_at: "2026-09-02T11:48:12Z"
sync_version: 1
skill_name: "bsa-extract"
description: "Extract or list files (especially scripts) from a Bethesda .bsa/.ba2 archive using the BSA Browser CLI (bsab.exe). Use when the user wants to pull .pex scripts (or any assets) out of a .bsa/.ba2, or inspect what an archive contains."
---

# Extract from a .bsa / .ba2 archive (bsab.exe)

Pull files out of a Bethesda archive — most often the compiled `scripts/*.pex` so they can be
decompiled and edited.

## Tool (from config)

- `$Tools.bsab` — from `.claude/config/tools.json` (loaded via `.claude/config/tools.ps1`); the
  BSA Browser CLI (`bsab.exe`). Run the **modlist-install** skill to point it at a modlist's copy,
  or edit `tools.json`.
- Usage: `bsab [OPTIONS] FILE [FILE...] [DESTINATION]`
  - `-l:[AFNSX]` list, `-e:[N]` extract (`N` = flatten, no subfolders)
  - `-f FILTER` simple wildcard filter (case-insensitive, repeatable), `--exclude FILTER`
  - `--regex REGEX`, `-o` overwrite, `-i` ignore errors

## Steps

1. **List first** to see what's inside and confirm the path layout (scripts usually live under
   `Scripts\*.pex`):

```powershell
. ".claude/config/tools.ps1"
& (Assert-Tool $Tools.bsab 'bsab') -l -f "*.pex" "<Archive.bsa>"
```

2. **Extract** the scripts to a destination folder, preserving the internal directory structure:

```powershell
. ".claude/config/tools.ps1"
& (Assert-Tool $Tools.bsab 'bsab') -e -o `
  -f "*.pex" "<Archive.bsa>" "<destination>"
```

## Where to extract

- Scripts from **your own** mod that you intend to edit → a working folder, then decompile into
  `src/<ModName>/Scripts/source/` (see the `pex-decompile` skill).
- Scripts from **someone else's** mod, for reference/lookup only → `reference/<name>/`
  (gitignored). Never commit third-party assets.

## Notes

- `.bsa`/`.ba2` archives are gitignored — never commit them; they're large and regenerable.
- Drop the `-f` filter to extract everything; add more `-f`/`--exclude` filters to narrow.
- Use `-e:N` if you want files dumped flat without their subfolders.
