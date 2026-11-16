"""Record R789: Warhammer's add-to-cart speaks the image's GraphQL."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 215. Warhammer 加购改成镜像的 GraphQL —— REST 那版是编的

> R789。改 `RetailFlows.cs`（`WarhammerFlow.AddToCartAsync` + `AddToCartMutation` 常量）；
> 新增 `WarhammerGraphQlTests`（5 条）。

### 一、改之前

```csharp
var payload = new JObject { ["sku"] = c.Session.VariantId, ["quantity"] = c.Session.Quantity };
var res = await PostJsonAsync(c, $"{ApiHost}/api/basket/items", …);
```

**`/api/basket/items` 是编的。** 镜像里那个路径一次都没出现。

### 二、改之后：用镜像的 mutation 原文

R788 从池子 `0x1470cc484` 取回的 `AddToCart`，变量在签名里全拼出来：

```
mutation AddToCart($sku: String!, $fascia: String!, $linkedOfferId: String, $offerId: String,
  $quantity: Int, $statusPoint: String, $recaptchaToken: String, $storeId: String,
  $algoliaQueryId: String, $objectId: String)
```

**非空只有两个：`sku` 与 `fascia`。响应只选一个字段：`ctCartJWT`。**

复刻件现在发：

```json
{"operationName":"AddToCart","query":"<镜像原文>","variables":{"sku":…,"fascia":…,"quantity":…}}
```

**并且把响应里的 `ctCartJWT` 记进会话** —— 那是后续步骤用来认证的。

### 三、`fascia` 我没有猜

**`fascia` 是必填，但它的取值没取证。**
**所以不存在时直接如实失败**：

> `warhammer: AddToCart requires a fascia (storefront), and the image does not spell out its value`

**理由与 R785 一致**：`fascia` 猜错会把商品加到错的店面，**而且不会报错**。

### 四、Observation / Inference

- **Observation**：operation 名、十个变量、哪两个非空、唯一被选字段、`recaptchaToken` 是变量
- **Inference（中）**：`/graphql` 接受 `{operationName, query, variables}` 这个信封 ——
  **这是 GraphQL-over-HTTP 的标准形状，镜像自己的请求构造器与它一致，但没有把信封拼出来**

### 五、5 条测试

```
TheOperationNameMatchesTheRecoveredText        以 "mutation AddToCart(" 开头
SkuAndFasciaAreTheOnlyNonNullArguments         恰好 2 个 '!'
TheOptionalRecaptchaTokenIsDeclared            说明该站加购要 reCAPTCHA
TheSelectionIsTheCartJwt                       只选 ctCartJWT + __typename，不含 products
EveryDeclaredVariableIsAlsoPassedThrough       十个变量声明与传参都在
```

**为什么要这五条**：**536 字符手抄，错一个字符照样编译通过。**
**测试查的是不变量，不是抄写本身。**

### 六、一次真实的偶发，不粉饰

第一次全量：**1765 通过 / 1 失败**，失败是 `TaskProfileViewTests.TaskAndProfileUserControlsConstruct`。

- **单跑该测试：17 / 17 通过**
- **复跑全量：1766 通过 / 0 失败**

**所以是全量并行下的偶发（Avalonia UI 构造），与这一轮改动无关。**
**但我没有因此就说它"过了"** —— 判据是复跑，不是推断。
**若它以后反复出现，应单列成一条 flake，而不是混进"失败"或"通过"。**

### 七、验证

```
构建                已成功
WarhammerGraphQlTests   5 / 5
完整套件            1766 通过 / 0 失败 / 0 跳过（1761 + 5）
四项度量            4 / 0 / 17 / 78 / 0（未变）
Warhammer 覆盖率    未变 —— 这一轮换的是既有步骤的请求形状，不是补步骤
```

### 八、仍然 Unknown

- **`fascia` 的取值**：**Unknown** —— 现在会让加购在这上面明确失败，而不是猜。
- **`SubmitOrderAsync` 仍是 `/api/orders`（编的）** —— 镜像里有 `ApproveOnboardPaymentMutation`，
  但订单提交那一步的 operation 未定位。
- **其余五条 mutation 未翻**：`AddItemToCart` / `AddCreditCard` / 两条匿名 / `ApproveOnboardPayment`。
- **响应消费面**：只用了 `ctCartJWT`。
"""

VERDICT = """

---

## 第 789 轮：Warhammer 加购改成镜像的 GraphQL

### 改之前是编的

`POST {ApiHost}/api/basket/items` —— **镜像里那个路径一次都没出现。**

### 改之后用 R788 取回的原文

```
mutation AddToCart($sku: String!, $fascia: String!, $linkedOfferId: String, $offerId: String,
  $quantity: Int, $statusPoint: String, $recaptchaToken: String, $storeId: String,
  $algoliaQueryId: String, $objectId: String)
```

**非空只有 `sku` 与 `fascia`；响应只选 `ctCartJWT`。**

请求体：`{operationName, query, variables}`，并把 `ctCartJWT` 记进会话供后续认证。

### `fascia` 我没有猜

**必填，但取值没取证** → 不存在时如实失败，而不是猜。
**猜错会把商品加到错的店面，而且不报错。**

### 5 条测试

operation 名 · 恰好两个非空 · `recaptchaToken` 在 · 只选 `ctCartJWT` · 十个变量都传。

**536 字符手抄，错一个字符照样编译 —— 所以测试查的是不变量。**

### 一次真实的偶发

第一次全量 **1765/1**，失败是 `TaskProfileViewTests`。**单跑 17/17 过，复跑全量 1766/0。**

**是全量并行下的偶发，与本轮改动无关 —— 但我用复跑证明，没有用推断。**

### 验证

```
WarhammerGraphQlTests 5/5 · 整套 1766 / 0 · 度量未变 · 覆盖率未变（换形状，不补步骤）
```

### 仍然 Unknown

`fascia` 取值 · `SubmitOrderAsync` 仍是编的 `/api/orders` · 其余五条 mutation 未翻 · 响应消费面
"""

BACKLOG_ADD = """

## 核心 — Warhammer GraphQL（R789 已落地一条）

**`AddToCart` 已改成镜像原文**（R788 取回，池子 `0x1470cc484`）：

```
mutation AddToCart($sku: String!, $fascia: String!, … ) { addToCart(…) { ctCartJWT __typename } }
```

- 请求体 `{operationName, query, variables}`，`ctCartJWT` 记进会话
- **`fascia` 必填但取值 Unknown → 明确失败，不猜**
- 5 条测试钉住不变量（非空数 · 只选 ctCartJWT · 十变量都传）

| 待做 | 说明 |
|---|---|
| `SubmitOrderAsync` | **仍是编的 `/api/orders`** —— 订单提交的 operation 未定位 |
| `AddItemToCart` / `AddCreditCard` / 两条匿名 / `ApproveOnboardPayment` | 未翻（原文在 `analysis/warhammer_graphql.txt`） |
| `fascia` 取值 | Unknown |
| 响应消费面 | 只用了 `ctCartJWT` |

**注意**：本轮覆盖率未变 —— **换的是既有步骤的请求形状，不是补步骤。**
**质量改动不要记成覆盖进展。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s += %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R789", BLOCKER)
    ensure(RSTATUS, "R789", BLOCKER)
    ensure(RVERDICT, "第 789 轮", VERDICT)
    ensure(BACKLOG, "R789", BACKLOG_ADD)

    for path, markers in ((RBLOCK, ("R789",)), (RSTATUS, ("R789",)),
                          (RVERDICT, ("第 789 轮",)), (BACKLOG, ("R789",))):
        body = io.open(path, encoding="utf-8").read()
        print("  check %-26s %s" % (path.split("\\")[-1], all(m in body for m in markers)))

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R789: Warhammer's add-to-cart speaks the image's GraphQL instead of an invented REST call\n\n"
         "The old code posted to {ApiHost}/api/basket/items with a sku and a quantity. That path appears nowhere in the\n"
         "image. R788 recovered the site's actual AddToCart mutation, and its signature spells out everything the\n"
         "request needs: ten variables of which exactly two are non-null, sku and fascia, and a selection set that\n"
         "returns a single field, ctCartJWT.\n\n"
         "So the flow now posts the image's own query text inside the standard GraphQL envelope, with operationName,\n"
         "query and variables, and records ctCartJWT into the session because that token is what later steps\n"
         "authenticate with. The recaptchaToken variable being declared at all says this site's add-to-cart expects a\n"
         "solved reCAPTCHA, so the flow passes one through when the anti-bot tokens hold it.\n\n"
         "fascia is required and its value is not recovered, so its absence is a clear failure naming that fact rather\n"
         "than a guess. Getting fascia wrong would add the item to the wrong storefront without any error surfacing,\n"
         "which is the same reasoning that kept the Casio region token out of the code.\n\n"
         "Five tests pin the invariants rather than the transcription: the operation name, exactly two bangs, the\n"
         "recaptcha variable being declared, the selection containing ctCartJWT and nothing else, and all ten variables\n"
         "both declared and passed through. A 536-character hand copy that loses one character still compiles, so a\n"
         "compile is not evidence here.\n\n"
         "One genuine flake, recorded rather than smoothed over: the first full run reported 1765 passed and one\n"
         "failure in TaskProfileViewTests.TaskAndProfileUserControlsConstruct. Run alone it passed 17 of 17, and the\n"
         "second full run passed 1766 of 1766. It is an Avalonia construction race under full-suite parallelism and\n"
         "unrelated to this change, but that conclusion rests on the rerun, not on assuming.\n\n"
         "Suite 1766 pass / 0 fail after the rerun; four metrics unchanged; Warhammer's coverage unchanged because this\n"
         "round changed the shape of an existing step rather than adding one."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
