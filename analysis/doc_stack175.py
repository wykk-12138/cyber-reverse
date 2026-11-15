import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 品牌校验抛出的错误，堆栈里不能有**自己的帧**（第 175 轮）

```
// A native IDL brand check throws from inside the engine, so the error's stack has no JS frame for the check at
// all: in JSC the top frame is the accessor itself, rendered 'get userAgent@[native code]', and the next frame is
// the caller. Ours is built in JS, so the stack carried the override's own frame -- at this script's URL, with a
// line and column -- and the Error wrapper's frame on top of it. Both are pure artifacts of this file.
```

### 一、机制

```js
// Captured ONCE, here. Reading Error.captureStackTrace at throw time would call whatever the page has installed
// on it -- announcing every brand-check throw and handing the probe a live reference to the installed getter.
const nativeCapture = typeof Error.captureStackTrace === 'function' ? Error.captureStackTrace : null;
```

抛错时：`nativeCapture(err, getter)` 把 getter **及其以上**的帧全部丢掉，然后**插一行假的原生帧**：

```
TypeError: Illegal invocation
    at get platform (native)
    at …调用者的帧…
```

实测正是如此 —— 第二行就是 `at get platform (native)`。

### 二、为什么「只读一次」很重要

若在抛错时读 `Error.captureStackTrace`，就是调用**页面装上去的那个**：每抛一次等于通知一次，
而且把装好的 getter 作为第二个参数**交到探针手里**。

> **在一个可被改写的内建上取值，等于把遥控器交给对方。**

### 三、这一轮的一句话

> 原版连**错误的形状**都照抄：不只「抛什么」，还有「抛的时候栈看起来像谁抛的」。
>
> **栈也是一份供词。**
'''

if "## 品牌校验抛出的错误" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("stack elision documented")
else:
    print("already present")
