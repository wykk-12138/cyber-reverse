# 11 · 本地跑 Nike payload 的实测结构（Jint 侧）

> 这份记的是**我们自己跑 nike-p.js 时量出来的东西**，不是原版二进制里的证据。
> 用途：复刻本地路时不必从零试错。每条都标了是 [实测] 还是 [未解]。
>
> 配套：`KasadaPayloadBootstrapTests`（钉住 §3 的三个数字）、`WebApiShims.cs`（§6 的 52 个全局）、
> `ScriptRuntime.DecodedStrings`（§4 的解码表）。

---

## 1. payload 的分行结构 [实测]

`fixtures/nike-p.js` 共 6 行，长度 `[150921, 0, 161, 6299, 177, 0]`：

| 行 | 长度 | 是什么 |
|---|---|---|
| 0 | 150,921 | 主 IIFE：解码器 `A`、常量表 `U`、指令分发 `D`、帧构造 `h`、以及占位 |
| 1 | 0 | 空 |
| 2 | 161 | 一行 Babel 版权注释（`regenerator-runtime`） |
| 3 | 6,299 | **Babel `regenerator-runtime`** —— 与 Kasada 无关，但**必须能跑**，否则后面全废 |
| 4 | 177 | VM 主循环 `m(e)` + 启动 `m(I)` |
| 5 | 0 | 空 |

**第 3 行是个独立的 IIFE**，`u` 在其中是 `function u(t,r,e)`（`defineProperty` 包装），**不泄漏到外层**。

## 2. 字符串被编码存储 [实测]

**直接 grep 原文件，`webdriver` / `userAgent` / `plugins` / `platform` / `WebGL` 全部 0 命中。**
字面量编码在数据段里，运行时用

```js
w += String.fromCharCode(x & 4294967232 | x * 41 & 63)
```

拼回来。所以「搜不到」不等于「没有」，任何基于 grep 的结论在这份 payload 上都无效。

hook `String.fromCharCode` 可以把重建过程录下来（`ScriptRuntime.DecodedStrings`）。
跑到失败点为止录到 **6,309 字符**，其中可读的包括：

```
valueOf  x-kpsdk-h  abrupt  ntoLowerCase  finalize already called  endsWith  action
configuration  parentNode  kpsdk-ready  border  vfp  charCodeAt  finish  parse  navigator
DELETE  verbose  __proto__  reinterrogationTimeoutDuration  Failed to send frontend error,
fetch returned a  <64-hex>  Set  marker  ArrayBuffer  clientTime  Function  StartBuffer
Truncated  readystatechange  SDK error  Date  Invalid  Done  Payload  Uint8Array  PATCH
bubbles messages by sendBeacon  remote-configs  sha256  default  includes  Math
```

**注意**：这套名字里**没有** `webdriver` / `plugins` / `WebGL` / `canvas`。
**nike-p.js 主要做协议与哈希，不是重度浏览器指纹。** 这一点和"Kasada 靠指纹"的直觉不符，是实测修正。

## 3. 解码器 `A` 与那次 `splice` [实测，已被 `KasadaPayloadBootstrapTests` 钉住]

```js
var O = "length";
var t = A(F, "3RM19lar~F2OkHzTGVj8eNicLxDI^4UsYypC<JSXo7Kmv6PQWbfw=AE+ZB$tudq|gnh0>5", 39);
var c = t[O];                       // c = t.length
var L = "";
var H = c + (L + true)[O];          // H = c + 4   （常数 4 藏在 "true".length 里）
var y = t[c + L.indexOf(".")] ^ H;  // L 是 28 个随机小写字母 ⇒ indexOf(".") 恒为 -1
                                    // 所以 y = t[c-1] ^ (c+4)，纯算术
t.splice(y, t[y + I.m[0]] + 2);     // I.m[0] 初始为 1
```

`A(r, u, a)` 是 **LZ 解码器**：`u` 是 60 字符的字典，`a = 39` 是有效前缀长度，
`C = new Map()` 建字符→位置索引，`C.get(r[N++]) || 0` 查表（查不到当 0 —— 这一步会**静默**吞掉坏字符）。

**实测三个数字**：

```
start = 13772   count = 6283   len = 75771
```

⇒ `t` 原本 75,771 项；`[13772, 20055)` 是字符串池，切走后 `t` 变成 69,488 项；
`[0, 13771]` 是字节码。

**字节码头**：

```
[59, 62, 3, 62, 5, 62, 7, 62, 9, 62, 11, 62, 13, 62, 15, 62, 17, 62, 19, 62, 21, 62, 23, 62]
```

PC 从 **1** 开始（帧里 `m:[0]`，但入口 `e.m[0] = 1`），所以 `t[1] = 62` 是第一条 opcode，
后面跟着 **3, 5, 7, 9, …** 递增的参数。

**这三个数与 `H`/`y` 一样，一个宿主值都不读** —— 所以它们稳定，不是"环境不同导致错位"。

## 4. VM 的栈结构 [实测]

```js
function h() { var e = [1, {D:s, $:null, g:[], m:[0], B:void 0}, void 0]; return {m:e, T:void 0} }
```

`e.m` 这一个数组**同时是三种东西**：

| 下标 | 含义 |
|---|---|
| `m[0]` | **程序计数器** |
| `m[1]` | **帧对象** `{D, $, g, m, B}` |
| `m[2..]` | **局部变量槽**（初始 `void 0`，由 `B` 写入） |

取值/存值**完全对称**：

```js
function p(e){ return t[e.m[0]++] >> 5 }     // 消耗 PC，返回槽位号
function B(e,n){ e.m[p(e)] = n }             // 写槽位
function X(e){ return U(t, e.m, g, P) }      // 读槽位（经常量解码器）
```

**常量编码表 `g = [4, 24, 22, 8, 14, 42]`**，`U` 的判定顺序：

| 条件 | 结果 |
|---|---|
| `f & 1` | 内联小整数 `f >> 1` |
| `f === 8` | `true` |
| `f === 22` | 字符串（`P.O` 切片，或内联 `charCode` 解码） |
| `f === 14` | `null` |
| `f === 24` | `false` |
| `f === 42` | （另一条分支） |
| 其它 | **`u[f >> 5]` ← 从栈槽位取** |

## 5. 当前卡点 [实测 + 已定位到 opcode]

失败签名（三轮不变）：

```
executed=False   offset=144669
error = Cannot read properties of undefined (reading '<28 个随机小写字母>')
stack: at i (payload:1:146667) → at m (payload:5:116) → payload:5:15
```

### 5.1 指令表 `u` 是个 Proxy（86 条指令）

上一轮我搜不到 `u` 的定义，是因为它写成 `}}u=new Proxy([…], handler)`，前面的 `}}` 不在我的正则里。

```js
u = new Proxy([ …86 个 handler… ], (function () {
    var e = Array.from({length: 86}, function (n, r) { return r });   // [0..85]
    return {
        get: function (n, r) {
            var T = Number(r);
            if (Number.isNaN(T) && r !== v) return function () {};     // 非数字键 → 空函数
            if (!Number.isFinite(T)) return e;                        // → 索引数组（假 length）
            return n[e[T]];                                           // 正常取
        }
    };
})());
```

其中 `v = typeof O[M]`，`O = "length"`、`M = window.Promise` —— `"length".Promise` 是 undefined，
所以 **`v === "undefined"`**。于是：

| 访问 | 得到 |
|---|---|
| `u[62]` | 真正的第 63 个 handler ✓ |
| `u.length` | **`[0,1,…,85]`**（不是 86 —— 反分析手法） |
| `u.anything` | 空函数 |

**数组长度 86，`t[1] = 62` 在范围内 ✓**

### 5.2 第一条指令是 opcode 62 —— `g[i] = void 0`

```js
// u[62]，50 字符
function(n, e, a, v){ var i = e(n), o = v(n); o.g[i] = void 0 }
```

`v` 就是 `f = e => e.m[1]`（取帧对象），`o.g` 是帧里的 `g: []`。所以这条指令是**清空一个捕获变量槽**。

字节码头 `[59, 62, 3, 62, 5, 62, 7, …]` 配合 `PC` 从 1 开始、参数走 `f & 1 → f >> 1` 的内联整数解码，
读出来就是**连续清 `g[1]`、`g[2]`、`g[3]` …** —— 正常的"作用域初始化"。

### 5.3 崩的是 opcode 12 —— call / apply

`146667` 落在这个 handler 的区间 `[146607, 146900)`：

```js
// u[12]
function(n, e, a, v, i, o){
    var r = e(n), l = e(n), u = e(n), _ = o[4];
    if (l[_] && l[_].w === l) {                       // regenerator 的 generator 对象
        var h;
        n.m = [l[_].X, {D:r, $:l, m:n.m, g:[], B:l[_].B,
                        E:(h = n.Q) === null || h === void 0 ? void 0 : h.get(l[_].E)},
               void 0,
               function(){ return arguments }.apply(void 0, u)];
        for (var t = 0; t < u.length; t++) n.m.push(u[t]);
    } else {
        n.m[2] = l.apply(r, u);                       // 普通调用：结果写进槽位 2
    }
}
```

三个 `e(n)` 依次弹出 **被调 this、被调函数、参数数组**。崩在 `l[_]`，即**第二个弹出的值是 undefined**。

**⇒ 字节码执行到"调用"时，栈上没有可调用的东西。**

注意 else 分支 `n.m[2] = l.apply(r, u)` —— **`m[2]` 就是上一条指令的返回值槽**。
所以 `m[2]` 未初始化与"调用栈空"是同一件事的两面。

### 5.4 已排除与未解

**已排除**：

| 假设 | 怎么排掉的 |
|---|---|
| 缺 Web 全局（52 个） | 全补后错误从 `reading 'bind'` 变成 `reading '<随机名>'`，前进了一步 |
| Promise 微任务没 drain | 实测 `Promise.resolve(7).then(v=>d=v)` 在 `Execute` 返回时 `d` 已是 7 |
| 字节码被 `splice` 错位 | `H`/`y` 是纯算术，三个数字稳定且已被测试钉住 |
| `crypto.subtle` 缺失 | 补了真 SHA/HMAC，offset 未变 —— 崩在这之前没走到加密 |
| `u` 未定义 | 它是 `new Proxy([…86…])`，能正常取到 `u[62]` |

**未解**：栈在 opcode 12 之前就已经不平衡 —— 即**某条 push 指令没执行，或执行了但没写槽**。
下一步要逐 opcode 追这段前缀的栈深度，而不是继续补宿主对象。

### 5.5 86 条 handler 的静态栈效应 [实测]

handler 的签名固定是 `(n, e, a, v, i, o)`：

| 形参 | 实参 | 作用 |
|---|---|---|
| `n` | 帧/状态 | 读写 `n.m`（栈+PC）、`n.T` |
| `e` | `X` | **pop 一个值**（经常量解码器 `U`） |
| `a` | `B` | **push 一个值**（写 `n.m[槽位]`） |
| `v` | `f` | 取帧对象 `n.m[1]` |
| `i` | `n` 数组 | `[window, [Promise, W], t, u]` |
| `o` | `r` 数组 | `[j, D, h, m, L, G]` |

按 `e(n)` / `a(n, …)` 计数，**29 条指令净 pop**：

```
-1: 0 4 14 20 26 32 33 38 39 41 42(→-2) 46 51 52 56 60 62 63 67 69 79
-2: 3 18 42 48
-3: 7 11 12 47 61
```

**净 pop 是栈机的常态**（两个操作数 → 一个结果），不是缺陷。但其中一条特别值得注意：

```js
// opcode 12 —— pop 3 个，却一次 a(n,…) 都不调
else { n.m[2] = l.apply(r, u); }
```

**它的结果不 push，而是写进固定槽 `m[2]`。**

这一条改变了整个栈平衡的读法：`m[2]` 是"上一次调用的返回值"专用槽，
而 `U` 的槽位分支 `u[f>>5]` 在 `f>>5 === 2` 时读的正是它。

**⇒ 崩点 = 字节码在第一次"调用"之前就去读了 `m[2]`。**

两种情况都会这样：

1. 字节码本应在调用**之后**读 `m[2]`，但 PC 提前跳到了那里；
2. 或者那次调用本该发生却没发生（`m[2]` 仍是 `void 0`）。

**要区分这两者，需要实际执行的 opcode 序列** —— 下一步给出。**

### 5.6 拿执行序列的办法（下一轮做）

payload 的指令表 `u` 是 `new Proxy(...)`，而 `Proxy` 在它自己的 IIFE 里是**全局构造器**。
所以在 shim 里包一层 `window.Proxy`，就能把每次 `u[index]` 的读取记下来，得到 opcode 序列，
再与静态栈效应表对照，就能定位第一次出现不平衡的位置。

```js
var OrigProxy = this.Proxy;
this.Proxy = function (target, handler) {
    if (handler && typeof handler.get === "function") {
        var wrapped = {}; for (var k in handler) wrapped[k] = handler[k];
        wrapped.get = function (t, prop, recv) { __dshOpcodes.push(String(prop)); return handler.get(t, prop, recv); };
        return new OrigProxy(target, wrapped);
    }
    return new OrigProxy(target, handler);
};
```

**代价**：这是诊断代码，会记录上万条 opcode，不该长期留在产品路径里。

### 5.7 执行序列与崩溃点 [实测]

包了 `window.Proxy` 之后拿到完整 dispatch 序列（共 **9,285** 次），开头结构非常规整：

```
62 × 27                       ← 清 g[1..27]（作用域初始化）
[ 3, 48, 63 ] × 27            ← 建闭包 → 写入捕获变量 → 跳回
3, 63                         ← 最后一组（无 48）
80                            ← push 一个空数组
12                            ← 第 111 次 dispatch，崩在这里
```

三条关键指令的源码：

```js
// 62：清一个捕获变量槽
function(n,e,a,v){ var i = e(n), o = v(n); o.g[i] = void 0 }

// 3：建闭包，把它 push 出去
function(n,e,a,v,i,o){
    var r, l=e(n), u=e(n), _=e(n), h=v(n), t=o[2], b=o[3], d=o[4];
    var p = function(){ … return f.m[2] };
    try { Object.defineProperty(p,"length",{value:_}); Object.defineProperty(p,"name",{value:u}) } catch(w){}
    p[d] = { X:l, B:h, w:p, E:… };     // d = o[4] = 那个 28 字符随机名
    a(n, p);                            // ← push 闭包
}

// 80：push 空数组（调用指令的参数列表）
function(n,e,a){ a(n, []) }

// 48：沿作用域链写一个捕获变量
function(n,e,a,v){ for(var i=e(n), o=e(n), r=v(n); r; r=r.B) if(i in r.g){ r.g[i]=o; return } throw 'ball' }
```

**崩时的字节码**（`t[320..344]`）：

```
[160,7,128,22,4,6071,160,15,128,192,63,745,19,128,40,3,224,7,128,22,4,6071,224,64,59]
```

**这里有个容易搞错的地方**：`X(e)` 读的是**字节码指定的槽位**，不是栈顶 ——
`a(n,x)` 是 `n.m[p(e)] = x`，`p(e)` 从字节码取**目标槽位号**。所以这不是 LIFO 栈机，
是**槽位机**：`m[2]` 是"上次调用返回值"的固定槽，`m[3..]` 是字节码分配的局部槽。

**⇒ 所以"栈不平衡"这个说法本身要改成"某个槽位在被读之前没有被写"。**

### 5.8 下一步：精确解字节码

静态推算参数个数会出错，因为**字符串常量占两个值**：

```js
if (f === 22) {                       // 22 = 字符串标记
    if (v && v.y) return v.y(r[u[0]++], r[u[0]++]);   // ← 消耗两个：偏移 + 长度
    …
}
```

所以要把 `t` 从 `[0]` 开始完整模拟一遍解码（`U` 的规则：奇数→内联整数、`4/8/14/22/24/42` 是标记、
字符串吃两个、其余 `f>>5` 是槽位），把 opcode 与参数一一对出来，
才能知道 `12` 读的是哪三个槽位、以及写 `m[7]` 的那条指令到底有没有执行。

### 5.9 字节码解码完成：崩溃指令的三个操作数 [实测]

补全 `U` 之后（完整源码在 payload `144778` 起）有一条**关键发现**：

```js
var U = function(r, u, a, v){
    var f = r[u[0]++];
    if (f & 1) return f >> 1;                       // 奇数 → 内联整数
    if (f === a[0]) { … double，吃两个字 … }         // a[0] = 4
    if (f === a[3]) return !0;                       // 8  → true
    if (f !== a[5]) {                                // !== 42
        if (f === a[2]) { … 字符串，吃两个字 … }      // 22
        return f === a[4] ? null                     // 14
             : f === a[1] ? !1                       // 24
             : u[f >> 5];                            // 槽位
    }
    // f === 42：函数到此结束，隐式返回 undefined
};
```

**`42` 没有 return 分支 —— 它是 payload 的 `undefined` 字面量。** 这不是 bug，是编码设计。

**解码器（`U` 规则 + 跳转感知）**：`63` 是 `n.m[0] = e(n)` 的无条件跳转，所以线性扫不行，要跟着跳。
按这个规则解出来的前 **110 条指令，与实际记录的 dispatch 序列逐条完全一致**（零 mismatch），
说明解码规则是对的。

**崩点前后的完整指令流**（`69448..69487` 是 splice 之后的尾部）：

```
108  op=3   pop=3 push=1   args=[int 5014, str, int 0, slot 5]     ← 建闭包，写进 m[5]
109  op=63  pop=1          args=[int 69477]                          ← 跳到 69477
110  op=80  pop=0 push=1   args=[slot 7]                            ← m[7] = []
111  op=12  pop=3          args=[undefined, slot 5, slot 7]          ← 调 m[5](undefined, m[7]) → 崩
```

**⇒ opcode 12 的三个操作数是 `undefined`（this）、`m[5]`（要调的闭包）、`m[7]`（刚 push 的 `[]`）。**

**`m[7]` 由 110 号指令写入，没问题。`m[5]` 由 108 号写入 —— 按解码结果它应该是一个闭包。**

### 5.10 当前唯一的矛盾

**`108` 写了 `m[5]`，`111` 读的也是 `m[5]`，两次算出来的槽位号一致（都是 `f >> 5 === 5`），
但 `111` 读到的却是 `undefined`。**

三种可能，下一轮用一次实验就能分开：

1. **`3`（opcode 3）在 `a(n, p)` 之前抛了异常** —— 它的 `Object.defineProperty` 包在 try 里，
   `p[d] = {…}` 不在 try 里，`a(n, p)` 也不在。若 `p[d]` 那行抛（比如 `d` 是 undefined 时对冻结对象赋值），
   `a(n, p)` 就不会执行。
2. **两次 `f >> 5` 指向的不是同一个数组** —— `12` 的 else 分支会 `n.m[2] = …`，而 if 分支整块换 `n.m`；
   若前面某条指令换过 `n.m`，`m[5]` 就是新帧里的空槽。
3. **我的 `pop/push` 计数在 `3` 上多算或少算了一个**，导致槽位号错位一格。

**验证办法**：在 shim 里包 `Object.defineProperty`，记录 `3` 是否走到 `a(n,p)` 那一步；
或者直接记录 `n.m` 数组的引用变化次数。

## 6. 已经补齐的宿主面 [实测]
`WebApiShims.cs`：52 个 Web/宿主全局（`TextEncoder` / `URL` / `Blob` / `Worker` / `AudioContext` /
`RTCPeerConnection` / `fetch` / `WebAssembly` / observer 族 …），每个都标了是 **shape** 还是 **behaviour**。

`crypto.subtle`：`digest` / `importKey` / `sign` 走宿主真实现（SHA-1/256/384/512 + HMAC），
其余明确 reject。**不用假哈希** —— 假值会让 payload 把错值塞进 token，比当场失败更坏。

`navigator` 原本就很完整（`userAgent` / `platform` / `vendor` / `languages` / `webdriver` /
`plugins` / `mimeTypes` / `hardwareConcurrency` / `deviceMemory` / `maxTouchPoints` / `sendBeacon`）。

## 7. 复算

```powershell
# 侧装 SDK（机器的 C:\Program Files\dotnet 只有 runtime）
$env:DOTNET_ROOT='D:\tools\dotnet8'
D:\tools\dotnet8\dotnet.exe test tests\Cybersole.Tests --filter "FullyQualifiedName~Kasada" -m:1
```

`KasadaPayloadBootstrapTests` 会打印（断言失败时）或钉住：`start/count/len` 三个数与字节码头四个值。
