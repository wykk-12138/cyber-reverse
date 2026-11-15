import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 356 轮：`Close` 家族再扩四个类型，`ProxyGroupView.Delete` 按真实形状写

### 一、这一轮补的

| 类型 | 成员 | 说明 |
|---|---|---|
| `ProxyGroupView` | `Close` / `Delete(IList<ProxyGroup>)` | 这个视图只编辑**一个**组，没有列表也没有 services，所以 `Delete` 由调用方把列表传进来 |
| `ProxyCreatorView` | `Close` | — |
| `ProfileGroupView` | `Close` | — |
| `StaggerStartView` | `Cancel` | 关窗即取消 |

`bind_scope.py`：37 → **34**。

### 二、又一次"先猜后错"

`Delete()` 第一版我写了 `_groups.SelectedItem` / `_services.Config.ProxyGroups` —— **全是猜的**，
编译报三个 `CS0103`。回滚、读了真实成员（`_group`、构造只收一个组）后，才有了
`Delete(IList<ProxyGroup> from)`。

**同一个错误在这一程里出现第 N 次**：R259 猜 API、R302 猜模型、R325 猜依赖、R345 猜签名、R356 猜字段。

### 三、验证

```
完整套件   1523 通过 / 0 失败 / 2 跳过
```

### 四、这一轮的一句话

> 我今天已经在"先读那一行"上栽了五次。第五次之后，我把规则从"要记得先读"改成
> **"写方法前先 grep 一次那个类的字段"** —— 把纪律变成动作。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\METHOD.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''

### §12 把纪律写成动作：写方法前先看一眼那个类的字段（R356）

"先读那一行"这条纪律，我这一程违反过至少五次（R259 猜 API、R302 猜模型、R325 猜依赖、R345 猜签名、
R356 猜字段），每次都是同一个后果：编译报错 → 回滚 → 重写。

**动作化**（比"记住"有效）：

1. 给某个类加成员之前，先 `grep 'class X' -Context 0,30` 看它的字段与构造签名；
2. 若该类型没有它需要的依赖（如 `ProxyGroupView` 没有 services/列表），**把依赖作为参数传进来**，
   而不是假设它存在；
3. 一次只加一个成员，**加完立刻编译**。
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('METHOD §12 added')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 356 轮（`Close` 家族再扩 4 个类型 + `ProxyGroupView.Delete`；类型级缺口 34）。

---

## `Close` / `Cancel` 家族覆盖

`TaskCreatorView` · `TaskDetailsView` · `TaskGroupView` · `ProxyCreatorView` · `ProxyGroupView` ·
`ProfileGroupView` · `StaggerStartView(Cancel)` · `HelpView.OpenUrl` · `UserView.OpenUrl`

约定：**无宿主窗口 → 返回 false**（可断言，不抛）。

## 新纪律（`docs/METHOD.md` §12）

写方法前先 `grep 'class X' -Context 0,30` 看字段与构造；类没有所需依赖就把依赖作为参数传入。
**一次只加一个成员，加完立刻编译。**

## 状态

```
完整套件   1523 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 34（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
