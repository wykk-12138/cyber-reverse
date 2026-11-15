import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 伪装终于有了调用者：22 行表 + 一趟最后的 pass（第 161 轮）

R160 把 `asNative` / `maskGetter` 造成了，**却一个都没登记** —— 这是本会话第五次「零件齐了没人调用」。
`MaskTargets` 就是调用者。

### 一、表是数据，不是代码

19 个 getter + 3 个函数，**每行带拥有者**：

```
G.navigator                plugins mimeTypes connection maxTouchPoints hardwareConcurrency
                           deviceMemory webdriver
G.Element.prototype        clientWidth clientHeight
G                          devicePixelRatio outerWidth outerHeight innerWidth innerHeight
G.Screen.prototype         width height darkMode
G.VisualViewport.prototype width
G.Performance.prototype    memory
G.speechSynthesis          getVoices
G.Document.prototype       createEvent
G.WebGLRenderingContext.prototype  getParameter
```

**为什么是数据**：测试可以逐行走。真浏览器里对每一行读描述符、问
`Function.prototype.toString`「你怎么说」——答源码的那一行就是自报身份的补丁。

### 二、pass 必须最后跑

```csharp
surfaceBody += MaskTargets.ApplyJs();     // 在 Engine/WASM/Mobile/Touches 之后
```

**尚未安装的 getter 无法被伪装** —— 所以顺序本身就是正确性。
`ThePassRunsLast` 断言它在 `MobileNavigator.BodyJs(userAgent)` 之后。

### 三、真浏览器逐行验证

22 行全部 `[native code]`（或 `absent`，因为某些平台上根本没有这个成员）。
断言是**逐行**的，不是抽样 —— 抽样会让第 20 行永远没人看。

### 四、这一轮的一句话

> 上一轮我说「补丁是两件事」。这一轮让那两件事**在同一处发生**：装补丁的 body 之后，
> 紧跟着一趟把这些名字全部登记为 native 的 pass。
>
> **机制和价值之间隔着的，通常只是一张表和一个调用点。**
'''

if "## 伪装终于有了调用者" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("mask pass documented")
else:
    print("already present")
