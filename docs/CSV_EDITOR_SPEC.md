# `ProfileCsv` 编辑器：从原版文案反推的功能清单

> **这份文档是什么**：复刻件的 `ProfileCsv` 编辑器目前大体是空壳（见 `BLOCKERS` §63 —— 字典里 40 条文案，39 条没有代码产出）。
> 本文不改代码，只把**原版会说的 39 句话**整理成一份可核对的验收面。
>
> **证据强度**（每一行都按这个读）：
> - **Observation**：原版 locale 里存在这条文案（键 + 原文），复刻件也存着；
> - **Inference（中）**：因此原版编辑器**有**这项动作或这个状态；
> - **Unknown**：这个动作**具体怎么做**（合并规则、冲突处理、撤销粒度…）——文案不告诉这些。
>
> 换句话说：**本文能证明「有哪些功能」，不能证明「功能怎么工作」。**
> 每一条的"行为"列因此全部是 Unknown，而不是我没写。

---

## 一、命令类（用户主动触发）

| 名称 | 原文 | 推出的动作 | 行为 |
|---|---|---|---|
| `AddRow` | `Add Row` | 在末尾加一行 | Unknown |
| `DeleteRows` | `Delete Rows` | 删除选中行 | Unknown（选中多行时的语义？） |
| `Duplicate` | `Duplicate Rows` | 复制选中行 | Unknown（复制到末尾还是紧邻？） |
| `MenuClear` | `Clear Cells` | 清空选中单元格 | Unknown |
| `MenuCopy` | `Copy` | 复制选中到剪贴板 | Unknown（TSV？CSV？） |
| `MenuPaste` | `Paste` | 从剪贴板粘贴 | Unknown（越界如何处理？） |
| `MenuFillDown` | `Fill Down` | 用首行填充下方选区 | Unknown |
| `Undo` | `Undo` | 撤销 | Unknown（粒度：按单元格还是按命令？） |
| `Apply` | `Apply Changes` | 把编辑结果写回 profile | Unknown（部分失败怎么办？） |
| `ConfirmDeleteFormat` | `Apply and delete {0} profiles` | 应用前提示将删除 N 个 | Unknown（N 如何计数） |

## 二、查找与替换

| 名称 | 原文 | 推出的动作 | 行为 |
|---|---|---|---|
| `Find` | `Find` | 查找 | Unknown |
| `Regex` | `Regex` | 正则模式开关 | Unknown（作用于查找还是替换） |
| `ReplaceAll` | `Replace All` | 全部替换 | Unknown |
| `ReplaceWith` | `Replace with` | 替换目标输入 | Unknown |
| `StatusRegexInvalid` | `Invalid regular expression` | 正则非法时报错 | Unknown（报错后是否保留上次模式） |
| `StatusReplaced` | `Replaced {0} values` | 报告替换了 N 处 | Unknown |

## 三、单元格校验

| 名称 | 原文 | 推出的规则 | 行为 |
|---|---|---|---|
| `ErrorBoolean` | `Use true or false` | **R651：无宿主** —— 两侧都没有布尔列（复刻件 15 列无 bool；原版池无 `oneCheckout`/`enabled`），宿主列 Unknown，故不能补。规则本身（true/false、大小写、`1`/`0`）仍 Unknown |
| `ErrorMonth` | `Month must be between 1 and 12` | 月份列范围 1–12 | **Observation 级的规则**，可直接实现 |
| `ErrorNameRequired` | `Profile name is required` | 名称列非空 | **Observation 级的规则**，可直接实现 |
| `ErrorYear` | `Year must be 2 or 4 digits` | 年份列 2 位或 4 位 | **Observation 级的规则**，可直接实现 |
| `StatusFixErrors` | `Fix the highlighted cells before applying` | 有错误时禁止应用 | Unknown（阻止还是仅提示） |

> **这一组是整份清单里唯一"规则本身写在文案里"的** ——
> 三条的判定条件由句子直接给出（范围、非空、位数），补它们**不算设计行为**。
> 这是全表里最接近"证据闭合"的一处，值得优先。

## 四、导入 / 导出

| 名称 | 原文 | 推出的动作 | 行为 |
|---|---|---|---|
| `Import` | `Import CSV` | 导入 CSV | Unknown |
| `Export` | `Export CSV` | 导出 CSV | 已有实现（`StatusExported` 之外的那条路径） |
| `StatusNoHeader` | `The CSV needs a header row with known column names` | 无表头时报错 | Unknown（"known column names" 的集合是什么） |
| `StatusParseFailed` | `Couldn't read the CSV: {0}` | 解析失败报错 | Unknown |
| `StatusImported` | `Merged {0} rows from {1}` | 报告合并了 N 行 | **注意 `Merged`**：说明导入是**合并**不是替换 → 合并键是什么 Unknown |
| `StatusIgnoredColumns` | `Ignored unknown columns: {0}` | 报告被忽略的列 | Unknown |
| `StatusDiscardConfirm` | `You have unsaved changes. Close again to discard them.` | 有关闭确认 | Unknown（"再点一次"的时限） |

## 五、模式与汇总

| 名称 | 原文 | 推出的状态 | 行为 |
|---|---|---|---|
| `ModeGrid` | `Grid` | 表格模式 | Unknown |
| `ModeText` | `Raw CSV` | 原始文本模式 | Unknown（切换时是否互相同步） |
| `SummaryNew` / `SummaryEdited` / `SummaryRemoved` | `{0} new` / `{0} edited` / `{0} removed` | 三态计数 | Unknown（如何判定"改过"） |
| `SummaryErrors` | `{0} errors` | 错误计数 | Unknown |
| `SummaryNone` | `No changes` | 无变更 | **Observation 级**：无变更时的固定文案 |
| `Title` | `CSV Editor` | 窗口标题 | 可直接用 |
| `AllColumns` | `All columns` | 列筛选的"全部"选项 | Unknown |
| `Clipboard` | `clipboard` | 粘贴来源名 | 可直接用 |
| `Hint` | `Editing the raw CSV replaces every row. Rows keep their profile through the Id column; rows without one become ne…` | 一段说明 | **这条信息量最大**：原始文本模式**整体替换**，行靠 `Id` 列保持身份 |

---

## 五半、宿主盘点（R660，自动生成：`python analysis/dead_copy_hosts.py`）

剥离死文案表自身后，按关键词搜索该类正文：

| 结果 | 条数 | 含义 |
|---|---|---|
| **无宿主** | **20** | 关键词在表外一次都不出现 → 要做它得先**加一个功能**，而那个功能的行为 Unknown |
| 值得一看 | 12 | 其中 5 个 `Summary*` 命中的是通用词 `Summary`（无判别力）→ **真正值得看的是 7 条** |

无宿主的 20 条：`AddRow` `AllColumns` `Clipboard` `MenuFillDown` `MenuPaste` `ErrorBoolean` `Export` `Find`
`ModeGrid` `Hint` `ModeText` `Regex` `ReplaceAll` `ReplaceWith` `StatusDiscardConfirm` `StatusExported`
`StatusImported` `StatusRegexInvalid` `StatusReplaced` `Undo`

值得一看的 7 条：`Apply` / `ConfirmDeleteFormat` / `DeleteRows` / `Duplicate` / `MenuClear` / `Import` / `StatusParseFailed`

**「无宿主」证明的是「复刻件里没有代码路径含该关键词」，不是「原版没有这项功能」。**

## 六、按证据强度排序的处置建议

| 组 | 条数 | 证据 | 能否现在补 |
|---|---|---|---|
| **规则写在文案里**（`ErrorMonth` / `ErrorNameRequired` / `ErrorYear` / `SummaryNone` / `Title` / `Clipboard`） | 6 | 文案即规格 | **可以** —— 不涉及猜行为 |
| 动作存在、细节 Unknown（命令、查找替换、导入导出、模式） | 27 | 只证明"有" | 不能：补了就是设计 |
| ~~需要外部数据~~ → **无宿主**（`ErrorBoolean`，R651）／缺列名集合（`StatusNoHeader`） | 2 | 部分 | 部分 |
| 与 `Id` 列身份相关（`Hint` 揭示的机制） | 1 | 文案揭示机制 | 需先确认 `Id` 列语义 |

> **最该先做的是第一组**：它们的判定条件就写在句子里，补进去不算猜。
> 其余 27 条应记为 **Unknown（缺行为规格）**，等凭据或反编译。

---

## 七、这份文档不是什么

- **不是行为规格**。它只说"原版会说什么"，不说"原版怎么做"。
- **不是完整性证明**。39 条是"会说的话"，不是"所有功能"——没有文案的行为不会出现在这里。
- **不是实现承诺**。除第一组外，其余条目在拿到证据前不应动手。

---

## 八、结案（R663）

> 这一族此前一直以「还剩 N 条」的形式挂着。本节把它按组定性，**不再以条数形式挂账**。
> 条数以 `python analysis/dead_copy_check.py` 与 `python analysis/dead_copy_hosts.py` 的输出为准，不在此复述。

### 逐组定性

| 组 | 定性 | 依据 |
|---|---|---|
| **一、命令类** | `Apply` **已实现**（按钮标签 "Apply" → "Apply Changes"）；其余 **无宿主** | `dead_copy_hosts.py`：类内表外搜不到对应关键词；`ApplyCore` 是唯一真宿主 |
| **二、查找与替换** | **无宿主**（6 条） | `Find` / `Regex` / `ReplaceAll` / `ReplaceWith` 在类内一次都不出现 |
| **三、单元格校验** | 3 条**已实现**（`ErrorNameRequired` / `ErrorMonth` / `ErrorYear`）；`ErrorBoolean` **无宿主** | 前三条由 R631 落地；`ErrorBoolean` 见 §84：两侧都没有布尔列 |
| **四、导入 / 导出** | `StatusNoHeader` / `StatusIgnoredColumns` / `StatusParseFailed` **已实现**；`Import` / `Export` / `StatusImported` / `StatusExported` **无宿主** | 该类**没有导出功能**（`Export` / `SaveFileDialog` / `File.WriteAll` 一个都没有）；`Import` 只命中 `"Imported …"` 的子串 |
| **五、模式与汇总** | **需换判据**（8 条） | `Summary` 是通用词，对该组无判别力；「两种模式是否互相同步」的行为仍 Unknown |
| **五半、宿主盘点** | 表本身已修正两次（R660 / R662） | 见该节的边界说明：**「无宿主」可信、「有宿主」不可信** |
| **六、处置建议** | `Title` **已实现**；`StatusFixErrors` **已实现** | R632 / R631 |

### 结案的准确含义

- **不是「都做完了」**，而是「**每条都有定性，没有一条还处于「待查」状态**」；
- 定性为**无宿主**的那些，正确读法是「**要做它，得先加一个功能，而那个功能的行为 Unknown**」；
- 定性为**需换判据**的那 8 条，缺的不是实现，是**一个能区分它们的判据**。

### 为什么可以就此收手

这一族里「规则写在句子里、且判据在自己手上」的条目**已经全部做完**（R631 三条校验 + `StatusFixErrors`、
R632 `Title`、R653 `StatusNoHeader`、R654 `StatusIgnoredColumns`、R661 `StatusParseFailed`、R662 `Apply`）。

**剩下的每一条都要么需要新增功能（行为未知），要么需要换判据（现有数据不支持）。**
继续一条条试，只会重复 R651/R652 那种「依据不成立、改动撤回」。

### 仍然 Unknown

- 29 条无宿主的条目在原版里各自做什么：**Unknown**（缺反编译或运行期观察）。
- 原版是否真有导出 / 撤销 / 查找替换：**Unknown**。
- 那 8 条「需换判据」需要什么样的判据：**Unknown**。
