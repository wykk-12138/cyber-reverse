import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 手机的**触觉面**与那道闸门（第 157 轮）

样本里还有两份东西：一份 `const NAV` 捕获，和一段讲清「为什么要补」的注释。

### 一、`const NAV`（逐字）

```
const NAV = {"standalone": false, "hardwareConcurrency": 4, "webdriver": false, "maxTouchPoints": 5,
             "cookieEnabled": true, "appCodeName": "Mozilla", "appName": "Netscape",
             "appVersion": "5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) AppleWebKit/605.1.15…"}
```

这台手机是 **iOS 27.0.1**、四核、**五个触点**。

### 二、闸门（原版注释，0x03d27ea7）

```
// hsw gates its whole worker path on one of them:
//   aK_ = ('ontouchstart' in window);  lK = uS && aK_ && <ua not Safari-shaped>;
//   QW = nW || lK
// With aK_ false the gate opens and we …
```

**`'ontouchstart' in window` 不是装饰** —— 一方墙的 worker 分支靠它和 UA 形状配对决定走哪条。
一个声称 iPhone、却答 `false` 的 profile，是在**回答一个对方用来选择的问题**。

### 三、replica 之前的样子

`MobileSurface` 装了屏幕、视口、Screen 形状，**却没装触点** —— `maxTouchPoints` 仍是宿主机的 10。
这和 R151 漏掉 `visualViewport` 是同一类：句子里的第二件事没做。

### 四、已落成 `MobileNavigator`

`MaxTouchPoints = 5`、`HardwareConcurrency = 4`、`IosVersion 27.0.1`、五个触觉处理器
（`ontouchstart/move/end/cancel/touchforcechange`）、`HswGate` / `HswConsequence` 两个常量。
只对 Apple UA 安装；真浏览器量到 `[true,5,true]`，而 Chrome profile 仍是 `false`。

### 五、`history.length` **谁都不改**

池子里 `pushState` / `replaceState` 出现 **0 次** —— 样本里的 `9` 是浏览器自己的数字。
所以「读它、但不写它」，并且测试断言三份 body 里都不出现这两个词。

### 六、又踩了同一个坑（第三次）

第一版 `BodyJs()` 用转义拼接，结果每个 `\\n` 落成**字面反斜杠 + n**、跑到字符串外面 —— 一个 SyntaxError，
浏览器整份吞掉，`maxTouchPoints` 停在 10。改成 C# 原始字符串（`"""`）后立刻正确。

> **同一个错误（转义 / 括号）已经三次了。这不再是运气问题，是我该改用 raw string 作为默认写法。**

### 七、这一轮的一句话

> 「装了屏幕」不等于「装了手机」。**一台声称是手机的设备，得在每一个会被问到的地方都是手机。**
'''

if "## 手机的**触觉面**与那道闸门" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("touch surface documented")
else:
    print("already present")
