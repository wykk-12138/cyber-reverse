# Kasada 技术档案（从 Cybersole 5.18.32 逆向恢复，可移植）

> **这份目录回答一个问题：一个桌面自动化客户端怎样在不接第三方打码/解题服务的前提下，让请求带上合法的 Kasada 凭据。**
>
> 材料有两个来源，每条结论后面都标了它属于哪一类：
>
> - **Obs（Observation）** —— 从 `target\Cybersole.exe`（.NET 10 NativeAOT，无 IL）里直接读到的字符串/元数据/符号，附地址，可用本文档的命令重算。
> - **Inf（Inference）** —— 由多条 Obs 加上 Kasada 的公开协议推出的做法，未在运行时验证。
> - **Unk（Unknown）** —— 明确没查到的东西，写清缺什么判据。
>
> 复刻件（`replica/`）的实现**不算证据**：它是我们自己的产出，引用它就是循环论证。文中提到它只用来标"我们踩过哪个坑"。

---

## 30 秒速览

Kasada 不是验证码，是**客户端完整性校验**：站点加载 `ips.js`，脚本在本地跑出一组请求头（`x-kpsdk-*`），服务端验签。所以"解 Kasada"不需要识图，只有两条正路 —— **自己跑那份脚本**，或**借一个真浏览器跑那份脚本**。

Cybersole 的做法是**四条路 + 一套统一状态机**（Obs，见 `06-evidence.md`）：

| 模式 | 触发条件 | 实现 |
|---|---|---|
| `Local`（Jint） | 默认 | 内嵌 **Jint 4.17.0** 解释器 + 自建浏览器 shim，在本进程里执行店铺的 `ips.js` |
| `Local`（浏览器） | 脚本需要 Jint 给不了的宿主 API | 内嵌 **DotNetBrowser 4.3.5**（完整 Chromium，**池化 + 信号量**），让真页面自己算 |
| `Api` | 配置了远端 solver | **HyperSolutions** 的服务通道：`kasada.hypersolutions.co/{botid,payload}`，代理式转发 |
| `Fallback` / `MobileFallback`（MFC） | 前两条都失败 | 降级通道，名字直接写在状态文案里 |

### 最重要的一条结论（`08-cd.md` §11）

**客户端自己不算，只搬运。** 九个头在本地的每个写入点都是「从 HTTP 响应头取出来，存进记录」，
没有任何一处实现 Kasada 的算法 —— 算法在 `ips.js` 里（本地路）或在服务商那侧（Api 路）。

这条一次性解释了三件看起来矛盾的事：

1. **"体感跟自主生成一样"** —— 确实不调外部服务（本地路），但也不是自己算；
2. **100 个任务占用不高** —— 客户端只是 JS 解释器 + 一个**池化**浏览器（`_browserSemaphore`）+ 字段搬运，
   没有每任务一套重型进程；
3. **`Reset` 一次清六个槽位** —— 那六个是"这一次握手的全部结果"，拿旧 `ct` 配新 `st` 就是一次不可能的组合。

### 还有一个常被问的：`x-kpsdk-cd` 有自己的算法吗

**没有。** `Sha256Hex` / `HashDifficulty` / `RandomAddSubtract` 那一批看着像算法，但它们所在类型里有 `get_Bmsz`，
同族有 `IAkamaiGenerator` —— **那是 Akamai 的 PoW**。Kasada 的 cd 只有两个来源：脚本产出、服务商响应。
详见 `08-cd.md` §10.3。

---

## 文件索引

| 文件 | 内容 | 复用场景 |
|---|---|---|
| [01-protocol.md](01-protocol.md) | **协议规格**：脚本 id、端点、九个头、cookie、sensor payload | 任何语言、任何站点 |
| [02-local-jint.md](02-local-jint.md) | **方案一**：Jint 本地执行 `ips.js`（主路，含可跑代码与踩坑） | 想零浏览器依赖、要低内存高并发 |
| [03-browser.md](03-browser.md) | **方案二**：真浏览器（DotNetBrowser / 手写 CDP） | 脚本用到 Jint 无法模拟的 API |
| [04-remote-api-fallback.md](04-remote-api-fallback.md) | **方案三/四**：远端 solver 通道、Fallback、MFC 移动降级 | 有服务端资源、或要兜底 |
| [05-states.md](05-states.md) | **状态机与文案契约**：两套 handler、`d__` 编号、全部失败串 | 照抄 UI 状态、做超时与重试策略 |
| [06-evidence.md](06-evidence.md) | **证据索引**：地址表、复算命令、分级 | 想自己重算，不想信我 |
| [07-boundaries.md](07-boundaries.md) | **边界**：Kasada ≠ Akamai ≠ Cloudflare（含四个已犯过的误判） | 避免把 SBSD/bm_sz 当成 Kasada |
| [08-cd.md](08-cd.md) | **`x-kpsdk-cd` 专章**：本地算法类型的成员表、payload 对照、两条本地实现 | 想搞清 cd 到底怎么来的 |
| [09-inventory.md](09-inventory.md) | **能力清单（不遗漏的判据）**：A–H 八族、逐条证据、⬜/Unk 缺口 | 想知道还差什么 |

---

## 复算命令（在本仓库根目录执行）

```powershell
# IDA 必须已载入 target\Cybersole.exe.i64（imagebase 0x140000000）
python analysis\ida.py health

# 引擎证据
python analysis\ida.py str Jint          --limit 100   # 期望 total >= 81，含 "Jint, Version=4.17.0.0"
python analysis\ida.py str Acornima      --limit 20
python analysis\ida.py str DotNetBrowser --limit 60    # 期望 total >= 12

# 方法名证据
python analysis\ida.py str Kasada        --limit 200   # 期望饱和（>200），含 IKasadaSolver / KasadaSolveRequest
python analysis\ida.py str DoChallenge   --limit 20    # 期望 total = 4
python analysis\ida.py str GenerateSensor --limit 20   # 期望 total = 7

# 协议字面量
python analysis\ida.py str kpsdk         --limit 40    # 期望 total = 17
python analysis\ida.py str 149e9513      --limit 20    # 期望 total = 5
```

**地址换算（重要）**：`analysis/pe_strings.txt` 里的偏移是**文件偏移**，`ida.py str` 返回的是 VA。
差值按池段位分两档：`0x03xxxxxx` → **+0x140000e00**，`0x06xxxxxx` → **+0x140001400**，`0x07xxxxxx` **未验证**。
例：池 `0x06dd9534 Kasada-Fallback` → VA `0x146dda934`（已用 `str Kasada-Fallback` 核对）。
**本文档里凡给了 VA 的都复核过；只标"池偏移"的说明没核。** 详细规则与已验证样本见 [06-evidence.md](06-evidence.md) §2。

---

## 三条别当耳边风的规则

1. **`total` 不等于 `returned`。** `ida.py str` 报三个键：`returned`（这次回来几条）、`saturated`（是否撞到 `--limit`）、`total`（只有 `saturated=false` 时才是真总数）。撞了上限就写"至少 N 条"。这条在这个项目里已经犯过五次。
2. **一个零需要对照才能读。** `kpsdk` 查到 0 说明不了问题，除非同时查到 `datadome` 之类已知非零的对照。
3. **裸看反编译只有控制流，配 `chars_va - 12` + `names_at.py` 才有完整语义。** 原版 96.87% 的函数是 `sub_*`，无业务符号名；必须先对冻结字符串对象头（`chars_va - 12`）查 `xrefs_to` / `disp32_scan_any.py` 定位业务函数，再用 `analysis/names_at.py` 把伪代码里的 `&off_146xxxxxx` 还原回原始字符串，才能同时拿到精确控制流与协议字段语义（见 [06-evidence.md](06-evidence.md) §2.5）。
