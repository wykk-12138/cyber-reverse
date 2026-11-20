"""R1319 record: the storefront gap narrows to registrable domains, and stays large.

R1318 said 1324 hosts. Merging subdomains to registrable domains and keeping only bare origins that sit in a
dense run of other bare origins -- the storefront table's actual shape -- gives 1319 hosts across
**1213 distinct registrable domains**. So the earlier number was not inflated by regional subdomains: these
really are separate domains, and the image lists roughly two thousand of them while the replica names 800.

The document is generated rather than written by hand, because a list of 1213 names is only useful if it can
be regenerated at will and cannot drift from the tool that produced it.
"""
import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
ROADMAP = 'docs/REMAINING_REPLICATION_ROADMAP.md'

ROUND = """
---

## 第 1319 轮：把 1324 收窄到"注册域"——差距没有变小，但口径终于准了

- **上轮的 1324 是主机数**。这轮做两件事把口径收紧：
  1. **归并到注册域**（含 `co.uk`/`com.au`/`co.jp` 等二级后缀表，`401games.ca` 是两段、`argos.co.uk` 是三段）；
  2. 镜像侧加**结构筛子**：只收**密集成串**的裸源站（±0x800 字节内至少还有 3 个同类）——
     镜像的店铺表是字典序大表；报错信息里引用过的孤立 URL 由此挡掉。
- **结果**：
  ```
  裸源站出现 2758，落在密集串里 2669
  复刻件域名形字面量 857 → 可归并到 800 个注册域
  无对应条目 1319 个主机 = **1213 个注册域**（.com 700 之前那次统计的性质不变）
  ```
  **归并几乎没有减少**（1324 → 1319 主机，1213 注册域）——说明这些**真的是彼此独立的域名**，
  不是同一家店的区域变体。上轮"上千个未列名主机"的判断站得住，而且现在有结构筛子撑着。
- **生成物**：`docs/STOREFRONT_SURFACE.md`（226 行，由 `--write-doc` 生成）。
  1213 个名字的清单**只有能随时重算、且不会与被它引用的工具漂移**才有用，所以是生成的而不是手写的。
  文档抬头写明：**这是"未列名"，不是"未处理"**（`ShopifyFlow` 通用）。
- **抽样确认这些是真店**：`1290sqm.com`、`401games.ca`（多伦多桌游店）、`303boards.com`、`5pm.fr` ——
  都是实体零售站，不是错误页里的主机名。

### 五要素

- **改了什么**：`analysis/storefront_gap.py`（注册域归并、密集串筛子、`--roots`、`--write-doc`）；
  新增生成物 `docs/STOREFRONT_SURFACE.md`；VERDICT / HANDOFF 记录。**未改 `replica/src` 与 `replica/tests`**。
- **验证命令与输出**：`python analysis/storefront_gap.py --write-doc` → 2669 / 857 / 800 / 1319 / **1213**，
  写出 226 行文档；`--roots --limit N` 可列任意前缀。
- **数字变化**：1324 主机 → **1319 主机 / 1213 注册域**；新增一份生成文档。套件不变。
- **证据等级**：Observation —— 五个数字 + TLD 分布 + 抽样验证的四个真实店铺域名，全部可重算。
  **Bound，不是 count**：上界性质在文档抬头写明。
- **还剩什么**：这层差距需要一个**范围决定**（哪些店值得建模 / 通用 flow 的覆盖边界怎么写），
  而不是继续一家一家补；以及原有的 AO 三个 checkout 体、Saucony 六步路径。
"""

POINTER = """
---

## 第 1319 轮

- 1324 主机收窄为 **1319 主机 / 1213 注册域**（加了二级后缀表 + "密集成串"结构筛子）。
  **归并几乎没减少** → 这些真是彼此独立的域名，不是区域变体。上轮判断成立。
- 生成物 `docs/STOREFRONT_SURFACE.md`（226 行，`--write-doc` 重算）。抬头写明**未列名 ≠ 未处理**。
- 抽样确认真店：`1290sqm.com`、`401games.ca`、`303boards.com`、`5pm.fr`。
- **下一步是范围决定，不是继续补店**：要么列建模优先级，要么写清通用 flow 的覆盖边界。
"""

ROADMAP_ADD = """
  7. **店铺面差距是结构性的，不是"还差几家"**（R1318/R1319）：镜像列出 **2669** 个裸源站，
     复刻件源码里有 **800** 个注册域，差集 **1213 个注册域**（清单见 `docs/STOREFRONT_SURFACE.md`）。
     加二级后缀归并后数字几乎不变，说明它们彼此独立而非区域变体。
     **这条不再是待办列表，而是一个范围决定**：要么给出建模优先级（哪些店值得做），
     要么在路线图里写清「通用 flow 覆盖到哪一层为止」的边界。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1319 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1319 \u8f6e')

text = io.open(ROADMAP, encoding='utf-8').read()
if 'STOREFRONT_SURFACE' in text:
    print('roadmap already references the surface doc')
else:
    anchor = '  6. **`Saucony`'
    start = text.index(anchor)
    end = text.index('\n\n', start)
    text = text[:end + 2] + ROADMAP_ADD + text[end + 2:]
    io.open(ROADMAP, 'w', encoding='utf-8', newline='').write(text)
    print('roadmap updated with the surface item')
