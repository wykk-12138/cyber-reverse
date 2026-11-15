import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 311 轮：第 1 件控件的设计稿（`ComboBoxEdit` 家族），仍然不编译

### 一、先把原版的东西读清楚

绑定表里同一命名空间下有三件：

| 类型 | 成员 |
|---|---|
| `Cybersole.Ui.Controls.ComboBoxEdit` | `ClearSelectionCommand`, `RemoveTokenCommand` |
| `Cybersole.Ui.Controls.ComboBoxToken` | `Text` |
| `Cybersole.Ui.Controls.ComboBoxGroupHeader` | `Name` |

推出的是：**多选下拉 + token 展示（可逐个移除）+ 分组标题 + 一键清空**。
推不出的是：token 的视觉形态、分组是否可折叠 —— 这些**不写进设计**。

### 二、复刻件现状

`UiKit.Combo(...)` 是**单选**，48 处使用；没有多选、没有 token、没有分组。

### 三、设计稿写了什么（`docs/CONTROL_DESIGN_ComboBoxEdit.md`）

- 类骨架（`Option` / `ComboBoxToken` / `ComboBoxGroupHeader` + `Selected` / `RemoveToken` / `ClearSelection`）；
- 交互等价原则：**不猜原版像素，只做等价交互**；
- **先不接页面** —— 原版绑这两个命令的页面未知，没有证据就不往界面上硬接（与 R265 一致）；
- 5 条验收 + 5 条测试（纯逻辑，不开窗口）；
- 完成后的账本动作：缺口 31 → 29，**先测后设**。

### 四、为什么这轮只写设计

可用内存 6.86 GB（低于硬线）。写设计稿不需要编译，而它能让下一轮**照着做**，不用再想一遍。

### 五、这一轮的一句话

> 之前几轮我把"31 个结构差异"判成了类；这一轮开始把其中一件**写成了可执行的设计**。

> **在动不了代码的时候，把"下一步做什么"写到别人能照着做的程度，本身就是产出。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 311 轮（第 1 件控件 `ComboBoxEdit` 家族的设计稿：`docs/CONTROL_DESIGN_ComboBoxEdit.md`）。

---

## 下一个可执行任务（照设计稿做）

`docs/CONTROL_DESIGN_ComboBoxEdit.md` 已写好：

- 原版三件：`ComboBoxEdit`（`ClearSelectionCommand`/`RemoveTokenCommand`）、`ComboBoxToken.Text`、`ComboBoxGroupHeader.Name`
- 复刻件现状：`UiKit.Combo` 单选，48 处使用
- 设计：多选 + token（可逐个移除）+ 分组标题 + 一键清空；**先不接页面**（无页面证据）
- 5 条验收 + 5 条测试（纯逻辑）
- 完成后缺口 **31 → 29**（先测后设）

## 状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R307）
mutation   29 条 / 锚点 29/29
缺口       31（8 抽 + 12 已核实等价 + 3 不可得 + 2 内部/重复）
Commit     40.6 GB / 可用 6.86 GB   ← 低于硬线
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
