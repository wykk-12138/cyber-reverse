import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 原版的解墙面：12 个方法，两处纠正（第 143 轮）

回到反编译主线：把原版所有「解墙」形状的方法名捞出来。

```
DetectAsync        ← 检测步，与 replica 的 DetectAsync 同名
SolveWafAsync      ← 通用解墙（一个墙一次调用）
RemoteSolve        ← 服务那条路，独立成一个方法
SolveBotD          ← DataDome 的 BotD 挑战
SolveCptChallenge  ← 插页式挑战
SolveRecaptcha     ← reCAPTCHA
SubmitCaptcha      ← 提交半，与取挑战分开
PollCaptchaAsync   ← **轮询**：至少有一条路是异步的
GetCheckoutCaptcha ← 结账时的验证码（Adyen 3DS captcha）
Solve3DS / Solve3DSRedirect / Solve3DSToken / SolvePayPal3DS
```

### 纠正一：**DataDome 原版是解的**

R141 的普查把 DataDome 记成「有主机、无协议」就停下了。但 `SolveBotD` 就是 DataDome 自己的挑战脚本，
原版有一个以它命名的方法 —— **原版解 DataDome**。

所以缺的是**本工作区对协议的了解**，不是原版的实现。和 R127 那次「缺的控制器在我的表里」是同一种措辞：

> **缺口在我的笔记里。**

`VendorWiring` 的状态**保持不变**（本工作区确实没接上），但理由改清楚了。

### 纠正二：至少有一条路是**轮询**的

`PollCaptchaAsync` 回答了本轮另一个问题：检测之后**不一定是原地 await**。
replica 的梯子是同步的 —— 对本地浏览器求解是对的，对「稍后才回答的服务」是不对的。

### 与 replica 已实现部分的对齐

| 原版 | replica |
|---|---|
| `DetectAsync` | `StoreFlow.DetectAsync` ✅ 同名 |
| `SolveWafAsync` | `CloudflareStrategyRunner` / `KasadaStrategyRunner` ✅ 通用形态 |
| `RemoteSolve` | `ApiKasadaSolver` / `ServiceCloudflareSolver` ✅ 服务路 |
| `SolveBotD` | ❌ 缺协议 |
| `PollCaptchaAsync` | ❌ 全是同步 await |

### 这一轮的一句话

> 我以为我在查「原版怎么做的」，结果查出来的是**「我上一轮说错了一句」**。
>
> **反编译最有用的时刻，不是它告诉我新东西，是它证明我旧的话不对。**
'''

if "## 原版的解墙面" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("solve surface documented")
else:
    print("already present")
