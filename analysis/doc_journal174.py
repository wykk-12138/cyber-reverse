import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 同源 iframe 有自己的构造函数（第 174 轮）

原版一句话说清了为什么要按**路径**记录补丁：

```
// Every patch is recorded with a realm-independent path ("Navigator","prototype") so it can be replayed into a fresh
// realm. An iframe gets its own constructors, so a same-origin child is otherwise completely unspoofed -- read
// iframe.contentWindow.navigator and the real Blink values come straight back.
```

```js
const pathOf = (target) => {          // ['Navigator','prototype'] / ['Intl','DateTimeFormat','prototype']
  if (target === G) return [];
  for (const name of KNOWN) {
    const holder = G[name]; if (!holder) continue;
    if (holder === target) return [name];
    if (holder.prototype === target) return [name, 'prototype'];
    for (const intl of INTL_NAMES) { … return ['Intl', intl]; … }
  }
  return null;
};
const record = (target, key) => { const path = pathOf(target); if (path) PATCHES.push({ path, key, from: target }); };
```

### 一、为什么「重跑整段脚本」不够

replica 原来靠「换一个 realm 再跑一遍 body」—— 能覆盖，但不精确：它只能补 body 碰过的对象，
而 `Intl.DateTimeFormat.prototype` 这类**三步路径**根本不在 body 的可达范围内。

journal 记录的是**「哪个对象上的哪个键」**，重放时按路径在新 realm 里解析出来，再把
**描述符原样**拷过去 —— 父窗口是数据属性的，子窗口也必须还是数据属性。

### 二、实测（真浏览器）

```
child = ["iPhone","iPhone",5,5,"function",true]
          ↑父     ↑子    ↑父 ↑子  ↑子有 canShare ↑且 [native code]
```

### 三、这一轮抓到的真 bug：品牌校验**不能跨 realm**

第一版守卫写的是 `this instanceof G.Navigator` —— 对**子 frame 的 navigator 是 false**，
因为子 realm 有自己的构造函数。于是重放到子窗口的访问器**在子窗口自己身上抛出** `Illegal invocation`。

改成正则无关的判据：

```js
let tag; try { tag = Object.prototype.toString.call(this); } catch (e) { tag = ''; }
if (tag !== '[object Navigator]') throw new TypeError('Illegal invocation');
```

`{}` 仍然答 `[object Object]` → 抛；任何 realm 的 navigator 都答 `[object Navigator]` → 通过。

### 四、这一轮的一句话

> 我写了一个「只接受自己人」的守卫，结果它把另一个房间里的自己人也挡在门外。
>
> **身份判据如果绑在某个具体对象上，它就不是身份判据，是地址判据。**
'''

if "## 同源 iframe 有自己的构造函数" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("journal documented")
else:
    print("already present")
