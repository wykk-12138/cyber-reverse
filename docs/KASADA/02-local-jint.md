# 02 · 方案一：Jint 本地执行 `ips.js`（Nike 走的就是这条）

> **一句话**：把店铺的 `ips.js` 抓下来，在**纯托管 JS 解释器**里配一套浏览器 shim 跑一遍，拿走它自己产出的 `x-kpsdk-*`。
> 不起浏览器、不联网解题、没有第二次往返 —— 这就是"体感跟自主生成一样"的原因：它**就是**自主生成。

---

## 1. 为什么确定原版用的是这条路（[Obs]）

| 证据 | 地址 | 说明 |
|---|---|---|
| `Jint, Version=4.17.0.0, Culture=neutral, PublicKey=00240000048000…` | `0x146dd37ac` | 程序集全名，版本坐实 |
| `Sebastien Ros@Javascript interpreter for .NET.` | `0x14316ea8d` | Jint 的 NuGet 包描述 |
| `A standard-compliant JavaScript parser, which is a fork of Esprima.NET combined with the .NET port of the acorn…` | `0x14315d5ef` | **Acornima**，Jint 4.x 的解析器 |
| `Jint.EnableHostContractVerification` | `0x146dd3aac` | **NativeAOT 专用开关** → Jint 是被 AOT 编进产物的，不是外挂 dll |
| `Jint.Native.Intl.Data.LikelySubtags.txt` | `0x146dd3b0c` | Intl 数据被嵌进产物 |
| `JintBlockStatement` / `JintStatement\`1` / `JintDoWhileStatement` / `JintClassDeclarationStatement` / `JintContinueStatement` / `JintDebuggerStatement` … | `0x1434cb5dd` 一带 | 完整的语句类族（不是零星引用） |
| `DoChallenge.GenerateJavascriptToken` | `0x14345d611` | **原版自己的方法名**：在 `DoChallenge` 里"生成 JS token" |
| `<<GenerateJavascriptToken>d__47` | `0x14345cee0` | 同名 async 状态机 |
| `KPSDK.scriptStart` | `0x146dd9774` | 直接引用 kpsdk 脚本的**内部全局符号** → 只有在自己宿主里跑它才需要 |

对照组（同一批查询下 **0 命中**，`saturated=false`）：
`ClearScript` · `Microsoft.ClearScript` · `V8Engine` · `WebView2` · `Puppeteer` · `chromedriver` · `NiL.JS`。

> `Jurassic` / `Chakra` 的命中是假阳性：前者是店名 `jurassic-cards-tcg`，后者是字体 `Chakra Petch`。

**结论**：Nike 的 Kasada 凭据由**进程内 Jint 解释器**产出。DotNetBrowser 4.3.5 也在产物里（[Obs]，见 03），
但那是**并存的第二条路**，不是 Nike 的常规路径。

---

## 1.5 原版自己的流程骨架（[Obs]，本轮从伪代码读出）

这不是推理了 —— 是 `sub_1408F28B0`（一个 async 状态机）的伪代码顺序：

```c
// ① 响应头里已经带了 ct？
if (hasHeaders(resp, &off_1471881C8 /* x-kpsdk-ct */))
    rec[11] = readHeader(resp, &off_1471881C8);        // 有就直接用
else
{
    // ② 没有 —— 从页面 HTML 里把脚本找出来
    doc  = this.field16.field16;                        // 已拿到的文档
    sel  = get(doc,  &off_147153CA8);                   //  'script[src*='ips.js']'
    src  = get(sel,  &off_1471620F8);                   //  'src'
    ua   = get(request, &off_1471795D0);                //  'user-agent'
    // ③ 带着 UA 去算（异步，结果回填 rec）
    awaiter = sub_1408EFAB0(rec, /*a2*/ 0, ua, 0, 1);
}
```

三个字符串全部解出（对象头即 `off_XXX` 本身）：

| 操作数 | 字符串 |
|---|---|
| `off_147153CA8` | **`script[src*='ips.js']`** |
| `off_1471620F8` | `src` |
| `off_1471795D0` | **`user-agent`** |
| `off_14710E630` | `payload` |
| `off_146DDA8A8` | `Kasada`（显示名；小写 `kasada` 是另一个常量） |

**两条由此升级的证据**：

1. **01 §2.3 的「从 HTML 里找脚本」从 [Inf] 升成 [Obs]** —— 原版用的就是这个 CSS 选择器，
   连选择器形态都抄到了（`script[src*='ips.js']`，子串匹配，不要求精确路径）。
2. **`user-agent` 是算 token 的输入之一** —— 01 §3.1 里"token 与 UA 绑定"从 [Inf] 升成 [Obs]。
   移植时这条不能省：换 UA 而不重算，等于告诉 Kasada 这是一次不可能的组合。

### 1.5.1 `Reset` 与记录槽位（[Obs]）

`sub_1408EF930` 就是 `Reset`：注册一个新对象，然后清空六个槽位 ——

```c
a1[7]  = 0;   a1[11] = 0;   // 11 = x-kpsdk-ct
a1[13] = 0;   a1[14] = 0;
a1[15] = 0;   a1[16] = 0;   // 15 = x-kpsdk-h, 16 = x-kpsdk-cd
```

**槽位表**（与 08 §9.1 的设头函数一致）：

| 槽位 | 头 |
|---|---|
| `rec[7]` | （未定） |
| `rec[11]` | `x-kpsdk-ct` |
| `rec[13]` / `rec[14]` | （未定） |
| `rec[15]` | `x-kpsdk-h` |
| `rec[16]` | **`x-kpsdk-cd`** |

`Reset` 一次清掉全部 —— 说明这六个是"一次握手的整体"，不能部分复用。

### 1.5.2 算出之后：带**全套 Chrome 头**去打店铺自己的端点（[Obs]）

`sub_1408EFC50` 是这一步的构造器，它的状态文案是 **`Getting Kasada (2)`** —— 注意是 `(2)`，不是 `(1)`。
全部操作数由 `analysis/names_at.py` 解出：

```http
POST/GET <店铺的 Kasada 端点>
x-kpsdk-ct:  <rec[11]>            x-kpsdk-dt: <rec[9]>
x-kpsdk-im:  <rec[10]>            x-kpsdk-v:  <EF620(rec)>
user-agent:  <与被算 token 时同一份>

content-length:    0
sec-ch-ua:         <动态>
sec-ch-ua-platform:<动态>
sec-ch-ua-mobile:  ?0
accept:            */*
accept-encoding:   gzip, deflate, br, zstd
accept-language:   <动态>
origin:            <动态>
referer:           <动态>
sec-fetch-site:    same-origin
sec-fetch-mode:    cors
sec-fetch-dest:    empty
priority:          u=1, i
cookie:            <会话 cookie 罐>
```

**这条头集是"整份 Chrome 伪装"**，不是只补 Kasada 的那几个头：

| 细节 | 为什么重要 |
|---|---|
| `sec-ch-ua` / `-platform` / `-mobile` | Client Hints，现代 Chrome 必带；缺了就是"不是浏览器" |
| `sec-fetch-site/mode/dest` | Fetch Metadata 三件套，Chrome 会自动加，脚本客户端常忘 |
| `priority: u=1, i` | Chrome 2023+ 的取回优先级格式，细节到位 |
| `accept-encoding: gzip, deflate, br, zstd` | **含 `zstd`** —— 与 `content-encoding: zstd` 的依赖一致 |
| `origin` + `referer` 同时带 | 跨源 POST 的真实形状 |

**⇒ 这一步是"拿到头之后怎么用"的完整答案**：把这几个 `x-kpsdk-*` 塞进一次**看起来完全像 Chrome** 的请求里，
打店铺自己的 Kasada 端点，拿回下一次的挑战响应。**头算对了但请求不像浏览器，一样过不去。**

### 1.5.3 `Getting Kasada (1)` 与 `(2)` 是两条不同的路（[Obs]）

| 文案 | 构造器 | 打向哪里 | 带什么 |
|---|---|---|---|
| `Getting Kasada (1)` | `sub_1411483E0` | `https://kasada.hypersolutions.co/payload` | `X-Type: kasada` + `X-Upstream-*`（04 §2.6） |
| `Getting Kasada (2)` | `sub_1408EFC50` | **店铺自己的 Kasada 端点** | `x-kpsdk-ct/dt/im/v` + 全套 Chrome 头（本节） |

**这两条不是重试关系**（`(1)` 与 `(2)` 不是"第一次失败再来一次"），
而是一个走服务商、一个直连店铺。原版把两个完全不同的对象都编成了 `Getting Kasada (n)`，
所以**光看状态文案分不出走的是哪条路** —— 这也是为什么 04 §3 那张"动词表"要配这张表一起看。

---

## 2. 为什么这条路能撑 100 个任务并发

| | Jint | Chromium（DotNetBrowser / CDP） |
|---|---|---|
| 执行方式 | 托管解释执行，无 JIT | 独立进程 + 渲染管线 |
| 单实例内存 | 一个 `EvaluationContext`（脚本 AST + 解释器状态） | 一个浏览器实例，量级差 2~3 个数量级 |
| 启动开销 | 微秒级 | 数百毫秒起 |
| 100 并发 | 100 份解释器状态 | 100 个浏览器进程（通常不可接受） |

**代价**：Jint 只实现 ECMAScript 语言本身，**没有 DOM/BOM**。缺的宿主 API 必须自己补 —— 这就是 shim 的作用，
也是这条路唯一真正的工程量所在。

---

## 3. 需要的 shim（按优先级）

这份清单不是猜的：它来自**在真浏览器里实际问出来的缺口**（`replica/docs/HISTORY.md` §6.79 记录了实测结果）：

```json
{"worker":"function","subtle":"object","getRandomValues":"function",
 "performanceNow":"function","bindOnFunction":"function",
 "promiseResolve":"function","requestAnimationFrame":"function"}
```

按 Kasada 脚本的依赖顺序，shim 至少要覆盖：

| 组 | 内容 | 缺了会怎样 |
|---|---|---|
| 定时与调度 | `setTimeout/setInterval/queueMicrotask/requestAnimationFrame` | 脚本永远不"就绪" |
| 加密 | `crypto.getRandomValues`、`crypto.subtle.digest`（**SHA-256 起**） | 摘要算不出来，握手停在中途 |
| 语言补丁 | `Function.prototype.bind`、`Promise`（含 `resolve/all`）、`Symbol` | 死在字节码解释器里（见 §5 的 91.8%） |
| 环境 | `navigator{userAgent,language,platform,hardwareConcurrency,deviceMemory}`、`screen{width,height,colorDepth}`、`location`（**必须 https/localhost**）、`document{cookie,createElement,addEventListener}` | 指纹全零，或直接抛错 |
| 存储 | `localStorage` / `sessionStorage`（可用内存字典） | 脚本读不到上一轮状态 |
| 网络 | `XMLHttpRequest`（至少 `open/send/setRequestHeader`） | 脚本无法上报，ct 不回流 |
| 图形 | `HTMLCanvasElement.getContext('2d')`（`getImageData`/`toDataURL`/`measureText`） | canvas 指纹段失败 |
| Worker | `Worker`（可先退化为"同步执行"） | 部分构型的脚本卡住 |

> **安全上下文这条很坑**：`crypto.subtle` 只在 https / localhost 下存在。用 `about:blank` 或 `data:` 起手，
> shim 里 `subtle` 是 `undefined`，Kasada 立刻失败。这条在浏览器里实测过，同样适用于 Jint 的 shim（`location.protocol` 要报 `https:`）。

---

## 4. 可跑骨架（C# + Jint 4.x）

```csharp
using Jint;
using Jint.Native;
using Jint.Native.Object;
using System.Security.Cryptography;
using System.Text;

/// <summary>在纯托管引擎里跑一份 ips.js，取回它自己产出的 x-kpsdk-*。</summary>
public sealed class KasadaJsRuntime : IDisposable
{
    private readonly Engine _engine;
    private readonly Dictionary<string, string> _cookieJar = new(StringComparer.OrdinalIgnoreCase);

    public KasadaJsRuntime(string userAgent, string pageUrl)
    {
        _engine = new Engine(o => o
            .Strict(false)                                  // Kasada 的产物代码不是严格模式写的
            .TimeoutInterval(TimeSpan.FromSeconds(20))       // 单次执行上限，防死循环
            .LimitRecursion(512)
            .MaxStatements(2_000_000));

        InstallEnvironment(userAgent, pageUrl);
    }

    private void InstallEnvironment(string ua, string url)
    {
        var uri = new Uri(url);
        var e = _engine;

        // ── window 自身 ──
        e.SetValue("window", e.Global);
        e.SetValue("self", e.Global);
        e.SetValue("top", e.Global);
        e.SetValue("globalThis", e.Global);

        // ── navigator ──
        var nav = new JsObject(e);
        nav.Set("userAgent", ua);
        nav.Set("appVersion", ua.Replace("Mozilla/", ""));
        nav.Set("language", "en-US");
        nav.Set("languages", e.Evaluate("['en-US','en']"));
        nav.Set("platform", "Win32");
        nav.Set("hardwareConcurrency", 8);
        nav.Set("deviceMemory", 8);
        nav.Set("webdriver", JsValue.False);   // 见 03 §5：这个字段的取值要跟真浏览器一致
        e.SetValue("navigator", nav);

        // ── screen / location ──
        var screen = new JsObject(e);
        screen.Set("width", 1920); screen.Set("height", 1080);
        screen.Set("availWidth", 1920); screen.Set("availHeight", 1040);
        screen.Set("colorDepth", 24); screen.Set("pixelDepth", 24);
        e.SetValue("screen", screen);

        var loc = new JsObject(e);
        loc.Set("href", url);
        loc.Set("origin", uri.GetLeftPart(UriPartial.Authority));
        loc.Set("host", uri.Host);
        loc.Set("protocol", uri.Scheme + ":");   // 必须 https: / http:，否则 subtle 不该存在
        e.SetValue("location", loc);

        // ── crypto：subtle 只在安全上下文暴露 ──
        var crypto = new JsObject(e);
        crypto.Set("getRandomValues", new ClrFunction(e, "getRandomValues", (_, args) =>
        {
            var arr = args.At(0).AsObject();
            var len = (int)arr.Get("length").AsNumber();
            var buf = RandomNumberGenerator.GetBytes(len);
            for (var i = 0; i < len; i++) arr.Set(i, buf[i]);
            return arr;
        }));
        var secure = uri.Scheme is "https" || uri.Host is "localhost" or "127.0.0.1";
        if (secure)
        {
            crypto.Set("subtle", BuildSubtle(e));      // digest 用 .NET 的 SHA-*，按算法名分派
        }
        e.SetValue("crypto", crypto);

        // ── 定时器：同步退化，但必须存在 ──
        e.SetValue("setTimeout", new ClrFunction(e, "setTimeout", (_, a) => { a.At(0).AsObject().Call(); return JsValue.Undefined; }));
        e.SetValue("setInterval", new ClrFunction(e, "setInterval", (_, a) => { a.At(0).AsObject().Call(); return JsValue.Undefined; }));
        e.SetValue("clearTimeout", new ClrFunction(e, "clearTimeout", (_, _) => JsValue.Undefined));
        e.SetValue("requestAnimationFrame", new ClrFunction(e, "requestAnimationFrame", (_, a) => { a.At(0).AsObject().Call(JsValue.Zero); return JsValue.One; }));

        // ── storage：内存字典即可 ──
        e.SetValue("localStorage", BuildStorage(e));
        e.SetValue("sessionStorage", BuildStorage(e));

        // ── document：cookie 必须接到真实 jar 上 ──
        var doc = new JsObject(e);
        doc.Set("cookie", new ClrFunction(e, "get_cookie", (_, _) => new JsValue(string.Join("; ", _cookieJar.Select(kv => $"{kv.Key}={kv.Value}")))));
        doc.Set("addEventListener", new ClrFunction(e, "document.addEventListener", (_, _) => JsValue.Undefined));
        doc.Set("createElement", new ClrFunction(e, "document.createElement", (_, a) => BuildElement(e, a.At(0).ToString())));
        e.SetValue("document", doc);
    }

    /// <summary>脚本正文是 UTF-8；页面给的往往是 `?x-kpsdk-v=` 带参的 URL。</summary>
    public void Load(string scriptSource) => _engine.Execute(scriptSource);

    /// <summary>按优先级探出口；现代构型常常只有 configure/isReady，那就退到嗅探（见 03）。</summary>
    public string? TryReadClientToken()
    {
        foreach (var expr in new[]
                 {
                     "window.KPSDK && window.KPSDK.ct && window.KPSDK.ct()",
                     "window.KPSDK && window.KPSDK.ct",
                     "window.KPSDK && window.KPSDK.state && window.KPSDK.state.ct",
                     "(function(){var m=document.cookie.match(/(?:^|;\\s*)kpsdk-ct=([^;]+)/);return m?m[1]:null;})()",
                 })
        {
            try
            {
                var v = _engine.Evaluate(expr);
                if (v.Type == Jint.Runtime.Types.String && !string.IsNullOrEmpty(v.AsString())) return v.AsString();
            }
            catch { /* 探测失败是预期的，不是错误 */ }
        }
        return null;
    }

    /// <summary>脚本把 x-kpsdk-* 写进 cookie 或全局时才用得上；纯线上嗅探的方案见 03。</summary>
    public IReadOnlyDictionary<string, string> ReadKasadaHeaders()
    {
        var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        var dump = _engine.Evaluate(
            "(function(){var o={};if(window.KPSDK&&window.KPSDK.headers){" +
            "for(var k in window.KPSDK.headers){if(/^x-kpsdk-/.test(k))o[k]=window.KPSDK.headers[k];}}return JSON.stringify(o);})()");
        // … 按项目里的 JSON 库解析 dump 即可，这里从略
        return headers;
    }

    public void Dispose() { /* Jint 的 Engine 无需显式释放；保留以便包一层池化 */ }
}
```

`BuildSubtle` / `BuildStorage` / `BuildElement` 三个方法按上面表格补齐即可 —— **它们都是"能跑就行"的桩，
不需要做到浏览器级保真**，因为 Kasada 只用它们取熵与取值。

---

## 5. 四个已知的坑（都是真踩过的）

### 5.1 只在 Jint 里跑到 91.8% 就死

一次实测（Nike 的 `ips.js`，157,563 字节）：

```
stopped at offset 144669 (91.8% of 157563)
Cannot read properties of undefined (reading 'bind')   @ line 1, col 144669
```

bootstrap、字符串表、解码器都过了，死在 Kasada **自制的字节码解释器**里。
**这是宿主 API 缺口，不是解析失败** —— 缺的正是 `Function.prototype.bind` / `worker` / `subtle` 这一类。
→ 修法是把 §3 的清单补齐，而不是换成浏览器。

### 5.2 现代构型的 `KPSDK` 不再导出 token

对 Nike 的现行构型实测：`KPSDK` 只暴露 `configure` 与 `isReady`，`ct()` / `sb()` / `cd()` 全都不存在。
→ 此时**不要**去猜导出名（那是把"猜"当"取证"）。正确做法是**嗅网络**：脚本算出的 token 总会挂在下一个请求的头上（03 §3）。

### 5.3 解析失败与执行失败必须分开

```csharp
// 两段式：PrepareScript（解析）→ Evaluate（执行）
// 前者失败 = payload 损坏（换一份脚本）；后者失败 = 缺宿主 API（补 shim 或换路）
```
一条合并的 try/catch 会把这两类混成"跑不通"，然后你就会错误地得出"必须用浏览器"的结论 —— 我们犯过这个错。

### 5.4 `NeedsRealBrowser` 要按异常类型判，不要按文案判

Jint 的措辞随版本变；按消息文本匹配会在升级时静默失效。

---

## 6. 什么时候必须换方案二

| 症状 | 处置 |
|---|---|
| shim 补齐后仍死在字节码解释器里，且缺口在 WebGL / Worker / WebRTC 这类**无法托管模拟**的 API | 换 03 |
| 站点把 Kasada 与 TLS 指纹、HTTP/2 帧序绑在一起，且要求 `cd` 加密 body | 换 03（同一份脚本上下文才配得出 cd） |
| 只是"探不到导出名" | **不要换** —— 用 03 §3 的嗅探法补 |

---

## 7. 复算

```powershell
python analysis\ida.py str Jint        --limit 100   # total >= 81，含 Version=4.17.0.0
python analysis\ida.py str Acornima    --limit 20
python analysis\ida.py str DoChallenge --limit 20    # total = 4，含 GenerateJavascriptToken
python analysis\ida.py str JintBlockStatement --limit 5
```
