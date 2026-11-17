"""Record R1073: the same query returns fewer strings than it did before the repair."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 同一条查询，**修复前 9 条、修复后 4 条** —— 那比分期族重要（R1073）

**本轮想做 ① 的实质证据：flow 的步骤顺序可以从不需类型映射的分期文案族里读。
→ 而去查的时候撞上一个数字对不上，而那个对不上必须排在分期族前面。**

### ① 那个不一致

| 轮 | 查询 | 结果 |
|---|---|---|
| **R1053** | `str "Solving PayPal 3DS"` | **9 条** —— `(1) (2) (2.1) (3) (4) (5) (6) (7) (8)` |
| **R1073** | `str "Solving PayPal 3DS"`（同一条） | **4 条** |

**→ 同一条 pattern、同一个 `Cybersole.exe`、同一个 `idb_path`。**
→ 所以差异**不在产物**，在**查询所见的数据库状态**。**

### ② 而中间发生了什么：一次 repair + 升级

**R1070 的框序里有：**

```
Database for file '…\\Cybersole.exe.id0' is not closed. Do you want IDA to repair it?
Please note that the repaired database will be upgraded to the current version of IDA
and may still have problems.
                                          → 点了 **是(&Y)**
```

**→ 而那次 repair 是**我自己点的**（按 goal 规程）。而它自己就警告了「may still have problems」。
→ **⇒ 那个 9 → 4 很可能是 repair/升级的结果，而不是产物变了。** **（Inference —— 未直接验证。）**

### ③ 而它是对的判据是什么，要写清

**→ 若 repair 丢了字符串，那 `fundamental 是一个**证据基线的变化**，而它会影响**所有**基于 `str` 的历史结论。
→ 而那些结论有：`FINGERPRINT_VOCAB.md`（2 命中）· `VENDOR_COVERAGE.md`（13 家）·
`CAPTCHA_COVERAGE.md`（6 家）· `PAYMENT_CHALLENGES.md`（9 条分期）· `BUSINESS_TYPES.md`（122 类型）。

**→ 这条不确认，那五份文档的数字都可能建立在一个**比现在更大**的表上。**

### ④ 而可验证的路径是明确的

| 判据 | 做法 |
|---|---|
| 池的条目总数是否变了 | IDA 的 `strings` 总数（R1053 记为 324,895）与现在比 |
| 是否只有 `(N)` 形状变了 | 查一个**稳定**的对照（如 `kpsdk` = 17，**未变**）|
| 还是整个池变了 | 查 `datadome` / `queue-it` 等 R1044 用过的对照 |

**→ 而 `kpsdk` 现在仍是 **17**，与 R1044/R1053 一致 ⇒ **不是整个池塌了。**
→ 所以差异可能只落在**长字符串**上（`Solving PayPal 3DS (2.1)` 21 字符），而那要单独验。**

### ⑤ 而本轮的分期族结论**作废**

**→ 我先报了「35 个族」，然后发现 33 个是字节噪声；筛完是 **0** 个「可读且多阶段」。
→ 而 0 又与我期望的 PayPal 箱矛盾 —— 而矛盾的原因就是上面那个 9 → 4。
→ **⇒ 所以「分期族」这条路**现在的**结论是「无法判定」，不是「没有族」。**

### ⑥ 数字

| 度量 | R1072 | **R1073** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| `kpsdk` 对照 | 17 | **17（未变）** |
| **`Solving PayPal 3DS`** | R1053: **9 条** | **4 条** |
| **分期族（可读且多阶段）** | — | **0 —— 但结论是「无法判定」** |
| **`str` 证据基线** | 假定稳定 | **可疑（repair 后）** |
| **受影响的历史文档** | — | **5 份** |

### 教训

> **「同一条查询两个结果」是**我自己**造成的，而它来自一个我按规程点的框。
> → 而那个框自己写着「may still have problems」—— 规程是对的（不点就连不上），
> 而代价是**证据基线可能变了**，而那件事必须在下一轮确认。**
> **→ 而这一轮的第二个教训：我差点把一个**基线漂移**读成「原版没有分期族」。
> → 两个数对不上时，先问「测量物变了没有」，而不是先解释差异。**
"""

if "同一条查询，**修复前 9 条、修复后 4 条**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1073 —— **同一条查询：修复前 9 条、修复后 4 条；那比分期族重要**

### 不一致

| 轮 | 查询 | 结果 |
|---|---|---|
| **R1053** | `str "Solving PayPal 3DS"` | **9 条** |
| **R1073** | 同一条 | **4 条** |

**同 pattern、同产物、同 `idb_path` ⇒ 差异在**数据库状态**，不在产物。**

### 中间发生的事：一次 repair + 升级

R1070 的框是 `… id0 is not closed. Do you want IDA to repair it?`，
正文自己写着 `the repaired database will be upgraded … and may still have problems`。**我按规程点了「是(Y)」。**
**⇒ 9 → 4 很可能是 repair 的结果（Inference，未直接验证）。**

### 而影响面

若 repair 丢了字符串，那是**证据基线**变了，影响 **5 份历史文档**：
`FINGERPRINT_VOCAB` · `VENDOR_COVERAGE` · `CAPTCHA_COVERAGE` · `PAYMENT_CHALLENGES` · `BUSINESS_TYPES`。

### 而可验证的路径

**`kpsdk` 仍是 **17**（与 R1044/R1053 一致）⇒ **不是整个池塌了**。
差异可能只落在**长字符串**上（`Solving PayPal 3DS (2.1)` 21 字符），需单独验。
另可比 IDA 的 `strings` 总数（R1053 记 **324,895**）。

### 而本轮的分期族结论作废

先报「35 个族」→ 33 个是字节噪声 → 筛完 **0** 个「可读且多阶段」。
而 0 与期望的 PayPal 箱矛盾 —— 矛盾的原因就是 9 → 4。
**⇒ 「分期族」这条路现在的结论是**「无法判定」，不是「没有族」。**

### 数字

| 度量 | R1072 | **R1073** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| `kpsdk` | 17 | **17（未变）** |
| `Solving PayPal 3DS` | R1053: 9 | **4** |
| 分期族（可读多阶段） | — | **0 —— 结论「无法判定」** |
| `str` 证据基线 | 假定稳定 | **可疑** |
| 受影响历史文档 | — | **5 份** |

**纪律**：两个数对不上时，先问「测量物变了没有」，而不是先解释差异。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1073", NOTE)
append(RBLOCK, "R1073", "\n---\n\n## 497. **同一条查询 9 条 → 4 条；证据基线可疑**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1073: the same query returns four where it returned nine, and the baseline is suspect\n\n"
     "The plan was to read flow step order from numbered stage families in the pool, which needs no mapping from names\n"
     " to addresses. The first thing that happened was a number not matching.\n\n"
     "R1053 asked for Solving PayPal 3DS and got nine strings, one through eight with a 2.1 among them. The same query\n"
     " now returns four. Same pattern, same artifact, same idb path, so the difference is not in the artifact but in\n"
     " what the database holds.\n\n"
     "What happened in between was a repair. R1070's dialog said an id0 had not been closed, asked whether to repair,\n"
     " and warned in its own text that the repaired database would be upgraded and might still have problems. The\n"
     " documented action is yes, and I took it. So nine becoming four is most likely the repair, though that is an\n"
     " inference rather than something verified.\n\n"
     "The scope matters more than the case. If the repair dropped strings, then the evidence baseline moved, and five\n"
     " documents were built on it: the fingerprint vocabulary, vendor coverage, captcha coverage, payment challenges\n"
     " and business types. The kpsdk control still reads seventeen, the same as in R1044 and R1053, so the pool has not\n"
     " collapsed wholesale; the loss, if real, is on longer strings, and comparing the total count of 324,895 recorded\n"
     " in R1053 is the check to run.\n\n"
     "That also voids this round's stage-family result. The tool first reported thirty-five families, thirty-three of\n"
     " which were byte noise once I dropped the end anchor, and after filtering for readable multi-stage names it\n"
     " reported zero -- which contradicts the known PayPal box. The contradiction is the nine-to-four, so the honest\n"
     " reading of that route is undetermined rather than empty.\n\n"
     "Figures: suite green at 2258, freshness zero files and zero lines, count unchanged, kpsdk still seventeen, the\n"
     " PayPal family down from nine to four, zero readable multi-stage families with the reason being the baseline, and\n"
     " five documents whose numbers rest on a pool that may have shrunk.\n\n"
     "Unknown: whether the repair removed strings, and whether the comparison total is still 324,895.\n\n"
     "The lesson is that when two numbers disagree the first question is whether the instrument changed, not how to\n"
     " explain the difference."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
