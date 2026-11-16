"""Record R836: the PopMart surface enumerated against the replica, token by token."""

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

## 260. PopMart 覆盖面**逐条枚举**：镜像 17 个记号，复刻件命中 1 类

> R836。未改产品代码。这张表是判据 (f) 的形状。

### 一、镜像的 PopMart 全貌（`ida.py str "opmart" --limit 200`，38 条）

**按性质分四组：**

| 组 | 记号 |
|---|---|
| **类型** | `$PopMartProductType` · `PopMartField` · `PopMartHandler` · `PopMartRpcHandler` · `PopMartBrowser` |
| **命名空间** | `Cybersole.Core, Version=5.18.32.0 … :Cybersole.Engine.Popmart` |
| **模式/站点变体** | `POPMART` · `POPMART DEBUG` · `POPMART-DEBUG` · **`POPMART-RESERVATION`** · `PopMart Store` · **`PopMart-Tax-All`** · `Popmart` · `Popmart.html` |
| **身份/路径** | `popmart` · `popmart.com` · `.popmart.com` · `_popmart_com` · **`popmart_apac`** · **`popmart_registration`** |
| **区域 API** | `prod-{apac,global,hk,mo,na,uk-online}-api.popmart.com` |
| **端点** | `/web/v2?partner=popmart&appKey=` · `/shop/v1/...`（13 个，R830 已对） · `activity/v1/activity/sample_info?key=` · `activity/v1/exhibit_draw/draw?` · `global-activities/json/popDraw.json?t=` |

### 二、逐条核复刻件

| 记号 | 复刻件 |
|---|---|
| `POPMART-RESERVATION` | **0** |
| `popmart_registration` | **0** |
| `Tax-All` | **0** |
| `POPMART DEBUG` | **0** |
| `PopMartField` / `PopMartHandler` / `PopMartRpcHandler` / `PopMartBrowser` / `PopMartProductType` | **全 0** |
| `popmart_apac` / `_popmart_com` | **全 0** |
| `/shop/v1/...`（13 个） | **全部命中**（R830） |

**`registration` 这个词在复刻件里有 13 处，但都在别的流程里**（`BstnFlow` · `DemandwareFlow` · `MagentoFlow` 等），
**`popmart_registration` 这一条没有。**

**结论：复刻件覆盖 PopMart 的店铺下单面（`/shop/v1`），不覆盖它的预约/抽签、注册、税费、区域主机、以及四个类型。**

### 三、这次枚举改变了什么

**R830 说「四块未建模」。这一轮把它变成一张逐条可对的表，并且发现上一轮漏了两组：**

- **`POPMART-RESERVATION`** —— 「预约」。R830 只知道有抽签 API，**不知道它作为一个模式名存在**
- **`popmart_registration`** —— 注册路径。**完全没提过**
- **`PopMart-Tax-All`** —— 税费处理。**完全没提过**
- **`popmart_apac`** —— 区域标识。R830 只记了 6 个主机名，**没记这个内部键**

**所以「四块」这个数是错的 —— 真实是至少七块。**
**而它之所以是错的，因为我上轮用「URL 形态」筛了一遍，把不带斜杠的键（`popmart_apac`、`POPMART-RESERVATION`）滤掉了。**

**这与 R830 自己刚记下的教训是同一条，只是换了个筛子：上一轮按站名搜，这一轮按 URL 形态筛。**

### 四、验证

```
ida.py str "opmart" --limit 200      -> 38 matches, 全部列出
复刻件 grep 13 个记号               -> 12 个为 0，`registration` 13 处但都在别的流程
ida.py str "/shop/v1/"              -> 41 matches（复刻件 13 个端点全在其中）
本轮未改产品代码
七项度量沿用
```

### 五、仍然 Unknown

- **`POPMART-RESERVATION` 是站点名还是模式名**：**Unknown** ——
  它与 `POPMART` / `POPMART DEBUG` 排在一起（`0x146e3454c` 起，间隔 40 字节），**像是一组同表条目**，
  但那张表是「站点别名表」还是「模式枚举」**没确认。**
- **`PopMart-Tax-All` 是税类别还是开关**：**Unknown**。
- **`popmart_apac` 与 6 个区域主机的映射关系**：**Unknown** —— 名字暗示 apac 对应 `prod-apac-api`，**未证。**
- **这七块里哪些非做不可**：**Unknown** —— 抽签可能要看任务模式；注册、税费、区域主机**可能是下单必需**。

### 六、教训

**上一轮我用「URL 形态」筛选，于是漏掉了 `POPMART-RESERVATION`、`popmart_apac`、`PopMart-Tax-All`
这三个不带斜杠的键 —— 而它们恰恰是最像「模式」的三个。**

**R830 记的教训是「别按站名搜，按复刻件写的串搜」。**
**这一轮补上后半句：也别按形态筛。完整列出来，再分类。**

**「四块」和「七块」的差别不是精度，是我漏了三个最能说明功能的词。**
"""

VERDICT = """

---

## 第 836 轮：PopMart 覆盖面逐条枚举 —— 上一轮说「四块」，真实是七块

### 镜像全貌（38 条，按性质分）

| 组 | 记号 |
|---|---|
| 类型 | `$PopMartProductType` · `PopMartField` · `PopMartHandler` · `PopMartRpcHandler` · `PopMartBrowser` |
| 命名空间 | `…:Cybersole.Engine.Popmart` |
| **模式/变体** | `POPMART` · `POPMART DEBUG` · **`POPMART-RESERVATION`** · `PopMart Store` · **`PopMart-Tax-All`** · `Popmart.html` |
| **身份/路径** | `_popmart_com` · **`popmart_apac`** · **`popmart_registration`** |
| 区域 API | `prod-{apac,global,hk,mo,na,uk-online}-api.popmart.com` |
| 端点 | `/web/v2?partner=&appKey=` · `/shop/v1/...`（13，已有） · `activity/v1/sample_info` · `exhibit_draw/draw` · `popDraw.json` |

### 复刻件命中

| 记号 | 复刻件 |
|---|---|
| `/shop/v1/...` 13 个 | **全部命中** |
| 其余 12 个记号 | **全 0** |

（`registration` 在复刻件有 13 处，但都在 `BstnFlow`/`DemandwareFlow`/`MagentoFlow` 等别的流程里，
`popmart_registration` 这一条没有。）

### 上一轮漏了什么，为什么

**R830 用「URL 形态」筛了一遍，把不带斜杠的键滤掉了 —— 而漏掉的三个恰好最像「模式」：**

- **`POPMART-RESERVATION`** —— 预约模式，R830 只知道有抽签 API，不知道它作为模式名存在
- **`popmart_registration`** —— 注册路径，**完全没提过**
- **`PopMart-Tax-All`** —— 税费，**完全没提过**

> **R830 的教训是「别按站名搜，按复刻件写的串搜」。这一轮补后半句：也别按形态筛。完整列出来，再分类。**

**「四块」与「七块」的差别不是精度 —— 是我漏了三个最能说明功能的词。**

### 仍然 Unknown

**`POPMART-RESERVATION` 是站点别名还是模式枚举**（与 `POPMART DEBUG` 相邻，间隔 40 字节，像同表条目）·
**`PopMart-Tax-All` 是税类别还是开关** · **`popmart_apac` ↔ 6 个区域主机怎么映射** · **七块里哪些非做不可**

### 验证

```
str "opmart" --limit 200 → 38 条全列 · 复刻件 12/13 记为 0 · str "/shop/v1/" → 41 匹配
产品代码未改 · 七项度量沿用
```
"""

BACKLOG_ADD = """

## 优先级 ① — PopMart 覆盖表（R836，逐条可复算）

| 记号 | 镜像 | 复刻件 |
|---|---|---|
| `/shop/v1/...`（13 端点） | 有 | **全部命中** |
| `$PopMartProductType` · `PopMartField` · `PopMartHandler` · `PopMartRpcHandler` · `PopMartBrowser` | 有 | **0** |
| **`POPMART-RESERVATION`** | 有 | **0** |
| **`popmart_registration`** | 有 | **0** |
| **`PopMart-Tax-All`** | 有 | **0** |
| `popmart_apac` · `_popmart_com` · `POPMART DEBUG` | 有 | **0** |
| 6 个 `prod-*-api.popmart.com` | 有 | **0** |
| `activity/v1/sample_info` · `exhibit_draw/draw` · `popDraw.json` | 有 | **0** |
| `/web/v2?partner=&appKey=` | 有 | **0** |

**R830 说「四块」，真实是七块** —— 因为上一轮用「URL 形态」筛，把 `POPMART-RESERVATION` / `popmart_apac` / `PopMart-Tax-All` 三个不带斜杠的键滤掉了。**而它们最像「模式」。**

> **R830 的教训是「别按站名搜」；这一轮补后半句：也别按形态筛。完整列出，再分类。**

| 仍 Unknown | |
|---|---|
| `POPMART-RESERVATION` 是别名还是模式枚举 | 与 `POPMART DEBUG` 相邻 40 字节，像同表条目 |
| `PopMart-Tax-All` 是什么 | 税类别 or 开关 |
| `popmart_apac` ↔ 区域主机映射 | 未证 |
| 七块里哪些非做不可 | 抽签看任务模式；注册/税费/区域主机可能下单必需 |
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R836", BLOCKER)
    ensure(RSTATUS, "R836", BLOCKER)
    ensure(RVERDICT, "第 836 轮", VERDICT)
    ensure(BACKLOG, "R836", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R836" not in h:
        h += ("\n## R836 补充 — PopMart 覆盖表\n\n"
              "38 条 PopMart 记号全部列出并对到复刻件：**13 个 `/shop/v1` 端点全部命中，其余 12 个记号为 0**。\n"
              "**R830 说「四块」是错的，真实七块** —— 漏了 `POPMART-RESERVATION` / `popmart_apac` / `PopMart-Tax-All`，"
              "因为上轮按「URL 形态」筛，把不带斜杠的键滤掉了。\n"
              "**教训补一句：别按站名搜，也别按形态筛。完整列出再分类。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R836"), (RSTATUS, "R836"), (RVERDICT, "第 836 轮"), (BACKLOG, "R836")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R836: the PopMart surface enumerated, and last round's four is really seven\n\n"
         "R835 established that the draw surface has no flow covering it. This round lists all thirty-eight"
         " PopMart-bearing strings and checks each against the replica, which turns a loose claim into a table anyone"
         " can re-run.\n\n"
         "The image carries five type names -- PopMartProductType, PopMartField, PopMartHandler, PopMartRpcHandler and"
         " PopMartBrowser -- a namespace, a group of mode or variant strings (POPMART, POPMART DEBUG,"
         " POPMART-RESERVATION, PopMart Store, PopMart-Tax-All, Popmart.html), identity keys (_popmart_com,"
         " popmart_apac, popmart_registration), six regional API hosts and five endpoints beyond the shop paths.\n\n"
         "The replica matches thirteen shop endpoints and none of the other twelve marks. The word registration appears"
         " thirteen times in the replica but always in other flows -- BstnFlow, DemandwareFlow, MagentoFlow -- and never"
         " as popmart_registration.\n\n"
         "So R830's \"four unmodelled surfaces\" was wrong and the real count is at least seven. The reason is"
         " mechanical: I filtered that search to URL-shaped strings, which dropped POPMART-RESERVATION, popmart_apac and"
         " PopMart-Tax-All because they contain no slash -- and those three are the ones that most look like modes rather"
         " than paths.\n\n"
         "That is R830's own lesson wearing a different filter. That round learned not to search by site name because the"
         " replica's strings do not contain it; this round filtered by shape and lost the three most informative words."
         " The complete list has to come before the classification, not after.\n\n"
         "Unknown: whether POPMART-RESERVATION is a site alias or a mode in an enumeration, since it sits forty bytes"
         " from POPMART DEBUG as if they were entries in one table, without that table's purpose being established; what"
         " PopMart-Tax-All is; how popmart_apac maps onto the six regional hosts; and which of the seven actually has to"
         " be built, since the draw may depend on a task mode while registration, tax and the regional hosts may be"
         " required for any order at all.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
