import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 又一段注释，三处纠正（第 169 轮）

`value(Navigator.prototype, 'languages', …)` 之后紧接的是 `NAV_PRUNE` 的**本体**，它把 R163 的三处判断都纠正了。

### 一、prune 是**白名单**，不是黑名单

```js
NAV_PRUNE = (realm) => {
  const proto = realm && realm.Navigator && realm.Navigator.prototype;
  if (!proto) return;
  nativeOwnNames(proto).forEach((key) => {
    if (!NAV_KEYS.has(key) && key !== 'constructor') { try { delete proto[key]; } catch (e) { } }
  });
```

R163 我写了九个名字去删。原版是**留下 51 个、其余全删**。

> 黑名单要在引擎每发布一个新接口时补一条；白名单**不会落后**。

我们的脚本还有几处把成员装在**实例**上（`deviceMemory` 等），所以 sweep 走**原型 + 实例**两遍 ——
这是同一规则的超集，实测逼出来的：不改的话 iPhone profile 仍然能读到 `navigator.deviceMemory`。

### 二、`audioSession`：`{}` + 一个 tag

```
// iOS exposes navigator.audioSession, which Blink has no equivalent for, so the prune above cannot restore it
// -- it was never there. hCaptcha serialises each navigator member with JSON.stringify, and on the device this
// one comes back as {} exactly like gpu and clipboard do, so a bare object with the right toStringTag reproduces
// what it reads.
const session = {};
Object.defineProperty(session, Symbol.toStringTag, { value: 'AudioSession', configurable: true });
Object.defineProperty(session, 'type', { value: 'auto', enumerable: false, configurable: true });
value(proto, 'audioSession', session);
```

**shim 不必模拟 API，它只需复现「读的人序列化出来的东西」。** 实测：

```
JSON.stringify(navigator.audioSession) → "{}"
Object.prototype.toString.call(…)      → "[object AudioSession]"
navigator.audioSession.type            → "auto"
```

### 三、`plugins` / `mimeTypes` 要**留原生**

```
// navigator.plugins / mimeTypes are left NATIVE. Blink's lists are the spec's five PDF viewers (filename
// "internal-pdf-viewer") and two PDF mime types, which is exactly what the iPhone reports: every device
// HAR -- iOS 26.6.1 (chrome-topps, tcg, topps-cp x2) and iOS 27.0.1 (shopify-cp-solve-28-10) -- sends
// topLevel.nv.plugins as five "internal-pdf-viewer", and the device collector reads lengths 5 / 2. An
// override here used to empty both, on the mistaken belief that WebKit's lists are empty, so every bot
// payload carried plugins: [] in plaintext.
```

R156 花了功夫「装五个插件」，**其实 Blink 本来就是五个**；而更早的 replica 装的是**三个**、`mimeTypes` 为空 ——
**比什么都不做更糟**。实测（原生，未打补丁）：`[5,2,"internal-pdf-viewer"]`。

### 四、这一轮的一句话

> 一段注释纠正了三处：机制（黑名单→白名单）、形状（`audioSession` 是 `{}`）、以及**「不要动」也是一种实现**。
>
> **最省力的修复，有时是删掉一段代码。**
'''

if "## 又一段注释，三处纠正" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("corrections documented")
else:
    print("already present")
