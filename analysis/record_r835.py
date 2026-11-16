"""Record R835: the PopMart draw surface has no flow covering it, and the decompilation says it is real."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

BLOCKER = """

---

## 259. PopMart 抽签面：**没有任何流程覆盖它**，而反编译确认它真的发请求

> R835。未改产品代码。

### 一、三块地名都定住了

用 R829 的路线（`str` → `xrefs` 到 `−12` → `dec`）：

| 端点 | 所在函数 | 大小 |
|---|---|---|
| `activity/v1/activity/sample_info` | `sub_140B8B340` | 0x188 |
| `activity/v1/exhibit_draw/draw` | `sub_140BC1340` | 0x2bc |

**`sub_140B8B340` 是 URL 构造**：建一个容量 76 的 `StringBuilder`，
再 `sub_141D2B8E0(..., &unk_14707BABC, 144)` —— **从 `0x14707babc` 追加 144 字节（72 字符）**，
那正是 `sample_info` 串本身，**然后接着追加参数**。

**`sub_140BC1340` 是 `async` 状态机**：`if (!*(_DWORD *)(a1 + 8))` 按状态分支、
`sub_141D0E0A0(a1)`（`AsyncTaskMethodBuilder.Start`）。

**所以这两个不是残留字符串，是真发请求的代码。**

### 二、没有任何流程覆盖它

| 流程 | 覆盖什么 |
|---|---|
| `PopMartFlow` | `/shop/v1/...`（13 个端点，全部有镜像对应，R830） |
| `RaffleFlow` | `r419.com` · `lndg.page` · `nodnod.digital` —— **Shopify 抽签 App 的域名** |

**`RaffleFlow` 不碰 PopMart。所以 `prod-hk-actapi…/activity/v1/exhibit_draw/draw` 这条路径
在复刻件里没有任何流程存在。**

### 三、它是不是一个独立任务类型

**查了三个候选，都没有：**

```
DrawTask   0
drawTask   0
LotteryTask 0
```

**镜像里唯一的 PopMart 类型标记是 `$PopMartProductType`（单个）。**

**所以抽签不是独立任务型，是 PopMart 模块内部的一条可选路径。**
**这与 `PopMartFlow` 注释里写的「Pop Mart sells sealed boxes」一致 —— 一家店，两种买法：**
**直接买盒（`/shop/v1/box/...`，复刻件有）与抽签（`activity/v1/exhibit_draw`，复刻件没有）。**

### 四、验证

```
ida.py str activity/v1/activity/sample_info      -> 1 match @0x14707babc
ida.py xrefs 0x14707bab0                          -> sub_140B8B340 (0x188 bytes)
ida.py dec 0x140b8b340                            -> 2079 chars, 容量 76 的 StringBuilder + 追加 144 字节
ida.py str activity/v1/exhibit_draw/draw          -> 1 match @0x14707bb64
ida.py xrefs 0x14707bb58                          -> sub_140BC1340 (0x2bc bytes)
ida.py dec 0x140bc1340                            -> 3435 chars, async 状态机
复刻件 RaffleFlow 域名: r419.com / lndg.page / nodnod.digital
ida.py str DrawTask / drawTask / LotteryTask      -> 全 0
本轮未改产品代码
七项度量沿用（含函数数量 277,120 / 171,690 / 61.96%）
```

### 五、仍然 Unknown

- **抽签路径在 PopMart 任务里怎么被触发**：**Unknown** ——
  **`$PopMartProductType` 是唯一的类型标记，它有没有「抽签」这个取值，得看枚举内容。**
- **`/web/v2?partner=popmart&appKey=` 的所在函数**：**Unknown** ——
  **`−12` 处的 xrefs 是 0，可能这条串是拼出来的（前缀 + 参数），而不是整串引用。**
- **`popDraw.json` 的所在函数**：**Unknown** —— 同样 0 xref。**这条看起来是「抽签数据源」，
  可能被 `PopmartBrowser` 的页面脚本读，而不是 C# 代码。**
- **抽签要不要做**：**Unknown** —— 取决于 Cybersole 的 PopMart 任务是否包含抽签模式。
  **而这条要么看枚举值，要么看 UI（优先级 ④）。**

### 六、教训

**R830 我说「四块未建模」，这一轮把其中一块从「未建模」推进到「确认无流程覆盖、且是真代码」。**
**两者的差别是：前者可能是我的分组方式不对（就像 `/shop/v1` 那次），后者是查过两种分组方式之后仍然空白。**

**而我查了 `RaffleFlow` 才敢这么说 —— 因为「抽签」这个词在复刻件里是有主的，
它有主在一个我一开始没想到的流程里。**
"""

VERDICT = """

---

## 第 835 轮：PopMart 抽签面没有任何流程覆盖

### 反编译确认它真的发请求

| 端点 | 所在函数 | 形状 |
|---|---|---|
| `activity/v1/activity/sample_info` | `sub_140B8B340` (0x188) | **URL 构造**：容量 76 的 StringBuilder，追加 144 字节 = 72 字符的端点串 |
| `activity/v1/exhibit_draw/draw` | `sub_140BC1340` (0x2bc) | **async 状态机**（`AsyncTaskMethodBuilder.Start`） |

### 没有任何流程覆盖它

| 流程 | 覆盖 |
|---|---|
| `PopMartFlow` | `/shop/v1/...`（13 个端点，全有镜像对应） |
| `RaffleFlow` | `r419.com` · `lndg.page` · `nodnod.digital` —— **Shopify 抽签 App** |

**`RaffleFlow` 不碰 PopMart → `exhibit_draw/draw` 在复刻件里不存在。**

### 它不是独立任务类型

```
DrawTask 0 · drawTask 0 · LotteryTask 0
```

**唯一的 PopMart 类型标记是 `$PopMartProductType`（单个）。**

> **所以抽签是 PopMart 模块内部的一条可选路径，不是独立任务型 —— 一家店，两种买法。**

### 验证

```
两个端点各有 1 match + 1 xref + 一次反编译（2079 / 3435 chars）
RaffleFlow 域名三个都不含 popmart · 三个任务型候选全 0 · 产品代码未改
```

### 仍然 Unknown

**抽签在任务里怎么被触发**（要读 `$PopMartProductType` 的枚举值）· **`/web/v2?partner=&appKey=` 与 `popDraw.json` 的 xref 都是 0**（可能整串是拼出来的，或被页面脚本读）· **抽签要不要做**（取决于 Cybersole 的 PopMart 任务是否含抽签模式 —— 枚举值或 UI）

### 教训

**上一轮我说「四块未建模」；这一轮把其中一块推进到「确认无流程覆盖、且是真代码」。**
**差别在于：前者可能只是我分组方式不对（`/shop/v1` 那次就是这样），后者是查过两种分组之后仍然空白。**
**而我先查了 `RaffleFlow` 才敢这么说 —— 「抽签」在复刻件里是有主的，主在一个我一开始没想到的流程里。**
"""

BACKLOG_ADD = """

## 优先级 ① — PopMart 抽签面无流程覆盖（R835，已取证）

**反编译确认是真代码，不是残留串：**

| 端点 | 函数 | 形状 |
|---|---|---|
| `activity/v1/activity/sample_info` | `sub_140B8B340` (0x188) | StringBuilder 容量 76 + 追加 144 字节（72 字符端点） |
| `activity/v1/exhibit_draw/draw` | `sub_140BC1340` (0x2bc) | async 状态机 |

**`RaffleFlow` 覆盖 `r419.com` / `lndg.page` / `nodnod.digital`（Shopify 抽签 App），不碰 PopMart。**

**不是独立任务型**：`DrawTask` / `drawTask` / `LotteryTask` 全 0；唯一标记 `$PopMartProductType`。

> **一家店两种买法：直接买盒（`/shop/v1/box/...`，有）与抽签（`exhibit_draw`，没有）。**

| 仍 Unknown | |
|---|---|
| 抽签怎么被触发 | 读 `$PopMartProductType` 的枚举值 |
| `/web/v2?partner=&appKey=` 的 xref | **0** —— 可能整串是拼出来的 |
| `popDraw.json` 的 xref | **0** —— 可能被页面脚本读 |
| 抽签要不要做 | 取决于任务是否含抽签模式（枚举值或 UI） |

**纪律**：**「未建模」与「确认无覆盖」是两句话。前者可能是分组方式不对，后者是查过两种分组后仍空白。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R835", BLOCKER)
    ensure(RSTATUS, "R835", BLOCKER)
    ensure(RVERDICT, "第 835 轮", VERDICT)
    ensure(BACKLOG, "R835", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R835" not in h:
        h += ("\n## R835 补充 — PopMart 抽签面\n\n"
              "`activity/v1/sample_info` → `sub_140B8B340`（URL 构造）· `activity/v1/exhibit_draw/draw` → "
              "`sub_140BC1340`（async）。**两个都是真代码。**\n"
              "**`RaffleFlow` 覆盖 Shopify 抽签 App（r419/lndg/nodnod），不碰 PopMart → 抽签面无流程覆盖。**\n"
              "不是独立任务型（`DrawTask`/`LotteryTask` 全 0），是 `$PopMartProductType` 下的一条可选路径。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R835"), (RSTATUS, "R835"), (RVERDICT, "第 835 轮"), (BACKLOG, "R835")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R835: the PopMart draw surface has no flow covering it, and the decompilation confirms it is real\n\n"
         "R830 listed four PopMart surfaces the replica does not model and could not say whether they matter. This"
         " round pushes one of them from unmodelled to confirmed-uncovered, using R829's route: the string, xrefs at"
         " minus twelve, then the enclosing function.\n\n"
         "Two endpoints resolve. activity/v1/activity/sample_info lives in sub_140B8B340, which builds a StringBuilder"
         " of capacity 76 and appends 144 bytes -- seventy-two characters -- from the sample_info string itself before"
         " continuing. activity/v1/exhibit_draw/draw lives in sub_140BC1340, an async state machine that switches on its"
         " state field and starts through AsyncTaskMethodBuilder. Neither is a leftover literal; both issue requests.\n\n"
         "No flow covers them. PopMartFlow models the /shop/v1 shop surface, which R830 confirmed is fully backed by the"
         " image. RaffleFlow models r419.com, lndg.page and nodnod.digital -- the Shopify raffle apps -- and never"
         " touches PopMart. So the draw path exists in the image and nowhere in the replica.\n\n"
         "It is not a separate task type either. DrawTask, drawTask and LotteryTask all return nothing, and the only"
         " PopMart type marker in the image is PopMartProductType. So the draw is an optional path inside the PopMart"
         " module rather than a task type of its own, which fits the flow's own comment about sealed boxes: one shop,"
         " two ways to buy.\n\n"
         "The distinction that matters for the record is between unmodelled and confirmed-uncovered. R830's four were"
         " the first; this one is now the second, because I checked two different groupings -- by site and by the word"
         " the replica actually uses -- and the draw still has no owner. I only reached that confidence after finding"
         " that RaffleFlow is where the concept lives, in a flow I did not think of when I started.\n\n"
         "Unknown: how the draw is triggered inside the PopMart task, which needs the values of PopMartProductType; the"
         " enclosing functions for /web/v2?partner=popmart&appKey= and popDraw.json, both of which have no xref at minus"
         " twelve and may be assembled from parts or read by page script rather than by C#; and whether the draw needs"
         " implementing at all, which depends on whether Cybersole's PopMart task offers a draw mode.\n\n"
         "No product code changed; seven metrics carry at 4 / 0 / 17 / 78 / 0 and 277,120 / 171,690 / 61.96%."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
