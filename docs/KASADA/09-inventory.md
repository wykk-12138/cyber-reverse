# 09 · Kasada 能力清单（不遗漏的判据）

> 这份是**判据**，不是叙述。目标是"把 Cybersole 所有 Kasada 能力全部挖出来"，那就必须先有一张能穷举的表，
> 否则"全部"永远只是"我记得的那些"。
>
> 状态：✅ 已进文档并带证据 · 🟡 有证据但未成文 · ⬜ 未挖到（附缺口说明）· **Unk** 挖过但拿不到（附缺什么判据）

最后更新：2026-11-18（本轮新增 §E 整族、§D 拟人输入、§B4 LZ 字母表）

---

## A. 引擎与执行环境

| # | 能力 | 证据 | 文档 | 状态 |
|---|---|---|---|---|
| A1 | 内嵌 **Jint 4.17.0** 解释器（AOT 编译进产物） | `Jint, Version=4.17.0.0` `0x146dd37ac` · `EnableHostContractVerification` `0x146dd3aac` · 语句类族 `0x1434cb5dd` | 02 | ✅ |
| A2 | 内嵌 **Acornima 1.7.0** 解析器 | `0x14315d5ef` | 02 | ✅ |
| A3 | 内嵌 **DotNetBrowser 4.3.5** + Chromium 二进制提取 | `0x14315a15d` · `ChromiumBinariesExtractor` `0x1432bb1c5` · `.cybersole-chromium.xml` `0x14336a99f` | 03 | ✅ |
| A4 | 浏览器指纹随机化：`GenRandomChrome` / `GenRandomIos` / `GenRandomSizedBrowser` / `GetRandomWebGLRenderer` / `IsChrome` | 池 `0x03448170`–`0x034481be` | 08 §1 | 🟡 |
| A5 | **shim 的具体内容**（注入了哪些宿主 API） | 无 | — | **Unk**：Jint 侧只有引擎证据；shim 是运行时行为，静态产物里不可观察。02 §3 的清单来自**浏览器实测缺口**，不是原版 |

## B. 脚本获取与解析

| # | 能力 | 证据 | 文档 | 状态 |
|---|---|---|---|---|
| B1 | script id 双 UUID 结构 | 池偏移 `0x06aabf24`（`/149e9513-…/2d206a39-…`，VA 未逐条复核） | 01 §2 | ✅ |
| B2 | 九条脚本/端点路径（`ips.js` · `fp` · `a-4-a/c.js` · `prop.json`） | 池 `0x06aabf24`–`0x06ab5cfc` | 01 §2.1 | ✅ |
| B3 | 从 HTML 找脚本：`script[src*='ips.js']` | `0x071528b4` | 01 §2.3 | ✅ |
| B4 | **LZ 字母表**（sensor 数据是 LZ 压缩的） | `get_LzAlphabet` `0x1434484a9` · `LzAlphabet` `0x143448511` / `0x146dee96c` | 08 §1.5 | 🟡 |
| B5 | 字母表的**具体内容** | 无 | — | **Unk**：只有 getter/setter，没有常量表命中；可能运行时从脚本取 |

## C. 挑战流程 —— 本地算（纯 JS 引擎侧）

| # | 能力 | 证据 | 文档 | 状态 |
|---|---|---|---|---|
| C1 | `GetScript` / `HandleResponse` 主循环 | `d__33`/`d__47` · `d__32`/`d__46` | 05 §1 | ✅ |
| C2 | `GetKasada` 取 token | `d__34`/`d__48` · `GetKasada@` `0x14345a910` | 05 §1 | ✅ |
| C3 | `GetWorkTime` 握手耗时 | `d__35`/`d__50` · `_kasadaWorkTime` `0x14345aa92` | 01 §6 · 05 §2 | ✅ |
| C4 | 传感器：`GenerateSensor` / `GetSensor` / `SubmitSensor` / `GetSensorData` | `GenerateSensor` 7 条 `0x143311103` 一带 · `GetSensorData` 8 条 `0x14331b944` 一带 | 02 §1 | ✅ |
| C5 | 挑战应答的量：`Answers` / `Duration` / `ServerTime` / `RemoteServerTime` | `get_Answers` `0x14344884a` · `RemoteServerTime` `0x143448a03`（其余同族） | 08 §1–2 | ✅ |
| C6 | cd 生成原语：`Sha256Hex` / `HashDifficulty` / `GetOffset` / `RandomAddSubtract` / `GetCdHeader` | `0x143448c9a` / `0x143448cab` / `0x143448d40` / `0x143448d2d` / `0x143448d52` | 08 §1 | ✅ |
| C7 | `SolveAsync`（`d__3`）主流程 | `<SolveAsync>d__3` = **`0x143448a28`**；全族另有 `d__1` `0x14344b31d` · `d__19` `0x14345b8df` · `d__20` `0x143447c43` · `d__8/9/10/11` `0x143366xxx`（2Captcha/CapSolver 等打码服务） | 08 §4 | 🟡（只有成员表） |
| C7a | **请求侧落地**：`rec[16]→cd`、`rec[11]→ct`、`rec[15]→h`、`sub_1408EF620(rec)→v` | `sub_1408F2CD0`（0x382，async）· 头对象头表见 01 §3.0 | 08 §9.1 | ✅ |
| C7b | **响应侧落地**：Api 路的 cd/ct/dt/dv 全部来自服务商响应头 | `sub_141148770`（0x3d0）· ct→+16 · dt→+24 · im→+32 · dv→+40 | 08 §9.2 | ✅ |
| C8 | **cd 的算法公式** | 无 —— **且判定为不存在**：`Sha256Hex`/`HashDifficulty`/`RandomAddSubtract` 同类型里有 `get_Bmsz`，同族有 `IAkamaiGenerator`（`AkamaiGeneratorHyped` / `AkamaiGeneratorJevi`）⇒ 那批属 **Akamai 的 PoW** | 08 §10.3 | ✅ **结案（负）**：Kasada 的 cd 只有两个来源 —— 本地脚本产出、服务商响应；本地自写算法的说法不成立 |
| C8a | `rec` 槽位表（9=dt · 10=im · 11=ct · 15=h · 16=cd · 17=?） | `sub_1408F2CD0` / `sub_1408EFC50` 两处伪代码交叉 | 08 §10.1 | ✅ |
| C8b | **负结论**：已读代码里没有写 `rec[16]` 的地方（只读、只被 Reset 清零） | `sub_1408F2CD0` · `sub_1408EF930` | 08 §10.2 | ✅（负结论，需更大范围对照） |
| C8c | 上游请求构造器（带 ct/dt/im/v + user-agent，注册 200） | `sub_1408EFC50`（0x2c5） | 08 §9.1 | ✅ |
| C8d | Kasada 的第三方解法**只有 HyperSolutions 一家**（`JeviSolver` 属 Akamai，不是第二家） | `JeviSolver` `0x143321d3a` vs `AkamaiGeneratorJevi` `0x1432364c3` | 08 §10.4 | ✅ |
| C9 | **`TL` 的语义** | `sub_1408F0450` / `sub_1408F3AF0`（各 0x12f）：响应里有 `'reload'` 就继续并首次记握手时刻，没有就报 `Failed solving Kasada (TL)`（UI 色 `#FB4961`） | 01 §7 | ✅ **结案** |
| C9a | `st` / `fc` / `h` 的写入点（都是从响应头取） | `st`→+104 · `fc`→+112 · `h`→+120，见 `sub_1408F0450` / `sub_1408F05E0` | 08 §11 | ✅ |
| C9b | **统一结论：客户端不算，只搬运** | 九个头逐条写入点全表 | 08 §11 | ✅ |
| C10 | `Reset`（重置握手状态） | `<Reset>b__44_0` `0x14345a9ac` · `<Reset>b__30_0` `0x14345add0` | 05 §1 | ✅ |

## D. 挑战流程 —— 真浏览器侧

| # | 能力 | 证据 | 文档 | 状态 |
|---|---|---|---|---|
| D1 | 离屏渲染宿主 `_offscreenHost` / `OffscreenHost` | `0x143448202` / `0x14343d15c` | 08 §1.5 | ✅ |
| D2 | 过 Turnstile 循环 `<LoopTurnstile>d__20` | 池 `0x034470a4` | 08 §1.5 | 🟡 |
| D3 | 鼠标/点击：`MoveMouse` · `MoveMouseAndClickAsync` · `MoveMouseAndClickWithoutTrajectoryAsync` | `0x143448170` · `0x14348bf91` · `0x14348bf44` | 08 §1.5 | ✅ |
| D4 | 屏幕级输入：`PressMouseOnScreenAsync` / `ReleaseMouseOnScreenAsync` / `PressKeyAsync` / `SuppressInput` | 池 `0x0348bfc5` 片 | 08 §1.5 | 🟡 |
| D5 | cookie / 代理：`SetCookies` / `DeleteCookies` / `SetProxy` / `MultiPartTlds` | 池 `0x034470a4`–`0x034473c9` | — | 🟡 |
| D6 | 浏览器池：`_browsersLock` / `_creating` / `get_Healthy` / `<RunWithTimeout>d__18` | 池 `0x03447014` 片 | — | 🟡 |
| D7 | 从网络头嗅探 token 的时序（`_headersTcs`） | 池 `0x0344742e` | 03 §3 | ✅ |

## E. 远端服务 —— **HyperSolutions**（本轮新挖，之前整套漏掉）

| # | 能力 | 证据 | 文档 | 状态 |
|---|---|---|---|---|
| E1 | `HyperSolutionsSolver` 类型 | `0x143321c61`（池 `0x03320e61`），`str` total = 1 | 04 §2.5 | ✅ |
| E2 | Kasada 端点 **`https://kasada.hypersolutions.co/botid`** | `0x14706ebfc` | 04 §2.5 | ✅ |
| E3 | Kasada 端点 **`https://kasada.hypersolutions.co/payload`** | `0x14706ec64` | 04 §2.5 | ✅ |
| E4 | 字段名 `kasadaRequest` | `0x1470ae4ec`（total = 1） | 04 §2.5 | ✅ |
| E5 | `IKasadaSolver` / `KasadaSolveRequest` / `KasadaSolveResult` | `0x1433216f6` / `0x1433218dc` / `0x143321733` | 04 §1 | ✅ |
| E6 | `KasadaCdSolver`（服务通道上的 cd 实现） | `0x143321dfa` | 04 §1 · 08 §5 | ✅ |
| E7 | 同一服务商的另两个端点（Akamai / TrustDecision）—— **用于划边界** | `akm.hypersolutions.co/{pixel,sbsd,v2/sensor}` · `trustdecision.hypersolutions.co/{decode,payload,sign}` | 07 §2.1 | ✅ |
| E8 | **`/payload` 与 `/botid` 的请求形状** | 反编译 `sub_14111CB10`（botid）/ `sub_1411483E0`（payload），见 04 §2.6：`POST` + `X-Type: kasada` + `X-Upstream-{Url,Method,Headers}` + `X-User-Id` + `X-Client-Version` + `content-encoding: zstd`；200/401/403 三档 | 04 §2.6 | ✅ |
| E8b | `/payload` 的状态文案 = **`Getting Kasada (1)`** ⇒ `Getting Kasada (n)` 就是打这个端点 | `0x146da1778`（`/botid` 那条是 `0x146da1588` = `Getting BotID`） | 04 §2.6 | ✅ |
| E9 | protobuf 的 solver 指令协议（`stage` / `ReceiveHeaders` / `target`） | 字段表 `0x143459xxx` · base64 样本池 `0x06f96c3c` | 04 §2 | 🟡（Inf） |
| E10 | `BotID` 族（`BotIdHandler` / `Getting BotID` / `BotID API down (Contact staff)`） | `0x143330b4e` · `0x146da1594` · `0x146b609ac` | — | ⬜ **待挖**：是不是 Kasada 的 botid，还是通用能力 |

## F. 模式、降级与状态机

| # | 能力 | 证据 | 文档 | 状态 |
|---|---|---|---|---|
| F1 | 四模式：`Api`(getting) / `Local`(solving) / `Fallback` / `MobileFallback` | 文案动词见 05 §4 | 04 §3 | ✅ |
| F2 | `KasadaHandler`（`d__32`–`d__35`）与 `KasadaMobileHandler`（`d__46`–`d__50`）两套 | `0x14345abb1` · `0x14345a632` | 05 §1 | ✅ |
| F3 | MFC 移动降级：`GetMfc` / `MfcEnabled` / `IsMobile` / `VersionProvider` | `d__49` · `0x14345a802` · `0x1434599e8` | 04 §4 | ✅ |
| F4 | 12 条状态/失败文案 | 05 §4 全表 | 05 | ✅ |
| F5 | **`MFC` 的展开与协议** | `Getting Kasada (MFC)` 属 getting 家族 · `GetMfc` 只在移动 handler | 10 §3 | 🟡 **收窄**：MFC = Api 路在 `IsMobile` 时的分支；展开本身仍 **Unk** |

## I. 移动构型（本轮新增，与"执行者"正交的第二维）

| # | 能力 | 证据 | 文档 | 状态 |
|---|---|---|---|---|
| I1 | 三个开关：`IsMobile` / `MfcEnabled` / `VersionProvider` | `0x14345a7e8` · `0x14345a802` · `0x14345a811` | 10 §2.1 | ✅ |
| I2 | `MobileDv` —— 移动端的 `x-kpsdk-dv` 取值 | `get_MobileDv` `0x14344855b` | 10 §2.2 | ✅ |
| I3 | `GenRandomIos` —— iOS 形态指纹生成 | `0x143448fbe` | 10 §2.3 | ✅ |
| I4 | 浏览器侧移动模拟四件套 + `SpoofMobile` 总开关 | `0x1433048fd` · `MobileUserAgent` `0x143306ee6` · `MobileViewport{Width,Height}` · `MobileWindowHeight` | 10 §2.4 | ✅ |
| I5 | 移动端 `x-kpsdk-v` 由 `VersionProvider` 注入（不与桌面共用常量） | 同上 | 10 §2.1 | ✅ |
| F6 | 重试策略（`Rotating` / `Retry limit reached` 的停/换语义） | 05 §5 | 05 | ✅ |

## G. 状态与持久化

| # | 能力 | 证据 | 文档 | 状态 |
|---|---|---|---|---|
| G1 | 九个握手字段 `_kasadaCt/Dt/Dv/St/Rst/Fc/H/Im/WorkTime` | `0x14345aa42`–`0x14345aa92` | 05 §2 | ✅ |
| G2 | 账号级凭据 `_accountKasada` | `0x14337b669` | 01 §4 · 05 §2 | ✅ |
| G3 | `_kasada` / `_kasadaMobile` | `0x143370d3d` / `0x143370d5b` | 05 §2 | ✅ |
| G4 | 设备 cookie `KP_UIDz` | `0x146dd97ac`（清单 `0x146dd97d4`） | 01 §4 | ✅ |
| G5 | 属性表 `Script`/`BasePath`/`KasadaCt`/`CookieName`/`IpsUrl`/`KasadaVersion` | `0x1434486b1`–`0x14344872b` · `0x143370826` | 05 §3 | ✅ |

## H. 站点差异

| # | 能力 | 证据 | 文档 | 状态 |
|---|---|---|---|---|
| H1 | 七个 per-store 版本头（Nike / Footsites / Scheels / Converse / Crocs ×3） | `0x146e1779c` · `0x146d93f64` · `0x146e7a4d4` · `0x146b9ec2c` 一带 | 01 §5 | ✅ |
| H2 | **每个站点的 script id 是否不同** | 池里 223 条 UUID 下界中，含 Kasada 路径的**只有 Nike 那一组**；IDB 复核 `prop.json`=4 · `x-kpsdk-v=`=3 · `/a-4-a/`=1 —— 全部属那一组 | 01 §2 · §2.0 | ✅ **结案**：每站不同、运行时解析（02 §1.5），硬编码那组只作 Nike 默认/回退 |
| H3 | 各站点用哪个模式（哪个站走 Local、哪个站必须浏览器） | 无 | — | ⬜ 待挖：需按站看流程代码 |

---

## 本轮新增（相对上一版 01–08）

1. **§E 整族**：`HyperSolutionsSolver` + `kasada.hypersolutions.co/{botid,payload}` + `kasadaRequest`
   —— 之前 04 写的是"自建远端 solver 的最小契约"，那是我按字段表**推的**；
   实际原版接的是 **HyperSolutions** 这个现成服务。**这是本轮最重要的一条更正。**
2. **§D 拟人输入**：`MoveMouseAndClick` 与 `…WithoutTrajectory` 成对、屏幕级按下/释放/按键、`SuppressInput`
   —— 浏览器路的反检测手段比上一版描述的多一层。
3. **§B4 LZ 字母表**：sensor 数据是压缩的，字母表是原版自带的可配置项。

## 下一步（按价值排序）

1. **E8**：`/botid` 与 `/payload` 的请求形状 —— 反编译 `HyperSolutionsSolver` 的调用点，或找 body 字段名。
2. **C8**：`SolveAsync` 的伪代码 —— cd 公式。
3. **H2/H3**：站点维度 —— 哪些站走哪条路。
4. **E10**：`BotID` 族归属。
5. **A5**：shim 内容（可能永远 Unk，需说明为什么）。

## 复算

```powershell
python analysis\ida.py str Kasada              --limit 400   # total = 57
python analysis\ida.py str hypersolutions      --limit 30    # total = 9
python analysis\ida.py str HyperSolutionsSolver --limit 5    # total = 1 → 0x143321c61
python analysis\ida.py str kasadaRequest       --limit 5     # total = 1
python analysis\ida.py str LzAlphabet          --limit 10    # total = 5
python analysis\ida.py str MoveMouseAndClick   --limit 10
python analysis\ida.py str BotID               --limit 10
```
