"""Record R805: casio's ceiling is complete, poq-app's ceiling is too, and a third checkout shape turns up."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 229. 三条发现：`casio` 天花板补齐、`poq-app` 也有天花板、**池子里还有第三套结账面**

> R805。未改产品代码。

### 一、`casio`：22 个组合都是 0（Observation）

R804 说「动作词 × bhawar 这个组合我没搜」。**这一轮补上**：11 个动作词 × 两个方向 = 22 个正则，
命中 **0 条新串**（把已知的两条主机串排除后）。

**所以 `casio` 的天花板现在是完整的**：**所有写法都试过，都是空。**
**5/7 是镜像能给出的全部。**

### 二、`poq-app`：`/clients/` 一共 7 条，5 条是真的

```
https://platform.poq.io/clients/office/AtaVerifyCaptcha
https://platform.poq.io/clients/office/recaptcha?trackingId=
https://platform.poq.io/clients/offspring/account/guest-token
https://platform.poq.io/clients/offspring/cart/items
https://platform.poq.io/clients/offspring/checkout/start
https://platform.poq.io/clients/offspring/products?ids=
（另两条是 SignalR 源码路径，误命中）
```

**Poq 的客户端 API 就这 5 个端点，`checkout/` 下面只有 `start`，没有提交。**

**所以 `poq-app` 的 4/7 也是天花板。** 它缺的三步（shipping / payment / order）**在镜像里没有对应端点。**

### 三、但 `/checkout/` 家族还有 40 条 —— 有第三套结账面

```
/Checkout/PlaceOrder/(\\d+)            ← 下单 URL 模式
/OnePageCheckout/Cart
/OnePageCheckout/Cart/MiniCartContent
/OnePageCheckout/Confirmation
/OnePageCheckout/CheckoutPlugin/SetBillingAddressAsync
/OnePageCheckout/CheckoutPlugin/SetGuestEmailAsync
/OnePageCheckout/CheckoutPlugin/SetShippingAddressAsync
/OnePageCheckout/CheckoutPlugin/SetGiftWrappingAsync
/checkout/?stage=payment|placeOrder|shipping
```

**`SetShippingAddress` / `SetBillingAddress` / `PlaceOrder` —— 正是缺的那三步的名字。**

**而且 `/OnePageCheckout/*`（0x146ab0…）与 Demandware 的 `/Checkout-Submit*`（0x146aaf…）在池子里相邻，
属于同一字符串簇** —— 很可能同属一个平台家族。

### 四、但它们**不是 URL**

`sub_140D6C4E0`（1387 B）与 `sub_140D6AAA0`（1539 B）两个调用者找到了。
**而 `CheckoutPlugin/Set*Async` 是 SFCC 的插件接口方法名 —— 客户端调用的是插件方法，不是路径。**

**所以这 40 条给出的是「形状」，不是「端点」。**
**把它们当 URL 用是 R773 那个错（把字段名当端点）的翻版。**

### 五、所以这一轮没有改代码

三条都是「查清了来源」，没有一条是「可以实现了」。
**而且第三条恰好说明：现在不该动 `poq-app`** ——
**它的四个现有动作是基于实机抓包的 Poq 客户端 API，而上面这套是另一个平台的形状。混在一起才是错。**

### 六、这一条对判据 (f) 的意义

`casio` 与 `poq-app` 的缺口理由现在都是**最硬的一类**：

| 模块 | 缺口 | 理由 |
|---|---|---|
| `casio` | shipping / payment | **22 个正则组合全空** |
| `poq-app` | shipping / payment / order | **`/clients/` 全部 5 个端点里没有** |

**不是「还没查」，是「查到了全部」。**

### 七、仍然 Unknown

- **`/OnePageCheckout/*` 属于哪个模块**：**Unknown** —— 两个调用者都在 `0x140D6xxxx`，
  **但那个函数没有暴露站点 id**。
- **这套是不是 SFCC**：**Inference（中）** —— `OnePageCheckout` + `CheckoutPlugin/Set*Async` 是 SFCC 的形状，
  **但池子里没有 `sfcc`/`salesforce` 字样被确认**。
- **`/Checkout/PlaceOrder/(\\d+)` 的调用点**：**没查**。

### 八、验证

```
本轮未改产品代码
完整套件保持 1766 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 九、教训

**「找到名字」和「找到端点」是两步。**
这一轮的 40 条看似把缺的三步全给了，**但它们是插件方法名** ——
**如果我把 `SetShippingAddressAsync` 当成 URL 去 POST，那会是这几十轮里最像成功的一次失败。**
"""

VERDICT = """

---

## 第 805 轮：两个天花板补齐，池子里还有第三套结账面

### `casio`：22 个组合都是 0

11 个动作词 × 两个方向，**命中 0 条新串**。**天花板完整了 —— 5/7 是镜像给的全部。**

### `poq-app`：`/clients/` 一共 7 条，5 条真的

```
clients/office/AtaVerifyCaptcha · clients/office/recaptcha?trackingId=
clients/offspring/{account/guest-token, cart/items, checkout/start, products?ids=}
```

**`checkout/` 下面只有 `start`，没有提交 → 4/7 也是天花板。**

### 但 `/checkout/` 家族还有 40 条 —— 第三套结账面

```
/Checkout/PlaceOrder/(\\d+)
/OnePageCheckout/{Cart, Cart/MiniCartContent, Confirmation}
/OnePageCheckout/CheckoutPlugin/{SetBillingAddressAsync, SetShippingAddressAsync,
                                 SetGuestEmailAsync, SetGiftWrappingAsync}
```

**`SetShippingAddress` / `SetBillingAddress` / `PlaceOrder` —— 正是缺的那三步的名字。**
**而且与 Demandware 的 `/Checkout-Submit*` 在池子里地址相邻，同一字符串簇。**

### 但它们**不是 URL**

两个调用者找到了（`sub_140D6C4E0` / `sub_140D6AAA0`），**而 `CheckoutPlugin/Set*Async` 是 SFCC 的插件方法名。**

> **把它们当 URL 用，就是 R773「把字段名当端点」的翻版。**
> **如果我把 `SetShippingAddressAsync` 当路径去 POST，那会是这几十轮里最像成功的一次失败。**

### 所以没改代码

**而且第三条恰好说明现在不该动 `poq-app`** —— 它现有的四个动作基于 Poq 的实机 API，
**上面这套是另一个平台的形状。混在一起才是错。**

### 对判据 (f) 的意义

| 模块 | 缺口 | 理由 |
|---|---|---|
| `casio` | shipping / payment | **22 个正则组合全空** |
| `poq-app` | shipping / payment / order | **`/clients/` 全部 5 个端点里没有** |

**不是「还没查」，是「查到了全部」。**

### 教训

**「找到名字」和「找到端点」是两步。**
"""

BACKLOG_ADD = """

## 核心 — 两个天花板 + 第三套结账面（R805）

**两个天花板补齐**：

| 模块 | 缺口 | 已排除的写法 |
|---|---|---|
| `casio` | shipping / payment | **22 个「动作词 × bhawar」正则，0 条新串** |
| `poq-app` | shipping / payment / order | **`/clients/` 全部 7 条（5 条真），没有提交端点** |

**第三套结账面（新发现，未使用）**：

```
/Checkout/PlaceOrder/(\\d+)
/OnePageCheckout/{Cart, Cart/MiniCartContent, Confirmation}
/OnePageCheckout/CheckoutPlugin/{SetBillingAddressAsync, SetShippingAddressAsync,
                                 SetGuestEmailAsync, SetGiftWrappingAsync}
/checkout/?stage=payment|placeOrder|shipping
调用者：sub_140D6C4E0(1387 B) · sub_140D6AAA0(1539 B)
```

**关键警告：`CheckoutPlugin/Set*Async` 是 SFCC 的插件方法名，不是 URL。**
**当 URL 用 = R773「字段名当端点」的翻版。**

| Unknown | |
|---|---|
| 这套属于哪个模块 | 两个调用者没暴露站点 id |
| 是否真是 SFCC | Inference（中）；池子里未确认 `sfcc`/`salesforce` |
| `/Checkout/PlaceOrder/(\\d+)` 调用点 | 未查 |

**纪律**：**「找到名字」和「找到端点」是两步。** 40 条看着把缺的三步全给了，**但一条都不是可调的路径。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R805", BLOCKER)
    ensure(RSTATUS, "R805", BLOCKER)
    ensure(RVERDICT, "第 805 轮", VERDICT)
    ensure(BACKLOG, "R805", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R805"), (RSTATUS, "R805"), (RVERDICT, "第 805 轮"), (BACKLOG, "R805")):
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
         "R805: two ceilings completed, and a third checkout surface that is names rather than paths\n\n"
         "R804 named the one variation it had not tried, so this ran it: eleven action words against bhawar in both\n"
         "directions, twenty-two patterns, zero new strings. Casio's ceiling is now complete rather than convenient.\n\n"
         "Poq-app turns out to have a ceiling too. The whole client API is seven strings, five of them real endpoints:\n"
         "guest-token, cart/items, checkout/start, products?ids= and two office captcha routes. Checkout has a start and\n"
         "no submit, so its four of seven is all the image carries, not all the work done.\n\n"
         "Then the checkout family yielded forty strings, including a third shape: OnePageCheckout with a CheckoutPlugin\n"
         "carrying SetShippingAddress, SetBillingAddress, SetGuestEmail and SetGiftWrapping, plus /Checkout/PlaceOrder\n"
         "with a numeric capture. Those are exactly the three steps casio and poq-app lack.\n\n"
         "They are not URLs. Two callers turned up and the names are SFCC plugin method names, so what they describe is\n"
         "the shape of a client plugin contract rather than anything to POST to. Using SetShippingAddressAsync as a path\n"
         "would be R773 repeated -- reading a field name as an endpoint -- and it would fail in the way that looks most\n"
         "like success, which is why nothing was wired.\n\n"
         "That also settles why poq-app should not be touched this round. Its four actions follow Poq's own client API\n"
         "from a live capture; the OnePageCheckout family belongs to something else, and mixing the two would be the\n"
         "error rather than the fix.\n\n"
         "Both modules now have the strongest kind of gap reason available: not 'not looked at yet' but 'every variation\n"
         "searched and the source does not contain it'.\n\n"
         "Unknown: which module the OnePageCheckout family belongs to, since neither caller exposes a site id; whether it\n"
         "is genuinely SFCC, which the shape suggests but the pool does not confirm; and the call site of the PlaceOrder\n"
         "pattern.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
