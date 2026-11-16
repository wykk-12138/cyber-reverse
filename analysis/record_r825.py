"""Record R825: all twenty availability scrapers reach a verdict, and five differ by site."""

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

## 249. 20 个 `ScrapeVariantAvailabilityAsync` 全部写判定；五个短模板按站点不同

> R825。未改产品代码（内存 1.29 GB，只读）。

### 一、为什么要查

R823 的扫描说「26 个重写只返回成功、不发 HTTP」，其中 19 个是 `ScrapeVariantAvailabilityAsync`。
**只抽读了两个**（`RetailFlows` 与 `Shopify`），都做了实事。**「两个是对的」不等于「全部是对的」。**

**一个只返回成功、不写判定的实现，会让监控报上一次的状态** —— 正是本会话反复遇到的「静默错值」。

### 二、结果：20 个，0 个空转

```
ScrapeVariantAvailabilityAsync implementations: 20
never write a verdict: 0
```

**全部写 `c.Session.Vars["available"]`。**

### 三、但 grep 级的检查骗过我多次，所以又抽读了 5 个最短的

那是模板化风险最高的一批（7–8 行）：

| 流程 | 判据 |
|---|---|
| `WarhammerFlow` | `body.Contains("\\"inStock\\":true")` |
| `FanaticsFlow` | `body.Contains("\\"inStock\\":true")` |
| `SuperswipeFlow` | `body.Contains("\\"available\\":true")` |
| `PocketGamesFlow` | `body.Contains("\\"available\\":true")` |
| **`RaffleFlow`** | **`c.Session.Vars.TryGetValue("open", ...)` —— 抽签「开放」才算有货** |

**关键是它们不一样。** `RaffleFlow` 根本不看 HTTP 响应体，它读的是上一步写进 session 的 `open` 标志 ——
**对抽签这是对的：抽签的「有货」等于「报名开放」，不等于某个商品字段。**

**模板没被盲目套用，这是本轮唯一想确认的东西。**

### 四、累计读过 10 个（全部 20 个的一半）

| 已通读 | 依据 |
|---|---|
| `BstnFlow` · `DemandwareFlow` · `FarfetchFlow` · `FootsitesFlow` · `GoatFlow` | 本轮前段打印 |
| `WarhammerFlow` · `FanaticsFlow` · `SuperswipeFlow` · `PocketGamesFlow` · `RaffleFlow` | 本轮抽读 |
| 其余 10 个（`Hbx` `Hybris` `Magento` `JohnLewis` `Nike` `PopMart` `YeezySupply` `Casio` `Scheels` `Shopify`） | **grep 级确认写了判定，未通读** |

### 五、验证

```
python analysis\\read_availability.py    20 个实现 / 0 个不写判定
抽读 5 个最长 8 行的：全部按站点不同
本轮未改产品代码
未跑全量（内存 1.29 GB < 2 GB）
四项度量沿用：4 / 0 / 17 / 78 / 0
```

### 六、仍然 Unknown

- **其余 10 个的判据是否各自正确**：**Unknown** —— grep 只证明它们**写了** `available`，
  **没证明写的规则对该站点是对的。** `NikeFlow` 31 行、`ScheelsFlow` 21 行、`CasioFlow` 23 行是其中最长三个。
- **这些字符串判据（`"inStock":true` 等）在真站上是否命中**：**Unknown** ——
  **它们是字符串匹配，而 5 个站点共用了 2 种模式**，可能有两个站用了同一个但只有一个对。
  这条只能靠实站验，需要凭据。

### 七、教训

**这一轮的答案是「没有缺陷」，而它比找一个缺陷更难得，因为我先确认了抽查不是白抽。**
**抽读 5 个最短的，是为了验证「它们不一样」—— 而如果一个模板被复制到 5 个站，
`0 个空转` 这个结论就只是说「都写了同一行」。**
"""

VERDICT = """

---

## 第 825 轮：20 个可用性解析全部写判定，五个短模板按站点不同

### 为什么查

R823 说 26 个重写只返回成功，其中 19 个是 `ScrapeVariantAvailabilityAsync`，**只抽读了两个**。
**「两个对」不等于「全部对」** —— 一个只返回成功、不写判定的实现会让监控报上一次的状态。

### 结果

```
20 个实现 · 0 个不写判定
```

### 但 grep 骗过我多次，所以又抽读 5 个最短的（7–8 行）

| 流程 | 判据 |
|---|---|
| `WarhammerFlow` / `FanaticsFlow` | `"inStock":true` |
| `SuperswipeFlow` / `PocketGamesFlow` | `"available":true` |
| **`RaffleFlow`** | **读 `Vars["open"]` —— 抽签「开放」才算有货** |

> **关键是它们不一样。`RaffleFlow` 根本不看响应体，它读上一步写的 `open` 标志 —— 对抽签这是对的。**
> **模板没被盲目套用。**

### 累计通读 10 个（半数）；其余 10 个 grep 级确认写了判定，未通读

### 验证

```
read_availability.py 20 / 0 · 未改产品代码 · 未跑全量（内存 1.29 GB）· 度量沿用 4 / 0 / 17 / 78 / 0
```

### 教训

**这一轮的答案是「没有缺陷」，而它比找到一个缺陷更难得 —— 因为我先确认了抽查不是白抽。**
**如果同一模板被复制到 5 个站，「0 个空转」就只是说「都写了同一行」。**
"""

BACKLOG_ADD = """

## 结案 — 20 个 ScrapeVariantAvailabilityAsync 全部写判定（R825）

```
20 个实现 · 0 个不写判定 · 抽读 5 个最短的：全部按站点不同
```

| 流程 | 判据 |
|---|---|
| `WarhammerFlow` / `FanaticsFlow` | `"inStock":true` |
| `SuperswipeFlow` / `PocketGamesFlow` | `"available":true` |
| **`RaffleFlow`** | **读 `Vars["open"]`**（抽签开放才算有货） |

**累计通读 10/20。其余 10 个（`Hbx` `Hybris` `Magento` `JohnLewis` `Nike` `PopMart` `YeezySupply` `Casio` `Scheels` `Shopify`）grep 级确认写了判定，未通读。**

| 仍 Unknown | |
|---|---|
| 其余 10 个的判据是否各自正确 | grep 只证明**写了**，没证明规则对该站对。最长三个：`NikeFlow` 31 行 · `CasioFlow` 23 行 · `ScheelsFlow` 21 行 |
| 字符串判据在真站是否命中 | **5 个站点共用 2 种模式**，可能有两个站用同一个但只有一个对。需实站验（等凭据） |

**纪律**：**「0 个空转」若来自同一模板被复制 5 份，就只是说「都写了同一行」。**
**抽读最短的，是为了验证「它们不一样」。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-26s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-26s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R825", BLOCKER)
    ensure(RSTATUS, "R825", BLOCKER)
    ensure(RVERDICT, "第 825 轮", VERDICT)
    ensure(BACKLOG, "R825", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    old3 = ("3. **`ScrapeVariantAvailabilityAsync` 有 19 个实现只返回成功** —— 抽查两个都是真活（读 `raw`、写 `available`），\n"
            "   **但没有全部读过。**")
    new3 = ("3. **`ScrapeVariantAvailabilityAsync` 已结案（R825）**：20 个实现**全部**写 `available` 判定，"
            "抽读 5 个最短的确认按站点不同"
            "（`RaffleFlow` 读 `Vars[\"open\"]`，`Warhammer`/`Fanatics` 查 `\"inStock\":true`）。"
            "**累计通读 10/20；其余 10 个只确认写了判定。**")
    if old3 in h:
        h = h.replace(old3, new3, 1)
        print("  handoff item 3 updated")
    elif "R825" in h:
        print("  handoff already updated")
    else:
        h += "\n## R825 补充\n\n20 个 `ScrapeVariantAvailabilityAsync` 全部写判定，抽读 5 个最短的确认按站点不同。\n"
        print("  handoff appended")
    io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)

    ok = True
    for path, key in ((RBLOCK, "R825"), (RSTATUS, "R825"), (RVERDICT, "第 825 轮"), (BACKLOG, "R825")):
        body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
        ok = ok and (key in body)
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R825: all twenty availability scrapers reach a verdict, and five short ones differ by site\n\n"
         "R823's scan reported twenty-six overrides that return only success, nineteen of them"
         " ScrapeVariantAvailabilityAsync, and only two had been read. Two being fine is not all being fine: an"
         " implementation that returns success without writing the verdict makes the monitor report the previous state,"
         " which is the silent wrong value this session keeps finding.\n\n"
         "All twenty write c.Session.Vars[\"available\"]. Zero silent.\n\n"
         "That check is grep-level, and grep-level checks have lied to me several times tonight, so I read the five"
         " shortest bodies as well -- the ones most exposed to copy-paste. Warhammer and Fanatics test"
         " \"inStock\":true, Superswipe and PocketGames test \"available\":true, and RaffleFlow does not look at the"
         " response body at all: it reads the `open` flag an earlier step wrote, because for a raffle available means"
         " the entry window is open rather than a product field. They differ, which is the thing worth confirming -- if"
         " one template had been copied to five sites, zero silent would only mean the same line appears five times.\n\n"
         "Ten of twenty are now read through. The other ten are confirmed by grep to write a verdict and not read, with"
         " NikeFlow at thirty-one lines, CasioFlow at twenty-three and ScheelsFlow at twenty-one being the ones most"
         " likely to hold a rule that is wrong for its site.\n\n"
         "Unknown: whether those ten reach the right verdict, since writing the key is not writing the right rule; and"
         " whether the string predicates fire on the real sites, since five sites share two patterns and only five"
         " distinct answers can be right, which needs credentials to settle.\n\n"
         "No product code changed; suite not run under the memory discipline at 1.29 GB; metrics carried at"
         " 4 / 0 / 17 / 78 / 0."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
