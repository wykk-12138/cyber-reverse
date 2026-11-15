import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 366 轮：`GoogleAccountsView.YouTube`，以及一个**关于绑定成员类型的发现**

### 一、池子里的线索

```
Cybersole.Ui.Views.Settings.GoogleAccountsView,Cybersole.YouTube!Getter
Cybersole.Ui.Views.Settings.GoogleAccountsView,Cybersole.YouTube!Setter
Cybersole.Ui.Views.Settings.GoogleAccountsView,Cybersole.YouTube!Property
"YouTube - {0}"          ← 一个窗口标题模板
```

三条访问器 + 一个标题模板 → `YouTube` 是**可读写的属性**，值是字符串（喂给 `YouTube - {0}`）。
已加 `public string? YouTube { get; set; }`，**不附带任何行为**（填充者未知）。

### 二、顺带看到的另一件事

同一段字符串里还有 `get_Add` / `get_Clear` / `get_Edit` / `get_Delete` —— 说明这些绑定成员在原件里
是**返回命令的属性**（`ICommand`），而不是方法。复刻件一律写成方法。

这不影响"成员存在"，但影响**绑定的形状**：一个 `ICommand` 属性能被 XAML 的 `Command=` 直接绑，
方法不能。**这一点记进 METHOD，暂不重构**（26 个视图全部改成命令属性是大工程，且没有证据要求必须如此）。

### 三、`Edit` 继续留白

`GoogleAccountsView` 里**没有任何编辑路径**（无按钮、无编辑器），所以 `Edit` 的语义无从推断。

```
完整套件   1525 通过 / 0 失败 / 2 跳过
bind_scope 18（类型数不变，`GoogleAccountsView` 还差 `Edit`）
```
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\METHOD.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''

### §13 绑定成员可能要求"命令属性"的形状（R366）

池子里同一段字符串同时出现 `get_Add` / `get_Clear` / `get_Edit` / `get_Delete`，
说明原件里这些**绑定成员是返回 `ICommand` 的属性**，而复刻件写成了方法。
方法能表达同样的行为，但 **XAML 的 `Command=` 只能绑属性**。

现状：不重构（26 个视图全改代价大、无强制证据）；新增成员时，
**如果它明显是"用户动作"，优先写成 `ICommand` 属性**，与原件同形。
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('METHOD §13 added')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 366 轮（`GoogleAccountsView.YouTube`；发现绑定成员可能是**命令属性**）。

---

## 新认识：绑定成员的"形状"（`docs/METHOD.md` §13）

池子里出现 `get_Add` / `get_Clear` / `get_Edit` / `get_Delete` → 原件的这些成员是 **`ICommand` 属性**。
复刻件写成方法，行为等价，但 XAML 的 `Command=` 只能绑属性。

**今后新增"用户动作"类成员，优先写成 `ICommand` 属性。**

## 状态

```
完整套件   1525 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 18（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
