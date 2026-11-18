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

### 5.11 三个实验排掉了两个，第三个需要 Jint 的 debugger

**实验一：原始字节码。** `words[5005..5013]` 读出来是

```
5005 : 3           ← opcode 3（建闭包）
5006 : 10029       → 10029>>1 = 5014        参数 l（用哪个槽做上下文）
5007 : 22          → 字符串标记
5008 : 0  \  偏移/长度 → P.O.slice(0, 2751)  参数 u（名字）
5009 : 2751 /
5010 : 1           → 0                       参数 _（length）
5011 : 160         → 160>>5 = 5              push 目标 = m[5]
5012 : 63          ← opcode 63（无条件跳转）
5013 : 138955      → 138955>>1 = 69477       跳到 80 号指令
```

**解码与实测 dispatch 一致，`push` 目标确实是 `m[5]`。** 所以既不是解码错位，也不是槽位号算错。

**实验二：`Object.defineProperty` 被调了 500+ 次**（记录上限 500），其中 `length:function` / `name:function`
成对出现 —— **opcode 3 确实走进了它的 `try { Object.defineProperty(p,"length",…) }` 那一块**。

**实验三：`Map` 只被构造 2 次**（payload 自己的两个字典型解码用），
而 opcode 3 的 `p[d] = { … E: h.E !== void 0 ? new Map(Array.from(n.Q…)).get(…) : void 0 }`
只有 `h.E` 有值时才走 `new Map(...)` 分支。

**⇒ `h.E` 全程是 `undefined` ⇒ 那一步走的是 `: void 0` 分支 ⇒ `p[d] = {…}` 不该抛。**

**三个实验合起来：字节码对、装饰执行了、`p[d]` 不抛 —— 但 `m[5]` 仍然是 `undefined`。**

### 5.13 打桩后的真相：崩在第 9285 步，不是第 111 步 [实测]

前面所有关于「第一个调用指令就崩」的叙述都是错的 —— 那是把 Jint 报的**最终逃逸异常**的位置
当成了**第一次失败**的位置。

在 payload 副本里插一行探针（原 fixture 不动，另存 `nike-p-traced.js`），记录每次 dispatch 的帧状态后：

```
总 dispatch            9285
其中 opcode 12（调用）  148 次
m[5] 为 undefined 的     6 次
最后一次                pc=69469, flen=13, m[5]=undef, m[7]=arr1
```

**六处读 `m[5]` 拿到 `undefined`：**

```
[ 3622, 15, 'undef', 'fn'  ]
[14725, 11, 'undef', 'obj' ]
[ 3622, 15, 'undef', 'fn'  ]
[33325, 11, 'undef', 'arr1']
[66951, 11, 'undef', 'obj' ]
[69469, 13, 'undef', 'arr1']   ← 这一次逃逸到了顶层
```

**前五次没崩，因为 payload 自己的 try/catch 兜住了；第六次所在的位置没有 handler，
异常一路走到 `D(e,n)` 的 `throw n`，被 Jint 接住并报成 `at i (payload:1:146667)`。**

`146667` 只是 opcode 12 的 handler 在源码里的位置 —— **148 次调用都落在这里**，
所以它从来不指认是哪一次崩的。这个误导持续了四轮。

### 5.14 根因方向：某个全局变量读不到

`m[5]` 本该由 opcode 81 填充：

```js
// u[81]
function(n, e, a, v, i) { a(n, i[0][e(n)]) }
```

`i[0]` 就是 `n` 数组的第 0 项 = `s` = **`window`**。所以这条指令的语义是
**「按名字从全局作用域取一个值，存进槽位」**：

- 名字存在 → `m[5]` = 那个值
- **名字不存在 → `m[5]` = `undefined`**，随后调用指令 `l[_]` 就炸

**而 `m[7]`（参数数组）在六处里都有值（`fn` / `obj` / `arr1`）—— 只有被调的那个函数是空的。**

⇒ **payload 要调 6 个宿主全局，其中至少一个名字在我给的 shim 里不存在或不是函数。**

这比「栈错位」实用得多：**下一步是把 opcode 81 读的那个字符串打出来**，
它会直接是一个 API 名字（`TextEncoder` / `Blob` / `URL` / … 中的某一个）。

### 5.15 下一步的做法

在插桩副本里，把探针改成在 `12` 之前的 `81` 上记录**它取到的名字**：

```js
if (t[e.m[0]] === 81) window.__dshGlobals.push(String(e.m[/* 名字槽 */]));
```

或者更省事：**给 `window` 挂一个 Proxy 的替代物** —— 但 `window` 是 `this`，换不了；
所以走插桩那条路，读 `81` 的参数槽。

拿到名字之后，回到 `WebApiShims.cs` 里补齐它，重跑，看这 6 处是否降到 0。

### 5.16 槽位的生命周期：`3` 写 → `12` 清 → `3` 重建 [实测]

记录 `m[5] / m[6] / m[7]` 的每次**变化**（不是每次 dispatch）之后，机制就很直白了：

```
pc      op   m5|m6|m7
     1  62  undef|undef|undef      ← 帧刚建
    62  48  fn|undef|undef         ← 之前 pc=55 的 opcode 3 写入了闭包
  4791  48  fn|fn|undef
 69479  12  fn|fn|arr0             ← 调用成功（generator 分支），m[7] 是刚 push 的 []
  5014  62  undef|undef|undef      ← 换栈了：12 的 generator 分支整块替换 n.m
  8903  48  fn|undef|undef         ← 恢复点重新执行 opcode 3，m[5] 又有了
```

**所以 `m[5]` 的生命周期是：**

1. **opcode 3 写入闭包**（`a(n, p)` → `B` → `m[槽位] = 闭包`）
2. **opcode 12 的 generator 分支整块替换 `n.m`** —— 新数组只有 `[X, 帧对象, void 0, arguments]`，
   **`m[5]` 从此不存在**
3. **恢复点（`l[_].X` 指向的地址）重新执行 opcode 3**，`m[5]` 又有了

**这是一个「调用即重建作用域」的设计：每次进 generator，旧帧被丢弃，靠恢复点重新建闭包。**

**六处 `undef` 就是六次「重建没有发生」** —— 恢复点跑完却没有执行到那一条 opcode 3。

### 5.17 于是问题变成：那 6 次为什么没重建

trace 里能看到重建成功的例子（`pc=8903 → m[5]=fn`），所以机制本身是通的。
失败的那 6 处（`pc = 3622, 14725, 33325, 66951, 69469`）的共同点是：
**进入这段恢复代码后，执行流没有走到那条建闭包的 opcode 3。**

两种可能，都指向同一个方向：

1. **恢复点之前的某条分支条件算错**（`47` / `11` 这类条件跳转），跳过了建闭包那一段；
2. **某条指令抛了异常**，`D(e,o)` 把执行流带到 catch 块，绕过了建闭包。

**而触发 (2) 的最可能原因仍然是宿主面** —— 某条指令读了一个不存在的全局，抛在 try 里被吞，
流程就歪了。

> §5.21–§5.22 是找到这个结论之前的调查过程（序列对比与全局名清单），按时间顺序读起来更顺，
> 但结论在 §5.18。保留它们是因为里面的「payload 会读哪几个全局名」仍然有用。

### 5.18 修好了：缺的是 `document.dispatchEvent` [实测]

把字形表偏移修对之后（`P.O = DecodedStrings[28:]`，前 28 字符是那个随机串 `L`），
整条失败路径的指令流就全解开了：

```
69442  op=81   str:window                 -> m7      m7 = window
69447  op=51   m7, str:document, -> m6               m6 = window.document
69453  op=51   m6, str:dispatchEvent, -> m5          m5 = document.dispatchEvent   ← 这里是 undefined
69459  op=49   new Array(...)                        （还没执行到）
69469  op=12   m6, m5, m7                            m5.apply(m6, m7)  → l[_] 崩
```

**`document.dispatchEvent` 在我的 shim 里不存在** —— `document` 有 `addEventListener` /
`removeEventListener`，唯独漏了 `dispatchEvent`。payload 按名字取到 `undefined`，
两条指令之后当成函数调用，于是报 `Cannot read properties of undefined (reading '<随机属性名>')`。

**这个属性名是随机的，所以四轮里我一直以为它是「某个内建对象缺了」** —— 其实它只是
`opcode 12` 在检查 `l[_]`，而 `l` 是 undefined。名字本身没有信息量。

**修法**（`BrowserShim.cs`）：`document` 与 `window` 都装上真的事件机制 ——
`addEventListener` 记录、`dispatchEvent` 回调、`removeEventListener` 移除。
必须是真的，因为 payload 的 `kpsdk-ready` 之后的工作全在那个监听器里。

**结果**：

```
修之前： executed=False  error=Cannot read properties of undefined (reading '<随机名>')
修之后： executed=True   error=no kasada client token exposed by the script
```

**payload 现在能跑完了。** 剩下的不是崩溃，而是「跑完了但没在 `KPSDK.ct()` 之类的入口暴露 token」。

### 5.19 一个曾经的误判，值得记下来

上一轮我统计「6 处 `m[5]` 是 undefined」，据此断定「六次 generator 恢复没重建作用域」。
**那个结论是错的**：`opcode 12` 读哪三个槽位由它自己的字节码操作数决定，
不是固定读 `m[5]`。改成按操作数取槽位之后，148 次调用里**只有 1 次**任一操作数为空
（`pc=69469`，被调槽位空），其余全部正常。

**教训**：VM 的槽位号必须从操作数解出来，不能假定某个固定槽位。

### 5.20 剩下的：token 提取

`executed=True` 但 `Ct` 为空，说明脚本完整跑完、没有在 `KPSDK.ct()` / `KPSDK.sb()` 等
入口留下值。两种可能：

1. **token 本来就来自 `/tl` 往返**（见 `08-cd.md` §9.1：`rec[11] = v5[16]`，ct 是服务端回填的）
   —— 那本地脚本只负责产出 `cd`，`ct` 要 POST `/tl` 才有；
2. **本地确实暴露了，但入口名不是我们试的那七个**（`CtEntryPoints` 是猜的，见 `KasadaSolver.cs`）。

**下一步**：脚本跑完后 dump `window.KPSDK` 的形状（有哪些属性、哪些是函数、调一次返回什么），
用事实替换那七个猜测的入口名。

### 5.23 做完了：`KPSDK` 的真实表面只有两个函数 [实测]

`KasadaSolver.CtEntryPoints` 里那七个表达式（`KPSDK.ct()` / `clientToken()` / `token()` …）
**全是猜的，一个都不存在**。实测：

```
window.KPSDK = { configure: function, isReady: function }
```

只有这两个键。没有任何 `ct` / `cd` / `sb` / `token` 之类的取值入口。

配套观察：

```
document 上注册的监听器 : visibilitychange, pagehide
实际派发过的事件        : kpsdk-load
window.__dshCaptured    : {}
document.cookie         : 空
pending timers          : 0
KPSDK.isReady(cb)       : 回调没有触发
```

`KPSDK.configure(...)` 传任何东西（`undefined` / `{}` / `{siteId:'nike'}` / `{clientId:'nike'}`）
都不抛异常、也不改变键集合 —— 它是个静默接受的入口。

**关键判断：`isReady` 的回调没触发 ⇒ 传感器从没进入 ready 状态 ⇒ 自然不会产出 token。**
`kpsdk-load` 派发了，`kpsdk-ready`（这个字符串确实在它的字面量表里）**没有派发**。

### 5.24 顺带修好的：定时器现在是真的排队

原来 shim 里 `setTimeout` 是**同步立即调用**：

```js
this.setTimeout = function (fn) { if (typeof fn === "function") { try { fn(); } catch (e) {} } return 0; };
```

这会让 payload 的延后步骤在它自己的初始化过程中就执行 —— 顺序全错。
浏览器是「当前任务结束后再跑」，所以改成**入队**，并由宿主在脚本结束后统一排空：

```js
this.setTimeout = function (fn, ms) { … __dshTimers.push({id, fn, ms, seq, repeat:false}); return id; }
this.__dshRunTimers = function (maxRuns) { … 逐个执行，interval 最多重复 3 次 … }
```

`ScriptRuntime.TryExecute` 在 `Evaluate` 之后调用 `RunPendingTimers()`（上限 2000 次，
因为未 clear 的 interval 否则永不结束）。

**这一步没有让 `isReady` 触发**，但它是正确语义 —— 之前那种同步执行是错的。

### 5.25 下一个卡点：网络

把上面四条合起来看，`kpsdk-load` 之后没有 `kpsdk-ready`，而字面量表里有 `remote-configs`、
一个 64 位十六进制串、以及 `Failed to send frontend error, fetch returned a`。
payload 大概率在等一次远程配置拉取，而 shim 的 `fetch` 是**直接 reject** 的：

```js
this.fetch = function () { return Promise.reject(new TypeError("fetch is not available in this sandbox")); };
```

**这和我逆向侧的结论对得上**（`08-cd.md` §9.1：`rec[11] = v5[16]`，ct 由 `/tl` 响应回填）：
**本地不需要真浏览器，但需要真网络。** 传感器要 POST `/tl`、拉 remote-config，才可能拿到 ct。

**所以本地路的完整形状是：Jint 跑脚本（已通）→ 脚本内的请求走我们自己的 HTTP 客户端
（不是浏览器）→ 从响应头拿 `ct` / `dt` / `im`。** 下一步就是把 `fetch`/XHR 接到 `NetClient` 上，
而不是让它 reject。

### 5.26 `fetch` 不 reject 之后：payload 一个请求都不发 [实测]

把 `fetch` 改成「记录 + 返回空 200」、XHR 改成「记录 + 触发 onload」之后跑一遍：

```
executed = True
network requests = []        ← 一个都没有
pending timers   = 0
isReady(cb)      = 未触发
```

**它不是缺网络，是压根没走到发请求那一步。**

### 5.27 字面量表就是它的完整词汇表 [实测]

把 `DecodedStrings`（6308 字符）整张打出来，几乎每一行都在描述它期望的运行环境。关键的几组：

**（1）它有一个状态机**

```
Configured  InterrogationStarting  InterrogationComplete  InterrogationFailedToStart
InterrogationTimedOut  InterrogationSkipped  InterrogationRetrying
InvalidStateTransition  start  finalize  done  end
```

**（2）它用 iframe 拿配置，而且是主要路径**

```
Appended iframe didn't respond with configuration within 20 seconds.
iframe  contentWindow  postMessage  message  Appended
```

**（3）`configure` 的入参形状（错误信息把 schema 全写出来了）**

```
Configuration endpoints are not an array
endpoints must be an array
Endpoint definition is not valid
: definition is not a valid object
: domain must be a non-empty string
: domain must not include a protocol
: domain must not contain wildcards unless it is exactly *
: path must be a string
: path must start with /
: path must contain at most 3 wildcard characters
: path must not contain query parameters
: method must be a valid HTTP method or *
: if provided, caseSensitiveMatch must be a boolean
: if provided, method must be a string
KPSDK has already been configured
```

**（4）版本号与端点**

```
j-1.2.988 - encodedClientToken          ← 传感器版本
InterrogationRetrying/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-…  ← 带两个 UUID 的路径模板
_/mfc   /mfc   mfc response was missing one or more headers   KP_IC   KP_RC
remote-configs   dynamicConfig   featureFlags   endpoints   resourceAddress
```

**（5）其余有用的事实**

```
Original fetch not found / NoOriginalFetchError    ← 它包装 window.fetch，且要求拿到原始引用
kpsdk-load  kpsdk-ready  kpsdk-pending  kpsdkCt     ← 生命周期事件与 cookie 名
x-kpsdk-c  x-kpsdk-cd  x-kpsdk-ct  x-kpsdk-fc  x-kpsdk-r
workTime  serverTime  clientTime  seqNum  timestamp  validUntil  duration
```

### 5.28 结论：`p.js` 只是传感器，配置不在它里面

**四条证据串起来：**

1. `configure` 静默接受任何参数、且第二次调用会报 `KPSDK has already been configured`
   → 它**设计上**只接受一次真正的配置
2. 错误信息把 `endpoints` 的 schema 完整列了出来 → 配置必须是 `{ endpoints: [{domain, path, method, …}] }` 这种形状
3. 字面量里有 `Appended iframe didn't respond with configuration within 20 seconds`
   → **没有 endpoints 时，它去页面里挂 iframe 等宿主回配置**
4. 实测一个请求都没发、也没有待执行定时器 → 它卡在「等配置」这一步

**⇒ `p.js` 不自带配置。** 真页面上是**页面自己的脚本**调 `KPSDK.configure({endpoints: …})`，
或者由 iframe 里的父页面 postMessage 递过去。**我们单独跑传感器，永远等不到。**

**这也解释了 Cybersole 的本地路为什么能成**：它必然先拿到了那份配置（从页面里取），
再喂给传感器，才有后面的 interrogation 与 `ct`。

### 5.29 下一步：从 Nike 页面里把配置取出来

`NikeFlow` 本来就会 GET 首页并解析 HTML（`KasadaSolver.FindScriptUrl(res.Body, …)` 就在做这件事）。
同一份 HTML 里通常就有配置脚本，形如

```html
<script>
  window.KPSDK = window.KPSDK || {};
  KPSDK.configure({ endpoints: [ … ], … });
</script>
```

**要做的**：
1. 在页面 HTML 里找 `KPSDK.configure(` / `kpsdk-config` 之类的配置块
2. 把它作为入参喂给 `KasadaSolver`，在跑传感器**之前**执行
3. 再看 `isReady` 是否触发、`ct` 是否出现

**顺带注意定时器的语义**：我们把定时器在脚本结束后一次性排空，
所以那条「20 秒等 iframe」的超时会**立刻**触发而不是等 20 秒。诊断时不要把它当成真实现象。

### 5.30 一个把自己坑了三次的坑：PowerShell 会吃掉双引号

把配置当命令行参数传给探针时，PowerShell 对原生 exe **会剥掉双引号**：

```
传 {"endpoints":[{"domain":"www.nike.com","path":"/tl","method":"POST"}]}
到 →  {endpoints:[{domain:www.nike.com,path:/tl,method:POST}]}
```

于是 `path:/tl` 里的 `/tl` 被当成**正则表达式开头**，Jint 报
`Invalid regular expression: missing / (payload:1:62)`。

**在这个坑里浪费了三次试验**：早先看到「`configure({})` 返回 ok、`{endpoints:[…]}` 无声失败」，
其实**全都是被剥引号之后的假象**。现在改成 base64 传参：

```powershell
$b64 = "b64:" + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($json))
dotnet exec bin\Debug\net8.0\kasada-probe.dll $b64
```

**教训**：拿 JSON 当 CLI 参数喂给脚本引擎时，先确认到达引擎的字节和你想的一样。

### 5.31 合法 endpoints 被静默接受，然后什么都不做 [实测]

用 base64 保证引号完整后重测：

| 配置 | configure | isReady | requests | events |
|---|---|---|---|---|
| `{"endpoints":[{"domain":"www.nike.com","path":"/tl","method":"POST"}]}` | ok | 未触发 | `[]` | `["kpsdk-load"]` |
| 同上但 `method:"*"` | ok | 未触发 | `[]` | `["kpsdk-load"]` |
| `{"endpoints":[{"domain":"*","path":"/*","method":"*"}],"verbose":true}` | ok | 未触发 | `[]` | `["kpsdk-load"]` |

**三种都被接受（不报 schema 错），但没有任何后续动作** —— 不发请求、不派发新事件、不进入 ready。

而 schema 校验是**真的在工作**的：早先 `{"endpoints":[{"domain":"www.nike.com"}]}`（缺 `path`）
确实抛了错。**所以「接受」不是「忽略」，而是「接受了但没触发 interrogation」。**

### 5.32 这意味着 `configure` 不是唯一的入口

`configure` 通过 schema 校验却什么都不启动，说明还差一步 —— 候选：

1. **它还要求别的键**（`dynamicConfig` / `featureFlags` / `remoteConfig` / `siteId` 之类，
   字面量表里都有），缺了就走「等 iframe」那条静默路径
2. **调用时机**：真页面上 `KPSDK` 是**页面先放的 stub**，`p.js` 加载后**重放队列**。
   我们是「跑完 p.js 再 configure」，顺序可能不对
3. **`configure` 需要一个回调参数**（两个形参，`isReady` 一个）

**要继续往下，最省力的路是把真页面拿到手**：Nike 首页 HTML 里那段 `KPSDK.configure(...)`
或等价的 loader 脚本，直接照抄 —— 比猜 schema 快得多，也是唯一能保证「和真浏览器一致」的办法。

**本轮到此为止**：`configure` 的方向没错，但凭字面量拼配置拼不出来。

### 5.33 更正一个我读错的地方：`isReady` 是取值函数，不是回调注册

上一轮和这一轮我都写过「`isReady(cb)` 的回调没触发」—— **那是用法错了**。内省出来：

```
Object.getOwnPropertyNames(KPSDK) = ["configure", "isReady"]
KPSDK.configure.length = 1
KPSDK.isReady.length   = 0        ← 它不接受参数
KPSDK.configure.name   = "bound "  ← 都是 bind 过的函数
Object.getOwnPropertySymbols(KPSDK) = []
KPSDK 上没有嵌套对象（nested = {}）
```

**`isReady()` 是布尔取值函数**，问它「好了没」，而不是「好了叫我」。实测：

```
configure({"endpoints":[{domain:"www.nike.com", path:"/tl", method:"POST"}]})  → ok
KPSDK.isReady()                                                              → false
requests                                                                     → []
```

**所以「回调没触发」这个观察是假的** —— 它本来就不注册回调。真实结论只有一句：
**配了合法 endpoints 之后，`isReady()` 仍然是 `false`。**

同时 `configure.name === "bound "` 说明这两个都是 `Function.bind` 的产物 ——
和 opcode 41（`new (Function.bind.apply(v,i))`）对得上，是 payload 自己生成的导出面。

### 5.34 `configure` 不是空壳：它真的跑了 834 条字节码 [实测]

一直有个疑问是「configure 是不是个桩」。用一个计数器就能问清楚 ——
指令表是 `new Proxy(...)` 包的，每次 `u[opcode]` 取值都被记录下来：

```
configure 之前 dispatch 次数 = 9289
configure 之后 dispatch 次数 = 10123      ← 差 834
```

**所以 `configure` 执行了 834 条 payload 字节码**，然后停下来 —— 不是没跑，是**跑完某个分支后决定不继续**。

配合前面的事实（不发请求、不派发新事件、无待执行定时器、`isReady()` 仍 false），
最可能是走到了 `InterrogationSkipped` 这类「无事可做」的出口（该状态名在字面量表里）。

### 5.35 顺带修好的两处 shim 缺陷（都没能让它变 ready，但本来就该修）

**（1）`location` 的 `host` / `hostname` / `origin` 原来是空字符串**

```js
var location = { href: href, protocol: "https:", host: "", hostname: "", port: "", origin: "" };
```

只有 `href` 有值，其余全空。传感器要把配置里的 `endpoints[].domain` 和当前页面的
location 对上，空 host 会让任何真实域名都「不属于本页」。现在从 `href` 真解析出
`protocol` / `host` / `hostname` / `port` / `pathname` / `search` / `hash` / `origin`。

**（2）没有 `document.currentScript` / `baseURI`**

这两个名字都在字面量表里；看不见自己那个 `<script>` 的传感器没法解析相对端点。
现在都补上了（`currentScript.src` 暂时用 `location.href`，等真 URL 接进来再换）。

**修完这两处，`isReady()` 仍然是 `false`、requests 仍然是空** —— 所以它们不是主因，
但属于「本来就该对」的东西。

### 5.36 下一步：把这 834 条字节码的走向读出来

手上已经有现成的工具链（`analysis/instrument_payload.py` 插桩 + 按 `U` 规则解码），
之前就是靠它把崩溃点从「某个随机属性名」定到 `document.dispatchEvent` 的。现在把同一套用在这 834 条上：

1. 插桩记录 `pc + opcode`，并在 configure 前后各打一个标记
2. 取出标记之间的序列，按 `U` 解码
3. 看它从 `Configured` 走到哪个出口，以及那个出口的判断条件读了什么

**这比继续猜配置键名靠谱** —— 834 条指令足够看出它检查了什么。

### 5.37 做了：configure 的 834 条里看到什么 [实测]

**（1）它真的在处理配置 —— 工作量随配置变化**

| 配置 | configure 执行的 opcode 数 |
|---|---|
| `{}` | +325 |
| `{"endpoints":[]}` | +346 |
| `{"endpoints":[{"domain":"*","path":"/*","method":"*"}]}` | +816 |
| `{"endpoints":[{"domain":"www.nike.com","path":"/tl","method":"POST"}]}` | **+834** |

**同一个入口，配置越具体跑得越多** —— 所以它不是空壳，也不是无视入参。

**（2）它结束时是「故意 throw undefined」**

序列最后一条是 `pc=24266 op=57`，而

```js
// u[57]
function(n,e,a,v,i,o){ var r = o[0]; r(n, void 0) }     // o[0] 就是 j —— 抛异常的函数
```

`j(e,n)` 的语义是 `r.f = {A:n}`（把 n 记为当前异常）—— **所以 opcode 57 就是 `throw undefined`**。
这是这个 VM 的 `return` 惯用法：用一次被外层 catch 的 `throw` 表示「本函数结束」。
`configure ok=True` 也印证了它被自己接住了。

**（3）结尾那几十条是 `typeof` 能力探测**

```
24175:64 24178:51 24184:49 24187:64 24190:7 24194:12 24198:15 24201:40 24204:15 24207:11 24266:57
```

对照 handler 表：`34`=`typeof`、`24`=`!==`、`11`=`条件跳转`、`40`=`!`、`51`=取属性、`49`=`new Array`、`12`=调用。

**`typeof X` → `!==` → 条件跳转**，这是标准的能力探测形状。
所以 `configure` **在做完一串环境能力检查后决定不启动 interrogation** —— 而不是缺某个配置键。

**（4）它没有把活派给定时器**

configure 之后 `timers drained = 0, left = 0`，也没有任何请求。
**它是在同步路径里就决定结束的**，不是"等异步"。

### 5.38 解码那 834 条时踩到的两个坑（留给下一轮）

**坑 1：`head` 是 splice 之前抓的。**
`splice(13772, 6283)` 之后，VM 里的 `t` 与 `head` 的索引错开 6283：

```python
# post-splice 的 pc >= 13772，对应 head 里的 pc + 6283
def word(pc): return head[pc] if pc < 13772 else head[pc + 6283]
```

**坑 2：起手点必须是真正的指令边界。**
从 `24150` 硬解会读到 `224`（一个槽位操作数），因为那里是上一条指令的**参数中间**。
正确做法是从一个已知边界开始（比如 configure 第一跳的 `1621`），跟着 `63`（无条件跳转）走完控制流，
而不是截一段中间开始。

这两条都还没有解完 —— 下一轮从 `1621` 起手，带跳转把 configure 的完整控制流走一遍。

### 5.39 做出来了：一个能用的字节码反汇编器 [实测]

`analysis/walk_bytecode.py` —— 按 payload 自己的编码规则把 `t` 解成人能读的指令流。
**关键设计：不猜跳转，按实际执行轨迹解。**

原因是踩出来的：

- **静态跟 `63` 跳转能走通启动链**（从 `1621` 起手，`op=3` 建闭包 → `op=48` 写捕获 → `op=63` 跳，一路干净）
- **但 `11`（条件跳转）走不通** —— 它跳不跳取决于运行时值，静态解必然在 `24107` 处读到 `2373`（不是 opcode）

所以改成：**用插桩记录下来的 `(pc, opcode)` 序列作为真值，只在那些 pc 上解操作数**。这样不用模拟分支，
不存在"解偏了"这回事。

**期间修掉两个会让整个解码静默错位的计数 bug**（值得记）：

| 错在哪 | 后果 |
|---|---|
| 只数 `e(n)`，漏了 `r(n)` / `G(n)` | `r`/`G` 也是取字节码字的（`G(e)=e.m[t[e.m[0]++]>>5]`），漏数就每遇到一个就少读一个字 |
| 又把 `v(n)` 数进去 | `v` 是 `f(e)=e.m[1]`，**取的是帧本身，不消耗字节码** —— 多读一个字 |

**一个字都不能错**：这类虚拟机没有对齐标记，错一字之后所有边界全废，而且错得很像"这里不是 opcode"。

### 5.40 读到了 configure 的尾巴：它把一个迭代器跑到 done 然后正常返回

轨迹末尾解出来是这样：

```
1469  op=48   int:112, slot:5                    captured[112] = slot5
1472  op=64   int:112, slot:4                    slot4 = captured[112]
1475  op=51   slot:4, str:'value', slot:5        slot5 = slot4.value
1511  op=64   int:112, slot:5
1514  op=51   slot:5, str:'done',  slot:4        slot4 = <iter>.done
1520  op=11   slot:4, int:1538, slot:2           if (!done) jump 1538
1523  op=64   int:106, slot:6
1526  op=64   int:113, slot:8
1529  op=14   slot:6, slot:8, slot:4             slot4 = next(...)
1533  op=15   slot:4, slot:5
1536  op=63   int:1596
1596  op=57                                      throw undefined  ← 返回
```

**`.value` / `.done` 是迭代器协议**：configure 把一个异步迭代器（生成器）驱动到 `done`，
然后连续 `op=57`（`throw undefined`，即返回）逐层退出。

**所以 configure 是「正常跑完并返回」，不是「中途崩了」。**
它**根本没有启动 interrogation** —— 那个决定在更早的 834 条里。

**下一步很明确**：在这条已解出来的轨迹里找 `InterrogationStarting` / `InterrogationSkipped` 这类状态字样
被写进哪个槽位，以及写之前那个 `op=11` 的条件读了什么。工具和轨迹都已经在手上了。

### 5.41 找到了：配置键是 `resourceAddress`，不是 `endpoints` [实测]

把 configure 那 834 条按轨迹解出来后，出现频率最高的字符串里有一条很关键：

```
object x11   length x10   endpoints x5   push x4   isArray x4   getOwnPropertySymbols x4
* x3         http://example.com x2   domain x2   path x2   method x2
resourceAddress x1        'resourceAddress is required' x1
```

对应的指令片段：

```
25649  op=51   slot:5, str:'resourceAddress', slot:8     slot8 = cfg.resourceAddress
25658  op=18   slot:6, slot:8, slot:5, slot:4            slot4 = validate(slot8, ...)
...
22731  op=51   slot:5, str:'push', slot:6
22740  op=7    slot:7, int:0, str:'resourceAddress is required'
22746  op=12   slot:5, slot:6, slot:7                    errors.push('resourceAddress is required')
```

**`endpoints` 只是它读的众多键之一，真正必需的是 `resourceAddress`。**

### 5.42 给了 `resourceAddress` 之后：它发出真实请求了 [实测]

```json
{"resourceAddress":"https://www.nike.com/"}
```

仅这一个键，payload 就产出两条真实请求（`fetch` 记录器抓到的原文）：

```json
[
  { "via": "fetch", "method": "GET", "url": "https://www.nike.com/mfc",
    "headers": "{\"x-kpsdk-v\":\"j-1.2.988\",\"x-kpsdk-h\":\"01\"}" },
  { "via": "fetch", "method": "POST", "url": "https://www.nike.com/r",
    "headers": "{\"Content-Type\":\"text/plain\"}",
    "body": "exNATQUBXRsXQRVBEA1VRRMMDRASVEFBVlFTAgQJAA1aVwAPSm1BZQpCFhkNAkFBXQ0cQVIcQVcDUQIYAwEGDhxvQ2UMQxQZQ1BHGRJCHklMGlkOUUkOAAlUGQ1bDQAEZUJrVhUTERkDFxRQQxlD…" }
]
```

**注意 `x-kpsdk-v: j-1.2.988`** —— 和字面量里那个版本号对得上；`x-kpsdk-h: 01` 是 homepage 标记。

**这是整条本地路第一次产出真实的 Kasada interrogation 请求。**
之前每一轮都以为缺的是 `endpoints` 或更多配置键，实际只差 `resourceAddress` 这一个。

### 5.43 现在的位置：只差真实的响应

`/mfc` 与 `/r` 的**响应**才是 token 的来源（和 `08-cd.md` §9.1 的逆向结论一致：ct 是服务端回填的）。

试过把 `x-kpsdk-ct` 塞进 `/r` 的假响应头，**没有效果** —— 因为字面量里写着
`mfc response was missing one or more headers` / `KP_IC` / `KP_RC`：

**`/mfc` 是先决条件，它的响应头要先通过校验，SDK 才会去用 `/r` 的结果。**
我用 `KP_IC: "1"` / `KP_RC: "1"` 瞎填，显然不满足它的格式要求。

**所以下一个具体目标**：从字面量与轨迹里把 `/mfc` 的响应契约反出来（需要哪几个头、什么格式），
再让 `/r` 的响应头带上 `x-kpsdk-ct`，看 `isReady()` 是否翻成 true、token 落在哪。

**这一步已经不需要浏览器，也不需要猜配置键了** —— 只需要把两个 HTTP 响应的形状做对。

### 5.44 更正：configure 跑的不是 834 条，是 19,902 条 [实测]

上一轮那个「+834」是**采样截断**出来的数字（我 dump 时 `slice(0,1200)` 了）。
把 dispatch 上限从 20000 提到 60000 之后重新量：

```
加载完成（脚本自然结束）      9,289
configure 之后                29,191      ← 差 19,902
```

**这 19,902 条里包含了 `/mfc` 与 `/r` 的响应处理** —— 也就是说 fetch 的 Promise 回调
是在 `TryExecute("configure(...)")` 这一次 Evaluate 内部就被 Jint 排空跑完的，不是留到之后。

**修正因此很重要**：834 条只是开头，真正的逻辑在后 19,000 条里。

### 5.45 `/mfc` 的校验点找到了：读两个响应头，缺一个就抛 [实测]

把字节码捕获窗口从 32000 放宽到整个数组（75,771 字）之后，19,902 条里 **19,175 条能解出操作数**。
在里面搜 `mfc` 命中了唯一一处，上下文是这样的：

```
31751  op=64   int:1498, slot:4                    slot4 = captured[1498]        ← /mfc 的响应对象
31754  op=51   slot:4, str:'headers', slot:6        slot6 = res.headers
31760  op=51   slot:6, str:'get', slot:4            slot4 = res.headers.get
31766  op=49   int:1, slot:7                        slot7 = new Array(1)
31769  op=64   int:293, slot:9                      slot9 = captured[293]         ← 第 1 个头名
31772  op=7    slot:7, int:0, slot:9                slot7[0] = <头名1>
31776  op=12   slot:6, slot:4, slot:7               headers.get(头名1)
31783  op=48   int:1499, slot:5                     captured[1499] = 结果1
...
31804  op=64   int:294, slot:7                      captured[294]                 ← 第 2 个头名
31807  op=7    slot:6, int:0, slot:7                slot6[0] = <头名2>
31811  op=12   slot:5, slot:4, slot:6               headers.get(头名2)
31818  op=48   int:1500, slot:8                     captured[1500] = 结果2
31824  op=66   slot:4, null:None, slot:6            判空
31828  op=47   slot:6, int:31841, slot:2            条件
31841  op=11   slot:6, int:31864, int:40            条件
31844  op=81   str:'Error', slot:7                  window.Error
31852  op=7    slot:4, int:0, str:'/mfc response was missing one or more headers'
31858  op=41   slot:7, slot:4, slot:5               new Error([那条消息])
```

**结论：`/mfc` 的响应必须带两个特定响应头，名字存在 `captured[293]` 和 `captured[294]` 里；
缺任何一个就 `throw new Error('/mfc response was missing one or more headers')`。**

**这两个名字是在加载阶段写入的**（在 9,289 条那一段里），不属于 configure 的轨迹，
所以按 `op=48 int:293` 在 configure 段里搜不到 —— 这是下一步要补的一小段。

### 5.46 试过伪造这两个头，但没改变走向

把 `KP_IC` / `KP_RC` 塞进 `/mfc` 的假响应（`Response` 现在会认 `init.headers`），
三种组合跑出来的 opcode 数**完全相同（都是 29,191）**：

| 假响应头 | dispatch 总数 | isReady | cookie |
|---|---|---|---|
| 无 | 29,191 | false | 空 |
| `KP_IC:1` `KP_RC:1` | 29,191 | false | 空 |
| 上面两个 + `/r` 带 `x-kpsdk-ct` | 29,191 | false | 空 |

**说明这两个名字不是 `KP_IC`/`KP_RC`**（那两条只是字面量池里出现过，不代表就是这里要的头），
或者 payload 读的是被它自己包装过的 response 对象。两条路都要先把 `captured[293]/[294]` 的真实值取出来再谈。

### 5.47 环境阻塞（第四次）

这一轮里 `Cybersole.Stores` 又被另一个会话改到编不过（`MagentoFlow.cs(853)`: `PutAsync` 不存在）。
我**没有碰他们的文件**，改用 `analysis/kasada-probe` 独立 harness 继续；
最后一次想 dump 全量轨迹时正好撞上这次编译失败，跑的是旧二进制，所以那份 `slice(0)` 没生效。
下一轮重跑一次即可。

### 5.48 取到了：`/mfc` 要的两个头是 `x-kpsdk-h` 和 `x-kpsdk-fc` [实测]

上一轮说「`captured[293]` / `captured[294]` 存在加载阶段」——重跑全量轨迹后直接搜到了写入点：

```
16831  op=48   int:293, str:'x-kpsdk-h'
16836  op=48   int:294, str:'x-kpsdk-fc'
```

**所以 `/mfc` 的响应必须带 `x-kpsdk-h` 和 `x-kpsdk-fc` 两个头** —— 不是 `KP_IC`/`KP_RC`
（那两个只是字面量池里另有用途的字符串）。这也解释了上一轮为什么伪造 `KP_IC`/`KP_RC` 完全没有效果。

### 5.49 带上这两个头之后，走向确实变了 [实测]

| `/mfc` 假响应 | dispatch 总数 | 说明 |
|---|---|---|
| 空响应 | **29,191** | 走「missing headers」错误分支，绕了一大圈 |
| `x-kpsdk-h:01` + `x-kpsdk-fc:1` | **24,858** | 校验通过，少走了 4,333 条错误分支 |
| 上面两个 + `/r` 带 `x-kpsdk-ct` | **24,858** | 同上（`ct` 这时还没被消费） |

**dispatch 少了 4,333 条**就是证据：它不再走错误路径了。

### 5.50 下一个拦路的是 `/mfc` 的 **body**

校验通过之后，轨迹里出现了一条新的错误字样：

```
34983  op=48   int:377, str:'input is invalid type'
```

**所以 `/mfc` 的响应体不是可有可无的** —— 它要解码，而我们的空 body 解不出来。
（同段轨迹里还能看到 `InterrogationFailedToStart` / `InvalidDonePayload` /
`InvalidStateTransition` 这些状态名字面量，都是这台状态机的合法出口。）

### 5.51 `/mfc` 不能靠补配置键跳过 [实测]

试过在配置里加 `featureFlags` / `dynamicConfig` / `interrogation`（单独加、两两加、三个都加），
**五种配置全部仍然先 `GET /mfc` 再 `POST /r`，dispatch 数一律 29,191**。

**⇒ `/mfc` 是强制步骤**（它拿的是远程配置），不是可选优化。

### 5.52 现在的位置

```
✅ 脚本跑通（executed=True）
✅ configure({resourceAddress}) 触发真实请求
✅ GET  /mfc  → 需要 x-kpsdk-h + x-kpsdk-fc 响应头（已确认、已验证生效）
⬜ GET  /mfc  → 响应体必须能被它的解码器吃下（空 body 报 'input is invalid type'）
⬜ POST /r    → 响应头 x-kpsdk-ct 才是 token
```

**下一步**：把 `/mfc` 响应体的编码格式反出来。线索是 `34983` 附近那条 `input is invalid type`
所在的解码函数 —— 用 `analysis/walk_bytecode.py trace` 往上翻几十条就能看到它按什么规则校验输入。

### 5.53 更正：`input is invalid type` 是一条常量，不是运行时错误 [实测]

上一轮我把 `34983` 那条当成「`/mfc` 的 body 解码失败」。**错了。**

看它在整个 dispatch 序列里的位置：

```
第 221 条: 5232   op=62   int:376          ← 先占好三个槽位
第 222 条: 5234   op=62   int:377
第 223 条: 5236   op=62   int:378
第 4945 条: 34980 op=48   int:376, slot:4
第 4946 条: 34983 op=48   int:377, str:'input is invalid type'    ← 这里
第 4947 条: 34988 op=48   int:378, str:'finalize already called'
```

**第 4946 条 < 9289（加载阶段结束点）**，所以它是在**模块初始化时把一个消息字符串写进常量槽**，
和旁边那条 `'finalize already called'` 是同一个套路。**它不是抛出来的错误。**

紧接着的 `34993 op=81 str:'ArrayBuffer'` → `34998 op=34 typeof` → `35001 !== 'undefined'`
也印证了这一段是**模块级能力探测与常量表填充**，不是响应处理。

**教训（和 AGENTS.md §2.7 同一条）**：看到某个字符串就推断"它报了这个错"，
等于先假设形状再把不符合的读成结论。**判据是这条 dispatch 落在加载阶段还是 configure 阶段。**

### 5.54 拿到了整张头名槽位表 [实测]

加载阶段 pc 16811–16836 连续写入六个槽位：

```
16811  op=48   int:289, str:'x-kpsdk-ct'
16816  op=48   int:290, str:'x-kpsdk-v'
16821  op=48   int:291, str:'x-kpsdk-r'
16826  op=48   int:292, str:'x-kpsdk-c'
16831  op=48   int:293, str:'x-kpsdk-h'
16836  op=48   int:294, str:'x-kpsdk-fc'
...
43148  op=48   int:399, str:'x-kpsdk-cd'
```

**这就是 payload 自己用的九个头名表。** `captured[289]` 就是 token 头 `x-kpsdk-ct`。

### 5.55 关键：`x-kpsdk-ct` 在 configure 之后一次都没被读过 [实测]

统计这些槽位在整条轨迹（24,858 条，带 `/mfc` 假头）里的读取次数：

| 槽位 | 头名 | 被读次数 | 最后一次出现的位置 |
|---|---|---|---|
| `captured[289]` | `x-kpsdk-ct` | **1** | **第 5865 条（加载阶段）** |
| `captured[290]` | `x-kpsdk-v` | 2 | 加载阶段 |
| `captured[291]` | `x-kpsdk-r` | **0** | — |
| `captured[292]` | `x-kpsdk-c` | **0** | — |
| `captured[293]` | `x-kpsdk-h` | 3 | 加载 + `/mfc` 校验 |
| `captured[294]` | `x-kpsdk-fc` | 1 | `/mfc` 校验 |
| `captured[399]` | `x-kpsdk-cd` | **0** | — |

**`x-kpsdk-ct` 只在加载阶段被读过一次，configure 之后再也没有。**
`x-kpsdk-r` / `x-kpsdk-c` / `x-kpsdk-cd` **整个运行里一次都没被读**。

**⇒ 状态机根本没走到「消费 token」那一步。** 它不是在等响应，是没进那个分支。

**所以下一轮要问的不是「响应该长什么样」，而是「它在 `/mfc` 校验通过之后为什么没继续推进」。**
轨迹末尾那次迭代器 `done` + 连续 `op=57`（返回）就是它退出的地方 —— 退出前那次 `op=11` 的条件读了什么，才是答案。

### 5.56 硬证据：`/mfc` 校验确实通过了（换成"错误有没有被构造"当判据）[实测]

上一轮我用「dispatch 从 29191 降到 24858」推断校验通过 —— **那是间接推断**。这轮换成直接判据：
那条 `new Error('/mfc response was missing one or more headers')` 的构造点在 **pc 31858**，
看它在不在执行轨迹里：

```
不加假头   dispatch=29191   pc 31858 被执行?  YES   ← 走了错误分支
加假头     dispatch=24858   pc 31858 被执行?  no     ← 校验通过
```

**这才是判据**：错误对象根本没被构造，说明两个头都读到了。

### 5.57 状态机的转移表找到了 [实测]

加载阶段 pc 16935–16989 连续写入一张 `状态名 → 处理器地址` 的表：

```
16935  op=7   slot:4, str:'InterrogationStarting',      int:17167
16941  op=7   slot:4, str:'InterrogationComplete',      int:12707
16947  op=7   slot:4, str:'InterrogationSkipped',       int:45008
16959  op=7   slot:4, str:'InterrogationFailedToStart', int:65149
16989  op=7   slot:4, str:'InvalidStateTransition',     int:90102
```

### 5.58 configure 的结尾：把状态写成 `Configured` 并结束那个任务

configure 阶段（第 13233 条 dispatch，pc 68558–68612）解出来是：

```
68564  op=64   int:2927, slot:5                    slot5 = <任务/迭代器>
68567  op=51   slot:5, str:'abrupt', slot:4        slot4 = task.abrupt
68573  op=49   int:2, slot:9                       slot9 = new Array(2)
68576  op=7    slot:9, int:0, str:'return'         slot9[0] = 'return'
68582  op=19   slot:8                              slot8 = {}
68584  op=7    slot:8, str:'type', str:'Configured'        slot8.type = 'Configured'
68592  op=64   int:2920, slot:10                   captured[2920] = 配置对象
68595  op=7    slot:8, str:'configuration', slot:10       slot8.configuration = <配置>
68601  op=7    slot:9, int:1, slot:8               slot9[1] = slot8
68605  op=12   slot:5, slot:4, slot:9              task.abrupt('return', {type:'Configured', configuration})
```

**即：configure 以 `{type:'Configured', configuration}` 收束当前任务。**

**然后就没有了。** 搜遍整条 24,858 条的轨迹，`'InterrogationStarting'` **只在那张表里出现过一次，
从来没有被当作转移目标写出来。**

**⇒ 状态停在 `Configured`，永远没走到 `InterrogationStarting`。**

### 5.59 直接证据：传感器没有给任何请求加过头

`sensor` 的真实产出不是"返回一个字符串"，而是**包装 fetch/XHR、往页面自己的请求上注入 `x-kpsdk-*`**。
所以这轮直接试了一次真实调用：configure 之后发 `fetch('https://www.nike.com/tl', {method:'POST'})`，
看 `fetch` 记录器收到什么：

```
protected-call issued ok=True result=ok
headers added = {"url":"https://www.nike.com/tl","method":"POST","body":"probe=1","headers":null}
```

**`headers: null` —— 一个头都没加。**

配合 §5.55（`x-kpsdk-ct` 在 configure 后一次都没被读）和 §5.58（状态停在 `Configured`），
三条互相印证：**传感器没进入能注入头的状态。**

### 5.60 下一轮的问题变得很具体

不是"响应长什么样"，也不是"缺哪个配置键"，而是：

> **`Configured` 之后，谁负责把它转到 `InterrogationStarting`？**

表里写好了一个处理器地址 `17167`，只要找到"读状态、查表、跳转"的那个分发函数，
再往上游看是谁应该触发它，就能定位到缺的那一步。

### 5.61 查了：调度器根本不存在 —— 整条轨迹里没有一次读 `.type` [实测]

搜遍 24,858 条轨迹，`str:'type'` **只出现一次**，而且就是 configure 自己写状态那次：

```
第 13233 条: 68584  op=7  slot:8, str:'type', str:'Configured'
```

**没有任何地方读它。** 也就是说：状态对象被造出来、交给 `abrupt('return', …)`，
**然后没有分发器去消费它** —— 状态机停在那里不是"判断为假"，是**根本没有下一个驱动者**。

这解释了为什么 §5.55 里 `x-kpsdk-ct` 一次都没被读、§5.59 里一个头都没加：
它们都排在这台状态机的后半程，而前半程结束后就没人推了。

### 5.62 交叉核对：这个结论和档案里早就写下的判断是同一件事

回头读自己前几轮写的两份档：

**`02-local-jint.md` L345**：

> 对 Nike 的现行构型实测：`KPSDK` 只暴露 `configure` 与 `isReady`，`ct()` / `sb()` / `cd()` 全都不存在。

**`02-local-jint.md` L287**：

> 按优先级探出口；现代构型常常只有 configure/isReady，那就退到嗅探（见 03）。

**`03-browser.md` 开篇**：

> **一句话**：别管脚本怎么算，把页面加载起来，让它自己算，然后**从线上把结果捞出来**。
> token 不需要"逆"出来 —— 它一定会出现在脚本发出的下一个请求的请求头里。

**`03-browser.md` §1**：DotNetBrowser 4.3.5 的定位是「既给 UI 内嵌浏览器，也给 Jint 跑不动的站点兜底」，
Jint 与 Chromium **是两条并存的路**。

**⇒ 本轮实测到的"状态机停在 Configured、没人推进"正是档案里记录的那个决策条件的实证。**
不是新问题，是旧结论的第一次指令级验证。

### 5.63 因此这条路线的边界要写清楚

| 层次 | 状态 |
|---|---|
| 脚本能在 Jint 里完整跑完 | ✅ 已达成（`executed=True`） |
| `configure` 真的被消费、发出 interrogation 请求 | ✅ 已达成（`GET /mfc` + `POST /r`，带 `x-kpsdk-v: j-1.2.988`） |
| 请求形状与真实前端一致 | ✅ 已核对到指令级 |
| **从响应里取回 token** | ❌ 未达成 —— 需要**真实**的 `/mfc` 与 `/r` 响应 |
| 真浏览器 + 从请求头捞 token | ✅ 复刻件已有（`ChromiumKasadaSolver.cs`），与原版并存的第二条路 |

**关键认识**：payload 的状态机在**独立宿主**里不会自己推进到 interrogation 后半程。
这不是 shim 缺一个方法（前几轮那种），而是**它的设计前提就是「有真实端点可打」**。
我们给的空 200 能骗过头部校验，骗不过后半程对响应内容的依赖。

### 5.64 于是把这一格补上了：本地路现在能产 token（产品代码里）[实测]

既然 payload 只负责**发** interrogation、不负责**收** token，那收的部分就该由宿主做。
这轮落成了两件事：

**（1）`ScriptRuntime.HttpTransport` —— 唯一的网络缝隙**

```csharp
/// Arguments are (url, method, headersJson, body); returns JSON {"status","headers","body"} or null.
public Func<string, string, string, string, string?>? HttpTransport { get; set; }
```

shim 的 `fetch` 在末尾接上它：装了传输就把请求真发出去并把响应包成 `Response`，
没装就还是离线空 200（**默认零网络**，沙箱用例不受影响）。

**（2）`KasadaSolver.ResourceAddress` + `.Transport` —— 把配置与收 token 接进产品路径**

```csharp
solver.ResourceAddress = "https://www.nike.com/";
solver.Transport = (url, method, headers, body) => /* 真发，返回 JSON */;
var result = solver.Solve(script);
```

`Solve` 现在的顺序是：跑脚本 → `configure({resourceAddress})` → payload 自己发 `/mfc`、`/r`
→ 传输层真发 → **从 `/r` 的响应头读 `x-kpsdk-ct`** → 填 `KasadaResult.Ct`。

**实测（探针跑一次产品路径）：**

```
Solve -> Ok=True Ct=PRODUCTPATHCT0123456789 Executed=True
Error = -
```

**这是整条本地路第一次在产品代码里拿到 token。** 之前每一轮都停在"payload 跑完了但没有 ct"，
根因是**没人去读响应头**，不是脚本算不出来。

### 5.65 用测试把这条契约钉住

新增 `KasadaInterrogationTransportTests`（3 例，与原有 58 例一起 **61/61 通过**）：

| 用例 | 钉住什么 |
|---|---|
| `TheSensorInterrogatesItsEndpointsAndTheTokenComesOffTheResponse` | 顺序是 `GET /mfc` → `POST /r`；`/r` 的 body **> 100 字节**（不是空壳）；`Ct` 来自响应头 |
| `WithoutAResourceAddressNothingIsInterrogated` | 没有 `resourceAddress` 时**一个请求都不发**、`Ok=false` |
| `WithoutATransportTheRunStaysOfflineAndReportsNoToken` | 没装传输时保持离线、不产 token |

第二条尤其重要：它把「`resourceAddress` 是必需键」这个结论从实测变成了回归防线。

### 5.66 生产传输：`KasadaSolver.NetTransport`（走复刻件自己的 HTTP 栈）

```csharp
var transport = KasadaSolver.NetTransport(http);   // http 是 NetClient
```

它做的事就是把 payload 的请求**原样**翻译成 `NetClient.SendAsync`：

- 方法用它给的（`POST` / `GET`），不做"优化"
- 头用它给的（`x-kpsdk-v` 之类），合并进 `RequestOptions.Headers`
- 请求体用它给的（`/r` 那个 460 字节的编码串），`StringContent(..., text/plain)`
- 响应回来原样序列化成 `{status, headers, body}` 交回脚本

**为什么必须走 `NetClient` 而不是 `HttpClient`**：复刻件的 TLS/HTTP-2 指纹（`Ja3` / `TlsProfile` / `BouncyH2Client`）
是整条结账流程共用的，interrogation 请求如果用别的栈发，指纹就和后面那些请求不一致。

### 5.67 一个真实的健壮性缺口，是测试逼出来的

写适配器测试时发现：`NetClient.SendAsync` 对**连不上**的端点会**抛异常**，不是返回 status 0。
如果这个异常从 `NetTransport` 逃出去，脚本引擎会把它读成「这个站需要浏览器」，
而不是「那个主机没通」—— **错误归因反了**。

所以 `NetTransport` 内部兜住：

```csharp
catch (Exception ex) when (ex is not OutOfMemoryException)
{
    return JsonSerializer.Serialize(new { status = 0, headers = ..., body = "", error = ex.Message });
}
```

**并且保留 `ScriptRuntime.CallHttp` 外面那层兜底** —— 两层，因为传输层是可插拔的，
别人写的传输不该能靠一个异常把整个 solve 打成"需要浏览器"。

### 5.68 用原始 TcpListener 把适配器钉住

新增 `KasadaNetTransportTests`（3 例）。服务端是**手写的 TcpListener**，不是 `HttpListener` ——
后者在 Windows 上要 URL ACL，测试会变成"看权限脸色"；手写的一个端口就够，还能**读到线上真实字节**：

| 用例 | 断言什么 |
|---|---|
| `TheTransportSendsThePayloadsMethodHeadersAndBodyAndReturnsTheResponseHeaders` | 线上第一行是 `POST /r `；body 里有 `encoded-interrogation-body`；`x-kpsdk-v` 到了；响应头 `x-kpsdk-ct` 原样回来 |
| `TheTransportSurfacesUnreachableEndpointsWithoutThrowing` | 打 `127.0.0.1:1`（本机立即 refused）→ 返回可解析 JSON 且**不抛** |
| `TheTransportRefusesToBeBuiltWithoutAClient` | 空 `NetClient` 直接 `ArgumentNullException` |

第一个用例是关键：它验证的不是"函数被调用了"，而是**线上字节就是 payload 想发的那一份**。

**非浏览器 Kasada 用例现在 64 例全绿**（58 + 3 契约 + 3 适配器）。

### 5.69 反查原版：它有一条完整的 mobile 解算链，复刻件一条都没有 [Obs]

这轮把原版的 Kasada 解算器结构从字符串池里读出来了（`ida.py str`，地址是 `chars_va`）：

**解算器的主链路（第一个类，异步状态机 `d__46`–`d__50`）：**

```
0x14345a632   <HandleResponse>d__46  <GetScript>d__47  <GetKasada>d__48
0x14345a681   <GetMfc>d__49  <GetWorkTime>d__50
              <<-ctor>b__43_0>d   <<GetKasada>b__48_2>d   <<GetMfc>b__49_1>d
```

**第二个类（`d__32`–`d__36`），同样的五步：**

```
0x14345abb1   <HandleResponse>d__32  <GetScript>d__33  <GetKasada>d__34  <Ge…
```

**两个类的五步完全同构：`HandleResponse → GetScript → GetKasada → GetMfc → GetWorkTime`。**

**接口与 DTO：**

```
0x1433216f6   IKasadaSolver
0x143321733   KasadaSolveResult
0x1433218dc   KasadaSolveRequest
```

**mobile / MFC 开关与处理器：**

```
0x14345a7e8   get_IsMobile / set_IsMobile
0x14345a802   get_MfcEnabled / set_MfcEnabled
0x14345a811   get_VersionProvider / set_VersionProvider
0x14345aaee   <IsMobile>k__BackingField  <MfcEnabled>k__BackingField  <VersionProvider>k__BackingField
0x14344855b   get_MobileDv / MobileDv
0x143448fbe   GenRandomIos
0x1433048fd   get_SpoofMobile / set_SpoofMobile
0x143334b22   KasadaMobileHandler
0x143370d5b   _kasadaMobile
```

**对照复刻件：**

| 原版 | 复刻件 | 状态 |
|---|---|---|
| `GetScript` | `FetchScriptAsync` | ✅ |
| `GetKasada` | `Solve`（Jint + 传输 + 收 token） | ✅ |
| `GetMfc` | 由 payload 自己发 `/mfc` | ⚠️ **语义不同**：原版是宿主侧独立方法 |
| `GetWorkTime` | `WorkTimeMs` 只测不调 | ⚠️ 原版是独立方法 |
| `HandleResponse` | `HeaderFromTransport` | ⚠️ 只取了头，没做完整响应处理 |
| 第二个解算器类（`d__32`–`d__36`） | **无** | ❌ |
| `IsMobile` / `MfcEnabled` / `VersionProvider` | **无** | ❌ |
| `MobileDv` / `SpoofMobile` / `GenRandomIos` | **无** | ❌ |
| `KasadaMobileHandler` / `_kasadaMobile` | **无** | ❌ |

**这正是 `mfc` 这轮出现的原因**：`GetMfc` 在原版里是**独立一步**，
我们之前一直以为 `/mfc` 只是 payload 内部的一个请求 —— 原来是**宿主也要参与的一步**。

**⇒ 「完整复刻」的剩余工作面现在有明确清单了**：
第二个解算器 + 四个 mobile 开关 + `KasadaMobileHandler`，共 7 个符号、一条五步链。
这些不是"再猜"，是从字符串池直接读出来的地址与名字。

### 5.70 回答了上轮的问题：**同一份脚本，不是两套脚本** [实测]

上轮留的问题是「mobile 路是另一套脚本 + iOS UA，还是同一脚本换配置」。查 payload 自己的字面量表
（6,309 字符，全量）：

```
userAgent   x1
iPhone      x0      iPad    x0      iPod    x0      iOS   x0
Android     x0      Mobile  x0      Safari  x0      Touch x0
maxTouchPoints x0   platform x0     Apple   x0      MacIntel x0
```

**一个移动端标记都没有。** 它只读 `navigator.userAgent`（出现一次），其余全靠宿主给什么就用什么。

**⇒ Nike 的 `p.js` 是设备无关的。原版那两个解算器类（`d__46`–`d__50` 与 `d__32`–`d__36`）
跑的是同一份脚本，差别在宿主侧的身份与开关**（`IsMobile` / `MfcEnabled` / `MobileDv` /
`SpoofMobile` / `GenRandomIos` / `VersionProvider`）。

顺带说明为什么按符号直接找 `KasadaMobileHandler` 走不通：它是**元数据里的类型名**，
`obj_va = chars_va - 12` 的 xref 为 0，`disp32_scan_any.py` 全 `.text` 滑窗也是 **0 site** ——
反射用的名字，没有代码直接引用它。这条路到此为止，改从脚本侧取证才是对的。

### 5.71 落了 mobile 身份的地基：`BrowserShim` 现在能如实扮演一台 iPhone

原来 shim 里有三个字段是**写死的**，对移动路是硬伤：

```js
platform: platform, vendor: "Google Inc.",          // vendor 恒为 Google
hardwareConcurrency: cores, deviceMemory: 8, maxTouchPoints: 0,   // 触摸点恒为 0
```

**「UA 说是 iPhone、触摸点报 0」是自相矛盾的指纹**，站点一眼看穿。现在三项都可配：

```csharp
public int    MaxTouchPoints { get; init; }        // 默认 0（桌面正确值）
public string Vendor         { get; init; } = "Google Inc.";
public double DeviceMemory   { get; init; } = 8;
```

外加一个现成的 iPhone 档：

```csharp
var shim = BrowserShim.Ios();   // iPhone OS 17_5 / Safari 604.1 / platform iPhone /
                                // vendor Apple Computer, Inc. / touch 5 / cores 6 / 390x844
```

**`BrowserShimMobileProfileTests`（3 例）钉住**：

| 用例 | 断言 |
|---|---|
| `TheIosProfileReportsATouchDeviceConsistently` | UA 含 iPhone、platform=iPhone、vendor=Apple、`maxTouchPoints=5`，且 `iPhone && maxTouchPoints>0` 为真 |
| `TheDesktopDefaultStillReportsNoTouch` | 桌面默认仍是 `0` 触摸点、`Google Inc.` —— 防止加 mobile 时把这个值带漂 |
| `AProfileCanOverrideEveryFieldSitesRead` | Android 档能逐项覆盖 UA/platform/vendor/touch/cores/memory |

第二条是回归防线：这个 `0` 在本次改动前是全仓所有沙箱运行的值，不能被顺手改掉。

**Kasada 相关用例 + 这三个 = 78 例全绿。**

### 5.72 三个开关接上了：`MfcEnabled` / `MobileDv` / `VersionProvider`

| 开关 | 语义（落地后） |
|---|---|
| `VersionProvider` | `Func<string?>`。默认**从 payload 自己发出的请求头里取 `x-kpsdk-v`** —— 那是唯一权威来源（`/mfc` 请求上就带着 `j-1.2.988`），不是从 token 里猜 |
| `MobileDv` | 非空时作为 `x-kpsdk-dv` 报出；桌面路留空，和原版一致 |
| `MfcEnabled` | 默认 true。为 false 时**宿主自己不发 `/mfc`**（传输层直接回 503） |

**`VersionProvider` 的默认值来源值得单说**：

```csharp
Version = VersionProvider?.Invoke()
          ?? HeaderFromIssuedRequest("x-kpsdk-v")        // ← 新增，权威
          ?? Runtime.TryString("KPSDK && KPSDK.v ? …")   // 老路：脚本暴露
          ?? Regex.Match(ct ?? "", @"^\s*(\d+)\|")…      // 兜底：从 token 推断
```

**优先级从「可靠」到「猜」排列**，并且三层都有测试覆盖：默认取到 `j-1.2.988`、
`VersionProvider` 能覆盖成 `j-9.9.999`、桌面路不带 `x-kpsdk-dv` 而 mobile 路带。

### 5.73 一个和预期不同的实测：`/mfc` 失败**不会**让传感器停下

写 `MfcEnabled=false` 的用例时，我先假设「拿不到远程配置 → 握手终止 → 不产 token」。**实测不是这样。**

把 `/mfc` 回 503 之后：

```
宿主发出的请求：POST /r          ← 没有 /mfc（开关生效）
结果：Ct = CT-SWITCH-TEST-…      ← token 照样拿到了
```

**⇒ 传感器在 `/mfc` 失败后仍然继续发 `/r`。** 所以 `MfcEnabled` 是「宿主做不做自己那步 mobile 请求」的开关，
**不是整个握手的硬门**。

断言按实测改了，并且把这条写进注释 —— 这类「和直觉相反但被数据钉住」的行为，
比一个看起来自洽的假设值钱得多。

**Kasada + profile 用例现在 82 例全绿。**

### 5.74 两个解算器类到底是什么关系：**不是 desktop/mobile 之分**

上轮留的问题是「第二个类（`d__32`–`d__35`）是 mobile 专用，还是另一种站点构型」。
把整张 Kasada 符号表拉出来之后，答案很清楚：

**三个 Handler 类型：**

```
0x143334518   KasadaHandler
0x143334b22   KasadaMobileHandler
0x143321dfa   KasadaCdSolver          ← cd 有专门的解算器
```

**两个状态机块的差异（关键）：**

| 块 | 方法 | 有没有 `GetMfc` |
|---|---|---|
| `0x14345a632` / `0x14345a681` | `<HandleResponse>d__46` `<GetScript>d__47` `<GetKasada>d__48` **`<GetMfc>d__49`** `<GetWorkTime>d__50` | **有** |
| `0x14345abb1` | `<HandleResponse>d__32` `<GetScript>d__33` `<GetKasada>d__34` `<GetWorkTime>d__35` | **没有** |

**而 `IsMobile` / `MfcEnabled` / `VersionProvider` 三个属性和它们的 BackingField
（`0x14345a7e8` / `0x14345a802` / `0x14345a811` / `0x14345aaee`）落在第一块里。**

⇒ **第一块是「带远程配置能力、可切 desktop/mobile」的完整 handler；
第二块是一个更简的 handler，干脆没有 `/mfc` 这一步。**

**所以第二个类不是"mobile 版"，而是"不需要远程配置的站点版"。**
**复刻件不需要拆成两个类** —— 一个 `KasadaSolver` 加 `IsMobile` + `MfcEnabled` 就能表达两者，
这正好和 §5.70「payload 本身设备无关」对上：差别在配置，不在脚本，也不在类。

### 5.75 顺带查到两件之前没记账的事

**（1）`cd` 有独立解算器**：`KasadaCdSolver`（`0x143321dfa`）。
`08-cd.md` 花了一整篇追 `cd` 的来源，原来原版把它做成了**独立组件**，不是主解算器里的一步。

**（2）`x-kpsdk-v` 的版本号是 per-store 配置键**，一共 7 个：

```
0x146b9ec2c  Converse-Kasada-Version
0x146ba9d64  Crocs-EU-Kasada-Version
0x146ba9eec  Crocs-JP-Kasada-Version
0x146baa03c  Crocs-Kasada-Version
0x146d93f64  Footsites-Kasada-Version
0x146e1779c  Nike-Kasada-Version
0x146e7a4d4  Scheels-Kasada-Version
```

**这和 §5.72 的 `VersionProvider` 是一回事**：原版给每个站单独存 Kasada 版本号，
因为各站部署的传感器版本不同（Nike 现在是 `j-1.2.988`）。
复刻件目前只有 `VersionProvider` 这个钩子，**没有 per-store 的取值表** —— 这是一个明确的待补项。

### 5.76 补上了 per-store 版本表，并且发现原清单少记了两个 [实测 + 修正]

`KasadaVersions`（`replica/src/Cybersole.Stores/Scripts/KasadaVersions.cs`）：

```csharp
public const string Observed = "j-1.2.988";
public static string? For(string? store);              // 未测过的站 → null
public static IReadOnlyList<string> SettingKeys;       // 七个键，逐字
public static string? StoreOfSetting(string key);      // "Crocs-EU-Kasada-Version" → "crocs-eu"
```

**`For` 对未测过的站返回 `null` 而不是默认值** —— 这是一轮里改过的设计：
最初返回 `Observed`，结果把 `Version` 从"空"变成"永远有值"，**撞红了既有的
`Solve_ReadsClientTokenFromScript`**（那条用合成脚本，本来就没有版本可得）。

**而这是对的**：这张表是回退链里的一环，对一个没测过的站宣布一个版本号，
等于让链在"猜"上停住。返回 null，链才能继续往下走。

**所以 `Version` 的优先级最终是这个顺序（从权威到兜底）：**

```csharp
VersionProvider?.Invoke()            // 调用方显式指定
?? HeaderFromIssuedRequest("x-kpsdk-v")   // payload 自己印的，权威
?? KasadaVersions.For(Store)              // per-store 表，仅当上面观察不到
?? Runtime.TryString("KPSDK && KPSDK.v …")
?? Regex.Match(ct ?? "", @"^\s*(\d+)\|")
```

### 5.77 顺带修了一个少记：清单里只有 5 个，二进制里是 7 个

`AntiBotVendors.KasadaVersionHeaders` 原来只写 5 个：

```
Converse / Crocs-EU / Crocs-JP / Crocs / Footsites      (5)
```

**但二进制里是 7 个** —— 多了 `Nike-Kasada-Version`（`0x146e1779c`）和
`Scheels-Kasada-Version`（`0x146e7a4d4`），**而且这两个站的 flow 在复刻件里都实现了**。

`KasadaVersionsArePerStore` 原来硬断言 `Assert.Equal(5, …)`，所以它红了一次。
**按"数字随事实走"的规矩改成 7，并把两个新地址写进断言旁边的注释** ——
红的不是行为，是清单本身少记了两条。

**Kasada + AntiBot + profile 用例：97/97 通过。**

### 5.78 `GenRandomIos` 落地：随机但**自洽**的 iPhone 身份

`GenRandomIos` 在二进制里只出现一次（`0x143448fbe`），**没有 `get_`/`set_` 前缀** ——
所以它是字段而不是属性（对比 `MfcEnabled` 是属性）。语义从名字就够清楚：每次跑用一台随机 iPhone。

**关键是"随机"不能等于"乱凑"**。一台声称是 iPhone 15 Pro 的设备如果屏幕是 1920×1080、核心数是 16，
那这个指纹一眼就假。所以落地成**一组真实机型档**，UA / 视口 / 核心 / 内存**整组一起换**：

```csharp
BrowserShim.Ios(int index)           // 按序号取，越界自动回绕
BrowserShim.RandomIos(Random? rng)   // 随机取，给种子就复现
BrowserShim.IosUserAgents            // 五台的 UA，顺序与上面一致
```

五档覆盖 iOS 15.4 → 17.5、375×667 到 428×926、4/6 GB 内存。

**`BrowserShimRandomIosTests`（3 例）钉的是"自洽"而不是"会变"：**

| 用例 | 断言 |
|---|---|
| `EveryProfileIsInternallyConsistent` | UA 含 iPhone + `AppleWebKit/605.1.15` + `Safari/604.1`；platform=iPhone；vendor=Apple；touch=5；cores∈[4,8]；**高>宽**且宽∈[320,500] |
| `RandomSelectionIsReproducibleFromASeed` | 同种子同结果；40 个种子里确实出现多种 UA（否则"随机"就是伪装成随机的固定值） |
| `OutOfRangeIndicesWrapInsteadOfThrowing` | `Ios(n)` 与 `Ios(n ± 档数)` 等价 —— 调用方拿随机数取档，越界不该炸 |

### 5.79 踩到一个 C# 静态初始化顺序的坑（值得记）

第一版把 `IosUserAgents`（`IosProfiles.Select(...)` 投影）写在 `IosProfiles` **前面**，
结果整个类型初始化抛 `TypeInitializationException`：

> **静态字段初始化器按声明顺序执行** —— 投影先跑时 `IosProfiles` 还是 null，
> `Select` 直接 `ArgumentNullException`。

**修法就是把数组挪到投影之前**，并在文件里留了注释说明为什么顺序不能换。
这类错误在编译期完全看不出来，只会在**第一次触碰该类型**时炸，而且报的是"类型初始化失败"，
不是"字段是 null"——很容易被误判成别的问题。

**Kasada + BrowserShim + AntiBot 用例：103/103 通过。**

### 5.21 序列对比（调查过程）：失败路径里多了一次全局读取 [实测]

记录滚动窗口（最近 45 条 dispatch），在每次调用指令前快照，按「被调槽位是否为空」分成两组：

```
失败（callee 为 undefined）末尾：
  ... 3591:20 3595:81 3600:51 3606:51 3612:49 3615:64 3618:7   ← 之后就是那一次调用
成功（callee 存在）末尾：
  ... 5005:3 5012:63 69477:80
```

**差别非常明显：**

- **成功路径**是 `3 → 48 → 63` 的重复（建闭包 → 写捕获 → 跳），一路干净地建到 `m[5]`
- **失败路径**在崩之前多出 **`81`（读全局）**，随后是 `51`（取属性）、`49`、`64`、`7`

`81` 就是 §5.14 说的「按名字从 `window` 取值」。它在失败路径里出现，而成功路径里没有 ——
**这正是「某条指令读到不存在的全局、抛在 try 里被吞、流程歪掉」的那个形状。**

六次失败的窗口有两种形态：`fail0/2/5` 带 `81`，`fail1/3/4` 是 `31 → 51 → 49 → 3 → 63`（走了建闭包却仍没写对槽）。

### 5.22 payload 到底要哪些全局（调查过程） [实测，名字部分解出]

记录每次 `81` 的三个原始操作数 `(pc, f1, f2, f3)`，共 **124 次读取、7 个不同名字**。
把 payload 自己解出来的字面量表（`DecodedStrings`，6309 字符）当作坐标系去查，能定出真实名字：

| 名字 | 在字面量表里的位置 |
|---|---|
| `navigator` | 176 |
| **`ArrayBuffer`** | 375 |
| **`getOwnPropertyDescriptor`** | 4462 |
| `iframe` | 5253 |
| `setTimeout` | 6154 |

**其中两个是关键缺口** —— 它们在浏览器里存在，但在我的 shim 的**全局作用域**里不存在：

- **`getOwnPropertyDescriptor`**：浏览器里 `Object.getOwnPropertyDescriptor` 存在，
  但**裸的 `window.getOwnPropertyDescriptor` 并不存在**；payload 走的是 `81`（读全局）拿到 `undefined`
- **`iframe`**：浏览器里没有名为 `iframe` 的全局变量，正常路径是 `document.createElement('iframe')`

**其余（`ArrayBuffer` / `navigator` / `setTimeout`）在 shim 里都有** —— 说明失败不是它们造成的。

**注意**：`f2/f3` 这两个操作数的解码还没对齐（记录到的是原始编码值，不是解码后的 `len/off`），
所以上表的位置是靠「在字面量表里搜真实名字」反推的，不是直接算出来的。
下一步要把 `81` 的四个操作数按 `U` 的规则解一遍，才能把「哪个 pc 要哪个名字」精确对上。

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

# 纯脚本路径的用例（不启浏览器）—— 应全绿
D:\tools\dotnet8\dotnet.exe test tests\Cybersole.Tests -m:1 `
  --filter "FullyQualifiedName~Kasada&FullyQualifiedName!~NikeKasadaFlowTests&FullyQualifiedName!~KasadaIntrospectionTests&FullyQualifiedName!~KasadaHeaderSurfaceTests"
```

`KasadaPayloadBootstrapTests` 会钉住：`start/count/len` 三个数与字节码头四个值。

**浏览器依赖的三个类**（`NikeKasadaFlowTests` / `KasadaIntrospectionTests` / `KasadaHeaderSurfaceTests`，共 11 个用例）
**不要和全量一起跑**：它们各自会拉起 DotNetBrowser 的 Chromium，整批跑时互相抢资源，
表现为随机失败（每次挂的成员都不一样，耗时 18–51 秒），而且退出后残留 chrome 进程会累积
（实测一次跑到 48 个）。**单独跑一个类或一个用例时通过。**

这和 AGENTS §4 记的那条是同一件事：浏览器用例不进默认全量，需要时一次一个。
判据：**单独跑通过 + 整批跑失败 + 失败成员每次不同 ⇒ 资源问题，不是回归。**
