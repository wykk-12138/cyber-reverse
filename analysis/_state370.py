import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 370 轮：`TaskView.PinGroups`，以及一个**否证**（绑定表其实没漏）

### 一、先怀疑自己的账本

`TaskView` 在池子里有 **30** 个带访问器证据的成员，比我记录的 6 个缺口多得多 ——
于是我怀疑 `docs/xaml_bindings.json` 漏了成员，跑了对齐检查：

```
访问器证据里的类型   102
xaml_bindings.json   174
只在访问器证据里出现的类型   0
成员列表不完整的类型         0
```

**否证**：绑定表是完整的，池子只多给了"形状"，没多给"名字"。

### 二、补上一个语义清楚的

`PinGroups`：Setter 证据 + `TaskGroup.Pinned` + 选择器按 `Pinned` 排序 →
写成**可读写属性**（设置时写 `Pinned` 并 `Save()`），与它"既是动作又是状态"的证据吻合。

`TaskView` 缺口 6 → 5（`CreateGroup` `LinkChange` `MoveGroup` `Quicktask` `Toggle` 仍无定论）。

```
完整套件   1525 通过 / 0 失败 / 2 跳过
bind_scope 18（类型数不变）
```

### 三、这一轮的一句话

> 我这一轮最大的产出是**一次否证**：我担心绑定表漏了三分之二的成员，查完发现一个都没漏。

> **怀疑自己的数据是对的；查完发现没问题，也是进展。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 370 轮（`TaskView.PinGroups`；否证了"绑定表漏成员"的怀疑）。

---

## 已否证（不必再查）

- 池子的访问器证据**没有**给出绑定表之外的类型或成员（102 vs 174，差集为空）；
  它唯一多给的是**形状**（`docs/BINDING_SHAPES.md`）。

## `TaskView` 剩 5 个无定论成员

`CreateGroup` · `LinkChange` · `MoveGroup` · `Quicktask` · `Toggle`
（`PinGroups` 已按"可读写属性 + `TaskGroup.Pinned`"实现）

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 18（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
