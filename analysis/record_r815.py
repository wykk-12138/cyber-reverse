"""Record R815: the pool is incomplete, two of five were false negatives, three remain."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 239. **`pe_strings.txt` 是不完整的** —— 撤回 R813 的两个假阴性

> R815。`analysis/recheck_ida.py`（留存）。未改产品代码。

### 一、我本来要删五个模块

R813 说 `bodega` / `bstn` / `nike-gs` / `saintalfred` / `shophmvs` / `trophyroom` 六个「任何写法在池子里都是 0」。
R815 准备据此把没有保留依据的几个删掉。

**动手前查连带影响时，在 `NikeHeaders.cs` 第 17 行看到：**

```
/// NIKE-GS                0x146df584c
```

**一个十六进制地址。** 于是去 IDA 里查：

```
NIKE-GS matches: 1
    0x146e11414    'NIKE-GS'
```

**它在镜像里。**（地址与注释里那个不同，说明注释可能是另一处引用，但两个都说明它在。）

### 二、那池子为什么搜不到

```
pool size: 9316662 chars
'NIKE-GS' in pool      : False
'nike-gs' in pool.lower: False
'NIKE' in pool         : True
```

**池子有 9.3 MB、含 `NIKE`，却不含 `NIKE-GS`。所以 `pe_strings.txt` 是抽样，不是全量。**

**这一条推翻了 R813 与 R814 的整个方法**：
**「池子里搜不到」不等于「镜像里没有」** —— 而我把它们当成同一件事，并据此写了两轮结论。

### 三、用 IDA 重查六个

```
bodega        HAS EVIDENCE  1   'Bodega'
nike-gs       HAS EVIDENCE  4   'NIKE-GS'
bstn          no match      0
saintalfred   no match      0
shophmvs      no match      0
trophyroom    no match      0
```

**所以五个待裁决里，两个是假阴性**：

- **`bodega`** —— 镜像里有 `'Bodega'`
- **`nike-gs`** —— 镜像里有 `'NIKE-GS'`（4 条）

**只剩三个真的没有**：`saintalfred` · `shophmvs` · `trophyroom`（`bstn` 有 §220 的裁决）。

### 四、差点犯的错

**我准备删五个。如果没查连带影响、没看到那行注释，就会删掉两个镜像里确实有的模块。**

**而删掉之后不会有任何东西报错** —— 测试只会从 63 变成 58，而那个数字本来就要改。
**一个「按证据删除」的动作，可能删掉证据本身。**

**这不是运气好，是「动手前先查连带影响」这条纪律救的。**
**如果我把「查连带」省掉、直接改 Registry，这一轮就是一次净损失。**

### 五、池子的性质现在要写清

`analysis/pe_strings.txt` **是 IDA 导出的一份字符串样本**，9.3 MB。
**它适合做「有没有这个东西」的正向线索（找到＝有），不适合做反向结论（没找到＝没有）。**

**这与 AGENTS.md §2.1 把池子列为「可信」并不矛盾，但它缺一句限定**：
**可信，但它是抽样；反向结论要用 IDA 的 `str`。**

**这一条该补进 AGENTS.md §2.7（扫描器的前置问题）**：**先问「我这个来源是全量还是抽样」。**

### 六、验证

```
python analysis\\recheck_ida.py       bodega 1 · nike-gs 4 · 其余 0
本轮未改产品代码
完整套件保持 1766 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- **`pe_strings.txt` 是怎么导出的、漏了哪些**：**Unknown** —— 我不知道它的导出命令，
  **所以也不知道它的抽样规则。** 补法：重导一份全量，或改用 IDA 的 `str` 做反向结论。
- **`saintalfred` / `shophmvs` / `trophyroom` 该不该删**：**仍是待裁决** ——
  **但现在要先用 IDA 确认，而不是池子。上面已经用 IDA 查过，三个都是 0。**
- **R814 的「1182 个 slug」是否也受影响**：**受影响** —— 那个数是从池子里数的，
  **真实值只会更多，不会更少。** 方向不变（远多于 33），但数值是下界。

### 八、教训

**「不在我的来源里」和「不存在」是两件事，而抽样来源让它们看起来像一件。**
**这一轮是「查连带影响」救了两个模块；下一轮该是「先问来源是否全量」避免这个问题。**
"""

VERDICT = """

---

## 第 815 轮：池子不完整 —— 撤回两个假阴性

### 我本来要删五个模块

R813 说六个模块「池子里任何写法都是 0」。我准备把没有保留依据的删掉。

**动手前查连带影响时，在 `NikeHeaders.cs:17` 看到 `NIKE-GS  0x146df584c` —— 一个地址。**

```
IDA: NIKE-GS matches: 1  ->  0x146e11414  'NIKE-GS'
```

**它在镜像里。**

### 那池子为什么搜不到

```
pool 9,316,662 chars
'NIKE-GS' in pool : False      'NIKE' in pool : True
```

> **`pe_strings.txt` 是抽样，不是全量。「池子里搜不到」不等于「镜像里没有」—— 而我把它们当成同一件事，写了两轮结论。**

### 用 IDA 重查

```
bodega 1 'Bodega' · nike-gs 4 'NIKE-GS' · bstn 0 · saintalfred 0 · shophmvs 0 · trophyroom 0
```

**五个待裁决里两个是假阴性。只剩三个真的没有。**

### 差点犯的错

**我准备删五个。没查连带、没看到那行注释，就会删掉两个确实存在的模块 —— 而删完不会有任何东西报错，测试只会从 63 变 58，那个数字本来就要改。**

> **一个「按证据删除」的动作，可能删掉证据本身。**
> **这次是「动手前先查连带影响」救的。**

### 池子的性质要写清

**9.3 MB 的样本，适合做正向线索（找到＝有），不适合做反向结论（没找到＝没有）。**
**R814 的 1182 也是从池子里数的 —— 那个数是下界，方向不变。**

### 验证

```
recheck_ida.py · 产品代码未改 · 整套 1766 / 0 · 度量未变
```

### 教训

**「不在我的来源里」和「不存在」是两件事，而抽样来源让它们看起来像一件。**
**这一轮是「查连带」救的；下一轮该是「先问来源是否全量」避免它。**
"""

BACKLOG_ADD = """

## 判据 — **池子不完整**，两个假阴性撤回（R815）

**新增** `analysis/recheck_ida.py`。

```
pe_strings.txt = 9,316,662 chars 的样本
含 'NIKE'，不含 'NIKE-GS'   ->  但 IDA 在 0x146e11414 找到 'NIKE-GS'
```

**所以 `pe_strings.txt` 是抽样。适合正向下结论（找到＝有），不适合反向（没找到＝没有）。**

### IDA 重查六个

| 模块 | IDA | 结论 |
|---|---|---|
| `bodega` | **1 条 `'Bodega'`** | **有证据（R813 假阴性）** |
| `nike-gs` | **4 条 `'NIKE-GS'`** | **有证据（R813 假阴性）** |
| `bstn` | 0 | 有抓包裁决（§220） |
| `saintalfred` | 0 | **待裁决** |
| `shophmvs` | 0 | **待裁决** |
| `trophyroom` | 0 | **待裁决** |

**五个待裁决 → 三个。**

| 影响 | |
|---|---|
| R813 的「6 个零证据」 | **修正为 3 个** |
| R814 的「1182 slug」 | **下界**（也是池子数的），方向不变 |
| AGENTS.md §2.7 待补 | **先问「来源是全量还是抽样」** |

**纪律**：**一个「按证据删除」的动作，可能删掉证据本身。**
**这次是「动手前先查连带影响」救的两个模块。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R815", BLOCKER)
    ensure(RSTATUS, "R815", BLOCKER)
    ensure(RVERDICT, "第 815 轮", VERDICT)
    ensure(BACKLOG, "R815", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R815"), (RSTATUS, "R815"), (RVERDICT, "第 815 轮"), (BACKLOG, "R815")):
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
         "R815: the string pool is a sample, and two of the five zero-evidence modules do have evidence\n\n"
         "R813 concluded six modules had no image evidence, searching analysis/pe_strings.txt for the id and every\n"
         "domain under six forms. I was about to delete the unsupported ones. Checking the blast radius first turned up\n"
         "a comment in NikeHeaders.cs recording NIKE-GS at a hexadecimal address, and IDA confirms the literal is in\n"
         "the image at 0x146e11414.\n\n"
         "So the pool is incomplete. It runs to 9.3 million characters, contains NIKE, and does not contain NIKE-GS.\n"
         "That makes it a sample rather than an inventory, and it collapses the distinction R813 depended on: not\n"
         "present in the pool is not the same as not present in the image, and I had treated them as one thing for\n"
         "two rounds.\n\n"
         "Re-checking all six with IDA changes the answer for two of them. bodega has 'Bodega' and nike-gs has\n"
         "'NIKE-GS' four times, so both were false negatives. bstn, saintalfred, shophmvs and trophyroom return\n"
         "nothing, and of those bstn already carries the R220 ruling that keeps it on capture evidence. That leaves\n"
         "three genuinely unsupported, not five.\n\n"
         "The near miss is worth more than the correction. Deleting five would have removed two modules the image\n"
         "actually contains, and nothing would have complained: the suite counts 63 and would simply have started\n"
         "counting 58, a number the deletion was going to change anyway. An action taken on evidence can destroy the\n"
         "evidence, and the only reason it did not was the habit of checking the blast radius before editing.\n\n"
         "The pool's standing has to change to match. It is good for positive leads -- a hit means present -- and\n"
         "unusable for negatives. Section 2.1 lists it as trustworthy without that qualification; the missing sentence\n"
         "is that it is a sample and reverse conclusions need IDA's own search. R814's 1182 slugs came from the same\n"
         "pool, so that figure is a lower bound, though the direction survives: it still far exceeds thirty-three.\n\n"
         "Unknown: how pe_strings.txt was exported and what its sampling rule is, which is why its gaps cannot be\n"
         "predicted; whether saintalfred, shophmvs and trophyroom should be deleted now that IDA also returns nothing\n"
         "for them; and how far the slug count is understated.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
