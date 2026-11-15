import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 顺序重排：做到了 28/50，但**相对顺序 100%**（第 165 轮）

R159 只把 `NAV_ORDER` 记下来，没有执行。这一轮把 `reseat` 真跑起来。

### 一、机制（原版自己就在 Screen 上用）

```js
const d = Object.getOwnPropertyDescriptor(target, name);
if (!d || !d.configurable) return;      // 不可配置就搬不动
delete target[name];
Object.defineProperty(target, name, d); // 重加 = 移到末尾
```

按顺序依次执行，可配置的属性就会排在末尾、彼此保持给定次序。

### 二、实测（真浏览器）

```
before own = [maxTouchPoints, scheduling, userActivation, geolocation, ink, …]
after  own = [scheduling, ink, doNotTrack, webkit*, windowControlsOverlay, vibrate,
              constructor, standalone, hardwareConcurrency, …, javaEnabled]
recorded names present on the prototype: 28/50
relative order preserved: True
```

三条结论，都要照实写：

1. **不可配置的 Blink 名字永远在前面**（`scheduling`、`ink`、`webkitTemporaryStorage`…）—— 任何 reseat 都搬不动它们；
2. **50 个记录名里只有 28 个真的在 `Navigator.prototype` 上** —— 其余在 `Object.prototype` 或本引擎没有；
3. **在这 28 个之间，记录的相对顺序 100% 达成。**

所以断言写的是**测量到的事实**，不是理想：

```csharp
Assert.True(relativeOrder, "the recorded relative order is achieved among the properties that exist");
Assert.True(present.Count >= 20);
```

### 三、顺手纠一个数字

R159 的注解说 `NAV_ORDER` 是 **49** 项 —— **列表本身是 50 项**。测试里的常量改成从列表读。

> **数字要从数据里取，不要从描述数据的那句话里取。**

### 四、这一轮的一句话

> 「顺序重排」听起来是一个动作，实际是**一次谈判**：浏览器说哪些能搬、哪些不能，我们只能搬能搬的。
>
> **做不到 50/50 不是失败，假装做到了才是。**
'''

if "## 顺序重排：做到了 28/50" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("reseat documented")
else:
    print("already present")
