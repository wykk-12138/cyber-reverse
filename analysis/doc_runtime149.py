import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 真浏览器冒烟：两段 JS **根本没在跑**（第 149 轮）

前一轮用字符串断言证明「两段拼进了脚本」。这一轮启动真实 headless Chromium，把同一份脚本装进页面，
再把挑战帧会读的东西读回来 —— 结果四次红。

### 一、四次红，四个不同原因

| 症状 | 真实原因 |
|---|---|
| 全都没生效 | ① **`Page.addScriptToEvaluateOnNewDocument` 只对「下一个文档」生效** —— 在 `about:blank` 上求值量到的是打过补丁之前的浏览器 |
| 仍然全都没生效 | ② `about:blank` 根本不触发新文档脚本，得导航到真实文档 |
| 仍然全都没生效 | ③ **`applySurface(W)` 的形参叫 `W`，而 `WebAssemblySurface.BodyJs()` 里 `const W = G.WebAssembly`** —— 同作用域重名 = **SyntaxError**，浏览器把它吞掉，整份脚本静默不执行 |
| `outerHeight = 769` 而非 874 | ④ 桥以 **363×684** 启动窗口，而 profile 声称 874 —— 宿主窗口比声称的矮 |

诊断的关键一步是**看 `navigator.webdriver`**：补丁本该删掉它，结果它是 `boolean` ——
**说明整份脚本一行都没跑**，而不是「某段没跑」。这一步把猜测变成了结论。

### 二、三个教训，每个都可以复用

1. **「脚本装上了」不等于「脚本在跑」。** 要在**新文档**里、读**被补丁影响的属性**来验证，
   而不是断言字符串、也不是在旧文档上求值。
2. **SyntaxError 是最安静的失败。** 注入脚本外层套着 `try/catch`，一个重名 `const`
   会让整份脚本变成空操作，而没有任何报错传给调用方。
3. **几何的矛盾可能来自窗口尺寸，不是来自补丁。** 原版注释早就写了：
   > the host window must actually be this size or clicks land outside the viewport we claim —
   > one impossibility traded for another. See SolverWindow sizing.

### 三、这一轮的处理

- 三条原因都修好，`SurfaceRuntimeTests` 五条**真浏览器**断言全绿：
  WebAssembly 计数 `[16,1,2,6,6]`、JSPI 三名消失、两个 `type()` 返回 `{kind}`、
  `createEvent('TouchEvent')` 返回 `["object","",0,false]`、缩放比 `[402,402,684,684]`、
  子元素 `clientWidth` 仍是自己的 50、Chromium profile 下 JSPI **仍在**（闸门有效）。
- **第④条不修，钉住**：`outerHeight` 目前是宿主窗口高度，测试显式断言
  `parts[6] < MobileSurface.ScreenHeight` 并注明「窗口尺寸要跟随 profile」。
  **这是下一轮的具体任务，不是可以顺手抹掉的差异。**

### 四、这一轮的一句话

> 上一轮我写的是「模型正确、测试通过、但没接进去 —— 那叫笔记」。
> 这一轮发现：**接进去了，也可能是死的。**
>
> **能跑和看起来接好了，是两件完全不同的事；区分它们的唯一办法是真的跑一次。**
'''

if "## 真浏览器冒烟" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("runtime smoke documented")
else:
    print("already present")
