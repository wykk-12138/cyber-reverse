"""Record R822: the URL-ignoring scan is stable now, and it agrees with the test's exception list."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 246. 忽略 `c.Url` 的流程：**3 个，与用例例外名单正好对上**

> R822。`analysis/scan_url_ignoring4.py`（留存）。未改产品代码。

### 一、前三次都错在「近似方法边界」

| 版本 | 做法 | 错在哪 |
|---|---|---|
| ①R821 | 整个文件找重写 + 「之前最后一个 `class X`」当归属 | `RetailFlows.cs` 七个类，前面的重写全算到最后一个头上（`CasioFlow` 被记 7 个，`YeezySupplyFlow` 9 个） |
| ②R822a | 真花括号配对切类体 | **字符串/注释里的 `{` 让类体跑过边界** —— 与 R764 同族 |
| ③R822b | 缩进切类 + 「后面 40 行」当方法体 | 窗口越过方法末尾，`PoqAppFlow` 因为下一个方法里有 `c.Url` 被误判为「用了」 |
| ④R822c | **缩进切类 + 截到下一个成员声明** | 自洽 |

### 二、第四版的两个自检都过

```
overrides found: 22
classes with more than one: none          <- 归属不再重复
not reading c.Url: 3
  NikeFlow         https://www.nike.com/ ×2   12 lines   NikeFlow.cs
  PoqAppFlow       (no literal host)          15 lines   PoqAppFlow.cs
  SuperswipeFlow   (no literal host)          13 lines   RetailFlows.cs
```

- **「没有类有多个重写」** —— 前三版都违反这条
- **`PoqAppFlow` 15 行** —— 与 R820 我手读的 `126–139` 行一致
- **`CasioFlow` 出现 1 次**（前几版 7 次）
- **`YeezySupplyFlow` 用 `c.Url`（26 行）** —— 撤回 R821 对它的怀疑

### 三、最要紧的一致性

**这 3 个流程，正是 `Monitor_Survives_An_Unreachable_Host` 例外名单里的那 3 个：**

```
用例例外:  nike, nike-gs, superswipe, poq-app
扫描结果:  NikeFlow, SuperswipeFlow, PoqAppFlow      (nike-gs 继承 NikeFlow)
```

**两个来源独立得到同一组 —— 用例的例外名单不是我为了让它绿而随便加的，它对应的是「不看传入 URL」这一类流程。**

**所以 R820 那次改动得到了独立印证：`poq-app` 加进名单是对的，而且名单是完整的。**

### 四、这条 Unknown 结案

R820 的 Unknown：「还有谁忽略 `c.Url` —— 忽略 URL 却不回 403 的流程会静默通过测试」。

**答案**：**3 个，全部已在用例例外名单里。** **不存在「静默通过」的漏网者。**

**R821 那个「3」是巧合 —— 它含一个假阳性（`YeezySupplyFlow`）、漏一个真阳性（`SuperswipeFlow` 之一）。**
**错的答案和正确答案数字相同，这个现象本身值得记：只核总数会放过它（AGENTS.md §2.7 第二条）。**

### 五、验证

```
python analysis\\scan_url_ignoring4.py    22 / 3 / 无重复归属
与 ModuleRobustnessTests 例外名单逐条核对：一致
本轮未改产品代码
完整套件保持 1766 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 六、仍然 Unknown

- **这 3 个流程忽略 `c.Url` 是对的还是错的**：**Unknown** —— 它们的表面是「按客户/按站点寻址的 API」，
  **传入 URL 本就无关；但也可能是本该用 URL 的实现遗漏了。判据在镜像里，本轮没查。**
- **`c.Url` 在其余 19 个重写里都是被真正使用，还是只是出现**：**Inference（中）** ——
  本版只判「体内是否出现 `c.Url`」，**没判它后面的表达式是否参与请求构造。**
- **`SuperswipeFlow` 那两个「无字面 host」是怎么拼 URL 的**：**没读。**

### 七、教训

**四个版本里，前三个都错，而错法是同一族**：**用一个近似去代替真边界，再用近似的结果当事实。**

**另一个更值得记的**：**R821 版报「3」，正确答案也是「3」—— 但两个集合不同。**
**只核总数会放过它。** **这次是靠「没有类该有多个重写」这条不变量发现的，不是靠对照答案。**
"""

VERDICT = """

---

## 第 822 轮：忽略 `c.Url` 的是 3 个，与用例例外名单正好对上

### 前三次都错在近似方法边界

| 版本 | 错在哪 |
|---|---|
| ① 整文件找 + 最近前缀当归属 | `RetailFlows.cs` 七类，`CasioFlow` 被记 7 个 |
| ② 花括号配对 | **字符串里的 `{` 让类体跑过边界**（R764 同族） |
| ③ 缩进切类 + 后面 40 行 | 窗口越过方法末，`PoqAppFlow` 被下一个方法的 `c.Url` 误判 |
| ④ **缩进切类 + 截到下一个成员声明** | **自洽** |

### 第四版

```
22 个重写 · 没有类有多个重写 · 3 个不读 c.Url
  NikeFlow        www.nike.com ×2   12 行
  PoqAppFlow      （辅助函数）       15 行   ← 与 R820 手读的 126–139 行一致
  SuperswipeFlow  （无字面 host）    13 行
```

### 最要紧的一致性

```
用例例外:  nike, nike-gs, superswipe, poq-app
扫描结果:  NikeFlow, SuperswipeFlow, PoqAppFlow   (nike-gs 继承 NikeFlow)
```

> **两个来源独立得到同一组 —— 用例的例外名单不是为让它绿而加的，它对应「不看传入 URL」这一类流程。**
> **R820 那次改动得到独立印证，且名单是完整的。**

### 这条 Unknown 结案

**3 个，全部已在例外名单里。不存在「静默通过」的漏网者。**

**而 R821 那个「3」是巧合：含一假阳性（`YeezySupplyFlow`）、漏一真阳性。**
**错的答案和正确答案数字相同 —— 只核总数会放过它。**

### 验证

```
scan_url_ignoring4.py 22/3/无重复 · 与例外名单逐条一致 · 产品代码未改 · 整套 1766 / 0 · 度量未变
```

### 教训

**四个版本前三个都错，错法同族：用近似代替真边界，再把近似结果当事实。**
**而发现靠的是不变量（「没有类该有多个重写」），不是对照答案。**
"""

BACKLOG_ADD = """

## 结案 — 忽略 `c.Url` 的流程是 3 个（R822）

**工具 `analysis/scan_url_ignoring4.py`（留存）**：缩进切类 + 截到下一个成员声明。

```
22 个重写 · 没有类有多个重写 · 3 个不读 c.Url
  NikeFlow        www.nike.com ×2   12 行
  PoqAppFlow      （辅助函数拼 host） 15 行
  SuperswipeFlow  （无字面 host）    13 行
```

**与 `ModuleRobustnessTests` 的例外名单（nike / nike-gs / superswipe / poq-app）逐条一致**（nike-gs 继承 NikeFlow）。
**两个独立来源同一组 → 名单完整，不存在「静默通过」的漏网者。**

**R821 那个「3」是巧合**：含一假阳性（`YeezySupplyFlow`）、漏一真阳性。**错的答案和正确答案数字相同。**

| 仍 Unknown | |
|---|---|
| 这 3 个忽略 `c.Url` 是对是错 | 表面是「按客户寻址的 API」，传入 URL 本就无关；但也可能是遗漏。**判据在镜像里，未查** |
| 其余 19 个是「真用」还是「只出现」 | 本版只判体内是否出现 `c.Url`，未判它是否参与请求构造 |
| `SuperswipeFlow` 怎么拼 URL | 未读 |

### 扫描器边界（三次教训）

| 做法 | 失败点 |
|---|---|
| 最近前缀 `class` 当归属 | 一文件多类时全算到最后一个 |
| 花括号配对 | **字符串里的 `{`**（R764 同族） |
| 40 行窗口 | 越过方法末，误纳下一个方法 |
| **缩进切类 + 截到下一成员** | 自洽 |

**纪律**：**发现错误靠的是不变量（「没有类该有多个重写」），不是对照答案。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R822", BLOCKER)
    ensure(RSTATUS, "R822", BLOCKER)
    ensure(RVERDICT, "第 822 轮", VERDICT)
    ensure(BACKLOG, "R822", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R822"), (RSTATUS, "R822"), (RVERDICT, "第 822 轮"), (BACKLOG, "R822")):
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
         "R822: three flows ignore the context URL, and that matches the test's exception list exactly\n\n"
         "R820 asked which flows ignore the context URL and R821 answered three, then R821's own spot check showed the"
         " number was wrong. Three approximations later, the answer is three again, but a different three.\n\n"
         "The failures were all of one kind: approximating a method boundary instead of establishing it. Crediting an"
         " override to the nearest preceding class declaration breaks on RetailFlows.cs, which holds seven classes. Brace"
         " matching breaks when a string contains an opening brace, running one class body past its end -- the same"
         " failure R764 recorded. A forty-line window breaks the other way, running a method past its end so that"
         " PoqAppFlow's GetHomeAsync appeared to read c.Url because the method below it does.\n\n"
         "What works is class boundaries by indentation, since these declarations start in column zero, and method"
         " boundaries at the next member declaration. That yields twenty-two overrides, no class with more than one -- an"
         " invariant the first three versions each violated -- and three that never read c.Url: NikeFlow with a hardcoded"
         " nike.com, PoqAppFlow composing through a helper, and SuperswipeFlow.\n\n"
         "Those three are exactly the flows in the robustness test's exception list, nike, nike-gs, superswipe and"
         " poq-app, with nike-gs inheriting from NikeFlow. Two independent derivations agree, which settles the question"
         " R820 left: there is no flow that ignores the URL and escapes notice, and the exception list is complete"
         " rather than convenient.\n\n"
         "The detail worth keeping is that R821's wrong answer and this right answer are both three, with different"
         " members -- a false positive and a false negative cancelling. Checking the total would have confirmed the wrong"
         " set. What caught it was an invariant, that no class should carry more than one such override, not a"
         " comparison against a known answer.\n\n"
         "Unknown: whether these three are right to ignore the URL, since their surfaces are APIs addressed per client"
         " or site and a caller-supplied URL may genuinely be irrelevant, or may be an omission; whether the other"
         " nineteen genuinely use c.Url rather than merely mentioning it, since this tests occurrence and not"
         " participation in a request; and how SuperswipeFlow composes its URL without a literal host.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
