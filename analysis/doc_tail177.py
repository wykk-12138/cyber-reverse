import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## `enumerable !== false` —— 一个表达式，不是常量（第 177 轮）

`value()` 的收尾这一段以前没读过：

```js
Object.defineProperty(getter, 'name', { value: 'get ' + name, configurable: true });
Object.defineProperty(target, name, {
  get: getter,
  configurable: true,
  enumerable: enumerable !== false,
});
record(target, name);
```

replica 一直写死 `enumerable: true`。**对本工作区装的每个成员恰好都对，但作为形状是错的** ——
原版把它做成参数：默认 `true`，调用点说 `false` 就是 `false`。

### 一、为什么默认是 `true`

因为设备就是那样：`for (var k in navigator)` 数得出 32 个键，这几个成员都在里面。
实测（真浏览器）：

```
[["platform",true,true,true,false],["userAgent",true,true,true,false],
 ["vendor",true,true,true,false],["appVersion",true,true,true,false]]
   ↑accessor ↑enumerable ↑configurable ↑无 value 字段
for (k in navigator) 里有 platform  →  true
```

### 二、同一段里还有两个形状

**`method()`** —— 替换函数的**arity 取自原函数**，而且原函数作为**第一个参数**交给 builder：

```js
const replacement = noProtoMethod(function () { return build.call(this, original, arguments); });
Object.defineProperty(replacement, 'length', { value: original.length, configurable: true });
asNative(replacement, name);
target[name] = replacement;
```

**`reseat()`** —— R165 已实现，逐行核对**完全一致**：

```js
const listed = order.filter((k) => kept[k]);
const rest = own.filter((k) => kept[k] && order.indexOf(k) < 0);
const seq = listed.concat(rest);
seq.forEach((key) => { try { delete proto[key]; } catch (e) { } });
seq.forEach((key) => { try { Object.defineProperty(proto, key, kept[key]); } catch (e) { } });
```

> 「设备没列出的成员保持相对顺序、落在末尾；不可配置的成员不动」—— 我们两周前就是按这句写的。

### 三、这一轮的一句话

> 三个形状，一个是我抄错（`enumerable`），两个是我早就抄对（`method` 的 arity、`reseat` 的顺序）。
>
> **核对的价值不只在发现错，也在确认对 —— 后者让「对」从运气变成依据。**
'''

if "## `enumerable !== false`" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("tail documented")
else:
    print("already present")
