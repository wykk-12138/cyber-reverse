# 04 · 方案三/四：远端 solver 通道与降级（Fallback / MFC）

> 这份讲"不自己算"的几种兜底。**先明确一件事：Nike 的常规路径不是这里**（那是 02）。
> 这条是原版留的旁路：自己有服务端资源时用它更快，或者主路失败时降级。

---

## 1. 接口形状（[Obs]）

| 类型 | 地址 | 说明 |
|---|---|---|
| `IKasadaSolver` | `0x1433216f6` | **一个接口** —— 所以 solver 是可插拔的，这是"四种解法"能并存的原因 |
| `KasadaSolveRequest` | `0x1433218dc` | 请求契约 |
| `KasadaSolveResult` | `0x143321733` | 响应契约 |
| `KasadaCdSolver` | `0x143321dfa` | 名字里的 **Cd** = 与 `x-kpsdk-cd` 相关（[Inf]） |

**[Inf]** 有 `Request`/`Result` 这一对 + 一个接口，说明原版把 solver 抽成了服务调用边界；
`KasadaCdSolver` 是其中一个实现，专门处理需要 cd 的场景。

---

## 2. 服务通道是 protobuf（[Obs]）

字段表（`0x034590` 一带连续命中，逐字）：

```
_Wire            _SolverInstruction   _SolverAdvance     _SolverBody
_SolverEcho      _SolverEchoInstruction  _SolverEchoReport  _SolverError
_SolverFetchResult  _SolverHeader    _SolverLink        _SolverOutcome
_SolverPageTiming   _SolverPrefetched _SolverReply       _SolverStart
_SolverTiming    _NullableSolverTiming  _SolverWant
_ListSolverEcho  _ListSolverFetchResult _ListSolverInstruction
SolverInstructionSerializeHandler   Create_ListSolverInstruction
```

`List*` 前缀 + `SerializeHandler` = **protobuf 的 repeated message + 序列化器**，不是手写 JSON。

池里还有一条**已编码的 protobuf 样本**：

```
0x06f96c3c  bnNlQgcKBXN0YWdlIuMFCg5SZWNlaXZlSGVhZGVycxIaCgZ0YXJnZXQYASAB
```

Base64 解出来头部是：

```
"nse"  0x07  "\n\x05stage"  "\"\xe5\x05"  "\n\x0eReceiveHeaders"  "\x12\x1a"  "\n\x06target"  "\x18\x01 \x01"
```

可读出的字段名：**`stage`**、**`ReceiveHeaders`**、**`target`**。

**[Inf] 由此推出的交互模型**：

```
客户端 → 服务端：  SolverInstruction { stage, target, headers… }
服务端 → 客户端：  SolverEcho / SolverReply / SolverFetchResult（分阶段回填）
```

即 **"分阶段"的远程求解**：服务端会问你"现在到哪一步了"（`stage`）、要哪些头（`ReceiveHeaders`），
你再把 `target`（要解的 URL）与 `headers` 发过去。这是个能**多轮**走的通道，不是一次性买卖。

`_SolverPageTiming` / `SolverTiming` / `SolverStart` 的存在说明：**服务端也关心时序**，与 01 §6 的 `workTime` 同源。

---

## 2.5 原版接的真实服务：**HyperSolutions**（[Obs]，本轮新挖）

之前这一节写的是"如果你要自建远端 solver"，那是我从字段表推的**通用契约**。
实际情况是：**原版接的是一家现成服务 —— HyperSolutions**，同一家给三个厂商提供端点。

```
0x143321c61   (HyperSolutionsSolver                      ← 类型（str total = 1）

0x14706ebfc   https://kasada.hypersolutions.co/botid     ← Kasada
0x14706ec64   https://kasada.hypersolutions.co/payload
0x1470ae4ec   kasadaRequest                              ← 请求字段名（total = 1）

0x1470517f4   https://akm.hypersolutions.co/pixel        ← Akamai（划边界用）
0x147051854   https://akm.hypersolutions.co/sbsd
0x1470518b4   https://akm.hypersolutions.co/v2/sensor
0x14708ac54   https://trustdecision.hypersolutions.co/decode   ← TrustDecision
0x14708accc   https://trustdecision.hypersolutions.co/payload
0x14708ad44   https://trustdecision.hypersolutions.co/sign
```

**三条推论**：

1. **`Kasada API down (Contact staff)` 里的 "API" 就是这两个端点** ——
   "Contact staff" 是给运营看的：服务挂了得找服务商，客户端无解。这解释了为什么它是 `Contact staff` 而不是"重试"。
2. **`KasadaCdSolver` 大概率就是"走 `/payload` 的那个"**（[Inf]）—— 名字里的 cd 对应 `x-kpsdk-cd`，
   而 `/payload` 正是收 payload 的端点。`/botid` 应该对应 `ct`/身份侧。
3 **[Unk] 请求体形状没有** —— 只有 URL 与字段名 `kasadaRequest`，没有 body 结构。
   要拿到得反编译 `HyperSolutionsSolver` 的调用点。

> **别把两种 host 混了**：`https:///ips.js?&x-kpsdk`（空 host，**店铺**提供脚本）与
> `https://kasada.hypersolutions.co/*`（**服务商**的 solver 端点）是两件完全不同的事。
> 01 §2.1 的"host 是空占位"只对前者成立。

---

## 3. 四种模式与它们的动词（[Obs] + [Inf]）

`KasadaStrategy` 的四模式，动词是原版文案自带的：

| 模式 | 动词 | 触发 | 状态串（[Obs]，见 05） |
|---|---|---|---|
| `Api` | **getting**（去要） | 配置了远端 | `Getting Kasada (1)` / `(2)` / `(MFC)` |
| `Local` | **solving**（自己算） | 默认 | `Failed solving Kasada` / `(TL)` |
| `Fallback` | falling back | 前两条失败 | `Kasada-Fallback` |
| `MobileFallback` | falling back | 需要移动端构型 | `Kasada-Mobile-Fallback` |

**`getting` 与 `solving` 是两个不同的动词** —— 这个区分原版写进了文案里，是判断"走哪条路"的第一手依据：
看到 `Getting Kasada` 说明在用服务，看到 `Failed solving Kasada` 说明在本机算。

---

## 4. MFC：移动端降级（[Obs]）

| 证据 | 地址 |
|---|---|
| `GetMfc`（async `d__49`） | `0x14345a681` |
| `get_MfcEnabled` / `set_MfcEnabled` | `0x03459a02` |
| `get_IsMobile` / `set_IsMobile` | `0x034599e8` |
| `get_VersionProvider` / `set_VersionProvider` | `0x03459a11` |
| 状态串 `Getting Kasada (MFC)` | `0x146da1804` |

**三个可开关的字段**（`MfcEnabled` / `IsMobile` / `VersionProvider`）⇒
MFC 是**可配置的移动构型通道**，并且版本号由 `VersionProvider` 注入 —— 说明移动端的 Kasada 版本与桌面不一致。

**[Unk]** `MFC` 的展开（Mobile Flow Challenge？Mobile Fingerprint Challenge？）没有证据。
可以确定的只有：它是 Api 路径上的一个**变体**（`Getting Kasada (MFC)` 属于 getting 家族），
并且**只有 `d__46`–`d__50` 那一套 handler 有 `GetMfc`**（`d__32`–`d__35` 那套没有，见 05）。

---

## 5. 降级链（[Inf]，照 02/03 的实测顺序排）

```
1. Local/Jint        ← 默认。快、省内存、无外部依赖
   ↓ 失败（shim 补不齐 / 需要 cd / 探不到导出）
2. Local/Browser     ← 同一进程内 Chromium，天然同上下文（03）
   ↓ 失败（站点 403 headless / 无浏览器可用）
3. Api（KasadaCdSolver）  ← 有服务端时
   ↓ 失败（服务不可达）
4. Fallback / MobileFallback(MFC)
   ↓ 全部失败
   → 报 "Failed Kasada (Retry limit reached)"，换代理重来
```

**注意第 3 条的文案**：服务不可达时报 `Kasada API down (Contact staff)`（`0x06dd94dc`），
`Contact staff` 是给运营看的 —— 它说明**这条路依赖你控制之外的东西**，所以不该是默认路。

---

## 6. 如果你要自建远端 solver

看完 §2 的字段表，自建的最小可行契约是：

```
POST /solve
  { "stage": "<上一轮服务端给的状态>", "target": "<要解的 URL>",
    "headers": { "<需要回填的头名>": "…" }, "wire": "<传输类型>",
    "pageTiming": { "start": ts, "timing": ms } }

200 OK
  { "reply": "<本轮要客户端做的事>", "want": ["x-kpsdk-ct"],
    "outcome": "advance|done|error", "error": "…" }
```

三条设计要点（都是 02/03 里验证过的约束）：

1. **必须多轮**（`stage` / `advance`）——一次性接口在 Kasada 上不够，握手本身就是多阶段。
2. **时序要透传**（`pageTiming` / `workTime`）——服务端造出来的 token 如果时序荒谬，站点一样拒。
3. **UA 与 token 绑死** —— solver 返回的 token 只能用于它自己那套 UA/指纹，换个会话就废。

---

## 7. 复算

```powershell
python analysis\ida.py str IKasadaSolver     --limit 5
python analysis\ida.py str KasadaSolve       --limit 10
python analysis\ida.py str SolverInstruction --limit 10
python analysis\ida.py str MfcEnabled        --limit 5
python analysis\ida.py str ListSolver        --limit 10
```
