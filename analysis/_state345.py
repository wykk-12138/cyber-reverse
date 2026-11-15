import io
p = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t = io.open(p, encoding='utf-8').read()
t = t.replace('| `GroupSummary` | `Clone` `Delete` `Edit` `StartAll` `StopAll` | 组摘要行上的五个操作，行为清楚但未落到该类型 |',
              '| `GroupSummary` | `Clone` `Delete` `Edit` | **`StartAll` / `StopAll` 已于 R345 落地**；剩下三个语义未定（Clone 是否连任务一起复制？Edit 的参数是什么？） |')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('backlog updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 345 轮：`GroupSummary` 补 `StartAll` / `StopAll`，另三个**留白**

### 一、按 R344 定的三档处理

| 成员 | 判定 | 处理 |
|---|---|---|
| `StartAll` / `StopAll` | 语义无歧义：把本组任务交给引擎启停 | **实现**（返回处理了多少个） |
| `Clone` / `Delete` / `Edit` | `Clone` 是否连任务一起复制？`Edit` 参数是什么？ | **留白**，只记名 |

实现要点：`StartAll` 只数"未在运行"的、`StopAll` 只数"在运行"的，各返回计数 —— 这样测试能断言，
而不是只能看"没崩"。

### 二、两次编译失败都因为**读错模型**

1. `_services.Tasks.StopAll(tasks)` —— 实际签名是 `StopAll(IEnumerable<string> ids)`；
2. 测试里 `new BotTask { IsRunning = true }` —— `IsRunning` 是**只读计算属性**（`State is Monitoring/Waiting/CheckingOut`），
   要写 `State`。

都是"没先读那一行"的老毛病（R259 / R302 / R325 同源）。

### 三、验证

```
GroupSummaryTests   2 通过
完整套件            1509 通过 / 0 失败 / 2 跳过
bind_scope          GroupSummary 缺 5 → 缺 3（Clone, Delete, Edit）
```

### 四、这一轮的一句话

> "三档处理"这个规则是上一轮才定下的，这一轮就用它挡了三次"顺手编个实现"的冲动。

> **规则的用处不在写下来那天，在于第二天它替你说了"不"。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 345 轮（`GroupSummary` 补 `StartAll`/`StopAll`；`Clone`/`Delete`/`Edit` 按规则留白）。

---

## 三档处理的第二次应用

| 成员 | 判定 | 结果 |
|---|---|---|
| `GroupSummary.StartAll` / `StopAll` | 语义无歧义 | **已实现**（返回计数，可测） |
| `GroupSummary.Clone` / `Delete` / `Edit` | 语义未定 | **留白**，记在 `docs/BINDING_BACKLOG.md` |

## 两次编译失败的原因（同一老毛病）

`StopAll` 实际签名是 `StopAll(IEnumerable<string> ids)`；`BotTask.IsRunning` 是**只读计算属性**。
都是"没先读那一行"（R259 / R302 / R325 同源）。

## 状态

```
完整套件        1509 通过 / 0 失败 / 2 跳过
名字级缺口      17
类型级缺口      44（筛查器口径）
mutation        29 / 29 fired
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
