"""Record R786: the region token is not a literal, and the prefix helper that follows from it."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 212. 区域 token **不是字面量**；所以按设置取，不猜

> R786。改 `RetailFlows.cs`（`CasioFlow.RegionVar` + `RegionPath`）；新增 `analysis/casio_record_dump.py`。

### 一、先看两片字符串区，答案是否定的

**第一片**（`0x146fc1d40` 起，512 B）—— 我以为 `casio_*` 是 R761 那种 `Key<value` 打包记录：

```
+0x0006 'case'      +0x0016 'caseFirst'   +0x002a 'casio.com'
+0x003e 'casio_can_purchase'   +0x005e 'casio_dob'   +0x0072 'casio_gender'
+0x008a 'casio_image_url'      +0x00a6 'casioid'     +0x00ba 'casiostore.bhawar.com'
+0x00da 'castle.js' +0x00ee 'cat'
```

**按字母序排列、每个都是独立字符串 —— 这是全局字符串表的切片，不是键值记录。**
**R761 那个「打包 FieldName + 分隔符 + 值」的模型，在这五个字段上不成立。**

**第二片**（`0x146b7d800` 起，8,704 B）—— 找 `Casio` 那族：

```
+0x07ee 'Casio'      +0x07fe 'Casio Login'
+0x0816 'Casio SG'   +0x082a 'Casio US'
```

**它们夹在 `Cash On Delivery` / `Cast` / `Catalan` / `Cebu` / `Central…` 之间** ——
**同样是字母序全局池，这些是 UI 商店列表的显示名。**

**旁边没有 `au` / `sg` / `us`，也没有 `Casio AU`**（`CasioAU` 在 `0x1433…`，那是**类型名区**）。

### 二、结论

> **区域 token 在二进制里不是独立字面量。**

它要么运行时拼（例如把显示名小写），要么来自配置。
**这与 `CasioRegion` 零 xref 完全吻合：它是设置项，按名字读，值由用户设置提供。**

**所以我不猜 token。** 猜出来的 token 会把每一个 Casio 请求都塞到一个没人要求的路径前缀下 ——
**而那种错只会以 404 的形式出现，看起来像"网站变了"。**

### 三、改了什么

```csharp
public const string RegionVar = "CasioRegion";

protected static string RegionPath(FlowContext c, string rest)
{
    if (c.Session.Vars.TryGetValue(RegionVar, out var region) && region.Length > 0)
        return "/" + region.Trim('/') + "/" + rest.TrimStart('/');
    return "/" + rest.TrimStart('/');
}
```

**没有区域时，返回值与改动前逐字相同** —— 第四次用「最坏情况等于没改」这个模式。
**它不解锁任何步骤，但把 `/{region}/` 这件事从注释变成了结构：区域一到位，加购/登录/支付直接可用。**

### 四、过程中的两次自伤

1. **数字少一位**：我把 `0x146B7D800` 写成 `0x146B7CC0`（8 位），
   `VA - imagebase` 得到**负数的 RVA**（`-0x12b948340`），脚本报 "not file-backed"。
   **已给脚本加守卫**：`START < IMAGE_BASE` 直接报「字面量少了一位」。
2. **改坏了 `FindVariantAsync`**：我用方法头部的前几行当锚点做替换，
   **把它们替换掉了**，留下一个悬空的 `if (!m.Success)`。
   构建立刻报错，我按残块把方法补回去了。
   **这正是 AGENTS.md「按整块锚点替换，禁按行号手术」的反面 —— 我用的是「半个块」当锚点。**

**两次都是同一类：我对自己写下的字面量不够谨慎。而两次都是构建或守卫先发现。**

### 五、验证

```
构建                已成功
Casio 相关测试      9 / 9
完整套件            1761 通过 / 0 失败（与改动前同数）
四项度量            4 / 0 / 17 / 78 / 0（未变）
```

### 六、仍然 Unknown

- **区域 token 的取值**：**Unknown** —— 现在有结构承接它，但值本身仍未取证。
- 它是运行时拼的还是配置给的：**Unknown**。
- `casioid` 商品 id / 变体 id：**Unknown**（R783）。
- `Casio Login` 的端点：**Unknown**。
"""

VERDICT = """

---

## 第 786 轮：区域 token 不是字面量

### 两片字符串区，答案都是否定的

**`casio_*` 那片**：`case` → `casio.com` → `casio_can_purchase` → … → `cat`，
**按字母序、各自独立 —— 是全局字符串表的切片，不是键值记录。**
**R761 那个「打包 Key<value」的模型在这五个字段上不成立。**

**`Casio` 那片**：`Casio` / `Casio Login` / `Casio SG` / `Casio US`
**夹在 `Cash On Delivery` / `Cast` / `Catalan` / `Cebu` 之间** —— **UI 商店列表的显示名。**

**旁边没有 `au`/`sg`/`us`**（`CasioAU` 在 `0x1433…`，是**类型名区**）。

> **区域 token 在二进制里不是独立字面量** —— 运行时拼或来自配置。
> **这与 `CasioRegion` 零 xref 吻合：设置项，按名字读。**

### 改了什么

`RegionPath(c, rest)`：有区域就拼 `/{region}/…`，没有就返回原路径。

**没有区域时返回值逐字相同** —— 第四次用「最坏情况等于没改」。
**它不解锁步骤，但把 `/{region}/` 从注释变成了结构。**

### 两次自伤

1. **数字少一位**：`0x146B7D800` 写成 `0x146B7CC0` → **RVA 变成负数**。**已给脚本加守卫。**
2. **改坏了 `FindVariantAsync`** —— 我拿方法头的前几行当锚点，**等于用「半个块」当锚点**，
   留下悬空的 `if`。构建报错后补回。

> **AGENTS.md 说「按整块锚点替换」—— 我这次用的是半个块。**

### 验证

```
构建绿 · Casio 相关 9/9 · 整套 1761 / 0 · 度量未变
```
"""

BACKLOG_ADD = """

## 核心 — Casio 区域（R786 更新）

**结论：区域 token 不是二进制里的独立字面量。**

两片字符串区都查过：
- `casio_*` 那片是**字母序全局表切片**（不是键值记录 —— 修正 R761 的模型）
- `Casio` / `Casio SG` / `Casio US` 是 **UI 显示名**，夹在 `Cash On Delivery` / `Catalan` / `Cebu` 之间
- `CasioAU` 在 `0x1433…`，是**类型名**不是显示串

**所以 `CasioRegion` 零 xref 的意思就是：设置项，值由用户配置给，不是我能从镜像抄的。**

**已做**：`CasioFlow.RegionPath(c, rest)` —— 有区域拼 `/{region}/…`，无区域返回原路径（逐字不变）。

| 项 | 状态 |
|---|---|
| 区域 token 取值 | **Unknown**（结构已就位，值仍缺） |
| 运行时拼 vs 配置给 | Unknown |
| `casioid` 商品/变体 id | Unknown |
| `Casio Login` 端点 | Unknown |

**纪律**：`analysis/casio_record_dump.py` 已加守卫 —— `START < IMAGE_BASE` 直接报「字面量少了一位」，
因为 R786 就犯过这个错（`0x146B7D800` → `0x146B7CC0`，RVA 变负）。
"""


def main():
    for p, marker, text in ((P1, "R786", BLOCKER), (P3, "R786", BLOCKER), (P2, "第 786 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R786" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += Casio 区域")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R786: the region token is not a literal, so the prefix comes from the session and is not invented\n\n"
         "Two string windows settle the question by answering it negatively. The block around casio.com is the\n"
         "alphabetically sorted global pool -- case, caseFirst, casio.com, casio_can_purchase, casio_dob,\n"
         "casio_gender, casio_image_url, casioid, casiostore.bhawar.com, castle.js, cat -- so R761's model of packed\n"
         "key/value records does not hold for these five fields. The block around Casio holds Casio, Casio Login,\n"
         "Casio SG and Casio US, sitting among Cash On Delivery, Cast, Catalan and Cebu: the UI's store list. No au, sg\n"
         "or us token sits beside them, and CasioAU lives in the type-name region rather than among display strings.\n\n"
         "So the region token is not a literal in the binary. It is assembled at run time or supplied by\n"
         "configuration, which is exactly what a zero-cross-reference setting implies. I am not guessing one: a\n"
         "guessed token would push every Casio request under a prefix nobody asked for, and the only symptom would be\n"
         "404s that look like the site changed.\n\n"
         "CasioFlow gains RegionVar and RegionPath. With no region in the session the helper returns byte-for-byte\n"
         "what the old code returned, which is the fourth use of the pattern where the worst case equals the previous\n"
         "behaviour. It does not unlock a step, but it turns the /{region}/ note into structure: once a region arrives,\n"
         "cart, login and payment paths are ready.\n\n"
         "Two self-inflicted errors this round, both about trusting my own literals. I typed 0x146B7D800 as 0x146B7CC0,\n"
         "which made the RVA negative and produced 'not file-backed'; the dump script now refuses any START below the\n"
         "image base and names the likely cause. And I replaced FindVariantAsync's header by using its first lines as\n"
         "an anchor, which is the opposite of the whole-block rule this repository states -- 'half a block' is still a\n"
         "partial match. The build caught it and the method is restored.\n\n"
         "Suite 1761 pass / 0 fail, unchanged in count; four metrics unchanged."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
