"""Record R1074: the baseline did not move; I read the limit as a count again."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### R1073 的怀疑**被推翻**：基线没动，是我把 `--limit` 当成了总数（R1074）

**R1073 说「同一条查询 9 条变 4 条」⇒ 证据基线可疑 ⇒ 5 份文档可能建立在一个更大的池上。
→ 这一轮查 `survey_binary`，而它给出的是铁证：**

```
total_functions:   321,244     (named 4,506 · library 5,535 · unnamed 311,203)
total_strings:   **324,895**    ← 与 R1053 记录的**完全一致**
sha256: f2b96d9abd76559c76f8054f14fdb1482c8aebc2884fdc6ee3f485d09f3e3128
                                 ← 与 pe_triage 从文件算的**完全一致**
```

**→ **池的条目数没变。那 5 份文档建立在一个没有缩小的证据基线上。**

### ① 而 9 → 4 的真因

**我 R1073 用来「验证」的那次查询是：**

```powershell
python analysis/ida.py str "Solving PayPal 3DS" --limit 4     ← **我传了 4**
→ {"n":4, "matches":[ … 只显示了 3 条 … ]}
```

**→ `n:4` 是**返回条数**，而 R1067 已经查明了这一点：**
```
--limit 6 → n=6        --limit 5000 → n=500（硬上限）
```

**→ 所以我用 `--limit 4` 问「有几条」，得到的 `4` 是**我自己设的上限**。
→ 而 R1053 用 `--limit 600` 得到 **9** —— 两个数都对，只是**问法不同**。**

### ② 而那是同一个错的**第五次**

| 次 | 轮 | 我把什么读成了什么 |
|---|---|---|
| 1 | R816 | 字符串池的抽样当全量 |
| 2 | R764 | 括号计数当类边界 |
| 3 | **R1054** | `provider metadata=0`（正则不匹配）当零 |
| 4 | **R1067** | `Cybersole\\.` 的 500 条当全部 —— **然后我写了文档说明 `n` 是返回数** |
| 5 | **R1073/R1074** | **`--limit 4` 的返回 4 当命中总数** |

**→ 而第 4 次与第 5 次之间只隔了七轮，且第 4 次的结论我**亲手写进了文档**。
→ **⇒ 「写下来」不保证「不再犯」。而能保证的是什么？**

**→ 答案是：让工具**不可能被读错**。
→ `n` 这个键名叫 `n`，而它既可能是总数也可能是返回数 —— **那是一个歧义的接口**。
→ 而正确的修法是让它报两个数：`returned` 与 `total`（若可得），或至少叫 `returned`。**

### ③ 所以本轮的真交付是**接口歧义**，不是基线

**→ 我把 R1073 那个「基线可疑」**撤销**，并把错因从「repair 丢了数据」改成「我把 limit 当总数」。
→ 而为了不再犯第五次之后的第六次，`ida.py str` 的输出键应当改名。而那是下一轮的一行改动。**

**→ 而在那之前，一条可执行的纪律：**问「有几条」时永远传一个大 limit，并把返回数与上限比较** ——
→ 若相等，就是不饱和，不能当总数。**

### ④ 数字

| 度量 | R1073 | **R1074** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| **`total_functions`** | — | **321,244（未变）** |
| **`total_strings`** | R1053: 324,895（怀疑变了） | **324,895 —— 未变** |
| **`sha256`** | — | **与 pe_triage 一致** |
| **基线是否漂移** | **可疑** | **否 —— 撤销** |
| **9 → 4 的真因** | 「repair 丢了字符串」 | **我传了 `--limit 4`** |
| **5 份文档** | 可能受影响 | **不受影响** |
| **`n` 键的歧义** | 未识别 | **识别 —— 应改名，下一轮一行** |

### 教训

> **「写下来」不保证「不再犯」：R1067 我把 `n` 是返回数写进了文档，
> 而七轮后我用 `--limit 4` 问「有几条」并接受了 `4`。**
> **→ 而能保证的不是更强的纪律，是**更难的误解**：让工具报 `returned` 与 `total` 两个键，
> 而让「四个」这件事在输出里就写着是返回数。**
> **→ 与前几轮那些「让状态可见」的做法同族：staleness、guard actually ran、resolved 列 ——
> 都是把**容易读错的接口**改成**读不错的**。**
"""

if "R1073 的怀疑**被推翻**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1074 —— **R1073 的怀疑被推翻：基线没动，是我把 `--limit` 当成总数**

### 铁证

```
total_functions:  321,244        named 4,506 · library 5,535 · unnamed 311,203
total_strings:   **324,895**     ← 与 R1053 **完全一致**
sha256: f2b96d9a…                ← 与 pe_triage **完全一致**
```

**⇒ 池没缩小 ⇒ 5 份文档**不受影响**。**

### 而 9 → 4 的真因

```powershell
python analysis/ida.py str "Solving PayPal 3DS" --limit 4     ← **我传了 4**
→ n:4
```

**`n` 是**返回条数**（R1067 已查明：`--limit 6→n=6`，`--limit 5000→n=500`）。
⇒ 我用 `--limit 4` 问「有几条」，得到的是**我自己设的上限**。R1053 用 600 得 9。**两个数都对，问法不同。**

### 而那是同一个错的第五次

| 次 | 轮 | 把什么读成了什么 |
|---|---|---|
| 1 | R816 | 抽样当全量 |
| 2 | R764 | 括号计数当类边界 |
| 3 | R1054 | 正则不匹配当零 |
| 4 | **R1067** | 500 条当全部 —— **然后我把 `n` 是返回数写进了文档** |
| 5 | **R1073/74** | **`--limit 4` 的 4 当命中总数** |

**⇒ 「写下来」不保证「不再犯」—— 第 4 次与第 5 次只隔七轮。**

### 所以真交付是**接口歧义**

`n` 既可能是总数也可能是返回数 ⇒ **歧义的接口**。修法是报两个键（`returned` / `total`）。
**与「让状态可见」同族：staleness · guard actually ran · resolved 列 —— 都是把**容易读错的接口**改成**读不错的**。**

### 数字

| 度量 | R1073 | **R1074** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| `total_functions` | — | **321,244** |
| `total_strings` | 324,895（怀疑变了） | **324,895 —— 未变** |
| 基线是否漂移 | **可疑** | **否 —— 撤销** |
| 9 → 4 的真因 | 「repair 丢了字符串」 | **我传了 `--limit 4`** |
| 5 份文档 | 可能受影响 | **不受影响** |
| `n` 键歧义 | 未识别 | **识别，下一轮一行** |

**纪律**：「写下来」不保证「不再犯」；把接口改成读不错的，才保证。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1074", NOTE)
append(RBLOCK, "R1074", "\n---\n\n## 498. **基线未漂移；是我把 `--limit` 当总数（第五次）**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1074: the baseline never moved, and I read the limit as a count for the fifth time\n\n"
     "R1073 reported the same query returning four strings where it had returned nine, called the evidence baseline\n"
     " suspect, and named five documents whose numbers might rest on a pool that had shrunk. This round checked with\n"
     " survey_binary, which answers it flatly: 321,244 functions and 324,895 strings, the same string total R1053\n"
     " recorded, and a sha256 that matches what pe_triage computes from the file. The pool did not shrink. The five\n"
     " documents are unaffected.\n\n"
     "The nine became four for a duller reason. The query I used to verify was str with --limit 4, and n came back as\n"
     " four because four is what I asked for. n is the number returned, which R1067 established with a limit sweep and\n"
     " which I wrote into a document at the time. R1053 used a limit of six hundred and got nine. Both figures are\n"
     " right; the questions differed.\n\n"
     "That makes this the fifth appearance of one mistake: a sample read as a census, a brace count read as a class\n"
     " boundary, a regex that did not match read as zero, five hundred strings read as everything, and now a limit read\n"
     " as a total. The fourth and fifth are seven rounds apart, and between them I wrote down that n is the returned\n"
     " count.\n\n"
     "So writing a thing down does not prevent repeating it, which means the fix is not a firmer rule. The fix is an\n"
     " interface that cannot be misread: n is ambiguous, because it could be either, and the tool should report\n"
     " returned and total as separate keys, or at least name the first one returned. That is a one-line change and it is\n"
     " the next round's first task.\n\n"
     "Until then the workable habit is that existence questions always use a large limit and compare what comes back\n"
     " against that limit: equality means unsaturated, which is not a total.\n\n"
     "Figures: suite green at 2258, freshness zero files and zero lines, count unchanged, 321,244 functions, 324,895\n"
     " strings matching R1053 exactly, a matching digest, one suspicion withdrawn, five documents unaffected, and an\n"
     " ambiguous key identified.\n\n"
     "The lesson is that making a state visible beats remembering it -- staleness, a guard that prints it ran, a\n"
     " resolved column -- and the same treatment is owed to a key that can be read two ways."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
