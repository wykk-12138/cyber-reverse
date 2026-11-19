# 厂商风控接线审计（从 `replica/src` 分阶段迁出，R1274 第 1 步）

原先在 `replica/src/Cybersole.Stores/Scripts/VendorWiring.cs`（**294 行**）。它是台账，按 `AGENTS.md` §3 归 `docs/`。

**本文是第 1 步**：把可核实的内容逐字搬出来。代码删除是第 2 步，因为那份表被 **9 个测试文件**引用
（`VendorWiringTests` 31 处 · `VendorGapTests` 15 · `VendorSolvingModeTests` 15 · `PerimeterXMarkerTests` 9 · 另有 5 个文件），
一次性删会同时打断九处断言，必须一轮一起改。

## 一、审计的问题（R140 命名的缺陷）

> **检测存在、存储存在，两者之间的那次调用不存在。**

`StoreFlow.DetectAsync` 靠 body 标记或 `server` 头认出 cloudflare / kasada / imperva / datadome / perimeterx / queue-it；
`AntiBotProtocol.Cookies` 列出其中四家会设的 cookie。
**对复刻件真正要紧的是第三列——有没有东西真的去要一个 token 并把它写回去。** R140 之前六家这一列全空。

## 二、源码头部自带的表（逐字）

```
vendor        marker (detect)              cookie            call wired
cloudflare    cf-chl / server:cloudflare   cf_clearance      yes  (R140)
kasada        kpsdk                       kpsdk             yes  (R141)
imperva       _Incapsula_Resource         none named        no   — no cookie, no solver
datadome      datadome                    datadome          no   — host recorded, protocol not
perimeterx    px-captcha (inferred)       none named        no   — _px3 exists; px-captcha does not
queue-it      queue-it                    queue-it-set-cookie  no — queue, not a solver
```

**四个缺口不是同一种缺口**，说清是哪一种才可行动：

- **DataDome** 有 host 没协议（像 R140 之前的 Cloudflare）；
- **PerimeterX** 两样都没有；
- **Imperva** 的 cookie 家族**在镜像里根本不存在**；
- **Queue-it** 是**队列不是挑战**——正确的处理是**等**，不是解。

## 三、词表（逐字，来自源码枚举）

| 枚举 | 取值 |
|---|---|
| `State` | `Wired` · `HostWithoutProtocol` · `DetectedOnly` · `NotAChallenge` · `OriginalSolvesProtocolUnrecorded` |
| `MarkerSource` | `ImageLiteral` · `Inferred` |
| `Gap` | `None` · `VendorAbsent` · `NoPageMarker` |
| `Solver` | `None` · `Local` · `SelfHosted` · `UserThirdParty` · `Unknown` |

`Row` 的字段：`Vendor, Marker, Cookie, State, Note, MarkerFrom, Gap, Solver, Relayed`。

**注意 `MarkerSource.Inferred`**：`perimeterx` 的 `px-captcha` 是**推断**出来的标记，不是镜像字面量——
这一列存在的意义就是让"推断"和"读到的"分开。

## 四、已逐字转录的行（5 条）

| vendor | marker | cookie | state |
|---|---|---|---|
| cloudflare | `challenge-platform` | `cf_clearance` | `Wired` |
| kasada | `kpsdk` | `kpsdk` | `Wired` |
| datadome | `datadome` | `datadome` | `Wired` |
| queue-it | `queue-it` | `queue-it-set-cookie` | `DetectedOnly` |
| vercel | `x-vercel-challenge-token` | `_vcrcs` | `DetectedOnly` |

> Cloudflare 的 marker 从 `cf-chl` 改成了 `challenge-platform`：镜像**不含** `cf-chl`，含的是
> `/cdn-cgi/challenge-platform/`（页面级，`DetectAsync` 读的就是这个）。`cf_clearance` 等也在镜像里，
> 但那些是**cookie 名**，归 cookie 列。

## 五、**尚未转录**的行（第 2 步读源码补）

`imperva` · `perimeterx` · `akamai` —— 这三行是**多行格式**（尤其 Akamai 带一段证据注释），
本轮的正则没抓到。**我不凭记忆补写它们**；第 2 步读源码逐行转录。

Akamai 那段证据（已读到的部分）：

```
detection   AkamaiGHost (0x146b249dc) · AkamaiQueueName (0x146b24a0c) · AkamaiReferer (0x14…)
solving     "Solving Akamai (" (0x146e77ebc) · "(SBSD)" (0x146e77ef4) · "(SDS)" (0x146e77f3…)
failure     "Akamai Failed" · "Akamai Failed (Rotating)" · "Akamai Blocked (IP)" · …
control     SkipAkamai (0x146e7243c) · "Akamai disabled"
internal    GetAkamaiCookie · AkamaiHandler · AkamaiQueueHandler · AkamaiPixel · AkamaiGener…
```

⇒ **镜像确实解 Akamai**（有 "Solving Akamai" 与两个命名模式），而本仓**没有 Akamai 求解器**——
它在 fanatics 等站只以失败文案出现。这条是**真缺口**，不是记账笔误。

## 六、这条审计守的规则（逐字）

> detection and storage are cheap and were already present; the call between them is the work

## 七、第 2 步要做的事（写在这里，防止忘记）

1. 读源码补 `imperva` / `perimeterx` / `akamai` 三行；
2. 改 9 个测试文件，把对 `VendorWiring.Rows` 的反射/枚举断言换成**测试内数据**或直接断言运行时行为；
3. 删 `VendorWiring.cs` 与 `VendorWiringTests.cs`；
4. 全量跑一遍，**用例数下降要能逐条解释**。

## 八、第 2 步的依赖图（R1275 实测，把「9 个文件」变成工单）

命令：

```
Get-ChildItem tests\Cybersole.Tests -Filter *.cs | Select-String -Pattern 'VendorWiring\.'
```

| 测试文件 | 依赖的成员（次数） | 处置建议 |
|---|---|---|
| `VendorWiringTests.cs` | `Rows` 6 · `AuditRule` 3 · `State` 3 · `Gaps` 1 · `MarkerSource` 1 · `Wired` 1 | **整份删除**——它只为这张表存在 |
| `VendorGapTests.cs` | `Gap` 7 · `Rows` 2 · `MarkerSource` 2 | 主要是台账断言；**逐个判断**，能断行为的留下 |
| `VendorSolvingModeTests.cs` | `Solver` 7 · `Rows` 4 | 同上 |
| `PerimeterXMarkerTests.cs` | `Gap` 5 · `Rows` 3 · `MarkerSource` 1 | 同上 |
| `QueueItStateTests.cs` | `State` 3 · `Rows` 3 · `Gap` 1 · `MarkerSource` 1 | 同上 |
| `ImpervaAbsenceTests.cs` | `Rows` 1 · `Gap` 1 | **最小**，先在这里试改 |
| `WallDispatchTests.cs` | `Gaps` 1 · `Wired` 1 | 疑为同名碰撞（`Wall*` 系列自己的成员），**先确认** |
| `WallSolvingTests.cs` | `For` 2 | 同上 |
| `CaptchaDeliveryAttributionTests.cs` | 1 处（`VendorWiring.` 后缀被正则截断，实际成员待读） | 先确认 |

**做法建议**：从 `ImpervaAbsenceTests` 开始（依赖最小），一次改一个文件、跑一次定向用例，
**不要九个一起改**——那样红了就分不清是哪一处的问题（R1233 的形态）。

