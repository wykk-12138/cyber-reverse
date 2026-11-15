import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 把样本变成待办：指纹部分三栏审计，并关掉两栏（第 156 轮）

R152 的样本读起来像一份清单。这一轮把它分成三栏，然后**能关的都关掉**。

### 一、三栏

| 栏 | 成员 |
|---|---|
| **已有**（9） | `userAgentData.brands/mobile/platform`、`userAgent`、`platform`、`language`、`hardwareConcurrency`、`deviceMemory`、`webdriver_detect` |
| **已装**（7，本轮） | `connection.{effectiveType,rtt,saveData,downlink}`、`plugins`、`automationEnabled`、`screen.darkMode.enabled` |
| **装不了**（5） | `canvas-print-100-999`、`canvas-print-detailed-100-999`、`canvas_spoofing`、`js-errors`、`font-*` |

第三栏是这一轮最想保住的东西：

> **canvas 哈希不是可以覆盖的属性，而是跑一遍 canvas 的结果。**

一份声称能「安装」它的隐身脚本，是在夸自己的射程。`canvas_spoofing` 与 `js-errors` 更是原版**自己的记账**，
和它们描述的那些读数塞在同一个 namespace 里。

### 二、两处实测纠正

**① 插件是 5 个，不是 3 个。** 样本 `navigator.plugins.count = 5`，五个名字共享
`internal-pdf-viewer`。replica 之前是 3 —— 连「数一下」都能被抓。
慢速测试 `ChromiumStealthTests` 里那条 `Assert.Equal(3, …)` 已改成 5，并注明依据是样本。

> **数字要从样本里抄，不要从上一版代码里抄。**

**② 顺序决定胜负。** 引擎块最初插在 `apply` 的**开头**，于是它设的 5 个插件被后面那段旧的 3 个覆盖 ——
实测读到 `[3, [...]]`。移到 `apply` **末尾**才对。

移动时还顺手犯了个错：把调用插在了 `apply` 的闭合 `};` **之后**，多出一个 `};` ——
整份脚本 SyntaxError、静默不执行、六个断言同时红。**这是同一个坑第二次踩**（R149 也踩过）。

### 三、真浏览器量到的结果

```
plugins     = [5,["PDF Viewer",…],["internal-pdf-viewer",…]]
connection  = ["4g",50,false,10]
flags       = [false,false]        // navigator.automationEnabled, screen.darkMode.enabled
```

六条真浏览器断言全绿。

### 四、这一轮的一句话

> 三栏里最容易被忽略的是**第三栏**：把「装不了」写下来，比把「还没装」写下来更难，
> 因为它要求承认射程有限。
>
> **一份诚实的清单，必须包含「做不到」那一栏。**
'''

if "## 把样本变成待办" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("coverage documented")
else:
    print("already present")
