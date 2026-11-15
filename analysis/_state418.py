import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 418 轮：`AccountGrid.AccountGroup` / `Edit`（类型级缺口 11 → 10）

### 一、补的两个

| 成员 | 形状（`bind_shape.py`） | 实现 |
|---|---|---|
| `AccountGroup` | `Getter,Property` | 返回首行的 `GroupId`（一个网格只显示一个组；空网格返回空串） |
| `Edit` | `Getter,Property` | `_rows.Count > 0`（有行才谈得上编辑） |

两者都是**只读**，与形状证据一致。

### 二、验证

```
CloseAndOpenFamilyTests   6 通过 / 0 失败
bind_scope                11 → 10 个类型
```

### 三、这一轮的一句话

> 这两个成员都不难 —— 难的是**先确认它们是只读的**，否则我会顺手加个 setter。

> **形状证据省下的不是打字时间，是"改错方向"的时间。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('类型级缺口 11（tools/bind_scope.py）', '类型级缺口 10（tools/bind_scope.py）')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
