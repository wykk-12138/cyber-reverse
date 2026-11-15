import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## `credentials` 的答案不是虚拟认证器，是**转发**（第 170 轮）

原版那段注释比前面几段都长，一次说清三件事，而 replica 三件都错：

```
// Chrome for iOS does not expose WebKit's CredentialsContainer to the page. Its passkey script
// (components/webauthn/ios/resources/passkey_controller.ts, injected into every frame) caches the native one and
// then runs Object.defineProperty(navigator, 'credentials', {value: credentialsContainer})
// -- an OWN property of the navigator INSTANCE, non-enumerable, non-writable and non-configurable, holding a plain
// object of four script functions. Two things follow on the device and both were wrong here:
//   - for (k in navigator) SKIPS credentials, because a non-enumerable own property shadows the enumerable one on
//     the prototype. hCaptcha ships that loop verbatim as topLevel.nv: the device sends 32 keys, this engine sent
//     33 with `credentials: {}` after audioSession.
//   - the value is a plain Object whose methods print script source, not an [object CredentialsContainer] whose
//     methods print [native code].
// The prototype member stays, so getOwnPropertyNames(Navigator.prototype) keeps the device's 41 names.
```

### 一、原版**没有实现 WebAuthn**

它做的是：拿引擎自己的容器 → 四个方法各包一层转发 → 伪装源码。

```js
const fn = function () {
  const target = native && native[row.name];
  if (typeof target !== 'function') return Promise.reject(new TypeError('navigator.credentials is unavailable'));
  return target.apply(native, arguments);
};
```

**比虚拟认证器更小、也更忠实。** R163 把这件事写成「开放项」，这一轮可以关掉了 —— 关的方式是**换一个问题**。

### 二、三个可测的事实

实测（真浏览器）：

```
[true,false,false,false,-1,"function",1,"function get() { [native code] }"]
  ↑own ↑非枚举 ↑非可写 ↑非可配 ↑for-in 里没有 ↑是函数 ↑arity 1 ↑看起来原生
'credentials' in Navigator.prototype  →  true   （原型成员也在，影子关系成立）
```

- **非枚举自有属性** → `for (k in navigator)` **跳过**它 → 32 键而非 33；
- **arity 与 `[native code]`** → 三元组的另两项；
- **原型成员保留** → `getOwnPropertyNames(Navigator.prototype)` 仍是设备的那个数量。

### 三、`canShare` / `share`：数据属性，不是访问器

```
// WebIDL operations are DATA properties; value() installs a brand-checked accessor, which is right for attributes
// like audioSession and wrong here, so these are defined directly.
```

`canShare({title:'x'})` → `true`，`canShare({})` → `false`；
`share` 拒绝时用的正是 WebKit 那句：

```
The request is not allowed by the user agent or the platform in the current context.   (NotAllowedError)
```

### 四、这一轮的一句话

> R163 我写下「虚拟认证器未实现」，把它当成一块要补的空白。R170 的注释告诉我：
> **原版也没实现 —— 它转发了。**
>
> **一个「未实现」的开放项，有时是因为问题问错了，而不是因为活儿没干。**
'''

if "## `credentials` 的答案不是虚拟认证器" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("credentials documented")
else:
    print("already present")
