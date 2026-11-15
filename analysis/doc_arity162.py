import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 三元组的另外两个：`length` 与 `name`（第 162 轮）

原版 shim 的条目是**三元组**：`{name, length, src}`。R161 只伪装了 `src`，
还把 `length` **从「刚被替换掉的那个函数」抄**——那是 shim 自己。

一个写成 `function () { … }` 的 shim，`length` 报 0，而平台的 `createEvent` 报 1。
**这是一条表达式就能读出来的差别。**

### 一、所以 arity 从**接口**来，不从实现来

```
getVoices   0     SpeechSynthesis.getVoices()
createEvent 1     Document.createEvent(type)
getParameter 1    WebGLRenderingContext.getParameter(pname)
toString    0     Function.prototype.toString()
```

`NativeArity.For(name)` 查表；表里没有就**抛**（构建期就炸，不是运行时静默）。
getter 的 `name` 是 `"get <prop>"`、`length` 是 0 —— 这一半之前碰巧是对的，**碰巧对不等于对**。

### 二、生成的 pass 现在写的是表里的数字

```js
M.asNative(owner.createEvent, 'createEvent', 1);   // 不再是 .length
```

测试断言 `DoesNotContain(".length)")` —— 旧形状必须消失。

### 三、真浏览器读回三元组

逐行读 `fn.name` / `fn.length`，并与 `NativeArity` 比对；另读一个 getter，
确认它是 `get plugins` / `0`。全部通过。

### 四、这一轮的一句话

> 三轮才把三元组读完：R160 读 `src`，R162 读 `name` 与 `length`。
> 每一轮我都以为「最重要的那个已经做了」。
>
> **一个被记录成三元的证据，通常三个都要做 —— 否则作者不会写成三元。**
'''

if "## 三元组的另外两个" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("arity documented")
else:
    print("already present")
