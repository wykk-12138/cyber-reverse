"""Record R819: the prune gate fix, and the stale-status defect the changed network exposed."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 243. **两个 prune 没按档位 gate，把桌面档的 `window.chrome` 删掉了**

> R819。`ChromiumBridge.cs`：把 global/document 两个 prune 放进已有的 Apple gate。

### 一、怎么发现的

上一轮全量里有两条失败，一条是我的文档措辞，另一条我只记了一句「被 metrics 默认排除」就放过了。
**这一轮回去查它，是真缺陷。**

```
ChromiumStealthTests.TheRestOfTheFingerprintLooksOrdinary
  {"chrome":"undefined","runtime":"undefined","plugins":5,"languages":"en-US,en",
   "cores":8,"memory":8,"vendor":"Intel Inc.","uaCh":"Chromium|Google Chrome|Not_A Brand"}
```

**八项里六项正确，只有 `chrome` 与 `runtime` 是 `undefined`。**
**而 Kasada 护的店第一件事就是查 `typeof window.chrome === 'object'`。**

### 二、为什么

`GlobalPrune` 的职责是「**删掉设备清单里没有的每一个 window 名字**」。而那份清单是 **iPhone 的** ——
`WindowNameTable` 记着 1062 个名字，来自一台被捕获设备上的 `Object.getOwnPropertyNames(window)`。

**拿 iPhone 的清单去 prune 一个桌面档，就会把桌面独有的名字全删掉，`chrome` 是其中之一。**

**而代码里本来就有这个规矩** —— `ChromiumBridge.cs` 第 344 行的注释写着：

> R193: gated on the device claim, like every other body that asserts iPhone facts.
> **A desktop profile must not inherit iPhone-only globals.**

**`NavPrune`、`MobileNavigator` 都已经在这个 gate 里，只有第 331–332 行那两个 prune 没有。**

### 三、改了什么

```csharp
if (MobileSurface.IsAppleUserAgent(userAgent))
{
    surfaceBody += GlobalPrune.GlobalBodyJs();
    surfaceBody += GlobalPrune.DocumentBodyJs();
}
```

**顺序不变**（仍在 `WindowOrderWrap` 之后、`CssStyleProperties` 之前），**只加了一层条件。**

### 四、验证

```
改前： {"chrome":"undefined","runtime":"undefined", ...}
改后： {"chrome":"object",   "runtime":"object",    ... 其余六项不变}

dotnet test --filter ChromiumStealthTests   5 通过 / 0 失败
```

**为什么它能烂着**：这条用例带 `[Trait("Speed","Slow")]`、要驱动真 Chrome，
**`metrics_report.py` 默认排除它** —— 于是套件绿着，缺陷在。

### 五、顺带诊出第二个缺陷：**`lastStatus` 会跨步残留**

改完后全量仍是 1765 / 1 失败：

```
ModuleRobustnessTests.Monitor_Survives_An_Unreachable_Host(id: "poq-app")
  Expected: Error    Actual: Captcha
```

**这一条 R818 那次全量是过的，所以不是我的改动引起的 —— 是网络变了，把它暴露了。**

**机制：**

```csharp
private static int? LastStatus(FlowContext ctx) =>
    ctx.Session.Vars.TryGetValue("lastStatus", out var raw) && int.TryParse(raw, out var code)
        ? code : null;
```

**`lastStatus` 只有一个槽位，每次请求覆盖。**

1. `Init` 打 `platform.poq.io` → 拿到 **403** → 写进 `lastStatus`
2. `GetHome` 打 `https://no-such-host.invalid/...` → **DNS 失败，根本不产生状态码**
3. `ClassifyMonitorFailure` 读 `lastStatus` → 仍是 **403** → 判成 `Captcha`

**一个从来不解析的主机，被报告成验证码墙。**

**`ClassifyMonitorFailure` 自己的注释写着「A 403 from an anti-bot is a captcha wall … very different from
"the host is down"」** —— **它的意图是对的，但它读的那个槽位不是这一步的状态。**

**这条没修**：`lastStatus` 的**写入方不在 `StoreFlowRunner.cs` 里**（该文件里只出现一次，是读），
**要找写入点才能决定是把槽位在每步前清空，还是改成按步记录。下一轮做。**

### 六、验证（本轮）

```
dotnet test --filter ChromiumStealthTests       5 通过 / 0 失败
dotnet test --filter DocsConsistencyTests       7 通过 / 0 失败
python tools\\metrics_report.py                  1765 通过 / 1 失败（poq-app，原因见上）
四项度量                                         4 / 0 / 17 / 78 / 0（未变）
```

**套件不是绿的，而原因是已知的、有机制的、下一轮要修的。** **这个状态要写着，不能抹平。**

### 七、仍然 Unknown

- **`platform.poq.io` 现在是否真的返 403**：**Inference（高）** —— 从「403 被继承」反推，
  **没有单独抓一次确认。**
- **`lastStatus` 的写入方在哪**：**Unknown** —— 本轮没找到，下一轮第一件事。
- **除 `poq-app` 外还有多少模块会踩这个残留**：**Unknown** ——
  这条用例是 `[Theory]` 跑全部 63 个模块，**只有 poq-app 红，说明其余模块的首步不产生 403。**

### 八、教训

**上一轮我把这条失败记成「被 metrics 默认排除」，然后放过了。**
**「被默认排除」说的是它不在定期跑的范围里，不是它不重要 —— 而它恰恰覆盖着默认套件看不到的那一层。**
"""

VERDICT = """

---

## 第 819 轮：两个 prune 没 gate，删掉了桌面档的 window.chrome

### 发现

```
{"chrome":"undefined","runtime":"undefined","plugins":5,...,"vendor":"Intel Inc."}
```

**八项里六项对，只有 `chrome`/`runtime` 是 undefined —— 而 Kasada 第一件事就是查它。**

### 为什么

`GlobalPrune` 删「设备清单里没有的 window 名字」，**而清单是 iPhone 的**（`WindowNameTable`，1062 个名字）。
拿 iPhone 的清单 prune 桌面档，就会删掉桌面独有的名字。

**而规矩本来就有**（R193 注释）：「A desktop profile must not inherit iPhone-only globals」。
`NavPrune`、`MobileNavigator` 都在 gate 里，**只有那两个 prune 没有**。

### 改了什么

```csharp
if (MobileSurface.IsAppleUserAgent(userAgent))
{
    surfaceBody += GlobalPrune.GlobalBodyJs();
    surfaceBody += GlobalPrune.DocumentBodyJs();
}
```

**顺序不变，只加一层条件。**

```
改前 chrome=undefined  →  改后 chrome=object（其余六项不变）
ChromiumStealthTests  5 通过 / 0 失败
```

**为什么能烂着**：它带 `Speed=Slow`、要驱动真 Chrome，**默认套件排除它** —— 套件绿着，缺陷在。

### 顺带诊出第二个：`lastStatus` 跨步残留

```
Monitor_Survives_An_Unreachable_Host(poq-app)  Expected: Error  Actual: Captcha
```

**R818 时是过的 —— 网络变了，把它暴露了。**

`lastStatus` 只有一个槽位：`Init` 拿 403 写进去 → `GetHome` 的 DNS 失败不产生状态 → 读到残留的 403 → 判成 Captcha。

> **一个从来不解析的主机，被报告成验证码墙。**

**没修**：写入方不在 `StoreFlowRunner.cs`，要找写入点才能决定清空还是按步记录。

### 验证

```
ChromiumStealthTests 5/0 · DocsConsistencyTests 7/0
metrics_report 1765 / 1 失败（poq-app，原因已诊）
四项度量 4 / 0 / 17 / 78 / 0 未变
```

**套件不是绿的，原因已知、有机制、下一轮修。这个状态要写着，不能抹平。**

### 教训

**上一轮我把这条失败记成「被 metrics 默认排除」就放过了。**
**「被默认排除」说的是它不在定期跑的范围里，不是它不重要 —— 而它恰恰覆盖着默认套件看不到的那一层。**
"""

BACKLOG_ADD = """

## 优先级 ③ — prune 已 gate；`lastStatus` 残留待修（R819）

### 已修

`ChromiumBridge.cs`：`GlobalPrune.GlobalBodyJs()` / `DocumentBodyJs()` 放进
`if (MobileSurface.IsAppleUserAgent(userAgent))` —— 与 R193 的规矩一致（桌面档不得继承 iPhone 独有的全局）。

```
改前 {"chrome":"undefined","runtime":"undefined", ...}
改后 {"chrome":"object",   "runtime":"object",    ...}
ChromiumStealthTests 5 通过 / 0 失败
```

**它此前烂着，因为该用例 `Speed=Slow` + 驱动真 Chrome，默认套件排除。**

### 待修（下一轮第一件事）

`ModuleRobustnessTests.Monitor_Survives_An_Unreachable_Host(poq-app)`：**Expected Error，Actual Captcha。**

**机制**：`LastStatus(ctx)` 读 `ctx.Session.Vars["lastStatus"]`，**单槽位、跨步残留**。
`Init` 的 403 → `GetHome` 的 DNS 失败（不产生状态）→ 读到 403 → 判 Captcha。

**阻塞点**：`lastStatus` 的**写入方不在 `StoreFlowRunner.cs`**（该文件只有读），需先定位写入点。

| 仍 Unknown | |
|---|---|
| `platform.poq.io` 是否真返 403 | Inference（高），未单独抓 |
| `lastStatus` 写入点 | **未找到，下一轮** |
| 其余模块是否踩同一残留 | 只有 poq-app 红，说明其余首步不产 403 |

**套件现状：1765 / 1 失败。不抹平。**

**纪律**：**「被默认排除」说的是不在定期跑的范围里，不是不重要** —— 它恰恰覆盖默认套件看不到的那一层。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R819", BLOCKER)
    ensure(RSTATUS, "R819", BLOCKER)
    ensure(RVERDICT, "第 819 轮", VERDICT)
    ensure(BACKLOG, "R819", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R819"), (RSTATUS, "R819"), (RVERDICT, "第 819 轮"), (BACKLOG, "R819")):
        body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R819: the device prunes were ungated and deleted window.chrome from desktop profiles\n\n"
         "The previous round's full run had two failures. One was my own doc wording. The other I noted as excluded from\n"
         "the default suite and moved past, which was the wrong call: exclusion from a periodic run says nothing about\n"
         "importance, and that test covers precisely the layer the default suite cannot see.\n\n"
         "ChromiumStealthTests.TheRestOfTheFingerprintLooksOrdinary reports six of eight properties correct -- five\n"
         "plugins, en-US,en, eight cores, eight gigabytes, Intel Inc., UA-CH brands with no Headless -- and chrome and\n"
         "runtime as undefined. A Kasada-protected storefront checks typeof window.chrome before it hands out a token.\n\n"
         "The cause is a prune that was never gated. GlobalPrune deletes every window name the device's list does not\n"
         "carry, and that list is the captured iPhone's 1062 names in WindowNameTable. Pruning a desktop profile against\n"
         "an iPhone list removes every desktop-only name, chrome among them. The rule already exists in the file: R193's\n"
         "comment says a desktop profile must not inherit iPhone-only globals, and NavPrune and MobileNavigator both sit\n"
         "behind that gate. The two prunes at lines 331 and 332 did not.\n\n"
         "Both now sit inside if (MobileSurface.IsAppleUserAgent(userAgent)), with the ordering the comments require\n"
         "unchanged. The probe returns chrome as object and runtime as object, the other six properties unchanged, and\n"
         "the five stealth tests pass.\n\n"
         "It survived because the test is marked Speed=Slow and drives a real browser, so metrics_report excludes it.\n"
         "The suite stayed green while the fingerprint advertised a missing object.\n\n"
         "That fix did not make the suite green. It still has one failure: the poq-app case of\n"
         "Monitor_Survives_An_Unreachable_Host expects Error and gets Captcha. It passed in R818's run, so the network\n"
         "changed rather than my edit breaking it -- and what changed exposed a latent defect. LastStatus reads one\n"
         "slot, ctx.Session.Vars[\"lastStatus\"], which every request overwrites. Init reaches platform.poq.io and gets\n"
         "403, storing it; GetHome then fails to resolve no-such-host.invalid, which produces no status at all; the\n"
         "classifier reads the 403 left behind and calls a host that never resolves a captcha wall. The classifier's own\n"
         "comment says a 403 from an anti-bot is very different from the host being down, and its intent is right -- the\n"
         "slot it reads is not that step's status.\n\n"
         "I did not fix that one. The writer of lastStatus is not in StoreFlowRunner, which only reads it, so the choice\n"
         "between clearing the slot per step and recording status per step needs the write site found first. That is\n"
         "the next round's first task, and the backlog says so along with the fact that the suite is 1765 of 1766 and\n"
         "not green.\n\n"
         "Unknown: whether platform.poq.io really returns 403 now, which I infer from the inherited status rather than\n"
         "having fetched it; where lastStatus is written; and whether other modules hit the same residue, which the fact\n"
         "that only poq-app fails suggests they do not, since their first steps produce no 403.\n\n"
         "Suite 1765 pass / 1 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
