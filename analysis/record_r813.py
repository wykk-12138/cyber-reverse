"""Record R813: criterion (f)'s store half, done mechanically, with both sides named."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 237. 判据 (f) 的站点半边：**57 个模块逐个查过，6 个零证据，而镜像里有 1182 个 `myshopify` slug**

> R813。新增 `analysis/check_store_evidence.py` 与 `analysis/refine_store_evidence.py`（均留存）。

### 一、为什么要机械做

判据 (f) 要求「**原版站点与风控清单从二进制取证 ↔ `Registry.cs` 与 `Flows/Scripts` 逐条对，未覆盖的每条写为什么**」。

- **风控那半 R807 做了**（12 个已声明项全在镜像里，`Signifyd` 补进第 8 家，`Riskified` 单列）
- **站点这半此前是逐站零散做的** —— 每个站单独探一次，**但没人回答「哪一个站从来没被问过」**

### 二、复刻件侧：57 行，不是 63

`store_catalog.py` 的打印输出被解析出 **57 行**（其余 6 行因域名是 `(none)` 或间距不同没匹配上）。
**这是脚本的解析限制，不是模块缺失** —— `store_catalog.py` 自己报「distinct flow types: 33」，
而 `DocsConsistencyTests` 与 `ParityDocTests` 交叉钉着 63/33。

**记在这里，因为 57 与 63 的差别会让人以为少了 6 个模块。**

### 三、镜像侧：49 有证据，8 没有

对每个模块，搜它的 id 与每个域名（裸主机）：

```
有至少一条命中：49 / 57
零命中：        8
  bodega · bstn · nike-gs · offthehook · saintalfred · shophmvs · trophyroom · vooberlin
```

### 四、按 §2.7 补写法：6 个仍然零

对 8 个各试 `id` / `<slug>.myshopify.com` / `<slug>myshopify` / `<slug>.com` / `<slug>-` / `<slug>_`：

| 模块 | 结果 |
|---|---|
| `bodega` | **任何写法都 0** |
| `bstn` | **任何写法都 0**（已知：保留依据是抓包，见 §220） |
| `nike-gs` | **任何写法都 0** |
| `saintalfred` | **任何写法都 0** |
| `shophmvs` | **任何写法都 0** |
| `trophyroom` | **任何写法都 0** |
| `offthehook` | 只有 `oth` 命中 613 —— **3 字母子串，`other`/`mother` 都会中，噪音** |
| `vooberlin` | 只有 `voo` 命中 23 —— **同上，`voodoo` 之类，噪音** |

**所以：6 个模块在任何写法下都零镜像证据；2 个只有子串噪音。**

### 五、更要紧的一件事：**1182 个 `myshopify` slug**

```
distinct myshopify slugs in the pool: 1182
```

**而复刻件的 33 个 Shopify 别名只覆盖其中极小一部分。**

**这是判据 (f) 的「未覆盖侧」** —— 判据要求「未覆盖的每条写为什么」，
**而此前所有讨论都在问「复刻件多了什么」，没人问「镜像里还有多少没有建模」。**

**必须说清 1182 这个数不是 1182 个店**：

- 里面有 `020d06-2`、`0593bf-2`、`061e33-3` 这类**随机 ID 形态**（Shopify 的临时/预览主机）
- 也有 `10corsocomo`、`100t`、`303boards-com` 这类**真店名**

**所以 1182 是「slug 形态的字符串数」，不是「站点数」。** **要得出站点数得逐个分类，这一轮没做。**

### 六、判据 (f) 现在的状态

| 半边 | 状态 |
|---|---|
| 风控清单 | **已对账**（R807）：12 项已声明全在镜像里，`Signifyd` 进表，`Riskified` 单列 |
| 站点清单（复刻件 → 镜像） | **已逐条**：49/57 有证据，6 个零、2 个只有噪音 |
| 站点清单（镜像 → 复刻件） | **未做**：1182 个 slug 未分类，**不知道有多少真店未建模** |

**所以 (f) 的两个方向里，一个做完了，一个刚被量化。**

### 七、验证

```
python analysis\\check_store_evidence.py     57 行 / 49 有证据 / 8 零
python analysis\\refine_store_evidence.py    6 个任何写法都 0；2 个只有子串噪音；1182 个 slug
本轮未改产品代码
完整套件保持 1766 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 八、仍然 Unknown

- **6 个零证据模块该不该删**：**Unknown** —— `bstn` 有抓包依据（§220 已裁决保留），
  **其余 5 个（`bodega`/`nike-gs`/`saintalfred`/`shophmvs`/`trophyroom`）没有**。**这是下一个该裁决的。**
- **1182 个 slug 里有多少是真店**：**Unknown** —— 需要逐个分类（随机 ID 形态 vs 可读店名）。
- **`nike-gs` 是不是 `kids.nike.com` 的别名**：**Inference（中）**，镜像里 `kids.nike` 也 0 命中。

### 九、教训

**「逐条对」有两个方向，我只做了一个方向好几十轮。**
复刻件多了什么、每个多了的为什么 —— 这是我在问的。
**镜像里有什么、哪些还没建模 —— 这是判据原文在问的，而 1182 这个数字此前从未出现过。**
"""

VERDICT = """

---

## 第 813 轮：判据 (f) 的站点半边，两个方向

### 复刻件 → 镜像：57 个模块逐个查过

```
有证据 49 / 57
零证据  8：bodega · bstn · nike-gs · offthehook · saintalfred · shophmvs · trophyroom · vooberlin
```

**按 §2.7 补了六种写法后再判：**

- **6 个任何写法都 0**（`bodega` · `bstn` · `nike-gs` · `saintalfred` · `shophmvs` · `trophyroom`）
- **2 个只有子串噪音**（`offthehook` 的 `oth` 613、`voo` 23 —— 3 字母子串，`other`/`voodoo` 都会中）

### 镜像 → 复刻件：**1182 个 `myshopify` slug**

**而复刻件的 33 个 Shopify 别名只覆盖极小一部分。**

> **这是判据 (f) 的「未覆盖侧」。此前所有讨论都在问「复刻件多了什么」，没人问「镜像里还有多少没建模」。**

**但 1182 不是 1182 个店**：里面混着 `020d06-2` 这类随机 ID 形态与 `10corsocomo` 这类真店名。
**要得出站点数得逐个分类 —— 这一轮没做。**

### (f) 的现状

| 半边 | 状态 |
|---|---|
| 风控清单 | **已对账**（R807） |
| 站点（复刻件 → 镜像） | **已逐条**：49/57 有据，6 零、2 噪音 |
| 站点（镜像 → 复刻件） | **刚被量化**：1182 slug，未分类 |

### 验证

```
check_store_evidence.py · refine_store_evidence.py · 产品代码未改 · 整套 1766 / 0 · 度量未变
```

### 仍然 Unknown

**5 个零证据模块没有保留依据**（`bodega`/`nike-gs`/`saintalfred`/`shophmvs`/`trophyroom`；`bstn` 有，已裁决）· 1182 slug 里真店有多少 · `nike-gs` 是否 `kids.nike.com` 的别名

### 教训

**「逐条对」有两个方向，我只做了一个方向好几十轮。**
**复刻件多了什么是我在问的；镜像里还有什么没建模是判据在问的。**
"""

BACKLOG_ADD = """

## 判据 (f) — 站点清单两个方向（R813）

**新增** `analysis/check_store_evidence.py` · `analysis/refine_store_evidence.py`（留存可复算）。

### 复刻件 → 镜像

```
57 行解析（store_catalog 的打印输出；它自己报 33 flow types，63 由 DocsConsistencyTests 钉着）
有证据 49 / 57
零证据  8 → 补六种写法后：6 个仍 0，2 个只有 3 字母子串噪音
```

| 零证据（任何写法） | 依据 |
|---|---|
| `bstn` | **有抓包依据，已裁决保留**（§220） |
| `bodega` · `nike-gs` · `saintalfred` · `shophmvs` · `trophyroom` | **无依据 —— 待裁决** |

### 镜像 → 复刻件（此前未做）

```
distinct myshopify slugs in the pool: 1182
复刻件 Shopify 别名：33
```

**1182 ≠ 1182 个店**：混有 `020d06-2` 这类随机 ID 与 `10corsocomo` 这类真店名。**需逐个分类。**

| 待裁决 | |
|---|---|
| 5 个零证据模块删不删 | **下一个该裁决的** |
| 1182 slug 里真店数 | 需分类随机 ID 形态 vs 可读店名 |
| `nike-gs` 是否 `kids.nike.com` | Inference（中），`kids.nike` 也 0 命中 |

**纪律**：**「逐条对」有两个方向。** 我之前几十轮只问「复刻件多了什么」，没问「镜像里还有什么没建模」。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R813", BLOCKER)
    ensure(RSTATUS, "R813", BLOCKER)
    ensure(RVERDICT, "第 813 轮", VERDICT)
    ensure(BACKLOG, "R813", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R813"), (RSTATUS, "R813"), (RVERDICT, "第 813 轮"), (BACKLOG, "R813")):
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
         "R813: criterion (f)'s store half, both directions, and the 1182 slugs nobody had counted\n\n"
         "Criterion (f) asks for the original's store list taken from the binary, compared item by item with\n"
         "Registry.cs, with a reason for everything not covered. The risk half was settled in R807. The store half had\n"
         "only ever been done one store at a time, which answers local questions and cannot show which store was never\n"
         "asked about.\n\n"
         "Reading store_catalog's printed rows gives 57 modules -- fewer than the 63 the consistency tests pin, because\n"
         "six rows have (none) domains or different spacing and the parse skips them. That gap is recorded rather than\n"
         "smoothed, since 57 against 63 reads like six missing modules.\n\n"
         "Searching the pool for each module's id and its bare domains leaves 49 with evidence and eight without.\n"
         "Section 2.7 says to ask how many forms a thing can take before calling it absent, so six more forms were\n"
         "tried: the id, slug.myshopify.com, slugmyshopify, slug.com, slug- and slug_. Six of the eight stay at zero.\n"
         "The other two only match three-letter prefixes -- oth at 613 hits and voo at 23 -- which is noise, since\n"
         "other and voodoo both contain them.\n\n"
         "Then the direction nobody had run. The pool carries 1182 distinct myshopify slugs against the replica's 33\n"
         "Shopify aliases. That is the uncovered side of criterion (f), and it had never been counted because every\n"
         "earlier question was what the replica has too much of rather than what the image has that nothing models.\n\n"
         "The 1182 is not 1182 stores. Random-id hosts like 020d06-2 sit beside readable ones like 10corsocomo, so the\n"
         "figure counts slug-shaped strings, not sites. Splitting them needs a classification pass that this round did\n"
         "not attempt, and calling the raw number a store count would be the same mistake as reading a substring hit as\n"
         "evidence.\n\n"
         "Unknown: whether the five zero-evidence modules without capture backing -- bodega, nike-gs, saintalfred,\n"
         "shophmvs, trophyroom -- should be deleted, since only bstn has a ruling behind it; how many of the 1182 are\n"
         "real stores; and whether nike-gs is kids.nike.com under another name, which the pool also does not contain.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
