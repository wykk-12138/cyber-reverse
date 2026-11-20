"""R1316 round record: the build IS reproducible; the embedded commit sha caused the belief that it was not."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
BLOCKERS = 'docs/BLOCKERS.md'

ROUND = """
---

## 第 1316 轮：构建其实是可复现的——「不可复现」是**内嵌 git sha** 造成的错觉

- **上一轮那个"说不清的哈希差异"，查清了，而且是个好消息。**
  `.publish-aot-prev` 还留着那个 `dab75acb…`（尺寸同为 61,294,592）。在产物里搜两个提交号：
  ```
  .publish-aot      (bcbee69f…) 含 0acaea82…  ← R1314 的提交
  .publish-aot-prev (dab75acb…) 含 02c69c45…  ← R1313 的提交
  ```
  **SDK 把 `<InformationalVersion>+<sha>` 烘进了程序集**，所以跨提交的两次构建**同尺寸、不同字节是正常的**；
  而同一次 HEAD 下连发两次（上一轮实测）**逐字节相同**。
- **推论一：构建是可复现的。** `tools/artifact_freshness.py` 里 R1211 写下的那句
  「publishing the same unchanged tree twice produced 39e8fd73... and 847757a0..., so this build is not
  reproducible」——**结论错了**，那两次大概率也是跨了提交。已把那整段注释改写成正确的解释。
- **推论二：§4.5 的哈希差分是有效的**，但只在**同一个内嵌提交号**下比较才有效；
  跨提交的哈希差异**没有信息量**。这条比"完全不可信"要精确得多。
- **落码（工具改进，不是文档改口）**：`artifact_freshness.py` 新增 `git_revision()` / `embedded_revision()`，
  报告里多一行：
  ```
  embedded source revision: 828e9290ac98 (is HEAD)
  ```
  它把「产物是不是当前源码建的」从**mtime 猜测**变成**内容事实**。加完第一次跑就抓到真状态：
  当时产物内嵌 `0acaea82…`、HEAD 是 `828e9290…`，而旧版工具报的是 `state: current`——
  **mtime 说"当前"，内容说"上一提交"。**
- 重发布后：`sha256 35f33923…`、`embedded source revision: 828e9290ac98 (is HEAD)`。
  哈希又变了一次，纯粹因为 HEAD 动了——**这本身就是机制的第三次确认**。

### 五要素

- **改了什么**：`replica/tools/artifact_freshness.py`（内嵌提交号读取 + 与 HEAD 比对 + 改写 R1211 的错误注释）；
  `replica/docs/VERDICT.md`、`docs/BLOCKERS.md`、`docs/HANDOFF.md` 记录。
  **未改 `replica/src` 与 `replica/tests`**，故不重跑变异；NativeAOT 重发布；`docs/METRICS.md` 重生成。
- **验证命令与输出**：`python tools/artifact_freshness.py` → 内嵌 `828e9290ac98 (is HEAD)`；
  产物 `61,294,592` 字节 / `35f33923…`；连发两次同源（上一轮）逐字节相同；
  `metrics_report.py` → 全部 exit 0。
- **数字变化**：产物 sha256 变（HEAD 动过，预期内），尺寸不变 61,294,592。
- **证据等级**：Observation —— 两个产物的内嵌提交号、两次同源发布逐字节相同、工具改后首跑报出的不一致。
  **本轮结论推翻 R1211 的既存记载**，理由是可复现的两条实测。
- **还剩什么**：Casio 签名（在下单/支付步骤）；AO 三个 checkout 体；Saucony 六步路径。
"""

BLOCK_UPDATE = """
---

## R1316 · 上一轮那条「产物哈希未解」已结案，结论与本条原写法相反

- **原写法（R1315）**：「两次连发相同，但与上一轮记录不同，未解；哈希差分只读作『可能变了』。」
- **真相**：产物内嵌**构建时的 git 提交 sha**（`<InformationalVersion>+<sha>`）。
  `.publish-aot-prev` 含 `02c69c45…`（R1313 提交），`.publish-aot` 含 `0acaea82…`（R1314 提交）。
  **跨提交构建必然不同字节、尺寸可相同；同一 HEAD 下构建逐字节相同（实测两次）。**
- **修正后的规则**：
  1. **构建是可复现的**——`tools/artifact_freshness.py` 里 R1211「not reproducible」的记载**错误**，已改写。
  2. 哈希差分**有效**，但**必须在同一内嵌提交号下比较**；跨提交的哈希差异不携带信息。
  3. 想知道"产物是不是当前源码建的"，读 `embedded source revision` 那一行，**不要靠 mtime**。
- **已加的工具**：`artifact_freshness.py` 现报告内嵌提交号并与 HEAD 比对；首跑即抓到
  「mtime 说 current、内容说是上一提交」的真实不一致。
"""

POINTER = """
---

## 第 1316 轮

- **构建可复现，"不可复现"是内嵌 git sha 造成的错觉**：产物里含 `<InformationalVersion>+<sha>`。
  跨提交构建同尺寸不同字节属正常；同 HEAD 连发逐字节相同（实测）。
- 已改写 `artifact_freshness.py` 里 R1211 的错误结论，并新增 `embedded source revision` 一行（与 HEAD 比对）。
  工具首跑即抓到「mtime 说 current、内容说上一提交」。
- 重发布后 `sha256 35f33923…`，内嵌 `828e9290ac98 (is HEAD)`。
- §4.5 的哈希差分**仍然有效**，条件是同一内嵌提交号。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1316 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1316 \u8f6e')
append(BLOCKERS, BLOCK_UPDATE, 'R1316 \u00b7 \u4e0a\u4e00\u8f6e\u90a3\u6761')
