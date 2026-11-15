import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## `prototype` 的有无，是一行语法的事（第 171 轮）

原版那三个 helper 里藏着最关键的一行：

```js
const renamed = (fn, name) => { try { fn.name via defineProperty } catch {} return fn; };
const noProtoMethod = (impl, name) => renamed(({ m() { return impl.apply(this, arguments); } }).m, name);
const noProtoGetter  = (impl, name) => renamed(Object.getOwnPropertyDescriptor(
  { get m() { return impl.call(this); } }, 'm').get, name ? 'get ' + name : '');
```

**`({ m() {} }).m` 是方法简写** —— 它和普通函数表达式几乎一样，**唯独没有 `prototype`**。
而 WebIDL 操作正是这样。`delete fn.prototype` 也能做到，但简写是**根本不创建**。

### 一、为什么这件事重要

一个 `function () {}` 有 `prototype`，一个 WebIDL 操作没有。检测器一行就能分开：

```js
'prototype' in navigator.canShare   // 设备：false
'prototype' in navigator.canShare   // 未处理：true
```

### 二、实测

```
[["canShare","function",false,true,"canShare",1],
 ["share","function",false,true,"share",1]]
   ↑类型      ↑无 prototype ↑prototype 为 undefined ↑name ↑arity
```

而 `credentials` 的四个方法**故意保留** `prototype` —— 原版说「四个函数在设备上是普通函数表达式
（它们有 `.prototype`）」，实测 `'prototype' in navigator.credentials.get === true`。

> **同一个文件里，两种 shim 对 `prototype` 的要求相反。** 不是随手写的，是照设备抄的。

### 三、顺带记下：`toString` 的伪装原版做得更细

```js
const real = nativeToString.call(this);
const match = V8_NATIVE.exec(real);
return match ? match[1].replace(V8_ACCESS…) : …;
```

它不存一段假字符串，而是**读真实源码再用正则改写**（`V8_NATIVE` / `V8_ACCESS`）。
我这一版用的是「存一条 `[native code]` 文本」，行为上等价但更粗 —— 记为后续可细化项。

### 四、这一轮的一句话

> 我一直把「像原生」当成字符串问题。这一轮发现它也是**语法问题**：
> 一个函数有没有 `prototype`，取决于它是怎么写出来的。
>
> **伪装不只藏在值里，也藏在值被创建的方式里。**
'''

if "## `prototype` 的有无" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("protoless documented")
else:
    print("already present")
