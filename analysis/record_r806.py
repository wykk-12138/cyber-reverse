"""Record R806: the OnePageCheckout family has an owner-shaped payload, and a display truncation of mine."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 230. `OnePageCheckout` 的载荷读出来了；**顺带发现我误读了自己的工具**

> R806。修 `analysis/off_slot_reader.py` 的显示截断。未改产品代码。

### 一、载荷是 `BillingAddressFormViewModel` 的属性名

`sub_140D6AAA0`（`SetBillingAddress` 的调用者）是一个表单构造器：
`sub_14130CC50(dict, 字段名槽, 值)` 重复二十几次。读那些槽：

```
BillingAddressFormViewModel.JapaneseName      日本
BillingAddressFormViewModel.FuriganaName      フリガナ
BillingAddressFormViewModel.JapaneseSurname
BillingAddressFormViewModel.FuriganaSurname
BillingAddressFormViewModel.{Surname, Name, PostalCode, City, Region,
                             CountryCode, Phone, PhonePrefix, Mobile, MobilePrefix, Email}
→ /OnePageCheckout/CheckoutPlugin/SetBillingAddressAsync
```

**所以那 40 条给的是「客户端视图模型的属性名 + 插件方法名」，一个可 POST 的 URL 都没有。**
R805 的判断（名字不是端点）成立，这一轮把载荷也补上了。

**而 `Furigana`/`JapaneseName` 说明这是日本店面。**
`casio` 是日本站，且 `dwfrm_billing_CashFields_furigana` 也在池子里 ——
**所以这套属于 Demandware 那个模块，而它已经 100%。**

### 二、但 `DemandwareFlow` 用的不是这套路径

```
OnePageCheckout 提到   False
Checkout-Submit 提到   True
dwfrm_ 提到            True
```

**它走 `/Checkout-Submit*` + `dwfrm_*`，两个都在镜像里。**
**所以 `OnePageCheckout` 是同一个平台的另一条结账路径，复刻件走的是另一条。**

**这不构成覆盖缺口**（`DemandwareFlow` 已满），**但记在这里：平台有两条路，复刻件只实现了其中一条。**

### 三、我误读了自己的工具

第一版读取器对十四个槽全部返回 `'BillingAddressFormView'`，
**而长度分别印着 `len=40`、`len=43`、`len=32`** —— **同一个字符串不可能有四种长度。**

**我据此判断「读错位置了」，写了个新脚本去分辨「槽」与「串对象」。** 新脚本给出的结果是完整的属性名。

**但真因不是读错，是显示截断**：

```python
print("    slot 0x%-10x %-24r len=%-4s%s" % (slot, (text or "")[:22], length, ...))
#                                                              ^^^^^ 第 159 行
```

**`text[:22]`。`BillingAddressFormView` 恰好 21 个字符。**

**所以**：

- **读取是对的**，`object+12` 那条规则一直是准的
- **长度一直印着正确的 40**，而我只看到 21 个字符
- **我把「显示被截断」读成了「读取位置错」**

**这是「先假设形状，再把不符合假设的读成证据」的又一次 —— 只不过这次假设的是「我的工具坏了」。**

### 四、修了什么

```python
shown = text or ""
clipped = len(shown) > 96
print("    slot 0x%-10x %-52r len=%-4s%s%s" % (
    slot, shown[:96], length, "" if ok else "   (check)",
    "   [%d chars, shown 96]" % len(shown) if clipped else ""))
```

**显示到 96 字符，超过就明说「共 N 字符，显示 96」—— 不再静默截断。**

验证：

```
slot 0x146b5e268  'BillingAddressFormViewModel.JapaneseName'            len=40
slot 0x146b5e7c8  'BillingAddressFormViewModel.Surname'                 len=35
slot 0x146ab0028  '/OnePageCheckout/CheckoutPlugin/SetBillingAddressAsync' len=54
slot 0x1471151d0  'poq-app-id'                                          len=10
```

### 五、影响范围

**这个脚本本会话用过多次。凡是显示不超过 22 字符的结论，全部不受影响**（`poq-app-id` 10、`off_1471150B0` 那批）。
**超过 22 的那些，我当时看到的是前缀 —— 但长度一直是完整的，所以「对不对」当时就能验。**

**没有一条既有结论依赖那个被截断的显示**：本轮之前用它读的都是短串。

### 六、验证

```
python analysis\\off_slot_reader.py 0x146B5E268 ...    （见上，全串显示）
本轮未改产品代码
完整套件保持 1766 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- **`OnePageCheckout` 那条路要不要实现**：**Unknown** —— `DemandwareFlow` 已满，
  加第二条路是「更全」还是「多余」，取决于原版是不是两条都走。**没有证据说明两条都走。**
- **`sub_140D6C4E0`（`SetShippingAddress` 的调用者）的载荷**：**没读** —— 大概率同形（`ShippingAddressFormViewModel`）。
- **日本店面是 `casio` 还是 `converse`**：**Inference（中）**，未定。

### 八、教训

**工具显示截断会伪装成工具读错，而「工具坏了」这个假设比「我没看清长度」更容易被接受。**
**判断工具坏了之前，先看它自己印出来的校验字段（`len=40` 就在同一行）。**
"""

VERDICT = """

---

## 第 806 轮：`OnePageCheckout` 的载荷读出来了；而我误读了自己的工具

### 载荷是 `BillingAddressFormViewModel` 的属性名

```
JapaneseName · FuriganaName · JapaneseSurname · FuriganaSurname
{Surname, Name, PostalCode, City, Region, CountryCode, Phone,
 PhonePrefix, Mobile, MobilePrefix, Email}
→ /OnePageCheckout/CheckoutPlugin/SetBillingAddressAsync
```

**四十条里没有一个可 POST 的 URL —— 全是视图模型属性名与插件方法名。**
**`Furigana`/`JapaneseName` 说明是日本店面；`DemandwareFlow` 已满，这套属于它。**

**但 `DemandwareFlow` 走的是 `/Checkout-Submit*` + `dwfrm_*`，不是这套。**
**同一平台两条路，复刻件只实现了一条 —— 不构成缺口，但记下来。**

### 我误读了自己的工具

十四个槽都返回 `'BillingAddressFormView'`，**而长度印着 40/43/32** —— 同一串不可能有四种长度。
**我据此判「读错位置」，写新脚本去分辨槽与串对象。**

**真因是显示截断：第 159 行 `text[:22]`。`BillingAddressFormView` 恰好 21 字符。**

> **读取是对的；长度一直印着正确的 40；我只看到 21 个字符。**
> **我把「显示被截断」读成了「读取位置错」—— 这是「先假设形状」的又一次，只不过假设的是「我的工具坏了」。**

### 修了什么

**显示到 96 字符，超过就明说「共 N 字符，显示 96」，不再静默截断。**

```
slot 0x146b5e268  'BillingAddressFormViewModel.JapaneseName'   len=40
slot 0x146ab0028  '/OnePageCheckout/CheckoutPlugin/SetBillingAddressAsync'  len=54
```

### 影响范围

**本会话之前用它读的都是短串（`poq-app-id` 10 字符那批），没有既有结论依赖被截断的显示。**

### 教训

**判断工具坏了之前，先看它自己印出的校验字段 —— `len=40` 就在同一行。**
"""

BACKLOG_ADD = """

## 核心 — `OnePageCheckout` 载荷 + 一个工具显示 bug（R806）

**载荷是 `BillingAddressFormViewModel` 的属性名**（不是 URL）：

```
JapaneseName · FuriganaName · JapaneseSurname · FuriganaSurname
{Surname, Name, PostalCode, City, Region, CountryCode, Phone, PhonePrefix, Mobile, MobilePrefix, Email}
→ /OnePageCheckout/CheckoutPlugin/SetBillingAddressAsync   （由 sub_140D6AAA0 构造）
```

**`Furigana`/`JapaneseName` → 日本店面 → 属 `DemandwareFlow`（已 100%）。**
**但 `DemandwareFlow` 走 `/Checkout-Submit*` + `dwfrm_*`，不是这套 —— 同平台两条路，实现了一条。**

| 项 | 状态 |
|---|---|
| `off_slot_reader.py` 显示截断（`text[:22]`） | **已修**：显示 96，超出明说总长 |
| 既有结论是否受影响 | **否** —— 之前读的都是短串 |
| `sub_140D6C4E0`（SetShippingAddress）载荷 | **未读**，大概率同形 |

**纪律**：**判断工具坏了之前，先看它自己印出的校验字段（`len=40` 就在同一行）。**
显示截断会伪装成读取错误，而「工具坏了」比「我没看长度」更容易被接受。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R806", BLOCKER)
    ensure(RSTATUS, "R806", BLOCKER)
    ensure(RVERDICT, "第 806 轮", VERDICT)
    ensure(BACKLOG, "R806", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R806"), (RSTATUS, "R806"), (RVERDICT, "第 806 轮"), (BACKLOG, "R806")):
        body = io.open(path, encoding="utf-8").read()
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R806: the OnePageCheckout payload is a view model, and my slot reader was displaying 22 characters\n\n"
         "Decompiling the SetBillingAddress caller shows a form builder setting dictionary keys one after another, so\n"
         "reading those key slots gives the payload: BillingAddressFormViewModel with JapaneseName, FuriganaName,\n"
         "JapaneseSurname, FuriganaSurname, Surname, Name, PostalCode, City, Region, CountryCode, Phone, PhonePrefix,\n"
         "Mobile, MobilePrefix and Email, posted to /OnePageCheckout/CheckoutPlugin/SetBillingAddressAsync.\n\n"
         "So the forty strings are view-model property names and plugin method names, with no callable URL among them.\n"
         "R805's reading holds and the payload is now known too. The furigana properties say the storefront is\n"
         "Japanese, and the dwfrm_billing_CashFields_furigana string in the same pool points at the Demandware module,\n"
         "which is already at 100 percent -- though it reaches checkout through /Checkout-Submit* and dwfrm_*, not\n"
         "through OnePageCheckout. The platform has two routes and the replica implements one.\n\n"
         "The correction worth recording is mine. The first reader reported every slot as 'BillingAddressFormView'\n"
         "while printing lengths of 40, 43 and 32, which cannot all describe one string. I concluded the reader was\n"
         "fetching from the wrong address and wrote a second script to separate the slot from the object it points at.\n"
         "The second script produced the full names -- because the first one was right all along and merely cut its\n"
         "display at twenty-two characters on line 159, where 'BillingAddressFormView' is twenty-one. The length was\n"
         "printed correctly on the same line the whole time; I read the truncated text and ignored the number next to\n"
         "it.\n\n"
         "That is the same habit as section 2.7 with the assumption pointed at my own tooling: assume a shape, then\n"
         "read what contradicts it as confirmation. The display now goes to ninety-six characters and says so when it\n"
         "cuts. Nothing earlier depended on it -- the strings read before this round were short ones like poq-app-id.\n\n"
         "Unknown: whether the OnePageCheckout route should be implemented alongside Checkout-Submit, which depends on\n"
         "whether the original walks both and nothing yet says it does; the payload of the SetShippingAddress caller,\n"
         "which is probably the same shape; and whether the Japanese storefront is casio or converse.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
