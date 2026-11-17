"""Record R1037: freshness at zero, and the withdrawal cost forty-three functions."""

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
### 陈旧度归零；而「停止假装」真的少了 **43** 个函数（R1037）

**R1036 说下一轮 publish 让陈旧度归零。做了，而它给出一个比文档改动更硬的数字。**

### ① 产物与源码同步

```
产物陈旧度（.publish-aot vs src）: 0 文件 / 0 行
```

**→ 那让完成判据 (c)「产物级对照可复算」**第一次成立**：
函数数量那一行现在来自**与源码同步**的产物，而不是来自一个陈旧的快照。****

**→ 而那是 R932 那条的正面：当时记录过「函数比例来自 `.publish-aot`，而那个产物可能陈旧」——
现在它是新的。**

### ② 而函数数从 174,336 掉到 **174,293**（−43）

**→ 那 −43 不是噪声，是 Farfetch 停止发请求的**产物后果**：**

| 原来 | 现在 |
|---|---|
| 7 个步骤各发请求，带 payload 构造、`TryRead` 调用链、`JObject`、`Regex` 等 | 7 个 `return Fail(...)` |
| 那些 helper 因此**被引用** | **不再被引用** ⇒ 被 NativeAOT trim（R963 的机制） |

**→ 所以「停止假装」不只是把注释改成报告 —— 它真的让 43 个只为那 7 条请求存在的函数消失。
→ 而比例 62.91% → **62.89%**。**

**→ 那是一个**方向正确但是减法**的变化：goal 要「函数数量对等」，
→ 而**删掉无据代码**让数量**离原版更远** —— 因为原版**有**那些函数（它真的有 Farfetch 的结账实现？）**

### ③ 而这里有一个真问题，而它必须写清

**`farfetch.com` 在镜像里 0 次** —— 那证明**原版的字符串池里没有这个域名**。
→ 但那**不能**证明原版没有 Farfetch 的流程：
→ 域名可能来自**配置文件**（原版有 `stores.json` 之类），而配置**不在 exe 的字符串池里**。

**→ 所以 R1036 的结论「整个站不在镜像里」有一个**未检验的前提**：
「站点的域名一定以字面量出现在 exe 里」。
→ 而 R1021 的 imperva 用同一个前提，而那次它的证据是**多重**的（六拼写 + 台账 + 无 solver 文案）。
→ **而 Farfetch 只有单重证据（域名 0）。**

**→ 所以本轮要把那 43 个函数的减少**作为证据**记下来：它同时是「停止假装」的代价，
和「我们可能删多了」的提示。→ 标 **Unknown**，不写成定论。**

### ④ 而那个前提该怎么检验（下一轮）

**查一个**已知存在**的站的域名是否在镜像里：**

| 若 | 则 |
|---|---|
| 已知存在的站（如 `nike.com`）域名在镜像里 | 域名可见 ⇒ Farfetch 的 0 是强证据 |
| 已知存在的站域名也 0 | **域名不可见** ⇒ Farfetch 的 0 什么也不证明，得撤回 |

**→ 而那是一次查询就能定的对照，而它正是 R1016 那条「判据有定义域」该问的问题。**

### ⑤ 数字

| 度量 | R1036 | **R1037** |
|---|---|---|
| 套件 | 2252 / 0 | **2252 / 0 / 0** |
| **产物陈旧度** | 6 / 5,669 | **0 / 0** |
| **函数数（replica）** | 174,336 | **174,293（−43）** |
| **函数数比例** | 62.91% | **62.89%** |
| **产物与源码同步** | **否** | **是（首次）** |
| **publish** | 未做 | **exit 0（仅既有 AOT 裁剪警告）** |
| **`farfetch.com` = 0 的证明力** | 当作决定性 | **存疑 —— 有未检验前提** |

### 教训

> **陈旧度归零是本轮最简单的部分；而它顺手给出的 −43 让上一轮的结论露了一个口子。**
> **→ 我上一轮把「域名 0 次」当作「站不存在」的决定性证据，而那依赖一个我没检验的前提：
> 站点域名一定以字面量出现在 exe 里。**
> **→ 而反例很容易找（配置驱动的站名），所以那不是吹毛求疵 —— 那是 R1016 那条的又一次：
> 先问这个判据的定义域，再相信它的零。**
"""

if "「停止假装」真的少了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

VERDICT = """

---

## 第 1037 轮：陈旧度归零；而「停止假装」真的少了 43 个函数

### ① 产物与源码同步 —— (c) 第一次成立

```
产物陈旧度（.publish-aot vs src）: 0 文件 / 0 行
```

**→ 函数数量那一行现在来自**与源码同步**的产物，不再是陈旧快照。
→ 那是 R932 那条的正面：当时记录「比例来自 `.publish-aot`，而它可能陈旧」。**

### ② 而函数数 174,336 → **174,293**（−43）

| 原来 | 现在 |
|---|---|
| 7 个步骤各发请求，带 payload 构造、`TryRead` 链、`JObject`、`Regex` | 7 个 `return Fail(...)` |
| 那些 helper **被引用** | **不再被引用** ⇒ NativeAOT trim（R963 机制） |

**→ 「停止假装」不只是注释改动 —— 43 个只为那 7 条请求存在的函数真的消失了。
→ 比例 62.91% → **62.89%**。**

### ③ 而它让上一轮的结论露了一个口子

**「`farfetch.com` 在镜像里 0 次」只证明**字符串池里没有这个域名**。
→ 它**不能**证明原版没有 Farfetch 的流程：域名可能来自**配置文件**，而配置不在 exe 的字符串池里。**

**→ 所以 R1036 的「整个站不在镜像里」有一个**未检验的前提**：
「站点域名一定以字面量出现在 exe 里」。
→ imperva 那次证据是**多重**的（六拼写 + 台账 + 无 solver 文案），而 Farfetch 只有单重。**
**→ 所以那 −43 同时是「停止假装」的代价和「可能删多了」的提示 ⇒ 标 Unknown。**

### ④ 下一轮：一次查询就能定的对照

**查一个**已知存在**的站（如 `nike.com`）域名是否在镜像里：**

| 若 | 则 |
|---|---|
| 在 | 域名可见 ⇒ Farfetch 的 0 是强证据 |
| 也 0 | **域名不可见** ⇒ Farfetch 的 0 什么也不证明，得撤回 |

### ⑤ 数字

| 度量 | R1036 | **R1037** |
|---|---|---|
| 套件 | 2252 / 0 | **2252 / 0 / 0** |
| **产物陈旧度** | 6 / 5,669 | **0 / 0** |
| **函数数（replica）** | 174,336 | **174,293（−43）** |
| **比例** | 62.91% | **62.89%** |
| **产物与源码同步** | **否** | **是（首次）** |
| **`farfetch.com` = 0 的证明力** | 当作决定性 | **存疑** |

### 教训

> **陈旧度归零是最简单的部分；而它顺手给出的 −43 让上一轮的结论露了一个口子。
> → 我把「域名 0 次」当作「站不存在」的决定性证据，而那依赖一个我没检验的前提。
> → 反例很容易找（配置驱动的站名），所以那不是吹毛求疵 ——
> 那是 R1016 那条的又一次：**先问这个判据的定义域，再相信它的零。****
"""

BACKLOG_ADD = """

## 判据 (c) — **陈旧度 0/0；(c) 首次成立；而 −43 个函数让 R1036 的结论存疑**（R1037）

### publish + 轮转

```
dotnet publish src/Cybersole.Ui -c Release -r win-x64 -p:PublishAot=true -p:UseSharedCompilation=false -m:1 -o .publish-aot-new
→ exit 0（仅既有 Jint/System.Data AOT 裁剪警告）
轮转：.publish-aot-prev 删除 · .publish-aot → prev · new → .publish-aot
```

**陈旧度 6 / 5,669 → **0 / 0** ⇒ (c)「产物级对照可复算」第一次成立。**

### 而函数数 −43

**174,336 → 174,293**（比例 62.91% → 62.89%）。
**→ 7 个步骤不再发请求 ⇒ 只为它们存在的 helper 不再被引用 ⇒ NativeAOT trim（R963）。**
**→ 「停止假装」真的少了 43 个函数，而不只是改注释。**

### 而它让 R1036 的结论存疑

**「`farfetch.com` 0 次」只证明**字符串池没有这个域名**。
→ 域名可能来自**配置**，而配置不在 exe 字符串池 ⇒ **前提未检验**。
→ imperva 那次是**多重**证据；Farfetch 只有单重 ⇒ 标 **Unknown**。**

### 下一轮的对照（一次查询）

**查 `nike.com` 之类的**已知存在**站域名是否在镜像里：在 ⇒ 域名可见（Farfetch 的 0 是强证据）；
也 0 ⇒ 域名不可见（**R1036 需撤回**）。**

### 数字

**套件 2252/0/0 · 陈旧度 6/5,669 → **0/0** · 函数数 174,336 → **174,293** · 比例 62.91% → 62.89%**

| 仍 Unknown / 待 YG | |
|---|---|
| 域名是否一定在字符串池里 | **待对照** |
| `FarfetchFlow` 去留 | **待 YG**（与上面那条耦合） |

**纪律**：先问判据的定义域，再相信它的零。
"""

BLOCKER = """

---

## 461. **陈旧度归零；(c) 首次成立；而 −43 个函数让 R1036 的结论存疑**

> R1037。**publish + 轮转三个目录。** 套件 **2252 通过 / 0 失败 / 0 跳过**。

### 一、产物与源码同步

```
dotnet publish src\\Cybersole.Ui -c Release -r win-x64 -p:PublishAot=true -p:UseSharedCompilation=false -m:1 -o .publish-aot-new
→ exit 0（仅既有 Jint / System.Data 的 AOT 裁剪警告）
轮转：删除旧 prev · .publish-aot → .publish-aot-prev · .publish-aot-new → .publish-aot

产物陈旧度（.publish-aot vs src）: 0 文件 / 0 行
```

**→ 那让完成判据 (c)「产物级对照可复算」**第一次成立**：
  函数数量那一行现在来自**与源码同步**的产物，而不是来自一个陈旧的快照。**

### 二、而函数数从 174,336 掉到 **174,293**（−43）

| 原来 | 现在 |
|---|---|
| 7 个步骤各发请求，带 payload 构造、`TryRead` 调用链、`JObject`、`Regex` 等 | 7 个 `return Fail(...)` |
| 那些 helper 因此**被引用** | **不再被引用** ⇒ 被 NativeAOT trim（R963 的机制） |

**→ 所以「停止假装」不只是把注释改成报告 —— 它真的让 43 个只为那 7 条请求存在的函数消失。
→ 而比例 62.91% → **62.89%**。**

### 三、而这里有一个真问题，必须写清

**`farfetch.com` 在镜像里 0 次** —— 那证明**原版的字符串池里没有这个域名**。
→ 但那**不能**证明原版没有 Farfetch 的流程：
→ 域名可能来自**配置文件**（原版有 `stores.json` 之类），而配置**不在 exe 的字符串池里**。

**→ 所以 R1036 的结论「整个站不在镜像里」有一个**未检验的前提**：
  「站点的域名一定以字面量出现在 exe 里」。

**→ 而 R1021 的 imperva 用同一个前提，而那次它的证据是**多重**的
  （六拼写 + 台账 + 无 solver 文案）；而 Farfetch 只有单重证据（域名 0）。**

**→ 所以本轮要把那 43 个函数的减少**作为证据**记下来：它同时是「停止假装」的代价，
  和「我们可能删多了」的提示。→ 标 **Unknown**，不写成定论。**

### 四、而那个前提该怎么检验（下一轮）

**查一个**已知存在**的站的域名是否在镜像里：**

| 若 | 则 |
|---|---|
| 已知存在的站（如 `nike.com`）域名在镜像里 | 域名可见 ⇒ Farfetch 的 0 是强证据 |
| 已知存在的站域名也 0 | **域名不可见** ⇒ Farfetch 的 0 什么也不证明，得撤回 |

**→ 而那是一次查询就能定的对照，而它正是 R1016 那条「判据有定义域」该问的问题。**

### 五、数字

| 度量 | R1036 | R1037 |
|---|---|---|
| 套件 | 2252 / 0 | **2252 / 0 / 0** |
| **产物陈旧度** | 6 / 5,669 | **0 / 0** |
| **函数数（replica）** | 174,336 | **174,293（−43）** |
| **函数数比例** | 62.91% | **62.89%** |
| **产物与源码同步** | **否** | **是（首次）** |
| **publish** | 未做 | **exit 0** |
| **`farfetch.com` = 0 的证明力** | 当作决定性 | **存疑 —— 有未检验前提** |

### 六、验证

```
cd D:\\projects\\cyber-reverse\\replica
Get-ChildItem -Directory -Filter ".publish-aot*"   -> .publish-aot 18:55 · .publish-aot-prev 16:48
python tools/metrics_report.py
  -> 函数数量 exit 0  277,120 / 174,293 / 62.89%
  -> 产物陈旧度 exit 0  0 / 0
  -> 完整套件 exit 0  2252 / 0 / 0
```

### 七、仍然 Unknown / 待 YG

- **站点域名是否一定以字面量出现在 exe 里**：**待下一轮的对照查询**。
- **`FarfetchFlow` 的去留**：**待 YG**，与上一条耦合。

### 八、教训

**陈旧度归零是本轮最简单的部分；而它顺手给出的 −43 让上一轮的结论露了一个口子。**

**→ 我上一轮把「域名 0 次」当作「站不存在」的决定性证据，而那依赖一个我没检验的前提：
  站点域名一定以字面量出现在 exe 里。**

**→ 而反例很容易找（配置驱动的站名），所以那不是吹毛求疵 —— 那是 R1016 那条的又一次：
  先问这个判据的定义域，再相信它的零。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R1037", BLOCKER)
    ensure(RSTATUS, "R1037", BLOCKER)
    ensure(RVERDICT, "第 1037 轮", VERDICT)
    ensure(BACKLOG, "R1037", BACKLOG_ADD)

    note = (
        "\n## R1037 补充 — **陈旧度 0/0；(c) 首次成立；而 −43 个函数让 R1036 的结论存疑**（套件 2252）\n\n"
        "**publish + 轮转**：`dotnet publish src/Cybersole.Ui -c Release -r win-x64 -p:PublishAot=true ...` → exit 0\n"
        "（仅既有 Jint/System.Data 裁剪警告）⇒ **产物陈旧度 6/5,669 → 0/0** ⇒ (c) 第一次成立。\n\n"
        "**而函数数 174,336 → 174,293（−43）**，比例 62.91% → 62.89%。\n"
        "→ 7 个步骤不再发请求 ⇒ 只为它们存在的 helper 不再被引用 ⇒ NativeAOT trim（R963）。\n"
        "→ **「停止假装」真的少了 43 个函数，不只是改注释。**\n\n"
        "**而那 −43 让 R1036 的结论露了一个口子**：\n"
        "「`farfetch.com` 0 次」只证明**字符串池**没有这个域名；域名可能来自**配置**，而配置不在 exe 字符串池。\n"
        "→ 所以「整个站不在镜像里」依赖一个**未检验的前提**：「站点域名一定以字面量出现在 exe 里」。\n"
        "→ imperva 那次是**多重**证据（六拼写 + 台账 + 无 solver 文案）；Farfetch 只有单重 ⇒ 标 **Unknown**。\n\n"
        "**下一轮的对照（一次查询）**：查 `nike.com` 之类的**已知存在**站域名是否在镜像里 ——\n"
        "在 ⇒ 域名可见（Farfetch 的 0 是强证据）；也 0 ⇒ 域名不可见（**R1036 需撤回**）。\n\n"
        "数字：套件 2252/0/0 · 陈旧度 **0/0** · 函数数 **174,293** · 比例 **62.89%** · 产物与源码同步 **是**。\n\n"
        "纪律：**先问判据的定义域，再相信它的零。**\n\n"
        "下一轮：做那个对照查询；它决定 Farfetch 的处置是否要撤回。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R1037" not in h:
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
             for p, k in ((RBLOCK, "R1037"), (RSTATUS, "R1037"), (RVERDICT, "第 1037 轮"), (BACKLOG, "R1037")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R1037: freshness at zero, and the withdrawal cost forty-three functions\n\n"
         "R1036 closed by asking for a publish. Done, and the artifact now matches the source for the first time --\n"
         " freshness at zero files and zero lines, which is what makes the completion criterion about comparing the\n"
         " artifact against the original actually computable rather than computed against a stale snapshot.\n\n"
         "The publish also priced the previous round. Function count fell from 174,336 to 174,293. Those forty-three were\n"
         " helpers that existed only to serve Farfetch's seven requests -- payload construction, the TryRead chain, the\n"
         " JObject and Regex work -- and with those requests gone nothing referenced them, so NativeAOT trimmed them. So\n"
         " withdrawing the pretence was not a documentation change: forty-three functions really did leave the artifact.\n\n"
         "Which is the good news and the problem at once. The evidence for that withdrawal was farfetch.com appearing\n"
         " zero times in the image, and that establishes something narrower than it looks: the string pool does not\n"
         " contain the domain. It does not establish that the original has no Farfetch flow, because a store's host can\n"
         " come from configuration and configuration is not in the executable's string pool.\n\n"
         "The premise -- that a store's domain is always a literal in the exe -- was never tested. Imperva's absence\n"
         " rested on three independent signals; Farfetch's rests on one. So the forty-three functions are recorded as\n"
         " both the cost of an honest change and a hint that the change may have gone too far.\n\n"
         "A single query settles it next round: look for a domain belonging to a store that certainly exists. If nike.com\n"
         " is there, domains are visible and the zero is strong. If it is not, domains are not visible, the zero proves\n"
         " nothing, and the withdrawal needs reversing.\n\n"
         "Figures: suite 2252 unchanged, freshness zero, count 174,293 for a ratio of 62.89 per cent, and the artifact in\n"
         " step with the source for the first time.\n\n"
         "Unknown: whether domains appear in the pool at all, and whether the flow should exist, which depends on it.\n\n"
         "The lesson is that the simplest part of this round -- the publish -- is what exposed the weakest premise of the\n"
         " last one, and that the question to ask of a zero is what its criterion can see.\n\n"
         "Artifact republished; suite green at 2252."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()