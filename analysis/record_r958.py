"""Record R958: three RPC steps recovered from one descriptor of consecutive ordinals."""

import io
import os
import re
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### 一条描述符给出十个 RPC 步骤，而复刻件**缺三个**（R958）

**R957 说「下一步反编译 `RpcGetPaymentMethods` 看返回形状」。查了 —— 而反编译这条路**先断了**，
而断掉的地方给出了更好的东西。**

### 反编译为什么走不通

```
ida.py funcs RpcGetPaymentMethods  -> 不过滤，从头返回所有 sub_XXXX
ida.py xrefs 0x14337ca41            -> xref_count: 0
```

**NativeAOT **剥掉了符号名**（只有 `sub_140xxxxxx`），而那串描述符是**反射表里的类型名**，
所以没有任何代码引用它 —— `xrefs` 为空。**

> **所以「按名字找函数再反编译」在这个二进制上不成立。而这一条之前从没被明确记下来。****

### 而那条描述符本身就是证据

```
d__169 RpcLogin              d__174 RpcCalculateShipping
d__170 RpcFindProduct        d__175 RpcValidateBuyRule
d__171 RpcCheckStock         d__176 RpcCreateOrder
d__172 RpcFetchAddress       d__177 RpcGetPaymentMethods
d__173 RpcCreateAddress      d__178 RpcSubmitCard
```

**十个连号 —— 一个 RPC 面，而且**有序**。**

### 而逐条对完，缺三个

| 镜像 | 复刻件 |
|---|---|
| RpcLogin · RpcFindProduct | `Login` · `FindProduct` ✅ |
| RpcFetchAddress · RpcCreateAddress | `BuildDestination` · `SubmitAddress` ✅（改名） |
| RpcCalculateShipping | `GetShippingRates` ✅（改名） |
| RpcCreateOrder · RpcSubmitCard | `SubmitOrder`/`PlaceOrder` · `SubmitPayment` ✅（改名） |
| **RpcCheckStock** | **无** |
| **RpcValidateBuyRule** | **无** |
| **RpcGetPaymentMethods** | **无** |

> **而三个都不是同义词：
> `CheckStock` 在订单存在**之前**问库存（页面的刮取是**页面说了什么**，这个是问店的库存服务，两者会不一致）；
> `ValidateBuyRule` 是**店自己的购买政策检查**（限量、地区、额度）；
> `GetPaymentMethods` 是**回答这家店提供哪些支付方式** —— 而 R957 正是因为不知道这个，才编了一个常量数组。****

### 所以三个都写成了有实体的步骤

**不是 `=> NotSupported` 的空壳 —— 每个都有真实分支：**

- **`CheckStockAsync`**：取 sku → 打库存 URL → 404/410 判缺货 → 非 2xx 判可重试 →
  **body 里找 `"available":false` / `"inStock":false`**（"200 不等于可买"）
- **`ValidateBuyRuleAsync`**：POST 政策 URL → 非 2xx 时**判不可重试**
  （重试一个政策决定只是把同一个问题再问一遍）
- **`GetPaymentMethodsAsync`**：取 URL → 解析出 offered → **交给 R957 的 `ChooseGateway`** →
  把选中项写回 `paymentGatewayName`。**这才是让 R957 那个选择函数有意义的调用点。**
- **`ParsePaymentMethodNames`**：在 `id`/`code`/`type`/`name`/`method` 五种字段名里找引号值，
  **不假设 schema**，找不到就返回空。

### 而构建崩了两次，两次都不是源码的问题

```
第一次: ilc 退出 -1073740791 (0xC0000409)
第二次: LNK1136: 无效或损坏的文件  (Cybersole.Ui.obj)
```

**第二次是第一次留下的坏 `.obj`。而连 `native` 目录一起删都不够 ——
要把 `src\\Cybersole.Ui\\obj` 与 `bin` **整个删掉**，才重发成功。**

> **所以「LNK1136 读起来像源码坏了」是假的：它是**崩溃的残留**，
> 而残留比崩溃活得更久、更像一个真错误。****

### 而一个守卫红了，而它自己的注释说了该怎么做

**`FlowSequenceTests.OnePopMartImageStepIsDispatchable` 断言 `map.Count == 176`。
我加了三个虚步骤 → 179。**

> **而那个测例的注释写着：「the fix is to write the new number in and say which step arrived —
> never to delete the assertion」。所以改了数字并写明三个步骤到了。**
> **而 `implementable` 仍是 8 —— 三个新步骤名都不在 PopMart 的 24 个名字里，与 `FindProductInstore` 同样的分裂。**

### 数字

| 度量 | R957 | **R958** |
|---|---|---|
| 套件 | 2115 | **2129** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,824 | **173,866（+42）** |
| **函数比** | 62.73% | **62.75%** |
| 产物大小 | 54,692 KB | **54,706 KB** |
| 分派表 | 176 | **179** |

### 教训

> **这一轮想要的证据（`RpcGetPaymentMethods` 的返回形状）**没拿到**，
> 而拿到的是一条更强的：那个二进制**不给名字**，所以「按名字反编译」整个方法在这个目标上不成立。**
> **而这一条比一次成功的反编译值钱 —— 它关掉了一条我会反复尝试的路，
> 同时把注意力推到唯一能用的东西上：**连号描述符里的顺序**。**
"""

if "一条描述符给出十个 RPC 步骤" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 958 轮：一条描述符给出十个 RPC 步骤，复刻件缺三个

### 反编译这条路先断了

```
ida.py funcs RpcGetPaymentMethods  -> 不过滤，从头返回所有 sub_XXXX
ida.py xrefs 0x14337ca41            -> xref_count: 0
```

**NativeAOT 剥掉了符号名（只有 `sub_140xxxxxx`），而那条描述符是反射表里的类型名，
所以没有代码引用它 —— `xrefs` 为空。**

> **所以「按名字找函数再反编译」在这个二进制上不成立。**

### 而描述符本身是更强的证据

```
169 RpcLogin · 170 RpcFindProduct · 171 RpcCheckStock · 172 RpcFetchAddress · 173 RpcCreateAddress
174 RpcCalculateShipping · 175 RpcValidateBuyRule · 176 RpcCreateOrder
177 RpcGetPaymentMethods · 178 RpcSubmitCard
```

**十个连号，有序。逐条对完复刻件缺三个：`CheckStock` · `ValidateBuyRule` · `GetPaymentMethods`。**

> **三个都不是同义词：`CheckStock` 在订单之前问店的库存服务（与页面刮取会不一致）；
> `ValidateBuyRule` 是店自己的政策检查；`GetPaymentMethods` 是**回答这家店提供哪些支付方式** ——
> 而 R957 正因不知此才编了常量数组。**

### 三个都写成了有实体的步骤

- **`CheckStockAsync`**：404/410 缺货 · 非 2xx 可重试 · body 找 `"available":false`/`"inStock":false`（200 ≠ 可买）
- **`ValidateBuyRuleAsync`**：非 2xx 判**不可重试**（重试政策决定只是再问一遍）
- **`GetPaymentMethodsAsync`**：解析 offered → 交 `ChooseGateway` → 写回 `paymentGatewayName`
- **`ParsePaymentMethodNames`**：五种字段名找引号值，不假设 schema

### 构建崩两次，都不是源码问题

**`ilc` 0xC0000409 → `LNK1136`（坏 .obj）。删 `native` 不够，要把 `obj` 与 `bin` 整个删掉。**

> **LNK1136 读起来像源码坏了，而它是**崩溃的残留** —— 残留比崩溃活得更久、更像真错误。**

### 一个守卫红了，而它的注释说了该怎么做

**`map.Count == 176` → 179。注释写着「write the new number in and say which step arrived —
never to delete the assertion」。`implementable` 仍是 8（三个新名不在 PopMart 24 个里）。**

### 数字

| 度量 | R957 | **R958** |
|---|---|---|
| 套件 | 2115 | **2129** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,824 | **173,866（+42）** |
| **函数比** | 62.73% | **62.75%** |
| 产物大小 | 54,692 KB | **54,706 KB** |
| 分派表 | 176 | **179** |

### 教训

> **想要的证据没拿到，而拿到的是「这个二进制不给名字，按名字反编译整个方法不成立」——
> 那比一次成功反编译值钱：它关掉了一条我会反复尝试的路，
> 同时把注意力推到唯一能用的东西上：连号描述符里的顺序。**
"""

BACKLOG_ADD = """

## 判据 (a)/① — 三个 RPC 步骤补上；按名字反编译不成立（R958，**+14 用例**）

### 反编译路断

**`funcs` 不过滤 · `xrefs` 空（符号被剥，描述符在反射表里）→ 按名字找函数不成立。**

### 描述符给的十步

**169 Login · 170 FindProduct · 171 CheckStock · 172 FetchAddress · 173 CreateAddress ·
174 CalculateShipping · 175 ValidateBuyRule · 176 CreateOrder · 177 GetPaymentMethods · 178 SubmitCard**

**缺三个：`CheckStock` · `ValidateBuyRule` · `GetPaymentMethods`**

### 补上的三个（有实体，非空壳）

**`CheckStockAsync`（404/410/非2xx/body 双标志）· `ValidateBuyRuleAsync`（非2xx 不可重试）·
`GetPaymentMethodsAsync`（解析→ChooseGateway→写回）· `ParsePaymentMethodNames`（五字段不假设 schema）**

### 构建残留

**`ilc` 0xC0000409 → `LNK1136`（坏 .obj）；删 `native` 不够，要删整个 `obj`+`bin`。**

### 数字

**套件 2115 → 2129 · 陈旧度 0/0 · 函数数 173,824 → **173,866（+42）** · 比 62.75% ·
产物 54,692 → 54,706 KB · 分派表 176 → 179**

| 仍 Unknown | |
|---|---|
| `RpcGetPaymentMethods` 的返回形状 | 按名字反编译不成立 |
| 10 个 RPC 的参数与返回 | 同上 |
| `ValidateBuyRule` 的 body 形状 | 只知道要 POST |

**纪律**：残留比崩溃活得更久、更像真错误。
"""

BLOCKER = """

---

## 382. 三个 RPC 步骤补上；按名字反编译不成立

> R958。**改产品代码 +14 用例。** 套件 **2129 通过 / 0 失败 / 0 跳过**。

### 一、反编译路断

```
ida.py funcs RpcGetPaymentMethods -> 不过滤，从头返回 sub_XXXX
ida.py xrefs 0x14337ca41           -> xref_count: 0
```

**NativeAOT 剥符号；描述符在反射表里，无代码引用 → 按名字找函数不成立。**

### 二、描述符给的十步（有序）

```
169 RpcLogin · 170 RpcFindProduct · 171 RpcCheckStock · 172 RpcFetchAddress · 173 RpcCreateAddress
174 RpcCalculateShipping · 175 RpcValidateBuyRule · 176 RpcCreateOrder · 177 RpcGetPaymentMethods · 178 RpcSubmitCard
```

**缺三个：`CheckStock` · `ValidateBuyRule` · `GetPaymentMethods`**

### 三、三个都有实体

- **`CheckStockAsync`**：404/410 = 缺货；非 2xx 可重试；body 找 `"available":false`/`"inStock":false`
- **`ValidateBuyRuleAsync`**：非 2xx → **不可重试**
- **`GetPaymentMethodsAsync`**：解析 offered → `ChooseGateway` → 写回 `paymentGatewayName`
- **`ParsePaymentMethodNames`**：`id`/`code`/`type`/`name`/`method` 五字段，不假设 schema

### 四、构建崩塌两次

**`ilc` 退出 `-1073740791`（0xC0000409）→ `LNK1136: 无效或损坏的文件`。
删 `native` 不够，要删整个 `src\\Cybersole.Ui\\obj` 与 `bin`，才重发成功 54,706 KB。**

**LNK1136 是崩溃的残留，不是源码问题。**

### 五、一个守卫红了

**`FlowSequenceTests.OnePopMartImageStepIsDispatchable`：`map.Count` 176 → **179**。
按它自己的注释改数字并写明三个步骤到了。`implementable` 仍 8。**

### 六、数字

| 度量 | R957 | R958 |
|---|---|---|
| 套件 | 2115 | **2129** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| **函数数** | 173,824 | **173,866（+42）** |
| **函数比** | 62.73% | **62.75%** |
| 产物大小 | 54,692 KB | **54,706 KB** |
| **分派表** | 176 | **179** |

### 七、验证

```
analysis/ida.py xrefs 0x14337ca41  -> xref_count: 0
analysis/ida.py str RpcGetPaymentMethods -> 十个连号
test --filter MissingRpcStepsTests       -> 14 通过
test --filter FlowSequenceTests          -> 7 通过
metrics_report.py                        -> 2129 通过 / 0 失败
```

### 八、仍然 Unknown

- **`RpcGetPaymentMethods` 的返回形状**：**Unknown** —— 按名字反编译不成立。
- **10 个 RPC 的参数与返回**：**Unknown** —— 同上。
- **`ValidateBuyRule` 的 body 形状**：**Unknown** —— 只知道要 POST。

### 九、教训

**想要的证据没拿到，拿到的是一条更硬的：这个二进制不给名字。**

**那比一次成功反编译值钱 —— 它关掉了一条我会反复尝试的路。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R958", BLOCKER)
    ensure(RSTATUS, "R958", BLOCKER)
    ensure(RVERDICT, "第 958 轮", VERDICT)
    ensure(BACKLOG, "R958", BACKLOG_ADD)

    note = (
        "\n## R958 补充 — 三个 RPC 步骤补上；按名字反编译不成立（+14 用例，套件 2129）\n\n"
        "反编译路断：`funcs` 不过滤 · `xrefs` 空（NativeAOT 剥符号，描述符在反射表里）→ 按名字找函数不成立。\n\n"
        "描述符给的十步（有序）：169 Login · 170 FindProduct · 171 CheckStock · 172 FetchAddress · "
        "173 CreateAddress · 174 CalculateShipping · 175 ValidateBuyRule · 176 CreateOrder · 177 GetPaymentMethods · "
        "178 SubmitCard。复刻件缺三个：CheckStock / ValidateBuyRule / GetPaymentMethods。\n\n"
        "三个都有实体：CheckStock（404/410/非2xx/body 双标志）· ValidateBuyRule（非2xx 不可重试）· "
        "GetPaymentMethods（解析→ChooseGateway→写回）+ ParsePaymentMethodNames（五字段不假设 schema）。\n\n"
        "构建崩塌：ilc 0xC0000409 → LNK1136（坏 .obj）；删 native 不够，要删整个 obj+bin。\n"
        "守卫 map.Count 176 → 179（按它自己注释的规矩改数字）。\n\n"
        "数字：套件 2115 → 2129 · 陈旧度 0/0 · 函数数 173,824 → **173,866（+42）** · 比 62.75% · "
        "产物 54,692 → 54,706 KB · 分派表 176 → 179。\n\n"
        "纪律：残留比崩溃活得更久、更像真错误。\n\n"
        "下一轮：10 个 RPC 的参数/返回形状（按名字不可达，需别的路径）；或转优先级 ②（风控对抗）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R958" not in h:
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h + note)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R958"), (RSTATUS, "R958"), (RVERDICT, "第 958 轮"), (BACKLOG, "R958")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R958: three RPC steps recovered from one descriptor, and there is no way to decompile by name\n\n"
         "R957 left a plan to decompile RpcGetPaymentMethods for its return shape. That route closed: funcs ignores its\n"
         " filter and returns every sub_XXXX from the start of the image, and xrefs on the descriptor's address returns\n"
         " zero. NativeAOT strips symbol names, and the descriptor is a type name in a reflection table, so no code\n"
         " references it. Decompiling by name does not work on this binary, which is worth recording because it is a route\n"
         " I would otherwise keep trying.\n\n"
         "The descriptor is the better evidence anyway. It lists ten RPC methods as consecutive state machines, in order:\n"
         " 169 RpcLogin, 170 RpcFindProduct, 171 RpcCheckStock, 172 RpcFetchAddress, 173 RpcCreateAddress,\n"
         " 174 RpcCalculateShipping, 175 RpcValidateBuyRule, 176 RpcCreateOrder, 177 RpcGetPaymentMethods,\n"
         " 178 RpcSubmitCard. Comparing against the replica, eight have a step under another name and three have none.\n\n"
         "None of the three is a synonym. CheckStock asks the shop's own stock service before an order exists, which can\n"
         " disagree with a scraped page. ValidateBuyRule is the shop's purchase policy -- quantity limits, region rules,\n"
         " an account past its allowance. GetPaymentMethods answers which methods a shop offers, which is exactly what\n"
         " R957 could not find and invented a constant array for.\n\n"
         "All three are written with bodies rather than returning NotSupported. CheckStock treats 404 and 410 as out of\n"
         " stock, other non-2xx as retryable, and looks for available:false or inStock:false in the body because a 200 does\n"
         " not mean buyable. ValidateBuyRule treats any non-2xx as final, since retrying a policy decision asks the same\n"
         " question again. GetPaymentMethods parses the offered names, hands them to R957's ChooseGateway, and writes the\n"
         " choice back to paymentGatewayName -- which is the call that makes that selection function mean anything.\n\n"
         "The build crashed twice and neither was the source. ilc exited 0xC0000409, and the retry reported LNK1136\n"
         " invalid or corrupt file, which reads like a source problem and is the wreckage of the first crash. Deleting the\n"
         " native intermediate directory was not enough; the whole obj and bin had to go before the publish produced an\n"
         " artifact.\n\n"
         "One guard went red and its own comment said what to do: the dispatch map's expected count went from 176 to 179\n"
         " because three virtual steps arrived, and the comment says to write the new number in and name the arrivals\n"
         " rather than delete the assertion. The coverage count stays at eight, since none of the three is among Pop Mart's\n"
         " twenty-four names.\n\n"
         "Figures: suite 2115 to 2129, freshness zero, count 173,824 to 173,866, ratio 62.73 to 62.75 percent, artifact\n"
         " 54,692 to 54,706 kilobytes, dispatch map 176 to 179.\n\n"
         "Unknown: the shape RpcGetPaymentMethods returns, since decompiling by name is unavailable; the parameters and\n"
         " returns of all ten; and what body ValidateBuyRule expects, of which only that it is a POST survives.\n\n"
         "The lesson is that failing to get the evidence I wanted produced a harder fact instead -- that this binary has no\n"
         " names to look up -- and that fact is worth more than a decompilation because it closes a path and pushes\n"
         " attention onto the one that works.\n\n"
         "Product code and two tests changed; suite green at 2129."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()