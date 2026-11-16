# 文案缺口清单（自动生成：`python tools/copy_audit_report.py`）

> 本文件是**生成物**，数字每次重跑都会刷新。汇总口径见 `docs/METRICS.md`（R433 裁决 1）。

| 区域 | 键/值对 | 原文缺失 | 近似错误 |
|---|---|---|---|
| `Accounts` | 36 | 0 | 0 |
| `Proxies` | 33 | 0 | 0 |
| `Tasks` | 40 | 0 | 0 |
| `Profiles` | 27 | 0 | 0 |
| `Analytics` | 12 | 0 | 0 |
| `Auth` | 27 | 0 | 0 |
| `Billing` | 0 | 0 | 0 |
| `Checkout` | 6 | 0 | 0 |
| `Data` | 20 | 0 | 0 |
| `HistoryWindow` | 17 | 0 | 0 |
| `Monitor` | 15 | 0 | 0 |
| `ProfileCsv` | 43 | 0 | 0 |
| `Release` | 4 | 0 | 0 |
| `Settings` | 255 | 0 | 0 |
| `SmartActions` | 22 | 0 | 0 |
| `TaskCreator` | 37 | 0 | 0 |
| `TaskGroup` | 30 | 0 | 0 |
| `Utilities` | 23 | 0 | 0 |
| `GroupModal` | 2 | 0 | 0 |

## 怎么读

- **原文缺失**：这句原文**和它的 key 名**在 `src/` 里都一处没有 → 代码从不查这条文案。
  只要 key 名出现就算"在用"（R622）：走 locale 的应用不会把值写在源码里，它按 key 查表。
- **近似错误**：几乎相同但不等 → 需要人工三分类（真缺陷 / 拼接假阳性 / 位置未定）。

## 已知的三分类结论（R398/R401）

| 类别 | 例子 | 处置 |
|---|---|---|
| 真缺陷 | `Disconnect` 缺席，只有状态词 | 已补（R401） |
| 拼接假阳性 | `" Custom Size"` vs `1 Custom Size` | 忽略 |
| 位置未定 | `Add Size` vs `Add Size(s)` | 先确认是哪个按钮 |

## 无宿主的区域

`Monitor` 的 7 条属于一个**复刻件里还不存在的页面**（没有 `MonitorView`）—— 不是待接线，是页面未实现。

## 原文缺失明细（R542 新增）

> 判据 b 要求"每条写明为何不可得"。下表是那几条本体 —— 没有它，"5 条"只是一个无法核对的数。

| 区域 | 键 | 原文 |
|---|---|---|
