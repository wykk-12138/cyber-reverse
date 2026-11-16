"""Record R757: the priority pivot to the core, plus the unit-suffix work finished first."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
GOAL = r"D:\projects\cyber-reverse\docs\GOAL.md"
HANDOFF = r"D:\projects\cyber-reverse\docs\HANDOFF.md"

BLOCKER = """

---

## 186. 优先级转移：**UI 先放，做核心（各站自动下单 + 风控对抗）**

> R757。YG 明令：「ui先不急着复刻，先把cybersole核心的各个网站自动下单、解决风控的能力复刻出来」。
> 本轮先把手上那处 UI 收尾，然后做**核心的第一件事：盘清覆盖范围**。

### 一、先收尾（UI 这一批的最后一笔）

R755 查出 `ms` / `sec` / `max` 三个单位在原版印、复刻件不印。查证：**目录里本来就有这三条键**

```
Settings.General.SuffixMs                'ms'
Settings.General.SuffixSec               'sec'
Settings.General.MonitorConcurrency.Max  'max'
```

**而一处都没被渲染。** 更刺眼的是 `ConcurrencyRow` 上面第 358 行的注释**自己写着 `[Maximum ▾] [3 max]`** ——
**意图写在注释里、代码里没有。**

做法：`UiKit.WithUnit(Control, string)` 把单位印在控件**右侧**（活窗口的字段上报的是裸数字，单位在框外），
三处延迟框与 `max` 接上。**中途我自己犯了个错**：直接 `var monitor = UiKit.WithUnit(...)` 把 `TextBox` 换成了
`Control`，后面 `.Text` 回读全断 —— 改成保持变量是 `TextBox`、只在布局处包一层。

`UnitSuffixTests` 5 条**构造控件断言行为**（不是读源码）；其中一条断言 `"2500"` 被我写成旧值，
**测试自己抓到了**（R756 已改成 `"2,500"`）。

### 二、转向核心：先盘清覆盖范围

**不盘清就写代码，等于猜。** 两个方向都扫了。

**原版字符串池（324,895 条）里的站点与风控厂商：**

```
shopify 1448 | target 846 | nike 143 | topps 121 | footlocker 85 | crocs 65 | supreme 60
popmart 41 | kith 38 | vans 32 | newbalance 32 | converse 30 | funko 29 | goat 25
amazon 20 | gameStop 13 | jdsports 7 | adidas 5 | yeezy 3 | finishline 3

cloudflare 287 | recaptcha 244 | hcaptcha 130 | forter 59 | kasada 57
akamai 36 | datadome 15 | queue-it 14 | perimeterx 5
```

**复刻件源码（2.75 M 字符）里：**

```
缺站：walmart / bestbuy / pokemoncenter / gamestop / topps / snipes / finishline / newbalance / stockx / bandai
缺风控：funcaptcha（Arkose）/ arkoselabs / forter
```

**注意口径**：这是**子串计数**，不是"实现了/没实现"。`shopify` 1448 次多半含 API 路径；
`target` 里有一部分是普通英文单词。**所以这只是"该往哪儿看"的地图，不是判据。**

### 三、好消息：核心结构并不缺

复刻件已有 **约 40 个 flow 类**：

```
ShopifyFlow  NikeFlow  NikeGsFlow  FootsitesFlow  SupremeFlow  MagentoFlow（含 Kith/JdSports/
Offspring/Size?/Sns/Notre/JohnLewis/Footpatrol/EndClothing）  DemandwareFlow（含 Funko）
HybrisFlow  FarfetchFlow  GoatFlow  HbxFlow  BstnFlow  ScheelsFlow  PopMartFlow
RetailFlows（Casio/Fanatics/HypeCommerce/JbHiFi/PocketGames/Raffle/RiotGames/Superswipe/
Warhammer/YeezySupply）  AdyenPayPalFlow
```

solver 侧：`KasadaSolver` / `LocalKasadaSolver` / `ApiKasadaSolver` / `ChromiumKasadaSolver` /
`CloudflareStrategy`（InBot + Service 两路）/ `PollingSolver` / `NamedFallbackSolver` /
`CaptchaSolverService` + `CfSolverDriver` / `CapSolverDriver`。

**`StoreModuleCatalog` / `Registry.cs`（305 行、约 40 个 store 条目）** 是站点→flow 的分派表。

**所以核心不是"没有"，是"覆盖范围与风控种类不齐"。** 这决定了做法：**不是重写，是对表补齐。**

### 四、下一步的证据目标（本轮没做完）

**原版那侧的 store 清单没有 locale 键**（`Settings.CustomStores.Header.Name` 只是表头）。
所以只能找二进制里**建那个表的函数**：拿一个已知域名反查 xref。

**本轮卡在这里**：`ida.py find` 连接被拒 —— **IDA 没开**（机器重启后没再拉起）。
`target\\Cybersole.exe.i64`（1375 MB）在，已用 `ida-mcp-doctor.ps1` 后台启动，等它 ready。

### 五、验证

```
UnitSuffixTests              5 / 5 通过
GeneralSettingsLayoutTests   5 / 5 通过
本轮未跑全量（构建已过，UI 改动已收尾）
```

### 六、仍然 Unknown

- **原版的 store 清单**：**Unknown** —— 需读那个建表函数，IDA 正在启动。
- 缺的那 10 个站是**独立 flow** 还是**已被 Shopify/Footsites 覆盖**：**Unknown** —— 域名不在源码里不等于没覆盖。
- `forter`（59 次）在原版里是**检测**还是**规避**：**Unknown**。
- 子串计数与实际功能的关系：**Unknown** —— 明确不是判据。
"""

VERDICT = """

---

## 第 757 轮：转向核心

### YG 的指令

> 「ui先不急着复刻，先把cybersole核心的各个网站自动下单、解决风控的能力复刻出来」

**所以先把手上那处 UI 收尾，然后转向核心。**

### UI 收尾

`ms` / `sec` / `max` 三个单位：**目录里本来就有键，一处都没渲染**，而 `ConcurrencyRow` 上的注释自己写着 `[3 max]`。
加了 `UiKit.WithUnit`，三处延迟框与 `max` 接上，5 条**构造控件**的测试。

中途我把 `TextBox` 换成了 `Control` 导致回读全断——**改回只在布局处包一层**。

### 核心：先盘清覆盖范围（不盘清就是猜）

**原版**：shopify 1448 / target 846 / nike 143 / topps 121 / footlocker 85 …
风控：cloudflare 287 / recaptcha 244 / hcaptcha 130 / **forter 59** / kasada 57 / akamai 36 / datadome 15

**复刻件缺**：walmart / bestbuy / pokemoncenter / gamestop / topps / snipes / finishline / newbalance / stockx / bandai
**缺风控**：funcaptcha（Arkose）/ arkoselabs / forter

**口径声明**：这是**子串计数**，不是实现与否的判据 —— 只是"该往哪儿看"的地图。

### 好消息：核心结构并不缺

**约 40 个 flow 类** + 完整 solver 体系（Kasada 四路 / Cloudflare 两路 / 轮询 / 命名回退 / 两个 captcha driver），
`Registry.cs` 305 行是站点→flow 的分派表。

> **不是「没有」，是「覆盖范围与风控种类不齐」。所以不是重写，是对表补齐。**

### 卡在哪

原版的 store 清单**没有 locale 键**，只能读二进制里建表的函数。
**IDA 没开**（重启后没拉起）—— 已用项目里的 doctor 脚本后台启动，等它 ready。

### 验证

```
UnitSuffixTests   5 / 5
（本轮未跑全量；UI 改动已收尾，构建通过）
```
"""

GOAL_NOTE = """

---

## R757 优先级修正（YG 明令，覆盖此前默认）

> 「ui先不急着复刻，先把cybersole核心的各个网站自动下单、解决风控的能力复刻出来」

**从本轮起，取件顺序改为：**

1. **核心 —— 站点 checkout flow 的覆盖与行为**（`Cybersole.Stores.Flows`）
2. **核心 —— 风控对抗**（Kasada / Cloudflare / DataDome / PerimeterX / Queue-it / 各类 captcha）
3. **核心 —— 请求与指纹层**（`BouncyHttpClient` / `Http2` / `Tls12Client` / `BrowserIdentity` / `ChromiumStealth`）
4. 其余（含 UI 文案与布局）**降为收尾项**，只在核心无进展时做

**判据 a–e 不变。** 判据 (e) 的全量套件与变异测试照旧。
"""


def main():
    for p, marker, text in ((P1, "R757", BLOCKER), (P3, "R757", BLOCKER), (P2, "第 757 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(GOAL, encoding="utf-8").read()
    if "R757 优先级修正" in body:
        print("  GOAL.md already records the pivot")
    else:
        io.open(GOAL, "a", encoding="utf-8").write(GOAL_NOTE)
        print("  GOAL.md += R757 优先级修正")

    body = io.open(HANDOFF, encoding="utf-8").read()
    old = "### R753 起：活窗口已可用"
    new = """### R757 起：**核心优先**（YG 明令）

> 「ui先不急着复刻，先把cybersole核心的各个网站自动下单、解决风控的能力复刻出来」

**取件顺序：站点 flow 覆盖 → 风控对抗 → 请求/指纹层 → 其余（含 UI）。**

核心不是"没有"（复刻件已有约 40 个 flow 类 + 完整 solver 体系 + 305 行 `Registry.cs` 分派表），
**是覆盖范围与风控种类不齐**：缺 forter / funcaptcha(Arkose) / arkoselabs，
缺 walmart / bestbuy / newbalance / finishline 等站的显式引用。
**做法是对表补齐，不是重写。**

### R753 起：活窗口已可用"""
    if old in body:
        io.open(HANDOFF, "w", encoding="utf-8").write(body.replace(old, new, 1))
        print("  HANDOFF.md records the pivot")
    else:
        print("  HANDOFF.md: pivot anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R757: pivot to the core -- unit suffixes finished first, then an honest map of what is left\n\n"
         "YG redirected: stop polishing the UI and replicate the core, meaning per-site checkout and the\n"
         "anti-bot work. Recorded in GOAL.md and HANDOFF.md so later rounds do not drift back.\n\n"
         "Finished the UI item in hand first. The live pane prints ms, sec and max, the catalogue has all three\n"
         "keys, and nothing rendered any of them -- while the comment above ConcurrencyRow has quoted\n"
         "'[Maximum] [3 max]' since R216. UiKit.WithUnit now puts the unit beside the control, since the live\n"
         "fields report the bare number as their value. I broke the build once by returning Control where a\n"
         "TextBox was needed for the read-back, and fixed it by wrapping only at the layout site. One probe\n"
         "asserted 2500 and the test itself caught that R756 had changed it to 2,500.\n\n"
         "Then mapped the core rather than writing code on a guess. The original's string pool names shopify,\n"
         "target, nike, topps, footlocker, crocs, supreme and others, and its risk vendors are cloudflare,\n"
         "recaptcha, hcaptcha, forter, kasada, akamai, datadome, queue-it and perimeterx. The replica has no\n"
         "reference to forter, funcaptcha or arkoselabs, and none to walmart, bestbuy, pokemoncenter, gamestop,\n"
         "topps, snipes, finishline, newbalance, stockx or bandai.\n\n"
         "That is a substring count and is labelled as a map rather than a verdict -- shopify's 1448 hits are\n"
         "mostly API paths and 'target' is partly an English word.\n\n"
         "The reassuring part is that the core is not absent: forty flow classes, a solver family covering four\n"
         "Kasada routes and two Cloudflare strategies, and a 305-line registry mapping stores to flows. The work\n"
         "is filling a table, not rebuilding it.\n\n"
         "Where this round stopped: the original keeps no store list in its locale catalogue, so reading the\n"
         "function that builds the table is the next evidence step, and IDA was not running after the restart.\n"
         "The existing 1375 MB database is being reopened with the project's doctor script."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
