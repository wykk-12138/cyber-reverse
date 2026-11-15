import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 343 轮：把 `LoginControl` 的五个绑定操作从 lambda 里提出来

### 一、改了什么

绑定表：`Cybersole.Ui.Views.Auth.LoginControl -> Cancel, OpenBrowser, SignIn, SignUp, UseCode`。
复刻件这五件事**都做了**，但全在点击回调的匿名函数里 —— 行为一样，**没有一个能被绑定的名字**。

现在：`Cancel()` / `OpenBrowser()` / `SignUp()` / `UseCode()` / `SignInAsync(code)` 五个成员，
按钮改为调用它们（`SignInAsync` 是 async 的，因为它要和 `AuthService` 换码）。

> 这是 R239 在 NotificationsView 上做过的同一件事：**行为已经在，但名字不在，就等于没有接口。**

### 二、验证

```
LoginControlTests 新增 TheFiveBoundOperationsExistAsMembers
完整套件           1506 通过 / 0 失败 / 2 跳过
bind_scope.py      LoginControl 已从"缺 5 成员"名单里消失
```

### 三、顺手把筛查工具修好（它一开始是错的）

上一轮交出去的 `bind_scope.py` 用"下一个声明"做块边界，结果**同一份代码两次跑出 23 和 49 两个数**。
这一轮重写：

1. **花括号配对**取块边界（不再靠猜）；
2. **沿基类上溯**合并祖先成员（继承来的不再算缺失）。

数字从 52 → **44**，且 `LoginControl` 干净了。但仍有 44 类报缺，其中相当一部分是
**框架成员**（`Close` 来自窗口/模态基类）—— 所以它的定位仍是**筛查器**，不是判决书。

### 四、这一轮的一句话

> 上一轮我拿着一个"能出数字"的脚本就去报 23 个缺口；这一轮同一脚本报 49。
> 差别的来源不是代码，是**我的块边界提取方法**。

> **工具给出数字之后，先问一句"这个数字稳定吗"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\METHOD.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''

### §10.1 筛查工具本身也会骗人（R343）

`bind_scope.py` 的第一版用"下一个声明"做块边界，**同一份代码跑出 23 和 49 两个不同的数**。
改成**花括号配对 + 基类上溯**后稳定在 44，且已修好的类型（`LoginControl`）确实消失。

> 规则：**任何新指标都要先跑两遍、隔一轮再跑一遍**；两次不一致，先修工具，别修代码。
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('METHOD §10.1 added')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 343 轮（`LoginControl` 五个绑定操作成为成员；`bind_scope.py` 修好块提取）。

---

## 这一轮两件事

1. **`LoginControl`**：`Cancel` / `OpenBrowser` / `SignUp` / `UseCode` / `SignInAsync` 从匿名回调变成成员，
   按钮改为调用（同一手法见 R239）。`bind_scope.py` 里该类型已干净。
2. **`bind_scope.py` 修好**：花括号配对 + 基类上溯；数字 52 → 44，且不再抖动。

## 工具现在的定位

**筛查器，不是判决书**：44 个"类型级缺成员"里仍有框架成员误报（`Close` 等）。
每条要手工复核；本轮抽的 `LoginControl` 五条全为真。

## 状态

```
完整套件        1506 通过 / 0 失败 / 2 跳过
名字级缺口      17
类型级缺口      44（筛查器口径，含误报）
mutation        29 / 29 fired
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
