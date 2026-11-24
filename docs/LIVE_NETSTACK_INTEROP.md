# `Cybersole.Http` 纯 C# QUIC / HTTP/3 / TLS 栈互操作与线上实测记录（`full-QUIC/HTTP3/TLS`）

> **所属分支**：`full-QUIC/HTTP3/TLS`（`main` 分支锁定在 `288a95e1d3fa4cb85d61d12cd5e55affcc33bd82` 未修改）
> **性质**：纯托管安全 C# 传输栈（`TransportMode.PureNetClient`）针对**第三方生产级实现（Go 1.26.2 + `quic-go@v0.61.0` + `x/net/http2`）**与**公网真实站点**（严格校验证书 `InsecureSkipVerify = false`，使用内嵌 `RootCertificates.bin`）的线级与协议级实测档案。

---

## 1. 可复现测试命令

在仓库根目录执行（注意先检查本机可用内存 `available >= 2 GB`，所有 `dotnet` 命令保持 `-m:1`）：

```powershell
$env:PATH="D:\tools\dotnet8;$env:PATH"
$env:DOTNET_ROOT="D:\tools\dotnet8"

# 1) 离线指纹 + 单元 + Go 1.26.2 / quic-go v0.61.0 第三方互操作测试（72/72）
dotnet test replica/tests/Cybersole.Tests/Cybersole.Tests.csproj -m:1 --filter "FullyQualifiedName~WireFingerprintTests|FullyQualifiedName~QuicHttp3Tests|FullyQualifiedName~TlsStackTests|FullyQualifiedName~ProtocolLayerTests|FullyQualifiedName~PureNetClientIntegrationTests|FullyQualifiedName~NetClientProtocolParityTests|FullyQualifiedName~ThirdPartyQuicTlsInteropTests" --logger "console;verbosity=normal"

# 2) 公网真实边缘与指纹 Oracle 互操作测试（[Trait("Speed", "Slow")]，17/17，含境内 UDP-443 多代 1-RTT 主动 KeyUpdate + 兼容海外 H3 胜出与境内 TUN 回退）
dotnet test replica/tests/Cybersole.Tests/Cybersole.Tests.csproj -m:1 --filter "FullyQualifiedName~LivePublicEdgeInteropTests" --logger "console;verbosity=detailed"

# 3) 海外直连 UDP-443 专项 HTTP/3、ALPS 0x44CD、PSK 复用、HTTP/3 指纹 Oracle、QPACK 动态表、多代主动 KeyUpdate 与 QUIC Retry 测试（11/11，须在海外无 UDP-443 拦截节点执行；已于 ba1d7c0 在 IAD VPS 全量 11/11 通过，详见 docs/OVERSEAS_QUIC_H3_VALIDATION.md）
dotnet test replica/tests/Cybersole.Tests/Cybersole.Tests.csproj -m:1 --filter "FullyQualifiedName~LiveOverseasHttp3InteropTests" --logger "console;verbosity=detailed"
```

---

## 2. 本轮发现并修复的真实协议 / 指纹 / 资源缺陷

每一项均在复刻件修复后补充了离线确定性回归测试（未降低任何断言或放宽证书校验）：

| # | 问题与根因 | 修复文件与符号 | 离线回归测试 |
|---|---|---|---|
| 1 | **HTTP/2 `ConnectionFlow` 双重减 `65535`**：`Http2Connection` 在连接级别流控误从 `ConnectionFlow` 再扣一次 `65535`，与原版 `sub_1412CA520` / `sub_14136CAA0`（IDA 实证 `*(v3 + 192)` 原值发 stream-0 `WINDOW_UPDATE` 且接收窗口 `+65535`）不符，导致 Akamai H2 指纹窗口增量偏小 | `Http2Connection.cs` (`ConnectionFlow` 发射与初始窗口)、`WireFingerprint.cs`、`ProtocolLayerTests.cs`、`WireFingerprintTests.cs` | `BuiltInProfiles_ProduceDeterministicSortedJa4AndExactAkamaiH2`、`Chrome133_NegotiatesH2CleanlyOverTcpWhenServerSelectsH2` |
| 2 | **`QuicConnection.DisposeAsync` 非幂等**：二次释放重复写关闭帧或抛异常 | `QuicConnection.cs` (`_disposed` 幂等守卫) | `QuicHttp3Tests` + `ThirdPartyQuicTlsInteropTests` |
| 3 | **QUIC 直连与竞速 DNS/IPv4 一致性**：`ProtocolRacer` 异步并行探测时直连 UDP 未共享 `DnsCache` 且偏好序未优先 IPv4 | `QuicConnection.cs` (`QuicConnectionOptions.DnsResolver`)、`ProtocolRacer.cs` (`ConnectH3Async`)、`Socks5UdpTransport.cs` (`OrderAddressesPreferIPv4`) | `ProtocolRacer_DualWinsHttp3_And_UdpBlackholeFallsBackToHttp2` |
| 4 | **TLS 1.3 HRR（HelloRetryRequest）违背 RFC 8446 §4.1.2 / §5.1**：收到 HRR 后未设置 `_negotiatedVersion`/`_suite`，`ClientHello2` 外层记录版本用了 `Tls10`（应为 `0x0303` `Tls12`），且重建时重排了扩展序 / 重新抽取了 GREASE 值 | `TlsHandshakeEngine.cs` (`HandleHelloRetryRequest`)、`TlsClientHelloBuilder.cs` (`SpecOverride` 在 HRR 下保留 `MaterializedSpec`) | `Tls13HrrWithChrome150_AcceptsMiddleboxCcs_UsesTls12RecordVersion_AndPreservesGreaseAndOrder`、`GoTls13_Chrome150_P256OnlyServer_ForcesHelloRetryRequestAndSucceeds` |
| 5 | **QUIC 1-RTT Key Update `"quic ku"` 误轮换 `HpKey` 及 `ack_delay` 编码指数**：Go `quic-go` 在 ~PN 100 触发 `KeyPhase 0 -> 1` 时，`QuicKeySet.UpdateKeys()` 改写了原本不随密钥更新变化的 header protection 密钥 `HpKey`（RFC 9001 §6.1），导致后续双向 1-RTT 包解密全部失败；出站 `ACK` 的 `ack_delay` 亦需使用 `(int)_spec.AckDelayExponent` | `QuicCrypto.cs` (`QuicKeySet.UpdateKeys` 保持 `HpKey` 不变)、`QuicConnection.cs` (`_appPrevReadKeys` 先行尝试解密 + `_spec.AckDelayExponent`) | `QuicGoV061_Http3_ZeroScid_NoSyntheticUa_FlowControl512KB_And_ConcurrentStreams`、`QuicHttp3Tests` (`HpKey` gen0→gen1→gen2 不变性) |
| 6 | **TLS 1.3 ALPS（`0x44CD` / `0x4469`）握手失败**：Google 等 BoringSSL 服务端在 `EncryptedExtensions` 回显 `application_settings` 时要求客户端在 `Finished` 前发送 10 字节空 `EncryptedExtensions`（`08 00 00 06 00 04 <codepoint> 00 00`）并纳入 `Client Finished` transcript；缺少该消息导致对端返回 `UnexpectedMessage (10)`，同时无 ALPN 携带 ALPS 须抛 `IllegalParameter` | `TlsHandshakeEngine.cs` (`_peerAlpsCodepoint` / `_peerAlpsSettings` / `PeerApplicationSettings`、TCP & QUIC 发送客户端 `EncryptedExtensions` 并入 transcript) | `Tls13Alps_TcpAndQuic_SendsClientEncryptedExtensionsBeforeFinishedAndVerifiesTranscript` (`chrome_150` `0x44CD` & `chrome_133` `0x4469`)、`Tls13Alps_WithoutAlpn_ThrowsIllegalParameter`、`LiveGoogle_And_NginxQuic_SucceedWithPureCSharpTls13` |
| 7 | **HTTP/3 3 条单向流限额边缘 GREASE 死锁（`6f223b21`，海外 IAD VPS 实测发现）**：Cloudflare（`one.one.one.one`、`cloudflare-quic.com`）与 NGINX（`quic.nginx.org`）按 RFC 9114 §6.2 最小值通告 `initial_max_streams_uni = 3`；此前发送 GREASE 的预设先开 Control → GREASE → QPACK Encoder，导致第 4 条必需的 QPACK Decoder 流永久阻塞超时（30s） | `Http3Connection.cs` (`StartAsync` 先开 3 条关键流 Control `0x00` / QPACK Encoder `0x02` / QPACK Decoder `0x03`，仅 `_quic.PeerMaxStreamsUni > 3UL` 时开 GREASE 流) | `Http3StartAsync_PeerAllowsOnly3UniStreams_OpensCriticalStreamsWithoutDeadlockingOnGrease` |
| 8 | **RFC 9001 §8.3 QUIC `EndOfEarlyData` 摘要污染（`6f223b21`，海外 IAD VPS 实测发现）**：`HandleTls13ServerFinished` 此前在 `if (!isQuic)` 外无条件调用 `AppendTranscript(eoed)`，在 QUIC 复用且服务端接受 `early_data` 时污染握手 transcript | `TlsHandshakeEngine.cs` (`HandleTls13ServerFinished` 收紧为 `if (!isQuic && _earlyDataAccepted && _clientEarlyTrafficSecret is not null)`) | `Tls13EarlyDataAccepted_InQuicMode_OmitsEndOfEarlyDataFromTranscriptPerRfc9001Section83` |
| 9 | **`EarlyData`（`0x002A`）严格对齐原版与 HRR ClientHello2 剥离（RFC 8446 §4.1.2）**：IDA 实证原版 `sub_141298620` / `sub_141298FA0`（`0x141299381`）仅在 `canOfferPsk`（`a3`）为真且预设含 `EarlyDataExtension`（仅 `ChromeQuicSpecs`）时发射 `0x002A`（不检查 `MaxEarlyDataSize > 0`），且 `sub_141298420`（`0x141298589..0x1412985DC`，谓词 `0x141337520`）在 HRR `ClientHello2` 中移除 `EarlyDataExtension`；同时 `sub_14129F560` 与 `sub_1412A0820` 在 QUIC 下不派生 `"c e traffic"`、不发 `EndOfEarlyData` | `TlsClientHelloBuilder.cs` (`OfferedEarlyData` 与 `offerEarlyData = canOfferPsk && !isHrrRetry`)、`TlsHandshakeEngine.cs` (`!isQuic && _clientHello!.OfferedEarlyData`、`HandleEncryptedExtensions` 校验 `OfferedEarlyData`) | `TlsClientHello_EarlyData_MatchesOriginalCybersolePskAndStripsOnHelloRetryRequest` |
| 10 | **`QuicConnection.InitiateKeyUpdate()` 违反 RFC 9001 §6.2 并发写/读双翻与缺少握手确认/在途门禁**：此前 `InitiateKeyUpdate()` 在无握手确认检查、无单次在途检查下同时翻转 `_appWriteKeys` 与 `_appReadKeys`，导致发起后在途旧相位对端包解密失败且允许连续多次 KeyUpdate 错配；现仅在 `_handshakeConfirmed` 且 `_writeKeyPhaseGeneration == _readKeyPhaseGeneration` 时只轮换写密钥并暴露 `WriteKeyPhaseGeneration`/`ReadKeyPhaseGeneration`/`ClientInitiatedKeyUpdates`/`PeerInitiatedKeyUpdates`/`WaitForHandshakeConfirmedAsync` | `QuicConnection.cs` (`InitiateKeyUpdate`、短头收包 `_appReadKeyPhase` 递增计数器、`_handshakeConfirmedTcs`) | `QuicConnection_ClientInitiatedKeyUpdate_PreservesInFlightOldPhasePackets_And_GuardsBackToBackUpdates`、`QuicGoV061_ClientInitiatedKeyUpdate_MultiGeneration_CompletesHttp3` |
| 11 | **`Http3Connection` QPACK 解码器流 `KnownReceivedCount` 并发竞态溢出（RFC 9204 §4.4.3）**：`DecodeHeadersSerializedAsync` 发送 `SectionAcknowledgment`（隐式推进编码端 `KnownReceivedCount`）与 `HandleServerQpackEncoderStreamAsync` 发送 `InsertCountIncrement` 之间缺乏共享 `_sentQpackKnownReceivedCount` 上限，多流并发解码动态表段时可先发送 `SectionAcknowledgment` 再追加全额 `InsertCountIncrement` 导致对端 `KnownReceivedCount > InsertCount` 报错；现统一在 `_decoderWriteLock` 内追踪 `_sentQpackKnownReceivedCount` 并只发增量 `currentInsertCount - _sentQpackKnownReceivedCount` | `Http3Connection.cs` (`_sentQpackKnownReceivedCount`、`_decoderWriteLock` 串行化、`Qpack*` 诊断属性)、`QpackCodec.cs` (`QpackDecoder.InsertCount` / `DynamicEntryCount` / `BuildInsertCountIncrement`) | `Http3Connection_QpackDecoderStream_NeverOverflowsKnownReceivedCount_UnderConcurrentSectionAck` |

---

## 3. 离线第三方生产栈互操作矩阵（Go 1.26.2 + `quic-go@v0.61.0` + `x/net/http2`）

夹具：`replica/tests/Cybersole.Tests/TestFixtures/QuicGoServer/{go.mod,go.sum,main.go}`（使用本地 Go 模块缓存离线编译）与 `ThirdPartyQuicTlsInteropTests.cs`（8/8 通过）。

| 用例 | 验证协议与场景 | 结果 |
|---|---|---|
| `GoTls13_Chrome150_MlKem768_MatchesWireClientHelloAndAkamaiH2` | TCP + `X25519MLKEM768` + HTTP/2 PREFACE/SETTINGS 与线级 `ClientHello` 比对 | ✅ 通过 |
| `GoTls13_Chrome150_P256OnlyServer_ForcesHelloRetryRequestAndSucceeds` | Go 服务端仅配置 `CurveP256` 强制触发 TLS 1.3 HRR + middlebox CCS 后完成 H2 | ✅ 通过 |
| `GoTls13_Chrome150Psk_SessionResumption_SetsDidResumeTrueOnSecondConnection` | Go TLS 1.3 `NewSessionTicket` 签发后第二次连接 PSK 恢复（`didResume=true`） | ✅ 通过 |
| `QuicGoV061_Http3_ZeroScid_NoSyntheticUa_FlowControl512KB_And_ConcurrentStreams` | UDP `quic-go v0.61.0`、`scidLen=0`、无伪造 UA、并发流与 512 KB 传输触发 `KeyPhase 0->1` Key Update | ✅ 通过 |
| `QuicGoV061_VerifySourceAddress_ForcesQuicRetryPacket_AndCompletesHttp3` | `VerifySourceAddress: true` 强制服务端发 QUIC `Retry` 包携带令牌重启握手并完成 HTTP/3 | ✅ 通过 |
| `QuicGoV061_ClientInitiatedKeyUpdate_MultiGeneration_CompletesHttp3` | `chrome_152` 握手确认后客户端主动发起多代 1-RTT KeyUpdate（`0->1->0`，`wGen>=2` / `rGen>=2` / `cliKu=2`）并校验 `SHA-256` 往返一致 | ✅ 通过 |
| `ProtocolRacer_DualWinsHttp3_And_UdpBlackholeFallsBackToHttp2` | `ProtocolRacer` 在双栈端口优先竞速胜出 `HTTP/3`，在 UDP 静默黑洞下平滑回退 `HTTP/2.0` | ✅ 通过 |

---

## 4. 公网真实站点与指纹 Oracle 实测矩阵（17/17 通过，`InsecureSkipVerify = false`）

以下结果为 `LivePublicEdgeInteropTests` 实测（`2026-11-24`），所有 TLS/QUIC 连接均启用 `UseEmbeddedDefaultRoots = true`（内嵌 `RootCertificates.bin`）做严格证书链与主机名校验。

### 4.1 第三方指纹 Oracle 实测（`tls.peet.ws/api/all` 与 `tls.browserleaks.com/json`）

| Profile | 观测端点 | `JA4`（本地 vs 远端） | `JA4_r` | `Akamai H2` | 说明 |
|---|---|---|---|---|---|
| `chrome_150` | `tls.peet.ws` | `t13d1516h2_8daaf6152771_806a8c22fdea` ✅ | 完全一致 ✅ | `1:65536;2:0;4:6291456;6:262144\|15663105\|0\|m,a,s,p` ✅ | 启用扩展乱序；`JA4` / `JA4_r` / `Akamai H2` 全一致 |
| `chrome_150_PSK` | `tls.peet.ws` | `t13d1516h2_8daaf6152771_806a8c22fdea` ✅ | 完全一致 ✅ | `1:65536;2:0;4:6291456;6:262144\|15663105\|0\|m,a,s,p` ✅ | 同上 |
| `chrome_152` | `tls.peet.ws` | `t13d1517h2_8daaf6152771_cb7bf5808d99` ✅ | 完全一致 ✅ | `1:65536;2:0;4:6291456;6:262144\|15663105\|0\|m,a,s,p` ✅ | 含自定义扩展 `0xCA34` 与签名算法 `0904,0905,0906` |
| `chrome_133` | `tls.peet.ws` | 远端 `t13d1516h2_8daaf6152771_d8a2da3f94cd`；本地 `t13d1516h3_...` ✅ | 加密套件 + 扩展哈希完全一致；原始 ALPN 扩展实测含 `["h3","h2","http/1.1"]` ✅ | `1:65536;2:0;4:6291456;6:262144\|15663105\|0\|m,a,s,p` ✅ | IDA `0x141353E20` / `sub_141337470` 实证 `Chrome_133` `ClientHello` 默认带 `["h3","h2","http/1.1"]`；`peet.ws` 在 TCP 连接上将 `ja4[8..10]` 归一化为 `h2` |
| `firefox_148` | `tls.peet.ws` | `t13d1917h2_4d8ed5baf28e_3cbfd9057e0d` ✅ | 完全一致 ✅ | `1:65536;2:0;4:131072;5:16384\|12517377\|0\|m,p,a,s` ✅ | 未乱序；**`JA3_hash` 精确一致 `992b82b242c18c86da84eff5bf3e3100`** |
| `chrome_150` | `tls.browserleaks.com` | `t13d1516h2_8daaf6152771_806a8c22fdea` ✅ | 完全一致 ✅ | `52d84b11737d980aef856699f885ca86` ✅ | text + hash 全一致 |
| `chrome_152` | `tls.browserleaks.com` | `t13d1517h2_8daaf6152771_cb7bf5808d99` ✅ | 完全一致 ✅ | `52d84b11737d980aef856699f885ca86` ✅ | text + hash 全一致 |

### 4.2 公网真实边缘 TLS 1.3 + HTTP/2 + HTTP/3（直连 UDP-443 与竞速回退）

| 目标 URL | 通道 / 测试 | 实测结果 |
|---|---|---|
| `https://one.one.one.one/cdn-cgi/trace` | `PureNetClient` TCP+TLS 1.3+H2 | `200`, `http=http/2`, `tls=TLSv1.3`, `kex=X25519MLKEM768` ✅ |
| `https://cloudflare-quic.com/` | `ProtocolRacer`（本地 TUN 拦截海外 UDP-443 后自动回退） | `200`, `HTTP/2.0`, `alt-svc=h3=":443"; ma=86400`, `125959 B` ✅ |
| `https://www.google.com/generate_204` | `PureNetClient`（验证 ALPS `0x44CD` 修复） | `204`, `HTTP/2.0`, `alt-svc=h3=":443"; ma=2592000,h3-29=":443"; ma=2592000` ✅ |
| `https://quic.nginx.org/` | `PureNetClient` TLS 1.3+H2 | `200`, `HTTP/2.0`, `alt-svc=h3=":443"; ma=86400`, `2523 B` ✅ |
| `https://www.nike.com/` / `https://www.akamai.com/` | `NetClient { Transport = TransportMode.PureNetClient }` | `nike.com`: `200` (`963493 B`, `server=unified-edge-router`)；`akamai.com`: `200` (`225354 B`) ✅ |
| `https://www.taobao.com/` / `https://www.tmall.com/`（`chrome_152` 多代主动 KeyUpdate + QPACK 探针） | **`QuicConnection` + `Http3Connection` 直连公网 UDP-443** | **两站均 4/4 请求 `200 HTTP/3`，两代客户端主动 KeyUpdate（`0->1->0`）全通：`wGen=2, rGen=2, cliKu=2, srvKu=0`；淘宝/天猫实测 `qpack=(ins=0,known=0,entries=0,dynSections=0)`** ✅ |
| `https://www.taobao.com/` | **`QuicConnection` + `Http3Connection` 直连公网 UDP-443** | **`200`, `HTTP/3`, `alpn=h3`, `cipher=0x1302`, `scidLen=0`, `93269 B`** ✅ |
| `https://www.tmall.com/` | **`QuicConnection` + `Http3Connection` 直连公网 UDP-443** | **`200`, `HTTP/3`, `alpn=h3`, `cipher=0x1302`, `scidLen=0`, `108760 B`** ✅ |
| `https://dns.alidns.com/resolve?name=example.com&type=A` | **`QuicConnection` + `Http3Connection` 直连公网 UDP-443** | **`200`, `HTTP/3`, `alpn=h3`, `cipher=0x1301`, `scidLen=0`, `253 B` JSON (`"Status":0`)** ✅ |
| `https://www.apple.com.cn/` / `https://www.aliyun.com/` | `ProtocolRacer`（`DisableHttp3 = false`） | `apple.com.cn`: `200`, `HTTP/2.0`, `145111 B`；`aliyun.com`: `200`, `HTTP/2.0`, `252227 B` ✅ |

> **对照组实证（排除 `Cybersole.Http` 假阴性）**：使用官方参考实现 Go `quic-go@v0.61.0` 对同一组境内边缘直连 UDP-443 探测，结果与 `Cybersole.Http` 一致：`www.taobao.com` / `www.tmall.com` / `dns.alidns.com` 均成功返回 `HTTP/3 200`，而 `www.apple.com.cn`（`context deadline exceeded` / QUIC `28: Reject connection`）、`www.aliyun.com`（`CRYPTO_ERROR 0x150: handshake failed`）与 `www.douyin.com`（`CRYPTO_ERROR 0x128`）在官方 `quic-go@v0.61.0` 下同样由服务端拒连或超时，属服务端策略所致而非 `Cybersole.Http` 实现缺陷；`ProtocolRacer` 对 `apple.com.cn` 与 `aliyun.com` 均已实测验证平滑回退 `HTTP/2.0` 返回 `200`。

### 4.3 海外直连公网 VPS 实测矩阵（美国东岸 IAD，无代理拦截，完整档案见 `docs/OVERSEAS_QUIC_H3_VALIDATION.md`）

测试环境：美国东岸 IAD 公网 VPS（Windows Server 2022，`.NET 8.0.428`，`Go 1.27.4`，出口 `104.254.189.209`，UDP-443 直连无代理拦截），最终全量复验提交 `ba1d7c03d03ecfe77989b45828864316b9c33194`（全部连接严格校验证书 `InsecureSkipVerify = false` + `UseEmbeddedDefaultRoots = true`）：

- **阶段 1（离线 + Go/`quic-go@v0.61.0`）**：**`72/72` 全部通过**（`11.52 s`）。
- **阶段 2（`LivePublicEdgeInteropTests`）**：**`17/17` 全部通过**（`6.74 s`）；`cloudflare-quic.com`（`200 HTTP/3`, `125,959 B`, `75 ms`）与 `www.aliyun.com`（`200 HTTP/3`, `157,055 B`, `452 ms`）均由 `ProtocolRacer` 竞速胜出 `HTTP/3`，`www.apple.com.cn` 平滑回退 `200 HTTP/2.0`（`145,111 B`）；`www.taobao.com`/`www.tmall.com` 多代主动 KeyUpdate 均 `wGen=2 rGen=2 cliKu=2`；`tls.peet.ws`（5 预设）与 `tls.browserleaks.com`（2 预设）的 `JA4` / `JA4_r` / `Akamai H2` 与本地 `WireFingerprint` **100% 一致**。
- **阶段 3（`LiveOverseasHttp3InteropTests`）**：**`11/11` 全部通过**（`22.77 s`）：

| 目标 / 用例场景 | 通道与预设 | 实测结果与线级观测（`ba1d7c0`） |
|---|---|---|
| `https://one.one.one.one/cdn-cgi/trace` | 直连 H3 & `ProtocolRacer` (`chrome_150`) | 均 `200 HTTP/3`，返回体含 `http=http/3`、`tls=TLSv1.3`、`kex=X25519MLKEM768`（`scidLen=0`, `cipher=0x1301`, `peerUni=3`, `hs=27.4 ms`）；单连接 8 并发流 `29 ms` ✅ |
| `https://cloudflare-quic.com/` | 直连 H3 & `ProtocolRacer` (`chrome_150`) | 均 `200 HTTP/3` 完整 `125,959 B`（`hs=23.4 ms`）；单连接 8 并发流满额 `1,007,672 B`（`370 ms`） ✅ |
| `https://www.google.com/generate_204` | 直连 H3 & `ProtocolRacer` (`chrome_150`) | 均 `204 HTTP/3`；公网真实 QUIC 路径实测确认 Google 下发 ALPS `0x44CD`（`len=182`）且客户端完成 ALPS `EncryptedExtensions` 握手（`hs=21.5 ms`） ✅ |
| `https://quic.nginx.org/` | 直连 H3 & `ProtocolRacer` (`chrome_150`) | 均 `200 HTTP/3`（`2,523 B`, `peerUni=3`, `hs=110.5 ms`） ✅ |
| `https://www.nike.com/` | 直连 H3 vs `PureNetClient` / `ProtocolRacer` | 直连 UDP-443 报 `QuicException: 200:internal error`（与同节点 `quic-go@v0.61.0` 对照组 `CRYPTO_ERROR 0x150 (remote): 200:internal error` 一致，属服务端策略）；`NetClient(PureNetClient)` 与 `ProtocolRacer` 均干净回退 `HTTP/2.0` 返回 `200`（`~1.08 MB`） ✅ |
| `https://www.akamai.com/` | 直连 H3 / `ProtocolRacer` / `NetClient` | 裸 UA 同 `quic-go` 对照组均获 `403`（`368 B` WAF）；携带完整 Chrome 导航头后三路均稳定 `200 HTTP/3`（`225,533 B`, `cipher=0x1302`） ✅ |
| QUIC PSK 会话复用 | `chrome_150_PSK` + `ChromeQuicSpecs` | `one.one.one.one`（`200 HTTP/3, resumed=True, hs=17.0 ms`）与 `www.google.com/generate_204`（`204 HTTP/3, resumed=True, hs=15.7 ms`）均成功复用 ✅ |
| HTTP/3 指纹 Oracle（`https://fp.impersonate.pro/api/http3`） | `chrome_150` & `chrome_152` | 均 `200 HTTP/3`，`initPn=0`, `scidLen=0`, `dcidLen=8`, `ja3n=36b3da67265214a919829c5e959f7425`，15 项 QUIC Transport Parameters、伪头顺序 `m,a,s,p` 与 `ChromeQuicSpecs`/本地 `WireFingerprint` 完全一致；`chrome_152` 发送完整 SETTINGS（`1:65536;6:262144;7:100;51:1;GREASE`），`chrome_150` 按 `sub_1412B05A0` 仅发 `51:1` ✅ |
| **公网 QPACK 动态表多请求并发**（`Overseas_Chrome152_QpackDynamicTable_MultiRequest_PublicEdges`） | 直连 H3 (`chrome_152`, 4 串行 + 6 并发) | **4/5 公网边缘真实触发动态表插表与解码**：Google `ins=76,known=76,entries=76,dynSections=10`；YouTube `ins=72,known=72,entries=72,dynSections=10`；LiteSpeed `ins=19,known=19,entries=19,dynSections=9`；Facebook `ins=105,known=105,entries=105,dynSections=10`（Cloudflare `peerQpack=(0,0)` 未启用） ✅ |
| **公网三节点多代 1-RTT 主动 KeyUpdate**（`Overseas_ClientInitiatedKeyUpdate_MultiGeneration_CloudflareGoogleNginx`） | 直连 H3 (`chrome_152`, `phase 0→1→0`) | `one.one.one.one`、`www.google.com/generate_204`、`quic.nginx.org` 三节点全部 `wGen=2, rGen=2, cliKu=2, srvKu=0` 且 3 轮请求全 2xx（`494 ms`） ✅ |
| **公网 IETF QUIC Retry 实测**（`Overseas_PublicQuicRetryEndpoints_VerifyRealRetryTokenAndHttp3`） | 直连 H3 (`chrome_152`, 严格 X.509) | **3 个独立公网实现实测 Retry 通过**：`quic.aiortc.org:4434` (`retry=True, token=73B, 0x1302, 200`)、`quic.tech:8444` (`retry=True, token=30B, 0x1301, 200`)、`nghttp2.org:4434` (`retry=True, token=90B, 0x1301, 200`)；`test.privateoctopus.com:4434` 自签证书被严格校验正常拒收；`http3-test.litespeedtech.com:4434` 8000 ms 超时 ✅ |

---

## 5. 诚实的 `Unknown` 与环境边界

> **已全部实测闭环的原 Unknown（截至 `ba1d7c0` 海外 IAD VPS `100/100` 全绿）**：
> - 海外直连 UDP-443 QUIC/HTTP/3（Cloudflare / Google / NGINX / Akamai / YouTube / LiteSpeed / Facebook）、Google QUIC ALPS `0x44CD`（`len=182`）、Cloudflare `X25519MLKEM768`、QUIC PSK 会话复用、第三方 HTTP/3 线级指纹 Oracle（`fp.impersonate.pro/api/http3`）；
> - **公网真实边缘 QPACK 动态表高频插入与并发解码**（Google `76` / YouTube `72` / LiteSpeed `19` / Facebook `105`，均 `ins == known == entries`）；
> - **公网真实边缘 1-RTT 客户端主动多代 KeyUpdate**（Cloudflare / Google / NGINX / 淘宝 / 天猫 5 个公网边缘均 `wGen=2, rGen=2, cliKu=2`）；
> - **公网真实边缘 QUIC `Retry` 包与 Retry Token**（`quic.aiortc.org:4434` / `quic.tech:8444` / `nghttp2.org:4434` 3 个独立 IETF 实现严格证书校验下 `retry=True` + `200 HTTP/3`）；
> - **0-RTT 应用数据包** 经 IDA 实证原版 `Cybersole.exe`（`sub_1412A0820` / `sub_14129F560`）从不派生 `"c e traffic"` 或发送 0-RTT 应用包，按原版行为不适用/已结案。

剩余边界（诚实保留，不夸大）：

1. **公网长连接服务端主动发起 1-RTT KeyUpdate（`Unknown`）**：本轮所有公网连接短生命期内均为客户端主动轮换（`srvKu=0`）；服务端主动触发 `KeyPhase 0→1` 密钥更新已由本地 Go `quic-go@v0.61.0` 夹具（~PN 100 触发）验证通过，公网边缘被动触发保持 `Unknown`。
2. **③-A 嵌入式浏览器宿主选型**：仍为 `docs/NETSTACK_ADR.md` 唯一待裁决议程（`DotNetBrowser 4.3.5.8591` vs WebView2 vs CEF），不随本网络栈支线越权替代裁决。
