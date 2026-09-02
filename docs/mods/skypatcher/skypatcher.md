---
id: "mods/skypatcher/skypatcher"
title: "SkyPatcher — runtime record patching via INI rules"
slug: "skypatcher"
section: "mods/skypatcher"
game: "skyrim"
kind: "research"
project: null
mod: "skypatcher"
tags: ["skyrim", "skypatcher", "distribution", "third-party-mod", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/prior-art/skypatcher.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 2, "unverified": 0, "upstream": 0, "verified": 7}
lines: 425
content_sha256: "95ab7b2de6d6fee52ff006fa410c3061f91efc832f197d93a3c1ff529d474ff7"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# SkyPatcher — runtime record patching via INI rules

**Subject:** SkyPatcher (SKSE plugin) by **Zzyxzz**. Source read at commit `f664900` (2026-04-21).
**Nexus:** <https://www.nexusmods.com/skyrimspecialedition/mods/106659>
**Source:** <https://github.com/Zzyxz/SkyPatcher.git> → cloned to `reference/mods/SkyPatcherSrc/`
(gitignored; `git clone --depth 1` to regenerate).

> **Evidence note.** Two sources, and **they disagree in places**:
>
> - **The C++ source** (25,624 lines, 28 modules) — `[verified]` as *what the code actually does*.
> - **The author's Nexus articles** — supplied by the user (Nexus returns HTTP 403 to automated
>   fetches). These document intent and give worked examples, and are the only source for the
>   filter *semantics* in §3.1.
>
> Where they conflict, **the source wins and the conflict is flagged** — see §3.4. Two documented
> keys do not work as written. Still not covered by either source: supported game runtimes and
> version history. Check the Nexus page by hand for those.

## 1. What it is

An SKSE DLL that **edits records in memory at game load** according to plain-text INI rules. There
is no plugin, no ESP, no FormID allocation, no masters. The records live in whatever plugins the
user already has; SkyPatcher reaches in and changes fields after the game has loaded them.

This is Ehlnofey's implementation **option B** in concrete form.

- Rules are applied at the SKSE `kDataLoaded` message (`main.cpp:1441`), i.e. after all plugins are
  loaded but before the game world is built.
- Because nothing is overridden in a plugin, **there is no record-level conflict with any other
  mod** — the usual "last plugin wins the whole record" problem does not arise. Two SkyPatcher
  configs touching the same record both apply, in file order.
- Conversely there is **nothing to inspect in xEdit**. The only diagnostic is the log.

## 2. Config layout

```
Data/SKSE/Plugins/SkyPatcher/<type>/*.ini        ← rules, recursive into subfolders
Data/SKSE/Plugins/SkyPatcher.ini                 ← the DLL's own settings
```

28 record types get their own folder (`main.cpp:1449-1621`):

```
npc  race  weapon  armor  ammo  magicEffect  ingestible  ingredient  spell  enchantment
projectile  outfit  scroll  misc  soulGem  faction  constructibleObject  book
movementType  leveledList  container  formList  reference  cell  location  encounterzone
```

Rules for Ehlnofey live in **`npc/`, `leveledList/`, `encounterzone/`** and possibly `cell/`.

### File loading rules (`readConfig`, e.g. `encounterzone.cpp`)

- Any `.ini` under the folder is read; **subdirectories are walked recursively**, so you can
  organise rules however you like.
- Lines beginning `;` are comments. Blank lines are skipped.
- **Conditional configs by filename.** If the filename contains `.esp`, `.esl` or `.esm`, the file
  is **skipped entirely unless that plugin is installed**:

  ```
  npc/Ehlnofey_Dawnguard.esm.ini      ← only loads if Dawnguard.esm is present
  ```

  That is a free, built-in compatibility mechanism — no scripting, no dependency checks. **Ehlnofey
  should use it for all DLC- and mod-specific rules.** `[verified]`

## 3. Line syntax

One rule per line, in two halves: **filters** (which records) and **operations** (what to do).
**Directives are separated by `:`**, and every value regex is `([^:]+)` — so a colon terminates a
value and **a value may never contain `:`**.

```ini
filterByFactions=Skyrim.esm|1BCC0:restrictToRaces=Skyrim.esm|13746:level=25
```

| Element | Form | Notes |
|---|---|---|
| Form reference | `PluginName.esp\|1BCC0` | Hex FormID, `\|` separator. ESL/ESPFE masked to `0xFFF` automatically |
| Form reference | `LCharBanditMelee1H` | A bare string is looked up as an **EditorID** |
| List of values | `a,b,c` | comma-separated |
| Tuple within a list | `a~b~c` | `~` is the inner delimiter for 2D arrays |
| Booleans | `true` / `yes` | anything else is false |
| "Leave alone" | `none` | every field explicitly tests `!= "none"` |
| Null a link | `null` | e.g. `location=null` clears an ECZN's location |

`GetFormFromIdentifier` (`utility.cpp:140`) is the resolver: `|` present → plugin+FormID lookup;
otherwise EditorID lookup. Note EditorIDs only resolve at runtime if something (usually
`po3_Tweaks`) preserves them — **prefer `Plugin.esp|FormID`, which always works.** `[verified]`
(the EditorID-preservation dependency is `[community]`)

Per the articles, EditorIDs are **not** supported for `objectsToAdd` / `factionsToAdd` (NPC) or
`formsToReplace` (outfit, leveled list). FormIDs may be shortened (`myMod.esp|08000223` →
`myMod.esp|223`), but the author recommends pasting the full FormID from xEdit.

### 3.1 Filter semantics — the thing that will bite you

**Different `filterBy*` families are OR'd, not AND'd.** Each family independently sets `found =
true` (`npc.cpp:2452-2536` — a matching keyword, race, outfit, class or combat style each set the
flag on their own). The articles state this outright: *"Filters work independent from each other…
If filterByWeapons has no match, filterByKeywords still can have a match."*

Within one family:

| Form | Logic |
|---|---|
| `filterByXy` | **AND** — every listed value must match |
| `filterByXyOr` | **OR** — at least one must match |
| `filterByXyExcluded` | **NOT** — any match kills the rule |

So to *narrow* a selection you cannot just stack `filterBy*` families — that widens it. Use the
**`restrictTo*`** keys, which are applied as gates after a record is `found`:

`restrictToRaces`, `restrictToGender`, `restrictToVoiceType`, `restrictToFlags`,
`restrictToTemplateFlags`, `restrictToSkill` (`=marksman~0~50`), `restrictToCombatStyle`,
`restrictToKeywords`, `restrictToMaleModelContains`.

> **`filterBy*` selects (union). `restrictTo*` constrains (intersection).** This is the single most
> important thing to get right when authoring Ehlnofey's rules, and nothing in the record data will
> tell you that you got it wrong — an over-broad filter silently patches more NPCs than intended.

Two more rules from the articles:

- **No filter at all ⇒ every record of that type is patched.** For leveled lists this must be made
  explicit with `noFilterLL=true` / `noFilterLLNPC=true` (`leveledlist.cpp:298,373`), because item
  and NPC lists are filtered separately.
- **The player is always excluded from race and keyword filtering.** To patch the player use
  `filterByNpcs=Skyrim.esm|7` **and no other filter**.

### 3.2 Rule ordering and conflicts

INI files are read **alphabetically, `0`–`z`**, and for a given field **the last write wins**. The
articles' example: `myCoolIronSword.ini` then `zuperIronSword.ini` → the `z` file wins. Rules that
only *add* or *remove* (keywords, spells, perks) compose without conflict; only same-field writes
collide.

**Practical consequence for Ehlnofey:** ship broad rules under an early-sorting filename and
narrow exceptions under a later one.

### 3.3 Folder naming — a real footgun

Because plugin-conditional configs are named after the plugin, two mods both shipping
`SkyPatcher/npc/Skyrim.esm.ini` will **overwrite each other in the mod manager**. Always nest under
a mod-specific folder:

```
SKSE/Plugins/SkyPatcher/npc/Ehlnofey/Skyrim.esm.ini     ✅
SKSE/Plugins/SkyPatcher/npc/Skyrim.esm.ini              ❌ collides with every other mod
```

### 3.4 Where the documentation is wrong

Both found by diffing the articles against the parser. **Both fail silently** — no error, no log
line, the directive is simply never matched:

| Documented | Actually parsed | Consequence |
|---|---|---|
| `calcForLevelAndEachItem=true` | **`calcLevelAndEachItem`** (`leveledlist.cpp:192`) | The documented spelling matches *no* regex — not `calcLevelAndEachItem`, not `calcForLevel`, not `calcEachItem` (each needs its literal followed by `\s*=`). The flag is never set. |
| `minLevelMult=1.5` | parsed with **`std::stoi`** (`encounterzone.cpp:269`) | Truncates to `1` → multiply by 1 → **no-op**. All six `ECZN` level fields use `stoi`; decimals are not supported despite the article's example. (NPC `level` *does* use `stof`, `npc.cpp:1252`.) |

Assume any SkyPatcher key is guilty until grepped. This is exactly guardrail 1 (*ground-truth before
claiming*) — and here the ground truth is the parser, not the mod page.

## 4. What matters to Ehlnofey

### 4.1 `npc/` — it can delevel actors directly

The NPC module is the largest (3,197 lines) and exposes ~90 keys. The level-relevant ones:

| Key | Effect |
|---|---|
| `level=25` | sets `actorData.level` — **a fixed level** (`npc.cpp:1250`, `stof`) |
| `calcLevelMin=` / `calcLevelMax=` | sets the `PcLevelMult` calc bounds (`npc.cpp:1258`) |
| **`setPcLevelMult=false=50`** | **clears the player-scaling flag**; the trailing number is the fallback level used when none can be calculated |
| `levelRange=25~100` + `changeStats=health=150~250` | interpolates a stat proportionally across a level band — L25→150 hp, L50→~183, L100+→250 |
| `healthBonus=` `staminaBonus=` `magickaBonus=` | flat offsets |
| `changeStats=` `changeSkills=` | actor values and skills |
| `perksToAdd=` `spellsToAdd=` `spellsToRemove=` | **capability**, the thing Requiem's rules engine does |
| `setTemplateFlags=` / `removeTemplateFlags=` | **break or redirect template inheritance** |

Filters — this is the important part, and it is far richer than Requiem's rules engine:

| Filter | |
|---|---|
| `filterByNpcs` / `Excluded` | explicit records |
| `filterByKeywords` / `Or` / `Excluded` | keyword sets |
| `filterByRaces`, `restrictToRaces` | race |
| `filterByFactions` / `Or` / `Excluded` | **faction** — Requiem's engine has no faction condition |
| `filterByClass` / `Excluded`, `filterByCombatStyle` | class, combat style |
| `filterByModNames` | which plugin the record comes from |
| `filterByEditorIdContains` / `Or` / `Excluded` | substring match on EditorID |
| **`filterByPCLevelMult`** | **selects NPCs that use player-level scaling** |
| `filterByEssential`, `filterByProtected`, `filterByGender`, `filterByAutoCalc` | misc |

`filterByPCLevelMult` is the deleveling primitive. *"Every NPC that currently scales with the
player, stop scaling"* is one line — note it needs **both** `setPcLevelMult=false` (clear the flag)
and `level=` (supply a fixed value), not just one:

```ini
; every player-scaled NPC becomes a fixed level 20
filterByPCLevelMult=true:setPcLevelMult=false=20:level=20
```

Requiem's ally exception (§1a of `requiem/plugin-analysis.md`) is one more directive — `Excluded`
filters subtract from the found set, so this narrows correctly where a second `filterBy*` family
would not:

```ini
filterByPCLevelMult=true:filterByFactionsExcluded=Skyrim.esm|5C84D,Skyrim.esm|5C84E:setPcLevelMult=false=20:level=20
```

The article's own worked example is instructive — it is a complete deleveling of one creature race,
including the warning that skipping `setPcLevelMult=false` leaves the bears at level 1000:

```ini
filterByRaces=Skyrim.esm|000131E8:levelRange=1~30:changeStats=health=625~900,calcStamina=10,calcMagicka=10:setPcLevelMult=false=50:setAutoCalcStats=false
```

Also relevant to bone 2 (*danger is legible*): `fullName=~…~` and `shortName=~…~` can rename NPCs,
which is how a tier ladder would be surfaced to the player without touching a record.

### 4.2 `leveledList/` — Requiem-style flattening is expressible

| Key | Effect |
|---|---|
| `clear=true` | **empties the list** (`leveledlist.cpp:674`) |
| `addToLLs=form~level~count` | append an entry; `level`/`count` default to 1 |
| `addOnceToLLs=` | append only if not already present |
| `removeFromLLs=form~level~count` | remove entries — **`level` and `count` accept comparison operators `<` `>` `<=` `>=`** |
| `removeObjectsByKeyword=` | remove entries whose object carries a keyword |
| `calcForLevel=true` | set flag `CalculateFromAllLevelsLessThanOrEqualPlayer` |
| `calcEachItem=true` | set flag `CalculateForEachItemInCount` |
| `calcLevelAndEachItem=true` | set **both** flags |
| `calcUseAll=true`, `clearFlags=true` | `UseAll`; clear all flags |
| `chanceNone=`, `chanceGlobal=` | chance-none and its global |
| `formsToReplace=`, `objectMultCount=` | swap entries, scale counts |

Filters: `filterByLLs` (item lists), `filterByLLNPCs` (actor lists),
`filterByEditorIdContains`/`Or`/`Excluded`, and `noFilterLL` / `noFilterLLNPC` to opt into
patching everything.

**The comparison operators are the find of the articles.** `removeFromLLs` accepts `<`, `>`, `<=`,
`>=` on the level and count fields, with `none` to skip a field:

```ini
; MLU-style truncation, generically: drop every entry gated above player level 30
filterByLLs=Skyrim.esm|571AA:removeFromLLs=Skyrim.esm|139B1~>30~none
; remove all Potions of Extreme Healing where count > 3
filterByLLs=myTestESP.esp|00001733:removeFromLLs=Skyrim.esm|39BE4~none~>3
```

This matters because it makes MLU's "cap the ceiling" a **rule about level thresholds** rather than
an enumeration of every high-tier item — the operation still needs a form to match on, but the level
predicate does the tier work. Combined with `removeObjectsByKeyword` (e.g. drop everything carrying
a Daedric material keyword), MLU's 84.6% truncation pass is expressible in a handful of lines.

**So Requiem's core move — flatten a gated ladder into a flat random pool — is one rule:**

```ini
; LCharDraugrBoss: replace the 13-entry level ladder with a flat pool of three variants
filterByLLs=Skyrim.esm|42480:clear=true:addToLLs=Skyrim.esm|DDD5D~1~1,Skyrim.esm|DDD5F~1~1,Skyrim.esm|DDD60~1~1:calcLevelAndEachItem=true
```

Entries are auto-sorted by level after insertion (`leveledlist.cpp:740`).

> ⚠️ **Gotcha: the flag setters assign, they do not OR.** Each writes `curobj->llFlags = <flag>`,
> replacing the whole flag byte. `calcForLevel=true:calcEachItem=true` on one line leaves **only**
> `CalculateForEachItemInCount`. The articles confirm this — *"Only one flag at a time can be set"*.
> Use `calcLevelAndEachItem=true` for both — **and note that is not the spelling the articles give;
> see §3.4.** `[verified]`

MLU-style truncation is equally expressible via `removeFromLLs` / `removeObjectsByKeyword` without
clearing.

### 4.3 `encounterzone/` — MLU-style banding is expressible

| Key | Effect |
|---|---|
| `minLevel=` / `maxLevel=` | set the band directly |
| `minLevelAdd=` / `maxLevelAdd=` | offset the existing value |
| `minLevelMult=` / `maxLevelMult=` | multiply the existing value |
| `location=` | reassign the zone's `LCTN` (or `null` to clear) |

Filters: `filterByEncounterZones` / `Excluded`, `filterByModNames`,
`filterByEditorIdContains` / `Or` / `Excluded`.

```ini
; Bleak Falls Barrow: fixed at exactly 20 — the zero-width band Ehlnofey wants
filterByEncounterZones=Skyrim.esm|38AB1:minLevel=20:maxLevel=20
```

The `Add`/`Mult` variants are interesting for a *global* pass — e.g. "raise every zone floor by 15"
in a single line, MLU's mean +17.1 shift approximated without enumerating 300 zones:

```ini
minLevelAdd=15
```

(A rule with no filter matches every record of that type — see `encounterzone.cpp`, where empty
filters set `found = true`.)

> ⚠️ **`minLevel`/`maxLevel` are `int8_t`.** Values outside **−128…127** are rejected with a log
> line and silently ignored. Requiem's level-250 Alduin could not be expressed as a zone bound.
> `[verified]`

### 4.4 `cell/` — reassigning zones

`cell.cpp:103` exposes `encounterZone=`, which attaches an `ExtraEncounterZone` to the cell (or
removes it with `null`). That is MLU's `C.Encounter` work — 138 cell records — as rules.

Cell filters are thin, though: `filterByCells` / `Excluded`, `filterByAcousticSpace`,
`filterByMusicType`, `filterBySkyRegion`, `filterByImageSpace`, and — **corrected 2026-07-29** —
`filterByKeywords` / `Or` / `Excluded`, which this section originally said did not exist. **No
location filter**, so cells must largely be enumerated. Useful escape hatches for compatibility:
`skipRecordByModNameContains=` and `skipRecordByLightingTemplateFromMod=`.

**The conclusion survives the correction, for a better reason** — the two filters that look like they
could target the wilderness in bulk both match *nothing* in the base game `[verified]`:

| Filter | Reads | Tamriel exterior cells carrying it |
|---|---|---|
| `filterByKeywords` | cell `Keywords` | **0 of 12,148** |
| `filterBySkyRegion` | `ExtraCellSkyRegion` (XCCM) | **0 of 12,148** |
| *(no filter exists)* | cell `Regions` (XCLR) | 6,999 of 12,148 ← the one worth requesting upstream |

`encounterZone=` also **adds** an `ExtraEncounterZone` to a cell that has none (`cell.cpp:781–802`),
not merely reassign an existing one — which is what makes the overworld reachable at all. See
`design/implementation-strategy.md` §6.3.

### 4.5 `location/` — rich filters, but it cannot set a level

`location.cpp` has the keyword filtering that `encounterzone/` lacks — `filterByKeywords`/`Or`/
`Excluded`, `filterByParentLocation`, `filterByEditorIdContains`/`Or`/`Excluded`,
`filterByMusicType`, `filterByUnreportedCrimeFaction`.

But its **operations are only** `fullName`, `keywordsToAdd`/`ToRemove`, `musicType`,
`parentLocation`, `unreportedCrimeFaction`. No level, no encounter-zone assignment. So you can
*select* "every location with `LocTypeDwarvenRuin`" and *tag* it — but you cannot turn that
selection into a difficulty band, because nothing downstream filters zones by location. See §5.3.

## 5. The limits — what SkyPatcher cannot do

These are the load-bearing gaps for Ehlnofey, all `[verified]` by absence in the source:

1. **No `GMST` support.** There is no `gmst`/`gameSetting` module. Both Requiem and MLU use game
   settings as a lever — Requiem flattens twelve `fDiffMult*` to 1.0; MLU compresses all four
   `fLeveledActorMult*`. **Neither is reachable from SkyPatcher.** A plugin is required for those
   six-to-twelve records, however small.
2. **No `LevelModifier` on placed actors.** `reference.cpp` exposes only `filterByRefs`,
   `disable` and `replaceBaseObject` — the string `LevelModifier` appears nowhere in the codebase.
   Vanilla's per-placed-actor Easy/Medium/Hard/VeryHard layer, which `CLAUDE.md` measures on **5,685
   of 10,504** placed actors and says to keep, **cannot be edited or read by SkyPatcher.**
3. **No location or keyword filter on encounter zones.** `encounterzone.cpp` filters only by
   explicit zone, mod name, and EditorID substring. So *"every zone whose location has
   `LocTypeDwarvenRuin`"* is **not expressible**. `location.cpp` can filter locations by keyword but
   can only edit keywords, music, parent and name — **it cannot set levels** (§4.5). The chain
   `LCTN keyword → ECZN level` is broken at both ends.
   → In practice a difficulty map must **enumerate zones by FormID**, or lean on
   `filterByEditorIdContainsOr` against Bethesda's zone naming. That is a real authoring cost, but
   ~360 enumerated lines is still small — and Phase 1's `dungeons.md` already has the table.
4. **No cross-record queries.** Rules are per-record predicates. There is no "NPCs *in* this
   location", no template-chain resolution like Requiem's `ActorInheritanceGraphParser`. If a level
   lives on a template, you must target the template yourself.
5. **Nothing is visible in xEdit.** No xEdit pass, no `formkey-check`, no Spriggit diff. The only
   verification is the SkyPatcher log and in-game observation — which collides directly with
   guardrail 6 (*"a clean build is not a working mod"*): here there is **no build to be clean**.
6. **Requires SKSE**, and the DLL is version-bound to game runtimes in the usual way. Which
   runtimes are supported is on the Nexus page I could not read.

## 6. Verdict for Ehlnofey

**SkyPatcher can express the deleveling core of both prior-art architectures with zero plugin
overrides.** That is the headline, and it materially changes the Phase 3 decision:

| Prior-art move | Expressible? |
|---|---|
| Requiem: flatten `LVLN` to a flat pool | ✅ `clear` + `addToLLs` + `calcLevelAndEachItem` |
| Requiem: fixed NPC levels | ✅ `filterByPCLevelMult` + `level` |
| Requiem: ally exception | ✅ `filterByFactionsExcluded` |
| Requiem: perks/spells by rule | ✅ `perksToAdd`, `spellsToAdd` (richer filters than Reqtificator) |
| MLU: `ECZN` bands | ✅ `minLevel` / `maxLevel` |
| MLU: truncate loot lists | ✅ `removeFromLLs` / `removeObjectsByKeyword` |
| MLU: reassign cell zones | ✅ `cell/encounterZone=` |
| **Requiem/MLU: GMST changes** | ❌ **needs a plugin** |
| **Keep vanilla's `LevelModifier` layer** | ❌ **not reachable at all** |
| **"All Dwarven ruins → tier 4"** | ❌ must enumerate zones |

**This is strong evidence for the hybrid** already sketched in `CLAUDE.md`, and it sharpens what
each half is for:

- **Rules (SkyPatcher INI):** the entire per-NPC, per-list, per-zone distribution. Reviewable plain
  text, no masters, no conflicts, ~360 zone lines plus a few hundred list lines. Compare Requiem's
  **108 MB** of override YAML and MLU's **22 MB**.
- **Plugin (`Ehlnofey.esp`):** only what rules cannot reach — the GMSTs, and any new records
  (keywords, new leveled lists to point rules at). Plausibly **a few dozen records**, which is
  exactly the "small hand-authored skeleton" the working recommendation asks for.

### Costs to weigh honestly

- **Hard SKSE dependency**, and a DLL that breaks on game updates until the author rebuilds. A
  plugin-only mod has no such failure mode.
- **The workspace's whole verification toolchain does not apply.** xEdit, `formkey-check`,
  Spriggit round-trip and `Test-RecordYaml.ps1` all operate on plugin records. Rules are unverifiable
  except in-game. **Ehlnofey would need a new kind of check** — at minimum a script that resolves
  every FormID referenced in the INIs against `reference/`, since a typo'd FormID fails **silently**
  (the `logger::critical` for a missing form only appears in the log).
- Guardrail 2 (*prefer a proven archetype*) is satisfied — SkyPatcher is widely used — but guardrail
  1 (*ground-truth before claiming*) is **harder**, not easier, under this design. §3.4 is the
  proof: two of the author's own documented keys do not work as written, and both fail silently.
  Any INI-checking script Ehlnofey writes should validate **key names against the parser regexes**,
  not just FormIDs.

### Open questions

1. **Does patching `ECZN` at `kDataLoaded` actually take effect?** The clamp semantics were already
   flagged `[community]` in `morrowloot.md`; doing it at runtime adds a second unknown — whether the
   engine has already cached zone data by then. **Test both together.**
2. **Save-game behaviour.** Runtime edits are not baked into a plugin, so what persists across a
   save/reload? `main.cpp` has `SaveCallback`/`LoadCallback` and SKSE co-save serialisation for
   *some* state — worth reading before assuming rules re-apply cleanly.
3. ~~Rule ordering and precedence.~~ **Answered by the articles** (§3.2): files load alphabetically
   `0`–`z`, last write wins per field, and add/remove operations compose without conflict.
4. ~~SPID comparison.~~ **Dropped deliberately.** SPID distributes *to* NPCs (spells, perks, items,
   outfits) rather than patching records, which makes it a poor fit for deleveling — it cannot
   touch leveled-list gates, NPC levels or encounter zones. SkyPatcher is the rule engine for this
   mod. (SPID remains a reasonable companion if Ehlnofey ever needs to *distribute* something.)
