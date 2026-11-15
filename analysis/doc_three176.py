import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 校验抛什么话、用什么判据、留什么栈（第 176 轮）

上一轮我把「抛 `Illegal invocation`」当成对的。这一段注释推翻了它，并且把**三件事**一次说清：

```
// The message follows WebKit's wording rather than Blink's "Illegal invocation", since WebKit is the engine being
// presented.
throw new TypeError('The ' + label + '.' + name + ' getter can only be used on instances of ' + label);

// The brand is checked with Object.prototype.toString, NOT instanceof. Child realms are patched by copying this
// descriptor into them, so the closure below keeps the PARENT's constructor -- and instanceof is realm-scoped, so
// `this instanceof Navigator` is false for a perfectly good navigator inside an iframe.

// Armed with an EMPTY head on purpose. Eliding our own frames is measured and safe; the native frame a real engine
// would show here is not -- WebKit adds no JS frame for an IDL brand check at all, so caller-frames-only is the
// faithful answer and inventing 'get x@[native code]' would be a guess in the payload.
ELIDE = [getter, ''];
```

### 一、三处修正

| 项 | 上一轮（R173–R175） | 原版 |
|---|---|---|
| 文案 | `Illegal invocation`（Blink） | `The Navigator.platform getter can only be used on instances of Navigator`（WebKit） |
| 判据 | 硬编码 `'[object Navigator]'` | **安装时**捕获 `brand = Object.prototype.toString.call(target)`，再用它比对 |
| 栈 | 插入假帧 `at get platform (native)` | **只删自己的帧**，不造假帧 —— 「造假帧是猜测」 |

### 二、为什么「造假帧」是错的

我上一轮为了让栈「像原生」插了一行 `at get platform (native)`。原版的判断更严格：

> eliding our own frames is measured and safe; the native frame a real engine would show here is not.

**能删的删，不能确定的不要编。** 这条标准比「像」更高：宁可少一行，也不多一个猜的。

### 三、`label` 从哪来

```js
const label = (target && target.constructor && target.constructor.name) || '';
```

不是写死 `'Navigator'` —— 同一个 `value()` 也装到 `Screen`、`CanvasRenderingContext2D` 等对象上。

### 四、这一轮的一句话

> 同一个错误，原版写的是**三种正确**：正确的话、正确的判据、正确的栈。我三样都差一点。
>
> **「差不多像」和「就是它」之间的距离，正好是一个探针。**
'''

if "## 校验抛什么话、用什么判据、留什么栈" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("corrections documented")
else:
    print("already present")
