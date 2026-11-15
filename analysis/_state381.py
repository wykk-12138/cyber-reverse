import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R381：登录窗口（实机，640×780 左右）

重启后落在登录窗口，正好把这块界面量了：

```
[ ]  Window "Login"                                      -  X
                        🐢
            Welcome to Cybersole 5.0
        Sign in with your Cybersole account

            ☑ Remember Me

        [      Sign in with browser      ]      ← 全宽绿色

        Don't have an account?  Sign Up
```

**只有三样可交互的东西**：`Remember Me`、`Sign in with browser`、`Sign Up`。
**没有** "Use a code instead"，也没有许可证选择器。

### 复刻件因此改了两处

1. 首屏去掉 `Use a code instead`（它与实测不符）；
2. 把它挪到**等待态**（点过浏览器登录之后），与验证码输入框放在一起 —— 那里才是它的出口。

文案逐条核对（全部命中 locale）：`Auth.Welcome` / `Auth.Login.Subtitle` / `Auth.Login.Button` /
`Auth.Login.RememberMe` / `Auth.Login.NoAccount` / `Auth.Login.SignUp`。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 381 轮：重启实机 → 落在登录页 → 量到一个真实差异

### 一、为什么重启 GUI

剩下 12 个缺口"需要界面位置"。重启原版（登录态已失效，停在 Login 窗口），先把这个窗口量下来。

### 二、实测

```
Welcome to Cybersole 5.0
Sign in with your Cybersole account
☑ Remember Me
[ Sign in with browser ]
Don't have an account?  Sign Up
```

**只有三样可交互**：`Remember Me` / `Sign in with browser` / `Sign Up`。

### 三、复刻件的差异（已修）

`LoginControl` 首屏多了一个 `Use a code instead` 按钮 —— 实测没有。已从首屏移除，
挪到**等待态**（与验证码输入框同处），那里才是它的语义位置。

### 四、验证

```
完整套件   1538 通过 / 0 失败 / 2 跳过
```

### 五、这一轮的一句话

> 这是这一程第 **十** 个实机核对过的界面，也是第 **五** 个"复刻件多了点什么"的发现。

> **多出来的控件和缺少的控件一样是错；前者更难发现，因为界面看起来"更完整"。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 381 轮（重启实机 → 量登录窗口；首屏去掉 `Use a code instead`）。

---

## 实机状态

原版进程在跑，停在 **Login** 窗口（登录态已失效）。GUI 无法进入主界面，因为需要用户账号登录。

**登录窗口已核对完毕**（第十个实机界面）：三样可交互控件，文案逐条命中 locale。

## 状态

```
完整套件   1538 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
UI 类      104 声明 / 28 不可达
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
