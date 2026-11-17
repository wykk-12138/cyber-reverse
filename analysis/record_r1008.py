"""Record R1008: R1004's readings confirmed, and a second invented key found."""

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
### R1004 的读数被新工具确认；而 `paymentMethodsUrl` 是**第二个自造键名**（R1008）

**R1007 说下一轮用新工具重验 R1004。验了，结论成立；而顺手在优先级 ① 上找到同一类错误的第二例。**

### ① 重验 R1004（双编码 + sha256 背书）

```
artifact  .publish-aot/Cybersole.Ui.exe
sha256    36c16b3b3fd536d23cf4920603afc7761729a505ed4e0975de38444912891409

  adyen                          utf-16-le 19   utf-8 0   yes
  Adyen                          utf-16-le  2   utf-8 1   yes
  commercehub                    utf-16-le 17   utf-8 0   yes
  CommerceHub                    utf-16-le  0   utf-8 1   yes
  CybersoleECOM                           0         0   no
  encryptedCardNumber                     0         0   no
  tokenUUID                               0         0   no
  /api/v1/sale                            0         0   no
  checkoutshopper-live.adyen.com          0         0   no
```

**→ R1004 的结论**成立**：`Id` / `Name` 属性在产物里，`AuthorizeAsync` 的方法体串一个都不在。**
**→ 而它给出一条更细的事实：**同一个类**里，小写 id 是 **UTF-16LE**（19/17），
大写 Name 是 **UTF-8**（1）。所以「哪种编码」连在**一个类型内部**都不统一。**

### ② 而优先级 ① 上找到同一类错误的第二例

**`GetPaymentMethodsAsync` 读 `Vars["paymentMethodsUrl"]`。查镜像：**

```
paymentMethodsUrl   0 命中
```

**→ 那个键名**不在镜像里**。它是 self-made。**
**→ 而 R956 修过的 `paymentGateway`（→ `_paymentGatewayName`）是**第一个**，这是第二个。**

> **两者同形：一个能编译、读起来正确的名字，所以没人会怀疑它。
> 差别在于这一个**没有替代名可得**。**

### ③ 而镜像里那个步骤是真的，连 ordinal 都对

```
0x14337f4a9  (RpcGetPaymentMethodsg
0x1433800e6  <<RpcGetPaymentMethods>b__177_0<<RpcGetPaymentMethods>b__177_1g   ← 两个 lambda
0x14337f4c9  RpcSubmitCardg
0x14338012e  .<RpcSubmitCard>b__178_2g
```

**→ `RpcGetPaymentMethods` 是真实的状态机，带**两个** lambda；`RpcSubmitCard` 带一个。
→ 而 `177` 与 `StoreFlow.cs` 注释里的 `177 RpcGetPaymentMethods` **对得上** —— 那条注释是对的。**

**→ 缺的不是步骤、不是 ordinal，是**路由**。而 R958 已确立「按名字反编译在 NativeAOT 下不成立」，
所以路由目前**不可得**，不是「没找到」。**

### ④ 所以这一轮改的是「让它可见」，不是「修好它」

**`GetPaymentMethodsAsync` 的注释现在写明三件事：**
1. `paymentMethodsUrl` 在镜像里两编码皆 0 —— 这个键名是自造的
2. 镜像有那个步骤（`RpcGetPaymentMethods` + 两 lambda），ordinal 177 对得上
3. **路由不可得**，且 R963 意味着零覆写 → 这个方法整个被裁

**并加守卫 `ThePaymentMethodsURLKeyIsRecordedAsInvented`：钉住「键名在、注释在、
且『No flow overrides this method today』在」。**

> **→ 守卫的判据不是「这个名字对不对」（它不对），而是「读源码的人会不会以为它被搜过」。
> 那条注释让后者不成立。**

### ⑤ 数字

| 度量 | R1007 | **R1008** |
|---|---|---|
| 套件 | 2218 | **2219（+1 自造键名守卫）** |
| 产物陈旧度 | 0 / 0 | **1 / 2,671（只改了注释）** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **R1004 读数** | 需重验 | **确认（双编码 + sha256）** |
| **已知自造键名** | 1（`paymentGateway`，R956 已修） | **2（+`paymentMethodsUrl`，无替代名）** |

### 教训

> **「自造键名」不是一次性的失误，它有一个**稳定的成因**：
> 一个编译得过、读起来对的名字，没有任何机制会质疑它。
> **→ 而唯一能发现它的动作是**去镜像里查那个名字** —— 那一步 R956 做过一次，
> 而 `paymentMethodsUrl` 从写下那天起活到 R1008 才被查。
> **→ 所以这一轮的守卫钉的不是名字，是「这个名字没被搜过」这件事的说法。****
"""

if "R1004 的读数被新工具确认" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1008 轮：R1004 的读数被确认；而 `paymentMethodsUrl` 是第二个自造键名

### ① 重验 R1004（双编码 + sha256）

```
adyen            utf-16-le 19   utf-8 0   yes
commercehub      utf-16-le 17   utf-8 0   yes
CommerceHub      utf-16-le 0    utf-8 1   yes
CybersoleECOM · encryptedCardNumber · tokenUUID · /api/v1/sale · checkoutshopper  全 0
```

**→ R1004 成立：`Id`/`Name` 在产物，`AuthorizeAsync` 的方法体串全不在。**
**→ 新细事实：同一个类里小写 id 是 UTF-16LE、大写 Name 是 UTF-8 —— 「哪种编码」连在一个类型内部都不统一。**

### ② 优先级 ① 上找到同一类错误的**第二例**

**`GetPaymentMethodsAsync` 读 `Vars["paymentMethodsUrl"]` —— 镜像 **0 命中**，那个键名是自造的。**

**R956 修过的 `paymentGateway` 是第一个，这是第二个。两者同形：能编译、读起来对，所以没人怀疑。
差别是这一个**没有替代名可得**。**

### ③ 而镜像里那个步骤是真的，连 ordinal 都对

```
(RpcGetPaymentMethodsg
<<RpcGetPaymentMethods>b__177_0<<RpcGetPaymentMethods>b__177_1g   ← 两个 lambda
RpcSubmitCardg  .<RpcSubmitCard>b__178_2g
```

**→ `RpcGetPaymentMethods` 是真实状态机，带**两个** lambda；`177` 与源码注释里的 ordinal **对得上**。
→ 缺的不是步骤、不是 ordinal，是**路由**。而 R958 已确立 NativeAOT 下按名反编译不成立 ⇒ **路由不可得**。**

### ④ 所以改的是「让它可见」，不是「修好它」

**`GetPaymentMethodsAsync` 的注释现在写明：① 键名两编码皆 0，是自造的 ② 镜像有那个步骤且 ordinal 对
③ 路由不可得，且零覆写 ⇒ 方法被裁。**

**并加守卫 `ThePaymentMethodsURLKeyIsRecordedAsInvented`。**

> **→ 守卫的判据不是「这个名字对不对」（它不对），而是「读源码的人会不会以为它被搜过」。**

### ⑤ 数字

| 度量 | R1007 | **R1008** |
|---|---|---|
| 套件 | 2218 | **2219（+1）** |
| 产物陈旧度 | 0 / 0 | **1 / 2,671（只改注释）** |
| 函数数 | 174,336 | **174,336** |
| **R1004 读数** | 需重验 | **确认** |
| **已知自造键名** | 1（已修） | **2（+`paymentMethodsUrl`，无替代名）** |

### 教训

> **「自造键名」不是一次性失误，它有一个**稳定的成因**：一个编译得过、读起来对的名字，没有任何机制会质疑它。
> → 唯一能发现它的动作是**去镜像里查那个名字** —— R956 做过一次，
> 而 `paymentMethodsUrl` 从写下那天活到 R1008 才被查。
> → 守卫钉的不是名字，是「这个名字没被搜过」这件事的说法。**
"""

BACKLOG_ADD = """

## 判据 (a)/① — **R1004 读数确认；`paymentMethodsUrl` 是第二个自造键名（无替代名，路由不可得）**（R1008）

### R1004 重验（`artifact_probe.py`，双编码 + sha256）

| 串 | utf-16-le | utf-8 |
|---|---|---|
| `adyen` | **19** | 0 |
| `commercehub` | **17** | 0 |
| `CommerceHub` | 0 | **1** |
| `CybersoleECOM` · `encryptedCardNumber` · `tokenUUID` · `/api/v1/sale` · `checkoutshopper-live.adyen.com` | 0 | 0 |

**→ `Id`/`Name` 在产物、`AuthorizeAsync` 方法体不在 —— R1004 成立。
→ 新事实：同一个类里 id 是 UTF-16LE、Name 是 UTF-8，「哪种编码」连类型内部都不统一。**

### 第二个自造键名

**`Vars["paymentMethodsUrl"]` 镜像 **0 命中**。R956 修过 `paymentGateway`，这是第二例。**
**而镜像里步骤是真的：`RpcGetPaymentMethods` 带两个 lambda，ordinal 177 与注释一致。
缺的是**路由**，而 R958（NativeAOT 下按名反编译不成立）⇒ 不可得。**

### 改了什么

**`GetPaymentMethodsAsync` 注释写明三点（键名自造 / 步骤与 ordinal 是真的 / 路由不可得且零覆写被裁）；
新增守卫 `ThePaymentMethodsURLKeyIsRecordedAsInvented`。**

**守卫判据不是「名字对不对」（它不对），是「读源码的人会不会以为它被搜过」。**

### 数字

**套件 2219（+1）· 陈旧度 1 / 2,671（只改注释）· 函数数 174,336 · 已知自造键名 2**

| 仍 Unknown | |
|---|---|
| `RpcGetPaymentMethods` 的路由 | 不可得（R958） |
| 还有多少自造键名未查 | 未扫 |

**纪律**：自造键名有一个稳定成因 —— 编译得过、读起来对，没有机制会质疑它。
"""

BLOCKER = """

---

## 432. **R1004 读数确认；`paymentMethodsUrl` 是第二个自造键名**

> R1008。**改 1 处注释 + 1 条守卫。** 套件 **2219 通过 / 0 失败 / 0 跳过**。

### 一、重验 R1004（新工具，双编码 + sha256）

```
artifact  .publish-aot/Cybersole.Ui.exe
sha256    36c16b3b3fd536d23cf4920603afc7761729a505ed4e0975de38444912891409

  adyen                          utf-16-le 19   utf-8 0   yes
  Adyen                          utf-16-le  2   utf-8 1   yes
  commercehub                    utf-16-le 17   utf-8 0   yes
  CommerceHub                    utf-16-le  0   utf-8 1   yes
  CybersoleECOM                           0         0   no
  encryptedCardNumber                     0         0   no
  tokenUUID                               0         0   no
  /api/v1/sale                            0         0   no
  checkoutshopper-live.adyen.com          0         0   no
```

**→ R1004 的结论**成立**：`Id` / `Name` 属性在产物里，`AuthorizeAsync` 的方法体串一个都不在。
→ 而它给出一条更细的事实：**同一个类**里，小写 id 是 **UTF-16LE**（19/17），
  大写 Name 是 **UTF-8**（1）。所以「哪种编码」连在**一个类型内部**都不统一。**

### 二、而优先级 ① 上找到同一类错误的第二例

**`GetPaymentMethodsAsync` 读 `Vars["paymentMethodsUrl"]`。查镜像：**

```
paymentMethodsUrl   0 命中
```

**→ 那个键名**不在镜像里**，是自造的。
→ R956 修过的 `paymentGateway`（→ `_paymentGatewayName`）是**第一个**，这是第二个。
→ 两者同形：一个能编译、读起来正确的名字，所以没人会怀疑它。
  差别在于这一个**没有替代名可得**。**

### 三、而镜像里那个步骤是真的，连 ordinal 都对

```
0x14337f4a9  (RpcGetPaymentMethodsg
0x1433800e6  <<RpcGetPaymentMethods>b__177_0<<RpcGetPaymentMethods>b__177_1g   ← 两个 lambda
0x14337f4c9  RpcSubmitCardg
0x14338012e  .<RpcSubmitCard>b__178_2g
```

**→ `RpcGetPaymentMethods` 是真实状态机，带**两个** lambda；`RpcSubmitCard` 带一个。
→ `177` 与 `StoreFlow.cs` 注释里的 `177 RpcGetPaymentMethods` **对得上** —— 那条注释是对的。
→ 缺的不是步骤、不是 ordinal，是**路由**。而 R958 已确立「按名字反编译在 NativeAOT 下不成立」，
  所以路由目前**不可得**，不是「没找到」。**

### 四、所以这一轮改的是「让它可见」

**`GetPaymentMethodsAsync` 的注释现在写明三件事：**

1. `paymentMethodsUrl` 在镜像里两编码皆 0 —— 这个键名是自造的
2. 镜像有那个步骤（`RpcGetPaymentMethods` + 两 lambda），ordinal 177 对得上
3. **路由不可得**，且 R963 意味着零覆写 → 这个方法整个被裁

**并加守卫 `ThePaymentMethodsURLKeyIsRecordedAsInvented`：钉住「键名在、注释在、
且『No flow overrides this method today』在」。**

**→ 守卫的判据不是「这个名字对不对」（它不对），而是「读源码的人会不会以为它被搜过」。**

### 五、数字

| 度量 | R1007 | R1008 |
|---|---|---|
| 套件 | 2218 | **2219（+1 自造键名守卫）** |
| 产物陈旧度 | 0 / 0 | **1 / 2,671（只改了注释）** |
| 函数数 | 174,336 | **174,336** |
| 函数比 | 62.91% | **62.91%** |
| **R1004 读数** | 需重验 | **确认（双编码 + sha256）** |
| **已知自造键名** | 1（`paymentGateway`，R956 已修） | **2（+`paymentMethodsUrl`，无替代名）** |

### 六、验证

```
cd replica
python tools/artifact_probe.py --strings adyen Adyen commercehub CommerceHub CybersoleECOM encryptedCardNumber tokenUUID "/api/v1/sale" checkoutshopper-live.adyen.com
  -> adyen utf-16-le 19 yes · commercehub 17 yes · 后缀串全 0
cd ../ && python analysis/ida.py str RpcGetPaymentMethods  -> {"n":5}，含两 lambda
python analysis/ida.py str paymentMethodsUrl              -> {"n":0}
cd replica
dotnet test --filter "FullyQualifiedName~PaymentGatewayNamingTests" -m:1  -> 5 通过
python tools/metrics_report.py  -> 套件 2219 · 陈旧度 1 / 2,671 · 函数数 174,336
```

### 七、仍然 Unknown

- **`RpcGetPaymentMethods` 的路由**：**不可得** —— R958 确立 NativeAOT 下按名反编译不成立。
- **还有多少自造键名未查**：**未扫** —— 需要一个「把所有 `Vars[...]` 键名对镜像查一遍」的扫法。

### 八、教训

**「自造键名」不是一次性的失误，它有一个**稳定的成因**：
一个编译得过、读起来对的名字，没有任何机制会质疑它。**

**→ 而唯一能发现它的动作是**去镜像里查那个名字** —— 那一步 R956 做过一次，
而 `paymentMethodsUrl` 从写下那天起活到 R1008 才被查。**

**→ 所以守卫钉的不是名字，是「这个名字没被搜过」这件事的说法。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1008", BLOCKER)
    ensure(RSTATUS, "R1008", BLOCKER)
    ensure(RVERDICT, "第 1008 轮", VERDICT)
    ensure(BACKLOG, "R1008", BACKLOG_ADD)

    note = (
        "\n## R1008 补充 — **R1004 读数确认；`paymentMethodsUrl` 是第二个自造键名**（套件 2219）\n\n"
        "**R1004 重验成立**（新工具双编码 + sha256）：`adyen` **utf-16-le 19** · `commercehub` **17** ·\n"
        "`CommerceHub` **utf-8 1** · 而 `CybersoleECOM`/`encryptedCardNumber`/`tokenUUID`/`/api/v1/sale`/`checkoutshopper` **全 0**。\n"
        "→ `Id`/`Name` 在产物、`AuthorizeAsync` 方法体不在。**新事实：同一类里 id 是 UTF-16LE、Name 是 UTF-8。**\n\n"
        "**优先级 ① 上找到第二例自造键名**：`Vars[\"paymentMethodsUrl\"]` 镜像 **0 命中**。\n"
        "（R956 修过 `paymentGateway` 是第一例。）\n"
        "而镜像里步骤**是真的**：`RpcGetPaymentMethods` 带**两个 lambda**，ordinal **177** 与源码注释一致。\n"
        "**缺的是**路由** —— 而 R958（NativeAOT 下按名反编译不成立）⇒ 不可得。**\n\n"
        "改动：`GetPaymentMethodsAsync` 注释写明三点（键名自造 / 步骤与 ordinal 真 / 路由不可得且零覆写被裁）；\n"
        "新增守卫 `ThePaymentMethodsURLKeyIsRecordedAsInvented`。\n"
        "**守卫判据不是「名字对不对」（它不对），是「读源码的人会不会以为它被搜过」。**\n\n"
        "数字：套件 2219（+1）· 陈旧度 1 / 2,671（只改注释）· 函数数 174,336 · 已知自造键名 2。\n\n"
        "纪律：**自造键名有稳定成因 —— 编译得过、读起来对，没有机制会质疑它。**\n\n"
        "下一轮：扫「所有 `Vars[...]` 键名对镜像查一遍」—— 那能一次性找出还有几个自造键名。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1008" not in h:
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
             for p, k in ((RBLOCK, "R1008"), (RSTATUS, "R1008"), (RVERDICT, "第 1008 轮"), (BACKLOG, "R1008")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1008: R1004's readings hold, and a second invented key name surfaces\n\n"
         "R1007 closed by naming this re-check as the next round's work. The probe confirms R1004: adyen appears nineteen\n"
         " times as UTF-16LE, commercehub seventeen, and every string from inside the method bodies is absent in both\n"
         " encodings. So the classes and their identifiers reached the artifact and the bodies did not.\n\n"
         "It also produces a fact finer than R1004's: within one class the lower-case id arrives as UTF-16LE and the\n"
         " capitalised name as UTF-8. Which encoding to search is not even uniform inside a single type, which is a good\n"
         " argument for never hand-writing the search again.\n\n"
         "Then priority one turned up the same defect a second time. GetPaymentMethodsAsync reads\n"
         " Vars[\"paymentMethodsUrl\"] and that string is absent from the image in both encodings. R956 corrected\n"
         " paymentGateway to the image's _paymentGatewayName; this is the same shape, a name that compiles and reads\n"
         " correctly so nothing questions it, with the difference that this one has no replacement to offer.\n\n"
         "The step itself is real, which makes the gap precise. RpcGetPaymentMethods exists with two lambdas beside it,\n"
         " RpcSubmitCard with one, and ordinal 177 matches the comment already in the source. What is missing is the\n"
         " route, and R958 established that decompiling by name does not work under NativeAOT, so the route is\n"
         " unobtainable rather than merely unfound.\n\n"
         "So the change is to make it visible rather than to fix it. The method now states that the key is not the\n"
         " image's, that the step and its ordinal are, and that the route cannot be had and that with no overrides the\n"
         " whole method is trimmed. A guard pins those three sentences, which is a different assertion from the usual\n"
         " one: it does not check whether the name is right, since it is not, it checks whether a reader could mistake it\n"
         " for a searched name.\n\n"
         "Figures: suite 2218 to 2219, freshness one file and 2,671 lines since the artifact was built because only a\n"
         " comment changed, count 174,336, two known invented key names.\n\n"
         "Unknown: the RpcGetPaymentMethods route, and how many other invented key names are still unexamined -- which\n"
         " suggests the next useful thing is a scan of every Vars key against the image rather than one more single find.\n\n"
         "The lesson is that an invented key name has a stable cause: it compiles, it reads correctly, and nothing in the\n"
         " process asks it where it came from. The only thing that finds one is looking for it in the artifact, which\n"
         " R956 did once and which paymentMethodsUrl waited from whenever it was written until this round.\n\n"
         "One comment and one guard changed; suite green at 2219."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()