"""Record R784: casioid first, sku as fallback -- and why R783's decision reversed."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 210. `casioid` 优先、`sku` 兜底 —— **推翻 R783 的决定，因为它的前提是错的**

> R784。改 `CasioFlow.FindVariantAsync`（+ 文档注释）；新增 `CasioIdentifierTests`（4 条）。

### 一、R783 的推理有一半是错的

R783 我拒绝加 `casioid`，理由是「`sku` 是更明确、更安全的既有概念」。

**那个前提没验。** 这一轮把它验了：

```
[Cc]asio.{0,24}[Ss]ku | [Ss]ku.{0,24}[Cc]asio   -> 0 matches
casio_sku                                        -> 0 matches
^sku                                             -> 30 matches（多为姓氏 Skute/Skupova…；
                                                    ），另有 SkuRegexes / SkuCorrections / get_ListAvailableSku
```

**镜像里 Casio 的配置记录没有任何 sku 概念**，而 `casioid` 与 `casio_can_purchase` /
`casio_image_url` / `casio_gender` / `casio_dob` 同处一条记录。

**所以复刻件原来那个 `"sku"` 正则对 Casio 来说是无据的猜测** —— **两个选项都无据时，
选镜像有据的那一个。**

### 二、改了什么

```csharp
var m = Regex.Match(body, @\"\"\"casioid\"\"\\s*:\\s*\"\"([^\"\"]+)\"\"\");
if (!m.Success) m = Regex.Match(body, @\"\"\"sku\"\"\\s*:\\s*\"\"([^\"\"]+)\"\"\");
if (!m.Success || …) return Fail(\"casio: neither casioid nor sku in the page\");
c.Session.VariantId = m.Groups[1].Value;
```

**顺序是「镜像的字段优先，复刻件原来的猜测兜底」** ——
**只带 sku 的页面行为与改动前完全一致。**

### 三、Observation / Inference 分开

- **Observation**：Casio 记录里有 `casioid`、没有 sku；两个函数读它（R783）
- **Inference（中）**：`casioid` 是购物车行需要的那个标识。
  **站点是否区分「商品 id」与「变体 id」仍未确立** —— 注释里写明了。

### 四、4 条测试

```
CasioidWinsWhenBothArePresent          两者都在 -> 取 casioid
SkuStillWorksWhenCasioidIsAbsent       只有 sku -> 行为与改前一致
NeitherPresentIsNoIdentifier           都没有 -> null（不是空串当成功）
TheFieldNameIsTheImages                字段名被钉住
```

### 五、过程中的两次自伤（都记下来）

1. **差点改错方法**：我用 `t.find('FindVariantAsync')` 在整份 `RetailFlows.cs` 里找，
   **命中 `YeezySupplyFlow` 的同名方法**（它的失败文案是 `"yeezy: no variant id in the page"`）。
   **这是 §2.7 的又一次：在文件里按方法名找，等于假设文件里只有一个同名方法。**
   最后靠 Casio 独有的文案锚点（`"casio: no sku"`）才定位正确。
2. **生成文本时把 `Groups[1].Value` 打成了 `Groups[1].Value`**，在测试文件里写坏了一次。
   **构建报错才发现。** 已修，并用脚本核过只剩合法的 1 处。

**第 2 条值得记**：我这轮的几处代码是手写生成的，**手写会坏字，而坏字编译期就能抓**——
**所以"构建绿"这条检查不能省，哪怕改动只有三行。**

### 六、验证

```
构建                已成功
CasioAvailabilityTests 5 + CasioIdentifierTests 4 = 9 / 9
完整套件            1761 通过 / 0 失败 / 0 跳过（1757 + 4）
四项度量            4 / 0 / 17 / 78 / 0（未变）
Casio 覆盖率        仍 71%（改的是标识来源，不是补步骤）
```

### 七、仍然 Unknown

- 站点是否区分商品 id 与变体 id：**Unknown** —— 这是 `casioid` 语义的最后一问。
- `casio_dob` / `casio_gender` / `casio_image_url` 的用途：**Unknown**。
- Casio 的 shipping / payment：**信息不足**（Adyen 已知、端点未知，R780）。
"""

VERDICT = """

---

## 第 784 轮：`casioid` 优先、`sku` 兜底 —— 推翻上一轮

### R783 的前提没验

我拒绝加 `casioid` 的理由是「`sku` 更明确、更安全」。**这一轮验了那个前提：**

```
casio…sku / sku…casio  -> 0 matches
casio_sku              -> 0 matches
```

**镜像里 Casio 的配置记录没有 sku 概念**，而 `casioid` 与 `casio_can_purchase` 等同处一条记录。

**所以复刻件原来的 `"sku"` 正则对 Casio 是无据的猜测。两个都无据时，选镜像有据的那个。**

### 改了什么

```csharp
var m = Regex.Match(body, @\"\"\"casioid\"\"…\");
if (!m.Success) m = Regex.Match(body, @\"\"\"sku\"\"…\");   // 兜底：只带 sku 的页面行为不变
```

**Observation**：记录里有 `casioid`、没有 sku。
**Inference（中）**：它是购物车行要的标识 —— **站点是否区分商品 id 与变体 id 仍未确立。**

### 4 条测试

两者都在取 `casioid` · 只有 sku 时行为不变 · 都没有时返回 null（不是空串当成功）· 字段名被钉住。

### 两次自伤

1. **差点改错方法** —— `find('FindVariantAsync')` 在整份文件里先命中 **`YeezySupplyFlow`** 的同名方法
   （失败文案是 `"yeezy: no variant id in the page"`）。
   **§2.7 又一次：在文件里按方法名找，等于假设只有一个同名方法。** 靠 Casio 独有文案才定位对。
2. **手写代码打坏了 `Groups[1].Value`**，构建报错才发现。

> **手写会坏字，而坏字编译期就能抓 —— 所以「构建绿」不能省，哪怕只改三行。**

### 验证

```
Casio 相关 9 / 9 · 完整套件 1761 / 0 · 四项度量未变
Casio 覆盖率仍 71%（改的是标识来源，不是补步骤）
```
"""

BACKLOG_ADD = """

## 核心 — Casio 标识（R784 已改）

`FindVariantAsync` 现在：**`casioid` 优先，`sku` 兜底**。

**依据**：Casio 配置记录里有 `casioid`（与 `casio_can_purchase` / `casio_image_url` /
`casio_gender` / `casio_dob` 同处），**且 `casio.{0,24}sku` 与 `casio_sku` 都是 0 匹配** ——
**镜像里 Casio 没有 sku 概念**。

| 项 | 状态 |
|---|---|
| 站点是否区分商品 id / 变体 id | **Unknown**（`casioid` 语义最后一问） |
| `casio_dob` / `casio_gender` / `casio_image_url` 用途 | Unknown |
| Casio shipping / payment | 信息不足（Adyen 已知、端点未知） |

**方法论记录**：在整份 `RetailFlows.cs` 里按方法名找 `FindVariantAsync`，**先命中 `YeezySupplyFlow`** ——
**同名方法在一个文件里有多个，按名字找必须先限定类体。**（§2.7 第八次）
"""


def main():
    for p, marker, text in ((P1, "R784", BLOCKER), (P3, "R784", BLOCKER), (P2, "第 784 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R784" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += Casio 标识")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R784: casioid first, sku as fallback -- reversing R783 because its premise was untested\n\n"
         "R783 declined to add casioid on the reasoning that sku was the safer, established concept. That premise was\n"
         "never checked. Checking it: casio.{0,24}sku matches nothing, casio_sku matches nothing, and the thirty ^sku\n"
         "hits are mostly surnames in a name list plus a general SkuRegexes table that belongs to no store. So the\n"
         "image's Casio record carries casioid and no sku at all, which means the replica's sku regex was itself\n"
         "unbacked. Between two unbacked orderings, take the one the image evidences.\n\n"
         "FindVariantAsync now tries casioid first and falls back to sku, so a page carrying only a sku behaves\n"
         "exactly as before. The comment separates what is observed -- the field exists, the record has no sku -- from\n"
         "what is inferred-medium: that casioid is the identifier a cart line needs. Whether the site distinguishes a\n"
         "product id from a variant id remains open, and saying so matters because that is the one remaining way this\n"
         "could be wrong.\n\n"
         "Four tests pin the ordering, the fallback, the null-on-neither case, and the field name.\n\n"
         "Two mistakes worth recording. I nearly edited the wrong method: searching RetailFlows.cs for find on\n"
         "FindVariantAsync hit YeezySupplyFlow's method first, recognisable by its 'yeezy: no variant id' message.\n"
         "That is section 2.7 again -- a method name inside a file is not unique, so the search has to be scoped to the\n"
         "class. And while writing the test I emitted Groups[1].Value as Groups[1].Value, which the compiler caught\n"
         "immediately. Hand-written text breaks characters; the build is what notices, which is why it is not optional\n"
         "even for a three-line change.\n\n"
         "Suite 1761 pass / 0 fail, up four; four metrics unchanged; Casio stays at 71% because this round changed\n"
         "where an identifier comes from, not how many steps exist."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
