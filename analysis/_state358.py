import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 358 轮：三个 `GroupName` / `Groups` 成员（类型级缺口 32 → 29）

### 一、按 §12 先读三个类

| 类型 | 已有的东西 | 补的成员 |
|---|---|---|
| `ProfileGroupView` | `ListBox _groups` + 构造里 `var name = UiKit.Text(...)` | `GroupName`（跟输入框同步，用 `_typedName` 记录） |
| `AccountGroupView` | `private readonly TextBox _name` | `GroupName => _name.Text` |
| `TaskGroupListView` | `AppServices _services` | `Groups => _services.Config.TaskGroups` |

这一轮**没有一次编译错误** —— 三个类都先读了字段，成员直接照真实形状写。

### 二、验证

```
完整套件   1525 通过 / 0 失败 / 2 跳过
bind_scope 32 → 29
```

### 三、这一轮的一句话

> 上一轮（R356/R357）我还在猜字段、猜类型；这一轮按 §12 先读，**零编译错误**。

> **纪律从"记住"变成"动作"之后，第一次见效。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 358 轮（`ProfileGroupView.GroupName` / `AccountGroupView.GroupName` / `TaskGroupListView.Groups`；缺口 29）。

---

## 类型级缺口的处理节奏（已稳定）

1. 先 `python tools/snapshot.py`；
2. `grep 'class X' -Context 0,20` 读字段与构造；
3. 按真实形状加**一个**成员；
4. `dotnet build` → 通过再加下一个。

R358 用这套流程补了三个成员，**零编译错误**。

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 29（类型级，起点 52）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
