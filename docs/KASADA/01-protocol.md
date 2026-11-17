# 01 · Kasada 协议规格

> 目标：读完这份就能在任何语言里自己实现 Kasada 客户端凭据生成，不必知道 Cybersole 的存在。
> 分级：**[Obs]** 二进制里读到的字面量（附地址）· **[Inf]** 由 Obs + 公开协议推出的行为 · **[Unk]** 未定。

---

## 1. 它是什么

Kasada 是一层**客户端完整性校验**，不是验证码，没有图可识。站点做三件事：

1. 页面里加载一份店铺自己的脚本（`ips.js`，或按脚本 id 的路径）；
2. 脚本在客户端跑，产出一组 `x-kpsdk-*` 请求头（核心是 `x-kpsdk-ct`，即 client token）；
3. 业务请求带上这些头，服务端验签；不合法就回 429/403 或软失败。

**推论（决定了整份文档的形状）**：解 Kasada 只有两条正路 —— 自己跑那份脚本，或借一个真浏览器跑那份脚本。所谓"打码服务"在 Kasada 上做的是前者：它替你跑脚本，把 token 卖给你。

---

## 2. 脚本 id 与端点

**[Obs]** 脚本 id 是**每个站点一组**的双 UUID，Cybersole 把 Nike 那一组硬编码在二进制里：

```
script id = /149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3
```

**别把这串当通用值** —— 换一个店铺就要换一组。恢复办法见 §2.3。

### 2.1 端点表（全部 [Obs]，列的是**池偏移**；换算规则见 06 §2）

| 路径 | 池偏移 | 作用 |
|---|---|---|
| `<id>` | `0x06aabf24` | 脚本 id 本身 |
| `<id>/` | `0x06aabfd4` | 带尾斜杠，作前缀用 |
| `<id>/ips.js?` | `0x06aac20c` | **主脚本** |
| `<id>/fp?x-kpsdk-v=` | `0x06aac144` | **指纹端点**（POST，带版本查询参数） |
| `<id>/a-4-a/c.js` | `0x06aac084` | 诱饵脚本：页面会加载，答案被丢弃 |
| `/ips.js?` | `0x06ab464c` | 主脚本的**裸形式**（id 走 cookie/参数时用） |
| `/fp?x-kpsdk-v=` | `0x06ab3db4` | 指纹端点的裸形式 |
| `/prop.json` | `0x06ab5ccc` | **配置文档** |
| `/prop.json?_=` | `0x06ab5cfc` | 同上，带 cache-buster |

**[Obs]** host 在二进制里是**空占位**：`https:///ips.js?&x-kpsdk`（`0x05e9fab0`）。
也就是说**站点域名由运行时提供**，镜像里没有可抄的 host —— 这也解释了为什么"远端 API 方案"在原版里没有现成的 host 可复用。

### 2.2 一次握手的时序（[Inf]，由端点表与头部集合推出）

```
1. GET  https://<store>/<id>/ips.js?x-kpsdk-v=<ver>     → 脚本正文（几十~一百多 KB）
2. GET  https://<store>/<id>/prop.json?_=<ts>          → 配置（可选，脚本自己会要）
3. 本地执行脚本，产出 x-kpsdk-cd / ct / …              → 见 02 或 03
4. POST https://<store>/<id>/fp?x-kpsdk-v=<ver>        → 指纹上报（body 含 sensor payload）
5. 业务请求带 9 个 x-kpsdk-* 头                        → 服务端验签
```

第 4 步的响应头会回填 `x-kpsdk-ct`；脚本内部的 `KPSDK.ct()` 不一定存在（见 02 的实测坑）。

### 2.3 换站点时怎么恢复 script id

**[Inf]** 从店铺首页 HTML 里找脚本标签：

```
<script src="https://<store>/<uuid-a>/<uuid-b>/ips.js?x-kpsdk-v=…">
```

**[Obs 佐证]** 二进制里有一条选择器形态的字面量 `script[src*='ips.js']`（`0x071528b4` 一带），说明原版也是这么找的。

---

## 3. 九个请求头（[Obs]，逐字）

池里九条连续命中（`str kpsdk` 的返回里全部可见）：

```
x-kpsdk-cd   x-kpsdk-ct   x-kpsdk-dt   x-kpsdk-dv   x-kpsdk-fc
x-kpsdk-h    x-kpsdk-im   x-kpsdk-st   x-kpsdk-v
```

**不是每个站点都用九个。** 原版把它们做成 9 个字段（`_kasadaCt/Dt/Dv/Fc/H/Im/Rst/St` + `_kasadaWorkTime`，见 05），
说明这些值是**逐握手缓存**的，而非每次现算。

### 3.1 每个头大致是什么（[Inf]，按 Kasada 公开行为）

| 头 | 含义 | 备注 |
|---|---|---|
| `x-kpsdk-ct` | client token，**核心凭据** | 必须与产出它的 UA 一致 |
| `x-kpsdk-cd` | client data，用于**请求体加密** | 同一份脚本上下文才能配 `cd` 加密 body |
| `x-kpsdk-v` | 脚本版本 | 见 §5 的 per-store 版本头 |
| `x-kpsdk-st` / `-rst` | 握手时间戳 / 接收时间戳 | 与 `workTime` 一起构成时序证据 |
| `x-kpsdk-dt` `-dv` `-fc` `-h` `-im` | 脚本内部状态的投影 | 语义 **[Unk]**，跟随脚本产出即可，不要自造 |

> **易错点**：token 与 UA 绑定。把 token 塞进一个 UA 不同的会话，Kasada 看到的是一次不可能的组合。
> Cybersole 为此专门做了"UA 跟着 token 走"（`FlowContext.KasadaUserAgent`，`replica/.../FlowContext.cs`），移植时照做。

---

## 4. Cookie 族

**[Obs]** 一条竖线分隔的候选清单，在池里出现三次（后两次是变体）：

```
0x06dd83d4   KP_UIDz|ak_bmsc|__cf__client__uuid
0x06dd8434   KP_UIDz|ak_bmsc|__cf__client__uuid_      （末尾多下划线：截断/拼接）
0x06dd8494   KP_UIDz|akm?_bmsc|__cf__client__uuid|mrk_atkr
```

拆开看：`KP_UIDz` = **Kasada 的设备标识 cookie**；`ak_bmsc` / `mrk_atkr` = Akamai；`__cf__client__uuid` = Cloudflare。
**这条清单是三家的合表**，不是 Kasada 专用（边界见 07）。

另外 Kasada 前缀的 cookie 族是 `kpsdk-*`（`kpsdk-ct` 等）。**[Obs]** 原版 `AntiBotProtocol` 里 Kasada 家族记的是 `kpsdk`。

**[Inf] 持久化什么**：`KP_UIDz` 与 `kpsdk-*` 值得按"账号/浏览器 profile"存下来复用 —— 同一设备多次出现比每次全新更像人。原版把 Kasada 凭据放在**账号级**（`_accountKasada`，`0x14337b669`），不是请求级临时变量。

---

## 5. 版本头是 per-store 的（[Obs]）

二进制里七个版本头，逐字：

```
Nike-Kasada-Version        Footsites-Kasada-Version   Scheels-Kasada-Version
Converse-Kasada-Version    Crocs-Kasada-Version
Crocs-EU-Kasada-Version    Crocs-JP-Kasada-Version
```

**这张表本身就是结论**：版本不能全局共用。同一个 Kasada 版本号在两个站点上未必一致，硬写一个全局常量会让一半站点看到"自称是什么、实际不是"。

`x-kpsdk-v` 的值形态：`j-1.2.988` 这一类（见 `replica/.../ScheelsFlow.cs` 的注释，来自实机抓包）。

---

## 6. Sensor payload 的结构（[Obs]，池里有一条真实样本）

```
0x07191c6c
{"workTime":1772713428577,"id":"1aea246e801c325a64839b2db3e4df92",
 "answers":[6,3],"duration":41.8,"d":1184,"st":1772707875172,"rst":1772707876356}
```

| 字段 | 含义（[Inf]） |
|---|---|
| `workTime` | 客户端时钟 |
| `id` | 本次传感器实例 id |
| `answers` | challenge 的应答（这里的 `[6,3]` 是某次 PoW/交互题的结果） |
| `duration` | 脚本自报的耗时（毫秒级浮点） |
| `d` | 负载长度/尺寸类字段 |
| `st` / `rst` | 开始/接收时间戳 |

**为什么原版专门记 `_kasadaWorkTime`（`0x14345aa92`）**：Kasada 会看握手耗时。几十毫秒产出的 token 比几百毫秒的更可疑。所以原版用 `Stopwatch` 实测并**照实上报**，而不是伪造一个好看的数。

**[Inf] 移植建议**：不要手写这份 payload。让脚本自己生成，你只负责把它的产物原样带出去。手写 payload 等于自己实现一遍 Kasada 的混淆逻辑。

---

## 7. TL 阶段

**[Obs]** 有一条专门的失败文案：

```
Failed solving Kasada (TL)     0x146d8a98c
```

**[Unk]** `TL` 的展开没有证据。可以确定的只有：它是 local solve 路径里的**一个可独立失败的阶段**，所以重试策略要能区分"整体失败"和"卡在 TL"。

---

## 8. 实现清单（照这个顺序做）

```
[ ] 1. 拿到 store 的 script id（HTML 里找 ips.js 标签）
[ ] 2. 取 ips.js 正文，记录 x-kpsdk-v
[ ] 3. 建一个能跑该脚本的环境  ← 02（Jint）或 03（浏览器）
[ ] 4. 从环境里取出 9 个头（含 ct），或从线上的下一个请求里嗅出来
[ ] 5. 把 token 与产出它的 UA 绑定存起来（账号级）
[ ] 6. 业务请求带齐头；body 需要加密时用 cd（03 §4）
[ ] 7. 失败按 05 的状态表分类，再决定重试还是换代理
```
