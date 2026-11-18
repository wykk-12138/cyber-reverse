# Kasada handshake, standalone

浏览器无关的 Kasada 客户端 token 获取实现。**零依赖**：只有 `KasadaHandshake.cs`，用 `System.Net.Http`，
复制进任何 .NET 8+ 项目即可。

## 怎么用

```csharp
var hs = new KasadaHandshake(httpClient);
var token = await hs.RunAsync(sensorScriptUrl);   // 页面 HTML 里的 p.js / ips.js 完整 URL
if (token is not null)
{
    token.ApplyTo(request);        // 把 x-kpsdk-ct / h / fc / r / v / Cookie 加到受保护请求上
    // 或单独取：token.ClientToken
}
```

`sensorScriptUrl` 必须带那两段 UUID —— 它是握手根目录的来源：

```
https://api.nike.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js
                        └──────────── uuid 1 ────────────────┘└──────────── uuid 2 ─────────────────┘
```

**从 origin 拼是拿不到的** —— `https://www.nike.com/mfc` 是 404。

## 它发的三跳（实网实测）

```
GET {dir}mfc                       -> x-kpsdk-fc（配置）、x-kpsdk-h（配置版本）
GET {dir}fp?x-kpsdk-v={build}      -> x-kpsdk-ct（token）、x-kpsdk-r（继续标记）
GET {dir}ips.js?KP_UIDz={token}    -> x-kpsdk-ct（受保护请求真正用的那个）
```

跑一次实网输出：

```
page 200 (1021882 chars)
sensor script = https://api.nike.com/{u1}/{u2}/p.js
  GET …/mfc -> 200
  GET …/fp?x-kpsdk-v=j-1.2.992 -> 200
  GET …/ips.js?KP_UIDz=… -> 200

token = 0AG0dCFuqChTjO3txRBRROs0rfb1XRgns4X4mk9co0g9PL8Sp1WkwKBY99ELUVZqx0ruZuF4Fg176fyjkZh…
build = j-1.2.992
  Cookie: KP_UIDz-ssn=…; KP_UIDz=…
  x-kpsdk-ct: 0AG0dCFuqChTjO3txRBRROs0rfb1XRgns4X4mk9co0g9PL8Sp1WkwKBY…
  x-kpsdk-fc: eyJmZWF0dXJlRmxhZ3MiOnt9LCJkeW5hbWljQ29uZmlnIjp7ImZyb250ZW5k…
  x-kpsdk-h: 01F47DxTPakzMm2tqdC3JSScDjKyQ=
  x-kpsdk-r: 1-AA
  x-kpsdk-v: j-1.2.992
```

## 三个会踩的坑

**1. 首跳不带 `x-kpsdk-h` 会拿到 304，什么都没有。**
`h` 是配置版本标签，**缺席被读成"我不用更新"，不是"我什么都不知道"**。所以固定发 `x-kpsdk-h: 01`，
服务端回 `01F47DxTPakzMm2tqdC3JSScDjKyQ=`（回显你的前缀 + 自己接一段配置指纹）。

**2. cookie 有两个，值相同，都要发。**
`KP_UIDz-ssn`（`HttpOnly; Secure; SameSite=None`）和 `KP_UIDz`（`HttpOnly`）。丢任何一个都是
抗爬系统专门盯的形状。

**3. `ct` 是一次性的。**
同一秒连打两次 `/fp`，两个 token 完全不同。不能缓存复用，每次会话重新取。

## 拿得到什么、拿不到什么

服务端自己的 `Access-Control-Expose-Headers` 就是答案：

```
x-kpsdk-ct, x-kpsdk-r, x-kpsdk-c, x-kpsdk-h, x-kpsdk-fc
```

| 头 | 来源 | 这条路可得 |
|---|---|---|
| `x-kpsdk-ct` | 服务端签发 | ✅ |
| `x-kpsdk-h` | 服务端（回显前缀 + 配置指纹） | ✅ |
| `x-kpsdk-fc` | 服务端（配置 JSON） | ✅ |
| `x-kpsdk-r` | 服务端（继续标记） | ✅ |
| `x-kpsdk-v` | 自己填 | ✅ |
| **`x-kpsdk-dt` / `im` / `st` / `cd`** | **客户端算** | ❌ |

**`dt`/`im`/`st` 不在服务端的暴露清单里**，它们是 sensor 自己算的。**目标站点如果校验它们，这条路不够。**

## 一个必须知道的前提：拿到 token ≠ token 有用

实测：`/fp` 对**任何**请求形状都签发 token（不带 `h`、不带 `v`、`v` 写垃圾、`h` 换前缀，全部 200）；
`ips.js?KP_UIDz=FORGED-TOKEN` 也照样 200 并回一个新 token；`POST /tl` 空 body 也 200。

**⇒ 手里有 token 证明不了任何事。** 只有受门保护的端点能回答，所以带上 `ProbeAsync`：

```csharp
var gate = await hs.ProbeAsync("https://your-target/protected", token);
Console.WriteLine(gate);   // bare=403(0b) token=200(1234b) gated=True
```

- **两次不同** → 那个端点是门，token 打开了它
- **两次一样** → 要么不要 Kasada，要么它真正要的是别的东西（登录态、API key）
- **`BareStatus == 0`** → 打不通

Nike 自己的主页加载只发四个 Kasada 请求，**一个业务请求都不带 ct**；商品 feed 带不带 ct 回应完全一样。
**所以 Nike 上找不到可验证的门** —— Kasada 真正发力的位置是 SNKRS 和结账，那些需要登录态。

## 自己跑

```bash
dotnet run -- https://www.nike.com/ https://your-target/protected
```

第一个参数是页面（用来找 sensor 脚本），后面每个 `http` 参数都会被 `ProbeAsync` 问一遍。

## 来源

每一条都是实网测出来的，不是文档抄的。完整推导（含原始逆向）在
[`docs/KASADA/11-jint-runtime.md`](../../docs/KASADA/11-jint-runtime.md) §6–§11。
