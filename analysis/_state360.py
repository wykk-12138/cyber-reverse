import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 360 轮：三个模型成员（类型级缺口 28 → 25）

| 类型 | 成员 | 依据 |
|---|---|---|
| `WebTask` | `Steps` | `BotTask` 已有同名列表，WebTask 是它的网页版孪生 |
| `Product` | `Color` | 绑定表点名；行颜色为空表示未设 |
| `SmartAction` | `Logs` | 绑定表点名；引擎追加、视图读取 |

三个都加在模型层，**不涉及 UI**，编译一次通过。

```
完整套件   1525 通过 / 0 失败 / 2 跳过
bind_scope 28 → 25
```

### 这一轮的一句话

> 模型层的成员最容易补，因为它们**不需要猜 UI 位置** —— 只需要知道它是数据。

> **缺口的难易不在数量，在"它属于层还是属于界面"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 360 轮（`WebTask.Steps` / `Product.Color` / `SmartAction.Logs`；类型级缺口 25）。

---

## 经验：模型层成员最省力

`WebTask.Steps`、`Product.Color`、`SmartAction.Logs` 三个都只加数据，不涉及 UI 定位，
编译一次通过。**先把这一层做完，剩下的都是界面问题。**

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 25（类型级，起点 52）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
