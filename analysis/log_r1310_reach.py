"""R1310 correction: the new type did not reach the artifact, and saying so is the deliverable.

After publishing I searched the artifact for the new constants and found none -- then for the type names,
and found every sibling except the new one. The size is byte-identical to the previous publish. So
SquareBrowserData was trimmed as unreachable: nothing in the application calls it, and its only callers are
tests, which the artifact does not contain.

Left unsaid, this round would have read as "the Square fingerprint ships". It does not. The code is correct
and generated from the image's bytes, and it becomes reachable the moment a Square browser flow calls it --
but until then it is source-level surface, and this file records that rather than letting the round record
imply otherwise.
"""
import io

VERDICT = 'replica/docs/VERDICT.md'
BLOCKERS = 'docs/BLOCKERS.md'

NOTE = """
### 第 1310 轮 · 补记：这份代码**没有进产物**

发布之后按 §4.5 的规矩复核，结果是：

| 检查 | 结果 |
|---|---|
| 产物里搜 `__UA__`（ASCII 与 UTF-16 两种） | **0** |
| 产物里搜 `L0NR598Z0FFW5`、`5120,1440` | **0** |
| 产物里搜类型名 `SquareBrowserData` | **0** |
| 同一次搜索里的 `SquareGateway` / `KomojuGateway` / `SauconyFlow` / `ToppsCdn` | **1 / 1 / 1 / 2** |
| 产物尺寸 | **61,259,776** —— 与上一轮**一字不差** |

四个同类都能搜到，说明"搜类型名"这个仪器本身是好的；而新类型一个都没有、尺寸又分毫未动，
合起来只能有一个解释：**`SquareBrowserData` 是不可达代码，被 AOT 裁剪掉了**。
应用里没有任何地方调用它，唯一调用者是测试，而测试不在产物里。

所以本轮的实际交付是**源码级 API 面 + 从字节生成的精确数据**，不是"随产物发布的行为"。
这与 §4.5 的告诫正好互为补充：§4.5 说"搜不到字面量不能推出被裁"，这里反过来——
**尺寸没变 + 同类名字都在 + 新名字不在**，三条同向，才敢下这个结论。

要让它进产物，得先有一条真实调用链（Square 的浏览器流程落地时自然就有了）。在那之前，
把它写进任何"已发布行为"的清单里都是错的。
"""

BLOCK_ENTRY = """
---

## R1310 · `SquareBrowserData` 被 AOT 裁剪，未进产物

- **现象**：产物里搜不到 `SquareBrowserData` 类型名，也搜不到它的任何常量（`__UA__`、`L0NR598Z0FFW5`、
  `5120,1440`），而同一批搜索能命中 `SquareGateway` / `KomojuGateway` / `SauconyFlow` / `ToppsCdn`；
  同时产物尺寸与上一轮**完全相同**（61,259,776 字节）。
- **判读**：不可达代码被裁剪。应用无任何调用点，唯一调用者是测试。
- **影响**：本轮的数据与 API 是**源码级**的，尚未随产物发布。这不影响测试有效性，但影响"已发布行为"的表述。
- **解除条件**：出现真实调用链（Square 浏览器流程落地）后重发布，并复核类型名进入产物。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, NOTE, '\u8fd9\u4efd\u4ee3\u7801**\u6ca1\u6709\u8fdb\u4ea7\u7269**')
append(BLOCKERS, BLOCK_ENTRY, 'R1310 \u00b7 `SquareBrowserData`')
