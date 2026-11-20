"""R1318 record: the image's storefront surface, quantified for the first time.

The question "how many stores does the image support" has been recorded as unknown since the coverage
document was written. It is still not answered exactly, but it now has a bound, produced by a script rather
than by reading a neighbourhood -- and the bound is large enough to change how the remaining work should be
framed: the replica models 67 stores and the image names 2671 bare origins, of which 857 are matched by
domain to something the replica already knows and 1324 are not.

The caveat is part of the finding: a host with no catalogue entry is not necessarily unhandled, because the
replica's ShopifyFlow serves any Shopify store generically. So 1324 is an upper bound on *unlisted* stores,
not on unhandled ones.
"""
import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
CORE = 'replica/docs/CORE_COVERAGE.md'

ROUND = """
---

## 第 1318 轮：镜像的店铺面第一次有了数量——比"少两家店"大两个数量级

- **起因**：前两轮补 Saucony 与 AO 都是**碰巧撞见**的。于是换个问法，直接量：
  镜像里所有"裸源站"形态的 URL（`https://host` 或 `https://www.host`，不带路径——那正是镜像店铺表的样子）
  与复刻件已知域名求差。新增 `analysis/storefront_gap.py`。
- **结果（可重算）**：
  ```
  镜像裸源站      2671
  复刻件已知域名   857
  无对应条目      1324   （.com 700 / .uk 163 / .au 92 / .jp 43 / .ch 32 / .fr 31 …）
  ```
  **这个数字必须带一句限定**：没有目录条目 ≠ 没有被处理——复刻件的 `ShopifyFlow` 是**通用**的，
  任何 Shopify 店都能跑。所以 1324 是**未列名店铺的上界**，不是未处理店铺的数量。
- **量这个数遇到的三次"假设形状"错误，与前人踩的坑一模一样**（都写进脚本头了）：
  1. 只扫 `Modules/` → 得 50 个域名（多数 flow 在 `Flows/`）；
  2. 解析 `store_catalog.py` 的表格 → 得 36（列被截断）；
  3. 只认 `Domains => new[] {...}` → 得 77（`Registry.cs` 里还有内联写法
     `new FlowStoreModule(new ShopifyFlow("100thieves", "100 Thieves", new[] { "100thieves.com" }))`）。
  最终取**整仓任何形如域名的字符串字面量**——对"缺口"这个问题，**过包含是安全方向**：它可能藏起一家店，不会凭空造出一家。
- **顺带说明镜像侧的两个筛子**：只收**裸源站**（把 CA-OCSP、报错信息里的主机挡掉），
  再排掉一份**显式列出的基础设施词表**（支付/CDN/分析/证书）。词表写在脚本里，**看得见就能被反驳**。
- **对剩余工作的意义**：路线图一直按"补几家缺的店"来安排，实际是**上千个未列名主机**。
  下一轮起要么承认这层差距并给出取舍（哪些店值得建模），要么明确"通用 flow 覆盖"的边界——
  **不能再用"还差几家"这种口径汇报**。

### 五要素

- **改了什么**：新增 `analysis/storefront_gap.py`（含三次错误的记录）；三份文档记录。
  **未改 `replica/src` 与 `replica/tests`**，故不重跑变异；产物未重发布；`docs/METRICS.md` 未变。
- **验证命令与输出**：`python analysis/storefront_gap.py` → `2671 / 857 / 1324`，TLD 分布如上；
  文档守卫 `DocsConsistency|CoreCoverage|ParityDoc` → 见本轮套件。
- **数字变化**：新增一组**此前不存在的度量**。套件不变（无新增用例）。
- **证据等级**：Observation —— 2671 个裸源站、857 个已知域名、1324 个差集及 TLD 分布，
  全部可由脚本重算。**Bound，不是 count** —— 上界性质已在文档里写明。
- **还剩什么**：把 1324 变成可行动的清单（哪些是同一家店的区域域名、哪些已被通用 flow 覆盖）；
  以及原有的 AO 三个 checkout 体、Saucony 六步路径。
"""

POINTER = """
---

## 第 1318 轮

- **镜像店铺面第一次量化**：裸源站 2671、复刻件已知域名 857、**无对应条目 1324**（.com 700 / .uk 163 / .au 92 …）。
  工具 `analysis/storefront_gap.py`。
- **这是上界不是数量**：无目录条目 ≠ 未处理，`ShopifyFlow` 是通用的。文档里写明了。
- 三次"假设形状"错误（只扫 Modules/ = 50、解析截断表格 = 36、只认 `Domains =>` = 77）都记在脚本头，
  最终取整仓域名形字面量——**对缺口问题，过包含是安全方向**。
- **口径要改**：不能再按"还差几家店"汇报，实际是上千个未列名主机。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1318 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1318 \u8f6e')

# The coverage document gains the bound, and keeps the "Unknown" and "connect/app" claims its guard reads.
text = io.open(CORE, encoding='utf-8').read()
addition = """
### 原始店铺表：仍 Unknown，但第一次有了上界（R1318）

- **仍 Unknown**：镜像到底支持多少家店，以及 `connect/app` 那条载荷，都还没有精确答案。
- **但已有界**（`python analysis/storefront_gap.py` 可重算）：镜像里"裸源站"形态的 URL **2671** 条，
  复刻件源码里形如域名的字面量 **857** 个，差集 **1324**（.com 700 / .uk 163 / .au 92 / .jp 43 …）。
- **限定**：无目录条目 ≠ 未被处理——`ShopifyFlow` 是通用 flow。**1324 是未列名店铺的上界**。
"""
if 'R1318' not in text:
    with io.open(CORE, 'a', encoding='utf-8', newline='') as fh:
        fh.write(addition)
    print('CORE_COVERAGE updated with the bound')
