"""Record R779: the Poq app flow is built and registered, and the bookkeeping it forced."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 205. App 面的 flow 建起来了 —— 证据攒够了才动手

> R779。新增 `replica/src/Cybersole.Stores/Flows/PoqAppFlow.cs`；`Registry.cs` 加一行注册；
> 五处计数同步。**这是本会话第一次「证据齐了才写」。**

### 一、写了什么

`PoqAppFlow : StoreFlow`，注册为 `poq-app`，域名 `platform.poq.io`：

```
身份（8 个常量，R777/R778 的 Observation）
  user-agent Poq-Native-iOS-App · accept application/json
  accept-encoding gzip, deflate, br · accept-language nl-NL,nl;q=0.9（标 Inference-low）
  version-code 26.0 · platform iphone
  poq-app-id 275 · poq-app-identifier a1dad595-7431-45bc-9fb9-684dac169b5b

四个动作（Observation）
  account/guest-token · products?ids= · cart/items · checkout/start
```

**身份通过 `c.Session.Headers` 落到会话上** —— 那是请求层真正读取的地方（`StoreFlow` 第 37/77 行就在这么用），
**所以身份被使用，不是死常量。**

**三个动态值**（`poq-country-identifier` / `poq-currency-identifier` / `poq-user-id`）从
`c.Session.Vars["header:<名字>"]` 取，**没有照抄常量** —— 照抄就是把运行时数据冒充成固定值。

**三个步骤故意不写**（shipping / payment / order）：镜像在这个面上没有它们的端点，
**而写一个恒失败的 override 会被覆盖率算作"已实现"**。

### 二、覆盖率

```
poq-app   +  +  +  +  -  -  -   57%
resolved 63/63 flows; fully covered 49; exempt 2
```

**57% 是忠实数字**：4 步有据，3 步原版没有。

### 三、加一个模块要改五处 —— 这是设计，不是麻烦

注册之后红了一串，全是账簿：

```
ParityDocTests.TheModuleCountInParityMatchesTheCatalogue      PARITY.md 62 -> 63
ParityDocTests.TheFlowTypeCountInParityMatchesTheCatalogue    PARITY.md 32 -> 33
StoreModuleTests.Catalog_Registers_All_Modules                CoreTests.cs 62 -> 63
ArrowAndBeastTests.TheCatalogueIsSixtyTwoModules              改名 + 62 -> 63
SummaryBlockTests.ModuleCountInTheGuideMatchesTheRegistry     VERDICT.md 顶部 reading guide 62/32 -> 63/33
```

**其中 `DocsConsistencyTests` 那处我在注册前就主动改了**（11 处 `62 个模块` → 63），
**另外五处是守卫替我找出来的。**

**这正是它的价值**：`ArrowAndBeastTests.TheCatalogueIsSixtyTwoModules` **把数字写进了测试名**，
所以数字变的时候名字会逼你面对它。**我不觉得这是繁文缛节 —— 它比"记得去改"可靠。**

### 四、验证

```
构建                已成功
ModuleCoverageTests poq-app 57%，resolved 63/63
完整套件            1752 通过 / 0 失败 / 0 跳过（与改前同数）
四项度量            4 / 0 / 17 / 78 / 0（未变）
```

**注意套件总数没变**（1752）：**加了一个模块、改了一个测试名、同步了五处数字，用例条数不变。**

### 五、这一轮与 R772 的区别

R772 我也建过一个 Poq flow，**那次是拿一个面去替换另一个面，被实机证据驳回，净改动为零。**
这一轮：**先确认了两个面并存（R773/R774）、确认了原版真的走 App 面（R775）、
把头名（R777）和取值（R778）攒齐**，**然后才写。**

**同一个对象，两次尝试，中间隔了六轮取证。**

### 六、仍然 Unknown

- **触发 App 面的任务类型**：**Unknown** —— 我现在把它注册成一个独立 module，
  **这是我选的形状，不是原版的形状**。类注释里写明了这一点。
- `poq-slot-conditions` 的取值：**Unknown**。
- `nl-NL` 是否被区域覆盖：**Unknown**。
- 三个动态值的语义：**Unknown**（会话数据）。
- App 面缺的 shipping/payment/order 是否原版也没有：**Inference（高）** —— 池子里没有端点，**未反证**。
"""

VERDICT = """

---

## 第 779 轮：证据攒够了才动手

### 建了什么

`PoqAppFlow`，注册为 `poq-app`，域名 `platform.poq.io`。

**8 个身份常量**（R777/R778 的 Observation）+ **4 个动作**（guest-token / products / cart-items / checkout-start）。

**身份通过 `c.Session.Headers` 落到会话** —— 请求层读的就是那里，**所以是真用，不是死常量。**
**三个动态值从会话取，不照抄常量。**
**三个步骤故意不写** —— 镜像在这个面上没有端点，而恒失败的 override 会被算作"已实现"。

### 覆盖率

```
poq-app   + + + + - - -   57%
resolved 63/63 · fully covered 49 · exempt 2
```

**57% 是忠实的。**

### 加一个模块要改五处 —— 这是设计

```
PARITY.md 62/32 → 63/33（两处）· CoreTests 62 → 63
ArrowAndBeastTests.TheCatalogueIsSixtyTwoModules → 改名 + 63
VERDICT.md 顶部 reading guide 62/32 → 63/33
```

**其中一个测试把数字写进了名字** —— 数字变时名字会逼你面对它。
**这比"记得去改"可靠。**

### 与 R772 的区别

R772 我也建过 Poq flow，**那次拿一个面替换另一个面，被实机证据驳回，净改动为零。**
这一轮：**先确认两面并存（R773/R774）→ 确认原版真走 App 面（R775）→ 头名（R777）→ 取值（R778）→ 才写。**

**同一个对象，两次尝试，中间隔了六轮取证。**

### 验证

```
套件 1752 / 0 · 四项度量未变 · poq-app 57%
```

### 仍然 Unknown

**触发 App 面的任务类型** —— 注册成独立 module **是我选的形状，不是原版的形状**，类注释里写明了。
"""

BACKLOG_ADD = """

## App 面 — 已建（R779）

`PoqAppFlow` 已注册为 `poq-app`（域名 `platform.poq.io`），覆盖率 **57%（4/7）**。

```
身份 8 常量 → c.Session.Headers（请求层真读的地方）
动作 4 个：guest-token / products?ids= / cart/items / checkout/start
动态 3 个：poq-country-identifier / currency / user-id ← 从 Session.Vars 取，不照抄
未写 3 个：shipping / payment / order ← 镜像在该面无端点
```

| 项 | 状态 |
|---|---|
| **触发 App 面的任务类型** | **Unknown —— 独立 module 是我选的形状，不是原版的** |
| `poq-slot-conditions` 取值 | Unknown |
| `nl-NL` 是否被区域覆盖 | Unknown |
| 缺的三步原版是否也没有 | Inference（高），未反证 |

**加模块的连带清单（R779 实测五处）**：`PARITY.md` 两处、`CoreTests.cs`、
`ArrowAndBeastTests`（名字里带数字）、`VERDICT.md` 顶部 reading guide。
**注册新模块前先想到这五处。**
"""


def main():
    for p, marker, text in ((P1, "R779", BLOCKER), (P3, "R779", BLOCKER), (P2, "第 779 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R779" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += App 面已建")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R779: the Poq app flow is built -- after six rounds of evidence, not before it\n\n"
         "PoqAppFlow is registered as poq-app against platform.poq.io. It carries the eight identity constants R777\n"
         "and R778 recovered, applies them through c.Session.Headers, which is where the request layer actually reads\n"
         "headers, and implements the four actions the image names: guest token, products by id, cart items and\n"
         "checkout start.\n\n"
         "Three things are deliberately absent or different. The three dynamic headers -- country, currency and user\n"
         "id -- are read from the session rather than filled with constants, because copying the image's literals into\n"
         "them would present runtime data as fixed values. And shipping, payment and order are not overridden at all:\n"
         "the image names no such endpoint on this surface, and an override that always fails would be counted as\n"
         "implemented by ModuleCoverageTests while being unable to complete a purchase. The module scores 57%, four of\n"
         "seven, which is what the evidence supports.\n\n"
         "Registering a module turned out to touch five places. PARITY.md states both the module count and the flow\n"
         "type count; CoreTests asserts the module count; ArrowAndBeastTests has the number in its own name; and the\n"
         "reading guide at the top of VERDICT.md repeats both figures. I had already updated the VERDICT prose before\n"
         "registering, and the guards found the other five. That is the design working: a test whose name contains a\n"
         "number forces you to look at it when the number changes, which beats remembering to check.\n\n"
         "This is the same object I built in R772 and reverted. That attempt replaced offspring's web surface with the\n"
         "app one and was refuted by live evidence. Between then and now: R773 established the two surfaces coexist,\n"
         "R774 found the app surface is a request identity rather than a platform family, R775 traced the call chain\n"
         "that proves the original uses it, R777 recovered the header names, R778 the values. Six rounds of evidence\n"
         "stood between the wrong version and this one.\n\n"
         "The shape is still my choice rather than the original's: whether it drives the app surface as a separate\n"
         "store module or as a mode inside offspring's tasks is unknown, and the class comment says so.\n\n"
         "Suite 1752 pass / 0 fail, unchanged in count despite the new module; four metrics unchanged."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
