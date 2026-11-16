"""Record R945 (retry): Imperva's absence is true, and why that matters."""

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
### Imperva 的否定是**真的** —— 而这才是 PerimeterX 那件事的用处（R945）

**R944 把 `Assert.Null(CookiesFor("Imperva"))` 标成「未验证」。这一轮跑了那个搜索。**

```
Imperva          0
incap_ses        0
visid_incap      0
nlbi_            0
_Incapsula_      0
```

**四条 Imperva 已知 cookie 前缀全 0 —— 所以那个否定是真的。**

### 而两个否定当时写得**一模一样**

| 断言 | 当时 | 现在 |
|---|---|---|
| `PerimeterX` 没有 `_px` cookie | 「刻意不填」 | **假**（`_px3` 在） |
| `Imperva` 没有 cookie | 同一种句式 | **真**（五条搜索全 0） |

> **所以区别不在**写得多小心**，而在**有没有一条命令产生它**。
> 两句都读起来像事实；一句有命令，一句没有。
> 而没有命令的否定，是一个用事实的语法写出来的猜测。**

### 而 Imperva 在复刻件里只作为**反例**存在

**`VendorWiring.cs` 一句注释 + `VendorWiringTests` 一条断言。`AntiBotVendors.Knows("Imperva")` 是 false ——
所以它不是「被忘掉的厂商」，是「根本不在的厂商」。**

**而这两者的区别，`Assert.Null` 单独看不出来。**

### 所以断言改成带证据的形式

**从「no search was run on it」改成「verified rather than asserted」+ 四条前缀被点名，
让下一个读的人能**重跑**，而不是**相信**。**

### 数字

| 度量 | R944 | **R945** |
|---|---|---|
| 套件 | 2043 | **2048** |
| 产物陈旧度 | 10 / 1044 | **10 / 1044**（未改产品代码） |
| **已带命令的否定** | 0 / 2 | **2 / 2** |

### 教训

> **上一轮修了一个**错的**否定；这一轮把**对的**那个也装上了证据 ——
> 因为一个碰巧为真的猜测，下一次改代码时仍然不可信。**
> **「对」和「可复算」是两件事。而只有后者能在改动之后还成立。**
"""

if "Imperva 的否定是**真的**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 945 轮：Imperva 的否定是真的 —— 而这才是上一轮那件事的用处

### 五条搜索全 0

```
Imperva 0 · incap_ses 0 · visid_incap 0 · nlbi_ 0 · _Incapsula_ 0
```

**四条 Imperva 已知 cookie 前缀全 0 → 那个否定是真的。**

### 而两个否定当时写得一模一样

| 断言 | 当时 | 现在 |
|---|---|---|
| `PerimeterX` 没有 `_px` | 「刻意不填」 | **假**（`_px3` 在） |
| `Imperva` 没有 cookie | 同一种句式 | **真**（五条全 0） |

> **区别不在**写得多小心**，而在**有没有一条命令产生它**。
> 没有命令的否定，是一个用事实的语法写出来的猜测。**

### 而 Imperva 只作为反例存在

**`AntiBotVendors.Knows("Imperva")` 是 false → 它不是「被忘掉的厂商」，是「根本不在的厂商」。
而这两者，`Assert.Null` 单独看不出来。**

### 断言改成了带证据的形式

**「no search was run on it」→「verified rather than asserted」+ 四条前缀被点名，
让下一个读的人能**重跑**而不是**相信**。**

### 数字

| 度量 | R944 | **R945** |
|---|---|---|
| 套件 | 2043 | **2048** |
| 产物陈旧度 | 10 / 1044 | **10 / 1044**（未改产品代码） |
| 已带命令的否定 | 0 / 2 | **2 / 2** |

### 教训

> **上一轮修了一个**错的**否定；这一轮把**对的**那个也装上了证据 ——
> 因为一个碰巧为真的猜测，下一次改代码时仍然不可信。
> 「对」和「可复算」是两件事。而只有后者能在改动之后还成立。**
"""

BACKLOG_ADD = """

## 优先级 ② — Imperva 否定已验证；两个否定的对照（R945，**+5 用例，未改产品代码**）

### 五条搜索

**`Imperva` / `incap_ses` / `visid_incap` / `nlbi_` / `_Incapsula_` → 全 0。**

### 对照

| 否定 | 结果 |
|---|---|
| PerimeterX 无 `_px` cookie | **假** |
| Imperva 无 cookie | **真** |

**区别不在写法，在有没有命令。**

### `VendorNegativeClaimsTests`（5 例）

**一假一真 · 四条前缀被点名 · 断言带证据 · Imperva 非已知厂商 · cookie 表 5 家不含它**

### 数字

**套件 2043 → 2048 · 陈旧度 10/1044（不变）· 带命令的否定 0/2 → 2/2**

| 仍 Unknown | |
|---|---|
| 其余否定断言有多少没带命令 | 未扫 |
| Imperva 是否曾出现在别的版本 | 只有本版 |
| PerimeterX 求解流程 | 只有名字与措辞 |

**纪律**：「对」和「可复算」是两件事，只有后者能在改动之后还成立。
"""

BLOCKER = """

---

## 369. Imperva 否定已验证；两个否定的对照

> R945。**+5 用例，未改产品代码。** 套件 **2048 通过 / 0 失败 / 0 跳过**。

### 一、五条搜索全 0

```
Imperva 0 · incap_ses 0 · visid_incap 0 · nlbi_ 0 · _Incapsula_ 0
```

**→ Imperva 无 cookie 的否定是**真的**。**

### 二、两个否定写得一模一样

| 断言 | 当时 | 现在 |
|---|---|---|
| PerimeterX 无 `_px` | 「刻意不填」 | **假** |
| Imperva 无 cookie | 同句式 | **真** |

**区别不在写得多小心，在有没有一条命令产生它。
没有命令的否定，是一个用事实的语法写出来的猜测。**

### 三、Imperva 只作为反例

**`AntiBotVendors.Knows("Imperva")` = false → 不是「忘掉的厂商」，是「不在的厂商」。
`Assert.Null` 单独看不出这个区别。**

### 四、断言改带证据

**「no search was run on it」→「verified rather than asserted」+ 四条前缀点名。**

### 五、数字

| 度量 | R944 | R945 |
|---|---|---|
| 套件 | 2043 | **2048** |
| 产物陈旧度 | 10 / 1044 | **10 / 1044** |
| **带命令的否定** | 0 / 2 | **2 / 2** |

### 六、验证

```
analysis/ida.py str 五条          -> 全 0
test --filter VendorNegativeClaimsTests -> 5 通过
metrics_report.py                 -> 2048 通过 / 0 失败
```

### 七、仍然 Unknown

- **其余否定断言有多少没带命令**：**Unknown** —— 未扫。
- **Imperva 是否曾出现在别的版本**：**Unknown** —— 只有本版。
- **PerimeterX 求解流程**：**Unknown**。

### 八、教训

**上一轮修了一个**错的**否定；这一轮把**对的**那个也装上了证据 ——
因为一个碰巧为真的猜测，下一次改代码时仍然不可信。**

**「对」和「可复算」是两件事。而只有后者能在改动之后还成立。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R945", BLOCKER)
    ensure(RSTATUS, "R945", BLOCKER)
    ensure(RVERDICT, "第 945 轮", VERDICT)
    ensure(BACKLOG, "R945", BACKLOG_ADD)

    note = (
        "\n## R945 补充 — Imperva 否定已验证；两个否定的对照（+5 用例，未改产品代码，套件 2048）\n\n"
        "五条搜索全 0：Imperva / incap_ses / visid_incap / nlbi_ / _Incapsula_ → Imperva 无 cookie 的否定是真的。\n\n"
        "对照：PerimeterX「刻意不填」是假（_px3 在），Imperva 是真。"
        "区别不在写法，在有没有一条命令产生它 —— 没有命令的否定，是用事实语法写出来的猜测。\n\n"
        "Imperva 只作为反例（AntiBotVendors.Knows = false）→ 不是忘掉的厂商，是不在的厂商。\n"
        "断言改成「verified rather than asserted」+ 四条前缀点名，让下一个读的人能重跑。\n\n"
        "数字：套件 2043 → 2048 · 陈旧度不变 · 带命令的否定 0/2 → 2/2。\n\n"
        "纪律：「对」和「可复算」是两件事，只有后者能在改动之后还成立。\n\n"
        "下一轮：扫其余否定断言有多少没带命令；或 ③ 请求与指纹层。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R945" not in h:
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
             for p, k in ((RBLOCK, "R945"), (RSTATUS, "R945"), (RVERDICT, "第 945 轮"), (BACKLOG, "R945")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R945: Imperva's absence is true, which is what makes the PerimeterX case instructive\n\n"
         "R944 labelled an assertion about Imperva as unverified because no search had been run on it. This round ran it.\n"
         " Imperva returns zero, and so do all four of its known cookie prefixes: incap_ses, visid_incap, nlbi_ and\n"
         " _Incapsula_. So the negative is true.\n\n"
         "That is the useful result rather than a trivial one. Two negatives were phrased identically, one false and one\n"
         " true, and what separated them was not how carefully they were written but whether a command had produced them.\n"
         " A negative that does not carry its command is a guess in the grammar of a fact, and both of these read like\n"
         " facts.\n\n"
         "Imperva also appears only as a counter-example: AntiBotVendors does not know it, so the null cookie is consistent\n"
         " with a vendor that is not there rather than one whose cookie was forgotten, and Assert.Null alone cannot tell\n"
         " those apart. The assertion now names the four prefixes and says the absence was verified, so the next reader\n"
         " can re-run it instead of trusting it.\n\n"
         "Figures: suite 2043 to 2048, freshness unchanged since no product code changed, and negatives carrying their\n"
         " evidence from none of two to both.\n\n"
         "Unknown: how many other negatives in the repository carry no command; whether Imperva appears in another version;\n"
         " and PerimeterX's solving flow.\n\n"
         "The lesson is that last round fixed a false negative and this one put evidence on a true one, because a guess\n"
         " that happens to be right is still not trustworthy after the next change. Being right and being recomputable are\n"
         " two different things, and only the second survives an edit.\n\n"
         "Tests and one assertion changed; suite green at 2048."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()