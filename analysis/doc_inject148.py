import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 两层表面接进注入链，并且**按声称的引擎开关**（第 148 轮）

R146 挖出 WebAssembly 面，R147 挖出 iPhone 面 —— 两个都只是**模型**，一个都没装上去。
这一轮把两段都缝进桥的 per-realm `apply`。

### 一、为什么必须进 `apply`

因为挑战帧是**读自己那个 realm** 的 WebAssembly 和 Screen，不会去问父窗口。
桥本来就有 per-realm 结构（`apply(W)` + `PATCHED` WeakSet + frame 重放），所以两个占位符：

```
__SURFACE_DEF__     ← 在 const apply 之前
__SURFACE_CALL__    ← 在 apply 末尾（每个 realm 都过）
```

### 二、闸门才是这轮的重点

```csharp
if (MobileSurface.IsAppleUserAgent(userAgent) || WebAssemblySurface.ShouldPatch(userAgent)) { … }
else surfaceDef = "const applySurface = (W) => {};";
```

理由两条，方向相反：

| 表面 | 为什么不能无条件装 |
|---|---|
| WebAssembly 计数 | 那些数字**是 Blink 的真实值**。一个声称 Chromium 的 profile **本来就诚实**，改了反而是新的谎 |
| iPhone 几何 | 这些数字描述 **402×874 的手机**。装在声称 363×684 桌面的 profile 上，等于「用一个不自洽换另一个不自洽」 |

> **补丁不是可以到处撒的谎，它只修正一处具体的不一致。**

### 三、几何只在顶层，钉箱处处生效

`MobileSurface.BodyJs()` 里：

```js
const isTop = (() => { try { return G === G.top; } catch (e) { return false; } })();
…
if (isTop) { innerWidth / innerHeight / outerWidth / outerHeight / devicePixelRatio }
// clientWidth / clientHeight 的 pin 在 if 之外 —— 挑战帧自己的比例也要为 1
```

这正是 R147 那条 frame 规则的代码形态。

### 四、五条测试

占位符在、调用在 `apply` **内部**（搜索从脚本字面量起算，避开 Replace 行里的同名占位符 ——
这个坑第一版就踩了）、闸门四例（iPhone / Chrome / Edge / 桌面 Safari）、
几何只在顶层而钉箱处处、两段都不 `throw` 且括号配平、非 Apple profile 装的是**空函数而不是错的函数**。

### 五、这一轮的一句话

> 两轮的证据到这一轮才第一次走到运行路径上。
>
> **模型正确、测试通过、但没接进去 —— 那叫笔记，不叫实现。**
'''

if "## 两层表面接进注入链" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("injection documented")
else:
    print("already present")
