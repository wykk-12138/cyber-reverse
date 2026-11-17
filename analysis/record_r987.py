"""Record R987: Bstn is not a store the original has, so R986's attribution was wrong."""

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
### `Bstn` **不在原版里** —— 而那四个占位不是原版的缺口，是**复刻件多出来的站没做完**（R987）

**R986 说「优先级 ① 的剩余 = 一个站的四个端点」。这一轮去取那三个端点，第一个动作就否掉了那个说法。**

### ① 原版里没有 `bstn`

```
ida.py str bstn      -> 0 命中
ida.py str api/bstn  -> 0 命中
ida.py str bstn.com  -> 0 命中
```

**`ida.py str` 查的是数据库本身，所以反向可用（§2.7b 的环）。
而 `core_coverage.py` 的 27 个 store host 里**也没有 bstn**：
`goat` `hbx` `popmart` `scheels` 都在，`bstn` 不在。**

> **三项一致：名字不在字符串池、不在 27 个 host 里、而它自己的占位写着 `endpoint unknown`。**
> **→ `BstnFlow` 是**复刻件自己加的站**，原版没有它。那四个占位不是「原版某站没做完」，
> 是「复刻件多了一个站，而那个站没做完」。****

### ② 而这条不能推广 —— 有三个校准项

**把 18 个站点 flow 名字逐个查原版：**

| flow | 命中 | 而平台在不在 |
|---|---|---|
| **Bstn** | **0** | **不在**（也不在 27 host 里） |
| **Hybris** | **0** | **在** —— `ecommerce-gateway.mollie.com … hypecommerce` |
| **PoqApp** | **0** | **在** —— `app.midtrans.com … poqapp` |
| Hbx | 调用失败，未判 | `hbx.com` 在 27 host 里 |
| 其余 14 个 | 2 – 40（40 是插件上限） | — |

> **所以「名字不在」只在 Bstn 上成立为「站不在」。
> `Hybris` 与 `PoqApp` 是**校准项**：名字缺失证明不了**平台**缺失 —— 原版卖 hybris 的店，
> 只是不叫这个名字。**
> **这正是 §2.7b 的那条：一个来源找不到 ⇏ 不存在。而这里的「第二个来源」
> 是 `core_coverage` 的 host 列表，它把 Hybris/PoqApp 的宿主都列了出来。**

### ③ 所以 R986 的归属错了，而数没错

| R986 说 | 实际 |
|---|---|
| 优先级 ① 剩余 = Bstn 四个端点 | **不是原版缺口** —— Bstn 不在原版 |
| 185 覆写 / 180 真 / 5 占位 | **对**（这一轮没有推翻） |
| 判据 (f) 27/27 matched / 0 unmatched | **对**，而它**从未把 Bstn 算进去** |

> **所以判据 (f) 的 store 覆盖仍是 **27/27、0 未覆盖**。
> 而 `BstnFlow` 的存在是一个**超出原版**的添加，它的 4 个占位说明那个添加没做完。**

### ④ 而处置有两种，这一轮不定

**① 删掉 `BstnFlow`** —— 若目标是「1:1」，原版没有的东西不该有。
**② 保留并标为「超出原版的添加」** —— 若多一个站是可接受的扩展。**

> **而这是 YG 该定的事，不是证据能定的。理由：两个方向都自洽，
> 而「1:1」这个词在这次对话里没有被明确到「不许有额外站」。**
> **所以记进 BLOCKERS，标为需要判断，而不是自己决定。**

### 数字

| 度量 | R986 | **R987** |
|---|---|---|
| 套件 | 2205 | **2205（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| flow 覆写 / 真 / 占位 | 185 / 180 / 5 | **185 / 180 / 5（未变）** |
| **判据 (f) store matched** | 27/27 | **27/27（Bstn 从未算入）** |
| **不在原版的站点 flow** | 未测 | **1（Bstn）** |

### 教训

> **R986 我把「复刻件的 35 个 flow」默认成了「原版那些站」。
> 而从没有人说过它们是同一批 —— `core_coverage` 的 27/27 与 35 个 flow 类型一直是两个数，
> 而我把它们读成了一个。**
> **而校验它只需一次 `ida.py str`。**
"""

if "`Bstn` **不在原版里**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 987 轮：`Bstn` 不在原版里 —— 那四个占位是复刻件多出来的站没做完

### ① 原版里没有 bstn

```
ida.py str bstn      -> 0
ida.py str api/bstn  -> 0
ida.py str bstn.com  -> 0
```

**`ida.py str` 查数据库本身 → 反向可用。而 `core_coverage` 的 27 个 store host 里也没有 bstn：
`goat` `hbx` `popmart` `scheels` 都在，`bstn` 不在。**

> **三项一致：名字不在池、不在 27 host、自己的占位写着 `endpoint unknown`。
> → `BstnFlow` 是**复刻件自己加的站**。那四个占位不是「原版某站没做完」，是「多出来的站没做完」。**

### ② 而这条不能推广 —— 有三个校准项

| flow | 命中 | 平台在不在 |
|---|---|---|
| **Bstn** | **0** | **不在**（也不在 27 host） |
| **Hybris** | **0** | **在** —— `ecommerce-gateway.mollie.com … hypecommerce` |
| **PoqApp** | **0** | **在** —— `app.midtrans.com … poqapp` |
| Hbx | 调用失败 | `hbx.com` 在 27 host 里 |
| 其余 14 | 2–40（40 是插件上限） | — |

> **「名字不在」只在 Bstn 上成立为「站不在」。Hybris / PoqApp 是**校准项**：
> 名字缺失证明不了**平台**缺失 —— 原版卖 hybris 的店只是不叫这名字。**

### ③ R986 的归属错了，而数没错

| R986 说 | 实际 |
|---|---|
| 优先级 ① 剩余 = Bstn 四个端点 | **不是原版缺口** |
| 185 / 180 / 5 | **对** |
| 判据 (f) 27/27 / 0 unmatched | **对**，且它从未把 Bstn 算进去 |

### ④ 处置有两种，这一轮不定

**① 删掉 `BstnFlow`**（若是严格 1:1）**② 保留并标为超出原版的添加**（若扩展可接受）。

> **这是 YG 该定的事，不是证据能定的 —— 两个方向都自洽，而「1:1」没被明确到「不许有额外站」。
> 记进 BLOCKERS，标为需要判断。**

### 数字

| 度量 | R986 | **R987** |
|---|---|---|
| 套件 | 2205 | **2205（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 覆写 / 真 / 占位 | 185 / 180 / 5 | **未变** |
| **判据 (f) store matched** | 27/27 | **27/27（Bstn 从未算入）** |
| **不在原版的站点 flow** | 未测 | **1（Bstn）** |

### 教训

> **R986 我把「复刻件的 35 个 flow」默认成了「原版那些站」。
> `core_coverage` 的 27/27 与 35 个 flow 类型一直是两个数，而我把它们读成了一个。
> 校验它只需一次 `ida.py str`。**
"""

BACKLOG_ADD = """

## 判据 (f) — **`Bstn` 不在原版里：名字 0 命中 · 不在 27 host · 占位写 endpoint unknown**（R987）

### Observation

```
ida.py str bstn / api/bstn / bstn.com  -> 各 0 命中
core_coverage 的 27 个 store host        -> 无 bstn（goat / hbx / popmart / scheels 都在）
```

**→ `BstnFlow` 是**复刻件自己加的站**。R986 说的「优先级 ① 剩余 = Bstn 四个端点」**归属错误** ——
那 4 个占位不是原版缺口，是多出来的站没做完。**

### 校准项（这条不能推广）

| flow | 名字命中 | 平台在不在 |
|---|---|---|
| **Bstn** | **0** | **不在** |
| **Hybris** | **0** | **在**（`hypecommerce` host 在） |
| **PoqApp** | **0** | **在**（`poqapp` host 在） |

**→ 名字缺失证明不了平台缺失（§2.7b 同一纪律）。**

### 判据 (f) 不变

**store 覆盖仍 **27/27 matched、0 unmatched**；`BstnFlow` **从未**被算入。**

### 需要 YG 判断的一条（不是证据能定的）

**`BstnFlow` 处置：① 删掉（严格 1:1）② 保留并标为超出原版的添加。
两个方向都自洽，而「1:1」未被明确到「不许有额外站」。**

### 数字

**套件 2205（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 覆写 185/真 180/占位 5 · 不在原版的站点 flow 1**

**纪律**：27 个 host 与 35 个 flow 类型一直是两个数，我把它们读成了一个。
"""

BLOCKER = """

---

## 411. **`Bstn` 不在原版里 → R986 的归属错误；判据 (f) 仍 27/27**

> R987。**只取证 + 一处归档更正。** 套件 **2205（R986 的记录仍有效，未改代码）**。

### 一、Observation：原版没有 bstn

```
ida.py str bstn      -> 0 命中
ida.py str api/bstn  -> 0 命中
ida.py str bstn.com  -> 0 命中
```

**`ida.py str` 查数据库本身 → 反向可用（§2.7b）。而 `core_coverage` 的 27 个 store host 里也没有 bstn：
`goat` `hbx` `popmart` `scheels` 都在，`bstn` 不在。**

**→ 三项一致（名字不在池 · 不在 27 host · 自己的占位写着 `endpoint unknown`）
→ `BstnFlow` 是**复刻件自己加的站**。**

### 二、更正 R986

| R986 说 | 实际 |
|---|---|
| 优先级 ① 剩余 = Bstn 四个端点 | **不是原版缺口** —— Bstn 不在原版 |
| 185 覆写 / 180 真 / 5 占位 | **对** |
| 判据 (f) 27/27 matched / 0 unmatched | **对**，且它**从未**把 Bstn 算进去 |

### 三、校准项：这条不能推广

| flow | 名字命中 | 平台在不在 |
|---|---|---|
| **Bstn** | **0** | **不在** |
| **Hybris** | **0** | **在** —— `ecommerce-gateway.mollie.com … hypecommerce` |
| **PoqApp** | **0** | **在** —— `app.midtrans.com … poqapp` |
| Hbx | 调用失败，未判 | `hbx.com` 在 27 host 里 |

**→ 「名字不在」只在 Bstn 上成立为「站不在」。Hybris / PoqApp 名字缺失而平台在 ——
名字缺失证明不了平台缺失，这正是 §2.7b 那条，而这里的第二个来源是 `core_coverage` 的 host 列表。**

### 四、需要判断的一条（不是证据能定的）

**`BstnFlow` 处置：**
**① 删掉** —— 若目标是严格 1:1，原版没有的东西不该有
**② 保留并标为「超出原版的添加」** —— 若多一个站是可接受的扩展

**两个方向都自洽；「1:1」在这次对话里没有被明确到「不许有额外站」。
这一条留给 YG 定，我不自己决定。**

### 五、数字

| 度量 | R986 | R987 |
|---|---|---|
| 套件 | 2205 | **2205（未改代码）** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 173,952 | **173,952** |
| 覆写 / 真 / 占位 | 185 / 180 / 5 | **未变** |
| **判据 (f) store matched** | 27/27 | **27/27（Bstn 从未算入）** |
| **不在原版的站点 flow** | 未测 | **1（Bstn）** |

### 六、验证

```
cd D:\\projects\\cyber-reverse
python analysis/ida.py str bstn      -> {"n":0}
python analysis/ida.py str api/bstn  -> {"n":0}
python analysis/ida.py str bstn.com  -> {"n":0}
cd replica
python tools/core_coverage.py | grep -i bstn   -> 无输出
python tools/core_coverage.py                  -> store hosts 27, store hosts matched 27, unmatched 0
```

### 七、仍然 Unknown

- **`BstnFlow` 该保留还是删除**：**需要 YG 判断** —— 两个方向都自洽。

### 八、教训

**R986 我把「复刻件的 35 个 flow」默认成了「原版那些站」。
而 `core_coverage` 的 27/27 与 35 个 flow 类型**一直是两个数**，我把它们读成了一个。**

**校验它只需一次 `ida.py str`。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R987", BLOCKER)
    ensure(RSTATUS, "R987", BLOCKER)
    ensure(RVERDICT, "第 987 轮", VERDICT)
    ensure(BACKLOG, "R987", BACKLOG_ADD)

    note = (
        "\n## R987 补充 — **`Bstn` 不在原版里 → R986 归属错误；判据 (f) 仍 27/27**（套件 2205，未改代码）\n\n"
        "`ida.py str bstn` / `api/bstn` / `bstn.com` **各 0 命中**（查数据库本身，反向可用），\n"
        "而 `core_coverage` 的 27 个 store host 里也没有 bstn（goat/hbx/popmart/scheels 都在）。\n"
        "→ **`BstnFlow` 是复刻件自己加的站**；R986 说的「优先级 ① 剩余 = Bstn 四个端点」**归属错误**。\n\n"
        "**校准项（不能推广）**：Hybris / PoqApp 名字也是 0 命中，但 `hypecommerce` / `poqapp` host 都在\n"
        "→ **名字缺失证明不了平台缺失**（§2.7b）。\n\n"
        "→ 判据 (f) 不变：**27/27 matched，0 unmatched**；Bstn 从未被算入。\n\n"
        "**需要 YG 判断的一条**：`BstnFlow` 删掉（严格 1:1）还是保留并标为超出原版的添加。\n"
        "两个方向都自洽，「1:1」未被明确到「不许有额外站」—— 我不自己决定。\n\n"
        "数字：套件 2205（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 覆写 185/真 180/占位 5 · 不在原版的站点 flow 1。\n\n"
        "纪律：**27 个 host 与 35 个 flow 类型一直是两个数，我把它们读成了一个。**\n\n"
        "下一轮：按 R986 的守卫继续 —— 或者核其余 34 个 flow 与 27 个 host 的对应关系（35 vs 27 的差是 8）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R987" not in h:
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
             for p, k in ((RBLOCK, "R987"), (RSTATUS, "R987"), (RVERDICT, "第 987 轮"), (BACKLOG, "R987")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R987: Bstn is not a store the original has, so R986 attributed its placeholders wrongly\n\n"
         "R986 concluded that what remained for priority one was one store's four endpoints. Going to fetch those endpoints\n"
         " refuted that in the first step.\n\n"
         "The original has no bstn: three spellings searched directly against the database return nothing, and bstn is not\n"
         " among core_coverage's twenty-seven matched store hosts, though goat, hbx, popmart and scheels all are. Three\n"
         " independent facts agree, and the replica's own placeholder for the cart says the endpoint is unknown. So BstnFlow\n"
         " implements a store the original does not have, and its four placeholders are an unfinished addition rather than an\n"
         " original gap.\n\n"
         "That cannot be generalised, and the calibration is in the same table. Hybris and PoqApp also return nothing by name,\n"
         " yet their platforms are plainly present -- hypecommerce and poqapp both appear as matched hosts. Absence of a name\n"
         " proves nothing about absence of a platform, which is the discipline section 2.7b records. Only Bstn has all three\n"
         " signals at once.\n\n"
         "So the figures from R986 stand: 185 overrides, 180 doing work, five placeholders. What changes is the attribution.\n"
         " Criterion (f) is untouched at twenty-seven of twenty-seven matched with none unmatched, because it never counted\n"
         " Bstn.\n\n"
         "Whether BstnFlow should be deleted or kept and marked as an addition beyond the original is a judgement call, not\n"
         " something the evidence settles: both directions are coherent and the objective never said extra stores are\n"
         " forbidden. That goes to the blocker list as needing a decision rather than being decided here.\n\n"
         "Figures: suite 2205 unchanged, freshness zero, count 173,952, store coverage twenty-seven of twenty-seven, one\n"
         " store flow absent from the original.\n\n"
         "Unknown: whether BstnFlow should stay, which needs the user rather than more evidence.\n\n"
         "The lesson is that I read twenty-seven matched hosts and thirty-five flow types as one number. They were always two,\n"
         " and checking cost a single string search.\n\n"
         "No product code changed; one attribution corrected and one decision raised."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()