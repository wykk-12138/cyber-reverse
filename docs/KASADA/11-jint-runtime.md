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
