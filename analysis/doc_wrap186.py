import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 只包一层窗口，别的都不碰（第 186 轮）

R180 把整个键序层建完却**没接线** —— 接上之后 `mutation-check.py` 挂住：一条被变异关掉的「重放路由」，
在包裹后的 `Object.getOwnPropertyNames` 之下永远等下去。

这一轮只接**最小的一片**：

```js
['getOwnPropertyNames', 'keys'].forEach((name) => {
  const original = Object[name];
  const wrapped = { wrap() {
    const target = arguments[0];
    const all = original.apply(this, arguments);
    if (!G.__topList) return all;
    const isWindow = target === G || (!!target && target.window === target && !!target.document);
    if (!isWindow) return all;                       // ← 别的对象原样放过
    return G.__topList(all, all, name === 'keys');
  } }.wrap;
  …
});
```

### 一、为什么只包窗口就够

api.js 真正调用的只有两处，而且都对着 `window`：

```js
function sr(){ return Object.keys(window).sort().join(",") }   // → wdata → wasm
```

页面里其他对象（数组、DTO、`document.body`）的行为**一个字节都不变** —— 这正是「不挂工装」的关键：
被变异关掉的那条重放路由走的是普通对象，`isWindow` 为 false，直接 `return all`。

### 二、实测

```
probe = [true,"b,a","b,a",3]
          ↑页面变量排在最后 ↑普通对象顺序不变 ↑Object.keys 也是 ↑源码三行（已伪装）
RealmReplayTests + SurfaceRuntimeTests + PatchJournalTests → 21 条全绿（重放路由未受影响）
```

### 三、这一轮的一句话

> 上一轮我学会了「排序比删除更接近原版」，这一轮学会了**「只包该包的那一个对象」**比「包住所有对象」更安全。
>
> **能力越大越要先问：这个能力真的需要覆盖那么大范围吗？**
'''

if "## 只包一层窗口，别的都不碰" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("documented")
else:
    print("already present")
