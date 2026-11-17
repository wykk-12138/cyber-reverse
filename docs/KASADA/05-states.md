# 05 · 状态机、字段与失败文案

> 这份是照抄用的：想在 UI 上显示、想区分"该重试还是该换代理"，就得用原版同一套词汇。
> 所有地址为 `ida.py str` 返回的真实 VA（`imagebase 0x140000000`）。

---

## 1. 两个 handler，两套状态机（[Obs]）

同一批方法名出现两次，`d__` 编号差 14：

```
A 组（KasadaHandler）        0x14345abb1
  <HandleResponse>d__32   <GetScript>d__33   <GetKasada>d__34   <GetWorkTime>d__35
  <Reset>b__30_0   <GetKasada>b__34_0/1/2

B 组（KasadaMobileHandler）  0x14345a632
  <HandleResponse>d__46   <GetScript>d__47   <GetKasada>d__48   <GetMfc>d__49   <GetWorkTime>d__50
  <-ctor>b__43_0   <Reset>b__44_0   <GetKasada>b__48_2   <GetMfc>b__49_1
```

**两组唯一的实质性差异**：B 组多一个 **`GetMfc`**，且 `GetKasada` 的 lambda 编号不同。
⇒ **移动版不是"另一份实现"，是同一流程多插了一个阶段**。移植时按"加一个可选阶段"处理，不要复制两套。

`GenerateSensor` / `GetSensorData` / `GenerateSbsd` 也各有多套 `d__` 编号（`7` / `8` / `5` 条命中），
说明**同一个传感器步骤在多个类里各有一份** —— 这是原版"每个店铺各写一份"的结构决定的，不是重复代码。

---

## 2. 九个握手状态字段（[Obs]，逐字）

```
_kasadaCt        0x14345aa56     _kasadaDt     0x14345aa42
_kasadaDv        0x14345aa60     _kasadaSt     0x14345aa6a
_kasadaRst       0x14345aa74     _kasadaFc     0x14345aa7f
_kasadaH         0x14345aa89     _kasadaIm     0x14345aa4c
_kasadaWorkTime  0x14345aa92
```

**这九个字段说明握手结果是被缓存的**，不是每次现算：
`ct` 是凭据；`dt`/`dv`/`st`/`rst` 是时序；`fc`/`h`/`im` 是脚本内部状态；`workTime` 是耗时。

另有三个更外层的：

```
_kasada           0x14370d3d      _kasadaMobile   0x143370d5b      _accountKasada   0x14337b669
```

`_accountKasada` 说明**凭据的宿主是账号**，不是任务、不是请求 —— 移植时把 token 与 UA 存在账号对象上。

---

## 3. 属性表（[Obs]，`str` 真值）

```
get_Script / set_Script          get_BasePath / set_BasePath
get_KasadaCt / set_KasadaCt      get_Bmsz / set_Bmsz      ← Bmsz 属 Akamai，见 07
get_CookieName / set_CookieName  get_IpsUrl / set_IpsUrl
get_KasadaVersion                get_MfcEnabled / set_MfcEnabled   0x14345a802
get_IsMobile / set_IsMobile      get_VersionProvider / set_VersionProvider
```

代表地址（全部 `str` 真值）：

```
get_Script     0x1434486b1     get_BasePath   0x1434486c7
get_KasadaCt   0x1434486e1     get_Bmsz       0x1434486fb
get_CookieName 0x14344870d     get_IpsUrl     0x14344872b
get_WorkTime   0x143448830     get_KasadaVersion 0x143370826
get_MfcEnabled 0x14345a802     set_MfcEnabled 0x14345a811
```

这组属性的存在本身就是规格：**一次握手需要知道 script 正文、base 路径、ct、cookie 名、ips 地址、版本**。
按这个字段集建模，移植到别的语言时不会漏。

> **`Bmsz` 不是 Kasada 的**（`get_Bmsz` 与 `GetBmszCookie` 同族）——`bm_sz` 是 Akamai 的 cookie。见 07。

---

## 4. 全部失败/进度文案（[Obs]，逐字 + 地址）

全部地址由 `python analysis\ida.py str Kasada --limit 200` 得到（`total = 57`，`saturated = false`），可直接复核：

```
Getting Kasada (                    0x146da174c    编号前缀
Getting Kasada (1)                  0x146da1784    **走服务商**（HyperSolutions /payload）
Getting Kasada (2)                  0x146da17c4    **直连店铺自己的 Kasada 端点**（带全套 Chrome 头）
Getting Kasada (MFC)                0x146da1804    移动构型变体
Failed getting Kasada               0x146d8a5e4    getting 路失败
Failed getting Kasada (Rotating)    0x146d8a624    getting 失败且正在换代理
Failed solving Kasada               0x146d8a94c    solving 路失败
Failed solving Kasada (TL)          0x146d8a98c    solving 在 TL（`reload`）阶段失败 — 见 01 §7
Failed Kasada (Retry limit reached) 0x146d8a2b4    整条策略放弃
Kasada API down (Contact staff)     0x146dda8dc    服务商不可达（运营问题）
Kasada-Fallback                     0x146dda934    降级 token
Kasada-Mobile-Fallback              0x146dda96c    移动降级 token
```

> **`(1)` 与 `(2)` 不是重试关系**（本轮纠正）：`(1)` 打 `kasada.hypersolutions.co/payload`，
> `(2)` 打店铺自己的端点 —— 两条完全不同的路被编成了同一个文案族。细节见 02 §1.5.3。

> 复算时注意：`str Kasada` 的 `total` 是 **57**，不是早期以为的"≥40"。`--limit` 给 200 才不会饱和。

**移植时照抄这些串**，因为它们是**行为契约**：看到哪个串就知道"走的是哪条路、败在哪一步"。
自己发明词（"kasada failed"）会丢掉这个信息量。

---

## 5. 重试策略（[Inf]，由文案反推）

| 文案 | 含义 | 该做什么 |
|---|---|---|
| `Getting Kasada (1)` → `(2)` | 服务在重试，编号递增 | 继续等，别插手 |
| `Failed getting Kasada (Rotating)` | 服务失败 **且代理在换** | 不要立刻重发 —— 代理换了，旧 token 全废 |
| `Failed solving Kasada` | 本机算失败 | 补 shim / 换浏览器路；**不要**重发同一份脚本 |
| `Failed solving Kasada (TL)` | 本机在 TL 阶段失败 | 同上，但可以只重跑该阶段 |
| `Kasada API down (Contact staff)` | 服务不可达 | 切回本地路；**不要**无限重试服务 |
| `Failed Kasada (Retry limit reached)` | 策略放弃 | 换代理 + 换 UA，重开整轮 |

**一句话**：`Rotating` 与 `Retry limit reached` 是两个明确的"停/换"信号，
其余都是"再试一次本阶段"。把这条规则硬编码进重试器，比任何指数退避都可靠。

---

## 6. 复算

```powershell
python analysis\ida.py str Kasada --limit 200        # 期望饱和（>200 条）
python analysis\ida.py str "Failed solving Kasada" --limit 10
python analysis\ida.py str GetMfc  --limit 10        # 含 d__49 / b__49_0 / b__49_1
python analysis\ida.py str MfcEnabled --limit 5
```

> `str` 的参数带空格时会被 PowerShell 拆开 —— 用双引号包住，或改查单词（`Kasada`）。
