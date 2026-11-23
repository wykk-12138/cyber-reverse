# `Cybersole.Http` 纯 C# QUIC / HTTP/3 / TLS 栈互操作与线上实测记录（`full-QUIC/HTTP3/TLS`）

> **所属分支**：`full-QUIC/HTTP3/TLS`（`main` 分支锁定在 `288a95e1d3fa4cb85d61d12cd5e55affcc33bd82` 未修改）
> **性质**：纯托管安全 C# 传输栈（`TransportMode.PureNetClient`）针对**第三方生产级实现（Go 1.26.2 + `quic-go@v0.61.0` + `x/net/http2`）**与**公网真实站点**（严格校验证书 `InsecureSkipVerify = false`，使用内嵌 `RootCertificates.bin`）的线级与协议级实测档案。

---

## 1. 可复现测试命令

在仓库根目录执行（注意先检查本机可用内存 `available >= 2 GB`，所有 `dotnet` 命令保持 `-m:1`）：

```powershell
$env:PATH="D:\tools\dotnet8;$env:PATH"
$env:DOTNET_ROOT="D:\tools\dotnet8"

# 1) 离线指纹 + 单元 + Go 1.26.2 / quic-go v0.61.0 第三方互操作测试（66/66）
dotnet test replica/tests/Cybersole.Tests/Cybersole.Tests.csproj -m:1 --filter "FullyQualifiedName~WireFingerprintTests|FullyQualifiedName~QuicHttp3Tests|FullyQualifiedName~TlsStackTests|FullyQualifiedName~ProtocolLayerTests|FullyQualifiedName~PureNetClientIntegrationTests|FullyQualifiedName~NetClientProtocolParityTests|FullyQualifiedName~ThirdPartyQuicTlsInteropTests" --logger "console;verbosity=normal"

# 2) 公网真实边缘与指纹 Oracle 互操作测试（[Trait("Speed", "Slow")]，16/16，严格 TLS 验证）
dotnet test replica/tests/Cybersole.Tests/Cybersole.Tests.csproj -m:1 --filter "FullyQualifiedName~LivePublicEdgeInteropTests" --logger "console;verbosity=detailed"
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

---

## 3. 离线第三方生产栈互操作矩阵（Go 1.26.2 + `quic-go@v0.61.0` + `x/net/http2`）

夹具：`replica/tests/Cybersole.Tests/TestFixtures/QuicGoServer/{go.mod,go.sum,main.go}`（使用本地 Go 模块缓存离线编译）与 `ThirdPartyQuicTlsInteropTests.cs`（7/7 通过）。

| 用例 | 验证协议与场景 | 结果 |
|---|---|---|
| `GoTls13_Chrome150_MlKem768_MatchesWireClientHelloAndAkamaiH2` | TCP + `X25519MLKEM768` + HTTP/2 PREFACE/SETTINGS 与线级 `ClientHello` 比对 | ✅ 通过 |
| `GoTls13_Chrome150_P256OnlyServer_ForcesHelloRetryRequestAndSucceeds` | Go 服务端仅配置 `CurveP256` 强制触发 TLS 1.3 HRR + middlebox CCS 后完成 H2 | ✅ 通过 |
| `GoTls13_Chrome150Psk_SessionResumption_SetsDidResumeTrueOnSecondConnection` | Go TLS 1.3 `NewSessionTicket` 签发后第二次连接 PSK 恢复（`didResume=true`） | ✅ 通过 |
| `QuicGoV061_Http3_ZeroScid_NoSyntheticUa_FlowControl512KB_And_ConcurrentStreams` | UDP `quic-go v0.61.0`、`scidLen=0`、无伪造 UA、并发流与 512 KB 传输触发 `KeyPhase 0->1` Key Update | ✅ 通过 |
| `QuicGoV061_VerifySourceAddress_ForcesQuicRetryPacket_AndCompletesHttp3` | `VerifySourceAddress: true` 强制服务端发 QUIC `Retry` 包携带令牌重启握手并完成 HTTP/3 | ✅ 通过 |
| `ProtocolRacer_DualWinsHttp3_And_UdpBlackholeFallsBackToHttp2` | `ProtocolRacer` 在双栈端口优先竞速胜出 `HTTP/3`，在 UDP 静默黑洞下平滑回退 `HTTP/2.0` | ✅ 通过 |

---

## 4. 公网真实站点与指纹 Oracle 实测矩阵（16/16 通过，`InsecureSkipVerify = false`）

以下结果为 `LivePublicEdgeInteropTests` 实测（`2026-11-23`），所有 TLS/QUIC 连接均启用 `UseEmbeddedDefaultRoots = true`（内嵌 `RootCertificates.bin`）做严格证书链与主机名校验。

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
| `https://www.taobao.com/` | **`QuicConnection` + `Http3Connection` 直连公网 UDP-443** | **`200`, `HTTP/3`, `alpn=h3`, `cipher=0x1302`, `scidLen=0`, `93269 B`** ✅ |
| `https://www.tmall.com/` | **`QuicConnection` + `Http3Connection` 直连公网 UDP-443** | **`200`, `HTTP/3`, `alpn=h3`, `cipher=0x1302`, `scidLen=0`, `108760 B`** ✅ |
| `https://dns.alidns.com/resolve?name=example.com&type=A` | **`QuicConnection` + `Http3Connection` 直连公网 UDP-443** | **`200`, `HTTP/3`, `alpn=h3`, `cipher=0x1301`, `scidLen=0`, `251 B` JSON (`"Status":0`)** ✅ |
| `https://www.apple.com.cn/` / `https://www.aliyun.com/` | `ProtocolRacer`（`DisableHttp3 = false`） | `apple.com.cn`: `200`, `HTTP/2.0`, `145111 B`；`aliyun.com`: `200`, `HTTP/2.0`, `252227 B` ✅ |

> **对照组实证（排除 `Cybersole.Http` 假阴性）**：使用官方参考实现 Go `quic-go@v0.61.0` 对同一组境内边缘直连 UDP-443 探测，结果与 `Cybersole.Http` 一致：`www.taobao.com` / `www.tmall.com` / `dns.alidns.com` 均成功返回 `HTTP/3 200`，而 `www.apple.com.cn`（`context deadline exceeded` / QUIC `28: Reject connection`）、`www.aliyun.com`（`CRYPTO_ERROR 0x150: handshake failed`）与 `www.douyin.com`（`CRYPTO_ERROR 0x128`）在官方 `quic-go@v0.61.0` 下同样由服务端拒连或超时，属服务端策略所致而非 `Cybersole.Http` 实现缺陷；`ProtocolRacer` 对 `apple.com.cn` 与 `aliyun.com` 均已实测验证平滑回退 `HTTP/2.0` 返回 `200`。

---

## 5. 诚实的 `Unknown` 与环境边界

1. **海外边缘（Cloudflare / Google / Nike / `quic.nginx.org`）直接 UDP-443 HTTP/3**：当前执行主机经本地 TUN 代理转发海外流量且静默丢弃海外 UDP-443，因此海外公网 HTTP/3 真实链路**无法在该网络环境下直接观测（标 `Unknown`）**；`ProtocolRacer` 从被阻断 UDP-443 回退 `HTTP/2.0` 已在公网实测通过，真实 QUIC v1 / HTTP/3 互操作已在境内 UDP-443 边缘（`taobao.com` / `tmall.com` / `dns.alidns.com`）与离线 `quic-go@v0.61.0` 服务端实测通过。
2. **③-A 嵌入式浏览器宿主选型**：仍为 `docs/NETSTACK_ADR.md` 唯一待裁决议程（`DotNetBrowser 4.3.5.8591` vs WebView2 vs CEF），不随本网络栈支线越权替代裁决。
