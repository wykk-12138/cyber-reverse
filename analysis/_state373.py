import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 373 轮：`TaskView.CreateGroup` / `MoveGroup`，顺带把 `TaskGroupView` 从"不可达"里救出来

### 一、补的两个

| 成员 | 行为 | 证据 |
|---|---|---|
| `CreateGroup()` | 新组 + 打开组编辑器（`TaskGroupView`），返回该视图 | locale `"CreateGroup.Name": "Name"` —— 一个带 Name 字段的建组对话框 |
| `MoveGroup(groupId)` | 把选中任务移到目标组（先从各组移除，再写入目标组），返回移动数量 | 同名成员在 `AccountGrid` / `ProfileView` 上都是"移到另一组" |

### 二、两个守卫红了，都是"真的变好了"

1. `UnreachedUiTypesTests`：`TaskGroupView` 出现在"不可达"基线里，而 `CreateGroup()` 现在**构造它** ——
   所以基线里该删掉它（这是改善，不是削弱）；
2. `SummaryBlockTests`：指南里"104 / **31** 不可达"要改成 **30**（`RESUME.md` / `SESSION_STATE.md` / `VERDICT.md` 同步）。

### 三、一次命名空间失误

`ViewHostModal` 在 `Cybersole.Ui.Views.Common`，我直接写了短名 → `CS0103`。加 using + 全名，通过。

### 四、验证

```
完整套件   1534 通过 / 0 失败 / 2 跳过
bind_scope TaskView 缺口 3 → 1（只剩 Toggle）
UI 类      104 声明 / 30 不可达（原 31）
```

### 五、这一轮的一句话

> 补一个成员，**顺手把一个从没被点开过的弹窗变成了真正可达的界面** —— 这不是副作用，这是收益。

> **"可达性"是会随调用点变化的活指标，不是一次性统计。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 373 轮（`TaskView.CreateGroup` / `MoveGroup`；`TaskGroupView` 变为可达，不可达 UI 类 31 → 30）。

---

## `TaskView` 只剩 1 个无定论

`Toggle`（`CreateGroup` / `MoveGroup` / `LinkChange` / `Quicktask` / `PinGroups` 都已落地）

## 可达性指标会动

`TaskGroupView` 因为 `CreateGroup()` 构造它，从"不可达基线"里删除 →
指南数字 31 → 30（三份文档同步）。**这类红是改善，不是回归。**

## 状态

```
完整套件   1534 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 17（类型级）
UI 类      104 声明 / 30 不可达
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
