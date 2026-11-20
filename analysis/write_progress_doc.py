"""Write docs/PROGRESS_AND_GAP.md and add pointers from the maintenance docs.

Every figure here comes from docs/METRICS.md (2026-11-20 15:24:49 +0800, all exit 0, no staleness warnings) or from a
tool output captured in this session. Nothing is estimated.
"""

import io

PROGRESS = """# 进度与差距（生成于 R1300，2026-11-20）

> **数字唯一来源**：`docs/METRICS.md`（2026-11-20 15:24:49 +0800，度量脚本全部 exit 0、时效警告为空）。
> 本文只回答两件事：**哪些面已经结案**、**离「核心模块完全逆向」还差什么**。
> 判据 a–f 的逐条证据在 `docs/GOAL_VERIFICATION.md`；本文不重复它。

---

## 一、一句话结论

**判据 a–f 六条全部达标**（那是「证据完整、可复算」的判据）；
**核心模块没有全部逆向完**。已完成的是「主干链路 + 取证台账」，未完成的是
**13 类具体欠账**，其中 5 类需要外部条件、8 类本机可做。

---

## 二、已经结案的面（有数字）

| 面 | 数字 | 命令 |
|---|---|---|
| 站点流程 | `flows 18` · `override steps 369` · **`unknown placeholders 0`** · `provenance exit 0` | `python tools/core_coverage.py` |
| 支付挑战 | `stages 9` · **`markers absent 0/5`** · `control ok True` | `python tools/payment_challenges.py` |
| captcha（识别面） | `families 6` · **`markers absent 0/5`**；四家 loader 字面量全部实证并接进 `StoreFlow.DetectAsync` | `python tools/captcha_coverage.py` |
| 风控厂商 | `controls ok True` · `missing 0` | `python tools/vendor_coverage.py` |
| 名字级绑定 | **`real gap 0`**；`missing 14` = noise 12 + not-in-function-set 2 | `python tools/bind_diff.py --buckets` |
| 类型级绑定 | **`scope misses 0`** | `python tools/bind_scope.py` |
| 类型缺失 | `absent 15` = renamed 13 + not-in-function-set 2 + **`unimplemented 0`** + **`unclassified 0`** | `python tools/bind_diff.py --type-presence` |
| 文案 | **`copy: zones with a missing key 0`** | `python tools/copy_audit_report.py` |
| 数据文件名 | `original-on-disk not in replica 0` | `python tools/datafiles_diff.py` |
| 传输层 | 默认路径与镜像同源：`SocketsHttpHandler` + `SslStream` + `Tls12\\|Tls13` + GREASE + 六个 handler 属性 | 见 `docs/BLOCKERS.md` R1293 |
| 套件 | 全量 `2485 通过 / 0 失败 / 2 跳过 / 2487` | `dotnet test --filter "Speed!=Slow" -m:1` |
| 变异 | **`59 fired / 0 decorative / 0 skipped`** · `staleness 0` | `python tools/mutation-check.py` |

---

## 三、核心模块逐项状态

图例：**✅ 结案**（证据齐全、无待办） · **🟡 部分**（有实现但还剩明确条目） · **⛔ 外部阻塞**

### ① 站点与结账流程（`Cybersole.Stores/Flows`）

| 项 | 状态 | 差什么 |
|---|---|---|
| 18 个 Flow / 369 个 override step | ✅ | 占位零、provenance exit 0 |
| 62 个店铺 → 18 个 Flow 的映射 | ✅ | 共用 Flow 由 `StoreRegistry` 决定（`store_catalog.py` 62 与 `DocsConsistencyTests` 交叉校验） |
| **per-store 差异** | 🟡 | `Stores/Flows` 的 **24 条 `inferred`** 已全部查过 324,901 条字符串 dump：**1 命中**（`/rest/V1` @`146AB72A4`）、**23 条 0 命中**。按 R1266（哈希差分已证 NativeAOT 部分串逐字节不可搜），0 命中只能读作 **unknown**，要 live capture |
| Farfetch 7 条 | ⛔ | `connect/app` 是**服务端下发**配置，schema 需原版登录（R1077 反编译结论；R1294 已按此分类结案） |
| `connect/app` channel payload 字段 | ⛔ | 同上，需登录后的真实响应 |

### ② 支付与客户端校验层

| 项 | 状态 | 差什么 |
|---|---|---|
| PayPal 3DS 九阶段 | ✅ | `PayPalThreeDs.cs` 1608 行；四份 GraphQL 文档全文；`stages 9 / markers 0/5` |
| Stripe 六端点 | ✅ | `descriptor` 面已落地（`GetStripePaymentIntent` / `CreateStripePaymentMethod` / `ValidateStripeIntent` / `StripeFallbackHandler` / API 版本 `2025-08-27.basil`） |
| Stripe 四构建器的**派发关系** | 🟡 | 文档记为 Unknown：四个构建器经 delegate/虚表间接派发，其 thunk 与存放槽（`0x147228EF8` / `0x1472279C8`）自身无 xref，**静态不可得** |
| captcha **识别面** | ✅ | 四家 loader 字面量 + `CaptchaSurface.Classify` + 接进 `DetectAsync` |
| captcha **执行面**（3 项） | ⛔ | `HCaptchaSpoof` / `RecaptchaEnterprise` / `TurnstileSiteKey`：原版在嵌入式 **DotNetBrowser 4.3.5.8591 + 外部 Chromium**（`DOTNETBROWSER_CHROMIUM_DIR`，AOT 须手工预置）里跑 `enterprise.execute()` 与 `turnstile.render()`。复刻件无该引擎，接入＝引入新依赖 |

### ③ 传输层（`Cybersole.Http`）

| 项 | 状态 | 差什么 |
|---|---|---|
| 默认路径 | ✅ | `NetClient` 六属性：`Tls12\\|Tls13`、`CipherSuitesPolicy`、ALPN、`MaxAutomaticRedirections=10`、`AutomaticDecompression=All`、`UseCookies` —— 全是平台同名属性，与镜像所用 `SocketsHttpHandler` 同源 |
| Brotli 字典 | ✅ | 122,784 B（RFC 7932 规定值）、`offset 0x62DD580`、标准前缀表；复刻件携带同一份。**限制**：.NET 8 的 `BrotliDecoder`/`BrotliStream` 不暴露字典参数 |
| `OwnTls` 自写栈 | 🟡 | 只提供 TLS 1.2，握手字节永不等于平台；**刻意保留**作指纹实验路径，非生产 |
| HTTP/3 是否真启用 | 🟡 | 镜像只有 `SocketsHttpHandler.Http3Support` 开关字符串，**无协商证据** |

### ④ UI 绑定与本地化（冻结面）

| 项 | 状态 | 差什么 |
|---|---|---|
| `real gap` / `unclassified` | ✅ | 均为 0 |
| 文案缺口 | ✅ | 0 |
| **`only in descriptors 137`** | 🟡 | 原版绑定描述符里 **137 条**只在描述符表、不在 XAML 表。`METRIC_CLAIMS.md` 只写了「差集那一侧不等于 XAML 没用它」，**这 137 条从未逐条看过** |
| **`shape mismatches 91`（core 3）** | 🟡 | 已列 `docs/SHAPE_GAPS.md` 并逐条处置过一轮，但 91 条未全部结案 |
| `datafiles: replica-only 2` | 🟡 | 复刻件提到 2 个原版数据目录与镜像字面量都查不到的文件名 |
| `AuthWindow` / `LicenseControl` | ✅（裁决） | R702 判 `NOT_IN_FUNCTION_SET`，见 `docs/DECISION_LICENSE_OUT_OF_SCOPE.md` |

---

## 四、为什么「函数数量」不能当完成度

`functions: 277,120 ↔ 179,840 = 64.90%`、`section-mass 57.09%` 这两个数**记录在案但不构成完成度**。证据是 .pdata 地址桶对照：

```
range        original   replica   replica/original
0x0             5,475     1,937        35.4%
0x600000        1,074     4,199       391.0%
0x1100000       2,020     9,500       470.3%
0x1200000       2,046    10,220       499.5%
0x1600000       2,864     9,730       339.7%
```

两侧代码**布局完全不同**（同样大小的桶里，复刻件的函数数可以是原版的 35%，也可以是 500%），
所以桶与桶之间没有对应关系，**无法从 64.90% 推出「实现了 64.9% 的功能」**。

要做成有意义的对照，需要**按模块归属**而不是按地址：原版无符号名，只能靠 IDA 里的字符串/描述符归属反推。
**这个分析从未做过**（列为第五节第 2 项）。

---

## 五、差距清单

### 本机可做（8 项，按性价比排序）

| # | 待办 | 为什么值得先做 |
|---|---|---|
| 1 | **137 条 only-in-descriptors 逐条分类** | 唯一一个「有明确数字、完全没查」的洞；分类后能把绑定面从「差集未知」变成「差集已解释」 |
| 2 | **函数分布按模块对照** | 决定 64.90% 里「框架差异」与「真没实现」各占多少；不做这一步，任何完成度都是猜 |
| 3 | `shape mismatches 91`（core 3 优先） | 绑定形状逐条结案，`SHAPE_GAPS.md` 已有底子 |
| 4 | `datafiles: replica-only 2` | 确认这 2 个名字是复刻件虚造还是原版运行时拼接 |
| 5 | Stripe 四构建器派发关系 | 目前判「静态不可得」，可用 `disp32_scan_any.py` 再扫一遍存放槽 |
| 6 | HTTP/3 是否真启用 | 需要一条能让原版走的请求路径；只有开关字符串不足 |
| 7 | `OwnTls` 的定位写清 | 避免后人把它当生产路径（已在 `BouncyTls.cs` 注释，可再收口） |
| 8 | `vendor named 11` 复核 | IDA 字符串缓存未建完时的**下限**，真值应为 13；缓存就绪后重跑即证 |

### 外部阻塞（5 项）

| # | 待办 | 所缺条件 |
|---|---|---|
| 1 | Farfetch 7 条 + `connect/app` payload | 原版有效登录凭据 |
| 2 | 23 条 `inferred` 的 0 命中 | live capture（真实请求/响应） |
| 3 | captcha 三项执行面 | 浏览器引擎（DotNetBrowser 商业授权，或另行裁决 WebView2/CefSharp） |
| 4 | `BotTask.Running` / `BotTask.Task` 成员类型 | 需运行态观察（同 1） |
| 5 | 8 条 claim 的 `unknown` | 逐条见 `docs/PARITY_CLAIMS.md` 的 `gap_reason` 列 |

---

## 六、判据 a–f 与本文档的关系（防误读）

- `docs/GOAL_VERIFICATION.md` 证明的是：**每一项声明都有 authority、命令、偏差方向**。
- 它**不证明**：功能已 100% 覆盖。
- 四条 claim 判 `fail`（节布局 6↔9、导出面 39↔1、导入面 17/438↔18/409、成员形状 91）都属
  AGENTS §0 明确豁免的「允许内部命名不同、不要求字节级一致」。
- 因此：**判据达标 ≠ 核心模块逆向完**。两者差的就是第五节的 13 项。
"""

POINTER = """
---

## 进度与差距总表（R1300）

**看整体进度先读 `docs/PROGRESS_AND_GAP.md`**：它按 ①②③④ 四个面逐项列状态（✅ 结案 / 🟡 部分 / ⛔ 阻塞），
并给出 8 项本机可做 + 5 项外部阻塞的差距清单。判据 a–f 的逐条证据仍在 `docs/GOAL_VERIFICATION.md`，
但**判据达标不等于核心模块逆向完**——两者差 13 项，明细见该文档第五节。
"""

VERDICT = """
---

## 第 1300 轮：进度与差距落成文档

- 新增 `docs/PROGRESS_AND_GAP.md`：①②③④ 四面逐项状态 + 13 项差距（8 可做 / 5 阻塞）。
- 关键澄清：`functions 64.90%` 与 `section-mass 57.09%` **不构成完成度**——.pdata 桶对照显示两侧布局无对应关系
  （同一桶内复刻件可为原版 35%，也可为 500%）。要得到有意义的对照，须按模块归属而非地址，该分析从未做过。
- 唯一「有数字但完全没查」的洞：`only in descriptors 137`，列为下一步第 1 项。
"""

BLOCKERS = """
## R1300 —— 进度口径定稿：判据达标 ≠ 核心模块逆向完

新增 `docs/PROGRESS_AND_GAP.md` 作为进度总表。三条口径必须一起引用，否则会误读：

1. **判据 a–f 达标**（证据完整、可复算）——见 `docs/GOAL_VERIFICATION.md`；
2. **核心模块未全完**——13 项差距，其中 **8 项本机可做**、**5 项外部阻塞**（原版登录凭据 / 浏览器引擎 / live capture）；
3. **函数数不是完成度**——`277,120 ↔ 179,840 = 64.90%` 只是产物规模比；.pdata 桶对照证明两侧布局无对应关系
   （`0x0` 桶 35.4%、`0x1200000` 桶 499.5%），所以这个比率**不能**读成「实现了 64.9%」。

另：`vendor: named in image 11` 是 IDA 字符串缓存未建完时的**下限**，真值 13；缓存就绪后重跑即证。
"""

for path, text, mode in (
        ('D:/projects/cyber-reverse/docs/PROGRESS_AND_GAP.md', PROGRESS, 'w'),
        ('D:/projects/cyber-reverse/docs/HANDOFF.md', POINTER, 'a'),
        ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', VERDICT, 'a'),
        ('D:/projects/cyber-reverse/docs/BLOCKERS.md', BLOCKERS, 'a')):
    if mode == 'a':
        io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    else:
        io.open(path, 'w', encoding='utf-8', newline='\n').write(text)
    print(('wrote' if mode == 'w' else 'appended'), path)
