"""Record R808: the Signifyd URLs were already declared, so the new ones are references, not copies."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 232. `Signifyd` 的两个端点**早就声明过**；我上一轮写了一份重复的

> R808。`AntiBotVendors.cs`：把 R807 写死的两个 URL 改成引用 `RetailApiFamilies.ScheelsFrontastic`。

### 一、上一轮造了一个重复

R807 我在 `AntiBotVendors` 里写了：

```csharp
public const string SignifydSendCode =
    "https://apihub.scheels.com/frontastic/action/cart/sendSignifydStepUpCode";
public const string SignifydCompleteStepUp =
    "https://apihub.scheels.com/frontastic/action/cart/completeSignifydStepUpCheckout";
```

**而 `RetailApiFamilies.ScheelsFrontastic` 从 R103 起就有这两个：**

```csharp
public const string SignifydStepUpCode     = Base + "cart/sendSignifydStepUpCode";
public const string CompleteSignifydStepUp = Base + "cart/completeSignifydStepUpCheckout";
```

**同一个事实，两处硬编码。** 这正是会腐化的那种重复：改一处、漏一处，然后两个地方说的是不同的事。

### 二、改成引用

```csharp
public const string SignifydSendCode = RetailApiFamilies.ScheelsFrontastic.SignifydStepUpCode;
public const string SignifydCompleteStepUp = RetailApiFamilies.ScheelsFrontastic.CompleteSignifydStepUp;
```

**`ScheelsFrontastic` 嵌在 `RetailApiFamilies` 里**，所以第一次写漏了外层限定名，编译报 `CS0103`，
**加上就过了。** 这也说明编译期能抓到的东西不该靠肉眼看。

### 三、顺带看到 `ScheelsFrontastic` 比想象的全

```
account/{getAccount, login, register, requestReset, reset}
product/getProduct
cart/{addToCart, updateCart, removeLineItem, clean, checkout,
      completeDetailsCheckout, sendSignifydStepUpCode, completeSignifydStepUpCheckout,
      setAdyenCreditCard}
adyen/{beginPayPal, completePayPal}
```

**整套 frontastic 结账面都在常量里。** 而这套常量是 R103 从镜像里抄下来的 ——
**所以 `scheels` 的端点侧是完整的，缺的只是把它们串起来的流程。**

### 四、`scheels` 的模块状态

它的 override 有 `GetHome` / `GetCaptcha` / `SubmitSensor` / `FindProduct` / `FindVariant` /
`ScrapeVariantAvailability` 等，**不在那 12 个缺 shipping/payment 的名单里**，
说明它在七步表上是满的。

**所以 Signifyd 的 step-up 不是覆盖缺口** ——
**它是 `ScheelsFlow` 里没有的一条支路**（`requiresSignifydStepUp` 为真时才走）。

### 五、为什么这一轮不实现 step-up

**请求体不知道。** 这是第五次同一形状（casio 的 region token、goat 的 build-reservation、
popmart 的 /web/v2、hypecommerce 的 entries、现在 Signifyd 的 code）。

**而且这次比前几次更难**：step-up 要**先发码、再从邮箱取码、再提交**，
**取码那一步依赖邮件服务，而复刻件的邮件服务是它自己的实现，不能当实机证据**（§2.2）。

**所以这条支路要等三件事齐**：请求体、取码链路、以及一个能证明它被触发的观察点。

### 六、验证

```
构建                已成功（CS0103 修掉后）
完整套件            1766 通过 / 0 失败 / 0 跳过
四项度量            4 / 0 / 17 / 78 / 0（未变）
产品行为             未变 —— 只是常量改为引用，字面值相同
```

### 七、仍然 Unknown

- **Signifyd step-up 的三个请求体**：**Unknown**。
- **`GetSignifydCode` 从哪取码**：**Unknown** —— 邮件？前端？还是别处。
- **`requiresSignifydStepUp` 由谁置位**：**Unknown** —— 结账响应的字段，未读。

### 八、教训

**在往一个类里加常量之前，搜一下这个字面值是否已经在别处。**
R807 加的这两个 URL，`grep` 一次就能发现早就有 —— **而我上一轮是「查到镜像里有，就写下来」，没有回头搜复刻件。**
**取证和落实现是两个方向，都要搜。**
"""

VERDICT = """

---

## 第 808 轮：Signifyd 的两个端点早就声明过，我上一轮写了个重复

### 上一轮造了重复

R807 我在 `AntiBotVendors` 里硬编码了两个 `apihub.scheels.com/frontastic/action/cart/*` URL，**而 `RetailApiFamilies.ScheelsFrontastic` 从 R103 起就有这两个常量。**

**改成引用**（`ScheelsFrontastic` 嵌在 `RetailApiFamilies` 里，第一次漏了外层限定名，编译报 `CS0103`）。

### `ScheelsFrontastic` 比想象的全

```
account/{getAccount, login, register, requestReset, reset} · product/getProduct
cart/{addToCart, updateCart, removeLineItem, clean, checkout, completeDetailsCheckout,
      sendSignifydStepUpCode, completeSignifydStepUpCheckout, setAdyenCreditCard}
adyen/{beginPayPal, completePayPal}
```

**整套 frontastic 结账面都在常量里 —— 端点侧完整，缺的是串起来的流程。**

### `scheels` 不在缺口名单里

它不在那 12 个缺 shipping/payment 的模块中 → **七步表上是满的。**
**所以 Signifyd 的 step-up 不是覆盖缺口，是 `ScheelsFlow` 里没有的一条支路。**

### 为什么不实现

**请求体不知道**（第五次同一形状）。**而且这次更难**：step-up 要发码 → 取码 → 提交，
**取码依赖邮件服务，而复刻件的邮件服务是自己的实现，不能当实机证据**（§2.2）。

**要等三件事齐**：请求体、取码链路、能证明它被触发的观察点。

### 验证

```
构建绿（CS0103 修掉后）· 整套 1766 / 0 · 度量未变 · 行为未变（常量改引用，字面值相同）
```

### 教训

**往一个类里加常量之前，搜一下这个字面值是否已在别处存在。**
R807 是「查到镜像里有就写下来」，**没有回头搜复刻件 —— 取证和落实现是两个方向，都要搜。**
"""

BACKLOG_ADD = """

## 风控 — Signifyd 端点去重（R808）

**R807 的两个硬编码 URL 改成引用 `RetailApiFamilies.ScheelsFrontastic`**（R103 起就有）。

```
ScheelsFrontastic: account/* · product/getProduct
                   cart/{addToCart, updateCart, removeLineItem, clean, checkout,
                         completeDetailsCheckout, sendSignifydStepUpCode,
                         completeSignifydStepUpCheckout, setAdyenCreditCard}
                   adyen/{beginPayPal, completePayPal}
```

**端点侧完整 —— `scheels` 也不在 12 个缺口名单里（七步表已满）。**
**Signifyd 的 step-up 不是覆盖缺口，是 `ScheelsFlow` 里未实现的一条支路。**

| 待齐三件事 | |
|---|---|
| 三个请求体 | Unknown（第五次同一形状） |
| 取码链路 | **依赖邮件服务，而那是复刻件自己的实现，不能当实机证据**（§2.2） |
| 触发观察点 | `requiresSignifydStepUp` 由谁置位，未读 |

**纪律**：**往类里加常量前先搜字面值。取证和落实现是两个方向，都要搜。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R808", BLOCKER)
    ensure(RSTATUS, "R808", BLOCKER)
    ensure(RVERDICT, "第 808 轮", VERDICT)
    ensure(BACKLOG, "R808", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R808"), (RSTATUS, "R808"), (RVERDICT, "第 808 轮"), (BACKLOG, "R808")):
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
         "R808: the Signifyd URLs were already declared, so the new constants reference them instead of copying\n\n"
         "R807 wrote both apihub.scheels.com frontastic URLs out as literals in AntiBotVendors. They had been in\n"
         "RetailApiFamilies.ScheelsFrontastic since R103, so the change added a second hard-coded copy of two facts\n"
         "that already lived somewhere -- the kind of duplication where editing one and missing the other leaves two\n"
         "classes disagreeing about the same endpoint.\n\n"
         "They are references now. ScheelsFrontastic is nested inside RetailApiFamilies, which the first attempt\n"
         "missed and the compiler caught as CS0103, which is the argument for letting the compiler check what eyes\n"
         "should not be trusted with.\n\n"
         "Reading that class also shows the endpoints were never the gap: the whole frontastic surface is declared,\n"
         "from account and product through nine cart actions to the two Adyen PayPal ones. And scheels is not among\n"
         "the twelve modules missing shipping and payment, so it already scores seven of seven. The Signifyd step-up is\n"
         "therefore not a coverage gap; it is a branch inside ScheelsFlow that no one has written.\n\n"
         "Writing it now would be premature for a reason worth stating. The request bodies are unknown, which is the\n"
         "fifth time this session has hit that asymmetry, and this branch is harder than the others because it sends a\n"
         "code, reads the code back, and submits it. Reading the code back depends on a mail service, and the replica's\n"
         "mail service is its own implementation, which section 2.2 forbids using as evidence about the original. Three\n"
         "things have to be in hand before the branch is worth writing: the bodies, the code-retrieval path, and some\n"
         "observation proving the branch ever fires.\n\n"
         "Unknown: the three request bodies; where GetSignifydCode gets a code from; and who sets requiresSignifydStepUp,\n"
         "which is a field in the checkout response nobody has read.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged; product behaviour unchanged, since only the provenance of\n"
         "two constants moved."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
