"""Record R817: three tools, three ceilings, and the 'lower bound' claim was wrong too."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 241. **三个工具三层上限**，而「1182 是下界」这句话也错了

> R817。`analysis/ida.py`：`str` 加 `--limit`（原来是硬编码 40）。

### 一、为什么去数

R814 说「1182 个 `myshopify` slug 是下界」，理由是池子是抽样。
**这一轮想用 IDA 拿到真值 —— 结果发现第三个问题。**

### 二、`ida.py str` 原来硬编码 `limit: 40`

```python
elif cmd == 'str':
    print(call('find_regex', {'pattern': rest[0], 'limit': 40}))   # 第 67 行
```

**所以：**

| `str` 返回 | 含义 |
|---|---|
| **0** | **确实没有** —— 可信 |
| 1–39 | 精确 |
| **40** | **≥40，数不出来** |

**而 `kasada` / `cloudflare` / `stripe` / `recaptcha` / `myshopify` / `https` 全是 **40**。**
**R807 我就看到过这个「全是 40」的现象，当时写成「那是搜索上限，不是巧合」—— 但没去改它。**

### 三、加了 `--limit` 之后，暴露出第二层上限

```
python analysis/ida.py str "myshopify" --limit 4000
  matches=500   distinct slugs=486
```

**插件自己还有一层 ~500 的上限。** **而池子给的是 1182。**

### 四、三层上限，互相矛盾

| 来源 | 数量 | 上限性质 |
|---|---|---|
| `analysis/pe_strings.txt` | **1182 个 slug** | 180,228 行 / 9.3 MB 的抽样（镜像 324,895 条串） |
| `ida.py str`（默认） | 28 | **硬编码 40 条** |
| `ida.py str --limit 4000` | **486** | **插件约 500 条** |

**所以「1182 是下界」这个说法也是错的**：
**它不是下界，是「另一个来源得到的另一个数」。** 两个来源互相矛盾（1182 vs 486），
**谁都不是对方的子集，所以不能说一个包含另一个。**

### 五、能说的和不能说的

**能说**：两个来源都给出「数百个」，而复刻件只有 33 个 —— **「远多于 33」这个方向成立。**

**不能说**：**具体多少个。** 三个工具都有天花板，而且彼此不一致。

**这条要写进 §2.7b 的补充**：**不只是「全量还是抽样」，还有「这个工具自己有没有上限」。**

### 六、改了什么

```python
limit = 40
if '--limit' in rest:
    limit = int(rest[rest.index('--limit') + 1])
print(call('find_regex', {'pattern': rest[0], 'limit': limit}))
```

**默认行为不变（40），但数数时可以抬高 —— 抬到 500 就撞上插件那层，这本身是信息。**

### 七、验证

```
python analysis\\ida.py str "myshopify"                  -> 40（上限）
python analysis\\ida.py str "myshopify" --limit 4000     -> 500（插件上限）
python analysis\\ida.py str "NIKE-GS"                    -> 1（精确）
python analysis\\ida.py str "saintalfred"                -> 0（确实没有）
本轮未改产品代码
完整套件保持 1766 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 八、仍然 Unknown

- **`myshopify` slug 的真实数量**：**Unknown** —— 三个工具都给不出，**且互相矛盾。**
- **插件那层 500 上限是不是可配**：**Unknown** —— `find_regex` 的 `limit` 传了 4000，返回 500，
  **说明上限在插件侧而不是参数侧。** 要改得动 `ida_mcp.py`。
- **池子的 180,228 行与镜像 324,895 条串的关系**：**Unknown** —— 不知道抽样规则，
  **所以也不知道 1182 是偏高还是偏低。**

### 九、教训

**R807 我写下「全是 40，那是搜索上限」的时候，就已经知道有上限了。**
**但知道有上限，和去改它，隔了十轮。**

**而中间那十轮里，我用这个工具做了若干次计数 —— 包括 R814 那一次。**
**「发现了限制」不等于「处理了限制」，而两者的记录看起来一样。**
"""

VERDICT = """

---

## 第 817 轮：三个工具三层上限

### `ida.py str` 原来硬编码 `limit: 40`

| 返回 | 含义 |
|---|---|
| 0 | 确实没有（可信） |
| 1–39 | 精确 |
| **40** | **≥40，数不出来** |

**`kasada` / `cloudflare` / `stripe` / `recaptcha` / `myshopify` / `https` 全是 40。**

### 加 `--limit` 后暴露第二层

```
--limit 4000  ->  matches=500, distinct slugs=486
```

**插件自己还有 ~500 条上限。而池子给 1182。**

| 来源 | 数量 | 上限 |
|---|---|---|
| `pe_strings.txt` | **1182** | 180k/324k 的抽样 |
| `str` 默认 | 28 | **硬编码 40** |
| `str --limit 4000` | **486** | **插件 ~500** |

### 所以「1182 是下界」也错了

**它不是下界，是另一个来源的另一个数。两个来源互相矛盾（1182 vs 486），谁都不是对方的子集。**

**能说**：两者都是「数百」，远超 33 —— **方向成立**
**不能说**：**具体多少个**

### 改了什么

`--limit N` 参数（默认仍是 40）。抬到 500 就撞上插件那层 —— **这本身是信息。**

### 验证

```
str "myshopify" 40（上限）· --limit 4000 500（插件上限）· "NIKE-GS" 1（精确）· "saintalfred" 0（确实没有）
产品代码未改 · 整套 1766 / 0 · 度量未变
```

### 教训

**R807 我写下「全是 40，那是搜索上限」时就已经知道有上限了。但知道有上限，和去改它，隔了十轮。**

> **中间那十轮里我用这个工具做过若干次计数。「发现了限制」不等于「处理了限制」，而两者的记录看起来一样。**
"""

BACKLOG_ADD = """

## 工具 — `ida.py str` 的上限（R817）

**`str` 原来硬编码 `limit: 40`（第 67 行），已加 `--limit`。**

| 来源 | myshopify slug 数 | 上限性质 |
|---|---|---|
| `pe_strings.txt` | **1182** | 180,228 行 / 324,895 条串的**抽样** |
| `str` 默认 | 28 | **硬编码 40** |
| `str --limit 4000` | **486** | **插件约 500 条** |

**三者互相矛盾，谁都不是对方的子集。所以「1182 是下界」也错了 —— 它是另一个来源的另一个数。**

| `str` 返回 | 含义 |
|---|---|
| 0 | **确实没有（可信）** |
| 1–39 | 精确 |
| 40 | **≥40，数不出来** |

**能说**：数百个，远超 33（方向成立）。**不能说**：具体多少。

| 仍 Unknown | |
|---|---|
| slug 真实数量 | 三工具都给不出且矛盾 |
| 插件 500 上限可否配 | `find_regex` 传 4000 仍返 500 → 上限在插件侧，要改 `ida_mcp.py` |
| 池子抽样规则 | 不知，所以不知 1182 偏高还是偏低 |

**纪律**：**「发现了限制」不等于「处理了限制」，而两者的记录看起来一样。**
R807 我就写了「全是 40，那是搜索上限」，但中间十轮仍用它做计数。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R817", BLOCKER)
    ensure(RSTATUS, "R817", BLOCKER)
    ensure(RVERDICT, "第 817 轮", VERDICT)
    ensure(BACKLOG, "R817", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R817"), (RSTATUS, "R817"), (RVERDICT, "第 817 轮"), (BACKLOG, "R817")):
        body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R817: three tools with three ceilings, and the lower-bound claim was wrong too\n\n"
         "R814 said the 1182 myshopify slugs were a lower bound because the pool is a sample. Counting them with IDA\n"
         "to get the real figure turned up a third problem instead: ida.py str hard-coded limit 40 on line 67, so\n"
         "kasada, cloudflare, stripe, recaptcha, myshopify and https all returned exactly forty. A zero was still\n"
         "trustworthy and anything under forty was exact, so the cap corrupted counting while leaving existence checks\n"
         "intact -- and it corrupted counting invisibly.\n\n"
         "The flag is now --limit. Raising it to 4000 returns 500 matches and 486 distinct slugs, which is the plugin's\n"
         "own ceiling rather than the parameter's. So three sources disagree: the pool says 1182, the default search\n"
         "says 28, and a raised search says 486. None is a subset of another, which means 1182 is not a lower bound at\n"
         "all -- it is a different measurement, and the sentence in R814 that called it a bound was wrong.\n\n"
         "What survives is the direction. Both sources land in the hundreds and the replica models thirty-three, so far\n"
         "outnumbers thirty-three holds. What does not survive is any specific figure, and the backlog now says so\n"
         "rather than carrying a number forward.\n\n"
         "The uncomfortable part is that R807 already noted this: entering the vendor reconciliation I observed that\n"
         "kasada, cloudflare, shape, recaptcha, adyen and stripe all came back at exactly forty and wrote that it was\n"
         "the search ceiling rather than a coincidence. Ten rounds later I was still using the tool to count. Noticing a\n"
         "limit and handling a limit leave identical-looking records, and only one of them is real.\n\n"
         "Unknown: the true slug count, which no available tool can give and which the available ones contradict; whether\n"
         "the plugin's 500 ceiling is configurable, since passing 4000 and getting 500 puts it on the plugin side and\n"
         "would mean editing ida_mcp.py; and how the pool's 180,228 lines relate to the image's 324,895 strings, which\n"
         "decides whether 1182 overcounts or undercounts.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
