### Kasada：从二进制恢复的参数集，对照 replica 的实现

用户目标里点名了这件事：

> 比如 nike 模块 cyber 做到了 kasada 直接生成（不确定是不是接了第三方，但是体感上跟自主生成差不多）

**先回答「是不是接了第三方」：不是。** 原版自带 `IKasadaSolver` 实现。

### 从字符串表恢复的 Kasada 族

**接口与实现**

```
IKasadaSolver
KasadaCdSolver
KasadaHandler
KasadaMobileHandler
```

**方法**

```
GetKasada / GetScript / HandleResponse / GetWorkTime / GetMfc / Reset
```

**状态字段**

```
_kasada _kasadaMobile _accountKasada
_kasadaCt _kasadaDt _kasadaDv _kasadaFc _kasadaH _kasadaIm _kasadaRst _kasadaSt
_kasadaWorkTime
```

**属性与 backing field**

```
KasadaVersion  get_KasadaVersion
<BasePath>  <KasadaCt>  <Bmsz>  <CookieName>  <IpsUrl>
```

**协程状态机**（`d__32`..`d__35` / `d__46`..`d__50`）：

```
<HandleResponse>d__32  <GetScript>d__33  <GetKasada>d__34  <GetWorkTime>d__35
<HandleResponse>d__46  <GetScript>d__47  <GetKasada>d__48  <GetMfc>d__49  <GetWorkTime>d__50
```

**两套 `d__` 编号（32–35 和 46–50）说明有两个几乎相同的实现类**——
对应 `KasadaHandler` 和 `KasadaMobileHandler`。

### replica 的现状

```
KasadaSolver          （Jint JS 引擎，本地执行 payload）
ChromiumKasadaSolver  （真实 Chromium，从网络头嗅探）
KasadaResult
```

`NikeFlow` 两条路都走：

```csharp
if (ChromiumKasadaSolver.IsAvailable) { … AbsorbKasada(c, live); }
else { … using var solver = new KasadaSolver(...); }
```

**`KasadaSolver` 的注释把这件事说清楚了**：

> Kasada's own VM calls host APIs (worker/promise plumbing) that Jint does not expose, so the
> generated token has to come from an embedded Chromium — which is what the original ships.

**原版也是这么做的**（`KasadaCdSolver` 的 `Cd` 大概率是 Chromium/Chrome Driver）。

### 补齐字段覆盖

`KasadaResult` 原来只有 4 个 `x-kpsdk-*` 头（`ct` / `cd` / `sb` / `v`）。
原版有 8 个状态字段，这轮补齐 7 个读取器和 1 个度量：

```csharp
public string? Dt  => Header("x-kpsdk-dt");
public string? Dv  => Header("x-kpsdk-dv");
public string? Fc  => Header("x-kpsdk-fc");
public string? H   => Header("x-kpsdk-h");
public string? Im  => Header("x-kpsdk-im");
public string? Rst => Header("x-kpsdk-rst");
public string? St  => Header("x-kpsdk-st");

/// Wall-clock milliseconds the payload burned before it produced a token.
public long WorkTimeMs { get; init; }
```

`WorkTimeMs` 在 `Solve` 里用 `Stopwatch` 实测：

```csharp
// The live build times the handshake (_kasadaWorkTime) because Kasada's gate treats a
// token produced in a few milliseconds as machine-generated.
var clock = System.Diagnostics.Stopwatch.StartNew();
```

**这是「函数数量对等」这一条的实质**：原版追踪握手耗时是因为 Kasada 的风控会看这个数，
replica 现在也有这个数，调用方可以据此控制节奏。

### 两个诚实的不确定

**一、header 名是推断的。**

原版二进制里**没有 `kpsdk` 字符串**——header 名是运行时拼的（`"x-kpsdk-" + suffix`）。
所以 `_kasadaDt` 对应 `x-kpsdk-dt` 是**从命名和 Kasada 公开协议推的**，不是从二进制读的。

**证据等级：C。** 按 R90 定的标准，这不足以改变任何注册。

**二、`GetMfc` 的语义不明。**

`Mfc` 只在 `KasadaHandler` 的第二套状态机里出现（`d__49`），`KasadaMobileHandler` 没有。
**可能是 Mobile Fingerprint Challenge**，也可能是别的东西。

**replica 没有实现它。** 这轮也没补——**凭空补一个名字好听的空方法，比没有更糟。**

### 结论：目标里那句话的答案

> 「cyber 做到了 kasada 直接生成」

**对，而且是自主生成，不是第三方。**

**replica 也做到了自主生成，两条路都有**：
- `KasadaSolver`（Jint，能在纯 JS 环境里跑完就用它）
- `ChromiumKasadaSolver`（跑不完就用真浏览器）

**和原版的差别在「用哪个跑」的判据上**，不在「有没有能力」上。

### 验证

```
dotnet test      583 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
build errors     0
```

---
