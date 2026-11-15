import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 252 轮（首次为绑定表扩模型：多动作 / 过滤行为 / 输入；缺口 78 → 72；全套 1432 绿）。

---

## 棘轮当前值：`MaxRealGap = 72`

## 模型已扩（R252，先有名字后有结构）

| 新类型 | 对应原版绑定 |
|---|---|
| `SmartActionStep` | `SmartActions.Action` |
| `SmartActionStepConfig`（Name/Required） | `SmartActions.ActionConfig` |
| `SmartActionFilterInput`（Filter/Input） | `SmartActions.FilterInputEntry` |
| `SmartAction.Actions` | `SmartActions.SmartAction.Actions` |
| `SmartActionFilter.Behaviour` + `.Inputs` | `SmartActions.Filter.Behaviour/.Inputs` |

据此补上五个命令：`AddAction` / `DeleteAction` / `AddInput` / `DeleteInput` / `ToggleFilterBehaviour`。

**剩下 2 个（`DeleteParam`、`UseTemplate`）**：前者需要"动作参数"的删除语义，后者需要模板来源，下一轮处理。

## 剩余 72 的头部

| 类型 | 缺 |
|---|---|
| `MessageBoxDialog` / `ProfileCreatorView` | 各 4 |
| `FilterRow` / `ProfileCsvRow` / `Platform` / `AccountGrid` / `AnalyticsView` | 各 2–3 |
| 其余 | 各 1–2 |

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
