"""Record R796: the card field names, and the Adyen question they raise."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 222. 卡字段名取全了 —— 而它们带出一个更要紧的问题

> R796。`HybrisFlow.SubmitPaymentAsync` 补上卡字段。

### 一、三族字段（Observation）

```
dwfrm_billing_creditCardFields_*           15 个
  adyenEncryptedData · cardBin · cardNumber · cardOwner · cardType · editNumber
  email · expirationMonth · expirationYear · phone · phonePrefix
  saveCard · saveCardAdyen · securityCode · selectedCardID

dwfrm_billing_paymentMethods_creditCard_*   6 个
  cvn · expiration · number · owner · saveCard · type

dwfrm_billing_gmoCreditCardFields_*         3 个   （日本网关）
```

**加上 `dwfrm_billing_paymentMethod` 与 `dwfrm_billing_paymentMethods_selectedPaymentMethodID`**
—— **用来指定用哪一种。**

### 二、`adyenEncryptedData` 是这个发现里最要紧的一项

**同一族里既有 `cardNumber`（明文）又有 `adyenEncryptedData`（Adyen 客户端加密）。**
**这说明该平台两种都支持，但没说这个站用哪一种。**

- 若这个站要 `adyenEncryptedData`，**复刻件发的明文卡字段会被拒**
- **而那种拒绝是可见的**（表单校验错误），不是静默的

**所以这里的选择是"发明文，让它自己拒"，而不是"猜一个加密字段的格式"。**
**加密字段是密钥+算法生成的，猜不了。**

### 三、实现

```
cardNumber     ← Profile.CardNumber
cardOwner      ← Profile.CardName
securityCode   ← Profile.CardCvv
expirationMonth/Year ← Profile.CardExpiry 拆两半（两位年补 20）
saveCard       ← "false"
email / phone  ← Account.Email / Profile.Phone
paymentMethod  ← Session.Vars["paymentMethodId"]（有才发，取值未取证）
```

**字段名全是镜像的。** 拆 `CardExpiry` 是复刻件自己的数据形状，不是镜像的。

### 四、验证

```
构建                已成功
完整套件            1766 通过 / 0 失败 / 0 跳过（未变）
四项度量            4 / 0 / 17 / 78 / 0（未变）
offspring 覆盖率     100%（未变 —— 这一步上一轮已经是"已实现"）
```

**覆盖率没动是对的**：这一轮换的是**同一个步骤里的字段**，不是补步骤。
**R791 就记过这一条：质量改动不要记成覆盖进展。**

### 五、仍然 Unknown

- **这个站要明文卡还是要 `adyenEncryptedData`**：**Unknown** —— 两种字段都在镜像里。
- **`paymentMethodId` 的取值**：**Unknown** —— 现在有就发、没有就不发。
- **`dwfrm_billing_paymentMethods_creditCard_*` 与 `..._creditCardFields_*` 该用哪一族**：
  **Unknown** —— 两族并存，现在用的是 `creditCardFields_` 那族（名字更全）。
- **`saveCardAdyen` 与 `saveCard` 的区别**：**Unknown**。
- **GMO 那一族是否只在日本站用**：**Inference（高）**，未验证。
"""

VERDICT = """

---

## 第 796 轮：卡字段取全了，而它们带出一个更要紧的问题

### 三族字段

```
dwfrm_billing_creditCardFields_*          15 个（含 cardNumber 与 adyenEncryptedData）
dwfrm_billing_paymentMethods_creditCard_*  6 个
dwfrm_billing_gmoCreditCardFields_*        3 个（日本网关）
+ dwfrm_billing_paymentMethod（选用哪种）
```

### `adyenEncryptedData` 是最要紧的一项

**同一族里既有明文 `cardNumber` 又有 `adyenEncryptedData`** —— **平台两种都支持，但没说这个站用哪种。**

- 若这个站要 `adyenEncryptedData`，**明文会被拒**
- **但那种拒绝是可见的**（表单校验错误），不是静默的

> **所以选择是「发明文，让它自己拒」，不是「猜一个加密字段的格式」—— 加密字段是密钥+算法生成的，猜不了。**

### 实现

卡号/持卡人/CVV/有效期（拆两半）/saveCard=false/email/phone + 可选的 paymentMethod。

**字段名全是镜像的；拆 `CardExpiry` 是复刻件自己的数据形状。**

### 验证

```
构建绿 · 整套 1766 / 0 · 四项度量未变 · offspring 覆盖率仍 100%
```

**覆盖率没动是对的** —— 换的是同一步骤里的字段，不是补步骤。

### 仍然 Unknown

明文卡 vs `adyenEncryptedData` · `paymentMethodId` 取值 · 两族字段该用哪族 · `saveCardAdyen` 与 `saveCard` 的区别
"""

BACKLOG_ADD = """

## 核心 — Hybris 支付字段（R796）

**三族卡字段名（镜像 Observation）**：

```
dwfrm_billing_creditCardFields_*          15 个：cardNumber · cardOwner · expirationMonth/Year
                                                securityCode · cardBin · saveCard · adyenEncryptedData …
dwfrm_billing_paymentMethods_creditCard_*  6 个：number · owner · cvn · expiration · type · saveCard
dwfrm_billing_gmoCreditCardFields_*        3 个（日本网关）
+ dwfrm_billing_paymentMethod
```

**已接**：`HybrisFlow.SubmitPaymentAsync` 发 `creditCardFields_*` 那族 + 地址 + 可选的 `paymentMethodId`。

| 仍 Unknown | |
|---|---|
| 明文卡 vs `adyenEncryptedData` | **两种字段都在镜像里，站点用哪种不知道** |
| `paymentMethodId` 取值 | 有就发、没有就不发 |
| 两族字段该用哪族 | 现用 `creditCardFields_`（名字更全） |
| `saveCardAdyen` 与 `saveCard` 的区别 | 未知 |

**纪律**：加密字段是密钥+算法生成的，**猜不了**。
**发明文让站点自己拒（可见的失败）胜过猜一个加密格式（静默的失败）。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R796", BLOCKER)
    ensure(RSTATUS, "R796", BLOCKER)
    ensure(RVERDICT, "第 796 轮", VERDICT)
    ensure(BACKLOG, "R796", BACKLOG_ADD)

    ok = True
    for path in (RBLOCK, RSTATUS, RVERDICT, BACKLOG):
        body = io.open(path, encoding="utf-8").read()
        key = "第 796 轮" if path == RVERDICT else "R796"
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R796: the card field names are recovered, and adyenEncryptedData is the question they raise\n\n"
         "Three families of card field names sit in the image: fifteen under dwfrm_billing_creditCardFields_, six under\n"
         "dwfrm_billing_paymentMethods_creditCard_, and three GMO names for a Japanese gateway, plus\n"
         "dwfrm_billing_paymentMethod to say which is in use.\n\n"
         "The interesting one is that the first family carries both cardNumber and adyenEncryptedData, alongside\n"
         "saveCard and saveCardAdyen. So the platform accepts a card either in the clear or through Adyen's client-side\n"
         "encryption, and nothing in the image says which this site requires.\n\n"
         "SubmitPaymentAsync now sends the image's own field names for the card, the holder, the security code, the two\n"
         "halves of the expiry, email and phone, and takes the payment method id from the session when a caller supplies\n"
         "one. The choice in the face of the encryption question is to send plaintext and let the site refuse: an\n"
         "encrypted field is produced from a key and an algorithm, so it cannot be guessed, whereas a rejection is\n"
         "visible and names itself.\n\n"
         "Coverage does not move, and that is correct -- this round changed the fields inside a step that already\n"
         "existed, not the number of steps, which is the distinction R791 set out after the Casio availability change.\n\n"
         "Unknown: which of the two card paths this site wants; what value the payment method id takes; which of the two\n"
         "field families is the live one; and how saveCard differs from saveCardAdyen.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
