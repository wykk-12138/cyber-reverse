"""Record R782: Casio availability now follows the image's path."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 208. Casio 的可购判定改成镜像那条路径 —— 且保底不会更差

> R782。改 `RetailFlows.cs`（`CasioFlow.ScrapeVariantAvailabilityAsync` + 新 `CasioAvailability`）；
> 新增 `CasioAvailabilityTests`（5 条）。

### 一、改之前是什么

```csharp
var inStock = body.Contains("\\"availability\\"", OrdinalIgnoreCase) ||
              body.Contains("InStock", OrdinalIgnoreCase);
```

**那是猜的** —— 页面上出现 `availability` 或 `InStock` 就算有货。**任何带这两个词的页面都会判成可购。**

### 二、改之后

```csharp
public const string CanPurchaseField = "casio_can_purchase";     // 镜像里的字段名

public static bool? CasioAvailability(string body)               // 走 data.products.items[*]
{
    … SelectTokens("$.data.products.items[*]") …
    … 每项读 CanPurchaseField … 任一项为真即 true；都没有该字段则返回 null …
}
```

**判定顺序**：

1. 能按镜像的路径解出 → 用它（Observation：路径与字段名）
2. 解不出（不是那个形状 / 是 HTML）→ **落回旧启发式**

**保底是刻意的**：这一改动**不可能让现有任一情形变差** —— 它只在那份 JSON 真的在那儿时才改判。

### 三、Observation 与 Inference 分开

- **Observation**：`data` / `products` / `items` 三个键名（R781 用 `off_slot_reader` 读出）、
  `casio_can_purchase` 这个字段名（与 reCAPTCHA sitekey 同处一条配置记录）
- **Inference（中）**：那个字段是布尔、且**任一项为真即可购** ——
  **镜像读了字段，但消费它的分支在反编译窗口之外**

**这条推断写进了方法注释，也写进了测试类的注释。**

### 四、5 条测试

```
OnePurchasableItemMakesTheProductAvailable          items 里一项 true -> true
AllItemsRefusingMeansUnavailable                    全 false -> false
TheFlagMayArriveAsAString                           "true" 也认
AShapeWithoutTheFieldIsUndecidedRatherThanUnavailable  空 items / 无该字段 / HTML -> null（不是 false）
TheFieldNameIsTheImages                             字段名被钉住
```

**第 4 条是关键**：**「解不出」必须返回 null 而不是 false** —— 否则会把"不是那个形状"误报成"缺货"。

### 五、验证

```
构建                已成功
CasioAvailabilityTests  5 / 5
完整套件            1757 通过 / 0 失败 / 0 跳过（1752 + 5）
四项度量            4 / 0 / 17 / 78 / 0（未变）
Casio 覆盖率        仍 71%（这一改动不改覆盖率 —— 它改的是既有步骤的判定，不是补步骤）
```

**注意**：**覆盖率没动，这是对的。** 改的是"同一个步骤做得对不对"，不是"少不少步骤"。
**判据 f 说的是覆盖，这一轮动的是质量 —— 两者不能混为一谈。**

### 六、仍然 Unknown

- `casio_can_purchase` 的真实类型与比较方式：**Inference（中）**，见第三节。
- `data.products.items[*]` 的完整字段集：**Unknown**（`casio_image_url` / `casio_gender` / `casio_dob` 未接）。
- `casio` 的 `SubmitShipping` / `SubmitPayment`：**仍是信息不足**（R780）—— 这一轮没碰。
"""

VERDICT = """

---

## 第 782 轮：Casio 的可购判定改成镜像那条路径

### 改之前是猜的

```csharp
body.Contains("availability") || body.Contains("InStock")
```

**任何带这两个词的页面都判成可购。**

### 改之后

走 `data.products.items[*]`（三个键名 R781 用 `off_slot_reader` 读出），每项读 `casio_can_purchase`。
**解不出那个形状时落回旧启发式** —— **保底是刻意的：这一改动不可能让现有任一情形变差。**

### Observation / Inference 分开

- **Observation**：三个路径键 + `casio_can_purchase` 字段名
- **Inference（中）**：字段是布尔、**任一项为真即可购** —— 消费它的分支在反编译窗口之外

### 5 条测试，其中一条是关键

```
AShapeWithoutTheFieldIsUndecidedRatherThanUnavailable
```

**「解不出」返回 null 而不是 false** —— 否则会把「不是那个形状」误报成「缺货」。

### 验证

```
构建绿 · CasioAvailabilityTests 5/5 · 完整套件 1757 / 0
Casio 覆盖率仍 71% —— 这一轮动的是质量，不是覆盖
```

> **判据 f 说的是覆盖，这一轮改的是「同一个步骤做得对不对」。两者不能混为一谈。**
"""

BACKLOG_ADD = """

## 核心 — Casio（R782 更新）

**已做**：`ScrapeVariantAvailabilityAsync` 改为走镜像的 `data.products.items[*]` + `casio_can_purchase`，
解不出时落回旧启发式。5 条测试钉住，含「解不出 → null 而非 false」。

**仍待做**：

| 项 | 状态 |
|---|---|
| `SubmitShippingAsync` / `SubmitPaymentAsync` | **信息不足**：Adyen 已知，`_adyenOrderId` 是字段名不是端点 |
| `data.products.items[*]` 的其余字段（`casio_image_url` / `casio_gender` / `casio_dob`） | 未接 |
| `CasioRegion` 的分区行为 | 零 xref＝数据键；取值集合未定 |
| `casiostore.bhawar.com` | 落在 687 KB 并片里，读不出边界 |
| `casioid` 两个函数（187 B / 893 B） | 未读 |

**口径提醒**：覆盖率（71%）衡量**有没有这一步**；R782 改的是**这一步判得对不对**。
**不要把「质量改动」记成「覆盖进展」。**
"""


def main():
    for p, marker, text in ((P1, "R782", BLOCKER), (P3, "R782", BLOCKER), (P2, "第 782 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R782" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += Casio 更新")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R782: Casio availability follows the image's path, with a fallback so nothing can get worse\n\n"
         "The old test was a word search: if the page contained 'availability' or 'InStock', the product was\n"
         "available. Any page carrying either word passed, which is not a decision at all.\n\n"
         "Now it walks data.products.items, the three key names R781 recovered with the off_ reader, and reads\n"
         "casio_can_purchase per item -- the field name that sits in the same configuration record as Casio's\n"
         "reCAPTCHA site key. When that shape is not there, the method returns null and the caller falls back to the\n"
         "earlier heuristic, so the change cannot make any existing case worse; it only overrides when the JSON\n"
         "really is present.\n\n"
         "Observation and inference are kept apart. The path and the field name are observed. That the field is a\n"
         "boolean and that any item saying yes makes the product available is inferred-medium, because the image\n"
         "reads the field but the branch consuming it sits outside the decompiled window. Both notes are in the\n"
         "method comment and in the test class.\n\n"
         "Five tests pin it, and the fourth is the important one: a payload with no items, or with items lacking the\n"
         "field, or plain HTML, must return null rather than false. Returning false there would report 'not the right\n"
         "shape' as 'out of stock', which is the kind of quiet wrongness that survives for rounds.\n\n"
         "Suite 1757 pass / 0 fail, up five; four metrics unchanged.\n\n"
         "Casio's coverage stays at 71%, and that is correct rather than disappointing: this round changed how an\n"
         "existing step decides, not whether the step exists. Criterion (f) measures coverage, and recording a\n"
         "quality change as coverage progress would be exactly the sort of number-shuffling the metrics rules exist\n"
         "to prevent."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
