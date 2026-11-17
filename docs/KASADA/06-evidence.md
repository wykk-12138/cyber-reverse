# 06 · 证据索引与分级

> 这份是"别信我，自己算"用的。每条结论 → 哪条命令、哪个地址、属于哪一级。

---

## 1. 分级定义

| 级 | 含义 | 判定标准 |
|---|---|---|
| **Obs** | 从产物里直接读到 | 有地址 + 有可重跑的命令 |
| **Inf** | 由多条 Obs + 公开协议推出 | 写明依据了哪几条 Obs |
| **Unk** | 没查到 | 写明缺什么判据 |

**反编译不在 Obs 里。** 原版 96.87% 的函数是 `sub_*`（321,244 个函数里 311,203 个无名字），
反编译能给你控制流，给不了"这个字符串是站名还是字段名"。所以本文档的 Obs 全部来自**字符串池与反射元数据** —— 那是 NativeAOT 里唯一保真的部分。

---

## 2. 地址换算（这里有个坑，先说清）

`analysis/pe_strings.txt` 里的偏移是**文件内偏移**，`ida.py str` 返回的是**虚拟地址**（`imagebase 0x140000000`）。

实测下来，差值**按池段位分成两档**（每档都有多个样本验证过）：

| 池段位 | 差值 | 已验证的样本 |
|---|---|---|
| `0x03xxxxxx` | **+0x140000e00** | `get_KasadaCt` · `get_Script` · `get_BasePath` · `get_CookieName` · `get_IpsUrl` · `get_KasadaVersion` |
| `0x06xxxxxx` | **+0x140001400** | `Kasada-Fallback` · `Kasada-Mobile-Fallback` · `Kasada API down` · `SBSD API down` · `Generating sensor (SBSD)` · `Solving Akamai (SBSD/SDS)` · `KP_UIDz` 清单 |
| `0x07xxxxxx` | **未验证** | —（本文档遇到 0x07 段一律标"池偏移"而不给 VA） |

示例（两边都对得上）：

```
池 0x06dd9534 + 0x140001400 = 0x146dda934   ← str Kasada-Fallback 返回一致
池 0x034478e1 + 0x140000e00 = 0x1434486e1   ← str get_KasadaCt   返回一致
```

**⇒ 规则：能算，但必须复核。** 凡是本文档里给了 VA 的，都用 `ida.py str` 对过；
凡是只标"池偏移"的，说明它在 `0x07` 段或没来得及核。把换算写成单一常量会在另一段上错 0x1400 字节 ——
那种错误看不出来，只会让人查到隔壁的字符串（我在写这份文档时就犯了两次，已被 `str` 抓出来）。

---

## 3. 命令总表（按结论分组）

```powershell
# ── 引擎：Jint（方案一的地基）─────────────────────────────────
python analysis\ida.py str Jint                  --limit 100   # total >= 81
python analysis\ida.py str Acornima              --limit 20
python analysis\ida.py str JintBlockStatement    --limit 5
python analysis\ida.py str EnableHostContractVerification --limit 5   # AOT 开关

# ── 引擎：Chromium（方案二的地基）─────────────────────────────
python analysis\ida.py str DotNetBrowser         --limit 60    # total >= 12
python analysis\ida.py str Chromium              --limit 60
python analysis\ida.py str cybersole-chromium    --limit 5

# ── 方案一的直接证据（原版自己的方法名）──────────────────────
python analysis\ida.py str DoChallenge           --limit 20    # total = 4
python analysis\ida.py str GenerateJavascriptToken --limit 10  # total = 4
python analysis\ida.py str KPSDK                 --limit 40    # 含 KPSDK.scriptStart

# ── 方案三/四（服务通道与降级）───────────────────────────────
python analysis\ida.py str IKasadaSolver         --limit 5
python analysis\ida.py str KasadaSolve           --limit 10
python analysis\ida.py str SolverInstruction     --limit 10
python analysis\ida.py str MfcEnabled            --limit 5

# ── 状态机 ────────────────────────────────────────────────
python analysis\ida.py str Kasada                --limit 200   # 饱和；含两套 d__ 编号
python analysis\ida.py str GetMfc                --limit 10
python analysis\ida.py str _kasada               --limit 30

# ── 协议字面量 ────────────────────────────────────────────
python analysis\ida.py str kpsdk                 --limit 40    # total = 17
python analysis\ida.py str 149e9513              --limit 20    # total = 5
python analysis\ida.py str KP_UIDz               --limit 10    # total = 3
python analysis\ida.py str x-kpsdk               --limit 40
```

---

## 4. 关键地址表

### 4.1 引擎

| 项 | 地址 | 级 |
|---|---|---|
| `Jint, Version=4.17.0.0, …` | `0x146dd37ac` | Obs |
| `Sebastien Ros@Javascript interpreter for .NET.` | `0x14316ea8d` | Obs |
| Acornima 描述（Esprima.NET fork） | `0x14315d5ef` | Obs |
| `Jint.EnableHostContractVerification` | `0x146dd3aac` | Obs |
| `Jint.Native.Intl.Data.LikelySubtags.txt` | `0x146dd3b0c` | Obs |
| `JintBlockStatement` 等语句类 | `0x1434cb5dd` 一带 | Obs |
| `DotNetBrowser` | `0x14315a15d` | Obs |
| `ChromiumBinariesExtractor` | `0x1432bb1c5` | Obs |
| `.cybersole-chromium.xml` | `0x14336a99f` | Obs |

### 4.2 方法名（这是"原版怎么做的"最硬的证据）

| 项 | 地址 | 级 |
|---|---|---|
| `DoChallenge.GenerateJavascriptToken` | `0x14345d611` | Obs |
| `<<GenerateJavascriptToken>d__47` | `0x14345cee0` | Obs |
| `<DoChallengeAsync>d__43` | `0x14345cea3` | Obs |
| `GenerateSensor`（7 条：d__5/9/11） | `0x143311103` 一带 | Obs |
| `GetSensorData`（8 条：d__30/34） | `0x14331b944` 一带 | Obs |
| `GenerateSbsd`（5 条：d__34/38） | `0x14331bca1` 一带 | Obs |
| `IKasadaSolver` | `0x1433216f6` | Obs |
| `KasadaSolveRequest` / `KasadaSolveResult` | `0x1433218dc` / `0x143321733` | Obs |
| `KasadaCdSolver` | `0x143321dfa` | Obs |
| `KasadaHandler` / `KasadaMobileHandler` | `0x143334518` / `0x143334b22` | Obs |

### 4.3 握手状态字段与方案

| 项 | 地址 | 级 |
|---|---|---|
| `_kasadaCt` … `_kasadaWorkTime`（九个） | `0x14345aa42`–`0x14345aa92` | Obs |
| `_accountKasada` | `0x14337b669` | Obs |
| 状态机 A 组（d__32–35） | `0x14345abb1` | Obs |
| 状态机 B 组（d__46–50，含 `GetMfc`） | `0x14345a632` | Obs |
| `KPSDK.scriptStart` | `0x146dd9774` | Obs |

### 4.4 协议

| 项 | 地址 | 级 |
|---|---|---|
| script id（Nike） | `/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3` | Obs |
| `/ips.js?` / `/fp?x-kpsdk-v=` / `/prop.json` / `/a-4-a/c.js` | 见 `01-protocol.md` §2.1（池偏移） | Obs |
| 九个 `x-kpsdk-*` 头 | `0x1471881a4` 一带 | Obs |
| `KP_UIDz\|ak_bmsc\|__cf__client__uuid` | `0x146dd97d4`（真 VA，同族另有 `0x146dd9834` / `0x146dd9894`） | Obs |
| sensor payload 样本 | 池偏移 `0x07191c6c`（**VA 未复核**，0x07 段差值未验证） | Obs |
| per-store 版本头（7 个） | 池偏移 `0x06b9ec2c` 一带（`Converse-Kasada-Version` 等） | Obs |

---

## 5. 每条主要结论的级别

| 结论 | 级 | 依据 |
|---|---|---|
| 原版内嵌 Jint 4.17.0 并被 AOT 编译 | **Obs** | 程序集全名 + AOT 开关 + 语句类族 |
| 原版同时内嵌 DotNetBrowser 4.3.5 | **Obs** | 程序集族 + Chromium 提取器 + 标记文件 |
| 有"在 JS 里生成 token"的方法 | **Obs** | `DoChallenge.GenerateJavascriptToken` |
| Nike 的常规路径是 Jint 而非浏览器 | **Inf** | 上三条 + 该站点脚本特征；**缺一条**：Jint 引擎与该方法的调用链关系 |
| 四种模式（getting/solving/fallback×2） | **Obs** | 文案动词 + `IKasadaSolver` 接口 + 两个 fallback 名 |
| 服务通道是 protobuf 分阶段协议 | **Inf** | 字段表 + 一条 base64 样本里可读出的 `stage/ReceiveHeaders/target` |
| `x-kpsdk-cd` 用于 body 加密 | **Inf** | 字段名 + Kasada 公开行为；原版把它单独建模（`ClientData`） |
| 九个头的**每个**语义 | **Unk** | 只知道名字与分组；`dt/dv/fc/h/im` 的语义没有证据 |
| `TL` 的展开 | **Unk** | 只有一条失败文案 |
| `MFC` 的展开 | **Unk** | 只有 `GetMfc` + `MfcEnabled/IsMobile/VersionProvider` |
| 原版 shim 具体注入了什么 | **Unk** | Jint 侧只有引擎证据；shim 内容无从观察。03/02 的清单来自**浏览器实测缺口**，不是原版 |
| `KasadaCdSolver` 的 Cd 是什么 | **Unk** | 名字指向 `x-kpsdk-cd`（Inf 级猜测），无实现证据 |

---

## 6. 复算时最容易犯的四个错（都犯过）

1. **把 `--limit` 当总数。** `ida.py str` 现在回三个键：`returned` / `saturated` / `total`。`saturated=true` 时 `total` 是 `"at least N"`，不能当结论。
2. **把零当"没有"。** 池是抽样（180,228 行 vs IDB 的 324,895 条字符串）。反向结论只能用 `ida.py str`（查数据库本身）。
3. **拿假阳性当发现。** `Jurassic` 是店名，`Chakra` 是字体名。任何"引擎名"命中都要读完整串再下判断。
4. **用像素偏移直接算 VA。** 见 §2：差值是浮动的，必须复核。
