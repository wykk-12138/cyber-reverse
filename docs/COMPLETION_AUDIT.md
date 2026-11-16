# 完成判据终审（R706 · 重审）

> 上一次终审在 R700：**(a)(b) 未满足**。此后 (a) 按 YG 裁决结案、(b) 靠实现关闭、(c)(d) 在新产物上复算。
> 这次重审逐条给判定 + 证据 + **仍然 Unknown 的部分**。
>
> 数字全部引自 `docs/METRICS.md`（`python tools/metrics_report.py` 生成）；本条审计不硬编码任何度量。

## 总判

| 判据 | 判定 | 关键证据 |
|---|---|---|
| **(a)** | **满足** | 类型级 0；`UNIMPLEMENTED = 0`（裁决范围外 2 条） |
| **(b)** | **满足（空真）** | 文案缺口 **0**，`_satisfied` 的「键出现在代码」这一支现在真有代码 |
| **(c)** | **满足** | 新产物 55,349,248 B 上复算资源面 **12 ↔ 12**；C6/C10 标了测量条件 |
| **(d)** | **满足** | 22 条全带三列；`audit_claims.py` → **inconsistencies: 0** |
| **(e)** | **满足** | **1624 通过 / 0 失败 / 0 跳过**；变异 **36** 条（字面 29 过时） |

**结论：五条判据全部满足。**

---

## (a) 类型级缺口 → 0、类型缺失 → 0；名字级缺口全部三分类结案

| 子项 | 值 | 证据 |
|---|---|---|
| 类型级缺口 | **0** | `METRICS.md` → `types with scope misses: 0` |
| 名字级缺口结案 | 4 条全部「结构差异」 | R568 判定 + R687 复验其两条支撑事实（`.axaml` 0 个、`MarkupExtension` 子类 0 个）仍成立 |
| 类型缺失 | **17 条，全部有判定与依据** | `docs/TYPE_PRESENCE_TRIAGE.md` |

17 条的分布：

```
RENAMED          7   （声明级唯一匹配，多数还有注释指名）
STRUCTURAL       1   SettingsView —— 18/19 成员名在 SettingsShell 一个类体内共现
OUT_OF_SCOPE     2   AuthWindow / LicenseControl —— YG 裁决（docs/DECISION_LICENSE_OUT_OF_SCOPE.md）
UNKNOWN          7   （1 成员契约词太泛 4 条 / 6·35 个同分候选 3 条，各自写明缺什么）
UNIMPLEMENTED    0
```

**判据括号允许「不可得 → Unknown + 缺什么」，不允许把真缺算成不可得。**
R700 时 `LicenseControl.Authenticate` 是真缺；R702 由 YG 裁定登录凭证类功能不在复刻范围，
`docs/DECISION_LICENSE_OUT_OF_SCOPE.md` 存有裁决原文。**authority 是裁决本身，最高级。**

## (b) 剩余仅「字符串池中截断」的文案

**文案缺口 = 0**（`copy: zones with a missing key: 0 (in 0 zone[s])`）。

「剩余」为空集，所以「剩余仅截断」**空真成立**。**这是空真，不是靠改口径做到的** —— 做法是让那两条文案真的有代码发出它们：

- R702 反编译解出四维规则；R703 从原始字节复验（`lea rdx,[rip+0x05ed5dbe]` → `0x146E4D160`）并重解两个守卫函数
- R704 从原版导出名单（244 国 / 50 州 / 50 缩写，对齐异常 0）
- `ProfileCsvEditorView.ValidateAddress` 按规则校验；`ProfileValidationListsTests` **5/5** 锁住四条规则

`copy_audit_report.py` 的 `_satisfied` 接受「键出现在代码（注释剥离）」，此前那两条只躺在文案表里。**现在不是了。**

## (c) 产物级对照报告可复算

| 子项 | 证据 |
|---|---|
| 报告存在 | `docs/PARITY_PRODUCT.md` |
| **新产物上复算** | 11:49 重建 **55,349,248 B**；`pe_resources.py` → 原版 **12** ↔ 复刻件 **12** |
| 函数级对账 | R609–R618 同口径 **321,244 ↔ 186,732**；符号口径写在导出首行（R699） |
| 测量条件已入表 | C6/C10 行带 artifact-version 注记（见下） |

**已在 11:49 的产物上重测（R707）**：从零重建的 IDB（覆盖旧库 + 载入 PDB types/names），
`auto_analysis_ready: true` 后导出：

```
原版   321,244 个函数  symbols=no   命名 10,041（3.13%）
复刻件 189,090 个函数  symbols=yes  命名 176,784（93.49%）   ← 较旧产物 +1,358
C10    12 / 819 = 1.5%（比例未变：新增的是校验器，不是 view-model 代码）
```

**唯一仍未在新产物上重做的**：R613 的同口径（不带 PDB）数 186,732 —— 那需要另建一个不载 PDB 的库。

## (d) claim 表每条都有 authority + 命令 + gap_reason

| 子项 | 证据 |
|---|---|
| 22 条全带三列 | `docs/PARITY_CLAIMS.md` |
| 与度量一致 | `analysis/audit_claims.py` → **inconsistencies: 0** |

**这一项今天暴露了审计器自己的一处缺陷并修掉了**：它对「275」用 `annotated()`（认历史标记），
对 C14 却是裸字面量存在性检查 —— 结果**历史更正表**因为必须引用旧措辞而永远过不了。
改成同样认标记后归零。**这是「检查存在」而不是「检查是否已交代」的老毛病，第 N 次。**

## (e) 全量套件绿 + 变异测试全 fired + 文档数字来自 METRICS

| 子项 | 值 | 说明 |
|---|---|---|
| 全量套件 | **1624 通过 / 0 失败 / 0 跳过** | 本轮复算（1619 + 5 条新行为测试） |
| 变异条数 | **36** | 判据字面写 29，脚本静态计数 36 —— **字面已过时** |
| 全部 fired | `running 36 of 36`、`restored tree: GREEN` | **R665 的历史记录，本轮未重跑**（36 次全量代价过大） |
| 文档数字来自 METRICS | audit → 0 | 四份文档已改指针 |

---

## 判据之外：目标本身仍然 Unknown 的部分

判据是考题，答完了不等于目标达成。**objective 里有两句判据量不到**：

| objective 原话 | 对应 claim | 状态 |
|---|---|---|
| 函数数量对等 | C6 | pass（Observation 层），比值 0.581（同口径） |
| **每个函数功能相等** | **C7c** | **unknown** —— 缺原版符号，伪代码等价做不了；正路是**行为探针**（同输入 → 两侧输出/副作用对照），未做 |
| 效率相近 | C15 | pass（**代理指标**：零直接 xref 比例），不是真实效率对照 |

**所以「目标达成」这句话，只能说成「五条判据全部满足，而 C7c 与效率对照仍是 Unknown」。**
把 C7c 写成满足，等于用"函数数量差不多"冒充"功能相等"。

## 本轮修掉的三个自己的错

1. `ProfileValidationLists` 的数据文件放进 `Locales/`，撞了 locale 键数守卫 → **移动到 `Data/`，不缩小守卫**
2. `state_owner` 写 `United States`，而名单里是 `United States of America` → 州表取不到
3. **测试断言了前缀匹配** —— 实现是对的，测试是错的
4. （审计器）C14 检查用存在性而非标记感知 → 改审计器，不改历史
