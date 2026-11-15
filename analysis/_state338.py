import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R338：Keyboard Shortcuts 页 —— 实机读到 18 条 chord，复刻件**全部一致**

实机（Settings → Keyboard Shortcuts）：

```
Keyboard Shortcuts — Edit and disable keyboard shortcuts
[Enable Keyboard Shortcuts]  ●

Tasks
  New Group      [Ctrl][G]  Task Creator   [Ctrl][N]
  Task Editor    [Ctrl][E]  Start All      [F1]
  Stop All       [F2]       Delete Selected[Delete]
  Clone Selected [Ctrl][C]  Search         [Ctrl][F]
  Quicktask      [Ctrl][Q]  Link Change    [Ctrl][M]
  Next Group     [Ctrl][→]  Previous Group [Ctrl][←]

Proxies
  New Group      [Ctrl][G]  Add Proxies    [Ctrl][N]
  Test All       [Ctrl][T]  Copy Selected  [Ctrl][C]
  Clone Selected [Ctrl][D]  Delete Selected[Delete]

Billing
  New Group      [Ctrl][G]  Add Profile    [Ctrl][N]
  …（下半截在折叠线以下）
```

每条 chord 右侧都有一个 `×`（清除该绑定），整页顶部是单个 `Enable Keyboard Shortcuts` 开关。

### 与复刻件对照

| 项 | 结论 |
|---|---|
| Tasks 12 条 chord | **全一致**（`Ctrl+G/N/E`、`F1`、`F2`、`Delete`、`Ctrl+C/F/Q/M`、`Ctrl+Right/Left`） |
| Proxies 6 条 | **全一致**（`Ctrl+G/N/T/C/D`、`Delete`） |
| 顺序与标签 | 一致（`KeyBindsView.TaskLabels` / `ProxyLabels`） |
| 顶部开关 | 一致（`Enable Keyboard Shortcuts`） |

### 新增守卫

`KeyBindChordTests`（3 条）：把 12 + 6 + 4 条 chord **用 `KeyBindMatcher.Describe` 的输出**钉住 ——
也就是说它测的是**界面上真正渲染的那个字符串**，而不是模型里的键码。

> Billing 后两条在实机折叠线以下，未本轮重读 → 测试注释里写明"这两条来自 R76 的抄录"，不冒充重测。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 338 轮：Keyboard Shortcuts 页 —— 18 条 chord 实机核对**全一致**，并钉成测试

### 一、实机读到的（Tasks 12 + Proxies 6）

```
Tasks    Ctrl+G  Ctrl+N  Ctrl+E  F1  F2  Delete  Ctrl+C  Ctrl+F  Ctrl+Q  Ctrl+M  Ctrl+Right  Ctrl+Left
Proxies  Ctrl+G  Ctrl+N  Ctrl+T  Ctrl+C  Ctrl+D  Delete
```

每条右侧一个 `×`（清除），页顶一个 `Enable Keyboard Shortcuts` 开关 —— 与复刻件一致。

### 二、这一轮的价值不在"改"，在"钉"

复刻件的模型里 chord 是**键码**（`Key = 50, Modifiers = 2`），界面上显示的是
`KeyBindMatcher.Describe(bind)` 的输出。所以新测试 `KeyBindChordTests` 断言的是**渲染出来的字符串**：

```csharp
Assert.Equal(new[] { "Ctrl+G", "Ctrl+N", "Ctrl+E", "F1", … }, actual);
```

**测界面文字，不测内部键码** —— 这才是用户能看出来的那一层。

### 三、一处诚实边界

Billing 的后两条 chord 在实机折叠线以下，本轮**没有重读**；测试注释里写明它们来自 R76 的抄录，
不冒充"本轮实测"。

### 四、验证

```
KeyBindChordTests   3 通过
完整套件            1493 通过 / 0 失败 / 2 跳过
```
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 338 轮（Keyboard Shortcuts：实机 18 条 chord 全一致，并用 `Describe()` 渲染值钉成测试）。

---

## 实机核对第九个面：Keyboard Shortcuts

`Tasks` 12 条 + `Proxies` 6 条 chord 与复刻件**完全一致**，顺序、标签、右侧 `×`、顶部
`Enable Keyboard Shortcuts` 开关都一致。

新守卫 `KeyBindChordTests`（3 条）断言的是 **`KeyBindMatcher.Describe()` 的输出**（界面文字），
不是模型里的键码 —— 前者才是用户看得见的。

**诚实边界**：Billing 后两条在实机折叠线以下，未重读，测试注释注明来自 R76 抄录。

## 状态

```
完整套件   1493 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     24.5 GB / 可用 14 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
