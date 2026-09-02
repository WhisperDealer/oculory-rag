---
id: "projects/ehlnofey/design/bucket-d-provisional.txt"
title: "bucket-d-provisional.txt"
slug: "bucket-d-provisional.txt"
section: "projects/ehlnofey/design"
game: "skyrim"
kind: "design"
project: "ehlnofey"
mod: null
tags: ["ehlnofey", "deleveling", "design", "generated-data", "source:ehlnofey"]
source_repo: "ehlnofey"
source_path: "arch-docs/design/bucket-d-provisional.txt"
source_branch: "main"
source_commit: "200b34859a65a8c464e84e3285fe4422a82ecb2d"
source_dirty: false
generated: true
generator: "src/Ehlnofey/extract-requiem.ps1"
superseded: false
superseded_by: null
phase: null
confidence: {"author": 0, "community": 0, "unverified": 0, "upstream": 0, "verified": 0}
lines: 76
content_sha256: "49961ae844570152ac8740abdf64ea6df220d322361d44f2f168bc97000dd773"
synced_at: "2026-09-02T11:44:19Z"
sync_version: 1
---

# bucket-d-provisional.txt

```text
# Bucket D - 66 LVLN written as a naive vanilla flatten, PROVISIONAL.
# Requiem's versions are unusable: they delegate to REQ_LChar_VoiceSpawns_* sublists that are
# Requiem-only AND still player-gated (1/2/5/8/9/10). These are the lists archetype-tiers.md
# 4/4.1 must author by hand - in particular the LCharAnimal* biome rosters, where a naive
# flatten inherits the level-35 density-ramp mix (BearCave x7 dominant) instead of freezing
# each biome at the reference level of its assigned tier.
DLC1LCharChaurusHunter - 0029A2_Dawnguard.esm
DLC2LCharBanditBoss - 01E8B4_Dragonborn.esm
DLC2LCharBanditMagic - 01E8A8_Dragonborn.esm
DLC2LCharBanditMelee1H - 01E8A9_Dragonborn.esm
DLC2LCharBanditMelee1HDarkElfMCommoner - 0374C0_Dragonborn.esm
DLC2LCharBanditMelee1HDarkElfMCynical - 0374BE_Dragonborn.esm
DLC2LCharBanditMissile - 01E8AA_Dragonborn.esm
LCharAnimalCanyonPredator - 04229B_Skyrim.esm
LCharAnimalCanyonPrey - 04229C_Skyrim.esm
LCharAnimalCoastSnowPredator - 0422A3_Skyrim.esm
LCharAnimalCoastSnowPrey - 0422A4_Skyrim.esm
LCharAnimalForest - 01E790_Skyrim.esm
LCharAnimalForestPredator - 042297_Skyrim.esm
LCharAnimalHills - 01E78F_Skyrim.esm
LCharAnimalMarshPredator - 042295_Skyrim.esm
LCharAnimalMountainSnowPredator - 04229D_Skyrim.esm
LCharAnimalMountainSnowPrey - 0422A2_Skyrim.esm
LCharAnimalPlains - 01E78D_Skyrim.esm
LCharAnimalPlainsPredator - 042293_Skyrim.esm
LCharAnimalSnowFields - 01E78E_Skyrim.esm
LCharBanditBoss - 03DF16_Skyrim.esm
LCharBanditBossCommonerF - 01A32F_Skyrim.esm
LCharBanditBossCommonerM - 01A33A_Skyrim.esm
LCharBanditBossEvenTonedF - 01A33B_Skyrim.esm
LCharBanditBossEvenTonedM - 01A33F_Skyrim.esm
LCharBanditBossNordF - 01A340_Skyrim.esm
LCharBanditBossNordM - 01A341_Skyrim.esm
LCharBanditBossNordM2HOnly - 0E1645_Skyrim.esm
LCharBanditBossOrcM - 01B0EA_Skyrim.esm
LCharBanditMelee1H - 039CFC_Skyrim.esm
LCharBanditMelee1HTank - 03DEC9_Skyrim.esm
LCharBanditMelee2H - 03DEC8_Skyrim.esm
LCharBanditMelee2HBerserk - 03DECA_Skyrim.esm
LCharBanditMeleeAny - 03DECD_Skyrim.esm
LCharBanditMeleeCommonerF - 01A31E_Skyrim.esm
LCharBanditMeleeCommonerM - 01A319_Skyrim.esm
LCharBanditMeleeEvenTonedF - 01A322_Skyrim.esm
LCharBanditMeleeEvenTonedM - 01A323_Skyrim.esm
LCharBanditMeleeNordF - 01A321_Skyrim.esm
LCharBanditMeleeNordM - 01A320_Skyrim.esm
LCharBanditMeleeOrcM - 01B0E9_Skyrim.esm
LCharBanditMissile - 01E770_Skyrim.esm
LCharBanditMissileCommonerF - 01A342_Skyrim.esm
LCharBanditMissileCommonerM - 01A343_Skyrim.esm
LCharBanditMissileEvenTonedF - 01A344_Skyrim.esm
LCharBanditMissileEvenTonedM - 01A345_Skyrim.esm
LCharBanditMissileNordF - 01A346_Skyrim.esm
LCharBanditMissileNordM - 01A348_Skyrim.esm
LCharBanditWizard - 01E771_Skyrim.esm
LCharBanditWizardCommonerF - 01B0F0_Skyrim.esm
LCharBanditWizardCommonerM - 01B0F3_Skyrim.esm
LCharBanditWizardEvenTonedF - 01B0F4_Skyrim.esm
LCharBanditWizardEvenTonedM - 01B0F5_Skyrim.esm
LCharBanditWizardNordF - 01B0F7_Skyrim.esm
LCharBanditWizardNordM - 01B0FB_Skyrim.esm
LCharChaurus - 01FA27_Skyrim.esm
LCharDeer - 0ABEDC_Skyrim.esm
LCharElk - 0DB2AC_Skyrim.esm
LCharMudcrab - 02183E_Skyrim.esm
LCharSabrecat - 0FE2D5_Skyrim.esm
LCharSkeletonMeleeMixed - 02D2D4_Skyrim.esm
LCharVampireCompanionFrost - 0640BE_Skyrim.esm
LCharWolf - 0B83C2_Skyrim.esm
SubCharVigilantOfStendarr01 - 10C452_Skyrim.esm
SubCharVigilantOfStendarrEvenTonedF01 - 10C45B_Skyrim.esm
SubCharVigilantOfStendarrEvenTonedMAccented01 - 10C45C_Skyrim.esm
```
