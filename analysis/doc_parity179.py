import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## V8 的话 vs JavaScriptCore 的话（第 179 轮）

「core 三个」我以为是引擎加固，读完发现是**引擎方言**。原版的 `MESSAGES` 表只有四行，每一行都是
Blink 的句子会暴露身份的地方：

```js
const MESSAGES = {
  "nullProp": "null is not an object (evaluating 'null.x')",
  "notFunction": "(void 0) is not a function. (In '(void 0)()', '(void 0)' is undefined)",
  "badArrayLength": "Array length must be a positive integer of safe magnitude.",
  "jsonCircular": "JSON.stringify cannot serialize cyclic structures."
};
```

### 一、五处补丁

| 项 | V8 | 设备（JSC） |
|---|---|---|
| 栈格式 | `    at fn (url:line:col)` | `fn@url:line:col` |
| `stack` 描述符 | 自有 **accessor** | **可写数据属性** |
| `Error.stackTraceLimit` | 10 | 100 |
| `new Array(-1)` | 另一句话 | `Array length must be a positive integer of safe magnitude.` |
| `JSON.stringify` 循环 | 另一句话 | `JSON.stringify cannot serialize cyclic structures.` |

还有一行小到容易漏：**`Function.prototype.bind`** —— V8 给绑定函数起名 `function bound () {…}`，JSC 不起。

### 二、为什么不用 `Error.prepareStackTrace`

```
// Error.prepareStackTrace would also reformat, but assigning it makes `typeof Error.prepareStackTrace` report
// 'function' where the device says 'undefined', trading one tell for another. Wrapping construction avoids that.
```

**用「更明显的假」换「不明显的假」，是亏的。**

### 三、这一轮踩的两个坑

1. **方法简写不能当构造函数**：`{ [name](...args) {} }[name]` 没有 `[[Construct]]`，
   `new Error('x')` 直接答 `Error is not a constructor`。错误构造器**必须**是函数表达式；
   `Array` 同理。R171 我要的是「没有 prototype」，这里要的是「能 new」—— **形状服务于用途**。
2. **JSC 的 `stack` 只有帧，没有消息行**：`toJscStack` 把不匹配的行丢掉是**对的**，
   消息在 `e.message` 上。实测 `get platform@<anonymous>:633:21`。

### 四、这一轮的一句话

> 我一直以为「伪装」是让值看起来对，这一轮发现还要让**错误的措辞、栈的排版、报错的类名**看起来对。
>
> **身份不只在成功路径上泄露，也在失败路径上泄露。**
'''

if "## V8 的话 vs JavaScriptCore 的话" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("parity documented")
else:
    print("already present")
