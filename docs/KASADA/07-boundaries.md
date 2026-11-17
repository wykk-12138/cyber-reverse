# 07 · 边界：Kasada 不是 Akamai，也不是 Cloudflare

> 这一份是为**防止把三家风控的能力混成一个**而写的。混淆的代价不是学术性的：
> 你会把 Akamai 的字段当成 Kasada 的需求去实现，然后在真站点上失败，再把失败归因给"Kasada 太难"。

---

## 1. 三家的指纹别名对照（[Obs]）

| 厂商 | cookie / 标识 | 脚本标识 |
|---|---|---|
| **Kasada** | `KP_UIDz` · `kpsdk-*`（`kpsdk-ct` 等） | `ips.js` · `x-kpsdk-*` · `KPSDK` 全局 |
| **Akamai** | `ak_bmsc` · `bm_sz` · `_abck` · `mrk_atkr` | `SBSD` / `SDS` 阶段的 sensor |
| **Cloudflare** | `__cf__client__uuid` · `cf_clearance` | `challenge-platform` / `cf-chl` |

**这四条 cookie 名在二进制里是同一条清单**（[Obs]，`0x146dd97d4`，同族还有 `0x146dd9834` / `0x146dd9894`）：

```
KP_UIDz|ak_bmsc|__cf__client__uuid
```

也就是说：**原版自己就把三家合在一张表里处理**。看到这条清单时不要以为"这些都是 Kasada 的" ——
它是"该清理/该持久化的设备标识候选表"，横跨三家。

---

## 2. Akamai 一族在二进制里的样子（[Obs]）

```
Generating Sensor (1)           0x146d9c024
Generating sensor (A)           0x146d9c0a4
Generating sensor (AWS)         0x146d9c0e4
Generating sensor (P)           0x146d9c12c
Generating sensor (SBSD)        0x146d9c16c
SBSD API down (Contact staff)   0x146e73444
SBSD Solving failed (Retrying)  0x146e73494
SBSD failed (Retrying)          0x146e734ec
Solving Akamai (                 0x146e93ae4
Solving Akamai (SBSD)           0x146e93b1c
Solving Akamai (SDS)            0x146e93b5c
SbsdRequest                     0x146e7a25c
GetBmszCookie                   0x14331c25a
get_Bmsz / set_Bmsz             0x1434486fb / 0x143448704
```

> 全部由 `str` 复核过（`str "SBSD API down"` → `0x146e73444`；`str "Generating sensor"` → 5 条；`str "Solving Akamai"` → 3 条）。

### 2.0 Akamai 的传感器有**五种变体**（[Obs]）

`Generating sensor (1)` / `(A)` / `(AWS)` / `(P)` / `(SBSD)` —— 五个并列的传感器类型。
**[Unk]** 各自的展开；只能确定它们是并列的，不是阶段（编号不递增），所以是**按场景选类型**，不是按顺序推进。

### 2.1 由此可确定的三件事

1. **`SBSD` 是 Akamai 的阶段名**（`Solving Akamai (SBSD)` / `(SDS)` 直接把厂商名与阶段绑在一起）。
2. **Akamai 也有"API down"**：`SBSD API down (Contact staff)` 与 `Kasada API down (Contact staff)` 句式完全一致
   ⇒ 两家都是"有本地路 + 有服务路"的双轨结构，不是 Kasada 独有。
3. **`Bmsz` / `GetBmszCookie` 属于 Akamai**（`bm_sz` 是 Akamai Bot Manager 的 cookie）。

---

## 3. 四个已经踩过的误判（写下来是为了不再犯）

### 3.1 把 `GenerateSbsd` / `GetSbsdData` 当成 Kasada 的步骤

早期文档（`replica/docs/FUNCTION_PARITY.md` §3.2）把
`GetScript` / `GenerateSensor` / `SubmitSensor` / `GetSensorData` / `GetKasada` / `GenerateSbsd` / `GetSbsdData` / `Generate`
列成一串"Kasada 步骤名"。

**实际是混的**：`GenerateSbsd` / `GetSbsdData` / `SbsdRequest` / `Bmsz` 都是 **Akamai** 的（§2）。
Kasada 侧对应的是 `GetKasada` / `GenerateSensor` / `SubmitSensor` / `GetSensorData`。

**教训**：一串方法名里有多个厂商的词汇时，**先按厂商分桶再建模**。这一步不做，后面所有进度都会被虚高。

### 3.2 用一条失败证据推出"原版不用 JS 引擎"

早期结论（`replica/docs/HISTORY.md` §6.78）：

> Jint 跑到 91.8% 死在 `Cannot read properties of undefined (reading 'bind')`
> **⇒ 结论：原版内置 Chromium**，它的 Kasada 不是"自主在 JS 引擎里算"

**这条结论过强。** 今天可核的事实是：**Jint 与 DotNetBrowser 同时存在**（06 §4.1），
Jint 还被 AOT 编译进去（`Jint.EnableHostContractVerification`）、还带着完整语句类族 ——
**一个不被使用的引擎会被 trim 掉**。

那 91.8% 证明的是什么？**证明"裸引擎 + 不全的 shim"跑不完**，不证明原版没这条路。
原版与该实验的差别就在 shim 的覆盖面 —— 而那正好是我们观察不到的部分（06 §5 已标 Unk）。

**教训**：一次失败只否证"我的配方"，不否证"这条路"。

### 3.3 把 `KasadaCdSolver` 的 `Cd` 猜成 Chrome Driver

早期文档写过"`Cd` 大概率是 Chromium/Chrome Driver"。

**没有证据支持这个读法。** 更自然的读法是 **`x-kpsdk-cd`（client data）** —— 因为同一个代码区里
`_kasadaCt` / `_kasadaCd` 这一族字段就是协议头的投影，而 `KasadaCdSolver` 与 `KasadaSolveRequest/Result` 同族。

**仍属 Inf**，但**方向反了**：不是"用浏览器解"，而是"专门处理需要 cd 的场景"。

### 3.4 早期断言"二进制里没有 kpsdk 字符串"

早期（`analysis/verdict_kasada_section.md` §"两个诚实的不确定"）写过：

> 原版二进制里**没有 `kpsdk` 字符串** —— header 名是运行时拼的（`"x-kpsdk-" + suffix`）

**已撤销。** `ida.py str kpsdk` 现在是 **total 17 / saturated=false**，九个头名逐个都在（`x-kpsdk-cd` 到 `x-kpsdk-v`）。

**原因**：当时用的是**抽样字符串池**，不是数据库本身。池是 180,228 行，IDB 有 324,895 条 —— 池里没有 ⇏ 镜像里没有。

**教训**：反向结论（"没有"）只能用查数据库的工具（`ida.py str`）下，不能用抽样池。

---

## 4. 一张决策表：遇到某个标识时先问"这是哪家"

| 你看到的 | 是哪家 | 该找什么 |
|---|---|---|
| `kpsdk` / `x-kpsdk-*` / `KPSDK` / `ips.js` / `KP_UIDz` | **Kasada** | 01–05 本目录 |
| `SBSD` / `SDS` / `bm_sz` / `_abck` / `ak_bmsc` / `sensor_data` | **Akamai** | 另一套（sensor 端点、`_abck` 轮换） |
| `cf-chl` / `challenge-platform` / `cf_clearance` / `__cf__client__uuid` | **Cloudflare** | 另一套（challenge 平台 + clearance cookie） |
| `captcha-delivery` / `datadome` | **DataDome** | 另一套 |
| `px-captcha` / `_px3` | **PerimeterX** | 另一套 |
| `queue-it` / `queueit` | **Queue-it**（排队，不是墙） | 排队 token，不是风控解 |

---

## 5. 复算

```powershell
# 三家的别名同框（这是"合表"的直接证据）
python analysis\ida.py str KP_UIDz --limit 10        # total = 3

# Akamai 阶段名
python analysis\ida.py str SBSD    --limit 20
python analysis\ida.py str Bmsz    --limit 10

# Kasada 侧
python analysis\ida.py str kpsdk   --limit 40        # total = 17
python analysis\ida.py str 149e9513 --limit 20       # total = 5
```

两家都有 `API down (Contact staff)`：

```powershell
python analysis\ida.py str "Kasada API down" --limit 5
python analysis\ida.py str "SBSD API down"   --limit 5
```

> 带空格的 pattern 在 PowerShell 里会被拆开 —— 加双引号，或者改查单词后用 `tar` 过滤。
