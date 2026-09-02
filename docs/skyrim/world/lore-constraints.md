---
id: "skyrim/world/lore-constraints"
title: "Lore constraints"
slug: "lore-constraints"
section: "skyrim/world"
game: "skyrim"
kind: "world"
project: null
mod: null
tags: ["skyrim", "world-research", "vanilla", "ehlnofey", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/world/lore-constraints.md"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: false
generator: null
superseded: false
superseded_by: null
phase: "Phase 1, document 6"
confidence: {"author": 0, "community": 10, "unverified": 5, "upstream": 0, "verified": 11}
lines: 267
content_sha256: "590affec6fe356ef8f2cddef0cff03059d4d2a82b26ea76079a1150658f79d6e"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# Lore constraints

**Phase 1, document 6.** What the fiction permits — the check on *"just make it harder."*

Every other Phase 1 document asks what the records do. This one asks what the setting will *allow*
Ehlnofey to do to them. It exists because a deleveling mod is constantly tempted to solve a balance
problem by moving a number, and some of those numbers are load-bearing for the world's fiction.

Confidence marks: `[verified]` = read in `reference/`, `[community]` = established lore/modding
knowledge from published sources, `[unverified]` = plausible, unchecked.

**Method.** In-repo records first (`reference/Base/*/Books/` are citable primary sources — the game's
own in-world texts), then UESP for the wider setting. Every claim below names either a FormKey or a
source link.

---

## 1. The central finding: the lore hierarchy *is* the level ladder

Skyrim's tier ladders are not anonymous. Every archetype's tiers carry **lore-bearing display names**,
and those names are already ordered by power. Pulling the English `Name:` off each tier record and
sorting by its static level `[verified]`:

| Archetype | Tier ladder as the game names it |
|---|---|
| **Draugr** | Draugr (1) → Restless Draugr (6) → Draugr Wight (13) → Draugr Scourge (21) → **Draugr Deathlord** (30) |
| Draugr bosses | Draugr Overlord (7) → Wight Lord (15) → Scourge Lord (24) → **Death Overlord** (34) |
| **Bandit** | Bandit (1) → Outlaw (5) → Thug (9) → Highwayman (14) → Plunderer (19) → **Marauder** (25) |
| **Forsworn** | Forsworn (1) → Forager (6) → Looter (14) → Pillager (24) → Ravager (34) → **Warlord** (46) |
| Forsworn boss | **Briarheart** (7 → 51 by tier) |
| **Vampire** | Fledgling (1) → Vampire (6) → Blooded (12) → Mistwalker (20) → Nightstalker (28) → Ancient (38) → **Volkihar** (48) → **Volkihar Master** (53) |
| **Falmer** | Falmer (9) → Skulker (15) → Gloomlurker (22) → Nightprowler (30) → **Shadowmaster** (38) |
| **Warlock** | Wizard (1) → Apprentice Conjurer (6) → Conjurer Adept (12) → Conjurer (19) → Ascendant Conjurer (27) → Master Conjurer (36) → **Arch Conjurer** (46) |
| **Dremora** | Churl (6) → Caitiff (12) → Kynval (19) → Kynreeve (27) → Markynaz (36) → **Valkynaz** (46) |

**This is the answer to bone 2's hardest question.** `progression.md` established that nothing gates
the world and that legibility is the only protection a player has. `factions.md` established there is
no faction-level lever for it. But the *name* is a lever, it is already in place, and it is the thing
a player actually reads. A character who sees "Draugr Deathlord" knows what they are looking at
without a level number ever appearing on screen.

**Constraint:** Ehlnofey must keep tier names aligned with tier power. If a rebalance makes a
"Restless Draugr" more dangerous than a "Draugr Scourge", it has broken the only legibility mechanism
the game has. Names are not decoration — under a fixed world they become the UI.

---

## 2. The proof case: Dremora

The in-game book **`Varieties of Daedra`** (`Book3ValuableVarietiesofDaedra`) sets out the Dremora
caste ladder explicitly `[verified]`:

> "The least of kyn castes are the **Churls**, the undistinguished rabble of the lowest rank of
> Dremora… Next in rank are the **Caitiffs**, creatures of uncalculating zeal… The highest of the
> regular rank-and-file of Dremora troops are the **Kynvals**, warrior-knights who have distinguished
> themselves in battle… Above the rank and file warriors of the Churl, Caitiff, and Kynval castes are
> the officer castes… The highest rank of Dremora is the **Valkynaz**, or 'prince'… The Valkynaz are
> rarely encountered on Tamriel."

And `EncDremoraMelee01`–`06` are named **Churl / Caitiff / Kynval / Kynreeve / Markynaz / Valkynaz**
at levels **6 / 12 / 19 / 27 / 36 / 46**. `[verified]`

The book's ladder and the record's ladder are the same object. The rarity claim is honoured too — the
Valkynaz sits at the top gate, so vanilla players almost never meet one.

Two details worth recording:

- Skyrim compresses the eight lore ranks to six, dropping **Varlet** (below Churl) and **Kynmarcher**
  (between Kynreeve and Markynaz). `[community]` — UESP gives all eight.
- `EncDremoraMelee06` is misspelled **"Valynaz"** while the Missile and Warlock tier-6 records
  correctly say "Valkynaz". `[verified]` A one-character vanilla typo; harmless, but if Ehlnofey
  touches these records it may as well fix it.

**Constraint:** the Dremora ladder is fixed by published lore and must not be reordered. If Ehlnofey
needs a stronger low-tier daedra it should add a Varlet below Churl, not promote a Churl.

---

## 3. Per-archetype lore constraints

What the fiction requires, permits, and forbids — for each family a deleveling pass will touch.

### Draugr and the Dragon Cult

Dragon Priests were the ruling class of the Dragon Cult; when they died their followers were killed,
reanimated and sealed in the tomb, waking periodically to **transfer energy to the priest** and sustain
his undeath. `[community]` The in-game books `The Dragon War` (`Book3ValuableTheDragonWar`) and
`Amongst the Draugr` (`Book3ValuableAmongstTheDraugr`) carry the same account. `[verified]`

- **Required:** a Dragon Priest must outrank every draugr in its own barrow. Vanilla honours this —
  priests are static **50**, the top draugr boss is **50**, ordinary draugr cap at 30.
- **Required:** draugr power should track the *tomb*, not the wanderer. They are bound to a place by
  definition, which makes them the archetype most naturally suited to a fixed, per-dungeon level.
- **Permitted:** wide spread. Restless Draugr through Deathlord is already 1→30.

### Falmer

The Falmer are the **Betrayed** — Snow Elves who sheltered with the Dwemer and were blinded by a toxic
fungus, degenerating over millennia. `[community]` `The Falmer: A Study` (`Book3ValuableFalmer`)
is the in-game source. `[verified]` They farm chaurus and keep frostbite spiders.

- **Required:** Falmer belong underground and in Dwemer ruins. Their placement is already
  lore-correct (`regions.md`: Winterhold has FalmerHive ×4 and CaveIce ×6).
- **Required:** the Falmer/chaurus pairing is symbiotic, not incidental — `factions.md` §5 shows
  `FalmerFaction` **Ally** `ChaurusFaction`. Do not separate them by tier.
- **Tension:** vanilla Falmer *shamans* cap at level 25 while melee Falmer reach 38
  (`enemy-taxonomy.md` §2.4). Lore gives no reason for the shaman to be weaker; the gap is a
  capability decision (spells vs. stats), not a fictional one. Ehlnofey may close it.

### Forsworn, hagravens and Briarhearts

Forsworn cells are led by hagraven "matrons" or **Briarheart** warriors. The Briarheart rite is
performed *by hagravens*, communing with Hircine: the subject's heart is removed and a briar heart set
in its place. King Faolan — **Red Eagle** — was the first Briarheart. `[community]`
In-game: `The "Madmen" of the Reach` (`Book2CommonMadmenoftheReach`) and
`Herbane's Bestiary: Hagravens` (`Book2CommonHagravens`). `[verified]`

- **Required:** hagravens outrank ordinary Forsworn — they *make* the Briarhearts. Vanilla has
  hagravens at static **20** while base Forsworn start at 1, and Briarhearts are the boss tier.
  Consistent.
- **Required:** Briarhearts are elite, not rank-and-file. Keep them a boss/champion tier.
- **Note:** Red Eagle himself is implemented as a **draugr boss** (`enemy-taxonomy` / `unique-enemies`
  §2.1 — leveled via `LCharDraugrBoss`), which is lore-defensible: he is a barrow-bound revenant by
  4E 201, not a living Briarheart.

### Vampires

Harkon and his family are **pure-blooded** Vampire Lords, gifted directly by Molag Bal; the Volkihar
bloodline **thins with each generation**, and the court holds its thin-blooded mainland descendants in
contempt. `[community]` In-game: `Immortal Blood` (`Book0ImmortalBlood`). `[verified]`

- **Required — and vanilla already does it:** the ladder must run thin-blooded → pure-blooded. It
  literally ends at **Volkihar Vampire (48)** and **Volkihar Master Vampire (53)**, above every
  mainland tier. This is the cleanest lore-to-record mapping in the game after the Dremora.
- **Constraint:** Harkon must sit above his own court. He is `PcLevelMult` ×1.2 / ×1.4
  (`unique-enemies.md` §6.1) while his courtiers are ×1 — preserved if all are fixed proportionally.

### Dwemer automatons

Automatons are constructs left running in sealed ruins, not a population. Centurions are the apex.
`[community]`

- **Required:** Centurions above Spheres above Spiders. Vanilla: Spider 6/12/16, Sphere 16/24/30,
  Centurion 24/30/36. Consistent.
- **Permitted, and arguably required:** automatons need not be gated by player level at all — they
  are machines in a locked ruin. This makes them the *best* candidate archetype for a strict fixed
  tier, and the fiction actively supports "you are not ready for this ruin."

### Giants and mammoths

Unprovoked giants are **passive**. They are semi-nomadic herders; attack a mammoth and the giant
responds. `[community]` In-game: `Lore:All About Giants` / `Giants: A Discourse` exist in the wider
setting; Skyrim's own implementation matches.

- **Hard constraint:** giants are **not** hostile-by-default, and `factions.md` §3 confirms
  `GiantFaction` has no Enemy relation to the player. A deleveling pass must not make giant camps
  aggressive to raise difficulty — that contradicts both the records and the fiction.
- **Note:** giants are already fully deleveled (static **32**, `LCharGiant` single-gate) and are the
  best existing example of bone 1 working. A level-32 creature standing peacefully in a level-2 zone
  *is* legibility: the player can walk up, observe, and choose.

### Daedra of Apocrypha

**Lurkers** and **Seekers** serve Hermaeus Mora, guarding forbidden knowledge in Apocrypha.
`[community]` Seekers are masters of illusion; Lurkers are amphibious guardians.

- **Required:** they belong to Apocrypha and the Black Books, not to Solstheim's surface. Vanilla
  honours this — the seven Black Book zones are a flat MinLevel **25** (`regions.md` §4.3).
- **Permitted:** Apocrypha having *no internal gradient* is fictionally fine. It is one realm,
  entered by one means, and Mora's servants have no reason to be graded by which book you opened.
  Ehlnofey should keep it flat and simply pick the height.

### Dragons

The dragon ladder (Dragon 10 → Blood 20 → Frost 30 → Elder 40 → Ancient 50) is an age hierarchy, and
`Atlas of Dragons` (`MQPaarthurnaxBook`) exists in game. `[verified]`

- **Required:** Alduin above all others. He is the only `PcLevelMult` ×1.2 [10–100].
- **Constraint noted in `unique-enemies.md` §3:** most "named" dragons have no record and inherit the
  generic ladder. Naming a dragon does not make it stronger in vanilla, and lore does not require it
  to — Mirmulnir is explicitly an ordinary dragon.

---

## 4. Where lore and a naive deleveling collide

Five places where "just make it harder" would break the fiction. These are the reason this document
exists.

1. **Do not make passive things hostile.** Giants, mammoths, and most `PredatorFaction` wildlife are
   neutral by design and by lore. Difficulty must come from *what they are*, not from aggression.
2. **Do not reorder a named ladder.** Dremora castes, Volkihar bloodline purity and the Dragon Cult
   hierarchy are published, in-game-documented orders. Changing relative power inside them is a lore
   error even if the absolute numbers improve.
3. **Do not level a place above its fiction.** A bandit camp is bandits. Making Embershard Mine
   level 30 to protect a new player is backwards — `progression.md` §5 shows Bethesda's answer was a
   *cap*, not a floor.
4. **Do not delete the `LevelGate*` globals without replacing their function.** They exist so a
   level-5 character does not meet a frost troll on the road (`progression.md` §2). Removing them is
   defensible under bone 1, but the fiction then requires the *geography* to carry the warning
   instead — frost trolls belong on mountains, and the player must be able to see the mountain.
5. **Do not let capability drift from name.** A "Master Conjurer" that cannot summon a Dremora
   Kynval is a lore failure that no level number fixes. `enemy-taxonomy.md` §3 shows capability is a
   separate axis from level; the names commit Ehlnofey to keeping them in step.

---

## 5. What this gives Phase 3

1. **`design/tiers.md` should adopt the existing names as the tier vocabulary.** The ladders in §1
   are already fictionally ordered, already player-facing, and already roughly evenly spaced. Naming
   Ehlnofey's tiers after them costs nothing and buys legibility for free.
2. **The Dremora ladder is the calibration reference.** Six named castes at 6/12/19/27/36/46, with an
   in-game book stating the order. If a proposed tier system cannot express that ladder cleanly, the
   tier system is wrong.
3. **Automatons, draugr and Apocrypha are the safest archetypes to fix hard** — all three are
   fictionally *static populations* in sealed places.
4. **Wildlife and giants are the most constrained** — they must stay passive, so their difficulty
   contribution is bounded by design.
5. **Solstheim's higher ceiling is lore-supported.** Ash Spawn, Lurkers, Seekers and Karstaag are
   categorically stranger than mainland fauna; `unique-enemies.md` §8 shows the DLC reaching 90 where
   Skyrim stops at 50. That is a fictional difference, not an inconsistency to normalise away.

## 6. Open questions

1. **Does the tier-name vocabulary extend cleanly to a fixed world?** Vanilla names describe *rank
   within an archetype*. Ehlnofey needs names that also communicate *absolute* danger across
   archetypes — is "Draugr Scourge" more dangerous than "Forsworn Ravager"? The player has no way to
   know. `[unverified]` — may need a cross-archetype visual or naming convention.
2. **How much lore support is there for regional difficulty?** `regions.md` found vanilla's gradient
   is placement-based. The Reach as a hostile homeland is well-supported; a general "north is harder"
   rule is not. `[unverified]`
3. **Are there in-game books that state relative power between factions?** Only within-faction
   ladders were found here. A cross-faction statement would be very valuable. `[unverified]`
4. **What does the Skaal / All-Maker material imply** about Solstheim's creatures being outside
   Nirn's normal order? Not surveyed. `[unverified]`

---

## Sources

In-repo primary sources (`reference/Base/01Skyrim/Books/`), all `[verified]`:
`Book3ValuableVarietiesofDaedra` · `Book3ValuableFalmer` · `Book3ValuableTheDragonWar` ·
`Book3ValuableAmongstTheDraugr` · `Book0ImmortalBlood` · `Book2CommonMadmenoftheReach` ·
`Book2CommonHagravens` · `Book3ValuableSnowPrince` · `Book3ValuableLostLegends` · `MQPaarthurnaxBook`

External lore, `[community]`:

- [Lore:Dremora](https://en.uesp.net/wiki/Lore:Dremora)
- [Lore:Varieties of Daedra](https://en.uesp.net/wiki/Lore:Varieties_of_Daedra)
- [Lore:Dragon Cult](https://en.uesp.net/wiki/Lore:Dragon_Cult)
- [Lore:Dragon Priest](https://en.uesp.net/wiki/Lore:Dragon_Priest)
- [Lore:Draugr and the Dragon Cult](https://en.uesp.net/wiki/Lore:Draugr_and_the_Dragon_Cult)
- [Lore:Falmer](https://en.uesp.net/wiki/Lore:Falmer)
- [Lore:Snow Elf](https://en.uesp.net/wiki/Lore:Snow_Elf)
- [Lore:Briarheart](https://en.uesp.net/wiki/Lore:Briarheart)
- [Lore:Forsworn](https://en.uesp.net/wiki/Lore:Forsworn)
- [Lore:Hagraven](https://en.uesp.net/wiki/Lore:Hagraven)
- [Lore:Volkihar](https://en.uesp.net/wiki/Lore:Volkihar)
- [Lore:Harkon](https://en.uesp.net/wiki/Lore:Harkon)
- [Lore:Vampire](https://en.uesp.net/wiki/Lore:Vampire)
- [Lore:Lurker](https://en.uesp.net/wiki/Lore:Lurker)
- [Lore:Seeker](https://en.uesp.net/wiki/Lore:Seeker)
- [Lore:Apocrypha](https://en.uesp.net/wiki/Lore:Apocrypha)
- [Lore:Giant](https://en.uesp.net/wiki/Lore:Giant)
- [Lore:Mammoth](https://en.uesp.net/wiki/Lore:Mammoth)
- [Lore:All About Giants](https://en.uesp.net/wiki/Lore:All_About_Giants)
