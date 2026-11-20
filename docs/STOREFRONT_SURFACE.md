# 镜像的店铺面 vs 复刻件（由 `python analysis/storefront_gap.py --write-doc` 生成）

> **这张表说的是"未列名"，不是"未处理"**：复刻件的 `ShopifyFlow` 是通用 flow，
> 任何 Shopify 店都能跑。没有目录条目只说明**没有这家店的专用条目**。

| 项 | 值 |
|---|---|
| 镜像里的裸源站（`https://host` / `https://www.host`，密集成串者） | 2669 |
| 复刻件源码里形如域名的字面量 | 857 |
| 其中可归并到注册域 | 800 |
| 无对应条目的主机 | 1319 |
| 无对应条目的**注册域** | **1213** |

## 方法上的两个筛子

- **只收裸源站**（不带路径的 `https://host`）——报错信息里引用过的 URL 由此被挡掉。
- **只收密集成串者**（±0x800 字节内有 ≥3 个同类）——镜像的店铺表是字典序大表，
  孤立的裸源站多半出现在别的语境里。
- 基础设施词表（支付 / CDN / 分析 / 证书）在脚本里显式列出，可被反驳。

## 未列名的注册域（前 200 个，按字典序）

| 注册域 |
|---|
| `1290sqm.com` |
| `152store.com` |
| `303boards.com` |
| `401games.ca` |
| `401tcgsupply.com` |
| `418skate.com` |
| `4elementos.com` |
| `4ucaps.com` |
| `5pm.fr` |
| `7017reign.com` |
| `7hillsroma.com` |
| `a-feeling.us` |
| `abovethecloudsstore.com` |
| `acallday.com` |
| `actawear.com` |
| `addictmiami.com` |
| `adriftshop.com` |
| `afistfulofdice.co.uk` |
| `aftermkt.co.uk` |
| `aimeleondore.com` |
| `airconcentre.co.uk` |
| `aj-tcg.co.uk` |
| `ajcollectables.com.au` |
| `ajogar.com` |
| `ajtoys.co.uk` |
| `alcrecords.com` |
| `alexzono.com` |
| `allhearts-mall.jp` |
| `alltheright.com` |
| `allthingsgames.co.uk` |
| `aloyoga.com` |
| `alphaicon.com` |
| `alphaindustries.co.jp` |
| `amazingames.ch` |
| `ambushdesign.com` |
| `amctheatresshop.com` |
| `analogue.co` |
| `andmary.co.jp` |
| `andwang.shop` |
| `anicorn-watches.com` |
| `animalkingdoms.co.nz` |
| `ansh46.com` |
| `anta.com` |
| `antipromo.com` |
| `antisocialsocialclub.com` |
| `antonia.it` |
| `antonioli.eu` |
| `apbstore.com` |
| `apolina-kids.com` |
| `apothicarte.com` |
| `apresse.jp` |
| `arcana-tcg.com` |
| `architectureandsneakers.com` |
| `arcitsours.com` |
| `arianagrande.com` |
| `arionline.com` |
| `artsandrecstore.com` |
| `ash-tcg.com` |
| `ashdowngaming.co.uk` |
| `asics.com` |
| `asossamplesale.com` |
| `asphaltgold.com` |
| `athenagames.com` |
| `atlasskateboarding.com` |
| `atmos-kl.com` |
| `atmos.co.id` |
| `atmos.ph` |
| `atmospink.co.id` |
| `australianspecialtycoins.com.au` |
| `awakenyclothing.com` |
| `babyssb.co.jp` |
| `bad-world.co.uk` |
| `badbunnyadidas.com` |
| `badwolfgaming.co.uk` |
| `bagosbreaks.co.uk` |
| `bakastore.ch` |
| `baklavafleamarket.com` |
| `balibu.ch` |
| `bape.com` |
| `barnesandnoble.com` |
| `basistheory.com` |
| `bazingacards.com` |
| `bbbranded.com` |
| `bdgastore.com` |
| `beachbreakshop.net` |
| `beamcardshop.com` |
| `beaniegames.co.uk` |
| `bearwalker.com` |
| `beaspunge.com` |
| `belgiumpokecenter.com` |
| `bellerose.com` |
| `ben-g.nl` |
| `bestcollectables.co.uk` |
| `bettergiftshop.com` |
| `betterwithage.co` |
| `bhawar.com` |
| `bigairshop.com` |
| `bigonelectricals.co.uk` |
| `billieeilish.com` |
| `binderful.co.uk` |
| `binderly.co.uk` |
| `birthoftheteenager.com` |
| `blackscreenrecords.com` |
| `blacksheepskateshop.com` |
| `blackyachtrock.com` |
| `blendsus.com` |
| `blientele.com` |
| `blonded.co` |
| `blood-records.co.uk` |
| `blowoutshop.de` |
| `blueflowers.com` |
| `bluetilesc.com` |
| `bmthofficial.com` |
| `boardgamebliss.com` |
| `bode.com` |
| `bonkers-shop.com` |
| `booghe.co.uk` |
| `boosterbox.ch` |
| `bootcamp.com.ph` |
| `boredofsouthsea.co.uk` |
| `bornxraised.com` |
| `bottleneckgallery.com` |
| `bouncewear.com` |
| `bournetoys.co.uk` |
| `bowsandarrowsberkeley.com` |
| `boxlunch.com` |
| `bratz.com` |
| `bremnertcg.co.uk` |
| `brickheadscollectables.com` |
| `bristolindependentgaming.co.uk` |
| `brokenplanet.com` |
| `brooklyn-shop.de` |
| `brooklynprojects.com` |
| `bseskate.com` |
| `buffering.jp` |
| `burberry.com` |
| `burnrubbersneakers.com` |
| `burton.com` |
| `buttercuplynne.com` |
| `buzzballz.com` |
| `buzzzskateshop.com` |
| `cactusplantfleamarket.com` |
| `calif.cc` |
| `canary---yellow.com` |
| `captaincard.ch` |
| `captcha-delivery.com` |
| `card-collective.com` |
| `card-collector.net` |
| `cardbot.com.au` |
| `cardboyz.com` |
| `cardcollectors.au` |
| `cardcollectorsuk.com` |
| `cardcosmos.de` |
| `cardfiends.co.uk` |
| `cardgalaxy.co.uk` |
| `cardgameclub.it` |
| `cardmaniac.ch` |
| `cardsdice.ch` |
| `cardtreasure.ch` |
| `cardverse.it` |
| `cardxchange.uk` |
| `cardzone.es` |
| `carhartt-wip.com` |
| `carhartt-wip.jp` |
| `carteonepiece.fr` |
| `cashatmaxx.co.uk` |
| `casio-intl.com` |
| `catchacard.ca` |
| `catscollectiblestcg.com` |
| `ccs.com` |
| `cdgcdgcdg.com` |
| `ceciliebahnsen.com` |
| `centretx.com` |
| `chalicecollectibles.com` |
| `challenger.sg` |
| `champssports.ca` |
| `character.com` |
| `charlixcx.com` |
| `cherry-fukuoka.com` |
| `cherrycollectables.com.au` |
| `chezmaman.com` |
| `chiefcards.co.uk` |
| `chiikawamarket.jp` |
| `chinacloudapi.cn` |
| `chinatownmarket.com` |
| `chokeholdcollectibles.com` |
| `christoysandfidgets.co.uk` |
| `circleshop.fr` |
| `citysports.com` |
| `civilclothing.com` |
| `civilizednationshop.com` |
| `cjhendrystudio.com` |
| `clairo.com` |
| `clickandcollectables.com.au` |
| `cmpop.co.uk` |
| `cncpts.ae` |
| `collectablesemporium.au` |
| `collectbydesign.co.uk` |
| `collecteebles.co.uk` |
| `collectiblemadness.com.au` |

> 其余 1013 个：`python analysis/storefront_gap.py --roots --limit 1213`。
