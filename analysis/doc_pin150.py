import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 窗口尺寸跟随 profile，几何要**反复钉**（第 150 轮）

上一轮留下的第④条（`outerHeight` 报 769 而不是 874）这一轮解决，中间踩了两层。

### 一、第一层：启动尺寸

```csharp
public string WindowSizeArgument(string? userAgent) =>
    MobileSurface.IsAppleUserAgent(userAgent)
        ? $"--window-size={MobileSurface.ScreenWidth},{MobileSurface.ScreenHeight}"   // 402,874
        : WindowSizeArgument();                                                        // 桌面仍 363,684
```

`LaunchAsync(…, string? userAgent = null)` 把它透传 —— **声明什么尺寸，就用什么尺寸启动**。
这正是原版注释要求的：`the host window must actually be this size`。

### 二、第二层：赋值不够，getter 也会被覆盖

改成 `Object.defineProperty(G, name, { configurable: true, get: () => v })` 之后**仍然报 769**。
于是写了一个探针，量到三件事：

```
outerHeight: own = { kind: 'own', get: true, configurable: true }   proto = none
define attempt = ["ok", 874]        ← 当场生效
outerHeight now = 874
```

**结论**：属性的确可以覆盖，`defineProperty` 也成功 —— 但**浏览器在文档开始之后、窗口真正实现时又装了一遍自己的几何**，
把我们的 accessor 换掉了。769 是那一刻回来的。

### 三、修法：在浏览器「安顿几何」的那三个时刻重钉

```js
const pinAll = () => { pin('devicePixelRatio',3); pin('outerWidth',402);
                       pin('outerHeight',874); pin('innerWidth',402); pin('innerHeight',684); };
pinAll();
['DOMContentLoaded', 'load', 'resize'].forEach((ev) => G.addEventListener(ev, pinAll));
```

因为描述符是 `configurable: true`，每次重钉都替换掉浏览器刚装的那个。

### 四、结果

`SurfaceRuntimeTests` 的几何断言从「钉住差异」变成**等值断言**：

```
[402, 874, 3, 402, 684, 402, 874]
```

### 五、这一轮的一句话

> 昨天我写「这是下一轮的任务，不是可以顺手抹掉的差异」。今天抹掉了 —— 但**是量出原因之后抹的，不是假装它不存在**。
>
> **一个差值要么被解释，要么被消除；两者都不做的「先这样」会一直留在系统里。**
'''

if "## 窗口尺寸跟随 profile" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("geometry pinning documented")
else:
    print("already present")
