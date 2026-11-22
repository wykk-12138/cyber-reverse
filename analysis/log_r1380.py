"""R1380 record: C8 built, and three classifier defects the first runs exposed."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
PARITY = 'docs/PARITY_CLAIMS.md'

ROUND = """
---

## 第 1380 轮：补上 **C8（字符串池分类比对）** —— 路线的最后一格静态工程

- **C8 一直是 `unknown`**，理由是"没有工具能做"：镜像的池在 `analysis/ida_strings.txt`，
  复刻件的池在 AOT 产物里，**没有任何东西把它们按 locale 键 / URL / 错误消息三类逐类比**。
- **新工具 `analysis/c8_string_class_compare.py`**：两侧都按同一套规则分类并对照，输出
  `docs/C8_STRING_CLASSES.md`。
  ```
  镜像 213,338 条 / 产物 117,322 条
  class            image  artifact  exact-in-artifact
  locale-key         971       935        19
  url               3507       283        14
  error-message     4192       139        48
  dependency        2277       692       218
  other           202391    115273     25085
  ```
- **首跑就暴露了它自己的三个缺陷**，逐个修掉（不是"能跑就算"）：
  1. **`AngleSharp.dll`、`RabbitMQ.Client` 被当成 locale 键** —— 任何点分标识符都匹配。
     改为排除程序集文件名/版本串，并单独设 `dependency` 类；
  2. **"All rights reserved"、"C# runtime library for …" 被当成错误消息** —— 那是被引用程序集的元数据，
     不是我们的文案。加了 20 余个 banner 标记 + 程序集名形状（`Dotted.Title.Case` 全大写段）；
  3. **修完仍有 `Bogus.dllg` 这种样本** —— 那是 **IDA 自己的字符串清单把相邻两条拼在一起**。
     **这不是我的 bug，是数据源的属性**，所以写成第四条限制而不是继续改规则。
  演进：`locale-key` 2851 → 2730 → **971**；`dependency` 0 → 400 → **2277**。
- **四条限制写在报告里，不藏在脚注**：
  ① 产物侧是字节扫描，AOT 有看不见的存储形态 ⇒ **缺席只能读作 unknown（§4.5）**；
  ② 镜像池含被引用程序集的元数据，纯文本规则无法完全分离 ⇒ **计数是上界**；
  ③ 镜像侧是 IDA 的清单，**会把相邻串拼接** ⇒ 点分类被抬高；
  ④ **这是"可比什么"的仪器，不是"是否匹配"的判决。**

### 五要素

- **改了什么**：新增 `analysis/c8_string_class_compare.py`、生成物 `docs/C8_STRING_CLASSES.md`；
  三个修正脚本；`docs/PARITY_CLAIMS.md` 的 C8 行改写（unknown → 有仪器 + 限制）；无源码改动。
- **验证命令与输出**：`python analysis/c8_string_class_compare.py --write-doc` → 见上表；四条限制随报告输出。
- **数字变化**：C8 从 `unknown` 变成**有可复算仪器**；复刻件源码未改，产物不需重发。
- **证据等级**：Observation —— 两类池的计数与分类、三次分类器演进的数字。
  **Correction ×3** —— 分类器的三条规则错在"把点分标识符当资源键""把库描述当文案""把拼接串当真实条目"。
- **还剩什么**：C7c（行为探针）已有 15 条，属持续增补而非一次性；其余见 `OPEN_ITEMS`（无静态项）。
"""

POINTER = """
---

## 第 1380 轮（C8 补齐）

- **`analysis/c8_string_class_compare.py`** 按三类（locale 键 / URL / 错误消息）+ `dependency` 分类对照两侧字符串池，
  生成 `docs/C8_STRING_CLASSES.md`：镜像 213,338 条 / 产物 117,322 条；
  `locale-key` 971 vs 935、`url` 3507 vs 283、`error-message` 4192 vs 139、`dependency` 2277 vs 692。
- **首跑暴露并修掉分类器三个缺陷**（程序集名当资源键、库描述当文案、IDA 拼接串当条目），
  `locale-key` 2851 → 971、`dependency` 0 → 2277。
- **四条限制随报告输出**：缺席只能读作 unknown（§4.5）、计数是上界、IDA 会拼接相邻串、**这是仪器不是判决**。
- 无源码改动 → 产物不需重发。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1380 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1380 \u8f6e')

parity = io.open(PARITY, encoding='utf-8').read()
old_row = '| C8 | 字符串池对等 | **unknown** | unknown |'
if old_row in parity:
    new_row = ('| C8 | 字符串池对等 | **instrument**（R1380：`analysis/c8_string_class_compare.py`，'
               '按 locale 键/URL/错误消息/dependency 四类对照，四条限制随报告输出） | — |')
    parity = parity.replace(old_row, new_row, 1)
    io.open(PARITY, 'w', encoding='utf-8', newline='').write(parity)
    print('PARITY_CLAIMS C8 row updated')
else:
    print('C8 row format differs; left for a human read')
