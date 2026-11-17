"""Record R1043: the ruling was in the file, and the real question is which resource takes the write."""

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
### 裁决就在那段代码上方；而真正的问题不是路由，是**哪个资源承接写入**（R1043）

**R1042 说下一轮找 `buy/orders/v2` 的真实路由当钥匙。找了 —— 而找到了路由，也找到了**自己正要重犯的错**。**

### ① 镜像里 Nike 的 buy 面是 **7** 条实名 URL

```
https://api.nike.com/buy/checkouts/v3/
https://api.nike.com/buy/checkout_previews/v3/
https://api.nike.com/buy/checkouts_jobs/v3/
https://api.nike.com/buy/checkout_previews_jobs/v3/
https://api.nike.com/buy/fulfillment_offerings_jobs/v2/
https://api.nike.com/buy/partner_cart_preorder/v2/
https://api.nike.com/buy/partner_cart_preorder_jobs/v2/
```

**→ 所以「Nike 没有结账面」是错的；`buy/orders/v2` 确实 0 次，而**结底面一直在 `buy/` 下**。**

### ② 而我正要做的动作，`NikeFlow.cs` 里已经裁决过

**我以为「找到 `checkouts/v3` ⇒ 把 shipping 改过去」是进展。而那段代码上方写着（R1014）：**

> R1013 replaced it with `checkouts/v3` on the strength of a header sentence — "the resource every step writes to" —
> which is true and does not settle **which resource carries a delivery write**. `CartUrl()`'s own had already ruled
> on exactly this move: "there is no way to tell which of `checkouts/v3` and `checkout_previews/v3` carries the add.
> **Swapping one guess for another would move the failure, not remove it.**"

**→ 所以：那条路由 **R1013 用过**，**R1014 撤回了**，而理由是**正确的**。
→ 而我这一轮差点第四次做同一个动作。**

**→ 那不是「没查到」，是**答案已经写在面前** —— 而那条教训已经记过两次（R995、R1014），
而这次是第三次站在同一个位置。**

### ③ 所以真正未决的问题**更窄**，而它被写进了生成物

| 问题 | 状态 |
|---|---|
| Nike 有没有结账面 | **有 —— 两个**（`checkouts/v3` · `checkout_previews/v3`） |
| 哪一个承接 **shipping 写入** | **Unknown** |

**→ 而「靠名字猜」被两条独立裁决否过（R48 · R1014），所以那不是可选路径。**

**→ 什么能解决它**：反编译一个**引用**那两条 URL 的函数，读它发什么方法、带什么 body。
→ 而那需要地址上的引用者 —— 而 NativeAOT 的池条目没有 xref（R1039 试过，0），
所以要用 IDAPython 搜 **immediates**，而不是 `xrefs_to`。

### ④ 所以本轮**不改代码**，改的是生成物

**`tools/core_coverage.py` 里加了这一段，重新生成后 `docs/CORE_COVERAGE.md` 从 3,275 字节增至 4,241：**

- Nike 的 7 条实名 URL
- 「Nike 没有结账面」是错的
- 未决的是**哪一个承接 shipping 写入**
- 为什么不能靠名字猜（R48 · R1014 的裁决）
- 什么能解决它（反编译引用者，下一轮）

**→ 而那让表里的 Unknown **更窄、更可动手** —— 上一轮它是「3 个未取证」，现在是「1 个具体的二选一」。**

### ⑤ 数字

| 度量 | R1042 | **R1043** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **Nike buy 面实名 URL** | 「0 条」 | **7** |
| **`buy/orders/v2`** | 0 | **0（仍）** |
| **Nike 未决问题** | 「3 个步骤未取证」 | **1 个：哪个承接 shipping 写入** |
| **`docs/CORE_COVERAGE.md`** | 3,275 字节 | **4,241 字节** |
| **我差点重犯的次数** | — | **1（被文件里已有的裁决挡住）** |

### 教训

> **这一轮我做对的事，是去读那段代码的注释** —— 而它就在我要改的方法**上方三行**。
> **→ 而它写着「换一个猜测只是移动失败」，且注明是 **R48 的裁决**，而那已经是两次教训。**
> **→ 所以第三条教训不是「先读再改」（那条已经有了），是：
> **当一件事你已经有「我知道该怎么改」的**冲动**时，那个冲动本身就是去读的理由。**
"""

if "裁决就在那段代码上方" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1043 轮：裁决就在那段代码上方；真正的问题不是路由

### ① 镜像里 Nike 的 buy 面是 **7** 条实名 URL

```
checkouts/v3 · checkout_previews/v3 · checkouts_jobs/v3 · checkout_previews_jobs/v3
fulfillment_offerings_jobs/v2 · partner_cart_preorder/v2 · partner_cart_preorder_jobs/v2
```

**→ 「Nike 没有结账面」是错的；`buy/orders/v2` 确实 0 次，而**结底面一直在 `buy/` 下**。**
**→ 且 `nike.com` 另有 55 条，含 `deliver/available_gtins/v3` 与 `accounts.nike.com/{authorize,token,challenge}/v1`。**

### ② 而我正要做的动作，`NikeFlow.cs` 里已经裁决过

> R1013 replaced it with `checkouts/v3` … which is true and does not settle **which resource carries a delivery
> write**. R48: "Swapping one guess for another would move the failure, not remove it."

**→ 那条路由 **R1013 用过，R1014 撤回了**，理由正确 ⇒ 我差点第四次做同一个动作。
→ 那不是「没查到」，是**答案已经写在面前三行**。**

### ③ 所以真正未决的问题更窄

| 问题 | 状态 |
|---|---|
| Nike 有没有结账面 | **有 —— 两个候选** |
| 哪一个承接 **shipping 写入** | **Unknown** |

**→ 靠名字猜已被 R48 与 R1014 两次否掉。
→ 解法：反编译**引用**那两条 URL 的函数（NativeAOT 池条目无 xref ⇒ 用 IDAPython 搜 immediates）。**

### ④ 本轮改的是生成物

**`core_coverage.py` 加这一段，表从 **3,275 → 4,241 字节**：
Nike 的 7 条 URL · 「没有结账面」是错的 · 未决的是二选一 · 为什么不能猜 · 什么能解决它。**

**→ 让 Unknown 从「3 个未取证」收窄成「1 个具体的二选一」。**

### ⑤ 数字

| 度量 | R1042 | **R1043** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **Nike buy 面实名 URL** | 「0 条」 | **7** |
| **Nike 未决问题** | 「3 个步骤未取证」 | **1 个：哪个承接写入** |
| **`CORE_COVERAGE.md`** | 3,275 字节 | **4,241 字节** |
| **差点重犯** | — | **1（被文件里的裁决挡住）** |

### 教训

> **这一轮做对的事，是去读那段代码的注释 —— 而它在我要改的方法**上方三行**。
> → 它写着「换一个猜测只是移动失败」，注明是 **R48 的裁决**，而那已是两次教训。**
> **→ 所以第三条不是「先读再改」（那条已有），是：
> **当一件事你已经有「我知道该怎么改」的**冲动**时，那个冲动本身就是去读的理由。****
"""

BACKLOG_ADD = """

## 判据 (f) — **Nike buy 面 7 条实名 URL；未决问题收窄成「哪个承接 shipping 写入」**（R1043）

### 7 条实名 URL

```
checkouts/v3 · checkout_previews/v3 · checkouts_jobs/v3 · checkout_previews_jobs/v3
fulfillment_offerings_jobs/v2 · partner_cart_preorder/v2 · partner_cart_preorder_jobs/v2
```

**→ `buy/orders/v2` 仍 0；**结底面一直在 `buy/` 下**。**

### 而我的动作已被裁决过

**R1013 换成 `checkouts/v3` ⇒ R1014 撤回（「路由存在不解决哪个承接写入」）；R48「换猜测只是移动失败」。
→ 我差点第四次做同一动作，而裁决在方法上方三行。**

### 收窄后的 Unknown

| 问题 | 状态 |
|---|---|
| Nike 有没有结账面 | **有 —— 两个候选** |
| 哪一个承接 shipping 写入 | **Unknown** |

**解法：反编译**引用**那两条 URL 的函数（池条目无 xref ⇒ IDAPython 搜 immediates）。**

### 编号

**`CORE_COVERAGE.md` 3,275 → **4,241** 字节（含 Nike 段与裁决引用）。**

### 数字

**套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · buy 面 7 · 未决 1（二选一）· 差点重犯 1**

| 仍 Unknown | |
|---|---|
| 哪个资源承接 shipping 写入 | **待反编译引用者** |
| Farfetch transport | 无线索 |

**纪律**：当一件事你已有「我知道该怎么改」的冲动时，那个冲动本身就是去读的理由。
"""

BLOCKER = """

---

## 467. **裁决就在那段代码上方；真正的问题不是路由，是哪个资源承接写入**

> R1043。**改 1 个生成器（未改业务代码）。** 套件 **2258 通过 / 0 失败 / 0 跳过**。

### 一、镜像里 Nike 的 buy 面是 **7** 条实名 URL

```
https://api.nike.com/buy/checkouts/v3/
https://api.nike.com/buy/checkout_previews/v3/
https://api.nike.com/buy/checkouts_jobs/v3/
https://api.nike.com/buy/checkout_previews_jobs/v3/
https://api.nike.com/buy/fulfillment_offerings_jobs/v2/
https://api.nike.com/buy/partner_cart_preorder/v2/
https://api.nike.com/buy/partner_cart_preorder_jobs/v2/
```

**→ 所以「Nike 没有结账面」是错的；`buy/orders/v2` 确实 0 次，而**结底面一直在 `buy/` 下**。**
**→ 且 `nike.com` 另有 55 条，含 `deliver/available_gtins/v3` 与
  `accounts.nike.com/{authorize,token,challenge}/v1`。**

### 二、而我正要做的动作，`NikeFlow.cs` 里已经裁决过

**我以为「找到 `checkouts/v3` ⇒ 把 shipping 改过去」是进展。而那段代码上方写着（R1014）：**

> R1013 replaced it with `checkouts/v3` on the strength of a header sentence — "the resource every step writes to" —
> which is true and does not settle **which resource carries a delivery write**. `CartUrl()`'s own had already ruled
> on exactly this move: "there is no way to tell which of `checkouts/v3` and `checkout_previews/v3` carries the add.
> **Swapping one guess for another would move the failure, not remove it.**"

**→ 所以：那条路由 **R1013 用过**，**R1014 撤回了**，而理由是**正确的**。
→ 而我这一轮差点第四次做同一个动作。**

**→ 那不是「没查到」，是**答案已经写在面前** —— 而那条教训已经记过两次（R995、R1014），
  而这次是第三次站在同一个位置。**

### 三、所以真正未决的问题**更窄**

| 问题 | 状态 |
|---|---|
| Nike 有没有结账面 | **有 —— 两个**（`checkouts/v3` · `checkout_previews/v3`） |
| 哪一个承接 **shipping 写入** | **Unknown** |

**→ 而「靠名字猜」被两条独立裁决否过（R48 · R1014），所以那不是可选路径。**

**→ 什么能解决它**：反编译一个**引用**那两条 URL 的函数，读它发什么方法、带什么 body。
→ 而那需要地址上的引用者 —— NativeAOT 的池条目没有 xref（R1039 试过，0），
  所以要用 IDAPython 搜 **immediates**，而不是 `xrefs_to`。

### 四、所以本轮**不改代码**，改的是生成物

**`tools/core_coverage.py` 里加了这一段，重新生成后 `docs/CORE_COVERAGE.md` 从 3,275 字节增至 4,241：**

- Nike 的 7 条实名 URL
- 「Nike 没有结账面」是错的
- 未决的是**哪一个承接 shipping 写入**
- 为什么不能靠名字猜（R48 · R1014 的裁决）
- 什么能解决它（反编译引用者，下一轮）

**→ 而那让表里的 Unknown **更窄、更可动手** —— 上一轮它是「3 个未取证」，现在是「1 个具体的二选一」。**

### 五、数字

| 度量 | R1042 | R1043 |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **Nike buy 面实名 URL** | 「0 条」 | **7** |
| **`buy/orders/v2`** | 0 | **0（仍）** |
| **Nike 未决问题** | 「3 个步骤未取证」 | **1 个：哪个承接 shipping 写入** |
| **`docs/CORE_COVERAGE.md`** | 3,275 字节 | **4,241 字节** |
| **我差点重犯的次数** | — | **1（被文件里已有的裁决挡住）** |

### 六、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str "/buy/" --limit 600        -> {"n":7}（七条 api.nike.com 实名 URL）
python analysis/ida.py str "nike\\.com" --limit 600    -> {"n":55}
cd replica
python tools/core_coverage.py   -> wrote docs/CORE_COVERAGE.md（4,241 字节）
python tools/metrics_report.py  -> 完整套件 exit 0  2258 / 0 / 0 · 陈旧度 0 / 0
```

### 七、仍然 Unknown

- **哪个资源承接 shipping 写入**：**待反编译引用者（下一轮）**。
- **Farfetch 的 transport**：无线索。

### 八、教训

**这一轮我做对的事，是去读那段代码的注释** —— 而它就在我要改的方法**上方三行**。

**→ 而它写着「换一个猜测只是移动失败」，且注明是 **R48 的裁决**，而那已经是两次教训。**

**→ 所以第三条教训不是「先读再改」（那条已经有了），是：
  **当一件事你已经有「我知道该怎么改」的**冲动**时，那个冲动本身就是去读的理由。****
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1043", BLOCKER)
    ensure(RSTATUS, "R1043", BLOCKER)
    ensure(RVERDICT, "第 1043 轮", VERDICT)
    ensure(BACKLOG, "R1043", BACKLOG_ADD)

    note = (
        "\n## R1043 补充 — **Nike buy 面 7 条实名 URL；未决问题收窄成「哪个承接 shipping 写入」**（套件 2258）\n\n"
        "**7 条实名 URL**：`checkouts/v3` · `checkout_previews/v3` · `checkouts_jobs/v3` ·\n"
        "`checkout_previews_jobs/v3` · `fulfillment_offerings_jobs/v2` · `partner_cart_preorder/v2` · (+`_jobs`)。\n"
        "→ `buy/orders/v2` 仍 **0**，而**结底面一直在 `buy/` 下**。\n\n"
        "**而我正要做的动作已被裁决**：R1013 换成 `checkouts/v3` ⇒ **R1014 撤回**（「路由存在不解决哪个承接写入」）；\n"
        "R48「换猜测只是移动失败」—— **裁决就在我要改的方法上方三行，而我差点第四次做同一动作。**\n\n"
        "**收窄后的 Unknown**：Nike 有结账面（两个候选）· 未决的是**哪一个承接 shipping 写入**。\n"
        "→ 靠名字猜被 R48/R1014 两次否掉；解法是**反编译引用那两条 URL 的函数**（池条目无 xref ⇒ IDAPython 搜 immediates）。\n\n"
        "**本轮改的是生成物**：`CORE_COVERAGE.md` 3,275 → **4,241** 字节，含 Nike 段与裁决引用。\n"
        "→ 让 Unknown 从「3 个未取证」收窄成「1 个具体的二选一」。\n\n"
        "数字：套件 2258/0/0 · 陈旧度 **0/0** · 函数数 174,293 · buy 面 **7** · 未决 **1** · 差点重犯 **1**。\n\n"
        "纪律：**当一件事你已有「我知道该怎么改」的冲动时，那个冲动本身就是去读的理由。**\n\n"
        "下一轮：用 IDAPython 搜引用 `0x147053d8c` / `0x147053c94` 的 immediates，读出哪个承接 shipping 写入。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1043" not in h:
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
             for p, k in ((RBLOCK, "R1043"), (RSTATUS, "R1043"), (RVERDICT, "第 1043 轮"), (BACKLOG, "R1043")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1043: the ruling was three lines above the method, and the real question is narrower\n\n"
         "R1042 left buy/orders/v2 as the key to three unknowns. Probing the family rather than the guess found seven\n"
         " real routes under api.nike.com/buy, so Nike has a checkout surface after all -- checkouts/v3 and\n"
         " checkout_previews/v3, each with jobs, plus fulfilment offerings and partner preorder.\n\n"
         "And then I nearly made the same edit for the fourth time. The comment three lines above the shipping method\n"
         " records that R1013 already switched to checkouts/v3, that R1014 withdrew it, and why: the route existing does\n"
         " not settle which of two resources carries a delivery write, and R48's ruling about swapping one guess for\n"
         " another is quoted there.\n\n"
         "So the finding is not the routes. It is that the question is narrower than last round stated it. Nike does\n"
         " have a checkout surface, with two candidate resources; which one takes the shipping write is the open\n"
         " question, and guessing by name has been refused twice on independent grounds. What would settle it is reading\n"
         " a function that references one of the two URLs -- and since NativeAOT pool entries carry no xrefs, that means\n"
         " searching immediates with IDAPython rather than xrefs_to.\n\n"
         "So no business code changed. The generated coverage document grew from 3,275 to 4,241 bytes to carry the seven\n"
         " URLs, the correction that Nike does have this surface, the narrowed question, both rulings, and the method\n"
         " that would answer it. Last round's unknown was three steps with no endpoint; this round's is one either-or.\n\n"
         "Figures: suite 2258 unchanged, freshness zero, count 174,293, seven buy URLs where the previous round recorded\n"
         " zero, one open question instead of three, and one near-miss that the file itself stopped.\n\n"
         "Unknown: which resource takes the shipping write, and Farfetch's transport.\n\n"
         "The lesson is not to read before editing, which is already written down twice. It is that the urge to make a\n"
         " change I feel sure about is itself the reason to go and read.\n\n"
         "One generator changed; suite green at 2258."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()