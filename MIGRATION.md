# 迁移记录：逆向工作区从 C: 搬到 D:

**时间**：第 127 轮（2026-11-12）
**原因**：C: 剩余空间紧张（25.9 GB，且逆向产生的 IDA 数据库与备份占了 2.7 GB）

---

## 新布局

```
D:\projects\cyber-reverse\
├── replica\            ← 复刻工程（1289 个文件，含 src / tests / tools / docs，617 MB）
├── analysis\           ← 取证脚本与字符串池（562 个文件，28 MB）
├── docs_baseline\      ← 原版 GUI 基线快照（17 个文件）
├── target\             ← 分析目标 + IDA 数据库（正在 D: 上重建）
│   └── Cybersole.exe        （123.3 MB，5.18.32）
└── MIGRATION.md        ← 本文件
```

**工作目录也切过来了**：`D:\projects\cyber-reverse`（后续所有相对路径都从这里算）。

## 删掉的东西

| 路径 | 大小 | 说明 |
|---|---|---|
| `C:\Users\wykk\AppData\Local\Cybersole\analysis\idb_backup` | **1.37 GB** | R110 的数据库备份 —— 数据库本体已随 `target\` 一起搬走，备份不再需要 |
| `C:\Users\wykk\AppData\Local\Cybersole\replica` | 0.62 GB | 已完整复制到 D: 并验证后才删 |
| `C:\Users\wykk\AppData\Local\Cybersole\analysis` | ~26 MB | 已完整复制（跳过备份与 `__pycache__`）后删 |
| `C:\...\Cybersole\current\Cybersole.exe.id*` | **1.37 GB** | 数据库搬到 `target\` 后删掉原位副本 |

**C: 释放约 2.7 GB**（25.9 GB → 28.6 GB 可用；其余被 D: 侧的构建产物占用）

## 保留的东西

`C:\Users\wykk\AppData\Local\Cybersole\current\` 里的**原版安装**保持不动 ——
那是 Cybersole 自己的安装目录，会（Velopack）自动更新；动它会破坏原版运行。
分析用的是 `target\` 里的副本（同版本 5.18.32）。

## 迁移后的验证

| 检查 | 结果 |
|---|---|
| `dotnet build Cybersole.sln -c Release`（清掉 bin/obj 之后） | **已成功生成** |
| `verify-steps.ps1 -All`（七步） | **ALL STEPS PASSED**（1057 通过 / 0 失败 / 2 跳过） |
| `tools/mutation-check.py` | **restored tree: GREEN** |
| IDA 重新载入 `target\Cybersole.exe` | 数据库在 D: 上重建，插件 `get_metadata` 返回 200 |

### 迁移时发现的一个硬编码路径

`tools/mutation-check.py` 第 15 行写死了
`REPO = r"C:\Users\wykk\AppData\Local\Cybersole\replica"`，搬到 D: 后立刻 `FileNotFoundError`。
改成从脚本自身位置推：

```python
REPO = str(pathlib.Path(__file__).resolve().parent.parent)
```

> **搬家是最好的硬编码体检** —— 不搬一次，这条路径会一直在那儿正确着。

## 踩到的坑（记下来）

1. **IDA 数据库搬走后，`Load existing` → `Reload file` → `Repair` 三个选项都不能原地复用**
   —— 文件是「未正常关闭」状态，最省事的做法是**直接载入并让它重建**（约 14 分钟）。
2. **PDB 询问一律选 No**：那份 PDB 只存在于 `actions-runner` 构建机，本地和微软符号服务器都没有。
3. **删原目录前必须先在新位置跑通测试** —— 这次是先 `robocopy` → 清 bin/obj → 构建 → 三步验证
   → 才删 C: 的副本。
