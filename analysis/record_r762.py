"""Record R762: Forter added, and the repo's guard caught my wrong module count."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 190. Forter 接进厂商表；而**仓库自己的守卫抓到了我写错的 module 数**

> R762。改 `AntiBotVendors.cs`（2 常量 + 1 厂商条目 + 类注释一行）、`AntiBotVendorTests.cs`；
> 改 `replica/docs/VERDICT.md` 去掉一处硬编码数字。

### 一、Forter 的集成图景（Observation）

```
端点   https://cdn3.forter.com/events            事件上传
       https://cdn123.forter.com/?u=            带用户参数的传感器地址
       https://cdn6.forter.com/  /  https://cdn0.forter.com/
       .cdn.forter.com/prop.json                属性/配置
       https://forter.cybersole.workers.dev/    ← 它自己的 Cloudflare Worker 代理
字段   forterToken · forterCookieToken · CheckoutData.ForterToken · BuildForterSessionId
类型   ForterEnvelope · ForterEventsEncoder · SensorResponsePropInit · ForterEnvelopePropInit
杂项   \"Forter sensor generation failed\" · \"Submitting forter\"
同区另有 Create_DdBrowser / Create_DdMobileEvent / Create_DdMobileTouchEvent  ← Datadog RUM
```

**`forter.cybersole.workers.dev/` 与 DataDome 的 `datadome.cybersole.io/` 是同一个架构**：
**用自家第一方主机转发厂商流量，而不是直连厂商域名。** 这一点这个文件本来就在 DataDome 条目上强调过，
所以 Forter 也照写成具名常量 `ForterRelay`，而不是散在证据列表里。

### 二、改了什么

```
AntiBotVendors.ForterEvents = "https://cdn3.forter.com/events"
AntiBotVendors.ForterRelay  = "forter.cybersole.workers.dev/"
new Vendor("Forter", …10 条证据字面量…)
类注释里加一行 Forter
```

**`AntiBotVendorTests` 的 `Assert.Equal(6, All.Count)` 改成 7** ——
按 AGENTS.md §3 判断：**这是形状随证据变，不是行为变**（Forter 一直在镜像里，R105 那次读漏了），
所以改数字并在注释里写清原因，测试名也从 `SixVendors` 改成 `SevenVendors`。
另加一条 `ForterIsFrontedByItsOwnWorkerLikeDataDomeIs`。

### 三、**仓库自己的守卫抓到了我一个错数字**

全量跑红，失败是 `DocsConsistencyTests.TheModuleCountInVerdictMatchesTheCatalogue`：

```
catalogue: 62 modules
claims in VERDICT: 62, 22
Expected: 62   Actual: 22
```

**那个 22 是我写的。** R759/R760/R761 我三次写「复刻件有 22 个 module」，
来源是 `analysis/store_catalog.py` 的输出 —— **而真实是 62，我的脚本少算了 40 个。**

**这是本会话第四次仪器错误**，但**第一次是仓库的守卫抓的，不是我**：

| 轮 | 仪器假设 | 后果 | 谁抓到 |
|---|---|---|---|
| R753 | 标签形如 `"Startup Page"` | 假缺席 | 我自己 |
| R759 | 字段形如 `=>` | `ShopifyModule` 抽出 `?` | 我自己 |
| R760 | 店名以显示名出现 | 7 个站误判可疑 | 我自己 |
| **R762** | **只扫 `Cybersole.Stores` 下的 `StoreModuleBase` 子类** | **22 vs 62** | **`DocsConsistencyTests`** |

**修法不是把 22 改成 62，而是把数字删掉** —— 因为「数字只有一个来源」，
文档里不该有会过期的计数。改后 `claims in VERDICT: 62` 只剩一处合法声明。

**那个测试的匹配模式也值得记**：prose 里 `(\\d+)\\s*(?:个模块|modules)` 且 `n >= 20`，
**代码围栏内的输出被剥掉**（那是历史日志，不是声明）。我第一次盲改「22 个」只替换了 2 处、
文档里还剩 17 处「22」全是别的意思 —— **盲改数字是错的方法，先读匹配模式才对。**

### 四、Datadog：一个新发现，未落地

`Create_DdBrowser` / `Create_DdMobileEvent` / `Create_DdMobileTouchEvent` 说明原版**还集成 Datadog RUM**。
**复刻件零引用。** 它**不是**反爬厂商（是遥测），所以**没有塞进 `AntiBotVendors`** —— 该另找位置。
**记为待办，不硬塞。**

### 五、验证

```
AntiBotVendorTests     6 / 6 通过（含新增 1 条）
DocsConsistencyTests   7 / 7 通过
完整套件               1751 通过 / 0 失败 / 0 跳过（1745 + 6）
四项度量               4 / 0 / 17 / 78 / 0（未变）
```

### 六、仍然 Unknown

- `ForterEnvelope` 的字段与 `ForterEventsEncoder` 的编码方式：**Unknown** —— 只看到符号，未反编译。
- `prop.json` 的用途与刷新时机：**Unknown**。
- Datadog 在复刻件的落点：**Unknown**（待办）。
- 我 `store_catalog.py` 为何少算 40 个：**Unknown** —— 未查（下轮）。
"""

VERDICT = """

---

## 第 762 轮：Forter 接上了，而守卫抓到了我写错的数字

### Forter 的图景

```
cdn3.forter.com/events · cdn123.forter.com/?u= · cdn0/6.forter.com · .cdn.forter.com/prop.json
forter.cybersole.workers.dev/          ← 自家 CF Worker 代理
forterToken · forterCookieToken · CheckoutData.ForterToken · BuildForterSessionId
ForterEnvelope · ForterEventsEncoder
```

**`forter.cybersole.workers.dev/` 与 DataDome 的 `datadome.cybersole.io/` 是同一架构**：
**第一方主机转发厂商流量。** 所以写成具名常量 `ForterRelay`，不散在证据列表里。

### 而仓库的守卫抓到了我一个错数字

```
DocsConsistencyTests: catalogue 62 modules / claims in VERDICT: 62, 22
```

**那个 22 是我写的** —— R759/R760/R761 三次说「22 个 module」，来源是我 `store_catalog.py` 的输出，
**真实 62，脚本少算 40 个。**

**本会话第四次仪器错误，第一次由仓库的守卫抓到：**

| 轮 | 仪器假设 | 谁抓到 |
|---|---|---|
| R753 | 标签形如 `"Startup Page"` | 我自己 |
| R759 | 字段形如 `=>` | 我自己 |
| R760 | 店名以显示名出现 | 我自己 |
| **R762** | **只扫一类子类** | **`DocsConsistencyTests`** |

**修法不是把 22 改成 62，而是把数字删掉** —— 数字只有一个来源，文档不该有会过期的计数。

### 一个方法教训

那个测试的模式是 prose 里 `(\\d+)\\s*(?:个模块|modules)` 且 `n >= 20`，围栏内输出剥掉。
**我第一次盲改「22 个」只中 2 处，剩 17 处「22」全是别的意思** ——
**盲改数字是错的方法，先读匹配模式才对。**

### Datadog：新发现，未落地

`Create_DdBrowser` / `Create_DdMobileEvent` / `Create_DdMobileTouchEvent` → 原版还集成 Datadog RUM。
**复刻件零。** 它不是反爬厂商，**所以没硬塞进 `AntiBotVendors`**。

### 验证

```
AntiBotVendorTests 6/6 · DocsConsistencyTests 7/7
完整套件 1751 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```
"""


def main():
    for p, marker, text in ((P1, "R762", BLOCKER), (P3, "R762", BLOCKER), (P2, "第 762 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R762: Forter joins the vendor table, and the repo's own guard caught my wrong module count\n\n"
         "Forter's contract from the binary: the cdn3 events endpoint, the cdn123 host carrying a user parameter,\n"
         "cdn0 and cdn6, prop.json, and forter.cybersole.workers.dev. That last one matters architecturally -- it\n"
         "is a first-party Worker fronting the vendor, exactly as datadome.cybersole.io does for DataDome, which\n"
         "this file already documents. So the relay gets its own named constant rather than sitting loose in the\n"
         "evidence list, and the vendor entry carries the token fields and the envelope/encoder types.\n\n"
         "The vendor count assertion moves from six to seven. That is a shape change following the evidence, not\n"
         "a behaviour change: Forter was always in the image and R105's read missed it. The test is renamed and\n"
         "the reason recorded.\n\n"
         "The full suite then went red on DocsConsistencyTests, and the failure was mine: VERDICT claimed 22\n"
         "modules where the catalogue has 62. The 22 came from analysis/store_catalog.py, which walks classes\n"
         "deriving from StoreModuleBase under one project -- it undercounts by forty. This is the fourth\n"
         "instrument error of the session and the first caught by something other than me.\n\n"
         "The fix was to delete the number rather than correct it, because documents should not carry counts that\n"
         "expire. Worth keeping: my first attempt blind-replaced every '22 个' in a 300 KB document and hit two\n"
         "occurrences, while seventeen others meant unrelated things. The test's pattern is prose-only arithmetic\n"
         "on module counts, so reading the pattern first was the right order.\n\n"
         "Also found: Create_DdBrowser and the DdMobile event builders show the original integrates Datadog RUM,\n"
         "which the replica lacks. It is telemetry rather than anti-bot, so it was not forced into the vendor list.\n\n"
         "Suite 1751 pass / 0 fail; four metrics unchanged."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
