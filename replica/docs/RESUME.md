# 接手简报（一页，R282 时点）

> 新会话从这里开始，不必翻 `VERDICT.md`（那是 124 万字节的编年史）。

## 1. 这是什么

复刻 `Cybersole.exe` 5.18.32（NativeAOT）。标准是**函数级功能对等**（不要求字节相同，命名可以不同）。
根路径 `D:\projects\cyber-reverse`，复刻件在 `replica/`（.NET 8 + Avalonia，`D:\tools\dotnet8\dotnet.exe`）。

**证据主次**：反编译/字符串池 = 主证据；GUI（cua）= 消歧与去噪；测试与守卫 = 回归。

## 2. 当前数字（引用时必须带口径）

| 指标 | 值 | 口径 |
|---|---|---|
| 完整套件 | **1606 通过 / 0 失败 / 2 跳过** | `dotnet test --filter "Speed!=Slow"`（R426 时点；R403 起内存不足时只用相关用例） |
| 绑定缺口 | **17**（real = `MaxRealGap` = 账本标题） | whole-source + **剥注释** + 排除 `HasMultiple_NN`/`Value_NN` |
| 不可达 UI 类 | **29**（105 个中，分母=Cybersole.Ui 所有 public class） | `UnreachedUiTypesTests` |
| 类型级绑定缺口 | **10 个类型** | `python tools/bind_scope.py` |
| 文案缺口 | Accounts/Proxies/Tasks/Profiles **四区清零**；Settings 21 条近似错误待核对 | `python tools/locale_text_gap.py` / `locale_near_miss.py` |
| `PARITY.md` 的 UI 类 | **84**（26 Window + 58 UserControl，分母不同） | `ParityDocTests` |
| 恢复的流水线 | 18 条 / 141 步（复刻件已建模 8 条，均字面量可对账） | A+B 布局合并去重 |
| 字面量流 | **8 条全部**（每条都有地址） | `FlowSource.Literal` + `StoreFlowDigestTests` |

## 3. 已逐字对齐的两处（可以直接引用）

- **八条流的步骤表**：每条都有字面量地址，`StoreFlowDigestTests` 钉住；
- **错误目录 13 条**：标题与详情 **13/13 + 13/13 在池子里逐字命中**，`ErrorCatalogDigestTests` 钉住。

## 4. 三件待办（按顺序）

1. **`python tools/mutation-check.py`** —— 全量 **29** 条，12–15 分钟，**期间不要做别的**。
   R286 已全量跑过一次：**24/24 全部 fired**（改前先 `python tools/mutation-audit.py` 查锚点）。加了 `--limit N` / `--only TEXT` 可廉价重测。
2. **跑一次全套** 确认 1606+（R426 时点为 1606；条数会因为合并/新增断言而变，别把旧数当基准）。
   低内存时用 `--no-build`（21 秒、内存只掉约 0.4 GB）。
3. 然后才是结构性工作：B 类 31 个（`FilterRow`/`ProfileCsvRow`/`ActionRow` 需**抽行控件**），
   或按 `docs/BINDING_BACKLOG.md` 的 A 类 2 个（都缺数据源）。

## 5. 已确认做不了（别再试）

| 项 | 为什么 |
|---|---|
| `Attributes.Platform` 三值 | 池子只有名（R225）、下拉点不开（R242 两次）、locale `Platform.*` 零键（R265） |
| `AnalyticsView.OpenRelease` | 无 release 目录、无浏览器服务（R254） |
| `X-Shopify-Generated-Cart-Token` 方向 | 头名在池里只出现 1 次；**要定方向必须运行时抓包**（R267） |
| 行控件家族 5 个 | 复刻件是内联构造，locale 也无对应文案 → 结构差异（R265） |
| 段→商店归属（14 条） | 方法名不含品牌（0/69）、邻居不含店名（0/69）、复刻件模块无对象可切（R271） |

## 6. 五条硬纪律（都是踩出来的）

1. **数字带口径**；注释不算实现；噪音按形状识别（`^(HasMultiple|Value)_\d+$`）。
2. **ceiling 只等于实测值**（先测后设）—— 已错 3 次（R254/R255/R263）；
   账本标题必须与它相同（`TheBacklogDocQuotesTheCeiling`）。
3. **改代码前先读那一行**（字段/方法签名）—— 不读就是 4 连错（R259）。
4. **用替换而不是插入**（`replace(anchor, anchor + new)`）—— 否则锚点行写两遍（R252/R255）。
5. **报"绿"必须说口径**（子集 ≠ 全套）。

## 7. 内存纪律（用户强调过四次）

| 指标 | 动作 |
|---|---|
| 可用物理 **< 8 GB** | **停手**：只做文档/脚本，不编译不跑测试 |
| Commit ≥ 30 GB | 软线，可做小步 |
| 每轮编译后 | `dotnet build-server shutdown`（实测回收 ~1.2 GB） |
| 每轮 | **一次重活**；不与 IDA/GUI 并行 |
| 测试后 | 查 `chrome` 进程与 `%TEMP%\cyb-chromium-*`（曾泄漏 9072 个目录 / 46.7 GB） |

## 8. 地图

| 文件 | 用途 |
|---|---|
| `docs/METHOD.md` | 做法总纲（三种证据 / 测量 / 计数 / 改动 / 推进 / 内存） |
| `docs/BINDING_BACKLOG.md` | 17 个缺口（全部已判定：12 等价 / 3 不可得 / 2 内部） |
| `docs/B_CLASS_DECISIONS.md` | 每个 B 类类型的判定 + 依据 |
| `docs/CONTROL_DESIGN_*.md` | 已落地的控件设计稿（ComboBoxEdit / ProfileCsvRow / FilterRow 家族） |
| `docs/FLOW_SEQUENCES.md` | 两种布局、18 条流水线、段→商店的边界 |
| `docs/GUI_GEOMETRY.md` | 唯一权威几何表（测过的数） |
| `docs/XAML_BINDINGS.md` | 绑定表怎么读、两种口径、三类分类 |
| `tools/` | `bind_diff.py` / `backlog_report.py` / `flow_dump.py` / `row_groups.py` / `flow_filter.py` / `mutation-check.py` |
