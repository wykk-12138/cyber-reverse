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

## 2. 服务通道是 protobuf（[Obs]，本轮从实物解出）

镜像里存着**四段 40 字符的 base64**（池 `0x06f96b1c` / `6bac` / `6c3c` / `6ccc`），
全部以 `bnNl` 开头 —— 解码是 `nse`，即 `...respo` **`nse`** 的尾巴。
它们是一份 **`.proto` 的 `FileDescriptorProto`** 序列化后被定长截断的碎片。

补 padding 解码后按 protobuf wire format 读：

```
0x06f96b1c  12 36 | 0a 11 "evaluation_result" | 18 01 | 20 01 | 28 0b 32 19 ".rpc.dom.Eval"
            → MethodDescriptorProto { name: "evaluation_result", … output_type: ".rpc.dom.Eval…" }

0x06f96bac  12 4d | 0a 11 "CreateArrayBuffer" | 12 1d ".rpc.CreateArrayBuf"
            → MethodDescriptorProto { name: "CreateArrayBuffer", input_type: ".rpc.CreateArrayBuf…" }

0x06f96c3c  42 07 | 0a 05 "stage" | 22 e3 05 |
              0a 0e "ReceiveHeaders" | 12 1a | 0a 06 "target" | 18 01 | 20 01
            → DescriptorProto { field[8] = {name:"stage"},
                                nested_type[4] = {name:"ReceiveHeaders",
                                                  field[2] = {name:"target", …}} }

0x06f96ccc  42 07 | 0a 05 "stage" | 22 e6 01 |
              0a 0b "PaintDialog" | 12 1c | 0a 06 "target" | 18 01 | 20 01 | 28 0b | 32 …
            → DescriptorProto { field[8] = {name:"stage"},
                                nested_type[4] = {name:"PaintDialog", …} }
```

**由此确定的四件事**：

1. **`stage` 是外层消息的一个字段（field 8）** —— 之前是 [Inf]，现在是 [Obs]。
2. **`ReceiveHeaders` 是嵌套消息类型**，它有一个 `target` 字段（field 2）带两个标志位（各 = 1）。
3. **`PaintDialog` 与 `ReceiveHeaders` 是同级嵌套类型** —— 同一个外层消息下并列。
4. **`rpc.dom` 那半边不是 Kasada 的**：`evaluation_result` / `CreateArrayBuffer` / `PaintDialog`
   属于 **`rpc.dom` 包**，是 **DotNetBrowser 自己的渲染进程 RPC**，与 solver 指令无关（见 07 §2.3）。

**⇒ 服务通道的形状**：一个带 `stage` 判别的信封，内嵌 `ReceiveHeaders` / `PaintDialog` 等具体消息。
`stage` 决定载荷是哪一种 —— 这正是 05 状态机里那些阶段切换的线上表示。

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
2. **`KasadaCdSolver` 就是走 `/payload` 的那个**（已由状态文案坐实，见 §2.6）。
3. **[Unk] 已消**：请求形状已在 §2.6 解出。

> **别把两种 host 混了**：`https:///ips.js?&x-kpsdk`（空 host，**店铺**提供脚本）与
> `https://kasada.hypersolutions.co/*`（**服务商**的 solver 端点）是两件完全不同的事。
> 01 §2.1 的"host 是空占位"只对前者成立。

---

## 2.6 协议解出来了：HyperSolutions 是**代理式转发**（[Obs]，本轮）

两条 URL 各自被一个函数构造请求，两个函数大小都是 `0x294`，结构逐行相同，只有两处不同：

| 函数 | 端点 | 状态文案 |
|---|---|---|
| `sub_14111CB10` | `https://kasada.hypersolutions.co/botid` | `Getting BotID` |
| `sub_1411483E0` | `https://kasada.hypersolutions.co/payload` | **`Getting Kasada (1)`** |

**第二个是决定性的**：`Getting Kasada (1)` 在 05 §4 里就是**"走服务商"**那条文案 ——
所以 **`Getting Kasada (1)` 就是在打 `/payload`**，`KasadaCdSolver` 的身份至此确定。
（`(1)`/`(2)` 不是重试序号：`(2)` 是直连店铺端点，见 02 §1.5.3。）

### 2.6.1 请求形状（逐字，从伪代码的字段写入还原）

```http
POST https://kasada.hypersolutions.co/payload
content-encoding: zstd
X-Type:            kasada
X-Upstream-Url:    <店铺自己的 Kasada 端点，例如 https://www.nike.com/<id>/fp?x-kpsdk-v=…>
X-Upstream-Method: <上游方法名>
X-Upstream-Headers: <上游请求头的 JSON>
X-User-Id:         <license / 账号 id>
X-Client-Version:  <客户端版本>
```

| 头 | 证据（String 对象地址） |
|---|---|
| `X-Upstream-Url` | `0x146f2e098` |
| `X-Upstream-Method` | `0x146f2e060` |
| `X-Upstream-Headers` | `0x146f2e020` |
| `X-Type` = `kasada` | `0x146f2dfc0` · 值 `0x1470ae4b8` |
| `X-User-Id` | `0x146f2e0d0` |
| `X-Client-Version` | `0x146f2d8b8` |
| `content-encoding` = `zstd` | `0x146fd6628` · 值 `0x14718f7c8` |
| 方法 `POST` | `0x146e34db8` |
| 响应字段 `StatusInfo` | `0x146e9b830` |

### 2.6.2 响应与状态码

伪代码里注册了三个状态码处理器：

```
200  → 正常路径，读 StatusInfo
401  → 鉴权失败（Key 无效）
403  → 鉴权失败（Key 过期 / 无权限）
```

**[Inf]** `401` 与 `403` 分开注册，说明服务商对"没这个 key"和"key 不能做这件事"给了不同的码 ——
自建同类服务时照抄这个区分，客户端才能给出不同提示（换 key vs 充值）。

### 2.6.3 这套协议的性质：**代理式转发**

`X-Upstream-Url` / `X-Upstream-Method` / `X-Upstream-Headers` 三件套的含义很清楚：
**客户端把"要访问哪个 Kasada 端点、用什么方法、带什么头"打包发给服务商，服务商替它去请求，再把结果压回来。**

这解释了为什么：
- 客户端不需要知道 Kasada 的加密细节（服务商算）；
- 但客户端**必须**知道店铺的 script id 与版本（那是 `X-Upstream-Url` 的一部分）；
- 响应是 `zstd` 压缩（Kasada 的 payload 本身很大，一百多 KB 起）。

**代价**：每次解题都要一次网络往返，且服务商能看到你的所有目标 URL —— 这也解释了为什么它是**旁路**而不是默认路。

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
