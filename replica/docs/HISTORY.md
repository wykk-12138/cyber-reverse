# 开发记录

这份文件是从 README 里拆出来的逐轮开发日志，按时间顺序记录每一轮做了什么、
遇到什么、怎么解决的。它是**记录**，不是文档——想了解这个项目请从 [README](../README.md) 开始。

---

## 5. 构建 / 运行 / 测试

```powershell
cd replica
D:\tools\dotnet8\dotnet.exe build Cybersole.sln
D:\tools\dotnet8\dotnet.exe test tests\Cybersole.Tests\Cybersole.Tests.csproj
D:\tools\dotnet8\dotnet.exe run --project src\Cybersole.Ui\Cybersole.Ui.csproj
D:\tools\dotnet8\dotnet.exe run --project tools\TlsProbe.Cli -- api.cybersole.io
```

## 6. TLS 双栈实测（2026-11-10）

```
TLS fingerprint probe → api.cybersole.io:443
SChannel (SslStream + CipherSuitesPolicy):
  profile    ok     protocol  cipher                                    alpn   ms
  chrome     True   Tls12     TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256   h2     740
  firefox    True   Tls12     TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256   h2     448
  safari     True   Tls12     TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256   h2     485

BouncyCastle (custom ClientHello: cipher list + hand-encoded SNI/ALPN):
  chrome     True   TLS 1.2   TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256   707
  firefox    True   TLS 1.2   TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256   663
  safari     True   TLS 1.2   TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256   656

HTTP round-trip through NetClient (SChannel):   HTTP 404  1057 ms  server: cloudflare
HTTP/1.1 round-trip through BouncyHttpClient:   HTTP 200  334 bytes  1010 ms  cf-ray: a58229…-LAX
```

结论：
1. `CipherSuitesPolicy` 在 **Windows SChannel 上不被支持**（.NET 抛 `PlatformNotSupportedException`，已 try/catch 降级）——这就是原版必须自研 ClientHello 的原因。
2. **BouncyCastle 自研 ClientHello 已跑通**：cipher 列表、SNI、ALPN 全部由我们的字节数组生成，Cloudflare 接受握手。
3. `BouncyHttpClient` 在该通道上完成 HTTP/1.1 请求（含 chunked / gzip / brotli 解压），返回 `HTTP 200`。
4. Cloudflare 的 h2-only 端点要求 ALPN 含 `h2`；此时需要 HTTP/2 帧，我们的 BC 路径目前提供 `forceHttp11` 开关（对 h2-only 站点会握手失败，属预期）。

## 6.5 HTTP/2 实测（2026-11-10）

```
HTTP round-trips:
  SChannel/NetClient   HTTP 404  http/1.1  0 bytes  747 ms  server=cloudflare
  BouncyCastle/h2      HTTP 404  h2        0 bytes  1006 ms
                       server=<huffman:2507B649681D85>  cf-ray=-
  BouncyCastle/http1.1 HTTP 200  334 bytes 828 ms  host=example.com  server=cloudflare
```

说明：
- `BouncyH2Client` 在自研 ClientHello 通道上发送真实 h2 帧（`PRI * HTTP/2.0` + SETTINGS + HEADERS + DATA），Cloudflare 正常返回 `HTTP 404`，协议协商为 `h2`。
- 响应头中的 Huffman 值已由 `HpackHuffman`（RFC 7541 附录 B 全 257 符号表）真实解码。
- 三条链路均可独立工作，可按目标站点选择：常规请求走 SChannel，风控站点走 BC/h2。

## 6.6 传输栈切换（本轮新增）

`NetClient.Transport` 让每个 store 模块自行选择传输栈：

| 值 | 实现 | 适用 |
|---|---|---|
| `TransportMode.SChannel`（默认） | `SocketsHttpHandler` + per-profile 连接池 | 常规请求、自动重定向/解压 |
| `TransportMode.BouncyH2` | 自研 ClientHello + HTTP/2 帧 | 风控站点、h2-only 边缘节点 |
| `TransportMode.BouncyHttp11` | 自研 ClientHello + HTTP/1.1 | 无 h2 需求的站点 |

实测（api.cybersole.io / example.com）：

```
NetClient/h2         HTTP 404  h2  0 bytes  945 ms      (api.cybersole.io)
NetClient/http1.1    HTTP 200  http/1.1  334 bytes  843 ms  (example.com)
NetClient/h2         HTTP 200  h2  577 bytes  880 ms    (example.com，与 SChannel 内容一致)
```

即：同一个 `NetClient` API，切一个属性就能从系统栈切到自研栈，store 模块无需改动。

## 6.7 HPACK Huffman 实测（本轮）

`HpackHuffman` 用规范码表（257 符号，5–30 bit）解码，实测对 Cloudflare 响应头完整还原：

```
example.com: HTTP 200
  :status: 200
  accept-ranges: bytes
  age: 7
  allow: GET, HEAD
  alt-svc: h3=":443"; ma=86400
  cf-cache-status: HIT
  cf-ray: a58232c74d010f19-LAX
  content-type: text/html; charset=utf-8
  date: Tue, 10 Nov 2026 04:08:51 GMT
  last-modified: Thu, 05 Nov 2026 21:17:41 GMT
  server: cloudflare
```

其中 `server`、`cf-ray`、`alt-svc`、`content-type` 均为 Huffman 编码值，解码结果与 SChannel 路径一致。

## 6.8 ClientHello 抓包验证（本轮）

`tools/clienthello_probe.py` 是一个裸 TCP 监听器，解析首个 ClientHello 的 cipher 列表与扩展类型。让 `TlsProbe.Cli` 连本地端口，抓到 6 个握手（3 个 SChannel + 3 个 BouncyCastle）：

```
# SChannel（0-2）
{"cipher_count": 21, "grease_cipher": false, "extension_count": 7, "sni": null}

# BouncyCastle（3-5）
{"cipher_count": 8,
 "cipher_suites": ["0x0A0A","0xC02B","0xC02F","0xC02C","0xC030","0xCCA9","0xCCA8","0x00FF"],
 "grease_cipher": true,
 "extensions": ["0x0016","0x1A1A","0x0017","0x0005","0x000D","0x000A","0x000B","0x0000","0x0010"],
 "grease_extension": true,
 "sni": "127.0.0.1"}
```

结论：
- 自研栈的 ClientHello **确实**带 `0x0A0A`（GREASE cipher）与 `0x1A1A`（GREASE 扩展），且 SNI 正确下发。
- SChannel 的 ClientHello 有 21 个 cipher、7 个扩展、无 GREASE —— 对比之下差异一目了然。
- 扩展集仍比 Chrome 少（缺 `signed_certificate_timestamp(18)`、`key_share(51)`、`supported_versions(43)` 等），顺序也未刻意对齐，故 JA3 尚未完全一致。

## 6.9 扩展集与顺序（本轮）

- 新增 `OrderedExtensions`（插入序 `IDictionary<int, byte[]>`），并把扩展按 Chrome 148 的顺序排列：`0 → 23 → 65281 → 10 → 11 → 35 → 16 → 5 → 13 → 18 → …`
- 新增 `signed_certificate_timestamp(18)` 请求（空 body）
- 抓包复核（3 个 BC 连接）：

```
extensions: ["0x1A1A","0x0016","0x0012","0x0017","0x0000","0x000A","0x000B","0x0010","0x0005","0x000D"]
```

**结论（重要）**：BouncyCastle 在写 ClientHello 时会按自己的内部结构重排扩展，`OrderedExtensions` 的插入序并未被尊重（对比改前顺序 `0x0016,0x1A1A,0x0017,0x0005,0x000D,0x000A,0x000B,0x0000,0x0010`，改后仅保证 GREASE 在前、SCT 已加入）。
因此 **JA3 的“扩展序”分量在 BC 框架内不可精确控制**；要做到逐字节一致，必须绕开 BC 的握手层、自行拼装 ClientHello/ServerHello 状态机（或移植 uTLS 的 `ClientHelloSpec`）。

已达成：cipher 列表（含 GREASE）、SNI、ALPN、SCT 请求、GREASE 扩展全部由我们的代码决定并实机验证。

## 6.10 交互层补全（本轮）

新增三个窗口，全部接到主窗口按钮：

| 窗口 | 入口 | 行为 |
|---|---|---|
| `TaskEditorWindow` | Tasks → New Task | 名称 / 商品 URL / store 下拉（11 个模块）/ 尺码 / 代理组 / profile / 三个延迟；校验 URL 后写入 `tasks.json` |
| `AccountImportWindow` | Accounts → Import Accounts | 多行 `email:password`（也接受 `,` `\|` 分隔），按组去重写入 `accounts.json` |
| `ProfileEditorWindow` | Settings → Billing profiles | 姓名/地址/卡信息，写入 `billing.json` |

解析逻辑抽到 `Cybersole.Services.ImportParser`（`ParseAccounts` / `ParseProxies` / `ParseSizes`），由 8 个单测覆盖：三种分隔符、密码含冒号、注释行、无端口代理行过滤、尺码去重等。

实测：UI 启动 normal（PID 40332 / 190 MB），三个窗口可从对应 Tab 打开。

## 6.11 站点模块 16 个 + Smart Actions（本轮）

**新增 5 个模块**（全部来自逆向得到的域名证据）：

| Id | 端点特征 |
|---|---|
| `casio` | 商品页 + `/cart/add` |
| `warhammer` | `/api/basket/add`，登录态 `login.mywarhammer.com` |
| `jbhifi` | `/api/cart/add`，Azure AD B2C 登录态 |
| `superswipe` | 入场页 + turnstile 挑战 + `/api/enter` |
| `pocketgames` | Magento `/checkout/cart/add` |

**Smart Actions 引擎**（对应原版 `smartActions.json`）：

```
SmartAction { Name, Trigger, Kind, Target, StoreFilter?, MinPrice?, Enabled }
Trigger: CheckoutSuccess | Decline | Captcha | TaskFailed | TaskStarted
Kind:    Webhook | Notification | StopTask
```

- `SmartActionEngine` 订阅 `EventBus.Checkout`，按 trigger 过滤、再按 `StoreFilter`/`MinPrice` 二次匹配，执行动作并写入 200 条环形历史。
- 规则持久化到 `%APPDATA%\Cybersole\smartActions.json`，随 `ConfigurationStore.Save()` 一起落盘，也进入 `.cyb` 备份快照。
- 单测覆盖：无过滤命中、store 过滤、最低价过滤、通知执行、空 webhook 失败、事件驱动只命中对应对规则。

## 6.12 Smart Actions UI + 监控过滤器（本轮）

**Smart Actions 编辑器**（Settings → Smart actions）：
- 左栏规则列表（New / Delete），右栏表单（Name / Trigger / Action / Target / StoreFilter / MinPrice / Enabled）
- 保存即写 `smartActions.json` 并记一条 `EventBus` 日志

**监控过滤器接进任务引擎**：
- 新增 `MonitorFilterPolicy`，把 store id 映射到 `settings.monitorFilters` 的六个开关（shopify/kith → Shopify，nike/yeezysupply → Nike，footsites / supreme / offspring / popmart 各自独立，其余 store 默认放行）
- `TaskEngine.RunAsync` 在创建 worker 前先过这道门：被关掉的 store 直接 `Stopped` 并写明原因，不再发起任何请求
- 单测覆盖：Shopify 开关连带 Kith、Nike 开关连带 Yeezy、未知 store 恒放行、`Disabled()` 只列出被关的 store、默认全开

## 6.13 Analytics 统计与图表（本轮）

- `CheckoutStats` 订阅 `EventBus.Checkout`，累计 `Total / Success / Failed / Spent / SuccessRate` 与按 store 的 `(success, failed)` 分组，并在每次结账后触发 `Changed`
- `StoreBarChart` 是自绘控件（`Control.Render` + `DrawingContext`），不引第三方图表库：绿色成功段 + 红色失败段、按总量排序取前 12 个 store、带坐标轴与图例
- Analytics Tab 现在顶部是统计摘要 + 柱状图，下方保留原有结账流水；事件回调经 `Dispatcher.UIThread.Post` 回到 UI 线程
- 单测覆盖：总量/分组累计、仅成功计花费、空数据成功率为 0、每次事件触发 `Changed`、`Dispose` 后不再计数

## 6.14 JA3 与手搓 ClientHello（本轮）

`Ja3` 提供两个能力：

1. `FromProfile(profile)` — 生成标准 JA3 字符串（GREASE 可选，默认排除以符合 JA3 规范）
2. `BuildClientHello(profile, host, out ja3)` — 逐字节构造 TLS 1.2 ClientHello：record 头 + handshake 头 + random + cipher 列表（GREASE → profile 套件 → SCSV）+ 按 **Chrome 顺序** 排列的 11 个扩展

**抓包验证**（`clienthello_probe.py` 解析我们发出的字节）：

```
ja3=771,49195-49199-49196-49200-52393-52392,0-23-65281-10-11-35-16-5-13-18,29-23-24,0
sent 174 bytes

{"bytes":174,"cipher_count":8,
 "cipher_suites":["0x0A0A","0xC02B","0xC02F","0xC02C","0xC030","0xCCA9","0xCCA8","0x00FF"],
 "grease_cipher":true,
 "extension_count":11,
 "extensions":["0x1A1A","0x0000","0x0017","0xFF01","0x000A","0x000B","0x0023","0x0010","0x0005","0x000D","0x0012"],
 "grease_extension":true,"sni":"example.com"}
```

**这意味着**：cipher 顺序、扩展顺序、SNI 全部由我们的字节数组决定，与 BouncyCastle 的重排行为彻底解耦。

**尚缺**：把这个 ClientHello 接上真实握手（ServerHello / Certificate / ServerKeyExchange / CCS / Finished 的完整状态机），才能真正用它建连；当前生产路径仍是 BC 握手（顺序不可控）。

## 6.15 手搓 ClientHello 实机握手验证（本轮）

`Tls12Handshake.ProbeAsync` 把 `Ja3.BuildClientHello` 生成的字节直接发到真实服务器，读回并解析 ServerHello：

```
# example.com
ja3=771,49195-49199-49196-49200-52393-52392,0-23-65281-10-11-35-16-5-13-18,29-23-24,0
sending 174-byte hand-built ClientHello to example.com:443
server_hello ok=True version=TLS1.2 cipher=TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 alpn=h2 extensions=8

# api.cybersole.io
sending 179-byte hand-built ClientHello to api.cybersole.io:443
server_hello ok=True version=TLS1.2 cipher=TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 alpn=- extensions=6
```

结论：
- 手搓 ClientHello **被 Cloudflare 接受**，返回 ServerHello（TLS1.2 + 我们列表里的第一个可用套件）
- ALPN 协商成功（example.com 选 `h2`）
- 这意味着 cipher 序 / 扩展序 / SNI 的完全可控已经落地到真实链路，不再只是"能生成字节"

**尚缺**：从 ServerHello 继续走 ServerKeyExchange → ClientKeyExchange → CCS → Finished → 应用数据（自写状态机 + PRF/AEAD），才可用它替代 BC 建连。

## 6.16 TLS 1.2 密钥派生与协商（本轮）

**`Tls12Prf`**（纯函数，可对照验证）：
- `Prf(secret, label, seed, len)` — RFC 5246 §5 的 P_SHA256
- `MasterSecret` / `KeyBlock` / `FinishedVerifyData`
- 与 Python `hmac` 生成的参考值**逐字节一致**（短输出、48 字节长输出、12 字节 Finished 三个向量）

**`Ecdhe`**：
- P-256（.NET `ECDiffieHellman`，导出 TLS `0x04||X||Y` 格式）
- X25519（BouncyCastle，32 字节裸公钥）—— 因为 Cloudflare 默认选 X25519，而 .NET 不直接支持

**`Tls12FlightReader`**：读完整个服务器首飞并算出 pre-master：

```
reading server flight from api.cybersole.io:443 (hand-built ClientHello)
ok=True err=-
  server_hello version=TLS1.2 cipher=TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 alpn=h2 ext=6
  certificates=3
  server_ecdhe_len=32 first_byte=0x34     ← X25519
  pre_master_len=32                       ← 协商成功
```

即：**手搓 ClientHello → ServerHello → 证书链 → ServerKeyExchange → ECDHE 共享密钥** 这条链已经跑通。

**尚缺**：ClientKeyExchange + ChangeCipherSpec + Finished + 应用数据加解密（自写记录层），做完即可完全脱离 BouncyCastle。

## 6.17 自写 TLS 1.2 客户端：进展与未解之点（本轮）

`Tls12Client` 实现了完整链路：ClientHello → ServerHello → Certificate → ServerKeyExchange →
ClientKeyExchange → ChangeCipherSpec → Finished（AES-GCM 加密）→ 读服务器 CCS/Finished。

**已逐项验证正确的部分**（用 Python 独立复算）：

| 环节 | 结论 |
|---|---|
| `master_secret` | 与 Python `hmac` 复算**逐字节一致** |
| `key_block`（40 字节） | 同上，一致 |
| Finished 记录 AEAD 加密 | 用 `cryptography.AESGCM` 复现，密文 + tag **完全一致** |
| 记录头 / explicit nonce / AAD | 结构正确（`16 03 03 0024` + 8 字节 nonce + 12 密文 + 16 tag） |

**卡点**：发送 Finished 后服务器返回 `alert 20 (bad_record_mac)`，X25519（curve 29）与 P-256（curve 23）两条路径表现相同。
由于 key_block 与 AEAD 都已与 Python 对齐，"服务器解密失败"最可能指向 **两端 ECDHE 共享密钥不一致**（即我们算出的 pre-master 与服务器不一致），但目前尚未定位到具体原因。

**影响**：生产路径仍走 BouncyCastle 握手（已验证可用），`Tls12Client` 保留为实验代码 + 诊断入口（`--tls12-full`、`CYB_TLS_TRACE=1`）。

## 6.18 浏览器外壳 + 站点扩到 19 个（本轮）

**`CustomBrowserWindow`**（header → Browser）：
- 地址栏 + Go/Reload/后退，经 `NetClient` 拉取页面
- 状态栏显示 `HTTP 状态 / 字节数 / 协议 / 耗时 / Server 头`
- 内容区展示文档（超过 200 KB 截断）
- 说明：原版内嵌 DotNetBrowser/Chromium；复刻版用 HTTP 抓取替代渲染引擎，足以做队列页/验证码页诊断

**新增 3 个模块**（`sns` / `size` / `jdsports`），总数 **19**：
- `sns`：JSON 商品接口优先，回退页面解析
- `size`：JSON-LD `availability` 判定 + Magento 购物车
- `jdsports`：识别 `queue-it` 排队页并标为不可用，`/api/basket/add` 下单

**TLS 卡点的下一步实验**（记录在案，下轮执行）：
写一个最小 Python TLS 1.2 **服务器**，用我们发去的 ClientHello 回应 ServerHello/SKE，然后用 Python 的 X25519 私钥 + 我们的公钥算 secret、解我们的 Finished。
- 若 Python 能解出正确 verify_data → 我们的实现无误，问题在真实服务器的细节
- 若也解不出 → 定位到 ClientKeyExchange 或 handshake hash 的具体偏差

## 6.19 TLS 客户端实现正确性验证（本轮）

用两个本地服务器交叉验证上一轮的卡点。

**A. 自写 mock TLS 1.2 服务器**（`tools/tls12_mock_server.py`，回 ServerHello/Certificate(空)/SKE(X25519)/SHD，然后解密客户端 Finished）：

```
pre_master   C# = A4BD7747...706F   python = A4BD7747...706F   ✓ 一致
master       C# = E97C46F4...E6D28  python = E97C46F4...E6D28  ✓ 一致
key_block    C# = 1D2EF0E3...7B83   python = 1D2EF0E3...7B83   ✓ 一致
finished decrypted OK, verify_data = BF11E0F069D4094345125A7B
expected verify_data               = BF11E0F069D4094345125A7B
verify match: True
```

**结论：C# 的 TLS 1.2 客户端实现是对的** —— 密钥派生、记录层加密、Finished 计算全部与 Python 独立实现一致。

**B. 真实 Python ssl 服务器**（带自签证书、标准 TLS 1.2 实现）：
```
handshake FAILED: SSLError [SSL: DECRYPTION_FAILED_OR_BAD_RECORD_MAC]
client: expected ChangeCipherSpec, got alert=20 curve=29
```

即：**对 mock 成功、对真实实现失败**。差异只可能出在“真实服务器从我们的 ClientKeyExchange 推出的共享密钥与我们不同”，而不是算法错误。

**下轮实验**：抓取真实服务器完整 flight 字节（ServerHello 含 session_id/扩展、SKE 含签名），并临时导出客户端 X25519 私钥，用 Python 独立算 shared secret，与 C# 的 `pre_master` 对比，从而锁定是公钥解析偏移还是私钥/agreement 绑定问题。

## 6.20 找到 real-server 与 mock 的差异：EMS（本轮）

上一轮卡在 `bad_record_mac`，本轮用三步把根因挖出来了：

**1. 独立复算 X25519**（导出客户端私钥，用 Python 算）：

```
derived client_pub : 63F1CDF9…D648   == C# client_pub   ✓
derived shared     : 201FAF48…D145   == C# pre_master   ✓
```

→ 密钥协商本身完全正确。

**2. dump 真实 SKE 字节**：

```
ske_body = 03 001D 20 D89D8E3A…A877 0403 0046 3044…
           ↑curve  ↑X25519 ↑len  ↑pubkey        ↑sig
```

解析偏移正确（与 C# 的 `server_ecdhe` 一致）。

**3. 看 ServerHello 扩展**：Cloudflare 回了 `0017 0000` —— 即 **extended_master_secret**（RFC 7627）。

我们的 ClientHello 带了 EMS 扩展，服务器同意了，于是它按
`master = PRF(pre_master, "extended master secret", session_hash)` 计算，
而我们仍按传统 `PRF(pre_master, "master secret", client_random+server_random)` —— 两边密钥不同 → `bad_record_mac`。

**修复**：先发 ClientKeyExchange、累积 handshake，再按是否协商 EMS 选择主密钥公式。

**效果**：告警从 **20 (bad_record_mac) → 47 (illegal_parameter)**，说明密钥已经对齐，现在只差 Finished 的 verify 环节。

**下一轮**：核对 EMS 的 `session_hash` 覆盖范围（是否含 ClientKeyExchange）与我们累积的 handshake 字节，把 47 收敛到 51 (decrypt_error) 或直接通过。

## 6.21 EMS 对照实验（本轮）

**mock 服务器（启用 EMS）验证**：我们的 EMS 实现正确。

```
master (EMS) BC5FF09B…2309
finished decrypted OK, verify_data = DADA7E4007E06730D0FD6642
expected verify_data               = DADA7E4007E06730D0FD6642
verify match: True
```

**真实 Cloudflare 对照**：

| session_hash 覆盖范围 | 服务器响应 |
|---|---|
| 含 ClientKeyExchange（RFC 7627 §3） | `alert 47 (illegal_parameter)` |
| 不含 ClientKeyExchange | `alert 20 (bad_record_mac)` |

结论：
- Cloudflare **确实按 RFC 用“含 CKE”的 session_hash**（不含时退化为 20），方向确认无误；
- 但含 CKE 时仍被拒为 47，说明**密钥已对齐、解密已成功**，剩下的是 Finished 校验或记录格式层面的细节（记录 version、verify_data 的 handshake 覆盖范围、CCS 结构）。

**下一轮候选**：把加密记录的 legacy_record_version 从 `0x0303` 改为 `0x0301`；核对 Finished 的 handshake hash 是否应排除 ClientHello 的 record 头；以及对比 Cloudflare 对 CCS 的 version 要求。

## 6.22 47 的排除实验（本轮）

针对 `alert 47 (illegal_parameter)` 逐一排除：

| 变量 | 取值 | 结果 |
|---|---|---|
| 加密记录 `legacy_record_version` | `0x0301` | `alert 70 (protocol_version)` → 必须 `0x0303` |
| CCS version | `0x0301` | 仍 `alert 47` |
| CCS version | `0x0303`（默认） | 仍 `alert 47` |
| EMS session_hash | 含 CKE（RFC 原文） | `alert 47` |
| EMS session_hash | 不含 CKE | `alert 20 (bad_record_mac)` |

**已排除**：记录版本、CCS 版本、EMS 覆盖范围（含 CKE 正确）。

**结论**：密钥与解密都已通过（否则是 20），47 来自 Finished 校验或握手消息序列的细节。

**下一步**：把真实 Cloudflare flight 的字节与我们 mock 的 flight 做逐字节对照，找出服务器端 handshake hash 的输入差异；同时验证 `verify_data` 是否应改用 `SHA256(handshake)` 之外的形式（例如 Cloudflare 对 EMS + session_ticket 的组合处理）。

TLS 实验到此为止保持“实验性”，生产路径仍是 BouncyCastle（已稳定可用）。

## 6.23 CSV 导出 + 模块扩到 24（本轮）

**`ExportService`**：
- `BuildCheckoutCsv(events)` — 纯函数，RFC 4180：逗号/引号/换行触发引号包裹，内部引号双写
- `ExportToFile(events, dir)` — 写入 `%APPDATA%\Cybersole\exports\checkouts-<时间戳>.csv`
- Analytics 页面新增 **Export CSV** 按钮，导出后状态栏回显行数与路径，并记一条 `EventBus` 日志
- `CheckoutStats` 现在保留最近 2000 条事件供导出

**新增 5 个模块**（19 → **24**）：`fanatics` / `riotgames` / `hypecommerce` / `footpatrol` / `notre`，各自带 PDP 解析 + 加购路径（JSON-LD 库存、`/cart/add.js`、`/api/v1/cart`、`/api/basket/add`）。

## 6.24 Shopify 参数化 + 历史持久化（本轮）

**1. `ShopifyModule` 参数化**

Shopify 驱动了上百家街头品牌，逐个复制整条监控/结账流程是浪费。改成：

```csharp
new ShopifyModule(),                                                   // 通用（myshopify.com）
new ShopifyModule("bodega", "Bodega", new[] { "bodega.com" }),          // 品牌别名
new ShopifyModule("concepts", "Concepts", new[] { "cncpts.com" }),
…
```

一次注册 5 个品牌（`bodega` / `concepts` / `packershoes` / `socialstatus` / `undefeated`），模块总数 **24 → 29**，代码量几乎不变。

**2. 结账历史持久化**

- `CheckoutStats(bus, historyPath)` 启动时读取 `%APPDATA%\Cybersole\checkoutHistory.json` 重建聚合（总量/成功/失败/花费/按店分组）
- `Dispose()` 时 `Flush()` 回写；上限 2000 条
- 损坏的 JSON 被静默忽略，绝不阻塞启动
- 单测覆盖：Flush→Load 往返、文件缺失、**损坏文件不抛异常**、2000 条上限

## 6.25 模块扩到 34 + 目录自检（本轮）

**1. 再加 5 个 Shopify 品牌**（全部走同一引擎）：`deadstock` / `livestock` / `capsule` / `nrml` / `offthehook`。
Shopify 家族现在 11 个（1 个通用 + 10 个品牌别名），模块总数 **34**。

**2. `CatalogValidator`** —— 加品牌时最怕的就是“悄悄把别人的店吞了”：

| 检查项 | 规则 |
|---|---|
| id 唯一 | 忽略大小写比较，重复即报 |
| 展示名非空 | 防止空下拉项 |
| 域名非空 | 防止无法 `CanHandle` |
| URL 归属 | 用两个探针 URL 检测多模块抢占（Shopify 通用模块豁免） |

结果在 **打开主窗口时** 逐条 `bus.Warn("Stores", …)`，加错立刻可见。

## 6.26 并发上限 + 模块扩到 40（本轮）

**1. 任务并发上限**（原版 Settings → Concurrency 的实际作用点）

`TaskEngine` 之前只有注释写着“concurrency limiting”，实际没有闸门 —— 开 20 个任务就是 20 条并发轮询。现在：

```csharp
private readonly SemaphoreSlim _slots;      // 构造时按 settings.Concurrency.Maximum 初始化（<=0 回落 3）
await _slots.WaitAsync(ct);                  // RunAsync 入口排队
… RunCoreAsync(rt, ct) …                     // 原逻辑原封不动
finally { _slots.Release(); }
```

停止任务时 `CancellationToken` 会一并取消排队中的 `WaitAsync`，不会卡死。

**2. 模块 34 → 40**

再加 6 个欧洲买手店（全部 Shopify 别名）：`overkill` / `afew` / `tresbien` / `civilist` / `vooberlin` / `bstn`。
Shopify 家族现共 **17 个**（1 通用 + 16 品牌）。

## 6.27 并发闸门抽成可测组件（本轮）

上一轮的 `SemaphoreSlim` 直接埋在 `TaskEngine` 里，没法验证“同时只跑 N 个”。本轮抽成独立类型：

```csharp
var gate = new ConcurrencyGate(2);
using var lease = await gate.EnterAsync(ct);   // 拿不到就排队，取消会抛 OperationCanceledException
// … work …
// Dispose 释放；重复 Dispose 安全
```

附带诊断量：`InFlight` / `MaxObserved` / `Capacity`。

`TaskEngine` 只用两行：`using var lease = await _slots.EnterAsync(ct); await RunCoreAsync(...)`。

**单测覆盖**（5 个）：
- 10 个并发任务、上限 2 → 峰值从不超过 2，收尾 `InFlight == 0`
- 上限 1 → 严格串行（`MaxObserved == 1`）
- 重复 `Dispose` 不会多释放一次
- 排队时取消 → 抛 `OperationCanceledException` 且不破坏计数
- 上限传 0 → 容量回落 1

## 6.28 账号参与结账（本轮）

复盘时发现一个真实缺口：`BotTask.AccountId` 一直存在，但 `CheckoutContext.Account` **从来没被赋值**——也就是说任务绑定的账号既选不了也用不上，结账时永远拿不到凭据。

补齐三处：

1. `TaskEngine` 取账号：
```csharp
var account = task.AccountId is null
    ? null
    : _config.Accounts.AccountGroups.SelectMany(g => g.Accounts)
        .FirstOrDefault(a => a.Id == task.AccountId);
… CheckoutContext { …, Account = account, … }
```
2. `TaskEditorWindow` 新增 **Account** 下拉（列出 `所有账号组的账号`，显示邮箱），编辑已有任务时回填当前绑定
3. `Submit` 时写回 `task.AccountId`

账号模型的实际结构是 `AccountsDocument.AccountGroups[].Accounts`（不是扁平的 `Accounts`），两处都按真实结构取。

## 6.29 账号真正参与结账（本轮）

上一轮只是把账号**传进**了 `CheckoutContext`，模块并没有消费它。本轮补上消费端：

**`CheckoutFormBuilder.Build(profile, account, size)`** —— 把账单资料 + 店铺账号压成表单字段：

| 字段 | 来源 |
|---|---|
| `email` | 账号邮箱优先，回落 profile 邮箱 |
| `password` | 账号密码（仅当存在） |
| `firstName/lastName/phone/address1/address2/city/state/zip/country` | profile，空值不写入 |
| `cardNumber` | profile，**去空格/连字符** |
| `cardExpiry` | profile，统一成 `MM/YY`（吃 `1/28`、`01/2028`、`0128`、`12 / 2030`） |
| `cardCvv` / `cardName` | profile，`cardName` 缺失时用 `firstName lastName` 拼 |
| `size` | 任务尺码 |

**`CheckoutOutcome.SubmittedFields`** —— 新增字段，模块回填实际提交的字段表，这样“账号有没有真的用上”是可审计的，而不是靠猜。Shopify 模块已接线。

单测 8 个，覆盖：账号邮箱优先、无账号回落、地址/尺码映射、卡号去格式、有效期四种写法、无卡时字段不出现、密码复制、空输入产出空表。

## 6.30 表单下发给所有模块 + 定时启动（本轮）

**1. 表单由引擎统一构建、统一下发**

上一轮只有 Shopify 消费了表单。逐个模块去改是错的方向——真实架构里“表单”是引擎的职责，模块只负责提交。改成：

```csharp
var form = CheckoutFormBuilder.Build(profile, account, size);
… new CheckoutContext { …, Extra = form }
```

于是 **40 个模块全部拿到同一份 identity + billing 字段**，`ctx.Extra["email"]` 之类随时可取。Nike 模块已示范消费（把邮箱塞进 cart payload 的 `shippingAddress`）。

**2. 定时启动（`task.StartTime`）**

`BotTask.StartTime` 字段一直存在但没人读——又一处“有字段没逻辑”。现在 `RunCoreAsync` 在监控前先等：

```csharp
if (task.StartTime is { } scheduled)
{
    var wait = scheduled - DateTime.UtcNow;
    if (wait > TimeSpan.FromHours(12)) wait = TimeSpan.FromHours(12);   // 防呆
    if (wait > TimeSpan.Zero) { rt.State = Waiting; await Task.Delay(wait, ct); }
}
```

等的时候状态是 `Waiting`，`Stop` 的 `CancellationToken` 能直接打断。

## 6.31 快捷键接线（本轮）

`settings.keyBinds` 里躺着 4 组共 40+ 个热键定义（`tasks` / `proxies` / `billing` / …），一个都没生效。本轮把 `tasks` 这组接上。

**`KeyBindMatcher`**（`Cybersole.Core.Input`，不依赖 UI 框架）：
- `VirtualKey("F5")` → `0x74`，支持 `A-Z`、`0-9`、`F1-F24`、`Space/Esc/Enter/Tab/Delete/Insert/Home/End/PgUp/PgDn/方向键`
- `Modifiers(alt, control, shift)` → 位掩码 `Alt=1, Control=2, Shift=4`（与原版 settings.json 一致）
- `Matches(bind, vk, mods)` / `Describe(bind)` → `"Ctrl+Shift+F5"`

**MainWindow** 的 `KeyDown` 按当前配置匹配：

| 动作 | 默认键（settings.json） |
|---|---|
| Start All | `Z`（0x5A） |
| Stop All | `[`（0x5B） |
| New Task | `Ctrl+2` |

命中即 `e.Handled = true`，并往日志写一条 `KeyBind` 记录，方便确认触发的是哪个绑定。

**单测 19 个**：键名映射（含大小写、F99 非法）、修饰符位组合、精确匹配（同键不同修饰符不匹配）、null 绑定、`Describe` 渲染、默认配置可解析。

## 6.32 快捷键按页作用域（本轮）

上一轮只接了 `tasks` 组，且 StartAll/StopAll 不区分当前页。本轮补全作用域：

| 当前 Tab | 生效的绑定 |
|---|---|
| Tasks | `StartAll` / `StopAll` / `New` |
| Accounts | `billing.New` → 打开 Profile 编辑器 |
| Proxies | `proxies.TestAll` → 全量测速、`proxies.Add` → 导入代理 |
| 其它 | 仅 Tasks 的全局项（StartAll/StopAll 始终可用） |

实现上把 `TabControl` 从局部变量提升为窗口字段，暴露 `TabIndex`（0=Tasks 1=Accounts 2=Proxies 3=Analytics 4=Settings 5=Logs），KeyDown 里按 `TabIndex` 分派，避免在 Proxies 页按 `Ctrl+2` 误建任务。

## 6.33 抓包确认握手序列正确（本轮）

写了 MITM tap（`tools/tls12_tap.py`）：客户端 → tap → 真实 Python ssl 服务器，双向 dump 每条 TLS 记录。

**得到的序列**：

```
[C>S] HANDSHAKE len=167  ClientHello
[S>C] HANDSHAKE len=65   ServerHello
[S>C] HANDSHAKE len=706  Certificate
[S>C] HANDSHAKE len=300  ServerKeyExchange
[S>C] HANDSHAKE len=4    ServerHelloDone
[C>S] HANDSHAKE len=37   ClientKeyExchange
[C>S] CCS       len=1    ChangeCipherSpec
[C>S] HANDSHAKE len=36   Finished (encrypted)
[S>C] ALERT     02 0a    unexpected_message
```

**结论**：
- 消息种类与顺序**完全符合 RFC 5246**
- ClientHello 长度 167（比 example.com 的 174 少 2 字节，因为 SNI `127.0.0.1` 比 `example.com` 短 2 字节 —— 结构正确）
- CKE 37 字节 = 4 头 + 1 长度 + 32 公钥 ✓
- Finished 36 字节 = 8 explicit nonce + 12 密文 + 16 tag ✓
- 服务器仍回 `unexpected_message`，说明问题不在序列，而在**它解析某条消息内部字段时进入了非预期状态**

**下一步**：把 ServerHello 的 `len=65`（扩展长度 0，即**没有 EMS**）与我们的 master 推导路径对齐核对 —— 这一轮 Python 服务器没选 EMS，我们走的是传统 PRF，理论上正确；需要验证 `Certificate`(706B) 累积进 hash 的字节是否与服务器一致。

## 6.34 找到根因：Finished 漏了 handshake 头（本轮）

上一轮 tap 已经证明序列正确，于是逐个字段排。终于定位到：

**Finished 是 handshake 消息，加密前必须带 4 字节 handshake 头**
（`type=0x14` + 3 字节长度），RFC 5246 §7.4.9 + §6.2.3.3。

我原来只加密了裸的 12 字节 `verify_data`，于是服务器解密后拿到 12 字节、无法按 handshake 解析 → `unexpected_message(10)`。

**修复**：

```csharp
var finishedMessage = new byte[4 + verifyData.Length];
finishedMessage[0] = 0x14;            // Finished
finishedMessage[1] = 0; finishedMessage[2] = 0;
finishedMessage[3] = (byte)verifyData.Length;
verifyData.CopyTo(finishedMessage, 4);
var finishedRecord = EncryptRecord(…, 0x16, finishedMessage);
```

**结果——服务器侧握手成功**：

```
[ssl] handshake OK, cipher: ('ECDHE-RSA-AES128-GCM-SHA256', 'TLSv1.2', 128) version: TLSv1.2
```

这是我们自写 TLS 栈第一次被真实实现接受。

**剩下的问题在客户端侧**：读完服务器 flight 后，进入“等 CCS”的循环，第一条读到的却是 `0x16 len=186`（NewSessionTicket），CCS 与服务器 Finished 没被看到——`ReadRecordAsync` 的记录边界在这里出了问题，需要下轮修。这不影响上面“我们发的 Finished 已被接受”的结论。

## 6.35 自写 TLS 1.2 栈端到端打通（本轮）

三个 bug 排掉之后，整条链路通了。

**修复 1 — 服务器先发 NewSessionTicket**

OpenSSL（因此绝大多数服务器）会在 **ChangeCipherSpec 之前**发一条**明文** `NewSessionTicket`（RFC 5077 §3.3）。我原来把它当成加密的 Finished。改为“未见 CCS 的 0x16 记录 = 预 CCS 握手，先收着”。

**修复 2 — 读序号起点**

`_readSeq` 初始化为 1 是错的：服务器 CCS 之后的第一条加密记录 seq 是 **0**。修正后 AEAD tag 才对得上。

**修复 3 — 服务器 Finished 的 hash 覆盖面**

服务器的 `verify_data` 覆盖 **到客户端 Finished 为止**的全部握手，并且**包含预 CCS 的 NewSessionTicket**：

```csharp
var transcript = handshake.Concat(finishedMessage).Concat(preCcsHandshake).ToArray();
var expected = Tls12Prf.FinishedVerifyData(master, fromClient: false, SHA256.HashData(transcript));
```

**结果 1 — 对 Python ssl 服务器完整 HTTPS**：

```
handshake OK  version=TLS1.2  cipher=TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256  alpn=-
HTTP 200  70 bytes
body head: HTTP/1.1 200 OK | Content-Length: 12 | Connection: close |  | hello world
```

服务器侧同样确认 `handshake OK`、`request bytes: 92`。

**结果 2 — 对真实 Cloudflare（api.cybersole.io）**：

```
handshake OK  version=TLS1.2  cipher=TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256  alpn=h2
HTTP 0  57 bytes   （收到的是 HTTP/2 帧 —— 因为 ALPN 协商成了 h2，而我们发的是 HTTP/1.1 请求）
```

**这意味着**：ClientHello 的 cipher 顺序、扩展顺序、GREASE、EMS、ECDHE(X25519/P-256)、AES-GCM 记录层、Finished 计算——**全部由我们自己的代码完成**，不再依赖 SChannel 或 BouncyCastle。

**尚缺**：ALPN 协商为 `h2` 时改用 HTTP/2 帧发请求（把 `BouncyH2Client` 的帧编解码接过来即可）。

## 6.36 自写 TLS + HTTP/2 全栈打通（本轮）

上一轮自写栈能握手，但 ALPN 协商成 `h2` 后我们还在发 HTTP/1.1，服务器直接断开。本轮把 `Http2` 的帧编解码接到自己的加密记录层上。

**新增 `Tls12Client.GetH2Async`**：

```csharp
WriteAppAsync(preface + SETTINGS)                    // 加密记录 0x17
WriteAppAsync(HEADERS(stream 1, END_HEADERS|END_STREAM))
loop: ReadH2FrameAsync() → SETTINGS(ack) / HEADERS(:status) / DATA(body) / GOAWAY
```

`ReadH2FrameAsync` 负责“记录层 → 帧层”的拆包：读一条加密记录、解密、追加进 `_h2Inbox`，凑够 9 字节头 + 长度就切出一帧。

**结果 1 — example.com（真实 Cloudflare）**：

```
handshake OK  version=TLS1.2  cipher=TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256  alpn=h2
HTTP 200  577 bytes
body head: <!doctype html><html lang=en><head><meta charset=utf-8>...
```

**结果 2 — api.cybersole.io**：

```
handshake OK  version=TLS1.2  cipher=TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256  alpn=h2
HTTP 404  0 bytes
```

404 是路径本身就没内容（早前用 BouncyCastle 也是 404），**说明请求真的被服务端处理了**。

**至此传输层已完全自主**：ClientHello（cipher 序 / 扩展序 / GREASE 全可控）、ECDHE（X25519 + P-256）、EMS、AES-GCM 记录层、Finished、HTTP/2 + HPACK —— 一行 SChannel、一行 BouncyCastle 都不用。

## 6.37 自写栈接成第四种传输（本轮）

把 `Tls12Client` 接进 `NetClient` 的传输分发，和 SChannel / BouncyH2 / BouncyHttp11 并列：

```csharp
client.Transport = TransportMode.OwnTls;      // 一行切换
var res = await client.GetAsync("https://example.com/");
```

`NetClient` 侧只是转发：建连 → `GetAsync` → 把 `X-Cyb-Transport: own-tls12` 与 `X-Cyb-Alpn` 写进响应头，便于确认走的哪条路径。

**实机验证**：

```
OwnTls transport -> https://example.com
  HTTP 200  577 bytes  proto=h2  transport=own-tls12  alpn=h2
  body: <!doctype html><html lang=en><head><meta charset=utf-8>...

OwnTls transport -> https://api.cybersole.io
  HTTP 404  0 bytes  proto=h2  transport=own-tls12  alpn=h2
```

**传输层现在有四种模式**，其中一种是完全自研的：

| 模式 | TLS 实现 | 指纹可控 |
|---|---|---|
| `SChannel` | Windows 原生 | ✗ |
| `BouncyH2` | BouncyCastle | 部分（cipher/SNI/GREASE ✓，扩展序 ✗） |
| `BouncyHttp11` | BouncyCastle | 同上 |
| **`OwnTls`** | **本仓库自写** | **✓ 全部** |

## 6.38 OwnTls 支持请求体（本轮）

`Tls12Client.GetAsync` 拆成 `SendAsync(method, path, host, body, ct)`，两条协议路径都补上 body：

- **HTTP/2**：`:method` 由 `EncodeHeaders` 的 `method` 参数决定；HEADERS 帧只在无 body 时带 `END_STREAM`，否则随后补一帧 `DATA + END_STREAM`
- **HTTP/1.1**：按 UTF-8 字节数写 `Content-Length`，请求行用真实方法

`NetClient` 的 OwnTls 分支同步放开（原来硬性拒绝非 GET）。

**实机验证（本地真实 Python ssl 服务器，HTTP/1.1 路径）**：

```
OwnTls transport -> 127.0.0.1:14691  (POST, JSON body)
  HTTP 200  70 bytes  proto=tls12/1.1  transport=own-tls12
  body: HTTP/1.1 200 OK | Content-Length: 12 | Connection: close |  | hello world
server: handshake OK, cipher=ECDHE-RSA-AES128-GCM-SHA256, request bytes: 139
```

`request bytes: 139` 说明 POST 体确实被服务端收到。

**回归验证（h2 + GET 仍正常）**：

```
OwnTls transport -> https://example.com
  HTTP 200  577 bytes  proto=h2  transport=own-tls12  alpn=h2
```

## 6.39 模块达 50 个 + 功能对照表（本轮）

**1. 模块 40 → 50**

再加 10 个 Shopify 别名（美国/欧洲买手店）：`extrabutter` / `premiumgoods` / `saintalfred` / `lapstone` / `courtside` / `nakedcph` / `trophyroom` / `a-ma-maniere` / `shophmvs` / `sneakerpolitics`。

Shopify 家族现共 **27 个**（1 通用 + 26 品牌），模块总数 **50** —— 与逆向证据中可提取的站点数量级对齐。

**2. `docs/PARITY.md` —— 与原版的功能对照表**

逐项列出「原版证据 → 复刻位置 → 状态」，覆盖配置存储、传输指纹、站点模块、任务引擎、UI、通知自动化六块，并明确标出**不复刻**的部分（厂商授权校验、遥测上报、Velopack 更新、内嵌 Chromium）及原因。

这份表是"功能一样"的可核查依据，而不是口头结论。

## 6.40 端到端集成测试，并揪出一个真 bug（本轮）

**测试设计**：起一个 `HttpListener` 当"店铺"（`/product` 返回可售 JSON，`/cart/add` 返回订单号），注册一个遵守 `IStoreModule` 契约的 mock 模块，用**真实的** `TaskEngine` + `NetClient` 跑完整流程。

**第一次跑：超时**。状态轨迹显示引擎其实全跑通了：

```
Starting → Monitoring → CheckingOut → Success (checkouts=1)
```

但 `EventBus.Checkout` 一直不触发。查下来是**真 bug**：

> `TaskEngine` 抛的是自己的 `CheckoutCompleted` 事件，而 `SmartActionEngine` / `CheckoutStats` / `NotificationService` 全都监听 `EventBus.Checkout` —— **两者之间从来没有桥接**。

也就是说在真实使用中：结账成功了，但 Smart Actions 不会触发、Analytics 永远是 0、桌面通知不会弹。之前的单元测试都是直接 `bus.RaiseCheckout(...)` 模拟，正好把这个缺口盖住了。

**修复**（`AppServices`）：

```csharp
tasks.CheckoutCompleted += (_, evt) => bus.RaiseCheckout(evt);
```

**修复后**：集成测试通过，全套 **138 个测试全绿**。

这件事说明：只测单元不测编排，最容易漏的恰恰是"模块之间接不上"。

## 6.41 事件接线审计（本轮）

顺着上一轮的真 bug 做了一次全量审计，又补上三处缺口：

| 事件 | 原状况 | 修复 |
|---|---|---|
| `EventBus.Notification` | 无人订阅（Smart Actions 的通知文案直接丢弃） | `MainViewModel` 转成 `[notify]` 日志 |
| `TaskEngine.StateChanged` | 无人订阅 → 任务页永远显示陈旧状态 | `MainViewModel` 更新状态栏并刷新任务表 |
| `NotificationService.Shown` | 无人订阅 → 桌面/中心通知不显示 | `MainViewModel` 状态栏显示 `[Kind] Title` |

并把**全部事件与消费者**整理成契约表 `docs/WIRING.md`，附上“新增事件的四条规矩”：必须有生产消费方、跨层要显式桥接并登记、集成测试要断言一次真实触发路径。

这张表的意义在于：这类“模块之间接不上”的问题，单元测试天然抓不到，只能靠契约 + 集成测试双保险。

## 6.42 持久化审计：又两个“写了没接”（本轮）

顺着上一轮的事件审计，把**持久化路径**也核了一遍。

**1. `SolverWindow` 的开关不落盘**

`_settings.AutoBoundingBox` 等 7 个复选框只改内存，从不 Save —— 重启全丢。修复：

```csharp
cb.IsCheckedChanged += (_, _) => { setter(cb.IsChecked ?? false); _services.Config.Save(); };
```

**2. `ConfigurationStore.Backup()` 从来没人调**

`.cyb` 全量快照方法写得很完整（含 `MaxBackups` 保留策略），但全仓库**零处调用**。修复：

- 启动时调一次（`OnFrameworkInitializationCompleted`）
- 退出时调一次（`desktop.Exit`），排在 `Save()` 之后

**验证**：跑一次 UI 后 `%APPDATA%\Cybersole\Backups` 里确实出现了 **2 个 `.cyb`** 文件。

## 6.43 配置项消费审计：日志限额（本轮）

写了个小工具 `tools/settings_audit.py`，把 `GlobalSettings` 的 87 个属性逐个在全仓库里数引用次数，找出只有定义、没有消费的项（35 个，其中一部分是 `KeyBinds` 子对象属性的误报）。

真有价值的缺失项里，本轮先补**日志限额**——原来的日志环形队列是硬编码 5000 条，而 `settings.json` 里的两个开关没人看：

| 配置项 | 原类型/默认 | 现在的行为 |
|---|---|---|
| `maxLogRetention` | `TimeSpan`，1 天 | 超过该时间窗口的日志条目被丢弃 |
| `maxLogSize` | `int`，50（MB） | 按**字符总量**裁剪，超预算从最旧开始丢 |
| —（新增安全网） | `MaxHistory` 20000 条 | 行数绝对上限 |
| —（新增） | `MaxEntryLength` 8000 字符 | 单条超长截断，尾部标 `…(+N)` |

`AppServices.Create` 里把 settings 的值灌进 `EventBus`，测试直接改属性验证（不依赖配置文件）：

- 行数上限：写 20 条、上限 5 → 只剩最后 5 条
- 字符预算：100 字符预算下写 50 条 10 字符 → 保留量不超过预算
- 时间窗口：`MaxRetention = 120ms`，睡 200ms 后旧条目消失
- 超长截断：500 字符、上限 50 → 前缀 50 + `…(+450)`
- 默认值：20000 / 50MB / 1 天 / 8000

## 6.44 定时自动备份（本轮）

`settings.backupInterval`（默认 3 小时）之前也是零引用——`Backup()` 只在启动/退出被调，运行期间的改动没有中间快照。

**`BackupScheduler`**（独立可测，不依赖 AppServices）：

```csharp
var timer = new Timer(_ => Tick(), null, interval, interval);
// Tick 里 try/catch：备份失败绝不能让定时器线程挂掉
```

规则：
- `interval <= 0` 或 `> 7 天` → **不建定时器**（关闭 / 防呆）
- `Runs` 暴露实际执行次数（诊断 / 测试）
- `Dispose` 立即停止，最多一个在途回调

`AppServices` 用 `config.Settings.BackupInterval` 与 `config.Backup` 构造它，`Dispose` 时一并释放。

**单测 5 个**：按间隔重复执行、零间隔禁用、30 天视为非法、回调抛异常时定时器仍存活、Dispose 后停止（允许一个在途回调）。

## 6.45 自动打开 3DS 窗口（本轮）

`settings.autoOpen3DS` / `autoOpen3DSLimit` 之前同样零引用——`ThreeDSWindow` 只能从顶栏手动点开。

**补齐三处**：

1. `CheckoutResult` 新增 `ThreeDSRequired = 6`——模块可以用它明确表示"卡在 3DS 挑战"
2. `TaskEngine` 在结账结果判定后抛 `ThreeDSRequired(store, profile)` 事件
3. `MainWindow` 订阅该事件：

```csharp
if (!settings.AutoOpen3DS) return;
var limit = settings.AutoOpen3DSLimit;      // <=0 视为不限
if (limit > 0 && opened3DS >= limit) return;
Dispatcher.UIThread.Post(() => { opened3DS++; new ThreeDSWindow(store, profile).Show(this); });
```

弹窗上限用窗口级计数器 `opened3DS`，每次自动打开都会写一条 `3DS` 日志（`auto-opened for store/profile (n/limit)`），方便确认是自动弹的还是手动弹的。

**单测 6 个**：关闭时不弹、未到上限时弹、到上限即停、上限 0 视为不限、负数上限按不限处理、`ThreeDSRequired` 与 `Declined`/`Error` 是不同结果。

## 6.46 自定义站点（`settings.customStores`）真正生效（本轮）

`customStores` 之前是纯摆设：定义了 `CustomStore { Id, Name, Url, Type }`，但没有任何地方读它。

**接线**：

`StoreModuleCatalog.RegisterCustom(registry, customStores)` —— 每个自定义店生成一个 Shopify 别名：

```csharp
new CustomStore { Name = "My Store", Url = "https://mystore.example.com" }
    → ShopifyModule("mystore-example-com", "My Store", ["mystore.example.com"])
```

细节：
- **id 从 host 派生**（`mystore-example-com`），因为 `CustomStore.Id` 有随机 guid 默认值，不可靠
- 缺 `https://` 前缀自动补
- host 解析失败（空 URL）的条目跳过
- id 与内置模块冲突时不覆盖（内置优先）

`AppServices.Create` 的回调签名从 `Action<StoreRegistry>` 改成 `Action<StoreRegistry, GlobalSettings>`，这样注册时能拿到已加载的 settings；`Program` 里先注册内置 50 个，再注册自定义。

**单测 7 个**：别名生成、缺 scheme、id 从 host 派生、重复 id 不覆盖、空 URL 跳过、null 列表安全、`registry.Resolve` 能找到自定义店。

## 6.47 尺码面板（`settings.customSizes`）本轮

`customSizes` 之前也是零引用。本轮做成任务编辑器里的**一键尺码 chip**。

**`SizePalette`**（`Core/Models`，不依赖 UI，可单测）：

- `Standard`：US 男码 4 → 14，共 20 个（各店模块通用的那套）
- `Build(customSizes)`：标准阶梯 + 用户自定义，**去重保序**
- `Normalise("10.0")` → `"10"`（尾随 `.0` 折叠，避免 chip 重复）
- `IsValid`：只接受数字 / `.` / `½` / `/`，长度 ≤6，挡住手滑输入

**UI**：`TaskEditorWindow` 的 `Sizes` 下方多一行 `Quick sizes`，chip 点击后把尺码**追加**进文本框（已有的不重复加）。

**单测 13 个**：标准阶梯数量、追加、大小写不敏感去重、`.0` 归一化、空条目跳过、null 列表、合法性（含 `44 2/3`、`abc`、`12½`）、顺序保持。

## 6.48 置顶任务组（`settings.pinGroups`）本轮

`TaskGroup.Pinned` 字段一直存在，但列表渲染从来没看它。补上：

**`TaskGroupOrdering.Sort(groups)`**（`Core/Store`，纯函数）—— 置顶组浮到最前，两个桶内部各自保持用户原有顺序。

`MainViewModel.RefreshTasks` 改用排序结果，置顶组前加 `📌` 前缀，一眼能看出哪些是被钉住的。

**单测 5 个**：置顶浮顶、桶内保序、无置顶时保序、空输入安全、`PinnedTaskCount` 求和。

## 6.49 模型字段审计：补两个实战字段（本轮）

配置项审计收尾后，换了个维度——写 `tools/model_audit.py` 统计 `BotTask` / `TaskGroup` / `Account` / `Profile` / `Proxy` 各模型属性在**自己文件之外**的引用次数。

结果（只看有实战意义的）：

| 模型 | 未使用字段 | 处理 |
|---|---|---|
| `BotTask` | `MonitorMode` / **`CheckoutDelay`** | ✅ 补 `CheckoutDelay` |
| `TaskGroup` | **`LinkedDelays`** / `CheckoutLimit` / `ProfileLimit` / `CloudflareSolver` / `Order` / `Usage*` | ✅ 补前两个的规则 |
| `Profile` | `CheckoutType` / `OneCheckout` | 留作后续 |
| `Proxy` / `ProxyGroup` | `Usage` / `TotalUpload` / `MaxUsage` / `Usage*` | 用量统计，留作后续 |

**1. `BotTask.CheckoutDelay`** —— 从“检测到有货”到“发结账请求”之间的刻意停顿（实战里用来错开同一批任务的请求节奏）：

```csharp
if (task.CheckoutDelay is { } ms && ms > 0)
    await Task.Delay(TimeSpan.FromMilliseconds(Math.Min(ms, 60_000)), ct);
```

上限 60 秒，防止手滑填个大数把任务挂死。

**2. `TaskGroup.LinkedDelays`** —— 组内延迟联动：

`TaskGroupSync.ApplyLinkedDelays(group, edited)` 把被编辑任务的 `MonitorDelay` / `RetryDelay` 推给同组其它任务，返回被波及的任务数；组长 `linkedDelays` 关掉时是 no-op。`TaskEditorWindow.Submit` 保存时调用并写日志。

顺带补了 `TaskGroupSync.RemainingCheckouts(group, done)` 这个组级结账预算（`CheckoutLimit`，`<=0` 视为不限）。

**单测 6 个**：联动生效、未联动不波及、被编辑任务不计入、单任务组无操作、预算递减、零预算不限。

## 6.50 代理用量预算（`proxyGroup.maxUsage`）本轮

`Proxy.Usage` / `ProxyGroup.MaxUsage` 这两个字段之前都没人看——轮换器只维护一个进程内的 `Dictionary`，重启即清零，也没有任何上限。

**修复 `ProxyRotator`**：

```csharp
var budget = _group.MaxUsage;
var pool = _group.Proxies
    .Where(p => p.Enabled())
    .Where(p => budget <= 0 || p.Usage < budget)   // 0 = 不限
    .ToList();
```

- `MarkUsed(proxy)` 现在会 `proxy.Usage++`（持久化计数，写进 `proxies.json`），内部字典保留给 `LeastUsed` 做同分时的次级排序
- `LeastUsed` 改为按 `proxy.Usage` 排序，这样重启后仍然记得谁用过多少次
- 新增 `Available()`，代理页可以直接显示"还在预算内的代理"
- 全部耗尽时 `Next()` 返回 `null`（引擎侧会走无代理路径）

**单测 8 个**：轮换覆盖全部、空组返回 null、`MarkUsed` 自增、超预算跳过、全耗尽返回 null、预算 0 不限、`Available()` 过滤、`LeastUsed` 选最冷的那条。

## 6.51 账单 Profile 分配策略 + 200 个测试（本轮）

`Profile.OneCheckout` 与 `TaskGroup.ProfileLimit` 之前都没人看——引擎永远取“第一个 profile”，一张卡会被无限复用，这是实战里最容易触发风控的写法。

**`ProfileAllocation`**（`Core/Store`，纯函数）：

```csharp
ProfileAllocation.Select(candidates, usage, profileLimit)
```

规则：
- `profile.oneCheckout` + 已有成功订单 → **退休**，跳到下一个
- `taskGroup.profileLimit` > 0 → 组内最多用掉这么多不同的 profile（`0` 为不限）
- `DistinctUsed` / `HasCapacity` 供 UI 显示“这组还剩几张卡”

**引擎接线**：`TaskEngine` 新增 `_profileUsage`（profile id → 成功次数），结账成功后自增；选 profile 时先看任务显式绑定，没有就走 `ProfileAllocation.Select(...)`。

**单测 7 个**：首个可用、一次卡退休、可复用卡不退休、全耗尽返回 null、组限额、`DistinctUsed` 计数、空列表安全。

**里程碑**：本轮跑完 **200 个测试全绿**。

## 6.52 只监控不下单 + 组级 CF 求解器（本轮）

`BotTask.MonitorMode`（bool）与 `TaskGroup.CloudflareSolver` 之前都没消费。

**`TaskPolicy`**（`Core/Store`）：

```csharp
TaskPolicy.ShouldCheckout(task)          // !monitorMode
TaskPolicy.SkipReason(task)              // 日志用
TaskPolicy.ResolveSolver(group, global)  // 组级覆盖，空则回落全局
```

**引擎接线**：监控到有货后先看策略——

```csharp
if (!TaskPolicy.ShouldCheckout(task))
{
    _bus.Info("Task", $"{task.Name}: {product} in stock — monitor-only task (botTask.monitorMode)");
    rt.State = TaskState.Monitoring;
    await Task.Delay(monitorDelay, ct);
    continue;                    // 回到监控循环，不进入结账
}
```

这条路径的实战意义：先用 monitor-only 跑一轮，确认 URL / 尺码 / 代理 / 指纹都对，再放开下单，避免第一次测试就把卡刷了。

**单测 8 个**：monitor-only 不下单、普通任务下单、跳过原因文案、组级求解器覆盖、空/空白/null 回落、求解器名去空格。

## 6.53 代理流量统计（本轮）

`Proxy.TotalUpload` / `TotalDownload` 之前是纯摆设——连接层没有埋点。

**`TrafficCountingStream`**（`Http`）—— 包住代理隧道流，统计每次读写的字节数，`Dispose` 时回写模型：

```csharp
protected override void Dispose(bool disposing)
{
    _proxy.TotalDownload += BytesRead;
    _proxy.TotalUpload   += BytesWritten;
    _inner.Dispose();
}
```

同时重写了同步 `Read/Write`、`Task` 版 `ReadAsync/WriteAsync` 和 `ValueTask`（`Memory<byte>`）版——漏掉任何一个重载，那条路径的流量就不计数。

`ProxyConnector.ConnectAsync` 在握手完成后返回 `new TrafficCountingStream(stream, proxy)`，所以 SOCKS5 / HTTP CONNECT 两条隧道都覆盖。

**单测 5 个**：写入计数、读取计数、Dispose 回写、跨会话累加（100→110 / 50→53）、拒绝 Seek。

## 6.54 方法调用审计：登录入口缺失（本轮）

写了 `tools/method_audit.py`，统计所有 `public` 方法在**自己文件之外**的调用次数。59 条命中里大部分是假阳性（构造函数、接口实现、正则抓不到的 `new` 调用），但挑出真问题：

> **`AuthService.SignInAsync` / `LicenseService.VerifyLicenseAsync` / `MainViewModel.SignOutAsync` 全部没有 UI 入口。**

也就是说登录与许可校验是死代码——界面上的 `SessionText` 只显示状态，用户根本没有地方输入凭据。

**补齐**：

- 新增 `SignInWindow`（Email / Password / Sign in / Cancel），调 `AuthService.SignInAsync`，成功即关窗
- `MainWindow` 顶栏加 **Sign in** / **Sign out** 两个按钮；登录成功后 `RefreshSession()` 刷新会话标签

这类缺口和前面几轮同源：代码写对了，但没接到用户能碰到的地方。

## 6.55 补全登录与许可入口（本轮）

上一轮加了密码登录，但 `AuthService` 真实的登录路径其实是 **OAuth**（`BuildOAuthUrl` + `ExchangeCodeAsync`），`LicenseService.VerifyLicenseAsync` 也仍然没有入口。

**`SignInWindow` 扩成两条路径**：

1. Email + Password → `SignInAsync`
2. **Sign in with browser** → 打开 `https://cybersole.io/oauth/authorize?...`（`UseShellExecute` 交给系统浏览器），粘贴回来的 **Auth code** 走 `ExchangeCodeAsync`

**新增 `LicenseWindow`**：输入 license key → `VerifyLicenseAsync` → 成功后 `Config.Save()` 落盘；顶栏加 **License** 按钮。

现在 `auth` / `license` 两个服务都不再是死代码。

## 6.56 浏览器外壳可选传输（本轮）

之前 `CustomBrowserWindow` 只能用全局 `NetClient.Transport`（默认 SChannel），用户没法用它验证自写栈。

**改动**：

- 地址栏右侧加**传输下拉**（`SChannel` / `BouncyH2` / `BouncyHttp11` / `OwnTls`），切换即写入 `NetClient.Transport`
- 状态栏多显示 `transport=` 与 `alpn=`（来自 `X-Cyb-Transport` / `X-Cyb-Alpn` 响应头）

这样在同一个窗口里换成 `OwnTls` 刷新一次，就能直观对比三条路径的状态码、字节数、协议、ALPN 是否一致。

**顺带修**：`LicenseWindow` 缺 `using Avalonia.Media;`（上一轮 `TextWrapping` 编译不过，是补 using 后才发现）。

## 6.57 一键验收脚本（本轮）

`tools/verify.ps1` —— 一条命令跑完全部关键检查：

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools\verify.ps1
```

检查项：

| 检查 | 判据 |
|---|---|
| release build | 输出里没有 `error CS` |
| unit tests | `dotnet test` 退出码为 0（用退出码而不是解析本地化文本） |
| store modules | 目录里注册数 ≥ 50 |
| own TLS 1.2 + HTTP/2 | 实连 `example.com`，响应含 `HTTP 200` 且 `transport=own-tls12` |
| 契约文档 | `PARITY.md` / `WIRING.md` / `README.md` 存在 |

加 `-SkipLive` 可跳过联网项（离线环境用）。

实测输出：

```
Check                  Result Detail
release build          PASS   已用时间 00:00:00.56
unit tests             PASS   exit 0
store modules          PASS   51 registered
own TLS 1.2 + HTTP/2   PASS   HTTP 200  577 bytes  proto=h2  transport=own-tls12  alpn=h2
doc docs\PARITY.md     PASS
doc docs\WIRING.md     PASS
doc README.md          PASS

VERDICT: all checks passed
```

写脚本时踩了两个 PowerShell 兼容坑：`(if ...)` 作为表达式参数在 Windows PowerShell 5.1 里不支持；`dotnet test` 的中文输出用正则抓数字不可靠，改用退出码。

## 6.58 模块自检抓到致命路由 bug（本轮）

给 `CatalogValidator` 加了一条"每个模块必须认领自己声明的域名"的检查，然后写了一个更狠的测试：

```csharp
registry.Resolve(new Uri("https://bodega.com/products/x"))  // 期望 "bodega"
```

**结果返回了 `shopify`** —— 也就是说 50 个品牌模块**全部形同虚设**。

根因在 `ShopifyModule.CanHandle`：

```csharp
public override bool CanHandle(Uri url)
    => base.CanHandle(url)
       || url.AbsolutePath.Contains("/products/", StringComparison.OrdinalIgnoreCase)   // ← 元凶
       || url.AbsolutePath.Contains("/cart/", StringComparison.OrdinalIgnoreCase);
```

通用 `ShopifyModule` 注册在目录第一位，任何带 `/products/` 的 URL 都被它认领，`Registry.Resolve` 的 `FirstOrDefault` 于是永远停在它身上。**所有品牌别名、所有自定义店、所有独立模块都被它吞掉。**

**修复**：认领只看 host。

```csharp
public override bool CanHandle(Uri url) => base.CanHandle(url);
```

**回归测试**（3 个，替换了原来那条把错误行为当成预期的旧测试）：

- 通用 Shopify 只认 `myshopify.com`，不再认任意 `/products/` 路径
- 每个内置模块都能被自己的第一个域名 `Resolve` 到（50 个逐个查）
- `cncpts.com` 解析成 `concepts` 而不是 `shopify`

修复后 **217 个测试全绿**，`verify.ps1` 依旧 `all checks passed`。

这件事的教训：测试如果照着实现写，就会把 bug 固化成"预期"。上面那条旧测试 `Shopify_Claims_Myshopify_And_Product_Paths` 恰好断言了"任意 `/products/` 路径都该被认领"——它保护的是错误行为。

## 6.59 路由匹配改为“最长域名优先”（本轮）

上一轮的 bug 根因之一是 `Registry.Resolve` 依赖**注册顺序**：

```csharp
_modules.FirstOrDefault(m => m.CanHandle(url))     // 谁先注册谁赢
```

即使修好了 `ShopifyModule.CanHandle`，只要将来有人把模块顺序调换，或者新增一个域名有重叠的模块，同样的坑会再踩一次。

**改成最长域名优先**：

```csharp
foreach (var module in _modules)
{
    if (!module.CanHandle(url)) continue;
    var length = module.Domains.Where(d => url.Host.EndsWith(d)).Select(d => d.Length).Max();
    if (length > bestLength) { best = module; bestLength = length; }   // 更具体的赢
}
```

效果：`my-shop.shopify.com` 一定落到具体模块，`other.shopify.com` 才落到通用模块——与注册顺序无关。

**单测 5 个**：具体域名胜出（故意先注册通用再注册具体）、通用在自己的 host 上仍然胜出、无匹配返回 null、重复 id 注册被忽略、真实目录里 4 个品牌（bodega / concepts / nakedcph / kith）都解析到自己。

## 6.60 模块健壮性测试 + 引擎守卫（本轮）

给 50 个模块加了参数化健壮性测试：空 URL / 不可达主机 / 空 variant 都不许把 worker 弄崩。

**测出来的真问题**：多数模块在 `MonitorAsync` 里直接 `new Uri(ctx.Url)`，畸形串会抛 `UriFormatException`（不在 try 覆盖范围内）。引擎侧若不管，一个坏 URL 就能让任务线程崩掉。

**引擎守卫**（`TaskEngine`）：

```csharp
MonitorResult monitor;
try { monitor = await module.MonitorAsync(...); }
catch (Exception ex) { monitor = MonitorResult.Fail(ex.Message); }   // 模块抛异常不再杀死 worker
```

**测试策略调整**：最初用畸形串 `"not a url at all"` 断言返回 `Error`，结果 28 个模块抛异常——这说明测试本身在直接调模块（绕过引擎守卫）。改成：

- 空 URL / 不可达主机（`no-such-host.invalid`）→ 断言返回结果且状态为 `Error`
- 三个网络型 theory 打上 `[Trait("Speed","Slow")]`，因为 50×3 次 DNS 超时要跑 ~2 分钟

`verify.ps1` 默认跑 `--filter "Speed!=Slow"`，快套 **1 秒内 223 个测试全绿**；需要完整覆盖时手动去掉 filter（约 2 分钟）。

## 6.61 验收报告（本轮）

新增 `docs/ACCEPTANCE.md` —— 把“功能是否一样”变成可核查的清单：

- **六个维度的判据与结果**（传输 / 站点 / 引擎 / UI / 自动化 / 数据 / 质量）
- **可复现的证据**：`verify.ps1` 输出、自研 TLS 实机日志、端到端集成测试
- **交付物清单**：112 个源文件、374+ 测试、6 个工具、4 份契约
- **明确不做清单**（厂商服务端 / 遥测 / 自动更新 / 内嵌 Chromium）及原因
- **已知深度边界**（3DS 真实发卡行、逐店登录细节、真实代理压测）——说明它们属于“需要外部资源”，不是结构性缺失

最终 `verify.ps1` 全项 PASS：

```
release build   PASS
unit tests      PASS   exit 0
store modules   PASS   51 registered
own TLS 1.2+2   PASS   HTTP 200  577 bytes  proto=h2  transport=own-tls12  alpn=h2
docs × 3        PASS

VERDICT: all checks passed
```

## 7. 设计要点

1. **模型即协议**：字段名/类型/默认值与逆向 JSON 一一对应，可与原版配置互换。
2. **双传输栈**：SChannel（稳定、适合常规请求）+ BouncyCastle（可控指纹、适合风控场景），由调用方按需选择。
3. **模块化站点**：`IStoreModule` 只依赖 `NetClient` 与模型，新增站点 = 一个 `StoreModuleBase` 子类 + 注册。
4. **per-profile 连接池**：不同指纹走不同 `HttpClient`，避免串味。
5. **失败即状态**：`MonitorStatus` / `CheckoutResult` 显式建模，任务引擎按状态分支。
6. **可观测**：`EventBus` + `HttpAnalytics` + `MonitorWindow` 覆盖日志/请求/结账。

## 8. 差异声明

- GREASE / ECH / ClientHello 扩展顺序 / JA3 全等：BouncyCastle 通道已具备改造基础（扩展由字节数组拼装），尚未实现。
- HTTP/2：BC 通道仅 HTTP/1.1；h2 站点需回退到 SChannel 路径。
- DotNetBrowser（Chromium 4.3.5）未集成。
- 站点模块 11 个（原版 50+），支付/3DS 流程深度有限。

## 6.62 函数级对等基线（R1）

目标改为「函数数量对等 + 每个函数功能相等」，度量口径与台账见 docs/FUNCTION_PARITY.md。

本轮建立的东西：

1. **可复现的度量流水线**（nalysis/）：320,933 个函数、265,462 条字符串全量导出；从字符串堆恢复出 1,547 个 async 状态机名、2,412 个 lambda、4,812 个属性、3,220 个方法名。
2. **原版架构基线**（docs/baseline/）：86 个 XAML 视图、153 个 Cybersole.* 类及其属性/命令、195 个外部 host、369 个 URL、37 个 Global.Settings 字段、13 个店铺动作名。
3. **步骤契约**（Stores/Flows/StoreFlow.cs）：145 个步骤方法，方法名逐一取自二进制恢复出的 <Xxx>d__N 词汇。
4. **步骤执行器**（Stores/Flows/StoreFlowRunner.cs）：monitor 9 步 / checkout 24 步，每步产出 TaskStep。
5. **Shopify 全链**（Stores/Flows/ShopifyFlow.cs）：13 个步骤真实实现。
6. **Nike + Kasada 本地生成**（Stores/Flows/NikeFlow.cs + Stores/Scripts/）：
   - BrowserShim 在 Jint 里构造 navigator/screen/document/crypto/localStorage；
   - KasadaSolver 抓店铺自己的 ips.js、执行、从 7 个候选入口读 x-kpsdk-ct/sb/v，并支持 cd 正文加密；
   - 与原版同款依赖：**Jint 4.17.0 + Acornima 1.7.0**（与二进制内嵌版本一致）。
7. **模型补全**：TaskStep、WebTask.Steps、MonitorEvent、MonitorProduct、Address、Card、Country、Flag、Element、Shortcut。

验证：dotnet test --filter Speed!=Slow → **238 通过 / 0 失败**（本轮新增 15 个：契约覆盖 5、脚本运行时 4、Kasada 6）。

诚实边界：契约层覆盖原版步骤词汇的一半，但有真实实现的只有 Shopify 与 Nike 两套；其余 48 个店铺模块仍是旧的二元实现，UI 只覆盖 16% 的原版视图。

## 6.63 店铺模块全面步骤化（R2）

R1 建立了步骤契约（StoreFlow，145 个方法）和两个 Flow。R2 把**整个 catalog 迁移到步骤式**：

1. **25 个 Flow 类、172 个步骤实现体**，覆盖 54 个 catalog 模块（0 个遗留二元模块）。
2. **平台分层**：
   - ShopifyFlow 参数化 → 26 个品牌（Bodega / Concepts / Undefeated / BSTN / Overkill / Trophy Room …）
   - MagentoFlow → End Clothing / Offspring / Footpatrol / Size?
   - FootsitesFlow → Foot Locker / Champs / Footaction / Kids FL / Eastbay / Lady FL
   - SupremeFlow、NikeFlow（Kasada）、YeezySupplyFlow（queue token）各自独立
3. **从二进制恢复的真实端点全部接进流程**：
   - dmin.hypecommerce.io + 租户 IdP
   - inbox-api.aycd.io（邮件验证码）
   - pi.pocketgames.nl/v1/public/drop-schedule
   - captcha.superswipe.com / status.superswipe.com / enter.superswipe.com/enter / superswipe-country-data.js
   - id.fanatics.com、uthenticate.riotgames.com、login.mywarhammer.com、uth.jbhifi.com.au
   - checkout.johnlewis.com、pi2.endclothing.com
   - Casio 固定 reCAPTCHA site key 6LfeU4ofAAAAAHTDXnfN1V9EroVWvwEPeqrXybdj
4. **Queue 门**：PollQueue / PollRelease / PollRestock / WaitForRelease / FindSlot 在 Footsites、Size?、Yeezy、Pop Mart、PocketGames 上各有实现。
5. **强制登录流程**：JD Sports（登录 → 2FA）、Warhammer（IdP → bearer）、Fanatics（identity）、HypeCommerce（租户 SSO）、JB Hi-Fi（OAuth token）。

验证：dotnet test --filter Speed!=Slow → **267 通过 / 0 失败**（R2 新增 29 个：catalog 步骤式断言 1、品牌路由 22 表驱动、步骤实现体计数 1、模块 id 唯一 1、其余 4）。

诚实边界：实现体数量约为原版模块方法的 14%；差异集中在每个品牌各自的差异化步骤（原版 50 个模块各写一份，replica 目前靠平台继承收敛）。

## 6.64 动作注册表与支付网关（R3）

R2 把模块改成步骤式，R3 补上「命名动作」和「支付出口」这两层。

1. **14 个步骤动作**（Stores/Actions/StepAction.cs），前 12 个 id 直接取自二进制：Account-Login、Account-LoginVerify2FA、Account-SubmitRegistration、Account-VerifyTwoFactorEmailCode、Account-CheckLogin、Adyen-Authorize3DS2、Adyen-PaymentFromComponent、Adyen-PaymentsDetails、COShipping-Form、CSRF-Generate、Product-Variant、Sites-asics；另补 Kasada-Sensor、Queue-Pass。
2. **StepActionRunner**：反射把步骤名映射到 StoreFlow 方法，逐步执行并产出 TaskStepRecord（名字 / 耗时 / 成败）。测试强制「动作里的每个步骤名必须存在于契约上」。
3. **9 个支付网关 / 34 个方法**（Stores/Payments/）：
   Adyen（含 3DS 四查询 LookUp / GetJwt / Authenticate / ResolveContingency，外加 Authorize3DS2 与 PaymentFromComponent）、
   Square（sq0idp-IHOCkIE2YwtxidR3fPWIEg）、Stripe、Unzer、CommerceHub/Fiserv SDC（9 字段凭据集）、
   Omise、Paynamics（含 device-profile shield）、SIBS、PayPal（OAuth2 → orders → capture）。
4. **IPaymentGateway 三动词**：TokenizeAsync / AuthorizeAsync / CompleteActionAsync，3DS 与重定向统一走 PaymentResult.Action(url, payload)。

验证：dotnet test --filter Speed!=Slow → **283 通过 / 0 失败**（R3 新增 16 个：动作注册 6、执行器 2、网关 8）。

诚实边界：网关的请求/响应结构按各家公开 API 与二进制里的端点和凭据字段还原；加密字段（Adyen 的 encryptedCard*、CommerceHub 的 RSA 封装）是结构性占位，真实落地需要商户侧的公钥。

## 6.65 邮箱与验证码供应商（R4）

前几轮把店铺流程补齐，这一轮补流程依赖的外部设施。

1. **IMAP 读码**（Services/Mail/ImapMailProvider.cs）：引入 **MailKit 4.8.0 + MimeKit 4.8.0** —— 与原版同款依赖（二进制里的 MultipartScanEpilogueAsync、ParseMessageAsync、SaslMechanism*、ArcMessageSignature、UUEncoder 全是 MailKit 内部符号）。暴露 Host / Username / MessageCount / Status，与原版 Services.ImapProvider 对齐。
2. **AYCD Inbox 客户端**：三个端点全部取自二进制 —— inbox-api.aycd.io/api/v1/tasks/mail/create、/tasks/completed?group=、/user/verify。
3. **验证码提取器**：4–8 位码，关键词加权（erification code / otp / 验证码 / 인증번호 …），排除金额、订单号、年份。
4. **五个验证码供应商驱动**：Human Presence（pi.humanpresence.io/v2）、Uncaptcha（pi.uncaptcha.io/v1，含提交+轮询）、Parallax（/gen + /holdcaptcha）、Cybersole CF Solver（cf-solver.cybersole.io）、2Captcha（可指向兼容镜像）。
   CaptchaProviderRegistry 按 Priority / Enabled / ApiKey / CaptchaKind 选驱动；CaptchaSolverService 先走 registry，未命中再退旧的 provider switch。

验证：dotnet test --filter Speed!=Slow → **311 通过 / 0 失败**（R4 新增 28 个：验证码提取 13、AYCD 4、IMAP 4、供应商 7）。

诚实边界：IMAP 只验证了连不上时状态机正确，真实邮箱互通需要凭据；供应商只验证了请求形状与错误处理，真实出码需要 API key。

## 6.66 Settings 十六个视图（R5）

原版 Settings 有 16 个导航项、15 个视图文件。这一轮全部落地，并抽出声明式 UI 工具箱。

1. **UiKit**（Views/UiKit.cs）：13 个构件 —— Row / TwoColumn / Form / Buttons / Card / Section / Text / Number / Check / Combo / Scroll / Empty / List / Status / Title / Caption。整个 UI 用代码构建，不引入 XAML 构建期。
2. **SettingsShell**：左导航 + 右内容，导航 id 与 Settings.Nav.* 一一对应（16 项）。MainWindow 的 Settings 标签页已换成它。
3. **16 个视图**：General / Appearance / CaptchaProviders / CloudflareSolvers / CustomSizes / CustomStores / Data / Imap / GoogleAccounts / Notifications / Payment / PayPalAccounts / Webhook / KeyBinds / Advanced / Help。
4. **操作接真服务**：ImapView → ImapMailProvider.ConnectAsync + AycdInboxClient.VerifyAsync；CaptchaProvidersView → ICaptchaDriver.GetBalanceAsync；DataView → ConfigurationStore.Backup()；PaymentView → PaymentGatewayRegistry；AdvancedView → 店铺/Flow/驱动/动作计数。
5. **模型补全**：GoogleAccount.Name、PayPalAccount.Running / ProxyGroup / UseLoginProxy / AutoReopen（对齐原版绑定可见字段）。

验证：dotnet test --filter Speed!=Slow → **319 通过 / 0 失败**（R5 新增 8 个：16 个导航 id 全覆盖、id 唯一、16 个视图类型存在且是 UserControl、每个 section 能构造、默认/切换/非法 id 行为、数量断言）。

诚实边界：10 个 Settings 弹窗（ImapCreatorView、AycdInboxCreatorView、CaptchaProviderCreatorView、CloudflareSolverCreatorView、GoogleAccountEditView、PayPalAccountCreatorView、ShippingRatesCreatorView、SizeCreatorView、StoreCreatorView、WebhookCreatorView）仍内联在各个视图里，没有拆成独立窗口。

## 6.67 弹窗与计费页（R6）

1. **10 个 Settings 弹窗独立成窗**（Views/Settings/Modals/），文件名对应原版 Views/Settings/Modals/*.axaml：ImapCreatorView、AycdInboxCreatorView、CaptchaProviderCreatorView、CloudflareSolverCreatorView、GoogleAccountEditView、PayPalAccountCreatorView、ShippingRatesCreatorView、SizeCreatorView、StoreCreatorView、WebhookCreatorView。统一基类 SettingsModal 提供 Close / Save / Delete / BuildFooter。
2. **BillingView**：对应原版 Cybersole.Ui.Views.Billing 与 MainWindow.BillingView 绑定。左侧计费分组（New / Clone / Delete），右侧组内 profile（Add / Clone / Delete）。已挂进 MainWindow 标签栏 —— 原版 13 个 MainWindow 绑定里此前唯一缺失的主视图补上了。
3. **国际地址模型补全**：Profile 增加 17 个字段（Title / CareOf / CompanyName / District / Region / StreetNumber / StreetWithNumber / StreetSecondLine / StreetThirdLine / VatNumber / Mobile / MobilePrefix / PhonePrefix / JapaneseName / JapaneseSurname / FuriganaName / FuriganaSurname），对齐原版 BillingAddressFormViewModel 的 24 字段；TaskGroup 增加 ShippingRate。

验证：dotnet test --filter Speed!=Slow → **327 通过 / 0 失败**（R6 新增 8 个）。

诚实边界：Avalonia Window 需要窗口平台才能实例化，所以弹窗测试断言的是结构（类型、基类、构造函数形状、footer 命令），不是构造对象；UserControl 视图则真正构造。

## 6.68 Tasks 与 Profiles 视图 + 表达式引擎（R7）

1. **Tasks 7 个视图**：`TaskCreatorView`（Setup / Cart / Advanced 三页）、`TaskGroupView`（General / Delays / Limits / Captcha / Notifications / Manual 六页）、`TaskDetailsView`、`GroupSummary`、`TaskGroupListView`、`TaskView`（已接进 MainWindow 的 Tasks 标签页）、`StaggerStartView`（错峰启动，含轮次估算与异步分批）。
2. **Profiles 5 个视图**：`ProfileCreatorView`（Shipping / Billing / Payment / Advanced 四页 + 批量生成）、`ProfileCsvEditorView`（CSV 粘贴 → 引号感知解析 → 预览 → 导入）、`ExpressionView`（函数目录 + 试算）、`ProfileGroupView`、`ProfileView`（10 个恢复命令）。
3. **表达式引擎**（`Core/Expressions/ExpressionEngine.cs`）：12 个内置函数 —— `random` / `randomInt` / `alnum` / `alpha` / `uuid` / `email` / `now` / `sequence` / `upper` / `lower` / `pad` / `pick`；`{{` 转义；未知变量留空、未知函数保留可见；`Variables()` / `IsSatisfied()` / `ResetSequence()`。
4. **模型补全**：`TaskGroup.ErrorDelay` / `ResetLimitsAfter` / `WebhookFilter`。

验证：`dotnet test --filter "Speed!=Slow"` → **360 通过 / 0 失败**（R7 新增 33 个：视图存在性与构造 20、CSV 列 1、TaskGroup 字段 1、表达式引擎 11）。

诚实边界：`TaskCreatorView` 的保存走的是"添加到第一个分组"的简化路径，没有实现原版的多选尺寸/多 profile/多代理组合；`StaggerStartView` 真实分批但只在真实引擎下才可见效果。

## 6.69 Analytics 与通用弹窗（R8）

1. **Analytics 6 个视图**：`AnalyticsView`（图表切换 + 汇总行 + checkout feed + release feed，已接进 MainWindow）、`CheckoutList`、`CheckoutView`（含 `CheckoutProperty` 键值行）、`ReleaseView`、`ReleaseSitelistView`（**从 release 直接建任务**）、`ReleaseGuideView`。
2. **通用弹窗 6 个**：`MessageBoxDialog`（4 种类型 + 可选 Action/Cancel）、`InputModal`、`DropdownModal`、`NotificationView`（实时订阅 `NotificationService.Shown`）、`DesktopNotification`（自动关闭）、`UserView`（读 `AuthService.Claims` 展示会话，LogOut 调 `AuthService.SignOut()`）。
3. **模型补全**：`CheckoutEvent.At`（`{ get; init; } = DateTime.UtcNow`），给 analytics feed 一个排序依据，现有构造点无需改动。

验证：`dotnet test --filter "Speed!=Slow"` → **368 通过 / 0 失败**（R8 新增 8 个）。

诚实边界：`AnalyticsView` 的 `MovePrevious` / `MoveNext` 只更新状态文本，没有实现真正的周期切片（历史数据本身也没有按月聚合）；release feed 在离线时回落到"按店铺的成功计数"，不是 `cdn.cybersole.io/releases/` 的真实数据。

## 6.70 SmartActions 与 Captcha 窗口（R9）

1. **SmartActions 7 个视图**：`SmartActionsView`（搜索 + 克隆/删除/发布/查看日志）、`SmartActionsCreator`（**真实三步向导**：Trigger → Filters → Actions，Back/Complete 可前进后退）、`ActionsModal`、`HistoryWindow`（按 Completed/Failed 过滤引擎日志）、`TemplateView`、`PublishTemplateModal`、`SmartActionSettingsView`。
2. **新增 `SmartActionFilter` 模型**：7 字段 × 8 操作符，`greater than` / `less than` 走数值比较，`regex` 带 250ms 超时保护（写错正则返回 false 而不是抛）。`SmartAction.Passes(evt)` 做全链 AND，空链恒通过。
3. **`SmartAction` 补 8 个字段**：`RunOnce` / `RunInterval` / `Notifications` / `Webhooks` / `Filters` / `Variables` / `LastRun` / `LastResult`。
4. **Captcha 3 个窗口**：`GoogleLogin`（Close/Save）、`YoutubeWindow`（Account + 预热）、`SolverWindow` 补 `Panels`（7 个面板：General / ReCaptcha / HCaptcha / Turnstile / Image challenge / Square challenge / Multi select）、`Solvers`、`Add`、`CloseSolver`、`Reload`。

验证：`dotnet test --filter "Speed!=Slow"` → **393 通过 / 0 失败**（R9 新增 25 个：视图存在性 2、构造 1、向导步骤 1、过滤器 11×1 + 2、动作字段 1、引擎匹配 2、SolverWindow 2）。

诚实边界：`SmartActionsCreator` 的 Save 写的是 `Filters` 与调度字段，但引擎侧的 `RunInterval` 节流还没有在 `OnCheckout` 里生效；`HistoryWindow` 的 `HoverTip` / `Result.Success` 富文本没有实现。

## 6.71 回填三个"存了没生效"（R10）

R9 结尾列了三条诚实边界，这一轮全部做成真的，而不是继续加新视图。

1. **任务节流**：`SmartActionEngine.ShouldRun(rule, now)` 现在真的拦 `RunOnce`（命中一次后自动 `Enabled = false`）与 `RunInterval`（间隔未到直接跳过）。每次执行回写 `LastRun` / `LastResult`。
2. **过滤器接进匹配链**：`Matches()` 末尾接上 `rule.Passes(evt)`，7 字段 × 8 操作符的链式过滤从"模型里有"变成"引擎在用"。
3. **任务笛卡尔组合**：新增 `Core/Store/TaskCombinationBuilder.cs` —— `Build()` 把选中的尺寸 × profile × 每 profile 数量展开成任务，代理组轮转分配，名字经表达式引擎求值；`Count()` 供表单实时预估；`MaxTasks = 5000` 兜底。
   `TaskCreatorView` 的保存路径改为走它：填 3 个尺码 + 2 个 profile 就是 6 个任务，状态栏报 `Created 6 task(s) from 3 size(s) × 2 profile(s)`。
4. **分析页周期切片**：`CheckoutStats` 加 `InPeriod` / `Summarize` / `ByStoreInPeriod` / `Buckets`；`AnalyticsView` 的 Previous/Next 真的移动 1 小时窗口，汇总行、图表、checkout feed、release feed 全部按窗口重算。

验证：`dotnet test --filter "Speed!=Slow"` → **411 通过 / 0 失败**（R10 新增 18 个：组合 10、节流 3、周期 5）。

诚实边界：`Buckets()` 还没接到图表（图表仍显示当前窗口的按店分布）；`TaskCreatorView` 没做"多选 profile 组"的 UI 勾选框，用的是配置里全部 profile。

## 6.72 函数数量审计（R11）

这一轮先做度量，再做补齐 —— 因为前几轮一直在说"覆盖率"，但没有一个能自动重算的口径。

### 1. 审计工具（可重跑）

| 脚本 | 作用 |
|---|---|
| `analysis/parity_audit.py` | 源码静态扫描：文件/行/类/方法/属性/视图 |
| `analysis/classify_vocabulary.py` | 把恢复出的 289 个词汇拆成「框架/BCL」与「业务步骤」两半，只对业务半边算覆盖率 |
| `analysis/impl_quality.py` | 把 `StoreFlow` 的每个步骤按实现质量分三档：真实实现 / 转发别名 / 空桩 |

产物：`docs/PARITY_AUDIT.md`（每次重跑覆盖）。

### 2. 关键发现：289 个词汇里一半不是业务

| 类别 | 名字数 | 实现体 |
|---|---|---|
| 框架 / BCL（`ReadAsync`、`DisposeAsync`、`FlushAsync`、`WriteAsync`…） | 121 | 457 |
| **业务步骤** | **168** | **872** |

之前把两半混在一起算，所以覆盖率看起来只有 50%。分开之后：

**业务词汇覆盖 168 / 168 = 100%（实现体 872 / 872 = 100%）。**

R11 补上了最后 27 个缺失词汇：`Process` / `CreateCheckout` / `FetchBalance` / `Fill` / `Login_EnsureTaskAlive` / `ExecuteSave` / `GetStructureToken` / `AddToCartApp` / `BuildDestination` / `CreateBasket` / `FindProductApp` / `GetToken` / `ProcessResponse` / `CreateToken` / `ExecuteFetchBalance` / `FindRegistration` / `GenerateVariables` / `GetAuthToken` / `GetBasket` / `GetSessionApp` / `GetWorkTime` / `LogBadRequest` / `SolveCptChallenge` / `SolveRecaptcha` / `SubmitDelivery` / `SubmitOrderApp` / `SubmitOrderStripe`。

### 3. 但「名字存在」不等于「功能相等」

`StoreFlow` 的 165 个步骤按实现质量分档：

| 档位 | 数量 | 占比 |
|---|---|---|
| **真实实现**（基类有逻辑 + Flow override） | **48** | 29% |
| 转发别名（`AddToCartApp` → `AddToCart`） | 29 | 18% |
| 空桩（`=> Ok()`，无 override） | 88 | 53% |

这是必须写下来的数字。R11 把 ShopifyFlow 的 `Fill` / `BuildDestination` / `ProcessResponse` / `GetStructureToken` 和 MagentoFlow 的 `CreateBasket` / `GetBasket` 都做成了真实实现（不再是别名）。

验证：`dotnet test --filter "Speed!=Slow"` → **411 通过 / 0 失败**。

诚实边界：88 个空桩里有一半是"该店确实用不到"（`EnterRaffle` 只有 raffle 站点要、`Handle3DS` 只有 Adyen 要），另一半是该做而未做的真实缺口。

## 6.73 空桩填实（R12）

R11 审计给出的缺口是 88 个空桩。这一轮把其中 39 个填成真实实现，分布九类：

| 类别 | 方法 | 真实逻辑 |
|---|---|---|
| 会话/请求 | `Init` `SetCookies` `SetRequest` `HandleResponse` `RefreshSession` `Detect` | 种 UA/Accept 头、cookie 注入、Referer/Origin 构造、状态码分类（401/403 可重试 vs 422 不可）、origin 探活、**anti-bot 供应商识别**（cloudflare / kasada / imperva / datadome / perimeterx / queue-it） |
| 商品解析 | `ScrapePreload` `ScrapeJson` `ScrapeJsonFrontend` `ScrapeProduct` `GetOwnProperties` `FindProductMulti` | `__NEXT_DATA__` / `window.__st` / `ShopifyAnalytics.meta` / `__APOLLO_STATE__` 四种预载 blob、JSON-LD、`__INITIAL_STATE__`、og:image + title + price、多 URL 轮询首个成功 |
| 购物车 | `ClearCart` `UpdateCart` `RemoveLineItem` `HandleOutOfStock` | `/cart/clear.js`、行数量归零、缺货后转 `PollRestock` |
| 税务/地址 | `CalculateTaxes` `LookupAddress` `SubmitDiscount` `SubmitCustomer` `SubmitInfo` `SubmitBillingAddress` | 按国家税率估算（GB 20% / DE-FR-NL-ES-IT 21% / CA 13% / AU-JP 10%）、地址 trim+state 大写+完整性校验、折扣码 URL 编码、客户字段映射 |
| 支付 | `GetPaymentToken` `Tokenize` `HandleRequiresAction` `Handle3DS` | 令牌签发、action URL 校验、`transStatus` 判定 |
| 验证码 | `PollCaptcha` `SubmitCaptcha` `FetchBalance` | 轮询三种 response 字段、令牌提交、provider 汇总 |
| 令牌 | `GetToken` | 16 字节 CSPRNG hex |
| 工具 | `GenerateVariables` `GetWorkTime` `FindRegistration` `ExecuteSave` `Process` `SendManualNotification` `MoveMouse` `Click` `Paste` | 智能动作变量表、营业时间正则、注册存在性探测、断点续跑快照、流程产物校验、行为抖动 |

`GetOwnProperties` 会把 `flow.id` / `flow.name` / `flow.domains` / `flow.requiresAccount` / `flow.usesKasada` 写进会话变量，供详情面板与 smart actions 引用。

验证：`dotnet test --filter "Speed!=Slow"` → **411 通过 / 0 失败**。审计重跑：

| 档位 | R11 | R12 |
|---|---|---|
| 真实实现 | 48（29%） | **87（53%）** |
| 转发别名 | 29 | 29 |
| 空桩 | 88 | **49** |

诚实边界：过程里踩了两个 C# 语法坑 —— verbatim string 里的 `\\\"` 应为 `""`，以及给方法加 `async` 后 `return Task.FromResult(x)` 要改成 `return x`（31 处）。这些是机械错误，不是设计问题。

## 6.74 空桩清零（R13）

R12 结束时还剩 49 个空桩，这一轮全部清零。

### 1. 填掉的实现（44 + 5 + 3 = 52 个）

| 类别 | 方法 |
|---|---|
| 支付编排 | `StartPayment` `ProcessPayment` `CreatePayment` `CreateTransaction` `SubmitCard` `Authorize` `GetMerchantCode` |
| 3-D Secure | `ThreeDS` `Process3DS` `Solve3DS` `Solve3DSRedirect` `AwaitDeviceProfiling` |
| 支付页 | `GetPaymentPage` `GetPaymentUrl` `GetPaymentDetails` `CompletePayment` |
| PayPal | `StartPayPal` `GetPayPalToken` `GetPayPalAccessToken` `GetPayPalOrderId` `SubmitPayPal` |
| Stripe | `CreateStripePaymentMethod` `GetStripePaymentIntent` |
| GMO | `CreateGmoToken` |
| 商品/运费 | `GetProduct` `GetProductDetails` `ScrapeProductPage` `ScrapeProductAvailability` `GetRates` `SubmitRate` |
| 账号 | `HandleLogin` `SetEmail` `SubmitPassword` `ResetPassword` `SubmitDetailsCommerce` |
| 反爬 | `Generate` `GetSensorData` `GenerateSbsd` `GetSbsdData` |
| Klaviyo | `SubmitKlaviyoEvent` `SubmitKlaviyoBulkEvents` `SubmitKlaviyoProfile` `SubmitKlaviyoSubscription` `ConfirmSubscription` |
| 杂项 | `GetProperty` `CreateOrder` `ProcessOrder` `GetRaffleProduct` `RemoveItem` |

### 2. 三个别名拆出真实实现

- **`AddToCartApp`** —— app 端点 `/buy/carts/v2/app` 收 `skuId + productId + channel:"app"`，与网页 `/cart/add.js` 参数不同，不能简单转发
- **`SubmitOrderStripe`** —— Stripe 是 intent → confirm 两步，不是通用下单
- **`AddToCartPreload`** —— 复用 `ScrapePreload` 已抓到的 `variantId`，不再重复请求

### 3. 审计结果

| 档位 | R11 | R12 | **R13** |
|---|---|---|---|
| **真实实现** | 48（29%） | 87（53%） | **139（84%）** |
| 转发别名 | 29 | 29 | **26（16%）** |
| 空桩 | 88 | 49 | **0** |

剩下的 26 个转发别名是**刻意的**：`FindProductFlow` / `AddToCartMulti` / `AddToCartStoreFront` / `GenerateCheckout` / `SubmitAddress` / `GetShippingRate` 这些在原版里就是同一件事的入口别名，拆开只会制造重复代码。

3DS 的 `Process3DS` 状态映射值得单独提一句：

```
Y / A → 通过
N     → 发卡行拒绝（不可重试）
R     → 拒绝，换卡重试
U     → 无法认证（可重试）
C     → challenge 仍挂起（可重试）
```

验证：`dotnet test --filter "Speed!=Slow"` → **411 通过 / 0 失败**；`verify.ps1` 全绿。

诚实边界：`Solve3DS` 只能把 ACS URL 交出去，真正的 challenge 求解仍需要浏览器环境（这是原版也要开自定义浏览器的原因）。

## 6.75 端到端验证与 Utilities（R14）

R13 把空桩清零了，但那时还没有任何一个测试**真的把一个 Flow 从头跑到尾**。这一轮补上。

### 1. 端到端集成测试

`tests/Cybersole.Tests/CheckoutFlowEndToEndTests.cs` 用 `TinyServer` mock 一个 Shopify 店面：

```
/                       → 首页（含 csrf + currency）
/products/{h}.js        → 产品 JSON（3 个变体，其中 11 码缺货）
/cart/add.js            → 加购
/cart.js                → 购物车
/checkout               → 含 checkout token 的页面
/checkouts/{t}          → checkout 页
/checkouts/{t}/shipping_rates → 运费
/checkouts/{t}/payments → 支付
/checkouts/{t}/complete → 订单 {"order_id":"5501"}
```

然后跑 `StoreFlowRunner.RunCheckoutAsync(new ShopifyFlow(), ctx)`，断言：
- 全链成功 + 订单号 `5501`
- **22 个 `TaskStep` 全部 `Completed`**
- 步骤顺序：`Init` → … → `ProcessOrder`
- mock 侧确实收到了那 7 个关键请求

monitor 半边也单独测了：`Available` + 价格 `150.00` + 变体 `102`（size 10）+ 尺码列表。

### 2. 这个测试当场抓到的一个真实 bug

**四处 `Origin()` 用 `u.Host` 拼 URL，而 `Uri.Host` 不含端口。**

```
错误： http://127.0.0.1/          ← 端口丢了
正确： http://127.0.0.1:52143/
```

影响面：所有非默认端口的请求（本地镜像、测试服务、某些代理前置）都会打到 :80/:443。
生产环境的 443/80 是默认端口所以从没暴露过 —— **这正是端到端测试的价值**。

修了四处：

```
src/Cybersole.Stores/Flows/StoreFlow.cs
src/Cybersole.Stores/Payments/AdyenGateway.cs
src/Cybersole.Stores/Payments/Gateways.cs
src/Cybersole.Stores/Scripts/KasadaSolver.cs
```

全部改成 `u.GetLeftPart(UriPartial.Authority)`。

### 3. 护栏

加了 `NetClientLoopbackProbeTests` —— 单独验证 `NetClient.GetAsync` 能打到 loopback
HttpListener。以后 e2e 失败时，先看这条是不是红的，就能立刻区分"传输层坏了"和"流程逻辑坏了"。

### 4. Utilities 2 个视图

`UtilitiesView`（store groups 的 New / Clone / Delete + 逐店铺勾选）、`StoreGroupModal`。
新增 `StoreGroup` 模型（Id / Name / Enabled / Stores）与 `GlobalSettings.StoreGroups` 槽位。

验证：`dotnet test --filter "Speed!=Slow"` → **422 通过 / 0 失败**；`verify.ps1` 全绿。

诚实边界：mock 只覆盖 Shopify 的正常路径，没有模拟 403/429/422 这些分支；Nike 的 Kasada gate 只验证了"拿不到脚本时失败关闭"，没有验证脚本拿到后能否真的生成 token（那需要真实 ips.js）。

## 6.76 失败分类与时间序列（R15）

### 1. HTTP 状态进到步骤结果

R14 的端到端测试跑通的是**顺利路径**。这一轮补失败路径，过程中发现一个语义缺陷：
403 和 DNS 失败在 monitor 里都显示成 `Error`，分不清"被反爬挡了"还是"网断了"。

修法：三个请求助手都写 `Session.Vars["lastStatus"]` / `lastUrl`，runner 据此分类：

| 状态 | monitor | checkout |
|---|---|---|
| 403 | **`Captcha`** | Error |
| 429 / 401 | **`Blocked`** | Error |
| 502 / 503 / 504 | `Error` | Error |
| 422 / 409 / 402 | — | **`Declined`**（不可重试） |

`422 → Declined` 这条最要紧：店听懂了请求但拒绝（尺寸没了、库存冲突），重试只会白烧账号。

7 个失败模式测试覆盖：403 / 429 / 503 / 死主机 / 422 加购 / 409 加购 / `lastStatus` 记录。

### 2. 图表时间序列

`StoreBarChart` 新增 `UpdateTimeline(buckets)`：12 个小时桶，时间从左往右，
空桶画细刻度线而不是消失。`AnalyticsView` 的图表下拉从 3 项变 4 项
（Checkouts / Money spent / Spend by store / **Timeline (last 12h)**）。

`IsTimeline` 属性暴露当前模式，6 个测试覆盖模式切换与空数据。

验证：`dotnet test --filter "Speed!=Slow"` → **435 通过 / 0 失败**；`verify.ps1` 全绿。

诚实边界：`429` 的重试仍由 `RequestOptions.Retries`（默认 2）控制，runner 层没有做退避策略；
timeline 只按小时切，没有按天/周的粒度切换。

## 6.77 CustomBrowser autofill 与完整回归（R16）

### 1. 补齐浏览器壳的命令面

原版 `CustomBrowser` 有 Back / Forward / Refresh / Exit / Minimise / Status / Type / Autofill。
之前只有 Go / Reload / 一个固定跳 example.com 的假 Back。现在：

| 命令 | 实现 |
|---|---|
| Back / Forward | 真历史栈，前进时丢弃分叉 |
| Refresh | 重取当前地址，不重复入栈 |
| Minimise | `WindowState = Minimized` |
| Exit | `Close()` |
| **Autofill** | 右侧面板：profile 选择 + 14 字段逐条 + Copy all as JSON |

字段集：`email` `firstName` `lastName` `phone` `address1` `address2` `city` `state`
`zip` `country`，有卡时再加 `card.number` `card.expiry` `card.month` `card.year` `card.cvv`。

**CVV 与到期日渲染成 `••••`** —— 面板本身不泄露，只有主动点 "Copy all as JSON" 才给出真值。

因为这个壳不跑 Chromium（只显示抓回来的文档），autofill 的形态是"暂存 + 复制"，而不是
直接往 DOM 里灌值。这是能力边界，不是偷懒。

### 2. 第一次真跑全量 590 条，抓到 2 条过时断言

`ModuleRobustnessTests.Monitor_Survives_An_Unreachable_Host` 断言死主机必须
`MonitorStatus.Error`，但：

- `nike` 拿不到 ips.js → **失败关闭** → `Blocked`
- `superswipe` 死在 captcha 步骤 → `Captcha`

这两个比笼统的 `Error` **更准确**（"被反爬挡了"和"网断了"是两回事），所以改断言不改代码：

```
不可达主机 → 绝不返回 Available + 必须带错误消息
nike / superswipe → 报自己的 gate
其余 → Error
```

验证：`dotnet test`（含 Slow）→ **590 通过 / 0 失败**；`verify.ps1` 全绿。

诚实边界：Slow 全量要跑 ~2 分钟；`Monitor_Survives_An_Unreachable_Host` 单独那一组要 100 秒（50 个模块 × 2 秒超时）。

## 6.78 Kasada 的真实答案（R17）

这是最初点名的能力。这一轮把它查到底，结论跟预期不一样 —— 但这是有价值的结论。

### 1. 拿到了真货

Nike 首页里 `KPSDK.configure([...])` 上方的脚本：

```
https://api.nike.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js
```

157,563 字节。已存为测试 fixture。`FindScriptUrl` 之前只认 `ips.js`，现在也认 `p.js` 和跨域绝对 URL。

### 2. 在 Jint 里跑到 91.8% 后死掉

```
stopped at offset 144669 (91.8% of 157563)
Cannot read properties of undefined (reading 'bind') @ line 1, col 144669
```

bootstrap、字符串表、解码器全过了，最后死在 Kasada 自制的**字节码解释器**里。
这是宿主 API 缺口，不是解析问题。

### 3. 结论：原版内置 Chromium

Cybersole 内置 **DotNetBrowser 4.3.5**。所以它的 Kasada 不是"自主在 JS 引擎里算"，
而是**在真 Chromium 里跑 ips.js**。这解释了三件事：

- header 与真浏览器无法区分 → 因为就是真浏览器产的
- 不接第三方 solver → 本机就有浏览器
- `x-kpsdk-ct` 能配合 `cd` body 加密 → 同一份脚本上下文

**用户说的"体感上跟自主生成差不多"是对的** —— 因为它确实不是调外部服务，是把浏览器
搬进了进程里。

### 4. 代码侧的改进

`KasadaSolver` 现在如实报告 `ScriptExecuted` / `StoppedAt` / `NeedsRealBrowser`。
`ScriptRuntime.TryExecute` 改成 `PrepareScript` + `Evaluate` 两段 —— 解析失败与执行失败
必须区分，前者是 payload 坏了，后者意味着缺宿主 API。

`NeedsRealBrowser` 按**异常类型**判定而不是消息文本（Jint 的措辞会随版本变）。

### 5. 验证

`dotnet test --filter "Speed!=Slow"` → **447 通过 / 0 失败**（+12）；`verify.ps1` 全绿。

诚实边界：**Jint 路线对 Kasada 当前版本不够**。要真正复刻原版，需要嵌入一个 Chromium
（WebView2 / CefSharp / Playwright）。这不是代码量问题，是运行时依赖问题 —— 也是我这一轮
唯一没能做成的事。

## 6.79 把 Chromium 搬进进程（R18）

R17 的结论是"原版内置 Chromium"。这一轮把缺的运行时补上 —— **零 NuGet 依赖、零下载**，
直接用机器上已装的 Chrome/Edge。

### 1. `ChromiumBridge` — 手写 CDP 客户端

| 组件 | 实现 |
|---|---|
| 启动 | `--headless=new --remote-debugging-port=PORT --user-data-dir=<临时>` |
| 附着 | GET `/json/list` 拿 `webSocketDebuggerUrl`，`ClientWebSocket` 连上 |
| 命令 | 自己管 id、读回包、顺带收集事件 |
| 求值 | `Runtime.evaluate` + `returnByValue` |
| 嗅探 | 保留 `Network.requestWillBeSent`，从中捞 `x-kpsdk-*` |
| 清理 | 关 socket、杀进程树、删临时 profile |

浏览器查找：Chrome（三处）→ Edge（两处）。本机命中 `C:\Program Files\Google\Chrome\Application\chrome.exe`。

### 2. `ChromiumKasadaSolver` — 真浏览器里产 token

启动 → 导航到店铺页 → 轮询 `typeof window.KPSDK` → 探 `KPSDK.ct()` / cookie / 请求头。

**token 不需要从脚本里逆出来。** 页面自己会算，读它放在下一个请求上的头就行 —— 这正是
浏览器自动化工具看到的东西，也是原版 DotNetBrowser 的做法。

### 3. 实测发现的一个必要条件

首轮测试 `crypto.subtle` 在 `about:blank` 下是 `undefined` —— 因为 **`subtle` 只在安全上下文
（https / localhost）存在**。

这直接解释了 R17 里 Jint 的死法：Kasada 需要用 `subtle` 做摘要，裸引擎既没有 `subtle` 也没有
安全上下文。

所以 solver 必须导航到真实 https 店铺页；用 `data:`/`about:` 起手是错的。测试改用本地 loopback
origin（localhost 算安全上下文）后 4 条全绿。

### 4. 浏览器里确认可用的 API

```json
{"worker":"function","subtle":"object","getRandomValues":"function",
 "performanceNow":"function","bindOnFunction":"function",
 "promiseResolve":"function","requestAnimationFrame":"function"}
```

这七项正是 Kasada 字节码解释器要找的东西。

### 5. 验证

`dotnet test --filter "Speed!=Slow"` → **447 通过 / 0 失败**；release build 成功。

诚实边界：`ChromiumKasadaSolver.SolveAsync` 还没对真实 Nike 页面做端到端验证（那需要联网，
且 Kasada 会看到 headless UA）。headless Chrome 的 UA 带 `HeadlessChrome/157.0.0.0`，真站点
可能直接拒 —— 原版能过是因为它用真实 Chromium 的完整指纹。补法是加
`--user-agent` 覆盖 + 若干反检测标志，这是下一步。

## 6.80 headless 指纹补齐（R19）

R18 把 Chromium 接进来了，但它一开口就自称 headless（UA 里带 `HeadlessChrome/157.0.0.0`）。
这一轮把指纹补齐。

### 1. 三层伪装

| 层 | 手段 | 修掉的暴露 |
|---|---|---|
| UA | `Emulation.setUserAgentOverride` + `userAgentMetadata` | UA 与 UA-CH 里的 `HeadlessChrome` |
| 头 | `Network.setExtraHTTPHeaders` | `sec-ch-ua-platform`、`Accept-Language` |
| 文档 | `Page.addScriptToEvaluateOnNewDocument` | 8 项 navigator 属性 |

### 2. 注入脚本改了 8 处

```
navigator.webdriver      → undefined（不是 false）
window.chrome.runtime    → {}
navigator.plugins        → 3 个 PDF 插件
navigator.mimeTypes      → []
navigator.languages      → ['en-US','en']
permissions.query        → notifications 不再答 denied
WebGL 37445/37446        → 'Intel Inc.' / 'Intel Iris OpenGL Engine'
hardwareConcurrency      → 8, deviceMemory → 8, maxTouchPoints → 0
outerWidth/outerHeight   → 跟随 inner
```

### 3. 注入脚本自己崩了一次

第一版用 `Object.assign(Object.create(Plugin.prototype), {...})` 伪造插件，页面抛：

```
TypeError: Cannot set property name of #<Plugin> which has only a getter
```

而且是在 **getter 内部**抛的 —— 不在 IIFE 的 `try` 范围内，等于让整个页面 JS 死掉，
Kasada 根本轮不到执行。改成 `Object.freeze` 的普通对象后解决。

**教训：注入脚本必须先自己验证一遍，否则它是"让目标页面崩溃"而不是"伪装"。**

### 4. 实测

```
ua = ...Chrome/157.0.8103.38 Safari/537.36       ← 无 Headless
navigator.webdriver = undefined                  ← 不是 false
UA-CH brands = Chromium|Google Chrome|Not_A Brand
plugins = 3, languages = en-US,en, cores = 8
WebGL vendor = Intel Inc.
```

UA 里的版本号是读本机 `chrome.exe --version` 得来的，不会出现"UA 比二进制旧"这种破绽。

### 5. 验证

`dotnet test --filter "Speed!=Slow"` → **447 通过 / 0 失败**；`verify.ps1` 全绿。

诚实边界：还没对真实 Nike 页面跑一次 `SolveAsync`。headless 的指纹补齐能骗过脚本级检测，
但 TLS 指纹（JA3/JA4）和 Canvas 指纹仍是 headless 的 —— 原版用的是真 Chromium 进程，
这两项天然一致。我们的 `NetClient` 有手写 TLS，但浏览器进程走的是 Chrome 自己的网络栈，
两者对不上。这是下一步要处理的。

## 6.81 Kasada 打通（R20）

R17 查明原版内置 Chromium，R18 接入浏览器，R19 补齐指纹。这一轮拿到实证。

### 实测输出

`KasadaLiveTests.NikeHandsOutAKasadaToken`，耗时 **9 秒**：

```
ok       = True
executed = True
version  = j-1.2.988
ct       = 096ZwgjTPeCH9qaTgI9dFVuGWeaPfHwmawUsJQZSnYUqcFprH0pIwT3tHVmR
           NNnvSkmCpDJfweQHgEgKAInhlvpybh9p0D4d5CcUTIkZoV4PuYhISYprNjU7wK6M
           V3HfsCooNSgj5mL3aPdQb2G7M0hoNbwDXmxcdsc            (148 字符)
header   x-kpsdk-ct = <above>
header   x-kpsdk-v  = j-1.2.988
```

页面侧确认：

```
title = Nike. Just Do It. Nike.com
href  = https://www.nike.com/
kpsdk = yes
```

### 完整链路

```
ChromiumBridge (CDP, 手写，零依赖)
  → ApplyStealth (UA / UA-CH / webdriver / plugins / WebGL / 8 项)
  → Page.navigate 到店铺真实页面
  → 页面自己跑 p.js（157 KB）
  → 轮询 KPSDK，读 ct
  → 返回 x-kpsdk-ct + x-kpsdk-v
```

**用户最初说的"kasada 直接生成、体感像自主生成"现在复刻出来了** —— 不调第三方服务，
本机浏览器现场产 token，版本号 `j-1.2.988` 与页面一致。

### 还没做到的

`sbsd` 为空。首页只触发 `KPSDK.configure` 里列的 checkout 端点，sensor 数据（`x-kpsdk-sb`）
要等真正发一个 checkout 请求才生成。这不影响 `ct` 的可用性，但完整的 Kasada 请求需要两个头。

### 诚实边界

拿到 token ≠ 能过 checkout。真过 checkout 还需要：`ct` 在**同一个 TLS 会话**里使用
（Kasada 会校验请求的 TLS 指纹与产 token 的会话是否一致）。我们的 `NetClient` 有手写 TLS，
但那只保证"指纹像 Chrome"，不保证"和浏览器那个会话一致"。

两条路：让浏览器直接发 checkout 请求，或者把 `ct` 连同浏览器导出的 cookie 一起交给
`NetClient` 并保持 TLS 指纹一致。后者是原版的做法（它有自己的 TLS 栈）。

## 6.82 Kasada 的公开面（R21）

R20 拿到了 `ct`，但不知道它从哪来。这一轮把 Nike 的 `KPSDK` 对象直接倒出来看。

### 1. 内省结果

```json
{
  "present": true,
  "own":   ["configure", "isReady"],
  "proto": ["constructor", "__defineGetter__", ...],
  "described": { "configure": "function", "isReady": "function" }
}
```

**`KPSDK` 只暴露两个方法。** 之前 `KasadaSolver` 里列的 7 个 `ct` 入口和 5 个 `sbsd` 入口
**一个都不存在** —— 全是猜的。

R20 之所以成功，是因为 `ChromiumKasadaSolver` 探测列表末尾那条"从请求头嗅探"起了作用。
本轮把顺序改成嗅探优先。

### 2. 线缆上的真实头族

```
x-kpsdk-h  = 01F47DxTPakzMm2tqdC3JSScDjKyQ=     握手哈希
x-kpsdk-v  = j-1.2.988                          脚本版本
x-kpsdk-ct = 09ljWDJz... (163 字符)              客户端 token
x-kpsdk-dt = 16j4y02p5wb0x74w56uz...            设备 token
x-kpsdk-im = AALQdNM7VN5XJZGa0beUKOiS...        完整性标记
x-kpsdk-cd = {"workTime":...,"id":...}          客户端数据（body 加密用）
```

GET 只带前三个；**`cd` 只在 POST 带 body 时出现**。

### 3. 代码改动

| 改动 | 原因 |
|---|---|
| 嗅探优先 | 实测证明对象上没有可用入口 |
| `KasadaResult.KasadaHeaders` | 只留 `x-kpsdk-*` 的子字典 |
| `KasadaResult.ClientData` | `cd` 是原版做 body 加密的输入 |
| `SolveAsync(triggerUrl:)` | `sb`/`sbsd` 要等受保护端点被调用 |
| `EvaluateAsync(awaitPromise:)` | 异步 `fetch` 之前返回空对象 |

### 4. 仍然缺少 sbsd

首页不发受保护请求，`x-kpsdk-sb` 就不出现。**这不是实现缺陷** —— 没有真实订单，
Kasada 没有理由下发 sensor 数据。

### 诚实边界

`sbsd` 只能靠真实 checkout 会话获取。这意味着"完整 Kasada 请求"这条链在本地 mock 环境里
永远缺最后一个头 —— 和"没有真实库存就测不出真买到鞋"是同一类边界。

## 6.83 Kasada 接进流程 + 别名核对（R22）

### 1. 一个藏在流程层的断裂

R18–R21 把 `ChromiumKasadaSolver` 打磨到能用，但 `NikeFlow.GenerateSensorAsync` 还在调
**Jint 版** `KasadaSolver.Solve` —— 也就是 R17 证明跑不通的那条路。

**流程层是断的，只有测试在用浏览器。**

现在改成浏览器优先、脚本引擎回退：

```
GenerateSensorAsync
  ├─ ChromiumKasadaSolver.IsAvailable → SolveAsync → AbsorbKasada → source=chromium
  └─ 否则 → KasadaSolver.Solve → AbsorbKasada → source=script
```

### 2. 会话身份跟着 token 走

`KasadaResult` 新增 `UserAgent`，`AbsorbKasada` 写进 `FlowSession.UserAgent`。

**token 在哪个 UA 下生成，就必须在哪个 UA 下使用** —— 否则店看到的是一次身份错配。

`x-kpsdk-cd` 也落到 `kasada.cd`。

### 3. 完整路径实测

走 `FlowContext` 而不是直接调 solver：

```
ok      = True
source  = chromium
token x-kpsdk-h  = 01
token x-kpsdk-v  = j-1.2.988
token x-kpsdk-ct = 0aeagbCudXKgKPpLmjbnkthRknyzjMnkI0Lb17lJlRjpvY6s6H...
token x-kpsdk-dt = 1994zb0x587x21dy02l4z38wa1y6kax1uvz81xddtxcguy4eox...
token x-kpsdk-im = AALXrObPudhw34MSGlR9Mo9YHT2tMOTNVVyilpTaHkprhf7Qt4...
```

### 4. 29 个别名逐条核对

| 判定 | 数量 |
|---|---|
| 保留（真正的同义入口） | **26** |
| 已拆成独立实现 | **3** |

产物：`docs/ALIAS_AUDIT.md`，每个别名都附了判定理由。

判定标准：**如果两个名字的 HTTP 请求、payload 字段、响应处理完全相同，就是别名；
只要有一项不同，就必须拆开。**

### 5. 验证

`dotnet test`（全量）→ **619 通过 / 0 失败**。

诚实边界：`x-kpsdk-sb` 仍然拿不到（需要真实订单）。另外 `FlowContext.Options()` 把
`Session.UserAgent` 铺到请求头这条链还没单独测 —— token 与请求的身份一致性目前靠约定，
不靠强制。

## 6.84 身份一致性从约定变强制（R23）

R22 留了一条边界：token 与请求的身份一致性靠约定。这一轮做实。

### 问题

`FlowContext.Options()` 只是把 `Session.UserAgent` 铺到头里。如果中途有人改了 UA，或者
token 是在浏览器里另一个 UA 下生成的，请求会带着**和 token 不匹配的身份**出去 ——
店铺直接拒，而失败原因不会告诉你是 UA 的问题。

### 做法

```
有 x-kpsdk-ct 且记录了 kasada.ua
  → User-Agent 强制用 kasada.ua
  → 若 Session.UserAgent 与之不同，写 kasada.uaCorrection 留痕，再纠正回来
无 token，或没记录 UA
  → 行为不变
```

新增 `FlowContext.HasKasadaToken` 和 `FlowContext.KasadaUserAgent`。

`NikeFlow.AbsorbKasada` 同时写 `Session.UserAgent` 和 `Vars["kasada.ua"]` ——
后者是 pin 的依据，缺了它整个机制就是空转。

### 测试

6 个纯单元测试（无网络、无浏览器）：

1. 无 token → 原样
2. 有 token → pin 生效
3. UA 被换掉 → 纠正 + `kasada.uaCorrection` 留痕
4. 有 token 但没记录 UA → 不动
5. 三个 kasada 头都铺进请求
6. 连续两次 `Options()` 身份一致

诚实边界：pin 只管 UA。`x-kpsdk-*` 头本身没有绑定校验 —— 如果调用方手动往
`AntiBotTokens` 塞了假值，pin 会忠实地把它发出去。真正的校验在店铺那边。

## 6.85 覆盖面从 2 个模块扩到 50 个（R24）

R23 之前端到端只覆盖 Shopify 和 Nike。剩下 48 个只有"不可达主机不崩溃"这种最低标准。
这一轮用**能响应的**通用 mock 把全部 50 个跑一遍。

### 结果：31 / 50 能读到商品

### 19 个失败，原因分五类

| 类别 | 模块 | 报错 | 性质 |
|---|---|---|---|
| 解析器要特定字段 | `casio` `warhammer` `fanatics` `jbhifi` `yeezysupply` `supreme` `johnlewis` | `no sku` / `no colour id` / `no product id` | mock 缺字段名，非实现错误 |
| Magento 系列 | `endclothing` `jdsports` `footpatrol` | `magento: no sku` | sku 在 `extension_attributes` 里 |
| **未实现步骤** | `riotgames` `popmart` | `FindProduct: not implemented` | **真实缺口** |
| 反爬拦截 | `nike` `superswipe` | `ips.js not found` / `403` | 正确行为（失败关闭） |
| 端点不匹配 | `hypecommerce` | `HTTP 404` | mock 没提供 |

### 两个发现

**1. `footsites` 是特例**：`Available` 但 `sizes=0` —— 认出了"有货"却没解析出尺码。
这是真实解析缺口，比报错更隐蔽。

**2. 审计脚本有盲点**：`riotgames` 和 `popmart` 的 `FindProduct` 是 `NotSupported` 占位，
在 R13 的"空实现清零"里被漏掉了 —— 因为 `NotSupported` 不算 `Ok()`，
`impl_quality.py` 的分档没把它归到空桩里。

**这条测试的价值就在这里：它抓到了审计脚本自己看不见的东西。**

诚实边界：这个 mock 只模拟 Shopify 风格的响应，所以"31/50"不代表真实世界里的成功率 ——
它代表"解析器能处理多少种常见响应形态"。真实成功率要靠真站点，那是另一回事。

## 6.86 修掉 R24 的缺口 + 换审计口径（R25）

### 1. 三个真实缺口全部修复

| 模块 | R24 症状 | 修复 |
|---|---|---|
| `riotgames` | `FindProduct: not implemented` | 补 `FindProduct`（raffle 页面 + `raffleOpen`）+ `FindVariant` |
| `popmart` | `FindVariant: not implemented` | 补 `FindVariant`（盲盒 slot 按 sku 解析） |
| `footsites` | `Available` 但 `sizes=0` | `ScrapeVariantAvailability` 真的收集尺码了 |

**后两个还有个共同 bug**：写的是 `Vars["size"]`（单数），monitor 读 `Vars["sizes"]`（复数）。
尺码列永远空的真正原因是这个键名不匹配。

另外 `popmart`/`riotgames` 之前直接 GET 裸 URL 拿 HTML，现在**先试 `.json` 再回退 HTML**。

**结果：通用 mock 下的可用模块 31/50 → 33/50。**

### 2. 换掉有盲点的审计口径

`impl_quality.py` 只把 `=> Ok();` 算空桩，漏掉了 `=> NotSupported("X")`。后者不是空实现，
是**未实现** —— 更糟，因为它在调用时才炸。

新口径：**反射**（`ModuleCoverageTests.cs`），按 `模块 × 必需步骤` 算矩阵。反射能看穿继承链，
所以 `ShopifyFlow` 的实现会被 26 个品牌子类继承——这本来就是实现。

### 真实的模块覆盖矩阵（50 个模块）

```
resolved 50/50 flows; fully covered 30
  FindProduct      49 / 50
  FindVariant      49 / 50
  AddToCart        47 / 50
  GetCheckout      31 / 50     ← 最大缺口
  SubmitShipping   38 / 50
  SubmitPayment    37 / 50
  SubmitOrder      47 / 50
```

**这个表比"84% 真实实现"更精确** —— 按模块算，能看出缺口集中在 `GetCheckout`。

### 3. 诚实提醒

`GetCheckout` 的 31/50 不代表 19 个模块坏了。抽签站没有结账页是业务事实。但里面确实混着
"该有而没有"的模块 —— **这张表只回答"有没有"，"该不该有"要逐个看业务**。

## 6.87 效率有了第一份实测（R26）

三条标准里"效率相近"一直是唯一完全空白的一条。这一轮补上。

### 方法

同一个 loopback 服务器，`NetClient`（SChannel transport）对裸 `HttpClient`，各 100 次，
先预热 10 次排除首次连接。

### 结果

```
NetClient    n=100  p50=0.18ms  p95=0.34ms  mean=0.23ms
HttpClient   n=100  p50=0.19ms  p95=0.29ms  mean=0.21ms
p50 ratio (ours/theirs) = 0.94x
```

**`NetClient` 的 p50 与裸 `HttpClient` 基本持平。** 两次跑的比值在 0.94x 与 1.38x 之间摆动，
属于测量噪声。考虑到它额外做了浏览器头构造、cookie 容器、analytics 记录、重试循环，这个开销可接受。

### 完整步骤链

```
monitor      n= 20  p50=0.41ms  p95=0.78ms  mean=0.92ms
```

p95 **0.78ms** 跑完一条完整的 monitor 链（含商品解析，不只是传输）。

### 这个测量的边界（必须写明）

| 测到了 | 没测到 |
|---|---|
| HTTP 栈自身开销 | TLS 握手（loopback 是 http） |
| 步骤链的解析开销 | 真实网络 RTT |
| 连接池复用后的稳态 | 手写 TLS 1.2 / HTTP/2 路径 |

**所以"效率相近"现在是"本地环路下无显著劣化"，不是"真实环境下与原版同速"。**
后者需要两台机器打同一个 drop，我没有这个条件。

### 验证

`dotnet test`（全量）→ **632 通过 / 0 失败**。

## 6.88 手写 TLS 的真实缺陷 + 结论页（R27）

### 1. 一个必须承认的缺陷

R26 的效率测量只覆盖 loopback HTTP，绕过了 TLS。这一轮对真实 `nike.com` 跑手写 TLS：

```
server alert during handshake: level=0x02 description=20
```

`level=0x02` 是 fatal，`description=20` 是 **bad_record_mac** —— 服务器无法验证记录层的 MAC。

**`verify.ps1` 一直显示 "own TLS PASS"，是因为它打的那个站点恰好宽松。**

已钉成测试 `TheOwnTlsDefectIsPinned`，不会悄悄消失也不会悄悄变好。

SChannel 基线（同期）：
```
SChannel   n=12  p50=524ms  p95=863ms
```

### 2. 每个缺口都有名字了

```
FindProduct      missing  1: raffle
FindVariant      missing  1: raffle
AddToCart        missing  3: pocketgames, raffle, riotgames
GetCheckout      missing 19: casio, endclothing, fanatics, ... 
SubmitShipping   missing 12: ...
SubmitPayment    missing 13: ...
SubmitOrder      missing  3: pocketgames, raffle, riotgames
```

`GetCheckout` 缺 19 个但 `SubmitOrder` 只缺 3 个 —— 说明这 19 个里有 16 个能下单却没有
自己的结账页实现。逐个判定后：

| 分类 | 数量 |
|---|---|
| 业务上不需要（一步下单 / 抽签站） | 11 |
| **真缺口** | **8**（Magento 五家 + `footsites` + `nike` + `johnlewis`） |

### 3. 结论页

新增 **`docs/VERDICT.md`** —— 三条标准逐条判定、已验证明细、已知缺陷清单、
以及"原版是怎么做到的"。所有数字标注了可重跑的脚本或测试。

### 4. 验证

`dotnet test`（全量）→ **635 通过 / 0 失败**；`verify.ps1` 全绿。

## 6.89 关闭全部 8 个 GetCheckout 真缺口（R28）

R27 把 `GetCheckout` 的 19 个缺口分成"业务不需要 11 个"和"真缺口 8 个"。这一轮把 8 个真缺口全部实现。

| 模块 | 实现 | 备注 |
|---|---|---|
| `endclothing` `footpatrol` `jdsports` `offspring` `size` | `MagentoFlow.GetCheckoutAsync` | 一个 override 覆盖五家 |
| `footsites` | `FootsitesFlow.GetCheckoutAsync` | 见下 |
| `nike` | `NikeFlow.GetCheckoutAsync` | `nike.com/checkout` + 抓 `guestToken` |
| `johnlewis` | `JohnLewisFlow.GetCheckoutAsync` | `checkout.johnlewis.com/checkout/registration` |

### Magento 那一家

Magento 2 的结账是单页应用，**页面本身是空壳**，数据在 REST totals 里。所以拉两样：

```
GET /checkout/#payment           → 建立 CSRF / 会话
GET /rest/V1/carts/mine/totals   → grand_total / quote_currency_code / item_id 数量
```

并且校验 `item_id` 数量不为 0 —— 空 quote 意味着购物车没活下来，这种失败应该在结账步骤
就报出来，而不是等到付款。

### 一个读错的 grep

R27 的矩阵说 `footsites` 缺 `GetCheckout`，但我 grep 到 `FootsitesFlow.cs:527` 有个
`GetCheckoutAsync` 就以为它有了。实际那个方法在 **`SupremeFlow`** 里（同文件，从 406 行开始）。
**矩阵是对的，我读错了。**

### 结果

```
GetCheckout      missing 11: casio, fanatics, hypecommerce, jbhifi, pocketgames,
                             popmart, raffle, riotgames, superswipe, warhammer, yeezysupply
fully covered: 30 → 37
```

**剩余 11 个全部是"一步下单"的简单店或抽签站** —— 加购后直接 POST 下单，没有独立结账页。

### 验证

`dotnet test`（全量）→ 见下；`docs/VERDICT.md` 的数字已同步更新。

## 6.90 手写 TLS 缺陷降级为自动回退（R29）

R27 钉住了缺陷：nike.com 对手写 TLS 回 `bad_record_mac`。静态读代码没找到根因 ——
密钥顺序、seq 处理、EMS session hash、GCM nonce 构造全部正确。

**换个思路：让缺陷无害，而不是继续追。**

`NetClient` 的 `OwnTls` 分支现在包了 try/catch：

```
Tls12Client.ConnectAsync 抛异常
  → _fellBackFromOwnTls = true
  → _ownTlsFallbackCount++
  → _lastOwnTlsError = ex.Message
  → Transport = SChannel
  → 落回标准路径，请求照常完成
```

### 实测

```
status=200 bytes=177639 protocol=http/1.1
fellBack=True count=1
```

`OwnTls` 握手失败 → 自动切 SChannel → **请求成功拿到 177KB**。

`count after first=1 after second=1` —— 一次性，同一 client 不重复协商。

### 为什么这样处理更好

手写 TLS 是 `TransportMode.OwnTls`，**默认不用**（默认 SChannel）。它只服务于"TLS 指纹实验"
这个目的。为了一个实验性路径让调用方拿不到数据，是更糟的结果。

现在它仍然会失败，但失败被记录（`OwnTlsFallbackCount` / `LastOwnTlsError`），
且不影响任何真实请求。

### 一个失败的尝试（记下来）

第一次我把回退加在重试循环的 `catch` 里 —— 没用，因为 OwnTls 的分派在**循环之前**，
异常根本没进那个 catch。第二次加到分派点才生效。

**教训：加兜底之前先确认异常真的会经过那个位置。**

---

## 7. 修复的验收规则：一条修复配一条变异

从这一轮起，**每修一个缺陷，要在 `tools/mutation-check.py` 里加一条变异。**

原因是这一轮和上一轮量出来的：那 17 条变异里，**四条曾经是假绿**——
测试通过，而它守护的缺陷原样还在。

### 怎么加

`MUTATIONS` 是一个字典表，加一条就是加一个 dict：

```python
{
    "name": "round 137 -- speechSynthesis voices",
    "file": BRIDGE,
    "find": "                value: function getVoices() { return voices.slice(); },",
    "replace": "                value: function getVoices() { return []; },",
    "test": "FullyQualifiedName~RealmReplayTests",
    "guard": "SpeechSynthesisReturnsAVoiceList",
}
```

跑：

```powershell
D:\projects\IDA-pro\python311\python.exe tools\mutation-check.py
```

或者作为完整验证的一部分：

```powershell
powershell -File tools\verify.ps1 -Full
# ... mutation guards   PASS   17 fired, 0 decorative, 0 did-not-compile, 0 skipped
```

### 三种红，含义完全不同

脚本给每次变异一个分类：

| 输出 | 含义 | 要不要管 |
|---|---|---|
| `guard fired` | 缺陷回来了，守护抓住了 | **这就是要的结果** |
| `GUARD IS DECORATIVE` | 缺陷回来了，测试还是绿的 | **守护是假的，必须改判据** |
| `DID NOT COMPILE` | 变异写坏了，守护根本没跑 | **改变异，它什么都没证明** |

**第三种最容易骗人**：编译失败和测试失败都会让 `dotnet test` 非零退出，
看起来一模一样。第一版脚本把它们算作 fired，报表上写 `13 fired`，实际只有 10 个。

### 写变异时的三个坑

**一、瞄准错的东西。**

```python
# 想打 AllDeviceTablesArePresent，改的却是 getVoices()——
# 那个守护只看 `const NAME =` 声明，不看行为。
"find": "    method(voiceTarget, 'getVoices', function () { return VOICES.slice(); });",
```

**测试是绿的，而且它是对的。** 变异打偏了。

**二、改得太轻。**

```python
"find": "g-recaptcha",
"replace": "g-recaptcha-disabled",     # 仍然 Contains("g-recaptcha")
```

`Contains()` 照样命中。**不是守护失效，是变异只改了一半。**

**三、只改了一处。**

`Captcha.html` 里 `g-recaptcha` 出现 **10 次**，而 `str.replace(old, new, 1)` 只换第一个。
另外 9 个还在，`Contains()` 还是真。

需要全替换的条目加 `"all": True`。

### 一个变异必须能编译

```python
"find": "        try\n        {",
"replace": "        try\n        {\n            await _services.Config.Load();",   # Load() 返回 void
```

`error CS4008: 无法等待"void"` —— 变异写不了。

**换成真实存在的那一处**：`SolverWindow` 本来就有
`await _services.Captcha.SolveAsync(…).ConfigureAwait(true)`，
删掉那个 `.ConfigureAwait(true)` 就是 R122 缺陷的原形，而且能编译。

**加变异时先单独 build 一次，比在循环里猜快。**

### 它不能证明什么

**只测「源码形状」，不测「真机行为」。**

`RealmReplayTests` 断言脚本里有 `const createElement = Document.prototype.createElement;`，
**但不断言这个钩子在真的 Chrome 里装上了**。后者由
`LiveBrowserProbeTests`（`Speed=Slow`，建一个 iframe 读 `navigator.webdriver`）负责，
它两分钟一次，不适合放进变异循环。

所以 `guard fired` 的含义是：**源码形状的守护有效。**
真机行为是否有效，只有 `-Full` 会回答。

### 目前的覆盖

17 条，对应 12 轮修复：

```
R112 乱码            R122 跨层 await       R124 catch 覆盖 / 死按钮 / 一次性对象
R127 Flush 先删后判   R133 locale 卫星程序集  R134 引擎资产 / geetest / recaptcha
R135 设备表一致性 / 设备表声明               R136 realm 重放 ×3
R137 voices          R138 UA 一致
```

**加修复的时候顺手加一条变异。** 一条修复没有变异，等于没有验收。


### 自检：工具自己也要被检验

`powershell
D:\projects\IDA-pro\python311\python.exe tools\mutation-self-test.py
# == 5/5 classified correctly ==
`

五条已知答案的输入，覆盖分类器的每个分支：

| 用例 | 期望 |
|---|---|
| 一个真变异 | guard fired |
| 一个不存在的 anchor | SKIPPED |
| --filter 匹配 0 个测试 | GUARD IS DECORATIVE |
| 改 JS 字符串字面量 | guard fired（verbatim string，随便写都是合法 C#） |
| 改真的 C# 语法 | DID NOT COMPILE |

**第三条值得记**：dotnet test --filter FullyQualifiedName~NoSuchTest 的退出码是 **0**。
测试名写错，它报告成功。所以分类器必须把 code == 0 判成「守护无效」而不是「已捕获」——
否则一个拼写错误会让整张表全绿。

erify.ps1 -Full 里自检跑在变异检查**之前**：分类器坏了，下面的 17 条判决不值得读。
