"""Record R772/R773: I built the Poq flow, a test refuted it, and I reverted."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"
AG = r"D:\projects\cyber-reverse\AGENTS.md"

BLOCKER = """

---

## 199. **我建了 PoqFlow，一个既有测试把它否了，我回滚并删掉了它**

> R772 建、R773 回滚。`Registry.cs` 恢复原状，`PoqFlow.cs` 已删除。**净改动为零。**

### 一、我做了什么

按 R771 的计划，用镜像里那 7 条 Poq 字符串建了 `PoqFlow`：

```
account/guest-token · cart/items · checkout/start · products?ids=   ← 4 步有据
office/AtaVerifyCaptcha · office/recaptcha?trackingId=              ← 常量
```

**只写有证据的 4 步，另外 3 步故意不写** —— 因为覆盖率把「声明了 override」就算实现，
写三个诚实的失败桩会把 71% 抬到 100% 而那句话是假的（我在类的注释里就是这么写的）。

然后把注册表从 `HybrisFlow("offspring", …)` 换成 `new PoqFlow()`。

**覆盖率如预测下降**：

```
offspring   +  +  +  +  -  -  -   57%
```

**我以为这就是"降到了证据支撑的数字"。**

### 二、然后全量红了

```
失败 PlatformAssignmentTests.OffspringIsHybrisNotMagento
  Expected: typeof(HybrisFlow)
  Actual:   typeof(PoqFlow)
```

**那个测试的依据是实机证据**：

> 「the home page contains "hybris" and calls `/view/resources/getUserInfo` and
> `/view/component/basket/minibasketAjax`, both answering JSON; no Magento surface does」

**所以 `offspring.co.uk` 的网页确实是 Hybris。**

### 三、我错在哪

**我把「一个表面」当成了「唯一表面」。**

- `platform.poq.io/clients/offspring/*` → **App 面**（Poq 是移动端平台）
- `offspring.co.uk/view/...` → **网页面**，是 Hybris

**两个都是真的。** 镜像里有 App 面的字符串，**不等于网页面也是 Poq**。
**这是 `AGENTS.md` §2.7 的第七次：先假设形状，再把不符合假设的读成"应该替换"。**

### 四、为什么删掉而不是保留

`PoqFlow` 留着就是**一个新的死类** —— 而我上一轮（R771）刚把 `OffspringFlow` 的"存在但从未构造"
记成一个真问题。**自己刚批评过的形状，不该由自己再造一个。**

**证据不丢**：7 条字符串完整记在本节与 R771 里，`BINDING_BACKLOG` 留了待办。

### 五、净结果

```
Registry.cs   恢复为 HybrisFlow("offspring", …)，加一条注释写明两种表面（R773）
PoqFlow.cs    已删除
完整套件      1752 通过 / 0 失败 / 0 跳过
四项度量      4 / 0 / 17 / 78 / 0（未变）
offspring     仍是 71%（与原状一致）
```

### 六、仍然 Unknown

- **原版有没有"App 面"的模块**：**Unknown** —— 镜像有 Poq 字符串，但有没有一条走它的任务类型未知。
  **在确认之前就给它建 flow，就是这一轮犯的错。**
- `office` 是 App 面的另一个 client：**Unknown** —— 同样不能因字符串存在就建模块。
- Poq 的支付端点：**Unknown** —— 池子里没有。
"""

VERDICT = """

---

## 第 772/773 轮：我建了，被否了，删了

### 我怎么想的

用 7 条 Poq 字符串建 `PoqFlow`，只写 4 个有据的步骤，把注册表从 `HybrisFlow` 换过去。
覆盖率如预测**下降**到 57% —— 我以为这就是"降到证据支撑的数字"。

### 然后全量红了

```
PlatformAssignmentTests.OffspringIsHybrisNotMagento
  Expected HybrisFlow, Actual PoqFlow
```

**那个测试的依据是实机证据**：offspring 主页里有 `hybris`，且
`/view/resources/getUserInfo`、`/view/component/basket/minibasketAjax` 都回 JSON。

### 我错在哪

**我把「一个表面」当成了「唯一表面」。**

- `platform.poq.io/clients/offspring/*` → **App 面**
- `offspring.co.uk/view/...` → **网页面，Hybris**

**两个都是真的。镜像里有 App 面的字符串，不等于网页面也是 Poq。**
**§2.7 第七次：先假设形状，再把不符合假设的读成"应该替换"。**

### 为什么删而不是留

留着就是**新的死类** —— 我上一轮刚把 `OffspringFlow` 的"存在但未构造"记成问题。
**自己刚批评过的形状，不该自己再造一个。** 证据记在文档里，不留在代码里。

### 净结果

```
Registry.cs 恢复 + 注释写明两种表面 · PoqFlow.cs 删除
套件 1752 / 0 · 四项度量未变 · offspring 仍 71%
```

### 仍然 Unknown

**原版有没有走 App 面的模块** —— 在确认之前给它建 flow 就是这一轮犯的错。
"""

BACKLOG_ADD = """

## 核心 — offspring 的两种表面（R773）

**已确认**：`offspring.co.uk` 网页 = **Hybris**（实机证据：主页含 `hybris`，
`/view/resources/getUserInfo`、`/view/component/basket/minibasketAjax` 回 JSON）。
镜像里的 `platform.poq.io/clients/offspring/*`（guest-token / cart/items / checkout/start / products?ids=）
是 **App 面**，Poq 平台。

| 项 | 状态 |
|---|---|
| 原版有没有走 App 面的任务类型 | **Unknown —— 必须先确认，再建 flow** |
| `office` client（AtaVerifyCaptcha / recaptcha） | Unknown，同上 |
| Poq 的支付端点 | Unknown，池子里没有 |

**本轮教训**：我因为镜像里有 Poq 字符串就把它当成 offspring 的结账面并替换了注册表，
被 `PlatformAssignmentTests` 的实机证据否掉。**"镜像里有某个面的字符串" ≠ "这个面就是它"。**

**R772 建、R773 回滚，净改动为零。** 证据记在 BLOCKERS §199 与 §198。
"""


def main():
    for p, marker, text in ((P1, "R773", BLOCKER), (P3, "R773", BLOCKER), (P2, "第 772/773 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R773" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += 两种表面")

    body = io.open(AG, encoding="utf-8").read()
    old = "| R768 | `NO-URLS` 表示\"关键词不匹配\" | 读起来是\"镜像里没有 URL\" | 结论被标签误导一轮 |"
    new = old + "\n| R772 | 镜像有某平台的字符串 = 那就是这个站的结账面 | **两种表面并存**（网页 Hybris / App Poq） | 改动被既有实机证据否掉，回滚 |"
    if "R772 | 镜像有某平台" in body:
        print("  AGENTS.md already lists R772")
    elif old in body:
        io.open(AG, "w", encoding="utf-8").write(body.replace(old, new, 1))
        print("  AGENTS.md += R772 row")
    else:
        print("  AGENTS.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R772/R773: I built the Poq flow, a live-evidence test refuted it, and I reverted\n\n"
         "R772 built PoqFlow from the seven platform.poq.io strings in the image -- guest token, cart items,\n"
         "checkout start, products by id -- deliberately overriding only the four steps the evidence supports, because\n"
         "the coverage test counts an override as an implementation and three honest failures would have reported 100%\n"
         "for a module that cannot complete a purchase. Registry.cs was switched from HybrisFlow to the new class and\n"
         "offspring duly fell from 71% to 57%, which I read as the faithful number.\n\n"
         "The full suite refuted it. PlatformAssignmentTests.OffspringIsHybrisNotMagento asserts HybrisFlow, and its\n"
         "rationale is live evidence: the home page contains 'hybris' and answers JSON at /view/resources/getUserInfo\n"
         "and /view/component/basket/minibasketAjax.\n\n"
         "So both surfaces are real. platform.poq.io/clients/offspring is the app surface -- Poq is a mobile\n"
         "platform -- while offspring.co.uk/view is the web surface, and that one is Hybris. What I got wrong was\n"
         "treating one surface as the only surface: the presence of app-surface strings in the image says nothing\n"
         "about the web surface. That is the seventh instance of the section 2.7 mistake, and the first where the\n"
         "assumption led me to replace something correct.\n\n"
         "PoqFlow was deleted rather than left unregistered. Keeping it would have created exactly the defect I\n"
         "recorded one round earlier about OffspringFlow -- a concrete flow class that nothing constructs. The\n"
         "evidence survives in BLOCKERS 198 and 199 and in the backlog; dead code would not have preserved it any\n"
         "better.\n\n"
         "Net change from the two rounds is zero. Registry.cs is restored with a comment naming both surfaces, the\n"
         "suite is 1752 pass / 0 fail, the four metrics are unchanged, and offspring is back at 71%.\n\n"
         "What remains open is the question I should have asked first: does the original have a task type that drives\n"
         "the app surface at all? Building a flow for it before confirming that is what this round got wrong."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
