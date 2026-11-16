# 交接（2026-11-16 20:10，机器重启前保存）

## 现在在哪

- **轮次**：R823 刚做完并提交。
- **套件**：`1765 通过 / 1 失败` —— 唯一红的是 `DocsConsistencyTests.TheModuleCountInVerdictMatchesTheCatalogue`，
  **原因是我自己在 `replica/docs/VERDICT.md` 里写了「N 个模块」式句子而 N≠63**。
  本次保存前已改措辞，**重启后先跑一次确认它转绿**。
- **四项度量未变**：名字级 `real gap 4 / missing 16` · 类型级 `0` · 类型缺失 `17` · 形状 `78` · 文案 `0`。
- **完整套件基线**：R820 时 1766 / 0。

## 本轮刚改的东西（已提交，未验完全量）

`ShopifyFlow` / `FootsitesFlow` / `MagentoFlow` 各删掉一处 `Guid.NewGuid().ToString("N")` 的 CSRF 兜底。
**139 个流程相关用例通过**；全量还差一次干净的跑。

## 重启后第一件事

```
cd D:\projects\cyber-reverse\replica
python tools\metrics_report.py
```

**期望 1766 / 0。** 若 `DocsConsistencyTests` 仍红，去 `replica/docs/VERDICT.md` 里找
「数字 + 个模块 / modules」且数字不等于 63 的那一行，改措辞（不要引号复述它，那会把模式又写一遍）。

## 下一步该做的（按价值排序）

1. **`GetHomeAsync` 忽略 `c.Url` 的 3 个流程**（`NikeFlow` / `PoqAppFlow` / `SuperswipeFlow`）——
   已确认与 `ModuleRobustnessTests` 的例外名单一致。**待判的是「忽略是对的还是遗漏」，判据在镜像里。**
   工具：`analysis/scan_url_ignoring4.py`（缩进切类 + 截到下一成员，唯一自洽的版本）。
2. **`StoreFlow.HandleResponseAsync` 是死代码** —— 有定义、无调用点，读 `lastStatus` 并按状态码分支。
   **它看起来该被某步调用。谁该调它，是下一个要查的。**
3. **`ScrapeVariantAvailabilityAsync` 有 19 个实现只返回成功** —— 抽查两个都是真活（读 `raw`、写 `available`），
   **但没有全部读过。**
4. 判据 (a)(b)(c)(d)(e)(f) 的状态见 `docs/COMPLETION_AUDIT.md` 与本文件下方。

## 完成判据现状（重启后不必重查）

| 判据 | 状态 |
|---|---|
| (a) 类型级缺口 / 类型缺失 | **已分类完毕**：`real gap 4` / `missing 16` / 类型缺失 17（`docs/TYPE_PRESENCE_TRIAGE.md`：2 越界 · 7 改名 · 1 结构性 · 7 契约无判别力） |
| (b) 文案 | **0**，无剩余 |
| (c) 产物级对照 | **PASS** —— `python analysis\verify_artifact.py`：1142/1142 locale · 20/20 资源 · 12/12 叶子 |
| (d) claim 表 | **PASS 规则** —— `python analysis\check_claims.py`：5 行，2 pass / 3 fail，全有 authority，非 unknown 全有命令 |
| (e) 套件 / 变异 / 数字来源 | **一条待转绿**（见上）；数字全部出自 `docs/METRICS.md` |
| (f) 核心覆盖表 | 风控已对账（R807）；站点复刻件→镜像已逐条（49/57 有据、6 零、2 仅噪音）；**镜像→复刻件未分类（池子有 1182 个 `myshopify` 主机，是下界）** |

## 工具状态（重要）

- **`analysis/pe_strings.txt` 是抽样，不是全量**（180,228 行 vs 镜像 324,895 条串）。
  **正向可用、反向不可用** —— 反向结论要用 `python analysis\ida.py str <pat>`。见 `AGENTS.md` §2.7b。
- **`ida.py str` 默认 `limit 40`**（已加 `--limit`），**插件侧还有约 500 条上限**。**数数要写明是下界。**
- **仓内扫描器：按花括号或按「最近前缀 class」定类边界都会错**（一文件多类 + 字符串里的 `{`）。
  **可用的做法**：缩进切类 + 截到下一个成员声明。

## 机器相关

**内存不足导致重启**。重启后若 `available < 2GB` 只用 `-m:1`；`< 1GB` 停构建。
**IDA 若需重开**：后台跑 `powershell -File "D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1" -Path <目标.i64>`，
同时用 CUA 轮询点掉「请确认」类对话框，直到再读一次没有框。
