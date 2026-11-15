import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 286 轮（**目标标记为 blocked**：连续 7 轮可用内存 < 8 GB 硬线，需用户重启才能继续）。

---

## 为什么停在这里（具体、可核验）

| 事实 | 值 |
|---|---|
| 可用物理内存 | **5.69 GB**（自定硬线 8 GB） |
| 连续低于硬线的轮次 | **7 轮**（R280–R286） |
| 我这一侧的残留进程 | dotnet / chrome / Cybersole / ida **均为 0** |
| `memreset.ps1`（purge） | 需要管理员权限，本会话**被拒**（`SeProfileSingleProcessPrivilege`） |
| 需要重启才能做的三件事 | ① 全量 `mutation-check`（24 条，12–15 分钟，同时拉全套）② 结构性工作（抽行控件 / B 类 31 个）③ 继续 GUI 交叉验证（要开原版窗口） |

**轻活已做尽**：文档（`METHOD.md` / `RESUME.md` / `BINDING_BACKLOG.md` / `FLOW_SEQUENCES.md` / `GUI_GEOMETRY.md`）、
工具（`bind_diff` / `backlog_report` / `flow_dump` / `row_groups` / `flow_filter` / `mutation-audit`）、
锚点修复（22/24 → **24/24**）、三组对账（账本↔棘轮、简报↔产物、数据↔不变量）。

## 重启后的执行顺序（不要改）

1. `python tools/mutation-check.py` —— 全量 24 条，12–15 分钟，**期间不做别的**；
2. `dotnet test --filter "Speed!=Slow"` —— 确认 1442+；
3. 结构性工作：按 `docs/BINDING_BACKLOG.md`（B 类 31 个，先抽 `FilterRow` / `ProfileCsvRow` / `ActionRow`）。

## 交接状态

```
完整套件 1442 通过 / 0 失败 / 2 跳过（R280/R281）
mutation 锚点 24/24 活；全量未跑
缺口 33（real = ceiling）    不可达 UI 类 29
18 条流水线 / 141 步；2 条字面量流
```

新会话从 `docs/RESUME.md` 开始。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
