# `Cybersole.Http` 海外直连公网 VPS QUIC / HTTP/3 / TLS 全量实测报告（`ba1d7c0`）

> **所属分支**：`full-QUIC/HTTP3/TLS`（`main` 分支锁定在 `288a95e1d3fa4cb85d61d12cd5e55affcc33bd82` 未修改）
> **验证提交**：`ba1d7c03d03ecfe77989b45828864316b9c33194`（承接 `6f223b21` 首轮海外实测修复）
> **实测日期**：`2026-11-24`（UTC `2026-11-24T02:32Z–02:37Z`）
> **安全约束**：全部公网测试严格保持 `InsecureSkipVerify = false` 与 `UseEmbeddedDefaultRoots = true`（验证内嵌 `RootCertificates.bin` 121 张根证书），全部 `dotnet` 构建与测试命令均带 `-m:1`。

---

## 1. 实测环境与对照组基线

- **主机 OS / 内存**：Microsoft Windows Server 2022 Standard (`10.0.20348`, x64)，16.0 GB 内存
- **公网出口**：美国东岸 Ashburn（Cloudflare 节点 `colo=IAD`，`loc=US`，IP `104.254.189.209`，直连公网无本地代理/TUN 拦截 UDP-443）
- **工具链**：
  - `.NET SDK`：`8.0.428`（Runtime `8.0.34`）
  - `Go`：`go1.27.4 windows/amd64`（离线模块缓存已预热，`ThirdPartyQuicTlsInteropTests` 使用 `GOPROXY=off` 编译 `quic-go@v0.61.0`）
- **目标框架核对**：`replica/Directory.Build.props` 为跨平台 `net8.0`
- **提交与分支核对**：
  - `git rev-parse HEAD` = `ba1d7c03d03ecfe77989b45828864316b9c33194`（`git show --stat ba1d7c0` 列出 19 个变更文件，`933 insertions(+), 132 deletions(-)`）
  - `git rev-parse main` = `288a95e1d3fa4cb85d61d12cd5e55affcc33bd82`

### Go `quic-go@v0.61.0` 官方参考对照组基线（同机直连 UDP-443）

| 目标 URL | `quic-go@v0.61.0` 实测结果 | 归因参考 |
|---|---|---|
| `https://one.one.one.one/cdn-cgi/trace` | `200 HTTP/3.0`, `alpn=h3`, `cipher=0x1301`, `curve=0x11ec` (`X25519MLKEM768`), `314 B`, `49 ms` | UDP-443 畅通 |
| `https://cloudflare-quic.com/` | `200 HTTP/3.0`, `alpn=h3`, `cipher=0x1301`, `curve=0x11ec`, `125959 B`, `31 ms` | UDP-443 畅通 |
| `https://www.google.com/generate_204` | `204 HTTP/3.0`, `alpn=h3`, `cipher=0x1301`, `curve=0x11ec`, `0 B`, `13 ms` | UDP-443 畅通 |
| `https://quic.nginx.org/` | `200 HTTP/3.0`, `alpn=h3`, `cipher=0x1301`, `curve=0x11ec`, `2523 B`, `206 ms` | UDP-443 畅通 |
| `https://fp.impersonate.pro/api/http3` | `200 HTTP/3.0`, `alpn=h3`, `cipher=0x1302`, `curve=0x001d`, `7051 B`, `151 ms` | HTTP/3 指纹端点可达 |
| `https://www.akamai.com/`（裸 UA 头） | `403 HTTP/3.0`, `alpn=h3`, `cipher=0x1302`, `curve=0x11ec`, `368 B`, `87 ms` | Akamai WAF 校验导航头；带完整 Chrome 头后 `Cybersole.Http` 返回 `200 HTTP/3` |
| `https://www.nike.com/` | `ERR (21 ms): CRYPTO_ERROR 0x150 (remote): 200:internal error` | 服务端策略拒绝 UDP-443 QUIC |
| `https://www.apple.com.cn/` | `ERR (10 ms): CRYPTO_ERROR 0x150 (remote): 200:internal error` | 服务端策略拒绝 UDP-443 QUIC |
| `https://www.aliyun.com/` | `ERR (87 ms): CRYPTO_ERROR 0x150 (remote): handshake failed` | 对照组被拒，`Cybersole.Http` (`chrome_150`) 实测握手成功获 `200 HTTP/3` |

---

## 2. 可复现测试命令与三阶段总览（`100 / 100` 全绿）

```powershell
# 阶段 1：离线 6 组 + Go/quic-go@v0.61.0 第三方互操作（72/72）
dotnet test replica/tests/Cybersole.Tests/Cybersole.Tests.csproj -m:1 `
  --filter "FullyQualifiedName~WireFingerprintTests|FullyQualifiedName~QuicHttp3Tests|FullyQualifiedName~TlsStackTests|FullyQualifiedName~ProtocolLayerTests|FullyQualifiedName~PureNetClientIntegrationTests|FullyQualifiedName~NetClientProtocolParityTests|FullyQualifiedName~ThirdPartyQuicTlsInteropTests" `
  --logger "console;verbosity=normal"

# 阶段 2：公网边缘与指纹 Oracle 互操作（17/17）
dotnet test replica/tests/Cybersole.Tests/Cybersole.Tests.csproj -m:1 --no-build `
  --filter "FullyQualifiedName~LivePublicEdgeInteropTests" `
  --logger "console;verbosity=detailed"

# 阶段 3：海外直连 UDP-443 专项 11 项（11/11）
dotnet test replica/tests/Cybersole.Tests/Cybersole.Tests.csproj -m:1 --no-build `
  --filter "FullyQualifiedName~LiveOverseasHttp3InteropTests" `
  --logger "console;verbosity=detailed"
```

| 阶段 | 测试套件 | 总数 | 通过 | 失败 | 跳过 | 实际耗时 |
|---|---|---:|---:|---:|---:|---:|
| **阶段 1** | 离线基线 + Go `quic-go@v0.61.0` 互操作 | 72 | **72** | 0 | 0 | `11.5150 s` |
| **阶段 2** | `LivePublicEdgeInteropTests` | 17 | **17** | 0 | 0 | `6.7407 s` |
| **阶段 3** | `LiveOverseasHttp3InteropTests` | 11 | **11** | 0 | 0 | `22.7721 s` |
| **合计** | **全三阶段** | **100** | **100** | **0** | **0** | **`41.0278 s`** |

---

## 3. 阶段 3 新增三项专项实测（原样标准输出）

本轮 `ba1d7c0` 新增的 3 项海外专项测试均一次通过，正式闭环原先遗留的公网 QPACK 动态表、公网海外多代主动 KeyUpdate、以及公网真实 QUIC Retry Token 三大验证项：

### 3.1 公网 QPACK 动态表高频插入与并发解码（`Overseas_Chrome152_QpackDynamicTable_MultiRequest_PublicEdges`，`7 s`）

```text
[Overseas QPACK chrome_152] https://www.google.com/: peerQpack=(cap=65536,blocked=100) clientQpack=(ins=76,known=76,entries=76,dynSections=10)
[Overseas QPACK chrome_152] https://www.youtube.com/: peerQpack=(cap=65536,blocked=100) clientQpack=(ins=72,known=72,entries=72,dynSections=10)
[Overseas QPACK chrome_152] https://cloudflare-quic.com/: peerQpack=(cap=0,blocked=0) clientQpack=(ins=0,known=0,entries=0,dynSections=0)
[Overseas QPACK chrome_152] https://www.litespeedtech.com/: peerQpack=(cap=4096,blocked=100) clientQpack=(ins=19,known=19,entries=19,dynSections=9)
[Overseas QPACK chrome_152] https://www.facebook.com/: peerQpack=(cap=4096,blocked=100) clientQpack=(ins=105,known=105,entries=105,dynSections=10)
```

- **结论**：5 个公网边缘均完成 4 次串行 + 6 次并发 `chrome_152` HTTP/3 请求，其中 **Google (`ins=76`)、YouTube (`ins=72`)、LiteSpeed (`ins=19`)、Facebook (`ins=105`)** 4 个公网边缘真实触发了 QPACK 动态表插入与动态响应头块解码，且全节点保持 `ins == known == entries`，验证 `Http3Connection` 并发 `SectionAcknowledgment` / `InsertCountIncrement` 锁串行与 `_sentQpackKnownReceivedCount` 追踪无溢出竞态。

### 3.2 公网三节点多代 1-RTT 客户端主动 KeyUpdate（`Overseas_ClientInitiatedKeyUpdate_MultiGeneration_CloudflareGoogleNginx`，`494 ms`）

```text
[Overseas KeyUpdate] https://one.one.one.one/cdn-cgi/trace: wGen=2 rGen=2 cliKu=2 srvKu=0 statuses=(200,200,200)
[Overseas KeyUpdate] https://www.google.com/generate_204: wGen=2 rGen=2 cliKu=2 srvKu=0 statuses=(204,204,204)
[Overseas KeyUpdate] https://quic.nginx.org/: wGen=2 rGen=2 cliKu=2 srvKu=0 statuses=(200,200,200)
```

- **结论**：Cloudflare、Google、NGINX 三大不同 QUIC 服务端实现均在握手确认后完成连续两代（`phase 0 → 1 → 0`）客户端主动 1-RTT KeyUpdate（`wGen=2, rGen=2, cliKu=2, srvKu=0`，3 轮请求全部 2xx）；叠加阶段 2 `taobao.com` / `tmall.com` 同样 `wGen=2, rGen=2, cliKu=2`，共 5 个真实公网边缘验证通过。

### 3.3 公网 IETF QUIC Retry Token 与严格证书校验（`Overseas_PublicQuicRetryEndpoints_VerifyRealRetryTokenAndHttp3`，`9 s`）

```text
[Overseas Retry Probe] https://quic.aiortc.org:4434/: status=200 version=HTTP/3 alpn=h3 cipher=0x1302 retry=True retryTokenLen=73 bytes=1196
[Overseas Retry Probe] https://test.privateoctopus.com:4434/: PROBE_ERROR (QuicException): x509: certificate signed by unknown authority ('CN=test.privateoctopus.com')
[Overseas Retry Probe] https://quic.tech:8444/: status=200 version=HTTP/3 alpn=h3 cipher=0x1301 retry=True retryTokenLen=30 bytes=462
[Overseas Retry Probe] https://http3-test.litespeedtech.com:4434/: PROBE_ERROR (TimeoutException): QUIC handshake to http3-test.litespeedtech.com:4434 timed out after 8000 ms.
[Overseas Retry Probe] https://nghttp2.org:4434/: status=200 version=HTTP/3 alpn=h3 cipher=0x1301 retry=True retryTokenLen=90 bytes=6616
```

- **结论**：**3 个独立 IETF QUIC 实现的公网 Retry 节点**（`quic.aiortc.org:4434` token 73 B、`quic.tech:8444` token 30 B、`nghttp2.org:4434` token 90 B）均在严格 X.509 根证书校验下完成 Retry Integrity Tag 校验、携带 Retry Token 重发 Initial 并成功返回 `200 HTTP/3`；`test.privateoctopus.com:4434` 因自签证书被严格校验正确拒收；`http3-test.litespeedtech.com:4434` 8000 ms 无响应超时。

---

## 4. 其余阶段 2 & 阶段 3 实测观测汇总

### 4.1 阶段 3 其余 8 项海外 QUIC/HTTP/3 实测（`ba1d7c0` 复跑全部通过）

| 用例 / 目标 | 路径与预设 | 关键实测输出 | 结果 |
|---|---|---|---|
| `one.one.one.one/cdn-cgi/trace` | 直连 H3 & `ProtocolRacer` (`chrome_150`) | 直连 `200 HTTP/3`, `alpn=h3`, `cipher=0x1301`, `scidLen=0`, `retry=False`, `peerUni=3`, `hs=27.4 ms`, `315 B`；Racer `200 HTTP/3`, `320 B`, `32 ms`；均含 `http=http/3`, `tls=TLSv1.3`, `kex=X25519MLKEM768` | ✅ |
| `cloudflare-quic.com/` | 直连 H3 & `ProtocolRacer` (`chrome_150`) | 直连 `200 HTTP/3`, `cipher=0x1301`, `scidLen=0`, `peerUni=3`, `125,959 B`, `72 ms` (`hs=23.4 ms`)；Racer `200 HTTP/3`, `125,959 B`, `123 ms` | ✅ |
| `www.google.com/generate_204` | 直连 H3 & `ProtocolRacer` (`chrome_150`) | 直连 `204 HTTP/3`, `cipher=0x1301`, `scidLen=0`, `peerUni=103`, **`alps=0x44cd(len=182)`**, `26 ms` (`hs=21.5 ms`)；Racer `204 HTTP/3`, `27 ms` | ✅ |
| `quic.nginx.org/` | 直连 H3 & `ProtocolRacer` (`chrome_150`) | 直连 `200 HTTP/3`, `cipher=0x1301`, `scidLen=0`, `peerUni=3`, `2,523 B`, `205 ms` (`hs=110.5 ms`)；Racer `200 HTTP/3`, `2,523 B`, `196 ms` | ✅ |
| `www.nike.com/` & `www.akamai.com/` | `NetClient(PureNetClient)` / `ProtocolRacer` / 直连 H3 | `nike.com`：`NetClient` `200` (`1,087,761 B`, `setCookieLen=1818`), Racer 回退 `200 HTTP/2.0` (`1,086,588 B`), 直连 H3 报 `200:internal error`（与 `quic-go` 一致）；`akamai.com`：三路带全浏览器头均 `200 HTTP/3`（直连 `cipher=0x1302`, `225,533 B`, `123 ms`） | ✅ |
| 单连接 8 并发多路复用 | 直连 H3 (`chrome_150`) | `cloudflare-quic.com`: 8×`200 HTTP/3` 共 `1,007,672 B`（每流 `125,959 B`）, `370 ms`；`one.one.one.one/cdn-cgi/trace`: 8×`200 HTTP/3` 共 `2,535 B`, `29 ms` | ✅ |
| QUIC PSK 会话复用 | 直连 H3 (`chrome_150_PSK`) | `one.one.one.one`: Conn1 `ticketsCached=1` → Conn2 `200 HTTP/3, resumed=True, hs=17.0 ms`；`www.google.com/generate_204`: Conn1 `ticketsCached=1` → Conn2 `204 HTTP/3, resumed=True, hs=15.7 ms` | ✅ |
| `fp.impersonate.pro/api/http3` | 直连 H3 (`chrome_150` & `chrome_152`) | 两预设均 `200 HTTP/3`, `cipher=0x1302`, `initPn=0`, `scidLen=0`, `dcidLen=8`, `remote_ja3n == local_ja3n` (`36b3da67265214a919829c5e959f7425`), `local_ja4=q13d0311h3_55b375c5d22e_653d80c3fe9d`, `header_order=:method,:authority,:scheme,:path,user-agent,accept`, 15 项 QUIC Transport Parameters 全匹配；`chrome_152` SETTINGS=`1:65536;6:262144;7:100;51:1;GREASE`，`chrome_150` SETTINGS=`51:1` | ✅ |

### 4.2 阶段 2 `LivePublicEdgeInteropTests` 关键观测（`17/17` 通过）

- **指纹 Oracle（`tls.peet.ws/api/all` 5 预设 + `tls.browserleaks.com/json` 2 预设）**：`JA4`、`JA4_r`、`Akamai H2`（及 `firefox_148` 的 `JA3_hash`）与本地 `WireFingerprint` 100% 精确匹配。
- **`ProtocolRacer` 海外竞速**：`cloudflare-quic.com`（`200 HTTP/3, 125,959 B, 75 ms`）与 `www.aliyun.com`（`200 HTTP/3, 157,055 B, 452 ms`）均由 H3 胜出；`www.apple.com.cn` 平滑回退 `200 HTTP/2.0`（`145,111 B, 176 ms`）。
- **直连公网多代主动 KeyUpdate**：`www.taobao.com` 与 `www.tmall.com` 均 `wGen=2 rGen=2 cliKu=2 srvKu=0`（`200 HTTP/3`）。

---

## 5. Observation / Fix / Unknown 分栏结论

- **Observation**：在海外无 UDP-443 拦截的真实公网环境下，`ba1d7c0` 提交的 `Cybersole.Http` 纯托管网络栈在严格证书校验下达成 **阶段 1 `72/72` + 阶段 2 `17/17` + 阶段 3 `11/11`（总计 `100/100`）全绿通过**；真实公网 QPACK 动态表（4 个公网边缘共 272 次动态表插入）、真实公网多代 1-RTT 客户端主动 KeyUpdate（5 个公网边缘）、真实公网 QUIC Retry Token（3 个独立 IETF 实现节点）、Google QUIC ALPS `0x44CD`、Cloudflare `X25519MLKEM768`、QUIC PSK 会话复用以及 TCP/HTTP2/HTTP3 指纹 Oracle 全部闭环验证。
- **Fix**：本次 `ba1d7c0` 实测未暴露新的协议或代码缺陷，无需改动业务源码。
- **Unknown / 边界**：
  1. **公网边缘服务端主动发起的 1-RTT KeyUpdate**：本轮所有公网连接短生命期内均为客户端主动发起（`cliKu=2, srvKu=0`）；服务端主动触发 `KeyPhase 0→1` 已由 Go `quic-go@v0.61.0` 本地夹具（~PN 100 传输 512 KB）验证通过，公网长连接被动触发保持 `Unknown`。
  2. **QUIC 0-RTT 应用数据包**：经 IDA 实证原版 `Cybersole.exe`（`sub_1412A0820` / `sub_14129F560`）不派生 `"c e traffic"`、不发 0-RTT 应用包，按原版行为不适用/已结案。
  3. **`③-A` 嵌入式浏览器宿主选型**：仍为 `docs/NETSTACK_ADR.md` 独立待裁决议程，不在本纯 C# 传输栈验证范围内。
