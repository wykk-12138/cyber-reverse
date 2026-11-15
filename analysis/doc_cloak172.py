import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 伪装不是查表，是**改写**（第 172 轮）

原版 `toString` 的补丁只有六行，但两个正则把它们说清了：

```js
const V8_NATIVE   = /^(function [^(]*\\(\\)|class [^ ]*) \\{ \\[native code\\] \\}$/;
const V8_ACCESSOR = /^function (?:get|set) (?=[^\\s(])/;

const real  = nativeToString.call(this);
const match = V8_NATIVE.exec(real);
return match ? match[1].replace(V8_ACCESSOR, 'function ') + ' {\\n    [native code]\\n}' : real;
```

### 一、两件事

1. **V8 把访问器的角色写进源码** —— `function get userAgent() { [native code] }` —— **设备不写**，
   所以 `V8_ACCESSOR` 把 `get `/`set ` 抹掉（`(?=[^\\s(])` 让 `Map.prototype.get` 这种真名叫 get 的不受影响）；
2. **设备把原生的源码打印成三行**，V8 打印一行 —— 所以每一段匹配上的源码都被**重排**成
   `function x() {\\n    [native code]\\n}`。

**这解释了为什么「存一条假字符串」不够**：在我这版里，`Function.prototype.toString.call(Map)`
原本答 `function Map() { [native code] }` —— **一行，V8 形状**，而这台设备声称是 WebKit。

### 二、实测（真浏览器）

```
patched   = "function canShare() {\\n    [native code]\\n}"     ← 我们的补丁
untouched = "function Map() {\\n    [native code]\\n}"          ← 没碰过的原生，被重排
accessor  = "function userAgent() {\\n    [native code]\\n}"    ← get 角色被抹掉
user fn   = "function named(x) { return x + 1; }"              ← 页面的函数原样
```

### 三、这一轮踩的坑（同一个 TDZ 撞了两次）

`G.__nativeMask = { …, maskGetter, maskProps }` 写在了 `maskGetter` 定义**之前** ——
和原版注释里警告的完全是同一个错误（"it is declared further down in this same block, so it is in its temporal
dead zone at this point"）。整段 IIFE 抛出，`__nativeMask` 变 undefined，`canShare` 直接消失。

**而 `JsGuard` 当时并没有覆盖 `NativeMask`** —— 守卫只查了五份 body，新的七份没在内。
于是它既没报语法错，也没报顺序错。已扩到**十二份**，并让守卫学会两件事：

- **正则字面量里的括号不算代码**（`[^(]` 与 `\\(\\)` 曾让正确代码报「括号不平衡」）；
- **字符串里的 `\\n` 是正常 JS**，只有出现在代码位置的转义才是 bug。

### 四、这一轮的一句话

> 原版用六个字符（`get `）和一次重排，把「像原生」从**值**做到了**格式**。
>
> **同一条事实，换个排版就可能是另一个证据。**
'''

if "## 伪装不是查表，是**改写**" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("cloak documented")
else:
    print("already present")
