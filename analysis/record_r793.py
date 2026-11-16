"""Record R793: three stores exempted with evidence, one lying label, one unexplained metric failure."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 219. 三家带证据进豁免；顺带改掉一个**撒谎的标签**

> R793。`ModuleCoverageTests.cs`：`YardstickDoesNotApply` 从 2 条加到 5 条；改正标签文案。

### 一、三家到底是什么形状（Observation）

| 站 | 证据 |
|---|---|
| **goat** | `www.goat.com/api/v1/drops/get-user-drops` · `drops/submit-drop-captcha` · **`order-reservation/build-reservation`** · `order-reservation/get-reservation-status`；UA 是 `GOAT/2.104.1 (iPhone; iOS 26.6; Scale/3.00)` |
| **popmart** | `PopMartHandler` · `PopMartRpcHandler` · `PopMartBrowser` · `$PopMartProductType` · `/web/v2?partner=popmart&appKey=` · `POPMART-RESERVATION` · `PopMart-Tax-All` |
| **superswipe** | `enter.superswipe.com/enter` · `captcha.superswipe.com` · `status.superswipe.com` · `data-superswipe-launch-id` · `_superswipe_launch_id_` · `.superswipe.app/youwillnevergetthis/fingerprint` |

**三家都不是"七步结账"**：

- **goat**：drop + **订单预留**（`build-reservation` / `get-reservation-status`）
- **popmart**：**自有整套栈**（Handler + RpcHandler + Browser）跑 **RPC + 预留**
- **superswipe**：**launch/enter 平台**，自己一套 captcha，有 launch id

### 二、所以进豁免，但理由与前两家不同

`fanatics` / `yeezysupply` 是**「镜像里没有结账面」**；
这三家是**「面是另一种形状」** —— **都在镜像里，只是没有购物车/运费/支付这些步。**

**豁免的名字叫 `YardstickDoesNotApply`，两种情况都符合。**

**必须说清代价**：分母从 61 降到 58，`fully covered` **仍是 50** ——
**这不是覆盖率上升，是分母变化。** 两者要分开看。

### 三、改掉一个撒谎的标签

豁免行的标签原来是 `(not in the image — see the exemption table)`。

**对 fanatics/yeezysupply 是对的，对这三家是错的** —— 它们在镜像里，形状不同而已。
**改成 `(yardstick does not apply — see the exemption table)`。**

**这是 §2.7 那一类错误的又一次**：标签说「镜像里没有」，读的人就会以为没有。
**我上一轮（R780）刚因为把字段名当端点栽过一次，这次是标签的措辞问题 —— 同一类，不同面。**

### 四、结果

```
resolved 63/63 flows; fully covered 50; exempt 5
goat / popmart / superswipe   71%   (yardstick does not apply — see the exemption table)
```

### 五、一次**查不出原因**的度量失败，如实记下

第一次跑 `metrics_report.py`：**`成员形状差异 exit 1`**，堆栈：

```
File "tools\\shape_audit.py", line 32, in <module>
    if text[i] == '{': depth += 1
TypeError: string indices must be integers, not 're.Match'
```

**但是**：

- **直接跑 `python tools\\shape_audit.py` → 正常，`total mismatches: 78`**
- **复跑 `metrics_report.py --skip-tests` → `exit 0 / 78`**

**所以是一次性失败，原因未查明。** 我看了那一带的代码（`text` 确实是字符串，`i` 来自 `range`），
**没有找到能让 `i` 变成 `Match` 的路径。**

**按项目纪律，这种要单列，不混进"通过"也不混进"失败"。** 若再出现，第一件事是
**把当时的工作树快照与 `shape_audit.py` 的字节一起留下**，否则下次还是查不出。

### 六、验证

```
构建                未改产品代码
ModuleCoverageTests resolved 63/63 · fully covered 50 · exempt 5
完整套件            1766 通过 / 0 失败 / 0 跳过
四项度量            4 / 0 / 17 / 78 / 0（复跑后）
```

### 七、仍然 Unknown

- **三家各自的真实流程**：**形状已知，步骤未取** —— goat 的 `build-reservation` 请求体、
  popmart 的 `/web/v2` RPC 协议、superswipe 的 enter 流程，**都还没读**。
- **`shape_audit.py` 那次失败的成因**：**Unknown**（第五节）。
- **`bstn`**：镜像里 0 字符串，仍是"复刻件多出来的模块"，未裁决。
"""

VERDICT = """

---

## 第 793 轮：三家带证据进豁免，并改掉一个撒谎的标签

### 三家的形状（都在镜像里，但都不是七步结账）

| 站 | 证据 |
|---|---|
| goat | `drops/{get-user-drops, submit-drop-captcha}` + **`order-reservation/{build,get-status}`**；UA `GOAT/2.104.1 (iPhone)` |
| popmart | **`PopMartHandler` / `PopMartRpcHandler` / `PopMartBrowser`** + `/web/v2?partner=popmart&appKey=` + `POPMART-RESERVATION` |
| superswipe | `enter.superswipe.com/enter` + 自有 captcha + `data-superswipe-launch-id` |

**goat = drop + 预留；popmart = 自有栈跑 RPC + 预留；superswipe = launch/enter 平台。**

### 进豁免，理由与前两家不同

`fanatics`/`yeezysupply` 是**「没有结账面」**；这三家是**「面是另一种形状」**。

> **代价说清：分母 61 → 58，`fully covered` 仍 50 —— 这不是覆盖率上升，是分母变化。**

### 改掉一个撒谎的标签

原来写 `(not in the image — …)`。**对前两家属实，对这三家是错的。**
改成 `(yardstick does not apply — …)`。

**§2.7 那一类：标签说「镜像里没有」，读的人就会以为没有。**

### 一次查不出原因的度量失败

`成员形状差异 exit 1`，`shape_audit.py:32 TypeError`（`i` 是 `Match`）。

**直接跑正常（78），复跑度量也正常（exit 0）。**
**我看了代码，没找到能让 `i` 变成 `Match` 的路径 —— 成因 Unknown。**

**单列，不混进「通过」也不混进「失败」。再出现时先把工作树快照与该文件字节留下。**

### 验证

```
resolved 63/63 · fully covered 50 · exempt 5 · 整套 1766 / 0 · 度量 4 / 0 / 17 / 78 / 0
```
"""

BACKLOG_ADD = """

## 覆盖 — 豁免从 2 增到 5（R793）

```
resolved 63/63 · fully covered 50 · exempt 5
```

**新增三条，理由都是「面是另一种形状」，不是「没找到」**：

| 站 | 形状 | 关键证据 |
|---|---|---|
| goat | drop + **订单预留** | `order-reservation/build-reservation` · `get-reservation-status` |
| popmart | **自有栈 + RPC + 预留** | `PopMartHandler`/`PopMartRpcHandler`/`PopMartBrowser` · `/web/v2?partner=popmart` |
| superswipe | **launch/enter 平台** | `enter.superswipe.com/enter` · `data-superswipe-launch-id` |

**口径提醒**：分母 61 → 58，`fully covered` 仍 50。
**这不是覆盖率上升，是分母变化 —— 两个数要分开读。**

| 仍待做 | |
|---|---|
| goat 的 `build-reservation` 请求体 | 未读 |
| popmart 的 `/web/v2` RPC 协议 | 未读 |
| superswipe 的 enter 流程 | 未读 |
| `bstn`（镜像 0 字符串） | 未裁决 |
| `shape_audit.py` 那次失败的成因 | **Unknown**，单列为偶发 |

**标签纪律**：豁免行原来写 `(not in the image …)`，对「没有结账面」属实、对「形状不同」是撒谎。
**已改成 `(yardstick does not apply …)`。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R793", BLOCKER)
    ensure(RSTATUS, "R793", BLOCKER)
    ensure(RVERDICT, "第 793 轮", VERDICT)
    ensure(BACKLOG, "R793", BACKLOG_ADD)

    ok = True
    for path in (RBLOCK, RSTATUS, RVERDICT, BACKLOG):
        body = io.open(path, encoding="utf-8").read()
        key = "第 793 轮" if path == RVERDICT else "R793"
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R793: goat, popmart and superswipe are exempted on evidence, and a label that lied is corrected\n\n"
         "All three are in the image; none is a seven-step checkout. goat carries drops/get-user-drops,\n"
         "drops/submit-drop-captcha and order-reservation/{build-reservation,get-reservation-status} under an iOS user\n"
         "agent, which is a drop with a held reservation. popmart carries PopMartHandler, PopMartRpcHandler and\n"
         "PopMartBrowser, an RPC endpoint at /web/v2?partner=popmart&appKey=, and POPMART-RESERVATION -- its own stack\n"
         "over RPC. superswipe is a launch entry: enter.superswipe.com/enter, launch ids in the DOM and storage, and its\n"
         "own captcha host.\n\n"
         "So they join YardstickDoesNotApply, on different grounds from fanatics and yeezysupply. Those two have no\n"
         "checkout surface at all; these three have a surface of another shape. The exemption's name covers both,\n"
         "which is why it was chosen, but the reasons are stored per store rather than generalised.\n\n"
         "The cost has to be said plainly: the denominator falls from 61 to 58 while fully covered stays at 50. That is\n"
         "not coverage rising, it is the denominator changing, and the two numbers must be read separately.\n\n"
         "The exemption row's label said 'not in the image', which was true of the first two and false of these three.\n"
         "It now says 'yardstick does not apply'. A label that states the wrong reason is worse than no label, because\n"
         "it tells the reader something untrue about the evidence -- the same family of error as R780, where a field\n"
         "name was read as an endpoint.\n\n"
         "One metric failure I could not explain and have not smoothed over. The first metrics run reported shape_audit\n"
         "exiting 1 with a TypeError at line 32, where the loop index appeared to be a re.Match. Running the tool\n"
         "directly gives the normal 78, and re-running the metrics gives exit 0. Reading that stretch of code shows\n"
         "text is a string and i comes from range, with no path that makes i a Match. So it is recorded as a one-off of\n"
         "unknown cause, kept out of both the pass and the fail columns. If it recurs, the first move is to preserve a\n"
         "working-tree snapshot and that file's bytes, because otherwise the next investigation will fail the same way.\n\n"
         "Suite 1766 pass / 0 fail; four metrics 4 / 0 / 17 / 78 / 0 after the rerun."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
