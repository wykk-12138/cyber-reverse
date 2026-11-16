"""Record R906: async method coverage is 20%, which is the direct function-parity measure."""

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
### 异步方法覆盖 **20.0%** —— 这才是函数对等的直尺度（R906）

**R905 发现 `RunShield` 存在。于是把它放大：镜像的 1,547 个异步方法名，复刻件里有没有。**

### 结果

| | |
|---|---|
| 镜像异步方法名 | **1,547** |
| 复刻件有 | **310（20.0%）** |
| 复刻件无 | **1,237** |

**新工具 `tools/async_method_coverage.py`，整词匹配、扫全 `src`。**

### 而 20% 与端点侧那个 100% 差得远

| 度量 | 值 | 量的是什么 |
|---|---|---|
| 端点覆盖（无宿主桶） | **100%** | URL 有没有被写下来 |
| **异步方法覆盖** | **20.0%** | **步骤有没有存在** |

**这两个不矛盾：一个 URL 写下常量算「有」，而**用它的方法**可能不存在。
R903 那 67 条 hostless 路径现在都有常量，而调用它们的方法多数还没有。**

**所以前几轮补常量是对的，但它补的是「路名」，不是「路」。**

### 而这是**上界**，不是缺口本身

**goal 允许改名。所以「名字不在」可能是：**
1. 功能真的没有
2. 功能在，但叫另一个名字

**这一条判别不了。要分辨得读每个缺失名字的语义 —— 那是 1,237 次判断。**

**所以这个数的正确读法是：**最多缺 1,237 个步骤**。**

### 而清单第一段就有一族很说明问题

```
AddToCart2 · AddToCartAstro · AddToCartBox · AddToCartDummy
AddToCartFrontend · AddToCartNext · AddToCartSvelte
```

**7 个 `AddToCart` 变体，按平台/框型/前端框架分。复刻件只有一个 `AddToCart`。**

**这是「一家店一个加车实现」的直接证据 —— 而不是一个可以参数化的通用步骤。**

### 前 80 个里的其他族

**`AcceptCallbacksAsync` · `AcceptLoopAsync`（服务端）· `AcquireAsync` · `AcquireLockAsync` · `AcquireUpdateLock`（并发）·
`AddAddress` · `AddPaymentMethod` · `AddPaymentToCart`（结账）· `AddImageAsync` · `AddHintImageAsync`（captcha 图）·
`Animate` · `AnimateViewportOffsetAsync`（UI）**

**所以 1,237 个缺失方法横跨服务端、并发、结账、captcha、UI —— 这就解释了为什么 20%。**
"""

if "异步方法覆盖 **20.0%**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R906 appended")

VERDICT = """

---

## 第 906 轮：异步方法覆盖 20.0% —— 这才是函数对等的直尺度

### 结果

| | |
|---|---|
| 镜像异步方法名 | **1,547** |
| 复刻件有 | **310（20.0%）** |
| 复刻件无 | **1,237** |

**新工具 `tools/async_method_coverage.py`：整词匹配，扫全 `src`。**

### 20% 与端点侧那个 100% 不矛盾

| 度量 | 值 | 量的是什么 |
|---|---|---|
| 端点覆盖（无宿主桶） | **100%** | **URL 有没有被写下来** |
| **异步方法覆盖** | **20.0%** | **步骤有没有存在** |

> **一个 URL 写下常量算「有」，而**用它的方法**可能不存在。
> R903 那 67 条 hostless 路径现在都有常量，而调用它们的方法多数还没有。**
> **所以前几轮补常量是对的 —— 但它补的是「路名」，不是「路」。**

### 而这是**上界**，不是缺口本身

**goal 允许改名。所以「名字不在」可能是功能真没有，也可能是功能在但叫别的名字。
这一条判别不了，要分辨得读 1,237 个名字的语义。**

> **所以这个数的正确读法是：**最多缺 1,237 个步骤**。**

### 清单第一段就有一族很说明问题

```
AddToCart2 · AddToCartAstro · AddToCartBox · AddToCartDummy
AddToCartFrontend · AddToCartNext · AddToCartSvelte
```

**7 个 `AddToCart` 变体，按平台/框型/前端框架分。复刻件只有一个 `AddToCart`。**

> **这是「一家店一个加车实现」的直接证据 —— 而不是一个可以参数化的通用步骤。**

### 前 80 个里横跨

**服务端（`AcceptLoopAsync`）· 并发（`AcquireLockAsync`）· 结账（`AddPaymentMethod`）·
captcha（`AddImageAsync` / `AddHintImageAsync`）· UI（`Animate`）**

### 教训

> **端点覆盖 100% 这个数让我觉得补得不错。而同一个镜像里，步骤层面只有 20%。**
> **两个数都真，而我只在报前一个。**
> **「有没有写下来」和「有没有实现」之间隔着一整层，而那一层才是 goal 的 (a)(e) 问的。**
"""

BACKLOG_ADD = """

## 判据 — 异步方法覆盖 **20.0%**（R906，**新工具 `tools/async_method_coverage.py`**）

### 结果

| | |
|---|---|
| 镜像异步方法名 | **1,547** |
| 复刻件有 | **310（20.0%）** |
| 复刻件无 | **1,237** |

### 与端点覆盖的关系

| 度量 | 值 | 量什么 |
|---|---|---|
| 端点（无宿主桶） | 100% | **URL 有没有被写下来** |
| **异步方法** | **20.0%** | **步骤有没有存在** |

**→ 补常量补的是「路名」，不是「路」。调用那 67 条路径的方法多数还没有。**

### 这是上界

**goal 允许改名 → 「名字不在」可能是功能真没有，也可能是叫别的名字。要分辨得读 1,237 个名字。**

### 一族证据

**`AddToCart` 有 7 个变体**：`2` · `Astro` · `Box` · `Dummy` · `Frontend` · `Next` · `Svelte` —— **复刻件只有一个。**
**→ 「一家店一个加车实现」，不是可参数化的通用步骤。**

| 仍 Unknown | |
|---|---|
| 1,237 里多少是真缺 | 需读每个名字语义 |
| 复刻件的 310 个是否行为相等 | 名字在 ≠ 实现对 |
| 7 个 AddToCart 变体各差什么 | 需逐个查 |

**纪律**：**「有没有写下来」与「有没有实现」隔着一整层 —— 那一层才是 goal 问的。**
"""

BLOCKER = """

---

## 330. 异步方法覆盖 **20.0%**：1,547 名里复刻件有 310

> R906。**新增工具，未改产品代码。**

### 一、结果

| | |
|---|---|
| 镜像异步方法名 | **1,547** |
| 复刻件有 | **310（20.0%）** |
| 复刻件无 | **1,237** |

**`tools/async_method_coverage.py`：整词匹配，扫全 `src`。**

### 二、与端点覆盖不矛盾

| 度量 | 值 | 量什么 |
|---|---|---|
| 端点（无宿主桶） | **100%** | URL 有没有被写下 |
| **异步方法** | **20.0%** | **步骤有没有存在** |

**一个 URL 写下常量算「有」，而用它的方法可能不存在。
R903 那 67 条路径都有常量了，而调用它们的方法多数还没有。**

**所以前几轮补常量是对的，但它补的是「路名」，不是「路」。**

### 三、这是上界

**goal 允许改名 → 「名字不在」可能是功能真没有，也可能叫别的名字。要分辨得读 1,237 个名字。**

### 四、一族直接证据

```
AddToCart2 · AddToCartAstro · AddToCartBox · AddToCartDummy
AddToCartFrontend · AddToCartNext · AddToCartSvelte
```

**7 个变体，按平台/框型/前端框架分；复刻件只有一个 `AddToCart`。**

**这是「一家店一个加车实现」的证据，而不是一个可参数化的通用步骤。**

### 五、前 80 个横跨的域

**服务端 `AcceptLoopAsync` · 并发 `AcquireLockAsync` / `AcquireUpdateLock` ·
结账 `AddPaymentMethod` / `AddPaymentToCart` · captcha `AddImageAsync` / `AddHintImageAsync` · UI `Animate`**

### 六、仍然 Unknown

- **1,237 里多少是真缺**：**Unknown** —— 需读每个名字的语义，那是 1,237 次判断。
- **复刻件那 310 个是否行为相等**：**Unknown** —— **名字在 ≠ 实现对。**
- **7 个 `AddToCart` 变体各差什么**：**Unknown** —— 需逐个查。

### 七、教训

**端点覆盖 100% 让我觉得补得不错。而同一个镜像里，步骤层面只有 20%。**

**两个数都真，而我只报了前一个。**

**「有没有写下来」与「有没有实现」之间隔着一整层，而那一层才是 goal 的 (a) 与 (e) 问的。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R906", BLOCKER)
    ensure(RSTATUS, "R906", BLOCKER)
    ensure(RVERDICT, "第 906 轮", VERDICT)
    ensure(BACKLOG, "R906", BACKLOG_ADD)

    note = (
        "\n## R906 补充 — 异步方法覆盖 20.0%（新工具 tools/async_method_coverage.py）\n\n"
        "1547 个镜像异步方法名，复刻件有 310（20.0%），缺 1237。\n\n"
        "与端点覆盖不矛盾：端点 100% 量的是 URL 有没有被写下来，异步方法 20% 量的是步骤有没有存在。"
        "补常量补的是路名，不是路。\n\n"
        "这是上界（goal 允许改名）。要分辨得读 1237 个名字的语义。\n\n"
        "一族直接证据：AddToCart 有 7 个变体（2/Astro/Box/Dummy/Frontend/Next/Svelte），复刻件只有一个。\n\n"
        "下一轮：1,237 里挑可判的子集（如 AddToCart 7 变体）逐个查。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R906" not in h:
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
             for p, k in ((RBLOCK, "R906"), (RSTATUS, "R906"), (RVERDICT, "第 906 轮"), (BACKLOG, "R906")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R906: async method coverage is twenty percent, which is the measure that function parity is actually about\n\n"
         "R905 found RunShield in the image's async-method table with no counterpart, and this round generalises it: of\n"
         " the 1547 async method names the image carries, 310 appear in the replica, twenty percent, and 1237 do not.\n\n"
         "That sits beside the endpoint figure without contradicting it. Endpoint coverage asks whether a URL is named\n"
         " somewhere, and the hostless bucket reached a hundred percent last round. Method coverage asks whether a step\n"
         " exists to use it. A URL can be recorded as a constant with no method behind it, which is exactly the state of\n"
         " the sixty-seven paths added in R902 and R903.\n\n"
         "So the constant work was right and it filled in road names rather than roads. The distinction matters because\n"
         " criterion (a) in the goal is about function parity, and a naming table cannot answer that.\n\n"
         "The figure is an upper bound on the gap, not the gap. The goal permits renaming, so an absent name may mean a\n"
         " missing feature or a present feature under another name, and nothing here distinguishes them; telling them\n"
         " apart means reading 1237 names.\n\n"
         "One family in the first eighty makes the shape concrete: there are seven AddToCart variants -- AddToCart2,\n"
         " Astro, Box, Dummy, Frontend, Next and Svelte -- split by platform, box type and frontend framework, while the\n"
         " replica has a single AddToCart. That is evidence of one cart implementation per store rather than one\n"
         " parameterised step.\n\n"
         "Unknown: how many of the 1237 are genuinely missing, which needs a semantic read of each; whether the 310\n"
         " present are behaviourally equal, since presence is not correctness; and what each of the seven AddToCart\n"
         " variants actually differs in.\n\n"
         "The lesson is about which figure I chose to report. Endpoint coverage at a hundred percent felt like progress\n"
         " and is true, while the same image measures twenty percent one layer down. Both numbers were available and I\n"
         " had been quoting the first.\n\n"
         "New tool; no product code changed; suite carries at 1805."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
