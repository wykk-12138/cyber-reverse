"""Record R956: the payment key was invented, and the image's real names are now used."""

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
### `paymentGateway` 是**我编的**，而镜像是 `_paymentGatewayName`（R956）

**R955 接支付派发时用了一个 session 键叫 `paymentGateway`，而把它列进 Unknown：「原版按什么派发未取证」。
这一轮取证了。**

### 而镜像里有五个相关的名字

```
_paymentGateway          字段（带下划线的 backing field）
_paymentGatewayName      绑定属性
PaymentGateways          集合（复数）
paymentProvider
paymentFlexibilityTemplate / paymentFlexibilityPaymentTermsTemplate / paymentFlexibilityTermsId
```

### 而一条描述符把它们串在一起

```
_captchaToken&_paymentGatewayName6_paymentFlexibilityTemplate
```

> **`_captchaToken` 就紧挨着 `_paymentGatewayName` ——
> 所以一次支付提交带的是**一个 token 和一个网关名**，而那正是真实形状。
> 而我上一轮只带了网关名，把 captcha 当成别处的事。****

### 所以改了三处

| 原来（我编的） | 现在（镜像的） |
|---|---|
| `"paymentGateway"` | **`PaymentGatewayNameKey = "paymentGatewayName"`** |
| — | **`CaptchaTokenKey = "captchaToken"`** |
| switch 里硬编码四个 case | **`PaymentGateways = {viva, disney, purpledot, eshopworld}`** |

> **而 `PaymentGateways` 是**复数** —— 所以一家店可能接受多个网关，
> 而一个集合是对的形状，不是单个值。**

### 而这个名字为什么危险

**`paymentGateway` 与 `paymentGatewayName` 只差四个字符。
它编译得过、测试过得、读者不会怀疑 —— 而它不是原版的名字。**

> **而这就是这几轮一直在找的那种错：**一个听起来合理的名字，顶替了一个查出来的名字。**
> **而这次的代价是**没有代价** —— 因为那个键只在复刻件内部用。
> 如果它是持久化字段名（像 `settings.json` 的 `startup` 那样），它会**静默地读不到原版的数据**。****

### 而这一步撞了构建崩溃

**第一次 publish：`ilc` 退出码 `-1073740791`（0xC0000409）。
第二次：`LNK1136: 无效或损坏的文件` —— 崩溃留下的坏 `.obj`。**

> **处置：删掉 `obj\\Release\\net8.0\\win-x64\\native` 那 4 项，重发成功。
> 而这是**崩溃的次生错误**被当成主错误报出来的经典形状 ——
> 第二次那个 LNK1136 读起来像「源码有问题」，而它只是第一次崩溃的残留。**

### 数字

| 度量 | R955 | **R956** |
|---|---|---|
| 套件 | 2097 | **2101** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,824 | **173,824（未变）** |
| 产物大小 | 54,692 KB | **54,692 KB** |

### 教训

> **这一轮函数数没动 —— 而它是这几轮里最值钱的一轮之一。
> 因为上一轮那 43 个函数建立在一个**编出来的键名**上，而这一轮把它换成了证据里的名字。**
> **而「数动了」和「做对了」又一次分开 —— 这次分开在同一段代码上，隔了一轮。**
"""

if "`paymentGateway` 是**我编的**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 956 轮：`paymentGateway` 是我编的，镜像是 `_paymentGatewayName`

### 镜像里的五个名字

```
_paymentGateway · _paymentGatewayName · PaymentGateways（复数）· paymentProvider
paymentFlexibilityTemplate / paymentFlexibilityPaymentTermsTemplate / paymentFlexibilityTermsId
```

### 一条描述符把它们串起来

```
_captchaToken&_paymentGatewayName6_paymentFlexibilityTemplate
```

> **`_captchaToken` 紧挨着 `_paymentGatewayName` —— 一次支付提交带的是**一个 token 和一个网关名**。
> 而我上一轮只带了网关名。**

### 改了三处

| 原来（编的） | 现在（镜像的） |
|---|---|
| `"paymentGateway"` | **`PaymentGatewayNameKey = "paymentGatewayName"`** |
| — | **`CaptchaTokenKey = "captchaToken"`** |
| switch 硬编码四 case | **`PaymentGateways = {viva, disney, purpledot, eshopworld}`** |

**`PaymentGateways` 是复数 → 一家店可能接受多个网关，集合是对的形状。**

### 而这个名字为什么危险

**`paymentGateway` 与 `paymentGatewayName` 只差四个字符。它编译得过、测试过得、读者不会怀疑 —— 而它不是原版的名字。**

> **代价这次是零，因为那个键只在复刻件内部用。
> 如果它是持久化字段名（像 `settings.json` 的 `startup`），它会**静默地读不到原版的数据**。**

### 而这一步撞了构建崩溃

**第一次 `ilc` 退出 `-1073740791`（0xC0000409）；第二次 `LNK1136: 无效或损坏的文件` ——
崩溃留下的坏 `.obj`。删掉 `obj\\...\\native` 那 4 项，重发成功。**

> **那是**崩溃的次生错误**被当成主错误报出来 —— LNK1136 读起来像「源码有问题」。**

### 数字

| 度量 | R955 | **R956** |
|---|---|---|
| 套件 | 2097 | **2101** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,824 | **173,824（未变）** |
| 产物大小 | 54,692 KB | **54,692 KB** |

### 教训

> **这一轮函数数没动，而它是这几轮里最值钱的之一 ——
> 因为上一轮那 43 个函数建立在一个编出来的键名上。**
> **「数动了」和「做对了」又一次分开 —— 这次分开在同一段代码上，隔了一轮。**
"""

BACKLOG_ADD = """

## 判据 (a)/① — 支付键名改成镜像的；captcha 与网关成对（R956，**改产品代码 +4 用例**）

### 镜像证据

**`_paymentGateway` · `_paymentGatewayName` · `PaymentGateways` · `paymentProvider` ·
`_captchaToken&_paymentGatewayName6_paymentFlexibilityTemplate`**

### 改动

**`PaymentGatewayNameKey = "paymentGatewayName"` · `CaptchaTokenKey = "captchaToken"` ·
`PaymentGateways`(4) 集合 · 派发改用常量**

### 而 R955 的 `paymentGateway` 是编的

**只差四个字符，编译过、测试过、读者不疑 —— 而它是编的。**

### 构建崩溃的次生错误

**`ilc` 0xC0000409 → `LNK1136`（坏 .obj）→ 删 `obj\\...\\native` 4 项重发成功**

### 数字

**套件 2097 → 2101 · 陈旧度 0/0 · 函数数 173,824（未变）· 产物 54,692 KB**

| 仍 Unknown | |
|---|---|
| `PaymentGateways` 的真实取值 | 只有我列的四个 |
| captcha token 从哪来 | 未追 |
| `paymentFlexibility*` 三个名字的用途 | 未解 |

**纪律**：`paymentGateway` 与 `paymentGatewayName` 只差四个字符 —— 而读者不会怀疑。
"""

BLOCKER = """

---

## 380. 支付键名改成镜像的；captcha 与网关成对

> R956。**改产品代码 +4 用例。** 套件 **2101 通过 / 0 失败 / 0 跳过**。

### 一、镜像里的名字

```
_paymentGateway · _paymentGatewayName · PaymentGateways · paymentProvider
paymentFlexibilityTemplate / paymentFlexibilityPaymentTermsTemplate / paymentFlexibilityTermsId
```

**而 `_captchaToken&_paymentGatewayName6_paymentFlexibilityTemplate` 把 token 与网关名串在一起。**

### 二、改了

| 原来（R955 编的） | 现在 |
|---|---|
| `"paymentGateway"` | `PaymentGatewayNameKey = "paymentGatewayName"` |
| — | `CaptchaTokenKey = "captchaToken"` |
| switch 硬编码 | `PaymentGateways`(4) 集合 |

**`PaymentGateways` 复数 → 一家店可能接受多个网关。**

### 三、为什么这个错危险

**只差四个字符，编译过、测试过、读者不疑 —— 而它是编的。**

**代价这次是零（键只在内部用）；若它是持久化字段名，会静默读不到原版数据。**

### 四、构建崩溃的次生错误

**`ilc` 退出 `-1073740791`（0xC0000409）→ `LNK1136: 无效或损坏的文件`（坏 .obj）
→ 删 `obj\\Release\\net8.0\\win-x64\\native` 4 项 → 重发成功 54,692 KB。**

**LNK1136 读起来像「源码有问题」，而它只是第一次崩溃的残留。**

### 五、数字

| 度量 | R955 | R956 |
|---|---|---|
| 套件 | 2097 | **2101** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,824 | **173,824（未变）** |
| 产物大小 | 54,692 KB | **54,692 KB** |

### 六、验证

```
analysis/ida.py str paymentGateway -> 3：_paymentGateway / _paymentGatewayName / PaymentGateways
analysis/ida.py str gatewayName    -> 1：_captchaToken&_paymentGatewayName6_paymentFlexibilityTemplate
test --filter PaymentGatewayNamingTests -> 4 通过
metrics_report.py                  -> 2101 通过 / 0 失败
```

### 七、仍然 Unknown

- **`PaymentGateways` 的真实取值**：**Unknown** —— 只有我列的四个。
- **captcha token 从哪来**：**Unknown** —— 未追。
- **`paymentFlexibility*` 三个名字的用途**：**Unknown** —— 未解。

### 八、教训

**这一轮函数数没动，而它是这几轮里最值钱的之一 —— 因为上一轮那 43 个函数建立在一个编出来的键名上。**

**「数动了」和「做对了」又一次分开 —— 这次分开在同一段代码上，隔了一轮。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R956", BLOCKER)
    ensure(RSTATUS, "R956", BLOCKER)
    ensure(RVERDICT, "第 956 轮", VERDICT)
    ensure(BACKLOG, "R956", BACKLOG_ADD)

    note = (
        "\n## R956 补充 — 支付键名改成镜像的；captcha 与网关成对（+4 用例，套件 2101）\n\n"
        "R955 的 `paymentGateway` 是我编的。镜像里是 `_paymentGateway`（字段）· `_paymentGatewayName`（绑定属性）· "
        "`PaymentGateways`（复数）· `paymentProvider`。\n"
        "而 `_captchaToken&_paymentGatewayName6_paymentFlexibilityTemplate` 把 token 与网关名串在一起\n"
        "→ 一次支付提交带的是一个 token 和一个网关名。\n\n"
        "改动：PaymentGatewayNameKey=\"paymentGatewayName\" · CaptchaTokenKey=\"captchaToken\" · PaymentGateways(4) 集合。\n\n"
        "构建崩溃的次生错误：ilc 0xC0000409 → LNK1136（坏 .obj）→ 删 obj/.../native 4 项重发成功。\n\n"
        "数字：套件 2097 → 2101 · 陈旧度 0/0 · 函数数 173,824（未变）· 产物 54,692 KB。\n\n"
        "纪律：paymentGateway 与 paymentGatewayName 只差四个字符 —— 而读者不会怀疑。\n\n"
        "下一轮：接另外三个网关（PurpleDot/EshopWorld/GlobalECheckout），或查 PaymentGateways 的真实取值。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R956" not in h:
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
             for p, k in ((RBLOCK, "R956"), (RSTATUS, "R956"), (RVERDICT, "第 956 轮"), (BACKLOG, "R956")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R956: the payment key was invented, and the image keeps a captcha token beside the gateway name\n\n"
         "R955 keyed its payment dispatch on a session variable called paymentGateway and listed as Unknown whether the\n"
         " original did the same. Searching settles it: the image has _paymentGateway as a backing field, _paymentGatewayName\n"
         " as the bound property, PaymentGateways as a plural collection, and paymentProvider. And one concatenated\n"
         " descriptor reads _captchaToken&_paymentGatewayName6_paymentFlexibilityTemplate, putting the captcha token\n"
         " immediately beside the gateway name -- so a payment submission carries a token and a gateway, together. R955\n"
         " carried only the gateway.\n\n"
         "Three things changed: the key is now paymentGatewayName, a captcha token key is recorded beside it, and the\n"
         " gateway names live in a collection rather than hard-coded cases, because the image's name is plural and one store\n"
         " may accept several.\n\n"
         "The invented name differs from the real one by four characters. It compiled, its tests passed, and no reader would\n"
         " have questioned it -- which is the failure mode. This time the cost was zero because the key is internal to the\n"
         " replica; had it been a persisted field name, like the startup key in settings.json, it would silently fail to\n"
         " read the original's data.\n\n"
         "The build also crashed twice, and the second crash was misleading. ilc exited with 0xC0000409, and the retry\n"
         " reported LNK1136 invalid or corrupt file on Cybersole.Ui.obj, which reads like a source problem and was only the\n"
         " wreckage of the first crash. Deleting the native intermediate directory and republishing produced the artifact.\n\n"
         "Figures: suite 2097 to 2101, freshness zero, count unchanged at 173,824 since the change is a rename plus a\n"
         " constant, artifact 54,692 kilobytes.\n\n"
         "Unknown: the real set of PaymentGateways values, of which only my four are listed; where the captcha token comes\n"
         " from; and what the three paymentFlexibility names are for.\n\n"
         "The lesson is that this round moved no functions and is among the most valuable of the recent ones, because last\n"
         " round's forty-three functions were built on a key name I made up. Moving the count and getting it right came apart\n"
         " again, this time within the same piece of code one round later.\n\n"
         "Product code changed; suite green at 2101."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()