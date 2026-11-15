import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 补丁是两件事：行为，以及它**自称是什么**（第 160 轮）

原版 `CRED_SHIM` 的每一项都带三样东西：

```
{"name": "get", "length": 1, "src": "function(e){if(!e?.publicKey){return O.get(e)}…"}
```

**为什么要记 `length` 和 `src`？** 因为它们**都会被读**：`fn.length` 是第二个，
`Function.prototype.toString` 是第三个。一个改了行为却答「`function () { … }`」的补丁，
**是在自报身份**。

### 一、replica 之前的样子

补了 `getVoices`、`createEvent`、十几个 getter —— **一个都没伪装 toString**。
任何一个检测器只要对那个 getter 调一次 `Function.prototype.toString.call(...)`，就看见源码。

### 二、`NativeMask`：注册表 + 一次覆盖

```js
const FAKES = new WeakMap();
const protoToString = Function.prototype.toString;
function toString() {
  const fake = FAKES.get(this);
  return fake !== undefined ? fake : protoToString.call(this);
}
asNative(toString, 'toString', 0);      // 连覆盖本身也要伪装
Object.defineProperty(Function.prototype, 'toString', { value: toString, … });
```

配 `asNative(fn, name, length)` 与 `maskGetter(target, prop)` 两个工具。
**安装顺序**：`NativeMask.BodyJs()` 在 `surfaceBody` 的最前面 —— 后面每一处补丁都能登记自己。

### 三、真浏览器量到

- 被补的 `navigator.plugins` getter：`toString` 答 `[native code]`；
- `Function.prototype.toString` 自身：也是 `[native code]`；
- `Element.prototype.clientWidth` 的 getter：同样；
- **页面的普通函数仍然打印源码**（`return x + 1`）——
  这条断言很重要：**伪装必须只盖住自己，不能把整个页面的 `toString` 变成静音**。

### 四、这一轮的一句话

> 上一轮我记下了 `CRED_SHIM` 带 `src`，还把它当「有趣的花边」。
> 这一轮才想明白：**它不是花边，它是规格 —— 说明 shim 的伪装有一半在文本上。**
>
> **证据里最不像证据的那一项，往往是你还没读懂的那一项。**
'''

if "## 补丁是两件事" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("mask documented")
else:
    print("already present")
