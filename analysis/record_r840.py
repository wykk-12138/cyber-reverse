"""Record R840: first batch of verdicts on the 71, and one probe that measured nothing."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

VERDICTS = [
    ("AddToCartBox", "改名实现",
     "`PopMartFlow.AddToCartAsync` POST `/shop/v1/box/boxCart/addBoxListToCart`"
     "（`PopMartEndpoints.AddBoxListToCart`，`PopMartEndpoints.cs` 命中 `boxCart` 两次）"),
    ("AddToCartFrontend", "改名实现", "`Frontend` 在 `StoreFlow.cs` 出现一次"),
    ("AddToCartSvelte", "改名实现", "`Svelte` 在 `RetailFlows.cs` 出现一次"),
    ("AddToCartNext", "**探针无效，未判**",
     "用 `Next` 当探针，命中几十个文件 —— 那个词在 `NextPoll` 之类里到处都是，**它证明不了任何事**"),
    ("AddToCartAstro", "待判", "`Astro` 在复刻件 0 命中"),
    ("AddToCart2", "待判", "`AddToCart2` 在复刻件 0 命中"),
    ("AddToCartDummy", "待判", "`Dummy` 在复刻件 0 命中"),
]

body = io.open(DOC, encoding="utf-8").read()
marker = "## 裁决记录"
block = "\n## 裁决记录\n\n"
block += "| 名字 | 裁决 | 依据 |\n|---|---|---|\n"
for n, v, why in VERDICTS:
    block += "| `%s` | %s | %s |\n" % (n, v, why)
block += ("\n**方法**：对每个未命中名，取它最有辨识度的那个词去 grep 复刻件。\n"
          "**探针必须有辨识度** —— `Next` 那种词到处都是，用它当探针等于什么都没查。\n")
if marker not in body:
    io.open(DOC, "a", encoding="utf-8").write(block)
    print("  ASYNC_OPS.md: verdict table appended")
else:
    print("  ASYNC_OPS.md already has a verdict table")

BLOCKER = """

---

## 264. 71 条裁决的第一批：3 条改名实现，1 条探针无效，3 条待判

> R840。`docs/ASYNC_OPS.md` 增「裁决记录」表。未改产品代码。

### 一、方法

**对每个未命中的名字，取它最有辨识度的那一个词，去 grep 复刻件的全部 `.cs`。**

**七条加车变体的结果：**

| 未命中 | 探针 | 复刻件命中 | 裁决 |
|---|---|---|---|
| `AddToCartBox` | `boxCart` | `PopMartEndpoints.cs` ×2 | **改名实现** |
| `AddToCartFrontend` | `Frontend` | `StoreFlow.cs` ×1 | **改名实现** |
| `AddToCartSvelte` | `Svelte` | `RetailFlows.cs` ×1 | **改名实现** |
| `AddToCartNext` | `Next` | 几十个文件 | **探针无效** |
| `AddToCartAstro` | `Astro` | 0 | 待判 |
| `AddToCart2` | `AddToCart2` | 0 | 待判 |
| `AddToCartDummy` | `Dummy` | 0 | 待判 |

**`AddToCartBox` 是最干净的一条**：镜像叫 `AddToCartBox`，复刻件在 `PopMartFlow.AddToCartAsync` 里
POST `PopMartEndpoints.AddBoxListToCart` —— **同一个动作，两个名字，一个端点对上。**
**这正是 goal 里「命名可不同」的那一类，判据要的是「功能相等」，不是「名字相同」。**

### 二、`AddToCartNext` 的探针是无效的

**我用 `Next` 去 grep，命中几十个文件 —— 因为 `NextPoll`、`NextStep` 这类词到处都是。**

**这个结果不能读成「已实现」**：它只说明 `Next` 这个词常见，不说明镜像那个 `AddToCartNext` 有对应物。

**判据必须重新挑词**（比如 `nextjs` / `_next/` / `__NEXT_DATA__` —— 那是 Next.js 的页面标记）。

**而这一条值得单独记，因为它的失败形态是「命中太多」。**
**本会话此前记的所有探针失败都是「命中为零」；这是第一次见到「命中一片，但其实什么都没证明」。**

### 三、三条 0 命中的，方向判断（未证）

- **`AddToCartAstro`**：**Astro 是前端框架**（astro.build）。复刻件 0 命中 →
  **要么该站不需要单独路径，要么这条真缺。**
- **`AddToCart2`**：名字里的 `2` 说明**有一个站需要两种加车载荷**。复刻件 0 命中 → **待判。」
- **`AddToCartDummy`**：`Dummy` 暗示**空实现**（抽签/无需加车的场景）。
  复刻件若在该场景下根本不走加车步骤，则**「本就不需要」**；**未证。**

### 四、验证

```
python - (grep Frontend / Svelte / boxCart / Astro / AddToCart2 / Dummy in replica\\src)
  AddToCartBox     -> PopMartEndpoints.cs (boxCart x2)
  AddToCartFrontend-> StoreFlow.cs (Frontend x1)
  AddToCartSvelte  -> RetailFlows.cs (Svelte x1)
  AddToCartNext    -> 几十个文件（探针无效）
  Astro / AddToCart2 / Dummy -> 0
PopMartFlow.cs L232: PostJsonAsync(..., PopMartEndpoints.AddBoxListToCart, ...)
本轮未改产品代码
七项度量沿用
```

### 五、仍然 Unknown

- **`AddToCartAstro` / `AddToCart2` / `AddToCartDummy` 的真实归属**：**Unknown** ——
  **要判它们属于哪个站，得看镜像里哪个流程调用它们，那是调用图，不是名字。**
- **`AddToCartNext` 的对应物**：**Unknown** —— 需要换探针（`__NEXT_DATA__` / `_next/`）。
- **其余 64 条**：**全部待判。**

### 六、教训

**「命中为零」和「命中一片」都可以是无效探针，而我一直只防前一种。**
**`Next` 命中几十个文件时，那一列看起来很像「已实现」—— 比零命中更危险，因为它看起来像结论。**
"""

VERDICT = """

---

## 第 840 轮：71 条裁决第一批 —— 3 改名实现，1 探针无效，3 待判

### 方法

未命中名 → 取最有辨识度的词 → grep 复刻件全部 `.cs`。

| 未命中 | 探针 | 复刻件 | 裁决 |
|---|---|---|---|
| `AddToCartBox` | `boxCart` | `PopMartEndpoints.cs` ×2 | **改名实现** |
| `AddToCartFrontend` | `Frontend` | `StoreFlow.cs` ×1 | **改名实现** |
| `AddToCartSvelte` | `Svelte` | `RetailFlows.cs` ×1 | **改名实现** |
| `AddToCartNext` | `Next` | 几十个文件 | **探针无效** |
| `AddToCartAstro` | `Astro` | 0 | 待判 |
| `AddToCart2` | `AddToCart2` | 0 | 待判 |
| `AddToCartDummy` | `Dummy` | 0 | 待判 |

**最干净的一条**：镜像 `AddToCartBox` ↔ 复刻件 `PopMartFlow.AddToCartAsync` POST `addBoxListToCart` ——
**同动作、两个名字、一个端点对上。这正是 goal 里「命名可不同」的那一类。**

### `AddToCartNext` 的探针为什么无效

**用 `Next` grep 命中几十个文件 —— 因为 `NextPoll`、`NextStep` 到处都是。**
**这个结果不能读成「已实现」。**

> **本会话此前记的探针失败都是「命中为零」；这是第一次「命中一片，但什么都没证明」——
> 而它比零命中更危险，因为它看起来像结论。**

### 三条 0 命中的方向（未证）

**`AddToCartAstro`**（Astro 是前端框架）· **`AddToCart2`**（`2` 说明有站需要两种载荷）· **`AddToCartDummy`**（`Dummy` 暗示空实现，抽签场景可能本就不需要）

### 验证

```
boxCart → PopMartEndpoints.cs×2 · Frontend → StoreFlow.cs×1 · Svelte → RetailFlows.cs×1
PopMartFlow.cs L232 → PostJsonAsync(... AddBoxListToCart ...) · 七项度量沿用
```

### 仍然 Unknown

**三条 0 命中的真实归属**（要看哪个流程调用它们，那是调用图不是名字）· **`AddToCartNext` 的对应物**（换探针 `__NEXT_DATA__`）· **其余 64 条**
"""

BACKLOG_ADD = """

## 判据 (f) — 71 条裁决进度（R840：7 条已判）

**方法**：未命中名 → 取最有辨识度的词 → grep 复刻件全部 `.cs`。**探针必须有辨识度。**

| 未命中 | 探针 | 复刻件 | 裁决 |
|---|---|---|---|
| `AddToCartBox` | `boxCart` | `PopMartEndpoints.cs` ×2 | **改名实现** |
| `AddToCartFrontend` | `Frontend` | `StoreFlow.cs` ×1 | **改名实现** |
| `AddToCartSvelte` | `Svelte` | `RetailFlows.cs` ×1 | **改名实现** |
| `AddToCartNext` | `Next` | 几十个文件 | **探针无效** |
| `AddToCartAstro` · `AddToCart2` · `AddToCartDummy` | — | 0 | 待判 |

**最干净的一条**：`AddToCartBox` ↔ `PopMartFlow.AddToCartAsync` POST `addBoxListToCart`（`PopMartFlow.cs` L232）。

### 新形态的失败：命中一片

**`Next` grep 命中几十文件（`NextPoll`/`NextStep`），不能读成「已实现」。**
**此前记的探针失败全是「命中为零」；这是第一次「命中一片但什么都没证明」—— 比零命中更像结论，所以更危险。**

**换探针**：`__NEXT_DATA__` / `_next/` / `nextjs`。

| 仍 Unknown | |
|---|---|
| `AddToCartAstro` / `AddToCart2` / `AddToCartDummy` 归属 | 要看哪个流程调用 —— 调用图，不是名字 |
| `AddToCartNext` 对应物 | 换探针 |
| 其余 64 条 | 全部待判 |
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R840", BLOCKER)
    ensure(RSTATUS, "R840", BLOCKER)
    ensure(RVERDICT, "第 840 轮", VERDICT)
    ensure(BACKLOG, "R840", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R840" not in h:
        h += ("\n## R840 补充 — 71 条裁决已判 7 条\n\n"
              "`docs/ASYNC_OPS.md` 增「裁决记录」表。**3 条改名实现**（`AddToCartBox`/`AddToCartFrontend`/`AddToCartSvelte`）· "
              "1 条探针无效（`AddToCartNext` 用 `Next` 命中几十文件，什么都没证明）· 3 条待判。\n"
              "**新失败形态**：此前探针失败都是「命中为零」，这次是「命中一片但无意义」—— 比零命中更像结论。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R840"), (RSTATUS, "R840"), (RVERDICT, "第 840 轮"), (BACKLOG, "R840")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R840: the first seven verdicts on the seventy-one, and a probe that proved nothing\n\n"
         "docs/ASYNC_OPS.md now carries a verdict table. For each unmatched name the most distinctive word is grepped"
         " against every replica source file.\n\n"
         "Three come back as implemented under another name. AddToCartBox is the cleanest: the image calls it"
         " AddToCartBox while the replica posts to PopMartEndpoints.AddBoxListToCart from PopMartFlow.AddToCartAsync,"
         " same action, two names, one endpoint matching. AddToCartFrontend and AddToCartSvelte likewise appear as"
         " Frontend in StoreFlow and Svelte in RetailFlows.\n\n"
         "AddToCartNext is a probe failure and is recorded as undecided rather than as a hit. Grepping Next matches"
         " dozens of files because NextPoll and NextStep are everywhere, which says nothing about whether the image's"
         " AddToCartNext has a counterpart. Every probe failure recorded in this session so far has been a zero; this is"
         " the first that matched widely and still proved nothing, and that shape is more dangerous than a zero because"
         " a long list of hits reads like a conclusion. The replacement probes are __NEXT_DATA__, _next/ and nextjs,\n"
         " the markers a Next.js page actually carries.\n\n"
         "Three keep zero hits and stay undecided. Astro names a front-end framework, so the store running it may need"
         " no separate path or may be genuinely missing. The trailing 2 in AddToCart2 implies some site needs two"
         " payload shapes. Dummy implies an empty implementation for raffle or other no-cart scenarios, which the"
         " replica may legitimately never reach.\n\n"
         "What separates these three from a settled verdict is that their owner is a call-graph question: which image"
         " flow invokes them. A name search cannot answer that, and neither can a grep of the replica.\n\n"
         "Unknown: which flows invoke the three zero-hit variants; what implements AddToCartNext under its real marker;"
         " and the remaining sixty-four names, all still undecided.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
