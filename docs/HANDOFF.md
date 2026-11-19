# 交接（2026-11-18 路线纠偏后）

> **这一节是「现在在哪」，给新会话第一步读。动态度量数值一律不写在这里** —— 唯一数字源是
> `docs/METRICS.md`（在 `replica/` 下由 `python tools/metrics_report.py` 生成）。
> 完整的新会话接手路由、NativeAOT 反编译 SOP 与未结案核心队列见 **`docs/HANDOFF_PROMPT_antigravity.md`** 与 **`docs/GOAL.md`**。

## 现在在哪

- **轮次与状态**：当前最新提交以 `git log --oneline -5` 为准；开始任何修改前先看 `git status --short`，切勿覆盖并行会话的改动。
- **套件**：绿（具体通过数见 `docs/METRICS.md` 的「完整套件」行）。
- **IDA**：就绪时 `python analysis/ida.py health` 返回 `status=ok` 且 `hexrays_ready=true`。必须在 IDA 在线时再跑 `metrics_report.py`（各覆盖率生成脚本已加 `controls ok` 非零退出守卫，拒写假零）。
- **度量项**：全部汇总在 `docs/METRICS.md` 摘要表里。**不要在任何活文档里硬编码这些数值。**

## 完成判据现状

| 判据 | 状态 | 复算命令 |
|---|---|---|
| (a) 类型级缺口 / 类型缺失 | **类型级已归零**。类型缺失逐条分类见 `docs/TYPE_PRESENCE_TRIAGE.md`（其中 `AuthWindow` / `LicenseControl` 已在 R702 裁决 `OUT_OF_SCOPE` 不做，见 `docs/DECISION_LICENSE_OUT_OF_SCOPE.md`） | `python tools/bind_scope.py`、`python tools/bind_diff.py --type-presence` |
| (b) 文案 | **已归零**（见 `docs/METRICS.md`） | `python tools/copy_audit_report.py` |
| (c) 产物级对照 | **可复算**：函数数、可执行段体量、地址分桶均由 `docs/METRICS.md` 自动生成 | `python tools/func_count.py`、`python tools/pe_sections.py`、`python tools/pdata_sections.py` |
| (d) claim 表 | **PASS**（全表逐行校验 authority + command + gap_reason） | `python analysis/check_claims.py` |
| (e) 套件 / 变异 / 数字来源 | 套件绿；变异测试以 `tools/mutation-check.py` 实测为准；全部活文档数字引用 `docs/METRICS.md` | `python tools/metrics_report.py`、`python tools/mutation-check.py` |
| (f) 核心覆盖 | 覆盖生成物已进 `docs/METRICS.md`；**下一步重点是把核心可执行能力逐项反编译落地（严禁用静态台账类代替运行时实现）** | `python tools/core_coverage.py`、`python tools/vendor_coverage.py` |

## 当前核心待办队列（按 YG 优先级 ①→②→③ 排序，不再从 UI `BINDING_BACKLOG.md` 取件）

1. **[优先级① · Checkout Flow] Nike 结账写入路由与请求体落地**：已通过 `chars_va - 12` 定位出 `checkouts/v3/` 与 `checkout_previews/v3/` 对应的两个可反编译业务函数（详见 `replica/docs/CORE_COVERAGE.md` §二），下一步反编译还原请求体并消掉 `NikeFlow.cs` 中的占位返回；其余含占位步骤的 Flow 同法推进。
2. **[优先级② · 支付挑战层] PayPal 3DS 与 Stripe Challenge 状态机实现**：入口函数与阶段清单见 `replica/docs/PAYMENT_CHALLENGES.md`，反编译后在 `Cybersole.Stores/Payments` 落成真实可执行状态机。
3. **[优先级② · 客户端挑战层] Kasada 本地主路对齐与 Captcha 驱动对位**：按 `docs/KASADA/`（`01`–`09`）与 `replica/docs/CAPTCHA_COVERAGE.md` 已落盘证据，修正 `NikeFlow.cs` / `KasadaSolver.cs` 的主辅路顺序与协议细节，对位各支持家族的驱动载荷。
4. **[优先级④ · 冻结收尾] UI 绑定与视图收尾**：`replica/docs/BINDING_BACKLOG.md` 冻结在最后，仅在 ①–③ 核心项全部结案或均卡外部凭据/裁决时处理。

## 工具的可信边界与工程红线（必读）

- **NativeAOT 冻结字符串定位铁律（`chars_va - 12`）**：冻结 `System.String` 布局为 `[MethodTable*:8][Length:4][UTF-16 chars]`，`ida.py str` 返回 `chars_va`，而 `.text` 代码引用指向对象头 **`obj_va = chars_va - 12`**！必须对 `chars_va - 12` 查 `xrefs_to` 或跑 `python analysis/disp32_scan_any.py` → `site_to_func.py`，再用 `python analysis/names_at.py` 解码伪代码中的 `&off_146xxxxxx`。严禁未减 `12` 就判「无 xref 不可得」。
- **产品代码红线**：**严禁往 `replica/src/` 新增任何静态逆向审计台账/缺口免责类**（如 `*Gaps`、`*Wiring`、`*Witness`）及行数钉子测试；考据写进 `docs/`，`replica/src/` 只写可执行运行时代码。
- **`analysis/pe_strings.txt` 是抽样**：**正向可用、反向不可用** —— 反向结论必须用 `python analysis\ida.py str <pat> --limit N`，并确认 `saturated: false`。见 `AGENTS.md` §2.7b。
- **写实现前先查现成代码**：在 `replica/` 跑 `python tools\where_is.py <名字>`，先读 implementation 组。
- **文档守卫**：`DocsConsistencyTests` 与 `HandoffHeadPointerTests` 会校验模块数口吻与活区块无硬编码度量值；`SourceEncodingTests` 严禁任何乱码样本文本。

## 机器相关

**内存纪律**：`available < 2GB` 只用 `-m:1`；`< 1GB` 停构建。
**IDA 若需重开**：后台跑 `powershell -File "D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1" -Path "D:\projects\cyber-reverse\target\Cybersole.exe.i64"`，同时用 CUA 轮询点掉「请确认」类对话框，**判据是「再读一次没有框」**。

---

# 历史（R823 时的交接原文，保留）

## 下一步该做的（按价值排序）

1. **`GetHomeAsync` 忽略 `c.Url` 的 3 个流程**（`NikeFlow` / `PoqAppFlow` / `SuperswipeFlow`）——
   已确认与 `ModuleRobustnessTests` 的例外名单一致。**待判的是「忽略是对的还是遗漏」，判据在镜像里。**
   工具：`analysis/scan_url_ignoring4.py`（缩进切类 + 截到下一成员，唯一自洽的版本）。
2. **两个真死步骤（R824 已确认）**：`HandleResponseAsync` 与 `RefreshSessionAsync`，总提及都是 1（只有自己的声明）。
   `StoreFlowParityTests` 的规范步骤表含 `RefreshSession`/`VerifySession` → **镜像有这些阶段**。
   **下一步：读反编译，看 `RefreshSession` 挂在哪个时刻。猜一个调用点 = 假覆盖（R799）。**
3. **`ScrapeVariantAvailabilityAsync` 已结案（R825）**：20 个实现**全部**写 `available` 判定，抽读 5 个最短的确认按站点不同（`RaffleFlow` 读 `Vars["open"]`，`Warhammer`/`Fanatics` 查 `"inStock":true`）。**累计通读 10/20；其余 10 个只确认写了判定。**
4. 判据 (a)(b)(c)(d)(e)(f) 的状态见 `docs/COMPLETION_AUDIT.md` 与本文件下方。

## 完成判据现状（重启后不必重查）

| 判据 | 状态 |
|---|---|
| (a) 类型级缺口 / 类型缺失 | **已分类完毕**：`real gap 4` / `missing 16` / 类型缺失 17（`docs/TYPE_PRESENCE_TRIAGE.md`：2 越界 · 7 改名 · 1 结构性 · 7 契约无判别力） |
| (b) 文案 | **0**，无剩余 |
| (c) 产物级对照 | **PASS** —— `python analysis\verify_artifact.py`：1142/1142 locale · 20/20 资源 · 12/12 叶子 |
| (d) claim 表 | **PASS 规则** —— `python analysis\check_claims.py`：5 行，2 pass / 3 fail，全有 authority，非 unknown 全有命令 |
| (e) 套件 / 变异 / 数字来源 | **一条待转绿**（见上）；数字全部出自 `docs/METRICS.md` |
| (f) 核心覆盖表 | 风控已对账（R807）；站点复刻件→镜像已逐条（49/57 有据、6 零、2 仅噪音）；**镜像→复刻件未分类（池子有 1182 个 `myshopify` 主机，是下界）** |

## 工具状态（重要）

- **`analysis/pe_strings.txt` 是抽样，不是全量**（180,228 行 vs 镜像 324,895 条串）。
  **正向可用、反向不可用** —— 反向结论要用 `python analysis\ida.py str <pat>`。见 `AGENTS.md` §2.7b。
- **`ida.py str` 默认 `limit 40`**（已加 `--limit`），**插件侧还有约 500 条上限**。**数数要写明是下界。**
- **仓内扫描器：按花括号或按「最近前缀 class」定类边界都会错**（一文件多类 + 字符串里的 `{`）。
  **可用的做法**：缩进切类 + 截到下一个成员声明。

## 机器相关

**内存不足导致重启**。重启后若 `available < 2GB` 只用 `-m:1`；`< 1GB` 停构建。
**IDA 若需重开**：后台跑 `powershell -File "D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1" -Path <目标.i64>`，
同时用 CUA 轮询点掉「请确认」类对话框，直到再读一次没有框。

## R826 补充

**长度守卫问题**：`ScheelsFlow`（`body.Length > 200`）与 `BstnFlow`（`> 2000`）把「响应体短/空」也判成 `available=false` ——
**误报缺货 = 错过 drop，不可重来**，而它由与商品无关的量决定。
**通读累计 12/20**（`NikeFlow` 31 行是好的那一类：结构化读取 + 缺输入明确失败）。
**未修**：两种改法都要镜像证据；IDA 未开（内存 1.63 GB）。

## R829 补充 — 反编译一个流程步骤的四步

```
1. ida.py str "<endpoint>"        -> string addr
2. ida.py xrefs <addr - 12>       -> 关键：−12（对象头），+0/+12 都是 0
3. ida.py dec <enclosing func>    -> async MoveNext
4. 找 &off_<addr> 那一行          -> 确认该步骤用了这个 endpoint
```

**首个用例 `/cart.js` 印证复刻件 `ShopifyFlow.cs:181` 已一致 —— 反编译核对这条路是通的。**
**`HandleBlock` 不走这条路**（不被字符串引用），需 MethodTable。

## R830 补充 — PopMart 覆盖面

复刻件的 13 个 `/shop/v1/...` 端点**全部有镜像对应**（`/shop/v1/` 41 matches）。自注「`/api/cart/add` 等无证据」也正确（0 匹配）。
**镜像另有四块未建模**：6 个 `prod-*-api.popmart.com` 区域主机 · `/web/v2?partner=&appKey=` · `activity/v1` 抽签 + `popDraw.json` · GraphQL `query buynow`。
**教训：搜镜像用「复刻件实际写的那个串」，不要用「站名」** —— 用站名会凭空得出「复刻件全无」。

## R831 补充 — 函数数量（目标第一句，首次测量）

`.pdata` 的 `RUNTIME_FUNCTION` 数：**原版 277,120 · 复刻件 171,690 · 62%**。
口径差异：与 IDA `af` 的 321,244 不可直接比；`.pdata` 数非叶函数，不含内联与裁剪。
**不能读成「少了 38% 功能」** —— 两边框架不同（原版 .NET 10 AOT；复刻件 .NET 8 AOT + Avalonia）。
**已完成（R832）**：`replica/tools/func_count.py` 注册为**第七项度量**，`METRICS.md` 有三行（original / replica / ratio）。

## R833 补充 — summary_bits 无串味

九个脚本 × 全部正则的矩阵：**每项 bits 只含自己的键，零串味**。
原因：其余条目都要求两到六词的短语，只有 R832 我加的那条用了裸词 `replica:`。
**已完成（R834）**：`METRICS` 每条声明 owned keys，`summary_bits(out, owned)` 只提取这些 ——
**串味从「可检出」变成「不可能」**。变异测试 `tools/mutation_ownership.py` 已响（松键进自己的行、不进 datafiles）。

## R835 补充 — PopMart 抽签面

`activity/v1/sample_info` → `sub_140B8B340`（URL 构造）· `activity/v1/exhibit_draw/draw` → `sub_140BC1340`（async）。**两个都是真代码。**
**`RaffleFlow` 覆盖 Shopify 抽签 App（r419/lndg/nodnod），不碰 PopMart → 抽签面无流程覆盖。**
不是独立任务型（`DrawTask`/`LotteryTask` 全 0），是 `$PopMartProductType` 下的一条可选路径。

## R836 补充 — PopMart 覆盖表

38 条 PopMart 记号全部列出并对到复刻件：**13 个 `/shop/v1` 端点全部命中，其余 12 个记号为 0**。
**R830 说「四块」是错的，真实七块** —— 漏了 `POPMART-RESERVATION` / `popmart_apac` / `PopMart-Tax-All`，因为上轮按「URL 形态」筛，把不带斜杠的键滤掉了。
**教训补一句：别按站名搜，也别按形态筛。完整列出再分类。**

## R837 补充 — 架构事实：DotNetBrowser

**镜像内嵌 DotNetBrowser**（数百条串）；**复刻件不引用该包**（1 处注释 + 7 个 csproj 无此包）。
复刻件的替代：自建 TLS（`Tls12Client`/`BouncyTls`/`Ja3`/`Http2`）+ 外部 Chrome 经 CDP。
**`ChromiumBridge.cs:13` 注释表明是有意取舍**，在 goal 允许范围内，但是优先级 ③ 最重要的设计事实。
**检索词纪律**：搜 `Browser` 得 10 条，搜 `DotNetBrowser` 得数百条 —— 先问「这个词是最具体的吗」。

## R838 补充 — PopNow 子系统

`PopNow` 29 处，读出 13 个方法名：`StartPopNowFlow` / `FetchPopNowSpuIds` / `ExtractPopNow` / `SelectPopNow` / `SelectMultiPopNow` / `AddToCartBox` / `ViewPopNow` / `StartPopNowViewTask` / `StartDailyCheckInTask` + `StartSignupFlow` / `StartClearFlow` / `StartInStoreFlow`。
**复刻件十二个名字全为 0。** 另：`NikeFlow`/`ShopifyFlow`/`FlowBase` 镜像全 0（复刻件命名自起）。
**三轮三次低估（四→七→九方法子系统）** —— 按词搜索给的是「含这个词的那些」，不是完整清单。
**判据 (f) 要完整清单：得遍历元数据后归类，或走类型图枚举某类全部方法。**

## R839 补充 — 115 个具名 async 操作

**`docs/ASYNC_OPS.md` 是判据 (f) 的骨架**：镜像 115 个具名 async 操作，复刻件按名字命中 44，未命中 71（全标「待判」）。
**`AddToCart` 有 15 个具名变体**（Astro/Next/Svelte/GraphQL/StoreFront/App/Dw…），复刻件一个虚方法 + 14 override。
**工具坑**：逐字节遍历 7 MB 会把 IDA 弄崩并写坏数据库 —— **用 `idautils.Strings()`**；
`py_eval` 用持久 globals（变量会残留）；内联 py 的反斜杠会被 shell 吃掉。
**重开 IDA 多了一个框**：「警告：Database still contains inconsistencies」→ 点「确定」。

## R840 补充 — 71 条裁决已判 7 条

`docs/ASYNC_OPS.md` 增「裁决记录」表。**3 条改名实现**（`AddToCartBox`/`AddToCartFrontend`/`AddToCartSvelte`）· 1 条探针无效（`AddToCartNext` 用 `Next` 命中几十文件，什么都没证明）· 3 条待判。
**新失败形态**：此前探针失败都是「命中为零」，这次是「命中一片但无意义」—— 比零命中更像结论。

## R841 补充 — 裁决累计 31/71

第二批 24 条：**9 改名实现 · 5「能力存在，命名未对上」 · 10 待判**。
**新区分**：探针失败有两种 —— ① 词没辨识力（`Stripe` 9 文件里有 `AdyenGateway.cs` 同族）· ② 能力真的没有。
机械规则：`>5` 文件 ⇒ 探针无效；`0` ⇒ 待判；`1–5` ⇒ 候选。
**先看**：`FinalizeCheckout`/`ValidateCheckout`/`VerifyCheckout`（锁车前校验）· `RestartSession`（与 `RefreshSession` 同族）。

## R842 补充 — 裁决一轮完成（累计 21 改名 / 5 能力存在 / 40 零命中）

工具 `analysis/adjudicate.py` 常驻。**`AddToCartNext` 换 `__NEXT_DATA__` 命中 —— R840 建议成立。**
**`StartDailyCheckInTask` 确认有实现**（`CheckIn` 横跨 `NikeSteps`/`PopMartEndpoints`/`StoreFlowSteps`）。
**探针到头**：40 条要判需**调用图**（从函数地址走，不从名字串走，R828 已证）。下一阶段工具：按地址找调用者。
**「为什么」不能是「我搜过没搜到」。**

## R843 补充 — 步骤表早已在仓里

**`replica/src/Cybersole.Stores/Flows/StoreFlowSteps.cs`（R112 起）有 9 个流程的步骤表，带 ordinal。**
R838–R842 从元数据提的 115 个名字是扁清单；**先读仓里已有的**。
**Nike：镜像 16 步 ↔ NikeFlow 17 重写，同名仅 2 个。差距是粒度** —— 镜像 10 个细步（`ValidateAddress`/`CheckInventory`/`GetShopperIp`…）vs 复刻件 3 个粗步。
**Pop Mart 24 步，抽签/展览/预约共 17 步；`PopNow` 只是其中一条流的一个词。**

## R844 补充 — 逐流程步骤对照

`analysis/flow_step_gap.py`：8 个流程 130 步，与复刻件同名重写 **22（16.9%）**。
**这不是覆盖率**：① `StoreFlow` 基类 165 步，没重写 ≠ 没实现；② 文件映射粗糙（共用文件里的重写不属于具体流程）；③ Nike 14 个不同名是**粒度**（镜像 10 细步 vs 复刻件 3 粗步）。
**108 条裁决框架**：粒度合并 / 基类默认 / 真缺（只有第三种是缺陷）。

## R845 补充 — 108 塌成 35

`analysis/partition_steps.py`：`StoreFlow` 165 虚步骤里已含 108 条中的 **49 条**（无缺口，只是没重写）。
剩 59 条：**24 PopMart（17 已证没有 + 7 未判）· 9 Nike（R843 已定性粒度）· 9 demandware-dual（App/Dw 双路）· 8 johnlewis（Stripe+交付回调）· 5 classic · 4 collectplus** → **剩 26 条要分别判**。
**「基类有」证明方法存在，不证明对它这个站行为正确。**

## R846 补充 — demandware-dual 结案；26 → 17

**`ScapiAppPath.cs`（R124）已把 dual 15 步按端点分完**：app 有端点 3 · dw 有控制器 3 · **app 无端点 4**。
**NoOrdersEndpoint**：「SCAPI 家族没有 orders 端点 → app 起手必须拐回经典控制器收尾」。
**剩 17 条**：johnlewis 8 · demandware-classic 5 · collectplus-app 4。
**第三次同样的错** —— 规则：**每批裁决前先 `ls Flows/*.cs | grep -i <flow>`**。下一轮先读 `JohnLewisStepMap.cs`，不是先判 johnlewis。

## R847 补充 — 17 塌成 4

**`JohnLewisStepMap.cs`（R118）答完 johnlewis 8 条 · `DemandwareStepMap.cs`（R117）答完 classic 5 条。**
**只剩 `collectplus-app` 4 条**（`Flows` 里无任何 CollectPlus 专属文件）—— 这次是真待判。
**关键引文**：「the step list is the client's phases and the endpoints are the server's resources」——
**步骤与端点不是同一层，用名字对齐去量，量出来的差异有一半是层级差。R844 的 16.9% 就是跨层级量当覆盖率。**

## R848 补充 — 线索收尾

**最后 4 条不是 Unknown，是已登记未证**：`LambdaWitness.Unwitnessed` 里就列着 `collectplus-app`。
**端点族一直在**：`StoreApiFamilies.cs` 的 `/component/singlepagecheckout/getClickAndCollectOrCollectPlusPoiStores`—— 探针找「标识符含 CollectPlus」，它写在路径里，所以 0 命中。
**注意**：`popmart` / `structure-token-*` 也在 `Unwitnessed` 里 —— R835–R838 说「没有」，这里说「未证」，**两句话不同**。
**判据 (f) 的正确做法：先读 `Flows` 目录里的分析文件，它们就是清单。**

## R849 补充 — 修正 PopMart 结论

**`PopMartEndpoints.cs` 有 39 个端点，14 个抽签/展览/预约端点全部存在；`PopMartStepMap.cs`（R116）已有 14 对映射。**
**缺的只是 `PopMartFlow` 里那 14 个驱动步骤**（11 个重写里一个都不是）。
**R835–R838 的「没有抽签面」在端点层是错的，只在步骤层成立。**
为什么没发现：R835 只查了 `activity/v1/exhibit_draw`（actapi 那条路），**而 `/shop/v1/storeOfflineDraw/join` 是另一条路。**

## R850 补充 — PopMart 14 步的证据边界

**3 可写**：`StartDrawFlow` `FindDraw`（`detail?uniqCode=`，参数记号 `_uniqCode`/`storeUniqCode` 都在）· `GetOrders`。
**11 只有端点、无请求形状**：`EnterDraw` `ChooseGoods` 等 —— **不写，理由与 R823 删 CSRF 兜底同一条**：
**能发请求但不知道发什么的方法，比不存在的步骤更坏。**
**写那 3 个的前置条件**：`StoreFlowRunner` 序列固定，且 **`StoreFlowSteps` 的 ordinal ↔ runner 调用表是否一致未查**。

## R851 补充 — 结构性发现

**`StoreFlowRunner` 是一条手写固定 21 步序列，所有流程共用；不用 `StoreFlowSteps` 的 ordinal。**
**镜像每个流程一条自己的序列**（Nike 16 · PopMart 24 · JohnLewis 19 · DW 12/15 · CollectPlus 17 · ST 15/12）。
**统一解释了 Nike 10 细步 vs 3 粗步、PopMart 14 抽签步写不进、JohnLewis 专属步骤无处放、R844 的 16.9%。**
**(f) 的「为什么」：不是端点缺/方法没写/粒度，是**执行框架形状不同**。
三种改法：① `StoreFlow` 加 `IReadOnlyList<Step>` 按流程取（最忠实）② runner 加 per-flow 分支 ③ 现状。**只有 ① 能让「功能相等」成立，本轮未改。**

## R852 补充 — ordinal 按流程编号

**130 个 ordinal，63 不同，67 跨流程重复，范围 20–153** —— 六个流程挤在 20–51 且重叠。
**→ 每流程自己编号 → 各自一个类、各自一套序列 → R851 从 Inference 升为 Observation。**
**反证**：`AddToCart` 在 JohnLewis 是 22、在 DemandwareClassic 是 32 —— **同名不同号，说明是不同方法**，
不是共享方法复用。**对「165 虚方法 + 按站重写」是个反证：镜像似乎每流程各写一份。**

## R853 补充 — 第九条序列 + 分母不可靠

**直接证据**：`<AddToCart>d__32` @`0x1434acef3` = DemandwareClassic 逐字；`<AddToCart>d__22` @`0x14338114f` = 未命名序列。**同名字两编号 → 编号按流程给 = Observation。**
**`GetHome(19)·FindProductMulti(20)·FindProduct(21)·AddToCart(22)·SubmitDiscount(23)` 不匹配 8 条中任何一条 → 镜像至少还有第九条序列。**
**没问过的问题：`StoreFlowSteps` 那 8 条是怎么选出来的？** R112 注释只说「相邻一段」，没说怎么定「哪些流程」。
**8 是 R844 那个 16.9% 的分母 —— 分母错了，百分比就错了。**

## R854 补充 — 67 段序列，8 条只是抽样

**1301 条含 `d__` 串 → 4 步以上递增运行 67 段**（`idautils.Strings()`；`str` 上限 500 不够）。
**`StoreFlowSteps` 的 8 条只是其中一部分，明显是业务流程的 ≥20 段。R844 的 16.9% 连分母都不对。**
**`HandleResponse · GetScript · GetKasada · GetWorkTime` @`0x14345abb1`** —— R824 那个「真死」步骤，**邻居是 `GetKasada`，所以它大概是 Kasada 流程里的一步（优先级 ②）。**
另三组指纹序列：`SubmitPOW`/`SubmitWebRtc` · `SubmitWpt`/`SubmitSensor` · 鼠标键盘行为组。

## R855 补充 — 站 × 变体 × 风控

**8 条之外的段一部分是任务变体**：raffle 有（96 处）· **sweepstake 0 · lottery 0**。
**`ProcessPaymentPaypalCreditCard` 那 11 步不是站，是支付变体** —— 「段属于谁」至少两层。
**→ 判据 (f) 的表需要三列：站 / 任务变体 / 风控**，而不是一列站名。

## R856 补充 — 任务层 = 5 个 Start*Flow + 3 个 *Task

`0x14337bdc4`: `StartSignupFlow`57 · `StartClearFlow`58 · `StartInStoreFlow`59 · `StartPopNowFlow`60 · `StartNormalFlow?`61
`0x14337cdcc`: `FetchTasks`187 · `StartDailyCheckInTask`188 · `StartPopNowViewTask`189
**编号连续 → 分派层入口。而 sweepstake/lottery 是流程内步骤（d__40–42 / d__36–37）→ R855 的「任务变体」不成立，属流程层。**
**最好答的下一个 Unknown：5 个 `Start*Flow` ↔ `Registry.cs` 63 个模块。**

## R857 补充 — 顶层维度不同

**镜像顶层 = 任务种类 5 种**（`StartSignupFlow` `StartClearFlow` `StartInStoreFlow` `StartPopNowFlow` `StartNormalFlow`）。
**复刻件顶层 = 店**（`Registry.cs` 64 模块 / 33 流程类 / 33 shop id），**没有种类层**。
**→ 复刻件能表达「对 Nike 结账」，表达不了「抽签任务 vs 常规结账」** —— 后者在镜像里是顶层选择。
**这比缺 14 个方法更根本；与 R851（序列形状不同）是同一问题两面。**
**规则：问「这些段属于谁」之前，先问「复刻件按什么维度组织」。**

## R858 补充 — `Task.Type` 是死字段

**`Tasks.cs` 有 `public string Type`，全 `src` 无一处 `.Type =` 赋给它。** `TaskCombinationRequest` 只有 `Store`。
**→ 复刻件有那个字段，没有那一层。死字段比缺字段更糟**：读代码的人会以为「已有，只是没接上」。
**同一条标准的第三种形态**：编造值（R823 CSRF）· 有形状没内容的方法（R850 抽签 11 步）· 没人写的字段（本轮的 Type）。
**本轮不删**：删不删取决于镜像有没有这个字段，未查；先删再查会删掉线索（R815）。

## R859 补充 — CreateInputModel 13 属性无 Type

**按镜像的属性书写模式 `类型,程序集.名字!访问器` 抽表，`CreateInputModel` 有 13 个属性，无 `Type`。**
**边界：那是创建表单输入模型，不是任务对象。**
**附带结论：五个 `Start*Flow` 的种类**不是在创建表单里选的** —— 复刻件从「没有种类输入」（正确）走到「没有种类派发」（错误）。**
**复刻件任务字段一半有出处（`MonitorMode`/`PriceCheck`/`MultiCart`），一半自造（`NameTemplate`/`CheckoutDelay` 0 命中）。**
**教训：找领域的**语法**比搜一个词有用 —— `Type` 有 27 个变体，直接搜等于没搜。**

## R860 补充 — 模型层齐备，Task.Type 冗余

**镜像 schema：`BotTask` 14（无 Type，有 `Task` 嵌套）· `BaseCheckout` 8（**有 Type**）· `TaskGroup` 17 · `WebTask` 2。**
**复刻件对照 14/14 · 8/8 · 17/17 · 2/2 —— 齐备。→ `Tasks.cs` 的 `Type` 是冗余，正确那份在 `BaseCheckout`。**
**优先级 ② Observation：`CaptchaSource` · `CloudflareSolverId` · 配额 · 计数全挂 `TaskGroup`，不是单任务。**
**未删理由：查了「有没有写」没查「有没有读」—— 只读不写也可能进 `tasks.json`，改输出结构会动用例。**
**对照是上界宽松**（正则搜整个文件，不是解析声明）。

## R861 补充 — 回到 R364 未定项

**`BotTask.Task` 的类型自 R364 起就记在 `BINDING_BACKLOG.md`** —— `Tasks.cs` 注释原话：「type could be an engine handle, an interface or a string id」。
**而它与 `Task.Type` 是一件事两面：若 `BotTask.Task` 的类里真有 Type，复刻件那行不是冗余，是**挪错了位置**。**
**规则（第五次同类教训）：查一个成员之前，先在 `BINDING_BACKLOG.md` 里搜它的名字。** 前四次是没读仓里的分析文件，这次是没读自己的待办清单。

## R862 补充 — R504 的天花板

**`BINDING_BACKLOG.md` L38–78 的 B 桶 31 条 = 「静态拿不到行为证据」，不是「没做」**：描述符无 xref · setter 编译期内联 · `ICommand` 行为藏在委托初始化点。
**这与 C7c（每函数功能相等）一直是 Unknown 是同一件事（R504 原话）。**
**目标分两层：数量对等可复算（61.96%）· 结构对等可达 · **行为相等静态不可达**。**
**唯一剩余路线 = 运行期差分，需原版登录凭据 → 待 YG 取舍。**
**教训：R504 记下后，我在 R824–R828 又重试了同一条路五轮。**

## R863 补充 — 天花板只挡 UI

**42 条点名的类全部是 UI**（`AccountGrid` `ActionsModal` `GoogleLogin` `MessageBoxDialog` …），成员是 `Add`/`Clear`/`Close`/`Delete`/`Save`/`StartAll` 等按钮动作。
**→ R504 天花板只挡 UI 成员行为（YG 已暂缓），不挡核心。**
**核心一步 = 方法发请求 → 行为证据在三处：端点串（R849 39 个）· 序列与 ordinal（R851–R856）· 参数记号（R850）。**
**待 YG 确认（分量已变）：按现优先级做核心、UI 行为记 Unknown，这条路认可吗？**
**教训：天花板的作用域和天花板本身一样重要。**

## R864 补充 — 两个阻塞拆开

**C7c 是一条整体 claim**（「任意两函数」），理由 = **缺 PDB / 调试符号** → **工具性**。
**R504 的 B 桶 31 条**（UI 成员）= 描述符无 xref / setter 内联 → **结构性**。
**两者是不同的问题。而 `rea` 的 `match_native_functions` 前提就是没有符号（按字节与 CFG 指纹配对）→ C7c 是**没试过第二套工具**，不是 dead end。**
**状态：核心请求形状有证据 · 函数级伪代码等价没试 rea 配对 · UI 成员行为结构性拿不到。**

## R865 补充 — C7c 卡在 provider

**`rea` 四个 native provider 全不可用**：ghidra/kuna `not_configured` · hopper `unsupported_host` · **ida 缺 `REA_IDA_MCP_CONFIG`**。
**→ `match_native_functions` 要的 `list_procedures` 出不来：工具在，provider 不在。**
**而 ida provider 只差一个环境变量（本会话 IDA MCP 一直通 13337）：写注册 JSON → 设变量 → **重启 REA**（= 允许停等 YG 的条目）。**
**收益不确定：.NET 10 ↔ .NET 8 AOT，字节相同的函数可能很少。**
**教训：「有个工具能做」≠「这工具在这台机器上能用」。**

## R866 补充 — 前置关系

**`GetOrders` / 抽签几步：`StoreFlow` 165 虚步骤里 0 · runner 21 序列里 0 · PopMartFlow 11 重写里 0。**
**进 runner → 污染所有流程；不进 → 死代码（R858 形态）。→ **前置关系：先让 runner 按流程取序列**。**
**修正 R850：它判「3 个可写」只查了「证据够不够」，漏了「位置有没有」。**
**下一步三件事：`StoreFlow` 加步骤列表 · runner 按流程取 · 再加步骤。** 影响 165 声明 / 33 流程类 / 1766 用例，**须先估影响面**。

## R867 补充 — 改造精确到四项

**`StoreFlow` 无任何序列（唯一 `IReadOnlyList` 是 `Domains`）；165 步骤是方法无派发表；而 `StoreFlowSteps.Flow.Names` 早就有序列数据，6 个文件全在分析侧用它。**
**四项：① 加 `StepSequence` 虚属性（一行）② 8 流程 override（8 处）③ runner 按它跑否则回落（一个分支）④ **「名字 → 委托」表 165 条 = 真活**。**
**卡点：第 4 项写法取决于 `csproj` 里 `PublishAot` / `TrimMode` —— 未查，下一轮第一件事。**
**教训：「影响面」该是分项表 —— 分项后才看出拦路的是一个 AOT 设置，不是 165 个声明。**

## R868 补充 — 序列机制建成（**已改产品代码**）

**三处改动**：`StoreFlow` 加 `StepSequence` 虚属性 + `StepDispatch` 反射表（165 条）+ `RunStepNamedAsync`；`PopMartFlow` override 序列；新建 `FlowSequenceTests`（7 用例）。
**套件 1773 通过 / 0 失败 / 0 跳过**（1766 + 7）。
**踩坑**：开放实例委托 `Func<StoreFlow,…>` 绑不上派生类声明 → 改按 `typeof(StoreFlow)` + `DeclaredOnly` 绑基类，靠虚分派。
**量出：map=165 · sequence=24 · implementable=0** —— 24 个镜像步骤名与 165 个方法名**零交集**。
**还没做**：其余 7 流程 override · runner 按序列跑的分支 · 写抽签步骤。**「抽签能跑」尚未成立。**
**教训：纸上估不出运行时约束 —— 估完就该动手。**

## R869 补充 — 去重 + runner 接上（**已改产品代码**）

**R868 的反射表是 `StepActionRunner` 的重复品**（后者更完整：`Invoke` 而非 `CreateDelegate`，含计时/记录/取消）。**已删，改指向它。**
**三个流程声明序列**：Nike 16 · PopMart 24 · JohnLewis 19；**五条序列无落点**（demandware-* / collectplus / structure-token-* → R855「是变体不是站」）。
**runner 分支已接**；写时踩出**假成功**（24 declared / 0 runnable → 空循环返回 Ok）→ 已修：0 runnable 直接 Error。
**形态谱第五种：编造值 → 空壳方法 → 死字段 → **空循环假成功**。**
**套件 1773 通过 / 0 失败 / 0 跳过。**
**教训：「先查有没有现成的」要包括**实现**，不只是分析。**

## R870 补充 — 教训做成命令

**`python tools\where_is.py <名字>`**：按 **implementation / analysis / test / doc** 四组报位置，只看文件名与路径。
**它第一次用就抓到自己没排除 `tools/.snapshots/`**（`StepActionRunner` 报 39 个文件，29 个是快照），已修 → 7 files。
**`PopMart` → 31 files，analysis 组含 `PopMartStepMap.cs`(18)** —— **R835 若跑过就会直接看到，而那是 R849 才发现六轮没读的文件。**
**已写进 `AGENTS.md §2.7c`**（五次踩坑表 + 两条配套：要包括**实现**；implementation 组有命中就先读再写）。
**边界：不查镜像（那是 `analysis/ida.py str`），不判该不该有。**

## R871 补充 — 第一步写出来（**已改产品代码**）：`GetOrders`，coverage 0→1

**`where_is GetOrders` → implementation 组空（确认没人实现）**，analysis 组指向 `CandidateSteps.cs`，那里写着「ordinal 104 被三个类共用」。**核：`GetAccessToken>d__104`@`0x1433737e2` 与 `GetOrders>d__104`@`0x14337c7e5` 在两条不同 blob → 撞号真，归属不模糊。**
**写了**：`StoreFlow.virtual GetOrdersAsync`（默认显式失败）+ `PopMartFlow` override → `GET OrderList` → `Session.Vars["orders"]`。**响应体整份存不解析（无 schema 证据）。**
**测试三数一起钉：`map=166` / `sequence=24` / `implementable=1`。套件 1773 通过 / 0 失败。**
**下一轮第一件事：`where_is GetInstoreOrders`（105，同段，可能有常量）。**

## R872 补充 — 猜错一个，写对两个（**已改产品代码**）：coverage 1 → 3

**R871 的「`GetInstoreOrders` likely 可写」被证伪**：`PopMartEndpoints` 无 in-store orders 端点（只有 `BuyNow`/`OrderCounter`/`CanPlaceOrder`/`OrderList`/`OrderDetail` + 抽签/票务）。**写它等于编 URL。**
**改写了一对**：`FindExhibit` → `StoreOfflineDrawInfo?alias=`（缺 alias 失败）· `EnterExhibit` → `POST StoreOfflineDrawJoin`（缺 exhibit 体失败）。**`StoreFlow` 各加默认失败的虚方法。**
**数字：`map 166→168` · `implementable 1→3` · 四数一起钉（168/24/3 + 三条 CanRunStep）。套件 1773 通过 / 0 失败。**
**待办里不写「likely」——只写「已确认，因为 X」或「未查，下一步查 Y」。**

## R873 补充 — 再写四个（**已改产品代码**）：coverage 3 → 7

**判据：查询形状写在常量里才可写。**写了 `StartDrawFlow`/`FindDraw`（`?uniqCode=`）· `FindDates`（无查询）· `FindTimeSlots`（`?uniqID=`）。**7 个 POST 请求体无证据 → 不写。**
**三个步骤会明确失败（刻意）**：`uniqCode`/`uniqID` 从 session 取而**没人往里放** —— 发空参数可能得 200，会被读成跑通。
**数字：`map 168→172` · `coverage 3→7` · 七条 CanRunStep 各标轮次。套件 1773 通过 / 0 失败。**
**下一轮该查「镜像里谁 produce `uniqCode`/`uniqID`」，不是再写步骤 —— 三步已写但跑不通。**

## R874 补充 — `uniqCode` 产者：名字层已到顶

**5 条全列**：`_uniqCode`(字段) · `currentUniqCode` · `storeUniqCode`(属性名) · `&storeUniqCode=1`(查询片段) · `/shop/v1/drawScratch/detail?uniqCode=`(端点)。**无产者形态。**
**→ 不是「没找到」，是「名字层问不出来」：写入是 setter 行为，R504 已证内联。**
**而这条修正 R863**：R504 那堵墙挡的是**所有属性写入**，与 UI 无关；我说「只挡 UI」收得太窄。
**还没试的静态路：从 `&storeUniqCode=1` 反推宿主 URL → 哪个页面带这个参数。下一轮第一件事。**
**纪律：写 Unknown 要写清层次（名字/结构/行为）。**

## R875 补充 — `&storeUniqCode=1` 没有宿主

**`0x146a85000`–`0x146a8C000` 有 335 条字母序串，全是 `&xxx=` 查询片段 —— 是一张**查表**，不是 URL 碎片。`&storeUniqCode=1` 值**恒为 1** → 固定标志位，**不需要来源**。**
**→ 修正 R850 的四记号并列**：`_uniqCode`(字段) / `currentUniqCode`·`storeUniqCode`(属性名) 需要来源；`&storeUniqCode=1` 不需要。**「uniqCode 从哪来」范围变小：两个运行时属性，不是三个。**
**同一形态第 N 次：把「一起出现」当成「同一件事」（R830/R836 · R863 · R875）。**

## R876 补充 — 第九条序列有名字：`DrawStores`

**两条探针空手**：12 个 `/shop/v1` 端点 12/12 已在 `PopMartEndpoints`（39 个无缺口）；draw 端点附近全是路径表，**无请求体键**。
**第三条给东西**（`0x1433803xx`，51 条）：模型字段表（`_drawid` `_uniqCode` `_winner` `_drawGoodsId` `_eventId` `_memberAlias` `_slots` `_startTime` `_turnstileKey` `_rpcAdyen*` `_rpcPayPal*`）**+ 第九条序列**：
**`DrawStores`: 21 Start · 23 GetHome · 24 CheckVerification · 25 SubmitSaleRegistration · 26 CheckLogin · 27 Register · 28 CompleteRegistration · 30 GetCart · 31 ClearCart · 32 FindProduct · 33 AddToCart · 34 ReplaceProduct**
**→ 名字误导：这是**发售注册流程**不是抽签；也不是 PopMart 别名（104 vs 21）。**
**`_turnstileKey` 作为模型字段存在 —— 优先级 ② 的一条线索。**
**下一轮第一件事：`where_is` 那几个步骤名，看 `DrawStores` 在复刻件里有没有落点。**

## R877 补充 — 覆盖最高的一条序列没有店类

**`DrawStores` 12 步 vs `StoreFlow` 172 虚方法 = 8/12**：有的 8 个是 `GetHome` `CheckLogin` `Register` `CompleteRegistration` `GetCart` `ClearCart` `FindProduct` `AddToCart`；缺 `Start`（有 `Init`）· `CheckVerification`（最近 `VerifySession`）· `SubmitSaleRegistration` · `ReplaceProduct`。
**⚠ 覆盖率 ≠ 完成度**：`DrawStores` 8/12 但**一步没写**（名字大多通用）；PopMart 7/24 但**七步真有端点证据**。**报覆盖时同时报两个数。**
**两个近似没算**：`Start`≈`Init`（推断）· `CheckVerification`≈`VerifySession`（不同概念）—— 算进去就是编的 10/12。
**`DrawStores` 在 Registry 里无模块 → 流程概念不是站**（同 R855）。**`DrawStores`=门店发售注册 vs PopMart=抽签，共用同一端点族。**
**最该判的一条：`DrawStores` 要不要建流程类 —— 建了 8 步能跑，但 `Id`/`Domains` 无从写。**

## R878 补充 — **撤回 R876**：第九条序列没有名字

**`DrawStores`@`0x143380392` 与 `_drawid`@`0x14338039d` 相隔 **11 字节**，而 `DrawStores` 10 字符 + UTF-16 结束符 = **22 字节** → 塞不进 → **独立字符串对象**。**NativeAOT 字面量表按首用顺序排布 → 相邻 ≠ 归属。**
**`DrawStores` 是**属性名**（夹在 `_documentNumber` 与 `_drawid` 之间，无下划线前缀）。**
**连带撤掉 R877「`DrawStores` 要不要建流程类」——问题不成立（归属未知）。8/12 数字不变，只是不该带归属前缀。**
**纪律：「看周围」不够 —— 要问「它们真的是同一个东西吗」；**能用算术回答（22 > 11）时就不该靠推断。****

## R879 补充 — 任务种类 **14** 个（不是 5）

**来源 `replica/docs/baseline/recovered_async_methods.txt`（1547 个异步方法名，全量）**：`Start*Flow` 14 个 + `Start*Task` 2 个。**R857 的来源是一个代码区（5 个）→ 判断对，数量错三倍。**
**14 个**：`AccountRegistration` `Clear` `DrawCheck` `DrawEvent` `Draw` `Exhibit` `InStore` `Normal` `PopNow` `Raffle` `Reservation` `Rpc` `Signup` `Tasks`。
**无名序列（21–34）按语义归属 `StartAccountRegistrationFlow`**（`CheckVerification`/`SubmitSaleRegistration`/`Register`/`CompleteRegistration` 对上）—— **Inference，不写进 `StoreFlowSteps`。**
**`Start` ≠ `Init`**（基线里两名都在）→ R877 的 9/12 不存在，**8/12 就是 8/12**。
**结构缺口**：任务种类这一层在复刻件里几乎没有对应物（`Registry.cs` 64 个模块是「站」不是「任务种类」）。

## R880 补充 — 任务种类这一层建起来了（**已改产品代码**）：14 + 2

**新增 `src/Cybersole.Stores/Flows/TaskKinds.cs`**：`FlowKind` 14 个 · `TaskKind` 2 个 · `TaskKindCatalog`（成员↔`Start*Flow` 名 + `Resolve()` 往返）。**每个成员都有基线出处，没有为对称而加的。**
**六测试**：14 / 2 / 出处名+往返 / 16 名互斥 / 不认识返回 null / **`TheKindAxisIsNotYetWiredToAnyFlow`（断言还没接进流程）**。
**套件 1779 通过 / 0 失败（原 1773 + 6）。**
**文档守卫第四次抓到我**：写「64 个模块」实际 63（历史 R457·R464·R813·R880）。**已修四处 → 63；下一轮改成不带数字的说法。**
**下一步：`FlowKind × Store → StoreFlow` 映射表**，需「某站的某 `Start*Flow` 存在」的证据。

## R881 补充 — 句式天花板测试

**新增 `DocsConsistencyTests.TheModuleCountPhraseDoesNotSpread`**：散文里「<数字> 个模块」(>=20) 处数 **<= 16**，只许降不许升。**不削既有守卫、不改历史、只针对增长。**
**它第一次跑就纠正我**：我先数出 13 当 ceiling，测试报 16 → 复核 16 才对（毛病：here-string 里 `chr(10)` + 反引号）。**所以它防的不只是句式，是「拿手工计数当基准」。**
**套件 1780 通过 / 0 失败（原 1779 + 1）。**

## R882 补充 — 5 个 `Start*Flow` 与 Pop Mart 抽签步骤同一片字面量区（**本轮未改产品代码**）

**`0x14337B000`–`0x14337CE00` 78 条**：`Start>56` `StartSignupFlow>57` `StartClearFlow>58` `StartInStoreFlow>59` `StartPopNowFlow>60` `StartNormalFlow>61` `FindProductInstore>76`，**同段还有 `GetOrders>104` `StartDrawFlow>115`** → 一个 blob 有 ordinal 56–116+。
**但 blob 可同时装基类与派生类字面量 → **不能说「PopMart 支持这 5 种」**。相邻粒度是 blob（比字符串更粗）→ 证据更弱。**
**所以 `FlowKind × Store → StoreFlow` 映射表本轮**不写** —— 没证据的映射表 = 把「看起来接了」当「接了」。**
**字段收获**：`_accountKasada`（Kasada token 账号级）· `_forter` · `_marketPlace`/`_locationId`/`_locationData`（门店模型）。
**下一步：查 ordinal→类 的映射手段（R504 那堵墙可能也挡）。**

## R883 补充 — `!Getter` 枚举：508 个类型（**新增基线文件，未改产品代码**）

**`replica/docs/baseline/recovered_accessors_by_type.txt`**：2,587 三元组 / 508 类型，带出处与边界头。分布 `Ui.Views` 60 · `Models` 22 · **`Stores` 0**。
**`Task.Type` 悬案解了**：`Cybersole.Models.Drop { Time, Type }` —— **`Type` 属于 `Drop` 不属于 task**；`CreateModel` 8 属性无 `Type`。
**R504 边界更正**：不是「全都拿不到」，是「**只有参与绑定的成员拿得到**」（`Stores` 为 0 即证）。**对 R882 的 ordinal→类 无帮助。**
**顺带**：`Store` 只有 `Url`；`Global.Settings` 21；**`TaskGroup` 9（含 `CaptchaSource`/`CloudflareSolverId` → 优先级 ②）**。
**纪律：发现一个形态 ≠ 把它枚举完（R859 → R883 隔六十轮，成本十分钟）。**

## R884 补充 — `where_is` 默认改整词（**改工具，未改产品代码**）

**它这一轮给了两次假答案**：① `where_is Drop` 子串 → 55 文件全是 `DropDown`/`ProxyDrop`，**真正的 `Drop` 在 `Checkout.cs:44` 不在其中**；② 我据此写了新 `Drop.cs` → **CS0101 重复定义**。
**改默认**：`默认整词 / --sub 才子串`（原为默认子串 / `--word` 才整词）。实测默认 16 文件含 `Checkout.cs`，`--sub` 55 文件。**理由写进 `--sub` 的 help。**
**两条测量**：`CreateModel` 镜像 8 / 复刻 20（**8 个全含，缺 0，多 12**）；`Drop` 镜像 `Time`+`Type` / 复刻 `Time`+`Stores`+`Type`（**`Stores` 未见于基线，但那是弱证据**）。
**套件 1780 通过 / 0 失败。**
**纪律：§2.7c 只规定「跑」，没规定「怎么用」。命令也有默认值，默认值本身可能是陷阱。**

## R885 补充 — 「形状 78」的证据源是抽样池（**改工具，未改产品代码**）

**工具早已存在**：`tools/shape_audit.py`（第三次 §2.7c 生效）。本轮只加 `--baseline` 与 `--extra` 两个开关。
**证据源问题**：抽样池 102 types / mismatches 78 vs R883 基线 211 types / **mismatches 0**。**池子少一半且含 `CreateModel` 缺席 → 「形状 78」从未包含它。**
**而基线有缺陷（R883 引入）**：格式丢了 `Getter`/`Setter` 种类 → `want_set` 永不成立 → **安静返回 0**。**下一轮重生成带种类的基线。**
**R884 那问题答了**：`CreateModel` 12 个多余属性中 7 个有证据 / 5 个没有（4 个是 `*Id` 外键 → **镜像用对象不用键，系统性差异**）。

## R886 补充 — 形状指标 **78 → 94**（**改工具链三处**）

**三层错的链**：R883 压缩丢种类 → R885 只加开关没改调用方 → **R886 重生成带种类的基线 + 改 `metrics_report.py`**。
**基线重生成**：1,275 行 (类型,属性) / 508 类型 / Getter 950 · Setter 687 · Property 950。
**数字**：抽样池 102 types → 78 mismatches；**全量基线 211 types → 94**。**94 比 78 差而更对 —— 过去一�直在少报。**
**套件 1780 通过 / 0 失败。**
**纪律：「知道了」和「改完了」之间那一步要机械检查 —— 加了开关就问「谁该用它」。**

## R887 补充 — 94 条形状差异 = 3 类 × 63 成员（**未改产品代码**）

**分类**：`?` 44（不存在）· `method` 34（有方法，镜像是可写属性）· `prop-get` 16（只有 getter）。
**归族**：94 条 = 63 成员；**`Close` 15（全 `?`）** · `Delete` 8 · `Edit`/`Save`/`MoveGroup` 各 3 · 其余 55 各 1。
**一个结构故事**：`Close`/`Delete`/`Save`/`Edit`/`Reset`/`Add` 全是视图动作成员，镜像是**可写 `ICommand` 属性** → **一次形态改造，不是 63 次补丁**（`AGENTS.md §3` 八项清单）。
**`BotTask.Running`/`Task` 均 `Getter,Property,Setter` → 可写属性**；与 R883 的 `Drop.Type` 是两件事。**R364 重述：`Task` 是可写属性，`Type` 挂在 `Drop` 上。**
**最该判：`Close`×15 要不要一次改**（15×8 项连带，可能改到一半）。

## R888 补充 — 「形状 94」里 **77 条是 UI**；核心 **17**（**改工具链两处**）

**按项目分组**：`Ui` 77（**优先级 ④，YG 明令缓**）· `Core` 12 · `Services` 5 · **`Stores` 0（① 零缺口）**。**→ 94 的 82% 在被缓的那一档；R881–R887 在提高一个主项不在目标上的指标的分辨率。**
**改动**：`shape_audit.py` 加按项目分组 + `core mismatches: 17`；`metrics_report.py` 加 pattern；**METRICS L23 总 94 / L24 核心 17**。
**核心 17 条**：`BotTask`(`Running`·`Task`) · `Checkout`(`Profile`) · `CreateModel`(`Inputs`) · `Notification`(`Timestamp`·`Title`) · `IWebhook`(4 个)。**最大一族 `BotTask` = 任务模型中心。**
**`Cybersole.Http` 未出现 → 94 条没一条命中请求层，而 ③ 正是请求层。**
**纪律：指标不需要错才会误导 —— 只需要没有按目标分解。**

## R889 补充 — 抽签 POST 请求体**静态不可得**（**未改产品代码**）

**三条路全关**：属性名（基线搜 13 个候选 0 命中）· 函数名（`funcs` 不按名过滤，镜像无符号）· **字符串 xref `0x14337c7e5` = `xref_count: 0`**。
**→ 状态机名字是编译期名字表，无代码引用。R504 扩为「这些名字本身也没 xref」。**
**我的错**：JSON 键读错（`functions`/`matches` vs `[{data:[…]}]`）→ 三次 0 结果，**差点写成「镜像里没有这些函数」**；救回的是用已知存在的名字先验工具。**纪律：任何「查询返回空」写成结论前，先用已知非空的输入跑同一条命令。**
**PopMart 前沿 = 静态天花板**：缺 7 个 POST 体 + `GetInstoreOrders` 端点，**都要运行期 → 需原版登录凭据（可停下等 YG）。**
**还有四条不需凭据**：`GetInstoreOrders` 端点 · 5 条变体序列 · 其余 7 个流程的 `StepSequence` · `method` 形态 34 条。

## R890 补充 — 端点覆盖 **41 / 41**（**+2 常量 +3 用例**）

**做法换成全量枚举再对比**：镜像 `/shop/v1/` 41 条 vs 复刻 39 → **缺 2（`store_ticket/reserve` · `store_ticket/sessionList`）、多 0**。**「多 0」更重要：39 个常量全部有镜像出处，没有编的。**
**`GetInstoreOrders` 不在 `/shop/v1/` 下** → 从「不知道在哪」到「知道不在哪」。**下一轮枚举别的前缀。**
**3 个用例双向钉住**，其中 `EveryConstantAppearsInTheImage` 钉「多出来的常量」= 编造。**套件 1783 通过 / 0 失败。**
**我的 grep 错**：`-SimpleMatch "box/|cash/desk"` → `|` 不生效 → 返回空像「都没有」（同一「返回空」形态第二次）。
**纪律：搜名字答那个名字；枚举全部再对比答整个空间 —— 还能答「有没有编的」。**

## R891 补充 — 第二个端点族 `/store/v1/`（**改产品代码**）：coverage 7 → 8

**找到 5 条**：`cart/add` · `cart/del` · `cart/listByStore?actionType=1&GID=` · **`order/listV3?currentPage=1&status=1&pageSize=20`（`GetInstoreOrders` 105）** · **`product/detail?storeId=`（`FindProductInstore` 76）**。
**改动**：`PopMartEndpoints` +5 常量 · `StoreFlow` +2 虚方法 · `PopMartFlow` +2 override。**虚步骤 172→174 · coverage 7→8 · 套件 1783 通过。**
**两点要紧**：① **锚用词不用形状**（松正则抓 GUID/base64，70 条无一条含 `order`）；② **`implementable` 8 不是 9** —— `FindProductInstore` 已实现但**不在 PopMart 的 24 个名字里**（ordinal 76 属更早的段），**测试两个都钉**。
**下一轮**：`/store/v1/` 那 3 条 cart 路径的步骤归属；有没有第三个族。

## R892 补充 — 端点族 **56 / 32 完全没有**（**未改产品代码**）

**第一次报 40，多报 8**：`JohnLewisBff.Base = ".../bff/"` + 相对路径 `"v2/orders"` → 整条字面量判据找不到。**改三级：exact 3 / relative 21 / absent 32。**
**32 个完全没有**：`/customer/v1/` 10 · `/Checkout/v2/` `/bff/v4/` 各 5 · `/threeds/v1/` `/bff/v3/` `/checkout/v2/` `/cart/v2/` 各 3–4 · … · **`/turnstile/v0/`（Cloudflare Turnstile）** **`/shield/v1/`**。
**优先级 ② 有两条具体缺口**：`/turnstile/v0/`（R876 的 `_turnstileKey`）与 `/shield/v1/`。
**边界：56 族是全镜像的**，`/bff/*` 属 John Lewis → 「32 个没有」≠「PopMart 缺 32 族」。**按站分组未做。**
**纪律：两次判据错方向相反（假 0 / 假 40），来源相同 —— 判据里藏了以为成立的前提。挑样本来推翻自己比相信输出便宜。**

## R893 补充 — 族 ↔ 宿主 **45 / 28**（**新文档 `docs/ENDPOINT_FAMILY_HOSTS.md`**）

**方法：同现**（一条字面量内同时有宿主与族，如 `//checkout.johnlewis.com/bff/v2/orders`）—— **比 R876 的池内邻近强，比 R892 的整条路径字面量稳（后者假设存储形式）。**
**结果**：`api.nike.com` **11 族** · `checkout.johnlewis.com` **4** · `www.vans.com` 3 · adyen/midtrans 各 2 · **`prod-hk-actapi.popmart.com` 1（`/activity/v1/`）** · **`challenges.cloudflare.com` 1（`/turnstile/v0/`）** · 其余 20 各 1。
**优先级 ② 三条**：Turnstile 端点 · AYCD OTP（`inbox-api.aycd.io`）· 3DS/支付重定向（cybersource/paypal/midtrans）。
**更正 R835：PopMart 有 2 个宿主**（`popmart.com` 带 `/shop/v1/`+`/store/v1/`；`prod-hk-actapi.popmart.com` 带 `/activity/v1/`）→ 错的形状是「一个站只有一个 API 宿主」。
**边界：45/56 · 同现不证明唯一归属 · 混了站与厂商 · 不说明复刻件实现情况。**

## R894 补充 — 按宿主覆盖 **17 / 45**（**未改产品代码**）

**分布**：`api.nike.com` **11/11（首个端点层齐的站）** · `checkout.johnlewis.com` 1/4 · adyen 1/2 · asics/goat/www.nike/aycd 各 1/1 · **`www.vans.com` 0/3** · **`challenges.cloudflare.com` 0/1** · **`prod-hk-actapi.popmart.com` 0/1** · 其余 18 个支付商各 0/1。
**Vans 0/3 而模块在（62 个店模块）→ 「模块在、端点不在」**，比「32 族完全没有」精确。
**17 是上界**：判据「族段出现过」太松可能误命中。**R892 太严高报 40 vs 32；本轮太松可能低报 —— 同一来源：松紧未标定。**
**新规矩：报覆盖数必须写「上界/下界/精确」+ 理由。**
**下一轮**：17 里有多少是泛段误命中（逐条约 100 次对比）；Vans 走的是哪一族。

## R895 补充 — 路径级 **55 / 171（32.2%）**（**未改产品代码**）

**判据三态**：whole（整条字面量）47 · tail（去族前缀的尾部字面量）8 · **missing 116** · **有 55（32.2%）**。
**两个分母**：族级 17/45 = 37.8% vs **路径级 55/171 = 32.2%**。**族级问「族有没有被提到」，路径级问「族下每条有没有」→ 提到 1 条族级给满分 → 族级高估覆盖率。**
**修正 R894**：族级 17 本身准；真问题不是判据松紧，是**分母**。**族级只用来数「涉及几个族」，覆盖率用路径级。**
**纪律**：「算准它会变吗」= 精度问题；「换分母它会变吗」= 定义问题 —— 别只报第一个。
**下一轮**：116 条缺失里多少「本来不需要」（`_jobs` 族可能是轮询副本）；171 里多少属支付商。

## R896 补充 — 分母拆开：站 **55/142（38.7%）** · 厂商 **0/28（0.0%）**（**未改产品代码**）

**55 条覆盖全部来自站；厂商 28 条一条没有。**
**32.2% 的真相**：混合 55/171 = 32.2% ← 两个问题被平均；**站 38.7% · 厂商 0.0%**。
**厂商 0/28 是干净缺口**：优先级 ② 的 `challenges.cloudflare.com`→`/turnstile/v0/` 与 `inbox-api.aycd.io`→`/api/v1/`；其余 3DS/支付。
**抓到一个具体误命中**：`inbox-api.aycd.io` 族级 1/1「有」而路径级 **0** —— 族段 `api/v1` 太泛。
**纪律：平均值的前提是各分量同质。站 API = 要实现的功能；厂商 API = 调用的外部服务。**
**下一轮**：厂商 28 条单独成表；`-` 无宿主那几条查清。

## R897 补充 — `where_is` 分大小写（**改工具默认，未改产品代码**）

**`where_is Vans` 只返回 docs（实现组 0）→ 我差点判「Vans 无模块、R894 错了」。实际实现写 `"vans"` 小写。**
**改默认**：`默认不分大小写 / --case 才严格`。改后 5 文件（`DemandwareControllers.cs` 2 · `DemandwareControllerTests.cs` 2）。
**R894 那半句对**：「模块在」（site id + 2 条测试）·「端点不在」（3 个族一条常量都没）→ **0/3 是真缺口。**
**同一串第三次默认值错误**（R884 子串 / R885 抽样池 / R897 大小写），**三次发现都靠副作用动作，没有一次是按计划查的。**
**下一轮**：取 Vans 那 3 个族的具体路径（R895 的路径级判据要具体路径），然后补常量。

## R898 补充 — Vans 6 条路径（**改产品代码 +6 用例**，套件 1783→**1789**）

**6 条**：`/cart/v1/cart/` · `/cart/v1/cartWithItem?locale=` · `/cart/v2/cart/` · `/cart/v2/checkout/order/` · `/cart/v2/checkout/order?locale=` · `/products/v2/products/`。
**而扫描输出里 `HOST` 行一条都没有** → 归属分两级：**族 = Observation（R893 共现）· 路径 = Inference**。**`VansEndpoints.OwnershipIsInference = true` 固化进类型。**
**6 用例**，含 `TheProductsPathReallyRepeatsItsWord`（双词是镜像里的）与 `OwnershipIsRecordedAsInferenceNotObservation`。
**一个恒真测试被换掉**（读自己的文件再查自己的字面量）。
**纪律：Observation 与 Inference 在文档里长得一样，只有标注能分开。**
**下一轮**：判这 6 条到底属不属 Vans（找路径级共现证据，扫描说没有）。

## R899 补充 — Vans 常量补 `/api`，归属升为 Observation（**改产品代码**，套件 1789→**1790**）

**根因**：R898 的扫描模式 `/(cart|products)/vN/` 从 `/api` **之后**开始匹配 → **路径少了 `/api`，而「没有宿主」这个观察也是假的**。
**5 条完整 URL**：`https://www.vans.com/api/cart/v1/cartWithItem?locale=` · `.../api/cart/v2/cart/` · `.../api/cart/v2/checkout/order/` · `.../api/cart/v2/checkout/order?locale=` · `.../api/products/v2/products/`。
**修正**：前缀补 `/api`；**`OwnershipIsInference` `true` → `false`**（宿主与路径同处一条字面量）。
**7 用例**（新增 `EveryPathCarriesTheApiPrefix` · `OwnershipIsNoLongerInference`）。
**纪律：一个 Inference 标注可能是扫描模式的假象 —— 先问「我的模式能不能看见它」，再决定标注。**
**下一轮**：查别的站的扫描是否也漏了 `/api` —— 若是，R892–R896 的覆盖数都低报。

## R900 补充 — **27 / 154** 条路径有族前缀，R892–R896 低报（**未改产品代码**）

**前缀分布**：`/api` 8 · `/payment` 4 · `/payment-authentication` 4 · `/web2` 3 · `/merchants` 2 · `/prod` 2 · 其余各 1。
**→ R895 的 55/171 低报最多 27**；**Vans 那 6 条只是其一，其余 21 条未修**。
**两个人口不同**（171 vs 154，去重粒度不同）→ **不能用同一测度两时点来读**。
**一个模式四轮四个数**（40 / 32 / 17-45 / 55-171）—— 都在 `/x/vN/` 地标处匹配，**而地标匹配默认前缀不存在**。
**纪律：扫之前问「我的模式假设了什么结构，那个假设能否被证伪」；找一条反例就够。**
**下一轮**：用同一提取法重跑覆盖率，得到可比的数；查后缀截断。

## R901 补充 — 一个正式工具一个数（**新增两个工具文件**）

**工具化**：`analysis/coverage_extract.py` + `replica/tools/endpoint_coverage.py`。**理由：R892–R900 同一问题五次五答案，每轮临时脚本各带假设。**
**三个桶**：**有宿主的站 3/55（5.5%）** · 厂商 0/32（0.0%）· **无宿主 46/67（68.7%）** · 合计 49/154（31.8%）。
**推翻 R896 的 38.7%**：它把无宿主那 67 条算进了站桶。**站 API 覆盖 5.5%，能定位到站的 31.8% —— 两个问题两个数。**
**五轮度量只动了 8 个常量。度量精度提升一倍不如一行常量值钱。**
**下一轮第一件事**：跑 `-v` 拿到那 52 条缺失清单，然后补常量。

## R902 补充 — `/customer/v1/` 10 条补齐（**改产品代码 +6 用例**）

**补 10 条**：地址四动词 · `customer/app` · `customer/exist` · `customer/guest/register` · `customer/login` · `customer/register` · `verification/send`。**先查过 `/customer/v1` 字面量全库无。**
**数字**：`hostless` 覆盖 **46/67 → 56/67（68.7% → 83.6%）** · 总缺失 **105 → 95** · 套件 **1790 → 1796**。**R892 以来第一次可测的产品进步。**
**归属 Unknown**（`OwnerIsUnknown = true`）：无字面量同时含路径与宿主 → **写常量正当，写步骤不正当**。
**下一族**：`/commerce/v1/` 2 条 · `/product-core/v1/` 2 条 · `/legacy/v1/` 2 条 · **`/shield/v1/verify_otp`（优先级 ②）**。

## R903 补充 — hostless 桶关闭 67/67 = 100%（改产品代码 +6 用例）

11 条：/checkout/v1/orders · submitThreeDS2Fingerprint?token= · /commerce/v1/bags · /commerce/v1/products · /legacy/v1/account/login · /legacy/v1/users/me · /marketing/v1/verificationcodes · /payments-vas/v1/card-capture · /product-core/v1/pdp · /pdp/sku · /shield/v1/verify_otp。

数字：hostless 56/67 → 67/67（100%）· 缺失 95 → 84 · 套件 1796 → 1802。

而 store covered 仍是 3 —— 前两轮补的全是无宿主侧；有宿主 55 条只覆盖 3 条，那是剩下的前沿，而它需要归位而非常量。

AntiBotRelated 子集让优先级 ② 可直接数。

下一轮：store 那 52 条缺失清单（-v）+ /shield/v1/verify_otp 单独查。

## R904 补充 — 加第三态 base-tail，浮出 13 条假阴性（改工具）

起因：store 缺失清单里 checkout.johnlewis.com 占 11 条，而 JohnLewisBff 用 Base + 相对路径存，逐字匹配看不到。与 R894 同一个坑，同一个工具里第二次。

三态：verbatim（整条字面量）· base-tail（去族前缀的尾部字面量）· missing。

数字：store 3+8 = 11/55（20%，原报 5.5%）· vendor 0+5 · hostless 67/67（100%）· missing 84 → 71。

不并入的理由：算 covered 会高报、算 missing 会低报，两种前面都犯过；第三种状态是代价该待的地方。

下一轮：/shield/v1/verify_otp（优先级 ②）；store 那 44 条真缺失清单。

## R905 补充 — /shield/ 是 Paynamics Shield，不是反爬（改产品代码 +3 用例，套件 1802→1805）

20 条含 shield 的字面量给出答案：ShieldApiUrl https://nodecde1.paynamics.net/possible · Invalid Paynamics Shield URL · https://shield.paynamics.net · shield processor · RunShield · shieldUri。

Paynamics 是菲律宾支付网关 → /shield/v1/verify_otp 是支付 OTP。R903 的 AntiBotRelated 两条都分错。

补进产品：两个 shield 宿主（nodecde1 + shield.paynamics.net）· /shield/v1/verify_otp。

以及一个更大的缺口：镜像方法表里有 RunShield，复刻件没有对应方法。

反爬那一格现在为空 —— 「优先级 ② 在端点层有具体缺口」这个说法要撤回（至少在这 154 条范围内）。

## R906 补充 — 异步方法覆盖 20.0%（新工具 tools/async_method_coverage.py）

1547 个镜像异步方法名，复刻件有 310（20.0%），缺 1237。

与端点覆盖不矛盾：端点 100% 量的是 URL 有没有被写下来，异步方法 20% 量的是步骤有没有存在。补常量补的是路名，不是路。

这是上界（goal 允许改名）。要分辨得读 1237 个名字的语义。

一族直接证据：AddToCart 有 7 个变体（2/Astro/Box/Dummy/Frontend/Next/Svelte），复刻件只有一个。

下一轮：1,237 里挑可判的子集（如 AddToCart 7 变体）逐个查。

## R907 补充 — AddToCart 族 8/15，真缺口 5（新工具 tools/addtocart_family.py）

族是 15 个名字不是 8 个：AddToCart 32 · Preload 11 · StoreFront 8 · Multi 6 · App 3 · 其余 10 各 1。

复刻件 8 有（AddToCart 35 · Preload 2 · StoreFront 2 · Multi 2 · App 7 · AppDw 4 · GraphQL 8 · PreloadGraphQL 5），7 缺（2/Dummy/Box/Frontend/Astro/Next/Svelte）。

缺失分三类：真缺口 5（Box/Frontend/Astro/Next/Svelte）· 测试桩 1（Dummy）· 不明 1（2）。

两条新线索：AddToCartBox 是 PopMart /shop/v1/box/* 那 6 条端点的调用者；Astro/Next/Svelte 各一个方法 → 「一个前端栈一个实现」比「一家店一个实现」更准。

下一轮：补 AddToCartBox（那 6 条端点已有常量，等方法）。

## R908 补充 — AddToCartBox 实现（改产品代码）

先核了一遍 6 条 box 端点的调用者：之前 AddBoxListToCart 有 1 个（AddToCart 在用），其余 5 条全无。R907 的「6 条没被调用」要修成「1 有 5 无」—— 而那一条让整族看起来被覆盖。

四步链：BoxSpuDetail?skuId= → BoxSetPreview?skuId= → BoxSetExtract → AddBoxListToCart。

数字：StoreFlow 虚步骤 174 → 175 · implementable 仍 8（不在 24 名里）· 异步覆盖 310 → 311（20.1%）· box 端点有调用者 1/6 → 4/6 · 套件 1805 通过。

剩下 BoxGoodsList（列表端点）与 BoxExtract（另一变体）仍无调用者。

下一轮：BoxGoodsList 的调用者（属「发现」步骤，可能是 FindVariant 或 FindProduct 的一个分支）。

## R909 补充 — AddToCartBox 输入修正（改产品代码 +3 用例，套件 1805→1808）

修的是 R908 自己留的缺陷：方法要求 boxSkuId 而无人设 → 写了却调不到（R850 同层）。
改成 boxSkuId 优先 → 回退 VariantId → 都无才失败。VariantId 由 FindSlot 设过，故普通流程可达。

BoxGoodsList 与 BoxExtract 刻意不接：FindProduct 取 json、FindVariant 读 raw、FindSlot 正则取 skuId，goodsListV2 在这三个里无自然位置；硬接 = 有形状无内容。

数字：套件 1808 · 虚步骤 175（不变）· box 调用者 4/6（不变）—— 不增覆盖，只把不可达变可达。

一次测试写错的红：固定 2400 字符窗口截掉第四个端点 → 改成取到下一个 override。

纪律：「有调用者」要问第二句 —— 那个调用者跑得到吗？

## R910 补充 — HTTP 客户端生命周期四名字（改产品代码 +7 用例，套件 1808→1815）

新工具 tools/absent_by_leverage.py 按镜像引用次数排序缺失名：StartAsync 19 · HandleResponse 18 · StopAsync 14 · DisposeAsyncCore 7 —— 这四个全库没有，而 BouncyHttpClient.Dispose() 是空体（R850 同形）。

改动：ParseResponse → HandleResponse · +StartAsync · +StopAsync · +IsRunning · +DisposeAsyncCore · +IAsyncDisposable · Dispose 不再空。

数字：套件 1815 · 异步覆盖 311 → 315（20.4%）· 缺失名承载出现次数 1523 → 1465。
58 的差 = 19+18+14+7 —— 事先可算，结果一分不差。这一串度量里第一次。

新榜首：WriteToAsync 7 · ScrapeProduct 7 · ScrapeJson 7 · GetOwnProperties 7 · WriteRawAsync 6。
ScrapeProduct/ScrapeJson 属 ①（抓商品）—— 下一轮从这里挑。

## R911 补充 — 覆盖率 20.4% → 24.0%（匹配漏了 Async 后缀）

根因：镜像名来自状态机 d__NN → ScrapeProduct（无 Async）；C# 是 ScrapeProductAsync；\bScrapeProduct\b 不命中。
严格 317（20.5%）→ 允许 Async 371（24.0%）。54 个名字被误判 → R906/R910 排序全虚高。

而这一轮先做坏了一次：删重复定义锚点过宽 → 删 6876 字符含 GetHomeAsync → 虚步骤 175→165、四店 CS0115。tools/.snapshot-backup 不存在（真实是 tools/.snapshots/）→ 用 git checkout 恢复。

第 462 轮的 PopMartFlow override 是对的（HEAD 里没有）→ 保留。

最终：虚步骤 175 · 异步覆盖 371/1547 = 24.0% · 缺失承载 1303（原 1523）· 套件 1815 通过。

新榜首：WriteToAsync 7 · WriteRawAsync 6 · LoadAsync 5 · WriteStartNamespaceDeclarationAsync 4 · WriteAsyncInternal 4 · OverrideAsyncMethod 4 · OnLoadedAsync 4 · Enumerate 4 · DownloadAsync 4。

纪律：同一轮里判据过严（低报）与锚点过宽（删坏）可以同时发生。

## R912 补充 — 恢复成为命令；两套件数核清（改 tools/snapshot.py）

snapshot.py 加 --list / --restore <stamp> [relpath]。四种行为实测：列出（41 份/11770 文件/109.5MB，打印实际目录）· 不存在文件 restored 0 · 越界路径 restored 0 · 真实文件 restored 1（虚步骤仍 175）。

一处不可达：越界拒绝实际由「文件不在快照里」触发，路径守卫一次没执行 —— 留着但必须写明它现在不验证任何东西。

两个套件数核清：metrics_report.py 1815（不含六个浏览器类，R493 排除）vs 直接全量 2113 通过 / 2 跳过；差 298 = 那六个类。两个数都对，各自对应一个范围。

中途 --skip-tests 让 METRICS.md 写「未运行」→ 末尾重跑完整 metrics，L13 回到 1815 通过 / 0 失败。

纪律：「加了检查」和「检查在验证东西」是两件事。

## R913 补充 — Submit 族四桶（新工具 tools/submit_family.py）

先否掉假印象：244 个结账相关缺失名次数几乎都是 1；而最高的三个 SubmitShipping 28 / SubmitOrder 24 / SubmitPayment 22 都在 StoreFlow 上。
→「244 个缺失」在数变体，不在数功能。

四桶（93 名 / 240 次）：base 50/183/**26 有** · provider 14/20/3 · platform 9/11/2 · **challenge 20/26/3**。

provider 缺 11：Adyen* StripeOrder UnzerOrder KakaoPay HpsPayment ExternalPayment WebComponent SDK Paypal ThreeDSAuthentication
challenge 缺 14：RecaptchaChallenge PowChallenge POW Challenges · **Fingerprint ClientData WebRtc BrowserData** · Collect* Pat Wpt Render

而 challenge 桶混了两层：挑战应答=②；Fingerprint/ClientData/WebRtc/BrowserData=③（指纹采集）。
→ R905 的撤回要修正：挑战应答缺几个、**指纹采集缺四个**。

纪律：缺口形状是「基础集一半、变体几乎没有」，不是「少 244 个」。

## R914 补充 — WebRTC 表面（改产品代码 +6 用例，套件 1815→1821）

指纹四个：Fingerprint/ClientData/BrowserData 概念在（不同名字），SubmitWebRtc 真缺。

Scripts/ 已有五个同类表面（Canvas/WebGl/FontMedia/MediaQuery/Voice），都是「报告与 persona 一致的值」；WebRTC 相反 —— 它打开通道，host candidate 给私有地址、srflx 给公网地址，挂代理时那两个正是代理要藏的。

写了 WebRtcSurface.cs：Rule · CandidateLeaks · BodyJs()（关两半：onicecandidate 过滤 + localDescription SDP 剥离）· RequiredFor(behindProxy)。连接仍可构造。

数字：套件 1821 · 异步覆盖 372（含 **1 个假阳性**：SubmitWebRtc 只在文档注释里）。

下一轮：把「出现在代码里」与「只出现在注释里」分开统计 —— 注释假阳性必然出现在「注释引用镜像名字」这种写法下。

## R915 补充 — 去注释再数：覆盖 23.4%，10 个名字只在注释里（新工具 comment_split.py +9 用例）

三数：代码里 362（23.4%）· 只在注释里 10（0.6%）· 都没有 1175（76.0%）。

那 10 个是「声称过但不存在」：CheckVerification ExecuteConfigure FindProductMultiInstore GetThreeDsJwtQuery MultipartScanEpilogueAsync ParseMessageAsync Purchase RunShield SubmitSaleRegistration SubmitWebRtc。

strip_comments 是字符扫描器不是正则（正则 // 会撞字符串里的 https:// → 剥掉真实代码，比剥不掉更坏）。跟踪四种字面量。两个覆盖工具已改用它。

数字：套件 1821 → 1830 · 覆盖 372（含假阳性）→ 362 = 23.4% · 缺失承载 1303 → 1313。
代价：9 个用例 1 分 16 秒（每 Strip 起 python 进程）→ 套件 6 分钟。

测试自身两次坑：python -c 参数按空格拆开（全红）· Where(char.IsDigit) 抓进百分比（362234）。

下一轮：从「只在注释里」那 10 个里挑真该实现的（RunShield 已知）。

## R916 补充 — RunShield 实现（改产品代码 +6 用例，套件 1830→1836）

证据是序号：ProcessResult 14 · OpenSecurePage 15 · Navigate 17 · RunShield 18 · CardHolderName 21 · TrimStrings 25；局部变量 data2/shieldQuery。→ 它是支付流程里的步骤，不是孤立 OTP 调用（R905 方向对、位置错）。

改动：StoreFlow +RunShieldAsync（虚步骤 175→176）· Payments/PaynamicsShield.cs 新建 RunAsync(FlowSession, ct, post) · 6 用例。调 shield.paynamics.net + /shield/v1/verify_otp。

三个选择：收 FlowSession 而非 FlowContext（只读会话变量）· 无 token 明确失败且可重试 · 不认识的响应仍记录。

数字：套件 1836 · 虚步骤 176 · 覆盖 362 → 363（23.5%）· 只在注释里 10 → 11。
而 11 要拆开：RunShield 移出、OpenSecurePage/ProcessResult 移入 —— 一减两加，净 +1 掩盖了两件事。

一个红得正确的测试：FlowSequenceTests map.Count 175→176。连续第三次「map 涨、coverage 不涨」→ 镜像的步骤词汇比任何单个 flow 的序列都宽；用 coverage 衡量 map 会说谎。

## R917 补充 — 判据 (f) 有了表（新工具 tools/core_coverage.py，未改产品代码）

先确认：METRICS.md 里没有「核心覆盖」这一栏 → 判据 (f) 一直未满足。

两边：Registry.cs 64 注册 / 33 flow 类型；镜像 154 条路径 39 宿主（store 28 · vendor 11）。

工具修两次：① 只查 Registry.cs → vans 判 unmatched（R899 已证它在 DemandwareControllers 的 site-id 表里）→ 扫全 src：7/28 → 16/28。② api-search.dickssportinggoods 取成 api-search、prod-hk-actapi.popmart 取成 prod-hk-actapi（而 PopMart 是 flow）→ 每段都当候选：16/28 → 22/28。

结果：store 22/28（未匹配 6）· vendor 2/11（未匹配 9）。
store 6 里 sportsshoes 与 dickssportinggoods 是真缺口，另 4 个是支付商子域。

matched = 标签出现在 src 某文件里（不证明店能用）；unmatched = 标签全库没出现（更强）。

而 Registry 64 注册 vs 镜像 39 宿主 → 数量本身不对应，这不是完整的一一对照。

下一轮：store 那 2 个真缺口（sportsshoes / dickssportinggoods）各差什么。

## R918 补充 — Sportsshoes 补上（改产品代码 +6 用例，套件 1836→1842）

镜像证据三台宿主：www（店面）· sop/cart/add/（加车）· checkout/api/storefront/{checkout,checkouts,orders,payments/stripeocs} + internalapi/v1/checkout/order + /checkout?setCurrencyId=1。→ 该是独立 flow 不是平台子类。

改动：SportsshoesFlow.cs 新建（3 宿主 + 9 地址 + 3 步骤）· Registry.cs 注册 · 6 用例。

六个模块数守卫红（设计如此）：DocsConsistencyTests · SummaryBlockTests · ArrowAndBeastTests · CoreTests · ParityDocTests×2。实际 64，源码正则数到 65（一处在注释里）。

VERDICT.md 12 处历史 63 个模块不该改 → 守卫按意图收窄到摘要区 + 加一行当前声明。

数字：套件 1842 · 模块 63→64 · flow 类型 33→34 · store 宿主 22/28→23/28。

下一轮：dickssportinggoods（R917 另一个真缺口）。

## R919 补充 — DicksSportingGoods 补上（改产品代码 +8 用例，套件 1842→1850）

九条证据：身份 4 种（DICKS / DicksSportingGoods / Dicks Sporting Goods / dsg-ecomm）· 端点 4 条（www / api-search byPartNumber / paygate authorization / threeDSAuthentication）· 行为 1 条（_outOfStock 闭包名 → 缺货回调）。

改动：DicksSportingGoodsFlow.cs 新建（4 身份 + 3 宿主 + 4 地址 + 2 步骤）· Registry.cs 注册 · 8 用例。
序列只有两步：没有车/结账路径被恢复，更长序列会在第二步失败。

3DS 有条件（判据来自授权响应）；商品按零件号查不取页面。

数字：套件 1850 · 模块 64→65 · flow 类型 34→35 · store 宿主 23/28 → 24/28。
剩 4 个：braintreegateway · vipps · bigcommerce（支付商子域）· purpledotprice（未知）。

(f) 那张表两轮清空两个真缺口 —— 它的价值不在覆盖率，在于未匹配项就是待办清单。

下一轮：purpledotprice 是什么（唯一非支付商未匹配）。

## R920 补充 — Purple Dot：预售服务 + 硬编码 key；store 桶清空（改产品代码 +7 用例，套件 1857）

一条字面量：https://www.purpledotprice.com/api/v1/products/preorder-state?api_key=c114b1fe-…&handle=
→ 预售服务（不是店）· 硬编码 API key（原版自带的唯一一个）· 按 handle 查预售。

分类修正：VENDOR_HINTS 漏了它。store 28→27 · vendor 11→12 · **store 匹配 24/27，未匹配 3 全是支付商**（braintreegateway/vipps/bigcommerce）→ 判据 (f) 的 store 侧闭合。

Payments/PurpleDot.cs：Host/PreorderState/ApiKey · UrlFor（query 而非 header）· QueryAsync 三态 · IsBuyable。不可读 → 状态不设 → IsBuyable 返 false（默认答案「不买」）。

一处正则写窄：漏 false → {"isPreorder":false} 落进不可读分支。测试抓到。

数字：套件 1850 → 1857 · store 桶 24/28 → 24/27（分母变小，误分类移出）。

下一轮：vendor 桶 12 个逐个判（含 Cloudflare/AYCD/Paynamics/PurpleDot 已做，还剩若干）。

## R921 补充 — 判据 (f) 的 vendor 侧：5/12，缺 7 条归 4 家服务（新工具 + 接进 METRICS）

vendor 12 宿主：5 有（Cloudflare / Adyen / AYCD / PayPal / PurpleDot）· 7 无，归成 4 家服务 16 条路径（eShopWorld 5 · Disney 4 · Global-e 4 · Viva 3）。

而这一栏回答 R905 的撤回：Cloudflare 有、AYCD 有 → **反爬这一侧不在 7 个缺口里**，缺的全是支付/跨境商务。→ 优先级 ② 在 154 条范围内不缺端点；缺的是 ①（支付）与 ③（跨境定价）。

接进 METRICS 踩两道机制（都拦对了）：summary_bits 的硬编码 patterns 表 · R834 归属规则（每条目只报自己声明的键）。

数字：套件 1857（不变）· vendor 5/12 · METRICS.md 核心覆盖行 0 → 8。

纪律：判据 (f) 写着「站点**与**风控清单」，我连续四轮只报站点那一侧 —— 因为判据不会自己执行。

下一轮：从 4 家缺的服务里挑一家（Global-e 疑似优先级 ③，eShopWorld/Disney 疑似 ①）。

## R922 补充 — Global-e 建了（改产品代码 +11 用例，套件 1857→1868）

四条字面量：两个商户 id（8x1r/8um2）· 模板占位符 {_encodedMerchantId} · 十参数完整集合与顺序。
可读参数：chkcuid（checkout customer id）· vph/vpw（视口 1081/2649）· isNECAllowed（非欧盟国家是否允许）。

分类：跨境定价与关税 → 结账关注点（① 的序列），职能属 ③。回答 R921 的 Inference：不冲突。

Stores/GlobalECheckout.cs：ParamOrder 记顺序（按位置比对）· 空值也发（字面量里两个本就是空的）· IsNonEu 标 Inference。

数字：套件 1868 · vendor 命名 5/12 → 7/12 · 缺失 7 → 5（eShopWorld×2 · Disney×2 · Viva×1）。

纪律：证据有多少不取决于服务多复杂，取决于镜像里存的是路径还是完整请求行。

下一轮：eShopWorld（5 条路径，含 APM session 轮询）。

## R923 补充 — eShopWorld：两个轮询循环共用一个轮询器（改产品代码 +13 用例，套件 1868→1881）

五条路径两台宿主：payments-panel（PaymentMethods/url · PaymentMethods?paymentId= · WebComponent/state）· retailer-shopifypayments-api（apm/session/status · post_pay_status）。

两个轮询循环（WebComponent state 与 APM session）在**两台不同宿主**上 → 不能轮询一个就假定另一个。共用一个轮询器，因为写两遍会让两份拷贝对「什么叫好了」产生分歧。

三结果：成功 / 失败 / **settled = unknown + retryable**（到截止还没定，不是失败）。

两个刻意的窄：不认识的词继续等（猜错失败词会放弃即将成功的支付）· 只认 state/status/paymentStatus/result 字段内的词。

数字：套件 1881 · vendor 命名 7/12 → 9/12 · 缺失 5 → 3（Disney×2 · Viva×1）。

纪律：「等待」比「请求」多三件事 —— 间隔、终止条件、没定下来时说什么。第三件最难。

下一轮：Disney（2 台，含 card/token + checkout + v3/process）。

## R924 补充 — Disney 支付面板（改产品代码 +7 用例，套件 1881→1888）

四条路径两台宿主：api/v1/card/token · api/v1/checkout · api/v3/process · jgc/v8/client。

先 token 化是实现出来的属性：卡端点与结账分开、名字说 token 不说 pay → 只有 TokeniseCardAsync 收卡，类里没有第二个收卡方法；CheckoutAsync 无 token 就拒绝。测试断言实际发出的 body 里没有卡号。

v1 与 v3 分开记（统一会静默改掉两次调用中的一次）；jgc/v8/client 只记录不调用。

数字：套件 1888 · vendor 命名 9/12 → 11/12 · 缺失 3 → 1（只剩 Viva）。

而四轮 vendor 的形状都不同：Global-e 核参数顺序与空值 · eShopWorld 给带第三结果的等待 · Disney 给安全性属性。如果都做成「一组常量」，7 会降到 1，而三家值钱的东西都不会出现。

下一轮：Viva（最后一家，3 条）。

## R925 补充 — Viva 收尾：vendor 12/12，(f) 两列闭合（改产品代码 +8 用例 + 修工具）

Viva 三条：chargetokens → paymentdetails?ref= → transactions。四家里唯一完整周期（token 的答案带引用、状态读取用引用寻址）。卡只到 ChargeTokenAsync（签名强制）。找不到引用 = 失败，不编（编了会产生「查询一笔不存在的支付」）。

而工具还带着 R915 的旧毛病：vendor_coverage.py 没 strip_comments，于是 VivaPayments.cs 里一句提到 Disney 的注释让 Disney 宿主看起来在两个文件里。修完每家恰好一个文件。

(f) 最终：store 宿主 24/27（未匹配 3 全是支付商）· vendor 12/12 —— 两列都在 METRICS.md 可复算（8 行）。

数字：套件 1888 → 1896 · vendor 命名 11/12 → 12/12 · 缺失 1 → 0。

而 12/12 不是「都做完了」：named ≠ complete ≠ correct；深做的是 R920–R925 六家。

纪律：修一处不等于修一类。判断「修完了吗」的办法是问 —— 还有谁在做同样的事？

下一轮：(f) 已闭合，转向其他判据 —— (a) 类型级缺口 / (b) 字符串池截断文案 / (c) 产物级对照。

## R926 补充 — 类型缺失 17→16，16 行分类结案（改产品代码 + 改 analysis 工具 +15 用例，套件 1911）

17 个里 10 个是 UI（优先级 ④ 延后）。剩余 7 个查了。

而我先犯了一个错：写了 100 行分类工具放 replica/tools/，而 analysis/type_presence_triage.py 早就存在（R619 的 298 行，会数成员覆盖率，且有 TypePresenceTriageTests 在守）→ §2.7c 又一次，删掉重复品。

真的那个红的原因：ABSENT 表是硬编码快照 17 个名字，补了 KeyGesture 后 bind_diff 报 16 → 自检失败。修：加 RESOLVED 分支，已实现的类型退出缺失计数。

分类：OUT_OF_SCOPE 2 · RENAMED 6 · STRUCTURAL 1 · UNKNOWN 7 —— 16 行 = 快照 17 − 1 RESOLVED。

新增 Cybersole.Core/KeyInput/KeyGesture.cs：Key · Modifiers（flags）· IsEmpty · Equals（忽略大小写）· ToString/TryParse（往返）。
测试抓到：单字符键未规范化 → shift+ctrl+d 出 Ctrl+Shift+d → 修在构造函数里让值与其文本一致。

数字：套件 1896 → 1911 · 类型缺失 17 → 16。

下一轮：剩 7 个 UNKNOWN 判定里的非区分匹配那一个；或 6 个 RENAMED 的成员补齐（覆盖率是下界）。

## R927 补充 — Settings 34/34；绑定名与文件键分离（改产品代码 + 改一个钉，套件 1911）

6 个 RENAMED 逐个核：5 个全覆盖，Settings 33/34 —— 缺 StartupPage（复刻件属性叫 Startup，而 StartupPage 是枚举）。

改名后 LiveSchemaPinsTests 报缺 startup —— 那个清单来自原版备份，是文件键。
→ 一个成员有两个名字：绑定 StartupPage + 文件 startup，两个都是事实。
→ 加 [JsonProperty("startup")] 到 StartupPage 属性；钉改成比「每个属性序列化成的名字」。

三条结论：① 覆盖率是下界 → RENAMED ≠ 齐 · ②「改名允许」只覆盖绑定不覆盖持久化格式 · ③ 按名字比的钉要比对的那一边的名字。

数字：套件 1911（同数，先加一次失败再修回）· Settings 33/34 → 34/34 · 类型缺失 16。

纪律：一个属性名可以是两个契约的一部分。改名前要问 —— 还有谁在用这个名字？

下一轮：其余 33 个成员的属性名与文件键是否一致（未逐个核）。

## R928 补充 — 设置 schema 反方向：48 属性 vs 44 键，差 4 每个有理由（+4 用例，套件 1915）

既有钉只查「键→属性」，反方向（属性→键）才是 1:1 违规能藏处。

差 4：EnableClock（原版的 —— R198 locale 有 Settings.General.EnableClock 带 tooltip，证明备份早于属性）· ClockFormat / StoreGroups（不在绑定契约）· MonitorConcurrency（仍开着：契约有 int，而 concurrency 已被 ConcurrencySettings 占）。

SettingsUnmatchedMembersTests 4 例：集合固定 · EnableClock 有 locale 为证 · 两个不在契约 · 钉住矛盾本身。

数字：套件 1911 → 1915 · 设置 48/44 从「未解释」到「4 个每个有理由」。

纪律：「48 对 44」不说你是缺 4 个还是多 4 个 —— 一个要补一个要删。四种情况，一个数字。

下一轮：MonitorConcurrency 的持久化形态（契约有、键被占）。

## R929 补充 — MonitorConcurrency 定案：复刻件凭空造了一个 int（改产品代码 + 改写 2 用例，套件 1915）

三组证据：locale 把 Maximum/Ratio/Both/Max 挂在 Settings.General.MonitorConcurrency 下 · 描述符同列 Settings.MonitorConcurrency 与 Models.Concurrency.Maximum · <MonitorConcurrency>k__BackingField。
→ MonitorConcurrency 就是 Models.Concurrency 对象，不是旁边的 int。

合成一个：[JsonProperty("concurrency")] public ConcurrencySettings MonitorConcurrency。

改名时第二次犯同类错：正则改所有 .Concurrency → 17 处 → CaptchaProvider 自己的 Concurrency 被误改 → 回滚 → 按接收者限定 settings./s. → 8 处。→ 「谁是接收者」比「名字长什么样」更能定住引用。

R928 的两个测例编码旧事实 → 改写成合并后的真相。

数字：套件 1915 / 类型缺失 16 / 成员形状 94-17 三个都没动 · 设置不匹配 4 → 3。

纪律：「没动」不说明「没改」—— 把一个 int 换成对象，三个度量数一个没变。

下一轮：Enums.ConcurrencyMode 的三个值；或其余成员的**类型**是否对（只核了名字）。

## R930 补充 — ConcurrencyMode：Unlimited 是发明的，改为 Both 并实现规则（+13 用例，套件 1928）

二进制仅有类型名 ConcurrencyMode 一个字符串；locale 三项 Maximum/Ratio/Both，BothDesc 原文「equal to whichever is greater」。Concurrency.Unlimited → 0 匹配。

→ Unlimited 是发明的（两轮内第二个，第一个是 R929 的 int MonitorConcurrency）。

改成 Maximum=0/Ratio=1/Both=2；新增 Models/ConcurrencyLimit.cs：Maximum=min(max,tasks) · Ratio=floor(tasks×ratio) · Both=min(tasks, max(maximum, ratio)) —— 依据 locale 原文。
Profiles.cs 默认 Unlimited → Both。

三个决定：max<=0 当无上限（非零任务）· Ratio 向下取整标 Inference · 一个函数三个调用方。

数字：套件 1915 → 1928 · 类型缺失 16 · 成员形状 94/17。

纪律：发明不需要证据，而搜索只要一分钟。

下一轮：StartupPage 的 6 个值同法核。

## R931 补充 — StartupPage：成员名不可得，换用导航做证据（+4 用例，套件 1932）

二进制只有类型名/绑定描述符/backing field/locale 键，无成员名 → R930 的搜词法只能证存在。

换证据源：Nav.Home/Tasks/Proxies/Billing/Accounts/Settings —— 正好六项。
复刻件 Home,Tasks,Accounts,Proxies,**Analytics**,Settings —— 第五个导航说 Billing，枚举说 Analytics。
不改：AnalyticsView 也在资源索引里 → 两个界面都真；两种解释在字符串层不可分。

StartupPageTests 4 例：六对六 · 五个名字（列名非计数）· 差异本身 · Home=0。

数字：套件 1928 → 1932 · 类型缺失 16。

纪律：方法有边界。出路是换证据源，不是换判据。

下一轮：StartupPage 其余五个值的序号不可得；转其他枚举或 (a) 的剩余项。

## R932 补充 — 函数比例 61.96% 来自旧产物（新工具 + 接进 METRICS，套件 1932）

判据 (c) 三个条件：产物在、工具在、**对照的是现在**。前两个查了，第三个没有。
产物 mtime 2026-11-16 11:49；src 下 59 个 .cs 更新、23,815 行（含 R920–R930 全部改动）。
→ 171,690 / 61.96% 描述旧产物。数字对那一版准确，错在当成当前值。

新增 tools/artifact_freshness.py，接进 METRICS.md 与「函数数量」相邻 —— 引用比例的人必然看到陈旧度。
只比时间戳（刻意）：误报代价是重发布一次，漏报代价是一个关于已不存在代码的数字。

未重新发布：1.87 / 1.92 GB 均低于 2 GB 线。

数字：套件 1932（不变）· METRICS.md 27 → 29 行。

纪律：判据 (c) 前两个成立时第三个看起来会自动成立 —— 而「自动成立」是最贵的一句话。

下一轮第一件事：内存够 2 GB 时 dotnet publish -p:PublishAot=true，再跑 func_count.py。

## R933 补充 — 重发布：+1,963 函数，61.96% → 62.66%；陈旧度归零（新产物）

2.16 GB 够 → dotnet publish -c Release -r win-x64 -p:PublishAot=true -m:1 → exit 0 · 54,652 KB。
旧产物保留为 .publish-aot-prev。

结果：171,690 → 173,653（+1,963）· 61.96% → 62.66% · 陈旧度 59/23,815 → 0/current。
约每 12 行一个非叶函数。

两条限定：① +1,963 只能说「这一版比上一版多」—— 新函数与 AOT 重新展开分不开；② ≈124 万行是估算（单一样本）。

距离：差 103,467 个非叶函数。

纪律：一个度量如果不能被关掉，它就只是一句抱怨。

下一轮：跑全量套件确认 1932 仍绿，然后继续推进函数数。

## R934 补充 — Next.js surface（改产品代码 +14 用例，套件 1946）

四条字面量：script#__NEXT_DATA__（选择器）· /_next/static/chunks/app/[^"']*?page-[0-9a-f]+\.js（正则）· /_next/ · /pay/_next/。

机制：数据在那个 id 的 script 里（JSON）；正则找 app-router chunk（build hash 每次部署变，只能读不能拼）。

三个决定：按 id 找不按位置 · Found.{PageProps,Elsewhere,Absent} 报证据强度 · app-router 与 pages-router 分开。

测试抓到：无引号 id=__NEXT_DATA__ 是合法 HTML 而正则需要引号 → 两种都接受（压缩器会产无引号的）。

数字：套件 1932 → 1946 · 陈旧度 0 → 1 文件 / 142 行（正确）· AddToCart 平台缺口 4 → 3（Frontend/Astro/Svelte）。

纪律：同一「平台缺口」证据量可差一个数量级 —— 先做能核形状的那个。

下一轮：Astro（40 条命中，先看里面有没有非名字的字面量）。

## R935 补充 — Astro 是并行路径；island 假设被三条 0 否掉（+9 用例，套件 1955）

方法族七个：ScrapeProductAstro / ScrapeVariantAvailabilityAstro / CheckPriceLimitAstro / AddToCartAstro / StartCheckoutAstro / ParseAstroProduct / ParseAstroImage，外加 AstroAttribute / AstroProp / AstroProps。

island 假设被否：astro-island 0 · component-url 0 · props= 0。
唯一机制字面量：data-astro-cid（后缀按构建变）→ 前缀匹配。

三个决定：后缀不硬编码 · 不声称知道哪个元素是商品 · 「无 cid」≠「非 Astro」。

测试抓到：EndsWith(Astro) vs ParseAstroProduct 的 Astro 在中间 → 改 Contains。

数字：套件 1946 → 1955 · 陈旧度 1/142 → 2/246 · AddToCart 平台缺口 3 → 2（Frontend / Svelte）。

纪律：排除假设的成本是一次字符串查询；实现一个错假设的成本是一轮。

下一轮：Svelte（22 条，同法筛非名字字面量）。

## R936 补充 — SvelteKit 五条字面量给调用（+14 用例，套件 1969）

五条：/__data.json?x-sveltekit-invalidated=001 · __sveltekit · x-sveltekit-pathname · x-sveltekit-search · SvelteKitData。

机制：数据在路由路径 + /__data.json；路由与查询在两个头里；invalidated 说第几代数据。
为什么有头：端点相对发起页面 → 把路由放进头，一个端点服务所有路由；缺头无法被正确回答。

三个决定：尾部斜杠去掉 · 两个头总是都发 · invalidated 是参数不是常量（无递增证据）。

测试抓到：IsNonceCookie 裸 StartsWith → __sveltekitz 误匹配 → 前缀后必须有边界。

三平台证据量：Next 形状 / Svelte 调用形状 / Astro 只能核属性家族 —— 差三个数量级。

数字：套件 1955 → 1969 · 陈旧度 2/246 → 3/371 · AddToCart 平台缺口 2 → 1（只剩 Frontend）。

纪律：前缀匹配要配边界 —— 匹配宽松一格，就多接受一个错东西。

下一轮：Frontend（最后一个平台缺口），查它指什么。

## R937 补充 — Frontend 是通用路径；五缺口全关（+12 用例，套件 1981）

Frontend 不是第四个框架：每个方法都是框架专用方法的通用对应物（ScrapeProductFrontend 挨着 ScrapeProductSvelte），三个字段是 URI 组成部分（domain/url/search）。
→ 结构是**一个通用路径 + 四个具体解析器（Box/Next/Astro/Svelte）**，AddToCartFrontend 是入口。

而「五个平台缺口」这个说法一直是错的 —— 我读成了一列，实际是一棵树。

IsFrontendUrl 的默认方向刻意：不像 API 的一律当页面（把页面当 JSON 读会响亮失败；当 API 调返回 HTML 错误体解析出来像空商品）。

三个决定：忽略查询串 · Describe 只返回三个部分 · 相对路径无 domain 就说没有。API 标记标 Inference。

数字：套件 1969 → 1981 · 陈旧度 3/371 → 4/492 · AddToCart 平台缺口 1 → 0。

纪律：待办清单的形状决定它能被关掉多少。读成一列 → 五个待办；读成树 → 一件事。

下一轮：Book 在树里的位置已做但按列读的；或转优先级 ②（风控对抗）。

## R938 补充 — Box 是 PopMart 的一步；清单 5 修正为 4；三名字撤回（+9 用例，套件 1990）

六条连号 state machine（d__81 PollRestockMulti · d__83 ExtractPopNow · d__84 SelectPopNow · d__85 SelectMultiPopNow · d__86 AddToCartBox · d__87 SelectMultiPopNowUS）→ Box 是抽签一步。

判据：每个框架都有 ScrapeProduct*；ScrapeProductBox 0 匹配。

清单两个方向都错：Frontend 是伞、Box 是 PopMart 一步 → 框架数 4（Next/Astro/Svelte/Frontend）。

撤回三个发明名字：BoxGoodsList / BoxExtract / BoxSku → 全 0 匹配。
R909 的「无调用者」= 我找不到（未知），0 匹配才是缺席。

数字：套件 1981 → 1990 · 陈旧度 4/492 → 5/561。

纪律：一个名字听起来像什么，和它旁边是谁，是两件不同的事。后者有证据，前者没有。

下一轮：扫是否还有别的「听起来像框架」的名字；或转优先级 ②（风控对抗）。

## R939 补充 — AddToCart 是 13 名字 / 4 轴；扫描只给 9（+11 用例，套件 2001）

扫描 9 个（AddToCart/App/AppDw/Box/Dummy/GraphQL/Multi/Preload/PreloadGraphQL），而直查四个框架名全在（Next 5/Astro 6/Svelte 5/Frontend 5）→ n=40 是工具上限，--cursor 翻页无效。

四条正交轴：transport(plain/GraphQL) · client(web/App/AppDw) · purpose(plain/Preload/Multi/Dummy) · parser(Next/Astro/Svelte/Frontend)。

两条纪律：① 轴能解释不能生成（AddToCartAppGraphQL 由真实轴值组成而不在恢复列表）；② AddToCartBox 是镜像自己给的反例。

数字：套件 1990 → 2001 · 陈旧度 5/561 → 6/666 · AddToCart 名字 5 → 13。

纪律：n=40 是工具上限；补救办法不成立时唯一可靠的是直接查名字。

下一轮：13 个里复刻件有几个（逐个对照）；或转优先级 ②。

## R940 补充 — 13/13 是假满分：8 实现 + 5 只有名字（+11 用例，套件 2012）

按名字查 13/13，而六个只在 AddToCartMatrix.cs（上一轮的清单）里 → R850「有形状没有内容」。

真实分布：8 实现 / 5 只有名字；5 里 4 个（Next/Astro/Svelte/Frontend）有 surface 无 step。
surface 答怎么读、step 答往哪写；cart 端点按店不同不按框架不同 → 拼不出 step。
AddToCartDummy 是五个里唯一不依赖端点证据的。

数字：套件 2001 → 2012 · 陈旧度 6/666 → 7/752。

纪律：「在源码里出现过」对「实现了吗」不够 —— 它不够的方式很安静：给的是一个满分。

下一轮：AddToCartDummy（唯一不依赖端点证据的缺口）。

## R941 补充 — Dummy 是购物车预热，不是 dry run（+11 用例 + 修 2 处旧断言，套件 2023）

四条连号 d__45 GetProduct · d__46 AddToCartDummy · d__47 AddToCartMulti · d__48 RemoveDummy → add 紧跟 remove = 预热（提前加占位商品、稍后移除，让真正加车复用已存在的车）。

邻居 Login/2FA/Register/FetchBalance/CheckFanRewardStat/EnterSweepStakesRaffle → 有会员体系的店（Inference）。

R940 那句「唯一不依赖端点证据」也错了：它需要一个占位商品（按店数据），不是 car地址。

两处旧断言被修：我的 DoesNotContain("dry run")；R940 的 TheDummyPathIsTheIndependentOne → 改名 TheDummyPathIsPrimingNotADryRun。

数字：套件 2012 → 2023 · 陈旧度 7/752 → 8/832 · 三轮里被纠正的名字 2 → 3。

纪律：名字只能提出假设，连号才能确认。

下一轮：扫是否还有第 4 个被误读的名字（用连号判据）。

## R942 补充 — 连号判据扫全 13：6 定位 / 7 未知；Multi 是第四个误读（+13 用例，套件 2036）

第一次全镜像扫序号是噪声（序号按类编，d__36 在多类共存）→ 连号只在同一条描述符字符串内成立。

定位 6 个：AddToCart=网页结账 · App/AppDw=App 会话 · Dummy/Multi=PopMart 抽签 · Preload=商品库存。
→ 第四个误读：AddToCartMulti 是 PopMart 加多个盒，不是通用多件车。

七个定不了位（Box/GraphQL/PreloadGraphQL/Next/Astro/Svelte/Frontend）—— 描述符扫描截断，缺席≠未知。

数字：套件 2023 → 2036 · 陈旧度 8/832 → 9/916 · 连号定位 0/13 → 6/13 · 被纠正名字 3 → 4。

纪律：判据用错范围时不会报错，它会给出一个语法通顺的错答案。

下一轮：7 个未定位的类（需从别处取完整描述符）；或转优先级 ②（风控对抗）。

## R943 补充 — 13/13 定位；两个来源被否；拼接伪影（套件 2036，红一次后重跑绿）

假设一被否：binding_descriptors.tsv 只装绑定（属性）不装方法 → 七个查不到是问错表。
假设二被否：序号在拼接串里被截断成三位（840 与 864 之间夹 85/87）→ 不可信。

可信的是邻居名 → 七类：PopMart 抽签 / 购物车 API / GraphQL 车 / 框架抓取×2 / 会话 / 网页结账。
而 AddToCartNext 旁边是 Svelte 名 = 拼接伪影 → 邻居名只说明「这一段有抓取方法」，不说明同类。

套件：第一次 metrics 1 失败 → 直接全量 2340/0/2 → 再跑 metrics 2036/0 = 偶发。

数字：定位 6/13 → 13/13 · 陈旧度 9/916 → 9/920。

纪律：一个能回答「相邻」问题的来源，不能当成能回答「这个」问题的来源 —— 而它不会报错。

下一轮：转优先级 ②（风控对抗）或 ③（请求与指纹层）。

## R944 补充 — PerimeterX 补上；假缺席被写了三遍（+7 用例 + 修 3 处，套件 2043）

转优先级 ②：Kasada 40 · DataDome 15 · PerimeterX 5(+_px 4) · Queue-it 13 —— 四个全在。
AntiBotProtocol.cs 覆盖六家但缺 PerimeterX，注释说「no _px cookie」—— 而 _px 有 4 条（_px3/__pxvid/_pxvid/_pxHandler）。

同一个假缺席写了三遍：类注释 + VendorWiringTests 的 Assert.Null + AntiBotProtocolTests 的 Assert.Null。
→ 三处里两处是测例；测例本来防这件事，而它们在这里保存了那件事。

补上：_px3 · __pxvid/_pxvid（刻意不合并）· PerimeterX-Token · PerimeterXHandler · 两条镜像措辞。
cookie 表 4 → 5（不是 7：Queue-it 用路由、TrustDecision 用脚本）。

数字：套件 2036 → 2043 · 陈旧度 9/920 → 10/1044。

纪律：一个听起来像纪律的错误，比一个听起来像错误的错误贵得多。

下一轮：Imperva 是否也有 cookie（同一类未验证断言）；或 ③ 请求与指纹层。

## R945 补充 — Imperva 否定已验证；两个否定的对照（+5 用例，未改产品代码，套件 2048）

五条搜索全 0：Imperva / incap_ses / visid_incap / nlbi_ / _Incapsula_ → Imperva 无 cookie 的否定是真的。

对照：PerimeterX「刻意不填」是假（_px3 在），Imperva 是真。区别不在写法，在有没有一条命令产生它 —— 没有命令的否定，是用事实语法写出来的猜测。

Imperva 只作为反例（AntiBotVendors.Knows = false）→ 不是忘掉的厂商，是不在的厂商。
断言改成「verified rather than asserted」+ 四条前缀点名，让下一个读的人能重跑。

数字：套件 2043 → 2048 · 陈旧度不变 · 带命令的否定 0/2 → 2/2。

纪律：「对」和「可复算」是两件事，只有后者能在改动之后还成立。

下一轮：扫其余否定断言有多少没带命令；或 ③ 请求与指纹层。

## R946 补充 — 否定断言三分类：772 → 118 → 8（+4 用例，未改产品代码，套件 2052）

772 条否定断言，764 条「没有证据」—— 而那个数几乎等于全部，因为它把两类算成一类：
自证（Assert.Null(CookiesFor("NoSuchVendor")) 由测试自己证明）· 需镜像（只有二进制能证）。

窄化到带名字 118 条 —— 绝大多数仍自证。真正需镜像的 8 条（1 settled，7 开）：
Nike 两条路径 · OrderV5/scheels · DataDomeRelay · PopMart CheckResult · JohnLewis Stripe · StoreFlowSteps GetMerchantCode · ScrapeProductBox（R938 已跑）。

按 R944 比例（3 条里 1 条假），那七条里约 2 条是错的 —— 而每条都长着「事实」的样子。

数字：套件 2048 → 2052 · 陈旧度不变 · 需镜像否定 未分 → 8。

纪律：分类不是筛选的礼貌说法，它是把「哪些需要做」和「哪些已经做完」分开的唯一动作。

下一轮：验那 7 条里最可能错的一条（DataDomeRelay 或 Nike 路径）。

## R947 补充 — 8 条验完：3 真 · 3 自证 · 1 撤回（套件 2053）

三条真的：datadome.co n=33（厂商域 api-js/api-sdk）、buy/carts 0、buy/orders 0。而 DataDomeRelay=datadome.cybersole.io/ 是第一方中继，datadome.co 不是其子串（第10字符 o vs y）。

三条自证：PopMart/JohnLewis 的 Assert.Null(EndpointFor(x)) 说的是「在 UnmappedSteps 里」—— 复刻件记账，不是镜像陈述。R946 归错类；那个机制一直在。

一条撤回：「OrderV5 不含 scheels」不存在 —— R946 从扫描样例一行推断，没读测试体。
而「3 条 1 假」是从 n=1 外推（R944 三条里两条是同一错写三遍）。

数字：套件 2052 → 2053 · 陈旧度不变 · 需镜像否定 8（7 开）→ 3 全真。

纪律：读一行扫描输出和读一个测试体，成本差十倍，而错误的代价相同：一个数字被写进文档。

下一轮：核心覆盖表（判据 f）—— 原版站点与风控清单 ↔ Registry.cs 与 Flows/Scripts 逐条对。

## R948 补充 — 判据 (f)：store host unmatched 3 → 0；三个都是支付 host（+6 用例，套件 2059）

vendor 侧 12 host absent 0；store 侧 27 host unmatched 3 = api.braintreegateway.com / api.vipps.no / payments.bigcommerce.com —— 全是支付 host 不是店。

三条路径：Braintree（含商户 id rfbkw27jcwmw2xgp，两条 client_api + assets host）· Vipps（adyen-card-enrollment/{initiate,commit} + checkout-frontend/session + checkout.vipps.no）· BigCommerce（/api/public/v1/orders/payments）。

VippsNo 按措辞记不按地区记（No 可作 Norway 或「否」）。

而 store unmatched 3 → 0 不是补了 flow，是那三个 host 现在在 src 里有名字 —— 工具的判据正是这个。

数字：套件 2053 → 2059 · 陈旧度 10/1044 → 11/1153 · store unmatched 3 → 0。

纪律：一个度量能归零，而它归零的原因可能只是你让被度量的东西出现了。

下一轮：判据 (c) 产物级对照（target\Cybersole.exe ↔ .publish-aot）重算一次；或 ③ 请求与指纹层。

## R949 补充 — 重发布：陈旧度 0，函数数一个没动（套件 2059）

重发布 .publish-aot\Cybersole.Ui.exe 54,652 KB · 陈旧度 11/1153 → 0/0 (current) · 函数数 173,653 未变。

而 173,653 与 R933 同一个数：R933 加了 1,963，这一轮加 0 —— 而中间新增十一文件 1153 行，全是 const 表/小静态类/测例，没有 non-leaf 函数。

换算：const 表/静态类/测例 → 0 个函数；真实逻辑（R933）→ +1,963。→ 剩余 103,467 缺口不能靠加表关掉。

解释十二轮函数数不动：R938→R949 套件 +69 用例，函数数不变 —— 产出是知识不是函数。

数字：套件 2059（未变）· 陈旧度 0/0 · 函数数 173,653 · 比 62.66%。

纪律：判据 (c) 通过的意思是「exe 从当前源码构建」，不是「更接近原版」。

下一轮：写一批真正有 non-leaf 函数的代码（优先 ③ 请求与指纹层，或 ① 未做的 flow 逻辑）。

## R950 补充 — 函数数=可达代码；RedirectPolicy 写了但被裁掉（+29 用例，套件 2088）

写了真逻辑（RedirectPolicy：hop 循环/TooManyRedirects/Retry-After 两种形式/[Throttling] 日志），重发布后函数数仍 173,653。

查产物：TooManyRedirects 不在、BouncyHttpClient 在 → 无调用者的类被 NativeAOT 裁剪器删掉。
→ 函数数量的是**可达代码**；R949 的「表 0 / 逻辑 1,963」被推翻，真相是「不可达 0 / 可达 >0」。

我自己也错过一次：搜 JA3/TlsProfile 都「不在」就判「TLS 层被裁」—— 而 NativeAOT 不把类名写成字面量。

修复中三个真 bug："1.2.3" 被日期解析器接受返回 0（加纯数字点串回落）· 循环多跑一跳 · Hops 多 1。

数字：套件 2059 → 2088 · 陈旧度 0/0 · 函数数 173,653 未变。

纪律：「写了一个类」和「产物里多了一个类」是两件事。

下一轮：把 RedirectPolicy 接进 NetClient.SendAsync（接线而非写作）；或先测已有 HTTP 层多少在产物里。

## R951 补充 — 接线成功；.pdata 数的是未被内联的函数（+5 用例，套件 2093）

接线成功：TooManyRedirects 从「不在产物」变成「在产物」，size 54,652 → 54,655 KB。R950 的「可达才进产物」证实。

而函数数还是 173,653 —— 工具注写着「.pdata excludes inlined and trimmed code」，我接的五个小方法全被内联。

三层：写了（源码有）✅ · 进产物（可达）✅ · 进 .pdata（未被内联）❌ —— 目标指的是第三层。
而 FollowAsync（async，会留状态机）反而没被接：接的是五个同步小方法 + 自己的递归。

数字：套件 2088 → 2093 · 陈旧度 0/0 · 函数数 173,653 未变 · 产物 54,652 → 54,655 KB。

纪律：第三件的判据是编译器的内联决定，不是我的意图。

下一轮：把 FollowAsync 接进去（async 状态机会留 .pdata 条目）；或测内联阈值。

## R952 补充 — 函数数 +128（十四轮首次变动）；四轮因果链收敛（套件 2093）

把 SendAsync 的递归换成 RedirectPolicy.FollowAsync（async → 状态机）：
函数数 173,653 → **173,781（+128）** · 比 62.66% → **62.71%** · 产物 54,655 → 54,674 KB。

而 +128 不是预期数：一个调用点带来 128 个 .pdata 条目（MoveNext · 泛型实例化 · 闭包类 · 内联副本）。

四轮因果链：不可达（R949 错）→ 可达才进产物（R950）→ 还要过内联（R951）→ async 留状态机（R952 对）。

缺口路径：103,467 / 128 ≈ 800 次接线（不是写 800 个方法，是把已有的 async 接进可达路径）。

修了 5 处旧断言（hops+1→limit+1 · Resolve · Clone · PreservesMethod 用法 · TooManyMessage）。

纪律：让数动的不是「更努力地写」，是找到那个数在数什么。

下一轮：统计复刻件有多少 async 方法未接进可达路径（这决定 800 次接线是否可行）。

## R953 补充 — 「800 次接线」估算作废；不可达分两种（+4 用例，套件 2097）

扫描：538 async · 93 个主类型无人引用的文件（26 含 async）。

第一个被查看的文件就打破了估算：Retail2Modules.cs 五个 module 全是已注册 flow 的副本（Casio/JbHiFi/PocketGames/Superswipe/Warhammer）。CreateAll() 返回 IStoreModule[]，module 类正好符合 → 加进去会让 Casio 在 catalog 里出现两次 = 行为错误。

两类必须分开：未接上（接线）vs 重复品（删）。「800 次接线」把两者算成一种。
538 是 async 关键字出现次数，不是未接方法数。

数字：套件 2093 → 2097 · 陈旧度 0/0 · 函数数 173,781（未改产品代码）· 纯重复 module 5。

纪律：一个估算的第一次具体查看，往往不是把它细化，是把它否掉。

下一轮：逐个查 93 个可疑文件里哪些是重复品（先删重复，再谈接线）。

## R954 补充 — 93 个分完：7 重复品 + 5 个我写的死代码（未改产品代码，套件 2097）

对的判据：`XxxModule` 有同名 `XxxFlow` → 重复品 7 个（Fanatics/Casio/EndClothing/Sns/Kith/Nike/Supreme）。
前两次判据错在「我以为 id 只有一种写法」（Id => 撞 catalog 得 1；Store => 收集得 0）。

而剩下 86 个里有五个是我 R920–R925 写的支付类，全部无人引用：
PurpleDot · GlobalECheckout · EshopWorldPanel · DisneyPaymentSheet · VivaPayments
→ 那五轮函数贡献 0；功能前进了，函数数没动。

数字：套件 2097（未变）· 陈旧度 0/0 · 函数数 173,781 · 重复品 7 · 死代码 5。

纪律：判据错在「我以为写法只有一种」时，换成问结构。

下一轮：给一个支付步骤（StoreFlow 的虚步骤里）接上五个支付类之一，测函数增量。

## R955 补充 — 支付派发接上两个网关：+43 函数（套件 2097）

SubmitPaymentAsync 从 `=> NotSupported` 改成按 paymentGateway 派发到 VivaPayments / DisneyPaymentSheet。
函数数 173,781 → **173,824（+43）** · 比 62.71% → **62.73%** · 产物 54,674 → 54,692 KB。

两个样本：redirect +128 · 两个支付网关 +43（≈21 每个）—— 增量不是常数，是 async 带的泛型实例化数。

而这次接线是对的：SubmitPaymentAsync 返回 NotSupported 是真缺口（步骤在、实现在、中间调用不在）。

五次签名错误：post 委托形状 · StepOutcome 无 Retryable() · EshopWorldPanel 无 IsSettled · NotSupported 要 await。全是「我以为签名是什么」而非「读签名」。

纪律：「死代码」是错的词 —— 代码只有可达不可达；不可达需要的不是重写，是一句调用。

下一轮：接另外三个网关（PurpleDot/EshopWorld/GlobalECheckout），或按原版证据核对派发方式。

## R956 补充 — 支付键名改成镜像的；captcha 与网关成对（+4 用例，套件 2101）

R955 的 `paymentGateway` 是我编的。镜像里是 `_paymentGateway`（字段）· `_paymentGatewayName`（绑定属性）· `PaymentGateways`（复数）· `paymentProvider`。
而 `_captchaToken&_paymentGatewayName6_paymentFlexibilityTemplate` 把 token 与网关名串在一起
→ 一次支付提交带的是一个 token 和一个网关名。

改动：PaymentGatewayNameKey="paymentGatewayName" · CaptchaTokenKey="captchaToken" · PaymentGateways(4) 集合。

构建崩溃的次生错误：ilc 0xC0000409 → LNK1136（坏 .obj）→ 删 obj/.../native 4 项重发成功。

数字：套件 2097 → 2101 · 陈旧度 0/0 · 函数数 173,824（未变）· 产物 54,692 KB。

纪律：paymentGateway 与 paymentGatewayName 只差四个字符 —— 而读者不会怀疑。

下一轮：接另外三个网关（PurpleDot/EshopWorld/GlobalECheckout），或查 PaymentGateways 的真实取值。

## R957 补充 — 网关选择改成过滤函数；四个编出来的名字删掉（+14 用例，套件 2115）

R956 修了键名却把 `PaymentGateways = {viva, disney, purpledot, eshopworld}` 留着 —— 那四个名字也是编的。
镜像的机制是：PreferredGateways / blockedGateways 两个设置 + RpcGetPaymentMethods 取 + ParsePaymentMethods 解析 + IsWalletOnly 分类 → 网关不是常量，是这家店返回的东西被两个设置过滤。

改成 ChooseGateway(available, preferred, blocked)：偏好顺序胜出 · 没偏好取第一个未封禁 · 全禁/空 → null。
IsWalletOnly 同时查 applepay 与 apple_pay。

函数数不动（小的同步方法被内联，与 R951 一致）—— 价值在把四轮前那 43 个函数依附的选择逻辑换成了有证据的。

数字：套件 2101 → 2115 · 陈旧度 0/0 · 函数数 173,824 · 产物 54,692 KB。

纪律：错误的下层还有一层，它长得不像错误，因为它是一个数组。

下一轮：反编译 RpcGetPaymentMethods 看返回形状（唯一能定 ParsePaymentMethods 的途径）。

## R958 补充 — 三个 RPC 步骤补上；按名字反编译不成立（+14 用例，套件 2129）

反编译路断：`funcs` 不过滤 · `xrefs` 空（NativeAOT 剥符号，描述符在反射表里）→ 按名字找函数不成立。

描述符给的十步（有序）：169 Login · 170 FindProduct · 171 CheckStock · 172 FetchAddress · 173 CreateAddress · 174 CalculateShipping · 175 ValidateBuyRule · 176 CreateOrder · 177 GetPaymentMethods · 178 SubmitCard。复刻件缺三个：CheckStock / ValidateBuyRule / GetPaymentMethods。

三个都有实体：CheckStock（404/410/非2xx/body 双标志）· ValidateBuyRule（非2xx 不可重试）· GetPaymentMethods（解析→ChooseGateway→写回）+ ParsePaymentMethodNames（五字段不假设 schema）。

构建崩塌：ilc 0xC0000409 → LNK1136（坏 .obj）；删 native 不够，要删整个 obj+bin。
守卫 map.Count 176 → 179（按它自己注释的规矩改数字）。

数字：套件 2115 → 2129 · 陈旧度 0/0 · 函数数 173,824 → **173,866（+42）** · 比 62.75% · 产物 54,692 → 54,706 KB · 分派表 176 → 179。

纪律：残留比崩溃活得更久、更像真错误。

下一轮：10 个 RPC 的参数/返回形状（按名字不可达，需别的路径）；或转优先级 ②（风控对抗）。

## R959 补充 — Queue-it 协议：从字段列表读出判定条件（+18 用例，套件 2147）

证据是一段字段列表：QueueHostMarkers · AcceptedCookiePrefix = `QueueITAccepted-SDFrts345E-V3_`（含哈希）· CookieValiditySeconds · MinRemainingSeconds。

MinRemainingSeconds 是要紧的那个：剩余几秒的通行证比没有更糟（授权的请求会在排队已离开之后被拒）→ 判据是「有效到够跑完吗」。

五条文案一条拼错：`Initiliazing Queue-it` → 照原样保留（改对拼写日志就不再和原版一样）。
一个状态两种意思：200+通行证=通过、200无通行证=还在排队 → Verdict(status, hasPass)。

数字：套件 2129 → 2147 · 陈旧度 1 文件 / 119 行（需重发）· 函数数 173,866（未变）。

纪律：一个线索的价值取决于它离行为有多近。

下一轮：重发消除陈旧度；或查 CookieValiditySeconds 的实际数值与排队轮询间隔。

## R960 补充 — PollQueueAsync 从 `=> Ok()` 变成真判定（+6 用例，套件 2153）

发现 PollQueueAsync 是 `=> Ok()` —— 命中排队页的流程认为自己通过了排队，没看任何东西。

现在：IsQueueHost 前置 · 循环到 deadline · Verdict 分类 · 剩余时间不足则继续等 · **超时 = retryable 失败**。
超时不是成功 —— 把超时说成成功的步骤比报错的步骤难查得多（下游拿到假绿灯）。

设置：queueTimeout(120s) · queuePollMs(2000) · queueMinRemaining(30s) · queuePassSeconds(300) —— 值标 Inference。

数字：套件 2147 → 2153 · 陈旧度 1/119 → **0/0** · 函数数 173,866 → **173,909（+43）** · 比 62.76%。

纪律：`=> Ok()` 读起来像设计不像缺陷 —— 差别只在有没有人覆写它。

下一轮：扫还有多少个 `=> Ok()` 的空壳虚步骤（它们的数量决定下一个批次）。

## R961 补充 — SolveCaptcha 变真实现；空壳 36 → 35（+20 用例，套件 2173）

数出 36 个 `=> Ok()` 空壳虚步骤，全在结账路径（GetCsrf/GetSession/CreateCart/GetCart/SubmitEmail/SubmitShippingMethod/GetShippingRates/SubmitBilling/Login/Register/SolveCaptcha/EnterRaffle/PollRelease/…）。

修了 SolveCaptcha：证据是 api.solvecaptcha.com 的 in.php + res.php 两个 URL 和三个连号状态机。
实现：提交 → taskId → 轮询 → token 落 AntiBotTokens[g-recaptcha-response]。
CAPCHA_NOT_READY = NotReady（正常路径）；空应答 = NotReady（传输失败）；ERROR_* = Failed。

**两次自我更正**：
① PowerShell 手写字节循环报「in.php 不在产物」→ Python 三行 utf16=True 全部在场（搜索工具假阴性）。
② StepActionRunner 靠**反射**建表，名字不出现在源码 → 「必须登记才可达」是错的（R870）。

数字：套件 2153 → 2173 · 陈旧度 0/0 · 函数数 173,909（未变）· 产物 54,706 → 54,720 KB · 空壳 36 → 35。

纪律：检查工具本身也要被检查 —— 尤其当它给出「没有」的时候。

下一轮：从剩 35 个空壳里挑一个证据最全的（GetCsrf 有 38 条字符串，是最多的）。

## R962 补充 — GetCsrf 变真实现；**并发现步骤体不进产物**（+13 用例，套件 2186）

GetCsrfAsync 从 `=> Ok()` 写成真实现（四种 token 形状 + 四个 cookie 名 + 八字下限）。
镜像证据：GetCsrf 在约二十个不同 ordinal 上（d__14/d__22/d__23/d__24/d__26/d__28/d__31/d__32/d__33/d__35/d__39/d__40/d__50…）→ 每家店自己读自己的 token。

**而真正重要的发现**：DLL 里字符串全在，AOT 产物里没有。查十二个标记串 —— 五在七不在。
在产物的都是静态类 const（QueueITAccepted / Initiliazing Queue-it / api.solvecaptcha.com / CAPCHA_NOT_READY / out of stock）；不在的是 StoreFlow 的步骤体串（SubmitPayment: / csrftoken / no csrf token on the page / queue not passed… / captcha not solved… / .queue-it.net / queueMinRemaining）。

→ 所以 R955 +43 / R958 +42 / R960 +43 那三次「接线让步骤体进产物」的归因**未证明**；
  更可能是静态协议类变得可达，但这一层未取证，标 Unknown。

→ **函数数这把尺子量不到「步骤体进产物」这件事**，而我一直拿它当进展指标。

数字：套件 2173 → 2186 · 陈旧度 0/0 · 函数数 173,909（未变）· 产物 54,720 → 54,724 KB · 空壳 35 → 34。

纪律：一个指标连续三轮不动而每轮都有动听的归因 —— 那本身说明归因错了。

下一轮：取证「哪些步骤体进产物、依据什么」（这是把尺子修好的前提）；在此之前不再用函数数当单轮进展判据。

## R963 补充 — **产物保留规则定下来了：有覆写才进产物**（只取证，未改代码，套件 2186）

三组对比：
① `Program.cs → RegisterAll → CreateAll()` 在 `OnFrameworkInitializationCompleted` 里 → 35 个 flow 都构造
   → **被裁的不是构造，是方法体**。
② `BstnFlow.GetCartAsync`（全仓**唯一覆写**）的串 `bstn: cart endpoint unknown` = **True**；
   同类未覆写方法的串 `bstn: order endpoint unknown` = False。
③ 零覆写基类步骤体串全 False（`queueMinRemaining` / `captcha not solved…` / `no csrf token on the page` /
   `SubmitPayment:`）；其静态依赖类 const 全 True（`QueueITAccepted` / `api.solvecaptcha.com` / `out of stock`）。

**规则**：`StoreFlow` 虚方法只在**有覆写**时保留 —— 派发表靠 `MethodInfo.Invoke`，反射在 NativeAOT 下不 root 方法。

**这推翻了八轮主张**：R955/R958/R960 的 +43/+42/+43 都归因成「接线让步骤体进产物」，那是错的；
增量来自静态协议类可达。明确记为更正。

**新策略**：每个 flow 覆写它真正需要的步骤 —— 既必然进产物，也**正是镜像的样子**
（`GetCsrf` 约二十份、`SubmitPayment` 每支付类一份，原版没有共用基类实现）。

数字：套件 2186（未变）· 函数数 173,909（未变）· 陈旧度 0/0 · 空壳 34（未变）。

纪律：**一个指标能在你做错事的时候动，这是它最坏的性质。**

下一轮：按新策略挑一个站，把某个空壳步骤**覆写进具体 flow**（不是基类），并核对它的串进产物。

## R964 补充 — 第一个按新策略写的覆写：+43，而规则收窄（套件 2186）

照 R963 的策略做了第一个真覆写：`BstnFlow.GetCsrfAsync`（拉 www.bstn.com → FindCsrfToken → 回退 csrftoken cookie）。

**产物核对两件事**：
① 覆写确实让方法进产物：173,909 → **173,952（+43）**，比 62.77%，产物 54,741 KB。
② 而方法体里的报错串**没进**：`www.bstn.com` True；`bstn: csrf page ` False；
   `bstn: no csrf token on the landing page` False；`bstn: cart endpoint unknown`（同步覆写）True；
   `bstn: checkout endpoint unknown (Adyen)`（另一覆写）False。

**规则收窄两条**：① 零覆写 → 基类体必被裁；② 有覆写 → 方法进产物，但体内字符串**按需保留**，判据 Unknown。
**→ 覆写是必要条件不是充分条件；串不在**不能**证明不在（§2.7b，这次踩在产物上）。**

修了一个钉住假成功的测例：`RunnerExecutesAnActionAndRecordsEveryStep` 的 fixture 从 `{}` 换成带 token 的页面
（行为变了改夹具，不是形状变了改数字）。

数字：套件 2186 / 0 / 0 · 陈旧度 0/0 · 函数数 173,952 · 比 62.77% · GetCsrf 覆写数 0 → 1。

纪律：串不在不能证明不在。

下一轮：给第二个站写覆写（挑一个有真实端点证据的站），并核对 +43 这个量是否稳定。

## R965 补充 — **34 个空壳全部有覆写**；R962/R963 的覆写数全错（正则漏 `async`）（套件 2186）

旧正则 `override\s+Task<StepOutcome>\s+<Step>Async` 漏掉 `async` 关键字 → 把大量覆写判成「没有」。
新正则 `override\s+(?:async\s+)?Task<StepOutcome>\s+<Step>Async` 下逐个数：
`ScrapeVariantAvailability` 13 · `GetCsrf` 4 · 五个 3 · 五个 2 · 其余约 20 个 1 · **零覆写 0 个**。

**倒掉**：R962「35 个空壳零覆写」；R963「零覆写→必被裁」的前提 + 「BstnFlow.GetCartAsync 唯一覆写」。
**仍成立**：R964「覆写让方法进产物（+43）」，直接观测。

**而真正的问题浮出来**：既然 34 个都有覆写，为什么只有 173,952 / 277,120（62.77%）？
→ 缺口**不在「有没有实现」上**，而我一直拿「写实现」当进展，实现早就有了。
要查：① 那 34 个覆写是否都进产物；② 62.77% 缺口在哪一层。

数字：套件 2186（未变）· 函数数 173,952（未变）· 陈旧度 0/0 · 零覆写空壳 34 → 0。

纪律：第二十二次「假设太窄」，这次漏的两个字是 `async`。

下一轮：查①——逐个核对 34 个覆写的独有串是否在产物里。

## R966 补充 — **179 个步骤名 0 个在产物；AOT 里派发表是空的**（只取证，套件 2186）

换了个不依赖 body 串的问法：查步骤**方法名**。理由：`StepActionRunner.Build()` 走 `GetMethods()`，
要让反射返回东西，裁剪工具必须保留 `StoreFlow` 的方法元数据（名字在内）。

结果：**179 个步骤 → 方法名在产物里 0 个**；阴性对照 `NoSuchStepNameAtAll` / `ZzzQqqWww` 也不在（对照正确）。

→ **AOT 产物里 `StepActionRunner.Invokers` 是空字典** → `Knows()` 恒 false → 按名字跑步骤在产物里跑不起来。

→ 62.77% 缺口的主因候选：**不是「没写」（R965：34 个全有覆写），是派发在 AOT 下失效，
   只经它可达的代码全被裁掉。**

而 `*StepMap` 是编译期字面量、不是反射 —— 哪条路活的未取证，标 Unknown。

数字：套件 2186（未变）· 函数数 173,952（未变）· 陈旧度 0/0 · 产物步骤名 0/179。

纪律：找出这件事的不是新工具，是换一个不依赖字符串的问法。

下一轮：让派发**不依赖反射**（把 Invokers 改成编译期字面量表，或给 StoreFlow 加 [DynamicallyAccessedMembers]），然后看函数数是否跳。

## R967 补充 — **步骤名 179/179 在场（UTF-8）；R966 倒掉；属性无效果**（套件 2186）

① 给 `StoreFlow` 加 `[DynamicallyAccessedMembers(PublicMethods)]`：函数数 173,952 **不变**，产物 +4 KB。

② **而检查本身是坏的**：补阳性对照发现 —— 反射元数据（类型名/方法名）存 **UTF-8**，
   字符串字面量存 **UTF-16**。`StoreFlow`/`StepActionRunner`/`GetCsrfAsync` 只 UTF-8；
   `'bstn: cart endpoint unknown'` 只 UTF-16；`Main`/`Initialize` 两编码都在；`NoSuchTypeAtAll` 都不在。

→ 用 UTF-8 重查 179 个步骤名：**179 / 179 全在**（UTF-16 下 0）。

→ **R966 倒掉**：`Invokers` 不是空的，「派发在 AOT 下失效」是假的。假因是我搜了 UTF-16。

→ 而**阴性对照通过是最危险的地方**：它只证明「搜不到不存在的东西」，不证明「搜得到存在的东西」。
   两者在编码不同时会分开，于是「全都不在」被读成结论而非警报。

数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 产物 54,728 KB · 步骤名 UTF-8 179/179。

纪律：检查要两向对照 —— 一个已知在、一个已知不在。

下一轮：用 UTF-16 重新核对那 34 个覆写的 body 串（这次编码是对的），然后找 62.77% 缺口的新候选。

## R968 补充 — 属性无影响（第二次确认）；body 串核对**原理上只能读一半**（套件 2186）

加属性后：`pdata-replica` 173,952 不变；名字 179/179 在（UTF-8）；
body 串抽样 5 个：`bstn: cart endpoint unknown` **True**，其余 4 个 False。

**两条并存**：方法元数据在 → 反射表能建；方法体大部分被裁 → `MethodInfo` 存在、`Invoke` 能调、
而**被调到的体可能已经不在了**。

**而核对方法到头了**：`bstn: cart endpoint unknown` 在、`bstn: checkout endpoint unknown (Adyen)` 不在 ——
同类、同形状、都是覆写。而 R964 已证字符串会被拆开存 → **「不在」这一向在原理上不可用**。
→ 这张表**只能读正向**：在 → 在；不在 → 什么都不能说。

**下一轮具体目标**：把两边 `.pdata` 按**地址段**切开，做出**缺口分布**（工具还没有，本轮立此目标）。
集中在某几段 → 答案在那几段；均匀分布 → 答案在别处。

数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 产物 54,728 KB · 名字 179/179 · body 1/5。

纪律：方向对了也不够 —— 被查的东西本身会被拆开存。

下一轮：写 `tools/pdata_sections.py`，把两边 .pdata 按地址段统计，给出缺口分布。

## R969 补充 — **缺口分布：复刻件代码在 0x1C00000 结束**（+1 工具，套件 2186）

写了 `tools/pdata_sections.py`（复用 func_count.py 的 PE 解析），两边 .pdata 按 1 MiB 分桶：

**0x0..0x1B00000：复刻件不缺甚至更多（1.5-4.9 倍）** —— Avalonia 与不同 BCL 的体量；
**0x1C00000..0x3100000：复刻件 0，原版约 10 万函数。**

→ 103,168 的缺口几乎全部就是那一段。**缺口不是「某类函数缺失」，是「复刻件的 .text 在那之后就没了」。**
→ 复刻件 .text ≈ 28 MB，原版 ≈ 49 MB，差 21 MB 装 10 万函数 → **整体体量差 1.75 倍**。

→ **R966 的「派发失效」候选被形状否掉**：那会均匀砍，不会从某地址起归零。
   候选原因被**形状**否掉比被另一个候选否掉可靠。

工具不能说的：两镜像布局独立，同桶数字不代表同一段代码 —— 说的是**密度**不是**身份**。

数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 复刻件 .text 上界 0x1C00000 · 原版 0x3100000。

纪律：一个上午在猜「为什么少」，47 行桶统计直接给出「少在哪」，而它把候选原因全换了。

下一轮：查原版 0x1C00000 以上的 10 万个函数**是什么**（用 IDA 按地址段采样函数名/字符串引用），
判定那是 BCL/Avalonia 体量差还是真缺口。

## R970 补充 — **段表：复刻件有两个可执行段；R969 框架修正**（+1 工具，套件 2186）

写了 `tools/pe_sections.py` 打段表，结果推翻了 R969 的框架：

**原版**：`.text` 0x1000→0x314DD68 = **51,695,104 B（49.3 MB）**，单一段。
**复刻件**：`.text` 0x1000→0xFD508 = **1,033,728 B（1.0 MB）** +
             `.managed` 0xFE000→0x1B817E8 = **27,801,600 B（26.5 MB）** ← 第二个可执行段。

→ **R969「复刻件的 .text 在 0x1C00000 结束」现象对、原因错**：0x1C00000 是 `.managed` 的结束，不是 .text 的。

→ 真正的数：代码体量比 27.5/49.3 = **55.8%**，而函数数比 **62.77%**。
   差 7 个百分点 → 复刻件函数平均更小（或原版更多大函数）—— 未取证是哪个。

→ 若不打段表，那个错解释会进 BACKLOG，下个会话会去 `.text` 里找 27 MB —— 而那里永远只有 1 MB。

数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 原版可执行 49.3 MB · 复刻件 27.5 MB · 体量比 55.8%。

纪律：观察对、解释错，比观察错更危险 —— 解释会被下一个会话当成前提。

下一轮：查那 7 个百分点差的成因 —— 统计两边 .pdata 里每个函数的 (End-Begin) 大小分布。

## R971 补充 — **函数大小分布：均值原版大 12.5%，中位数复刻件大 18%**（+1 模式，套件 2186）

`pdata_sections.py --sizes`（同一个 PE 走查，多一种汇总）：

| | 原版 | 复刻件 |
|---|---|---|
| 函数数 | 277,094 | 173,912 |
| 总字节 | 48,723,539 | 27,158,626 |
| 均值 | **175.8** | 156.2 |
| **中位数** | **73** | **86** |
| p99 | 1658 | 1361 |
| **max** | **687,318** | **74,836** |
| ≤64B | **46.3%** | 39.2% |
| 65..512B | 48.0% | **56.2%** |
| >512B | **5.7%** | 4.6% |

→ **「原版平均更大」是因为尾部不是典型**：原版中位数更小（73 vs 86），而均值有极少数巨函数拉动（max 687 KB）。
→ 那 7 个百分点是**编译器与代码形状**的差别，不是「少了功能」。

数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0。

纪律：**这一轮没抓到我自己的错，是中位数抓到了均值的错。**只有一个均值时我会说「复刻件函数更小」，
加上中位数那句话就反了 —— 两个数都对，它们描述分布的不同部位。

下一轮：查那 687 KB 的函数是什么（IDA 按地址段找 0x?? 起、长 687318 的那个）。

## R972 补充 — **均值差拆解：4096 B 以上那档贡献 83%；R971 的粗算错**（+1 工具，套件 2186）

`tools/pdata_decompose.py` 拆解 19.67 B 的均值差（总和精确匹配）：

| 档（B） | 原版占比 | 复刻件占比 | 贡献 |
|---|---|---|---|
| 0..32 | 27.6% | 21.1% | +1.01 B |
| 32..64 | 18.7% | 18.2% | +0.20 B |
| **64..128** | 23.6% | 30.6% | **−7.46 B** |
| **128..256** | 16.7% | 18.3% | **−3.37 B** |
| 256..512 | 7.8% | 7.3% | +1.00 B |
| 512..1024 | 3.6% | 2.9% | +4.84 B |
| **1024..4096** | 1.9% | 1.5% | **+7.04 B** |
| **4096..1MB** | 0.2%（671） | 0.2%（266） | **+16.40 B（83%）** |
| total | | | **+19.67 B** |

→ **R971「687 KB 函数只解释 2.5 B，大部分差来自极小函数比例」是错的**：
   4096+ 那档 671 个合起来解释 **83%**；0..64 两档只 +1.21 B，而 64..256 是 **−10.83 B**。

→ 而这一轮自己也撞了「说一套做一套」：文件头写「third mode rather than another script」然后写成了独立脚本。
   已改正并写出真实理由（固定档边界 vs 统一桶宽，两套不可互换的参数）。

数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 拆解总和 +19.67 B。

纪律：**心算的数字比没有数字更危险 —— 它看起来已经被算过了。**

下一轮：查那 671 个大函数（原版 4096..1MB 档）是什么 —— 那占均值差 83%。

## R973 补充 — **4096+ 的 671 个函数：均值差 83%、字节 15.8%、函数数 0.24%、反编译失败**（套件 2186）

671 个（4096 B 以上）合计 7,676,312 B = 原版可执行段的 **15.8%**；最大 `0x14117C4E0` = 687,318 B。

**对三个目标条款的贡献**：① 函数数量对等 → **0.24%**；② 功能相等 → 需反编译，**失败**；③ 效率 → 未测。
（而它们占**均值差 83%** 和**字节 15.8%** —— 两个都**不是目标**。）

→ `ida.py dec 0x14117C4E0` → `Decompilation failed`（687 KB 太大）；
  `xrefs` 显示被 `sub_1412241C0`（227 KB）引用 → 大函数互相调用的簇。

**处置：写进 Unknown，不占下一轮。**形状：671 个 / 15.8% 字节 / 函数数 0.24% / 反编译失败。

数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0。

纪律：**一个指标被解释清楚，不等于那个解释值得追。**

下一轮：回到函数数本身 —— 173,952 / 277,120 的差在哪一类函数（用 IDA 的 af 清单按 ordinal/类分组）。

## R974 补充 — **判据 (a) 分类结案：类型级 0；16 缺失 = 6 核心 / 9 UI / 1 未读**（套件 2186）

读 `docs/METRICS.md`（唯一数字源）判据 (a) 四个数：
**real gap 4**（全 `Ui.*`）· missing 16（12 噪声）· **类型级 scope misses 0** · **类型缺失 16**。

**4 条 real gap 全在 UI 层**：`Ui.Localization.LocalizeFormatExtension`(Value2) · `LocalizeSwitchExtension`(Condition) · `Ui.Views.Auth.AuthWindow`(Logout) · `LicenseControl`(Authenticate)
→ YG 明令 ui 不急 → 对核心优先级**零**，该**分类结案**。

**16 个缺失分三类**：
- **核心 6**：`Global.Settings`(34) · `CloudflareSolvers.CloudflareSolver`(9) · `Services.ImapProvider`(4) ·
  `Models.Concurrency`(3) · `SmartActions.ActionConfig`(2) · `Helpers.ObservableDictionary`2`(1)
- **UI 9**：`Ui.Localization.*` 四个 + `AccountsCreatorView` + `AuthWindow` + 三个同前缀
- **未读 1**：输出截断

→ 判据 a 第一半（类型级缺口 → 0）**已满足**；第二半 6 核心**未开工**（有成员清单，补起来确定）。
→ 而一个未核的可能：`Global.Settings` 34 成员，复刻件配置类存在只是**改名** → 若成立属「命名可不同」，不算缺口。

数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0。

纪律：按优先级切开一个数字，比反复报那个数字有用。

下一轮：核那 6 个核心类型里有几个只是改名（`where_is.py` 逐个查）。

## R975 补充 — **6 个核心缺失中 5 个只是改名；判据 a 类型缺失真实剩余 2**（套件 2186）

逐条核对：
- `Global.Settings`(34) → **`GlobalSettings.cs`**，抽样 8/8 全在
- `CloudflareSolvers.CloudflareSolver`(9) → 散在 `Drivers.cs`/`CaptchaSolverService.cs`，4/4 全在
- `Services.ImapProvider`(4) → **`ImapMailProvider.cs`**
- `Models.Concurrency`(3) → **`ConcurrencyLimit.cs`**
- `SmartActions.ActionConfig`(2) → **`SmartActions.cs`**
- `Helpers.ObservableDictionary`2`(1) → **未见**（`Count` 通用，不算证据）→ Unknown

→ **5 个是改名 → 属目标里写明的「命名可不同」→ 不算缺口，划掉。**
→ 判据 a「类型缺失」真实剩余：**1 核心待判 + 1 未读 = 2**（不是 16）。
→ 9 个 UI（YG 说不急）+ 1 未读 + 1 核心待判 = 11 合计。

数字：套件 2186 · 函数数 173,952 · 陈旧度 0/0 · 核心缺失 6 → 1 · 类型缺失 16 → 11。

纪律：**检查工具按名字判存在，而名字可不同是目标里的自由度 —— 那个洞装着 5 个假缺口。**

下一轮：查 `ObservableDictionary`2` 是否 BCL 现成类型（查 .NET 8 BCL 清单）+ 补读第 16 个。

## R976 补充 — **核心类型缺失 1 → 0：写了 ObservableDictionary`2**（+10 用例，套件 2196）

写了 `src/Cybersole.Core/Helpers/ObservableDictionary.cs`：IDictionary + IReadOnlyDictionary +
INotifyCollectionChanged + INotifyPropertyChanged。替换已有键只发 Item[]；移除携带旧对；重复 Add 先抛后不通知；
AddRange 只对新增键通知；Clear 空字典不发通知。

**两个守卫立刻红了，都按规矩处理**：
① `UnsubscribedEventsTests` → 白名单登记 CollectionChanged/PropertyChanged（先例是 CanExecuteChanged，契约事件）
② `BindScopeGuardTests` → `KnownUnseenTypes` 5 → 6（第二个双泛型类型，DECL 只匹配无类型参数的声明）

→ 函数数 173,952 **不变**：无人实例化它 → 被裁（R963/R967 规则）。所以是**尚未接线**，不是缺口。

数字：套件 2186 → 2196 · 陈旧度 0/0 · 函数数 173,952 · 类型缺失 16 → **15** · 核心类型缺失 1 → **0**。

纪律：守卫红了不是要绕过 —— 它要求一个理由，而理由给得出才是对的。

下一轮：剩余 15 个类型缺失 = 10 UI + 5 改名（已核）。所以判据 a 的「类型缺失」实质已结案，
下一步转回函数数（173,952 / 277,120）—— 用 rea 的 compare_functions 或 IDA 的类型清单对照。

## R977 补充 — **度量项 12 → 14；抓到单位 bug；修正 R969 的「约 10 万」为 156,590**（套件 2196）

判据 (c) 把两个工具注册成第 13、14 项度量（之前那些数是我手工量的、从散文里引用的）：
- **可执行段体量**（`pe_sections.py`）：`section-mass-ratio: 55.78%`（28,835,328 / 51,695,104）
- **函数分布**（`pdata_sections.py`）：`pdata-above-0x1C00000-original: 156,590` / `-replica: 0`

**抓到单位 bug**：第一版 `if k >= 0x1C00000`，而 `k` 是桶**索引** 28，不是字节地址 → 两侧都报 0。
它没抛异常，只是很确定地错了，而 0 正好是我以为的答案。修法 `k * bucket >= boundary`。

**修正 R969**：「0x1C00000 以上约 10 万」→ 真实 **156,590**。而缺口是反向运动的净额：
| | 原版 | 复刻件 | 差 |
|---|---|---|---|
| 0x1C00000 以下 | 120,530 | **173,952** | **+53,422** |
| 0x1C00000 以上 | **156,590** | 0 | **−156,590** |
| 合计 | 277,120 | 173,952 | **−103,168** |

→ 复刻件在分界线**以下**比原版多 44%。103,168 是两个大反向运动抵消后的净值。
→ 而地址分桶**定位不了**缺口（布局独立）。

数字：套件 2196 · 陈旧度 0/0 · 函数数 173,952 · 类型缺失 15 · 度量项 14。

纪律：一个单位 bug 报出的 0 恰好是我以为的答案 —— 是原版那一侧的 156,590 让那个 0 显得可疑。

下一轮：转到判据 (d) —— claim 表每条要有 authority+命令+gap_reason。

## R978 补充 — **判据 (d) 的检查从诞生起只审 5/22 行，而报 PASS；已修 +2 守卫**（套件 2198）

`docs/PARITY_CLAIMS.md` 是**五张表**（一节一张，各有表头）。`analysis/check_claims.py`（R811）
找到第一个表头后遇到第一个非表格行就停 → 只审 C1–C5 五行 → 报 PASS。
**6 个表头在 R811 当天就都在 → 不是回归，是从诞生起就这样。**

修法：改成遍历每一张表。修好之后 `claim rows: 22`，仍 PASS → **判据 (d) 确实满足，第一次被真正验证**。

新守卫 `ClaimsCoverageTests`（2 用例）：文档多表 + 脚本行数 == 测试独立计数。

另一条：`DELIVERY_STATUS.md` 判据 d 引用的 `claims parsed: 22` 来自 `audit_claims.py` 旧版本（`35e8721`），
现行版本打 `inconsistencies found: 0` → **命令能跑 ≠ 命令能复算出被引用的那句**。记 Unknown。

而我又撞了「先写后查」：写了 `audit_claims.py --structure` 却做成独立脚本（R972 同一次），已删除并改为修已有的。

数字：套件 2198 · 陈旧度 0/0 · 函数数 173,952 · claim 行 5 → 22 · 守卫 2。

纪律：覆盖 23% 的检查报 PASS，比没有检查更坏 —— 它的结论会被引用。

下一轮：判据 (e) —— 套件绿、变异测试全 fired。先跑 mutation-check.py 看现状。

## R979 补充 — **变异 33/36（1 装饰性 + 2 跳过）→ 判据 (e) 不满足；HANDOFF 头部已刷新**（套件 2200）

`python tools/mutation-check.py` 实测 36 条：**33 fired / 1 装饰性 / 2 跳过**，restored GREEN。
- **装饰性**：round 606 — 度量索引指向不存在的节，守卫 `EverySectionTheMetricIndexReferencesExists` 没红
- **跳过**：round 164 — `PARITY.md` 模块数，锚点 `**62 个注册模块` 已不存在
- **跳过**：round 623 — copy audit detail 循环，锚点那段循环已不存在

→ **「跳过」比「装饰性」更隐蔽：那条变异根本没跑，不红不绿，而套件照样绿。**

而 `HANDOFF.md` 头部停在 **R826**（落后 152 轮），写着套件 1766、类型缺失 17、形状 78，
**并且把「`check_claims.py`：5 行」写成判据 (d) 满足的证据 —— 那正是 R978 修掉的缺陷**。
→ 已刷新为指针 + 复算命令；历史 1,845 行原样保留。

顺带两条：
① `metrics_report.py` 的 `VERDICT_BY_FILE` 从 cwd 相对改成锚 `ROOT`（从仓库根跑时回退静默失效）
② `DEVIATIONS.md` 的「1,637 条」改成指针（`descriptor entries` 现值 951）
→ 修后活文档硬编码命中 **0 / 0 / 0 / 0**。

新守卫 `HandoffHeadPointerTests`（2 用例）。

数字：套件 2200 · 陈旧度 0/0 · 函数数 173,952 · 变异 33/36 · 活文档硬编码 0。

纪律：一条变异没跑就不红不绿，而整套仍然绿 ——「全 fired」只有报了分母的来源敢说。

下一轮：查 round 606 的守卫为何不红，以及 164 / 623 的锚点该换成什么。

## R980 补充 — **变异 35 fired / 1 装饰性（对象为空）/ 0 跳过**（套件 2200）

R979 的三处，两处是锚点过期，一处根本不可能红：
- **round 606**：`§99` 现在**是真的标题**（BLOCKERS.md 有 403 节）→ 变异不再改变任何东西。已改 `§9999`
- **round 164**：`find: "**62 个注册模块"` 而文档是 `**65` → 已给 `mutation-check.py` 加**正则锚点**
  （`find_re`/`replace_re`），改成 `(\*\*)(\d+)( 个注册模块)` → `\g<1>9\g<2>\g<3>`，永不宣言过期
- **round 623**：文案缺口现在是 **0** → 摘要 0、明细 0 → 两侧任何改动仍 0==0 →
  **守卫在原理上无法被触发**。**这不是「装饰性」，是对象为空。不改守卫，记待办。**

结果：36 条 → **fired 35 / 装饰性 1 / 跳过 0**（原 33/1/2），restored GREEN。

数字：套件 2200 · 陈旧度 0/0 · 函数数 173,952。

纪律：**「装饰性」一个词盖了两种情形 —— 守卫没用，和守卫的对象是空的。**
工具只有一个词，差点让我把 623 也当「守卫坏了」去改，那会把一条正确的守卫改坏。

下一轮：给 round 623 的守卫造一个非空情形（fixture 或让工具吃人造缺口）；然后把变异度量进 METRICS。

## R981 补充 — **变异 36 / 36 fired，0 装饰性，0 跳过 → 判据 (e) 第二句成立**（套件 2200）

R980 说 round 623 的守卫「对象为空」。这一轮的办法不是改守卫，是**让工具能指向别处**：
① `copy_audit_report.py` 加 `--pool` / `--src` / `--out`（默认 = 原常量）
② 守卫跑两次 —— 真实树（摘要 0 / 明细 0）+ fixture（键名在源码、值不在 → 正确代码 0/0，变异代码 0/1 → 红）

**手工验过它真的红**（应用变异 → `[FAIL] DetailRowsMatchTheSummaryTotal` → 还原 → 通过）。

全量：**running 36 of 36 → fired 36 / decorative 0 / skipped 0 · restored GREEN**。

→ 判据 (e) 第二句现在成立，而成立方式不是把守卫改严，是**给守卫一个能说话的对象**。

三轮（R978/R979-980/R981）修的是同一件东西 —— 检查沉默有三种原因：
| 原因 | 征兆 | 修法 |
|---|---|---|
| 只审了一部分 | `claim rows: 5` | 扩范围 |
| 锚点/前提过期 | `SKIPPED` / `DECORATIVE` | 换锚点 |
| 对象是空的 | `DECORATIVE` 而代码没变 | 造对象 |

数字：变异 36/36 · 套件 2200 · 陈旧度 0/0 · 函数数 173,952。

纪律：先看代码有没有变。变了还绿 → 装饰性；没变 → 没有对象。

下一轮：把变异度量（fired / decorative / skipped）注册进 METRICS —— 判据 (e) 需要一个能复算的数。

## R982 补充 — **变异度量进 METRICS：36/36/0/0，staleness 0**（+1 度量 +1 工具，套件 2200）

判据 (e) 第二句的 `36 / 36` 之前只活在散文里。一次完整变异约 12 分钟，塞进 `metrics_report.py` 会让它不被跑，
所以拆成两半：`mutation-check.py` 写 `analysis/MUTATION_RESULT.json`（带 `ran_at`）→
`tools/mutation_report.py` 读它。与 `artifact_freshness.py` 同一安排。

METRICS 五行：`mutation-fit: total 36 / fired 36 / decorative 0 / skipped 0 / staleness 0`。

**staleness 字段改了两版**：① 把 `docs/**` 算进来 → 任何文档编辑都让它变正 → 每轮都响 → 没人看；
③ 把自己算进来 → 改一次报告器就自我失效 → 按名字排除。两方向都验过（排除后 0 / 造源码文件 → 0:03:26 / 删掉 → 0）。

数字：度量项 15 · 变异 36/36 · staleness 0 · 套件 2200 · 产物陈旧度 0/0。

纪律：**一个每轮都响的告警，和不存在是一样的。**

下一轮：回到核心 —— 判据 (f) 的镜像→复刻件方向（`myshopify` 主机池 → 复刻差别名），或函数数那一刀按内容分。

## R983 补充 — **`HandleBlock` 只在一个类型里（1/4）；复刻件零；封锁判断分散 30 处**（套件 2200）

原版 `ida.py str HandleBlock` 第一条：`"<SetRequest>d__53$<HandleBlock>d__54*<HandleResponse>d__55`
→ async 状态机，与两个兄弟编号相邻。

而 `analysis/flows.txt`（按 utf-16-le 解码）四组计数：**HandleResponse 4 · SetRequest 2 · HandleBlock 1**。
| 组 | SetRequest | HandleBlock |
|---|---|---|
| d__53/54/55 | ✓ | **✓** |
| d__26/27/28 | ✓ | **✗** |
| Kasada d__46/47/48 | ✗ | ✗ |

→ **第 2 组是校准项：两兄弟都在、它不在 → 它不是这对兄弟的必然伴生。**

复刻件：`SetRequest` 在 `StepAction.cs`、`HandleResponse` 在 `BouncyHttpClient.cs`、**`HandleBlock` 零**，
而 `Blocked` 出现 **30 次**（`StoreFlow.cs` 11 · `HbxFlow.cs` 6 · 其余各 flow）。
→ 能力在，**形状不同（分散 vs 集中）**。而形状不同会不会导致行为不同，取决于 30 处是否一致 —— **未核，Unknown**。

→ 顺带修正 HANDOFF：「与优先级 ② 直接相关」应改为更窄的「某一个类型的私有步骤」。

数字：套件 2200（未改代码）· 陈旧度 0/0 · 函数数 173,952 · HandleBlock 原版类型数 1/4。

纪律：**「相邻」要有校准项，否则会被读成「伴生」。**

下一轮：核那 30 处封锁判断是否彼此一致 —— 那是「形状不同会不会导致行为不同」的关键。

## R984 补充 — **23 处 `!res.IsSuccess` → Blocked（404/500 都算封锁）；+3 守卫**（套件 2203）

29 处 `Blocked`，把「Blocked 行」上溯最近的 `if`：**23 处都是 `if (!res.IsSuccess)`**。
而 `IsSuccess => StatusCode is >= 200 and < 400` → **404 与 500 都是 Blocked**。

→ 与集中的 `StoreFlowRunner`（只 `401`/`429`/`!anti.Ok` 判 Blocked）**矛盾，错的是数量多的那半**。
→ 一个把「下架」报成「被封」的监控，比什么都不报更坏 —— 它把真的 drop 藏在「我被封了」的故事后面。
→ 与 HANDOFF 未结案项 #2（长度守卫用 `body.Length` 判缺货）**同一类**：用与目标现象无关的量去决定它，都是误报方向。

**这一轮加守卫不改那 23 处**：改它要逐站决定「404 对该站意味着什么」，需要镜像侧证据，未取到。
`BlockIsNotTheAbsenceOfSuccessTests`（3 用例）：`IsSuccess` 定义不变 · 混淆点 ≤ 23 · 混淆点 == 23。

数字：套件 2203 · 陈旧度 0/0 · 函数数 173,952 · 混淆点 23。

纪律：那 30 处的**共同点**不是一个共享判据，而是一行**复制了 23 遍的代码**。

下一轮：取镜像侧证据判「404 各站应是什么」，或先把 401/403/429 收进一个 `IsBlocked` 分类器并让 23 处改用它。

## R985 补充 — **状态码分类字符串层不可得；`HISTORY.md` 那条是复刻件历史不是原版证据**（套件 2203）

① `ida.py str 403/429/401` 全是噪声（GUID、`Build_403`、`10403`、Metalama 公钥、版本号）。
原因：状态码分类是**整数比较**，不产生字符串 → 字符串路线**原理上**不可得。要它得走代码，而已失败两次。

② **自我更正**：`HISTORY.md:1488`「状态码分类（401/403 可重试 vs 422 不可）」属于「6.73 空桩填实（R12）」一节，
是**复刻件自己的实现描述**，不是原版观察。拿它推原版 = 循环论证（§2.2 同类）。

③ 顺手暴露第三处矛盾：`StoreFlowRunner.cs:242` 把 `401` 判 `Blocked`（终止），而 `HISTORY.md` 说 401 可重试。
401 = 凭据过期，正是 `RefreshSession` 的理由 → 判终止等于提前关掉刷新会话。**未改**（同样缺原版证据）。

④ 结论：`HandleBlock` 与「状态码分类」**共用一个阻塞** —— 在原版里名字能不能落到代码上。
   两条不该再各占一轮。

数字：套件 2203（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 混淆点 23（守卫钉着）。

纪律：**「读起来像在描述原版」靠的是语气；看主语是谁才靠得住。**

下一轮：换一条不靠名字定位的核心工作 —— 判据 (f) 的镜像→复刻件方向，或 flow 级别的行为证据。

## R986 补充 — **185 覆写中 180 有实质工作；占位 5 个 = Bstn 下单链 4 + Shopify 有意 1**（+1 工具 +2 守卫，套件 2205）

新工具 `tools/flow_work_audit.py`：按 **flow 文件**分类每个覆写体（`hollow_audit.py` 是按步骤跨站数）。

**分类器第一版错了**：只把 `await`/`Http`/会话访问算工作，把 `=> OpenCheckoutAsync(...)` 判成占位（5 个假阳性）。
那正是 **R824 记过的形状：「委派是无接收者调用，`\w+\.名字` 一定漏」**。修好：**180 真 / 5 占位**。

| flow | 覆写 | 真 | 占位 |
|---|---|---|---|
| Magento 33 · PopMart 23 · Footsites 17 · Nike 15 · Scheels 12 · Farfetch/Hbx/Hybris 各 10 · Demandware 9 · Goat 8 | | 全真 | 0 |
| Shopify | 18 | 17 | **1** |
| **Bstn** | 9 | 5 | **4** |
| **合计** | **185** | **180（97.3%）** | **5** |

**5 个占位 = Bstn 的 AddToCart/GetCart/GetCheckout/SubmitOrder（消息都是 `endpoint unknown`）+ Shopify 的 GetCsrf（R823 有意不编造）。**

→ 优先级 ① 的剩余 = **一个站的四个端点**，不是「35 个站」。

守卫 `FlowWorkAuditTests`（2 用例）：占位 ≤ 5；有 ≥2 占位的 flow 必须写明 `endpoint unknown`。

数字：套件 2205 · 陈旧度 0/0 · 函数数 173,952 · 覆写 185/真 180/占位 5。

纪律：**「无接收者的调用看不见」—— 搜索时是它，分类时还是它。**

下一轮：取 Bstn 的三个端点（cart / checkout / order），把那一站的四个占位补成真实现。

## R987 补充 — **`Bstn` 不在原版里 → R986 归属错误；判据 (f) 仍 27/27**（套件 2205，未改代码）

`ida.py str bstn` / `api/bstn` / `bstn.com` **各 0 命中**（查数据库本身，反向可用），
而 `core_coverage` 的 27 个 store host 里也没有 bstn（goat/hbx/popmart/scheels 都在）。
→ **`BstnFlow` 是复刻件自己加的站**；R986 说的「优先级 ① 剩余 = Bstn 四个端点」**归属错误**。

**校准项（不能推广）**：Hybris / PoqApp 名字也是 0 命中，但 `hypecommerce` / `poqapp` host 都在
→ **名字缺失证明不了平台缺失**（§2.7b）。

→ 判据 (f) 不变：**27/27 matched，0 unmatched**；Bstn 从未被算入。

**需要 YG 判断的一条**：`BstnFlow` 删掉（严格 1:1）还是保留并标为超出原版的添加。
两个方向都自洽，「1:1」未被明确到「不许有额外站」—— 我不自己决定。

数字：套件 2205（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 覆写 185/真 180/占位 5 · 不在原版的站点 flow 1。

纪律：**27 个 host 与 35 个 flow 类型一直是两个数，我把它们读成了一个。**

下一轮：按 R986 的守卫继续 —— 或者核其余 34 个 flow 与 27 个 host 的对应关系（35 vs 27 的差是 8）。

## R988 补充 — **store 分母 27 → 15：十二个支付网关被算成「店」**（套件 2205）

`core_coverage.py` 用 `VENDOR_HINTS` 手写名单分 store/vendor，**名单之外默认 store**。
而名单只有风控厂商 + paypal/stripe/adyen/paynamics，于是十二个落进 store 桶：
braintreegateway · sibspayments · vipps · midtrans · gpayments · mollie · cybersource ·
bigcommerce · touchtechpayments · airwallex · klaviyo · ibm。

补齐之后：**store 27 → 15，vendor 12 → 24，store matched 15 / unmatched 0**。
→ 覆盖率不变，**分母变诚实**。判据 (f) 要的是「原版站点清单」，不是「主机清单」。

`riotgames` 特意没补：`authenticate.riotgames.com` 是身份 host，但 registry 里**也有** riotgames store flow，
移走会藏起那个配对。

**METRICS 的两个 vendor 数不是矛盾**：`core_coverage` 的 vendor 桶（支付+风控+基础设施）= 24，
`vendor_coverage.py` 的风险厂商 = 12。两个工具各自一致，「vendor」不是同一概念 —— 没查就当成矛盾改，会改坏它。

数字：套件 2205 · 陈旧度 0/0 · 函数数 173,952 · store 分母 15 / matched 15 / unmatched 0。

纪律：**默认规则的错只朝一个方向犯 —— 新东西被算进多数那类，于是没人看得见。**

下一轮：给「store 桶里不许出现支付标签」加一条守卫；并核 vendor 段口径（只搜 `Scripts/`）那个 Unknown。

## R989 补充 — **两列统一分母：vendor 未覆盖 20 → 6（全是支付网关）；假匹配 1 → 0**（套件 2205）

R988 留的 Unknown 解决了：vendor 段原用 `scripts_text()`（只读 `Scripts/`），而 store 段用整个 `src`。
改成共用 `all_src` 之后，**vendor 24 → matched 18 / unmatched 6**：
midtrans · gpayments · mollie · cybersource · touchtech · airwallex —— **六个全是支付网关，无一是风控厂商**。

→ 优先级 ②（风控）vendor 覆盖**完整**：cloudflare · kasada · datadome · perimeterx · queue-it · aycd ·
captcha · eshopworld · wdprapps · disney · global-e · vivapayments · paypal · adyen · klaviyo ·
braintree · sibs · vipps 全 matched。那 6 个属于**下单链路**（优先级 ①）。

**顺手修一个假匹配**：`registerdisney.go.com` 匹配在标签 `go` 上。
成因：分桶用整串 host（含 `disney`）、匹配用注册标签（`go.com` → `go`）。
改成「被 vendor 提示词打桶的 host 用那个提示词当标识」→ 经 `disney` 匹配，假匹配 0。

数字：套件 2205（未动测试）· 陈旧度 0/0 · 函数数 173,952 · store 15/0 · vendor unmatched 6 · 假匹配 0。

纪律：**两列放一张表 ≠ 两列在回答同一个问题。**

下一轮：核那 6 个支付网关在复刻件里是否真缺（`matched` 只说名字出现过，不说实现）；或给 store 桶加防支付标签的守卫。

## R990 补充 — **6 条未覆盖分类：1 指标盲区 · 1 伪造令牌 · 4 真缺**（套件 2205，未改代码）

核 R989 的 6 个支付网关：`where_is` 显示它们只在 `docs/VERDICT.md` 与 `docs/BINDING_BACKLOG.md`，
而 `core_coverage` 的 `all_src` 只走 `replica/src` → `unmatched` 准确。

**而六条分成三类：**
1. `threeds.airwallex.com` —— **指标盲区**：`Solve3DSRedirectAsync` 跟随**运行期** URL（来自 paymentData），
   host 名永不写进源码。泛化步骤覆盖率工具看不见。
2. `flex.cybersource.com` —— **被伪造值顶掉**：`StoreFlow.cs:1151`
   `c.Session.PaymentToken = "tok_" + Guid.NewGuid()...` **不调任何端点**。
   而 `ShopifyFlow.GetCsrf` 的注释写着 R823：「不编造 fallback —— 服务器未签发的令牌会让每个带它的请求被判无效」。
   同形第二处：`HISTORY.md` R12 表「`GetToken` | 16 字节 CSPRNG hex」。
3. `midtrans` / `gpayments` / `mollie` / `touchtech` —— **真缺**（收单会话 / 结果查询 / 状态轮询 / 支付选择）。

数字：套件 2205（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 未覆盖 6 = 1/1/4。

纪律：**「未覆盖」是混合类别 —— 做不到 / 没做 / 指标看不见 / 做了个假的，四者同名。**

下一轮：删掉 `GetPaymentTokenAsync` 的伪造令牌并让它调 `/flex/v2/tokens`（或写成显式 Fail + 原因），
同时核有无 override 真的调了端点。

## R991 补充 — **伪造的支付令牌已删；+2 守卫（验过会红）**（套件 2207）

`GetPaymentTokenAsync` 有 **0 个 override**，真令牌来自五处（`FootsitesFlow:353` 提 `"id"` ·
`MagentoFlow:806` 提 `"token"` · `ShopifyFlow:477` · `StoreFlow:1398/1474/1550` · `Gateways.cs` ×4）。
→ 那个 `Guid.NewGuid()` 只是**兜底**，而它会让「某个 flow 少写了一步」变成**假装成功**。

改成 `Fail($"{Name}: no payment token available … will not invent one", retryable: true)`。
理由直接引 R823：未签发的令牌让每个带它的请求被判无效；伪造只是把失败挪到下游、并伪装成被店方拒绝。

**而删掉它，全量套件一条都没红**（2222 通过 / 0 失败）→ 说明**没有任何用例覆盖那条兜底路径**。
所以产出不是删了三行，是加了两条守卫：
`NoCredentialIsMintedLocally`（全 src 不许 `Token = …Guid.NewGuid`）·
`TheFallbackReportsRatherThanInvends`（该方法必须还在、仍短路、含「will not invent one」—— 防「用删除来修」）。
**验过会红**：手动放回 1 处 → `[FAIL]` → 还原 → 通过。

数字：套件 2207（+2）· 陈旧度 0/0 · 函数数 173,952 · 伪造令牌 0 · 本地铸造凭据 0。

纪律：**删掉 + 全绿不是验证；验证是加一条会红的守卫并亲眼看它红一次。**

下一轮：核 `GetToken`（16 字节 CSPRNG hex）是不是同形第二处 —— 守卫没扫它（不同形）。

## R992 补充 — **`GetToken` = 接线缺口（三个名字都在原版）而非死代码；身体已改为报告；守卫加宽**（套件 2208）

`GetTokenAsync` / `CreateTokenAsync` / `GetAuthTokenAsync` **共用一个造 16 字节随机 hex 的身体**，
而 `GetAuthTokenAsync` 的注释写着「Acquire an authorisation token specifically」—— 授权令牌由服务器签发。

接线状态：`Vars["token"]` 写入 1 / **读取 0** · 三个方法**调用 0** · **不在任何步骤序列** · 字符串引用 0。
而原版 `recovered_method_names.txt` 里三个名字都在（行 453 / 1269 / 1595）
→ **形状在、边缺失**（R955：unreachable code needs a call, not a rewrite）→ **不是死代码该删**。

所以改的是**身体**：`Fail($"{Name}: no token source is known … will not invent a credential")`。
理由：接线的人不该拿到会造值的身体 —— 接上那一刻随机 hex 会变成「认证已完成」并流进请求。

**守卫加宽**：R991 的模式只匹配 `Token = <标识符>`，而这里是 `Vars["token"] = <随机字节>`（索引器）→ 漏。
加宽后两种形状都匹配；新增 `TheGenericTokenStepAlsoReports`。**验过会红**（放回 1 处 → 1 失败 2 通过 → 还原 3 通过）。

数字：套件 2208（+1）· 陈旧度 0/0 · 函数数 173,952 · 伪造通用/授权令牌 0 · 本地铸造凭据 0。

纪律：**「它不执行」只说明现在没问题，不说明它没问题。**

下一轮：核 `RefreshSessionAsync` / `HandleResponseAsync`（HANDOFF 记的另两个「真死步骤」）是否同形；
或回到优先级 ② —— 风控 vendor 全 matched 之后，核「matched 不等于接上」。

## R993 补充 — **状态码分类两份并存，409 冲突；`HandleResponseAsync` 未接上**（套件 2208，未改代码）

`HandleResponseAsync`（`StoreFlow.cs:349`）与 `ClassifyCheckoutFailure`（`StoreFlowRunner.cs:262`）
读同一个 `Vars["lastStatus"]`，各自有一份状态码表，而**只有后者在执行路径上**
（前者不在任何步骤序列、无调用点）。

**两份只在一个码上冲突，而那是 409：**
`ClassifyCheckoutFailure` → **Declined（终止）**，注释写着「A 409 (sold out during checkout) is the same story」；
`HandleResponseAsync` → **可重试**。
→ 409 = 结账途中售罄，判可重试会重试一件已卖出的东西。**所以接上它是危险的；接之前必须先对齐 409。**

**而这也更正 R985**：「原版状态码分类字符串层不可得」仍对，但它被我扩大成「这里没有」。
复刻件里有两份；`HISTORY.md` R12 那条描述的就是 `HandleResponseAsync`。**缺的不是原版证据，是一次 `where_is`。**

**未接上的理由**：`ClassifyCheckoutFailure` 那份有注释说明理由，`HandleResponseAsync` 那份没有；
「改哪一份」需要证据而非偏好 → 记 BLOCKERS。

顺手看到未追：`HandleResponseAsync` 下面紧挨 `DetectAsync`（`StoreFlow.cs:368`），从 body/headers 识别
cf-chl / kpsdk / _Incapsula_Resource / datadome / px-captcha / queue-it —— **优先级 ② 的实质内容**。

数字：套件 2208（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 分类器 2 份 · 冲突码 1（409）。

纪律：**「不可得」和「我没找到」是两个结论。**

下一轮：查 `DetectAsync` 接上没有 —— 那是优先级 ② 最实质的一块。

## R994 补充 — **墙接线 2/6 Wired；R989「优先级 ② 覆盖完整」撤回**（套件 2208，未改代码）

`src/Cybersole.Stores/Scripts/VendorWiring.cs`（R140/R141）**早有完整审计表**：
cloudflare **Wired** · kasada **Wired** · imperva DetectedOnly · datadome HostWithoutProtocol ·
perimeterx DetectedOnly · queue-it NotAChallenge。**2/6 接通，4 个缺口各有不同原因。**

→ **R989「优先级 ② vendor 覆盖完整（12/12）」撤回**：`vendor_coverage` 答「名字出现过」，
`VendorWiring` 答「链条完整」，12/12 与 2/6。这是「名字出现 ≠ 接上」的同一错误，只是高一层。

而 2 与 4 已被 `VendorWiringTests.cs:37-54` 与 `WallDispatchTests.cs:67-68` 钉住 → 「不知道」不是仓库的问题。

**最刺的是 `VendorWiring.AuditRule`：**
「detection and storage are cheap and were already present; the call between them is the work」
—— 正是 R992/R993 花三轮「发现」的形状。仓库 R140 就写成了常量。

优先级 ② 的剩余：imperva 缺**证据** · datadome 缺**协议** · perimeterx 缺**证据** · queue-it 缺**等待策略**。

数字：套件 2208（未改代码）· 陈旧度 0/0 · 函数数 173,952 · 墙 2/6 · 缺口 4（2 证据 / 1 协议 / 1 非墙）。

纪律：**`where_is` 查名字；「这件事有没有一张表」是另一种查法。**

下一轮：按这张表做 — datadome 的协议（唯一「缺代码」的那一格），或 imperva / perimeterx 的 cookie 取证。

## R995 补充 — **DataDome 协议在镜像里；新增第 5 个 state；+1 跨表守卫（验过会红）**（套件 2209）

取证：镜像里 DataDome 是完整链 —— `<GenerateSensor>d__11` `<SubmitSensor>d__12` `<GetSensorData>d__34`、
`https://datadome.cybersole.io/sensor`、`DataDomeKey`、`DatadomeSliderTask`、四阶段日志。
→ **「有 host 无协议」是错的**；协议在镜像里，缺的是**存回调用**。

**而我上一轮说「测试在保护一个已被更正的错误」—— 核查后只对一半**：`WallSolvingTests.cs:66` 的
`HostWithoutProtocol` 是 R141 **有意**保持的（`Wired` 要求检测→求解→**存回**三件齐全，存回没写）。
**错的是名字**：它说「协议不存在」，而实际是「协议在原版里、缺在我们的笔记里」。

改三处：① `VendorWiring.cs` 新增 `State.OriginalSolvesProtocolUnrecorded` + datadome 行改用它
② `VendorWiringTests.cs` 断言改用新 state + 新增 **`TheTwoAuditsAgree`**（跨表守卫）
③ `WallSolvingTests.cs` 断言改用新 state，**保留** `Assert.NotEqual(Wired, …)` —— 这一条最要紧，
只改前两处会让 R141 的意图消失。

跨表守卫：`WallSolving.HasSolveFor(v)` 为真 → `VendorWiring` 不得是 `HostWithoutProtocol`/`DetectedOnly`。
**验过会红**：改回 → 2 失败，其中跨表那条**独立**红。

判据 (f) 的 4 个缺口：imperva 缺证据 · **datadome 缺存回调用（协议已知）** · perimeterx 缺证据 ·
queue-it 等待策略。**`Wired` 仍 2/6 —— 未变。**

数字：套件 2209（+1）· 陈旧度 0/0 · 函数数 173,952 · 墙 2/6 · 状态 5 种 · 跨表矛盾 0。

纪律：**一个看起来在阻碍你的守兵，可能正站在正确的位置上。**

下一轮：写 DataDome 的存回调用（协议已知：sensor 端点 + 三方法 + 四阶段），把它从 2/6 推到 3/6。

## R996 补充 — **DataDome 接线完成：墙 2/6 → 3/6**（套件 2209）

**新建 `src/Cybersole.Stores/Scripts/DataDomeClearance.cs`（125 行）**，与 `CloudflareClearance.cs` 对称：
SensorUrl = `datadome.cybersole.io/sensor` · SdkUrl = `api-sdk.datadome.co/sdk/` · cookie `datadome` ·
四阶段 Getting/Initialising/Solving/Submitting · `ApplyAsync` 存回 `Vars` **且** `Cookies` ·
未配置时返回**状态**而非错误。

**`SolveDetectedWallAsync` 白名单加 `datadome` + 新增分支** —— 之前它只放行 cloudflare/kasada，
datadome 走不到任何 solver。**`Wired` 的意思是「检测→求解→存回三样都有人调」。**

这一轮**没有**发明第二条路：镜像只命名一个 relay + 一个 SDK，所以没有 service→in-bot 阶梯。

改了 5 处断言，其中两处是钉住 2/6 的（`VendorWiringTests` 用例名 → `ThreeOfSixAreWired`；
`WallDispatchTests` 的 `Gaps.Count` 4→3）。**踩到一个细节：`Wired` 顺序是行序不是字母序** ——
改成字母序立刻报 `Collections differ`。

**边界**：3/6 是「调用链存在、派发到它、存回写对」，不是「本机能过」（求解默认返回未配置，
与 Cloudflare 的 401 同口径）。

数字：套件 2209 · 陈旧度 0/0 · 函数数 173,952（未 publish）· 墙 3/6 · 缺口 3。

纪律：**一个标签的改善不等于工作的进展** —— R995 那个 state 是对的，而它一个字都没让墙过去。

下一轮：imperva 或 perimeterx 的 cookie 取证（剩下两个缺口都是「缺证据」）；或 publish 一次把函数数刷新。

## R997 补充 — **六行 marker 加出处列：4 ImageLiteral · 2 Inferred（cloudflare · imperva）**（套件 2210）

探针：`kpsdk` 17 · `queue-it` 13 · `datadome` 15 · `_px3` 在 —— 四个真串；
**`cf-chl` 0 · `_Incapsula_Resource` 0** —— 两个是**我们自己编的**。
→ 而 **Cloudflare 是已声明 `Wired` 的那一格**：它的检测标记是我们写的不是抄的。
→ `cf-chl` 能工作因为真实挑战页里有它 —— 但那是**常识**，不是镜像证据。

**PerimeterX 更正**：`_px3` · `_pxvid` · `PerimeterX-Token` · `PerimeterXHandler` ·
「PerimeterX block (Rotating proxy)」全在。旧 note「no `_px` cookie does」错。
那句「block (Rotating proxy)」说明原版把**被封与轮换代理**连起来 —— 那是行为不是 token 名。

加了一列：`MarkerSource { ImageLiteral, Inferred }`，`Row` 多一个参数，六行各补。
守卫 `TheMarkerColumnSaysWhereEachMarkerCameFrom` 钉住 `Inferred == {cloudflare, imperva}`
（测试没法重探二进制，所以钉集合；改动它得重跑 `ida.py str` 并在里面找到东西）。

数字：套件 2210（+1 守卫）· 陈旧度 0/0 · 函数数 173,952 · 墙 3/6 · marker 出处 6/6 · Inferred 2。

纪律：**判据 (d) 要的不是「有证据」，是「每条写着它的证据是什么」。**

下一轮：publish 一次刷新函数数（已多轮未 publish）；或查 `px-captcha` 是否也在镜像里（我只验了 `_px3`）。

## R998 补充 — **perimeterx 标记改 Inferred；`DetectAsync` 改用镜像里的 `captcha-delivery`（5/6 有据）**（套件 2210）

**R997 标错了一列**：`px-captcha` 镜像 **0** 命中，而 `_px3` 是 **cookie** 列的东西。
我标 `ImageLiteral` 时看的是「这个厂商有镜像证据吗」，而那一列问的是「**这个格子里的串**在镜像里吗」。
→ `Inferred` 现为 **3 个**：cloudflare · imperva · **perimeterx**。

**而镜像里有一个可用的标记**：`captcha-delivery` **4** 命中（`geo.captcha-delivery.com` · `/` · `/interstitial/`）。
→ `DetectAsync` 新增 `captcha-delivery` 分支，**排在 `px-captcha` 之前**。
→ 检测能力实际变强：之前只靠一个镜像里不存在的串，现在先测镜像里那个。

数字：套件 2210 · 陈旧度 0/0 · 函数数 173,952（未 publish）· 墙 3/6 · Inferred 3 · **有据标记 5/6**。

纪律：**一个刚加上的字段就能抓住写它的人 —— 这是它值得加的最好证据。**

下一轮：publish 一次刷新函数数（已多轮未 publish）；或 imperva 的标记（5/6 里最后那个没据的）。

## R999 补充 — **METRICS 摘要加「时效警告（生成）」；变异重跑 36/36；产物仍陈旧且不能 publish**（套件 2210）

本来要去 publish 刷新函数数，**1.8 GB 可用 → 按纪律不做 AOT publish**。查的过程中发现更要紧的事：
摘要表把 `173,952 / 62.77%` 排在 `15 个源文件更新` 的正上方而**无标注**，
而 `mutation-fit: staleness` 写着 `1:31:27` —— **两个过期的数与一个当前套件数同列。**
（`artifact_freshness.py` 自己的注释要求「must be labelled as such wherever it is quoted」，摘要区没做。）

**修生成器**：`metrics_report.py` 在摘要表前生成「时效警告」块，规则从工具输出读（不硬编码）。
**并重跑变异**（不耗内存）：**36/36 fired · 0 decorative · 0 skipped · GREEN · ran 14:06:23**。
→ 警告从 **2 条降到 1 条** —— 一条消失是因为被警告的那件事**真的被做了**。

剩下那条是产物：**修不了（内存不够），但它现在说出来了**。

数字：套件 2210 · 产物陈旧度 **15 / 10,753（未变）** · 变异陈旧度 0 · 变异 36/36 · 摘要警告 1 条。

纪律：**一个单一数字源的价值取决于它说清每个数的时效，不取决于它集中。**

下一轮：内存回到 2 GB 以上时 publish 一次，让函数数变当前；或继续核心（imperva 标记 / 优先级 ① 的 4 个真缺端点）。

## R1000 补充 — **publish 完成：173,994 / 62.79%，陈旧度 0/0；R991/R992 的改动不在产物里**（套件 2210）

内存回到 16.9 GB → AOT publish 跑通（50 秒，exit 0）。
**函数数 173,952 → 173,994（+42）· 比 62.77% → 62.79% · 陈旧度 15/10,753 → 0/0 · 产物 53.4 → 53.5 MB**
→ **R999 那个时效警告块消失了**（被它警告的两件事都做了；两次证明那个块跟着数据走）。

**而最有价值的不是新数字，是一个否定结论**：在两个 exe 的字节里搜我这三轮写的话 ——
| 串 | 新产物 | 旧产物 |
|---|---|---|
| `will not invent one`（R991） | **absent** | absent |
| `not invent a credential`（R992） | **absent** | absent |
| `DataDome clearance acquired`（R996） | **IN** | absent |
→ **R991/R992 的修复没进产物**（R963：零覆写基类虚方法被裁，改身体不改变产物）。
→ R996 的新类**进了**（被 `SolveDetectedWallAsync` 直接调用、静态可达）。
→ **`+42` 可归因到它 —— 这是 Observation 不是 Inference。**

**规则：进产物二选一 —— ① 有真实调用点 ② 被某个 flow 覆写。「把基类虚方法身体写好」是源码整洁，不是产物进展。**

数字：套件 2210 · 陈旧度 0/0 · 函数数 173,994 · 比 62.79% · 时效警告 0 条。

纪律：**区分「改对源码」与「改动产物」只需在产物里搜你写的那句话 —— 我三轮后才第一次做。**

下一轮：按新规则做核心 —— 给步骤真实调用点或让 flow 覆写它（优先级 ① 的 4 个真缺端点最合这条）。

## R1001 补充 — **4 个网关已写但零个进产物：`CreateDefault()` 无调用者，整族被裁**（套件 2214）

按 R1000 的规则①（真实调用点）做了：`Gateways.cs` 追加 4 个网关（Mollie / GMO / Touchtech / Midtrans，250 行），
`PaymentGatewayRegistry.CreateDefault()` 注册 → 13 个。构建成功、60 条支付用例 + 4 条新守卫通过。

**而 publish 后：4 个 host 串全 absent，函数数 173,994 → 173,994 不动。**
判别组：**`PaymentGatewayRegistry` 这个名字不在产物里** → `CreateDefault()` 没人调 → 整族死代码被裁。
→ 连既有 9 个里 **7 个也不在**（`sibspayments`/`squareup`/`unzer`/`omise`/`adyen` 全 absent），
只有 `api.stripe.com` / `paypal.com` IN（从 UI 的支付方式枚举可达）。
**→ 整个支付层在产物里几乎不存在。**

**规则收紧**：「注册」不是「接线」，「接线」不是「可达」。真正的判据是**从入口能不能走到**。
与 R963（反射不 root 方法）同一族但不同因：那次是调用方式不可见，这次是调用链不可达。

**正确方向**：让**具体 flow 覆写支付步骤**，在覆写里直接调 `registry.Resolve(id)?.AuthorizeAsync(c, ct)`
—— 调用链从 flow 出发才可达（R1000 的第二条路）。

数字：套件 2214 · 陈旧度 0/0 · 函数数 173,994（不动）· 新增 4 类 / 进产物 **0** · 既有在产物里 2/9。

纪律：**「我给它加了调用点」可以为真而不改变产物一个字节。**

下一轮：取证 host↔flow 对照（哪个 flow 该承载 Mollie/GMO/Touchtech/Midtrans），然后让那个 flow 覆写支付步骤并直接调 registry —— 否则第 5 个网关也一样进不去。

## R1002 补充 — **一句接线把 250 行代码拉进产物：+0 → +342**（套件 2214）

改两处：① `PaymentGatewayRegistry.Default`（静态单例）② `SubmitPaymentAsync` 里 `Default.Resolve(gateway)` → `AuthorizeAsync`。
**选 `SubmitPaymentAsync` 的理由：它有 12 个覆写 → 基类体保留 → 调用可达（R963 的反面）。**

**产物验证（肯定）**：`PaymentGatewayRegistry` IN · 4 个新网关 host 全 IN · `sibspayments`/`unzer`/`omise` IN
→ **产物里网关 2 → 9**。`needs a 3-D Secure step` absent（该分支未保留，可达的是 `AuthorizeAsync`）。

**函数数 173,994 → 174,336（+342）· 比 62.79% → 62.91% · 陈旧度 0/0。**
→ 同一份 250 行代码，R1001 是 **+0**、R1002 是 **+342**，差别只在那一行是否在可达的路上。

**可达性三档（R1000 修订）**：① 从入口可达 ② 被覆写 ③ 两者都没有（被裁）。
**「有调用语句」不构成任何一档。**

仍 Unknown：`squareup`/`adyen` 的 host 拼法；`RequiresAction` 分支为何未保留。

纪律：**可达性独立于代码量，它不写在任何一行里，只能被证明或被否证。**

下一轮：`GetPaymentMethodsAsync` 覆写 0 次 → 它必然被裁，把它接到某个覆写里去（或查原版是否真无覆写）。

## R1003 补充 — **可达性精确到方法；Square/Adyen 是我搜错串；Adyen/CommerceHub 整个不在 = id 不匹配**（套件 2214，未改代码）

**自我纠正 ×2**：`SquareGateway` 的真实 host 是 **`pci-connect.squareup.com`**（我搜 `api.squareup.com`）；
`AdyenGateway` 是 **`checkoutshopper-live.adyen.com`**（我搜 `adyen.com`）。→ 「absent」是我搜错了。
（AGENTS.md §2.7 那个形状第**十**次：先假设形状，再把不符读成不存在。）

**正确拼法重搜**：11 个网关的主 host **IN**（Square 也在）· **Adyen / CommerceHub 整个 absent** ·
7 个的次 host 全 absent（`api.sandbox.paypal.com` · `checkout-page.omise.co` · `nodecde1/shield.paynamics.net`）。

**规律**：IN 的都是 `AuthorizeAsync` 里 `$"{ApiHost}/…"` 那一段；absent 的次 host 全在
`TokenizeAsync` / `CompleteActionAsync` 里 —— **而 R1002 只接了 `AuthorizeAsync`。**
**→ 可达性精确到**方法**，不是到类。**

**Adyen/CommerceHub 的原因不同**：它们连被直接调的 `AuthorizeAsync` host 都不在 → 问题在**它们的 `Id` 没被 `Resolve` 命中**
（与 `CreateDefault` 同形状，只是发生在 id 上）。**那是可查的具体问题，不是缺证据。**

数字：套件 2214 · 陈旧度 0/0 · 函数数 174,336 · 主 host IN 11 · 次 host 全无 7 · 整个不在 2。

纪律：**「进了产物」要说到类、方法、还是那一行 —— 粗的那个听起来完成了更多。**

下一轮：查 `AdyenGateway.Id` / `CommerceHubGateway` 的 Id 与 `ChooseGateway` 的产出集合是否相交。

## R1004 补充 — **Adyen/CommerceHub 在产物里，被裁的是方法体；R1003 的 id 假设被否掉**（套件 2214，未改代码）

**否掉 id 假设**：`Id = "adyen"` / `"commercehub"` · `Resolve` 用 `OrdinalIgnoreCase` ·
`ChooseGateway` 返回商店提供的名字 → `"adyen"` 能命中 → **不是 id 的问题**。

**非 host 特征串全 absent**：`CybersoleECOM` · `encryptedCardNumber` · `tokenUUID` · `/api/v1/sale` · `commercehub.sessionId`。

**而短串计数把它翻了过来**：`adyen` UTF-16 **x19** · `commercehub` **x17** · `square` x10 · `omise` x52
→ **类与前两个方法在产物里，`AuthorizeAsync` 的方法体被裁。**
→ 这是「可达性精确到方法」的**下一层**：类在、`Id` 在、方法体不在。

**三次读数都往同一方向高估了裁剪**：「整个支付层几乎不存在」（R1001 ✗）· 「9 个网关进了」（R1002 偏粗）·
「Adyen/CommerceHub 整个不在」（R1003 ✗）—— **都把**方法体**的缺席读成**类/层**的缺席。**

**原因两个不同**：Adyen 的 `AuthorizeAsync` 里无 host 串（`ShopperHost` 在另两个方法）；
CommerceHub 用 `Host(c)`（**从 session Vars 读**），`DefaultHost` 常量只在被裁分支里。

数字：套件 2214 · 陈旧度 0/0 · 函数数 174,336 · id 在产物 13/13 · `AuthorizeAsync` 体在 11 · 长串全无 2。

纪律：**「在不在产物里」对长串和对类型名是两个问题 —— 我一直用一个答案回答两个。**

下一轮：查「只留签名」的触发机制 —— 或换到优先级 ① 的 flow 端点（那条路已有覆写证据）。

## R1005 补充 — **409 两难取消：镜像无状态码语义；缺货按消息分 3 类**（套件 2214，未改代码）

**IDA 就绪流程**：doctor 报 PROXY MISSING / PORT REFUSED，而 IDA 其实起来了停在框上 ——
`ida.py` 直连 13337 不走 DSH 代理。清框：unpacked→**Proceed with unpacked base** ·
id0→**是(Y)** · 「请稍候…」→**等** · **新框型「Database still contains inconsistencies」→ 确定**（本轮补记）。
→ `13337 LISTENING pid=44936`。

**409 的状态码语义在镜像里不存在**：`409` 40 条全是十六进制哈希；`Conflict` 30 条是 .NET 枚举名；
`unavailable` 40 条是 HTTP 枚举名。**所以 R993 的「哪份表对」在状态码层无解。**

**而原版在消息层给了答案**：`Out of stock (reservation failed), retrying` · `Out of stock (decoy)` ·
`Item is Out of Stock`。**缺货分 3 类：reservation failed→重试 · decoy→不重试（另有 `get_DecoyActive`）· 真缺货。**

**裁决**：两份表同错，都在按状态码分类。修法不是选一份，是**加一层消息判断**：
① 状态码层保守（409→Declined）② 含 `reservation failed`→可重试 ③ 含 `decoy`→不重试。
**接 `HandleResponseAsync` 之前必须先有这一层，否则 409 一律变可重试。**

数字：套件 2214 · 陈旧度 0/0 · 函数数 174,336 · 409 语义 无 · 缺货分类 3 · IDA 框型 4。

纪律：**取证的第一个用途不是选边，是检查那个二选一是否成立。**

下一轮：按三条证据加消息层（`reservation failed` / `decoy` / 真缺货），再接 `HandleResponseAsync`。
**仍停下等 YG**：DSH 的 ida 代理 MISSING（不影响 ida.py，但 mcp__ida__* 不可用）。

## R1006 补充 — **消息层实现正确（11 绿）但未进产物；`lastBody` 通道补上；R1002 可达性结论撤回**（套件 2218）

`ClassifyCheckoutFailure` 加消息层：`reservation failed`→`Error`（可重试）· `decoy`→`Declined`（不重试）·
两者同时出现**拒绝优先**；状态码层保持保守。**并补 `Vars["lastBody"]`** —— `home` 是**首页**，
缺货消息在 **checkout 响应**里（实现里的真错，本轮修掉）。**11 条测试绿。**

**而 publish 后：`reservation failed` · `decoy` · `lastBody` 全 absent，函数数 174,336 未变。**

**更重的是判别组把 R1002 否掉了**：`StoreFlowRunner` / `GuardAsync` 现在 **absent**，而 R1002 我记的是 **IN**。
而函数数在 R1002 之后没变 ⇒ 不是裁剪变化 ⇒ **其中一次读数是错的**，而记录不足以判断是哪一次。
→ **R1002「+342 因为可达」的解释撤回；R1004 的 `Id` 计数读数也需重验。**

数字：套件 2218（+4）· 陈旧度 0/0 · 函数数 174,336（未变）· 消息层进产物 否 · R1002 可达性 撤回。

纪律：**产物读数是观测 —— 观测要有稳定的对象和记录。**

下一轮：先设计一条**稳定的**产物读数方法（同一文件 + 存快照 + 记录 sha256），再重验 R1002/R1004 两条结论。

## R1007 补充 — **`tools/artifact_probe.py` 建立；一击推翻 R1006 的自我否证**（套件 2218，未改产品代码）

新工具 `replica/tools/artifact_probe.py`：每次探测记录**产物身份**（sha256/bytes/mtime），**两种编码并查**，
追加到 `analysis/ARTIFACT_PROBES.json`。

**第一次跑就推翻了 R1006**：
`StoreFlowRunner` **utf-8 1 → present** · `GuardAsync` **utf-8 2 → present** · `antibot` utf-16-le 3 → present
→ **我 R1006 只查 UTF-16LE，所以报 absent。R1002 的 IN 是**对的**，那条撤回**撤回**。**
→ 而 R967 早已立规：反射元数据是 UTF-8、字面量是 UTF-16LE，查错一种会给自信的「没有」—— 我在 R1006 违反了它。

**而消息层四个串两编码皆 0**（`lastStatus`/`lastBody`/`reservation failed`/`decoy`）—— **那部分结论对**，
且现在有 sha256 = 36c16b3b… 背书。

数字：套件 2218 · 陈旧度 0/0 · 函数数 174,336 · 带身份读数 全部 · R1002 结论 **恢复**。

纪律：**「两次读数矛盾」有第三种解释 —— 两次问的不是同一个问题。**

下一轮：用新工具重验 R1004 的 `adyen`/`commercehub` 计数（两编码并查），然后继续优先级 ①。

## R1008 补充 — **R1004 读数确认；`paymentMethodsUrl` 是第二个自造键名**（套件 2219）

**R1004 重验成立**（新工具双编码 + sha256）：`adyen` **utf-16-le 19** · `commercehub` **17** ·
`CommerceHub` **utf-8 1** · 而 `CybersoleECOM`/`encryptedCardNumber`/`tokenUUID`/`/api/v1/sale`/`checkoutshopper` **全 0**。
→ `Id`/`Name` 在产物、`AuthorizeAsync` 方法体不在。**新事实：同一类里 id 是 UTF-16LE、Name 是 UTF-8。**

**优先级 ① 上找到第二例自造键名**：`Vars["paymentMethodsUrl"]` 镜像 **0 命中**。
（R956 修过 `paymentGateway` 是第一例。）
而镜像里步骤**是真的**：`RpcGetPaymentMethods` 带**两个 lambda**，ordinal **177** 与源码注释一致。
**缺的是**路由** —— 而 R958（NativeAOT 下按名反编译不成立）⇒ 不可得。**

改动：`GetPaymentMethodsAsync` 注释写明三点（键名自造 / 步骤与 ordinal 真 / 路由不可得且零覆写被裁）；
新增守卫 `ThePaymentMethodsURLKeyIsRecordedAsInvented`。
**守卫判据不是「名字对不对」（它不对），是「读源码的人会不会以为它被搜过」。**

数字：套件 2219（+1）· 陈旧度 1 / 2,671（只改注释）· 函数数 174,336 · 已知自造键名 2。

纪律：**自造键名有稳定成因 —— 编译得过、读起来对，没有机制会质疑它。**

下一轮：扫「所有 `Vars[...]` 键名对镜像查一遍」—— 那能一次性找出还有几个自造键名。

## R1009 补充 — **326 个会话键扫完：152 在 · 159 不在（97 带点是表示方式差异）；`lastStatus` 从来不在产物里**（套件 2219，未改产品代码）

**`analysis/vars_key_provenance.py`**（两阶段，输出 `analysis/VARS_KEY_PROVENANCE.md`）。
**而第一阶段失效**：`settled by the sample: 0` —— 换行匹配对抽样格式不对，326 个全走 IDB（约 15 分钟）。

结果：**326 键 · 152 在 · 159 不在（带点 97 / 不带点 62）· 15 未解析。**

**三分类**：① 97 个带点键（`adyen.*`/`kasada.*`/`paypal.*`）—— 原版用**字段**不用字符串键，absent **正常**
② 5 个真自造（`lastStatus`/`lastBody`/`sensorKeys`/`paymentMethodsUrl`/`antibot.solver`）
③ 约 50 个待判（`orderProcessed`/`totalMinor` 像镜像语义）

**最重的一条：`lastStatus` 两编码皆 0 —— R993 说的「活通道」从来不在产物里。**
→ R1006 悬案有答案：**消息层读的通道本身不存在**，不是消息层被裁。
→ 「活通道」两个意思（复刻件内部活 vs 产物里存在）被混用 —— 而混用会让「接上」看起来像小事。

数字：套件 2219 · 陈旧度 1 / 2,671 · 函数数 174,336 · 键 326 / 152 / 159 / 15。

纪律：**把 159 当成 159 个待修是错的。**

下一轮：判那约 50 个不带点键（`orderProcessed`/`paymentStarted`/`totalMinor`/`transactionAmount` 优先）。

## R1010 补充 — **键名判据有定义域：159 个 absent 里约 154 个不可判且不需修**（套件 2219，未改代码）

按 R956 的教训换成四种形态再查（bare / `_field` / `get_Pascal` / `content=`）：
`orderProcessed` · `paymentStarted` · `totalMinor` · `transactionAmount` · `deviceProfiled` ·
`sizeLine` · `selectedRate` · `discountApplied` —— **全 0，四种形态一个都没有。**

**而全 0 不说明它们错 —— 说明这个问法对这一类**不适用**：**
原版没有 `Vars` 字典，它用**字段**，字段名不必与我们的键名相同。
→ **判据的定义域：只对**协议层**名字有判定力（`kpsdk`/`datadome`/`paymentGatewayName`/URL/cookie 名），
对**内部状态管理**没有。**
→ 与 **R730「不再写前缀分类器」同一课**：判据在某一层不适用时，用它得出的结论是假的。

**159 的正确读法**：97 带点（不可判，我们发明的命名空间）· ~57 驼峰内部（不可判）· **5 协议层（可判）**。
5 个里**只有 `paymentMethodsUrl` 该判**（端点在必须来自镜像，R1008 已记）；另 4 个是我们自己的通道名，缺失正常。

**152 present 的含义清楚了**：那 152 个是协议层名字 → **「抄来的都在，自己起的不在」—— 应有的样子。**

数字：套件 2219 · 陈旧度 1 / 2,671 · 函数数 174,336 · absent 159（154 不可判 / 5 可判 / 1 需修且已记）。

纪律：**判据在某一层不适用时，它的输出形状和「全都是缺陷」一模一样。**

下一轮：回核心 —— 优先级 ① 的 flow 端点（那条路已有覆写与 ordinal 证据）。

## R1011 补充 — **Nike 付款的两个端点镜像 0 命中，改成报告（覆写 ⇒ 原本真的会发出去）**（套件 2219）

**缺陷**：`NikeFlow.SubmitPaymentAsync`（**覆写 ⇒ 进产物**）打 `buy/orders/v2/…/initiatePayment` 与 `…/payment`。
而 `NikeEndpoints.cs:8-10`（R87）早写着这两族「the binary does not contain at all」—— **那两行又活了 900 多轮。**

**镜像查证**：`buy/orders/v2` **0** · `buy/carts/v2` **0** · `buy/checkouts/v3` **1** · `checkout_previews` **2** ·
`initiatePayment` **3**（`/rpc/payment/pay/initiatePayment` 无 host · `/InitiatePayment`）。
→ 操作是真的，**地址不成立**。

**改动**：改成 `Fail("nike: payment endpoint not captured -- …", retryable: false)` 并列出三个候选；
原两段移进 `private AttachCardAsync`（未调用，留证）。
**不拼 host + path**（`EndpointProvenanceTests` 禁的发明，会是第六次）；**不破坏能工作的东西**（那两条本来必 404）。

**同一原则第四次**：R823 CSRF 兜底 · R991 伪造令牌 · R1001 四网关 · R1011 本条 ——
共同点：把「我不知道」写成「它拒绝了我」。

数字：套件 2219（47 条 Nike 用例通过）· 陈旧度 2 / 2,7xx · 函数数 174,336（未 publish）· Nikon 活请求 2 → **0**。

纪律：**注释不是守卫；守卫要能被跑。**

下一轮：`GetPaymentMethodsAsync`（ordinal 57，零覆写 ⇒ 被裁）在 Nike 上覆写 —— 那是本轮起点的正题。

## R1012 补充 — **首个 `GetPaymentMethodsAsync` 覆写进产物；查出该族还有 4 处活代码；两个观测未解释**

**做成了**：`NikeFlow.GetPaymentMethodsAsync`（全仓第一个覆写）—— 地址 `NikeEndpoints.Checkouts`（`0x147053d8c`），
复用 `ParsePaymentMethodNames`，写 `PaymentGatewayNameKey`。
**产物验证**：`buy/checkouts/v3` **IN**（旧 absent）· `no checkout to read payment methods` **IN**。
→ 同时解决 R1008 的两件事（零覆写被裁 + 自造端点键）。

**未解释 ×3（标 Unknown，不写成结论）**：
1. **函数数 174,336 未变** —— 而 R1002 加一句 `Resolve` 涨 342。两个观测矛盾。
2. **metrics 报 2218/1，全套报 2236/0** —— **间歇失败，未定位**。
3. ~~字符串池~~ 已解释：**「代码留证」的未调用方法体可能留字面量**；删掉后 `nike: no card` 消失证明删对，
   而 `buy/orders/v2` 仍在 —— 因为它**本来就不止两处**。

**新查出该族仍 4 处活代码**：`NikeFlow.cs:493`（`/delivery`）· `NikeFlow.cs:670`（SNKRS cart）·
`StoreFlow.cs:2365`（`/buy/carts/v2/app`）· `NikeModule.cs:80`（SNKRS cart）。

数字：全套 2236/0/2 · metrics 2218/1（间歇）· 陈旧度 0/0 · 函数数 174,336（未变）· 覆写 1 · 残留 4 处。

纪律：**「修了两处」的满足感会让「还有几处」不被问出来。**

下一轮：修那 4 处（`NikeFlow.cs:493` 的 `/delivery` 最急，它是运单步骤，必 404），并定位间歇失败。

## R1013 补充 — **间歇失败不复现；Nike 无购物车端点（模型错）；修 `/delivery`；函数数未变已解释**

**间歇失败**：五次跑中一次，之后三次全 0（含 metrics 精确 filter **2219/0/0**）。失败那次我在同时 publish
⇒ 最可能构建服务器竞争。**不可复现 ≠ 已解决**，保留观察。

**Nike 的完整 buy 面 7 条，全 checkouts 家族**：`checkout_previews/v3/` · `..._jobs/v3/` · `checkouts/v3/` ·
`checkouts_jobs/v3/`（另 3 条同族）。而 **`buy/carts` 0 · `carts/v2` 0**。
→ **Nike 没有购物车端点、没有订单端点**，只有一个 checkout 资源 + preview + jobs。
→ 那 3 处「购物车」代码**是模型错不是拼错**。而 R87 那句「single `buy/checkouts/v3/` resource that each step
writes to」被读成了「换 URL 前缀」，它说的是**模型**。

**修了有据的一处**：`NikeFlow.cs:493` `/delivery` → `NikeEndpoints.Checkouts + CartId`。请求体保持原样。
**另 3 处未修**：需行为改动（购物车 → checkout），要先确证 checkout 创建语义。

**「函数数未变」现在解释了**：两次一致 ⇒ 规律 —— `NikeFlow` 的方法多已覆写且已在产物里，改身体不改函数数。
而 R1002 的 `+342` 是**从零拉进一整族新类**。**两者不矛盾：改已可达的代码 vs 让不可达的代码变可达。**

数字：metrics 2219/0/0 · 全套 2236/0/2 · 陈旧度 1 / 711 · 函数数 174,336 · Nike buy 端点 7 · 活代码 4 → 3。

纪律：**问「这个 host 有什么」比问「这几个族有没有」更能说明该怎么办。**

下一轮：取证 Nike checkout 的创建语义，改那 3 处（购物车 → checkout）。

## R1014 补充 — **撤回 R1012/R1013 的两次地址替换：R48 早已裁决「换猜是移动失败」**

**`NikeFlow.CartUrl()` 的注释（R48，656-682）原文**：
> 「the fourteen checkout steps share those five URLs … **no way to tell which of `checkouts/v3` and
> `checkout_previews/v3` carries the add. Swapping one guess for another would move the failure, not remove it.**」

**而我 R1012（`GetPaymentMethodsAsync`）与 R1013（`/delivery`）都把地址换成了 `NikeEndpoints.Checkouts`，
依据是「每个 step 都写它」—— 那是**真**的，而不决定哪个 step 写什么。**

**而交换猜测比 404 更坏**：旧地址只能 404 且说得出来；新地址返回 200 或 payload 错，
错误消息不再指向地址不存在。「payment methods HTTP 200 但没有付款方式」读起来像**商店不支持刷卡**。
→ 那是 R823/R991/R1001/R1011 那条原则的同一次违反，**只是披着「有据替换」的外衣**。

**回滚**：两处都改成 `Fail(..., retryable: false)` 并点名三个候选；**保留**① 覆写本身（让步骤不被裁，R963）
② 候选清单（镜像真的只有那五个）。

**R48 那条注释存在了 900 多轮，而我改的就是它下面的那个文件 —— 而我没读它。与 R995 同形。**

数字：套件 2219/0/0 · 全套 2236/0/2 · 陈旧度 1 / 681（净减 30 行）· 函数数 174,336 ·
「有据替换」地址 2 → **0** · 引用 R48 处 0 → **2**。

教训：**「有据」有两种 —— 这个地址存在，和这个 step 用这个地址。我满足的是第一种。**

下一轮：换一个站（那 3 处已封口，理由写清）；或取证 Nike 的 checkout 步骤体（R958 说按名不可得）。

## R1015 补充 — **端点扫描器跳过所有插值模板（一行 continue）；修掉后一次查出 11 个待判**

**盲区在 `endpoint-provenance.py` 第 165-167 行，而且明确写了**：
```python
# skip interpolated templates and obvious fragments
if "{" in value or value.endswith("/"):
    continue
```
→ Nike 那 4 处**全是**插值模板 ⇒ 全在界外 ⇒ 工具的「invented: 0」**是真的但没用**。
→ **R1010「判据有定义域」的第二次，这次在代码里，有行号。**

**修法**：`static_prefix()` 取第一个 `{` 之前；只在带路径时判；`proven(x) or proven(x.rstrip('/'))`。
只到 host 的前缀不管（它什么都不断言）。

**修完后**：`inline literals 268 → 328` · `not in pool 29 → 40` · `unknown 0 → 11` · 工具**退出码 1**。
11 个分布：`FarfetchFlow.cs` ×7 · `NikeFlow.cs` ×2 · `StoreFlow.cs` ×2。

**已能判的 2 个**：`NikeFlow.cs:652 buy/carts/v2/{…}` **确实不存在**；
`NikeFlow.cs:235 product_feed/threads/v2/` 在 `NikeEndpoints.ProductFeedThreads` 里**镜像有** ⇒ **疑似假阳性**
（结尾 `/` 与 `?fields=` 形不同）。

**不登记进 ledger**：`BASELINE = 0` 是收紧守卫；登记 11 个等于把「不知道」写进白名单。
→ 工具**红着是正确状态**；不影响套件（metrics 跑 dotnet test）。

数字：套件 2219/0 · 函数数 174,336 · 内联字面量 328 · 不在池 40 · 未登记 11 · 工具退出码 1。

纪律：**一个「0」可以同时是真的和没用的 —— 只要定义域排除了缺陷所在的那一类。**

下一轮：判那 11 个（先修假阳性判定，再逐个对镜像）。

## R1016 补充 — **池行带地址列 ⇒ 前缀规则一次没生效；修完 11 → 10，10 个经 IDB 全 0 命中**

**第一版前缀规则加对了，跑起来什么都没变**（仍 11，`NikeFlow.cs:235` 还在）⇒ 它**一次都没命中**。
**原因**：`pe_strings.txt` 的行是 `0x地址  串`：
`'0x0705312c  https://api.nike.com/product_feed/threads/v2?fields='`
→ `line.strip()` 保留地址列 ⇒ `startswith(URL)` 永不成立。
→ 而 `value in pool`（全文子串）一直对 ⇒ **「相等」路径好，「前缀」路径死，两条输出混在一份报告里。**

**修第二版**（剥掉 `0x…  ` 前缀）后再跑：`not in pool 40 → 39` · `unknown 11 → 10`，
而消失的正是 `NikeFlow.cs:235` —— **R1015 预测的假阳性，自己消失了。**

**剩 10 个逐个问 IDB：六个不同前缀**全** 0 命中**：
`/api/ff-products/v1/products` · `/api/basket/v1` · `/api/checkout/v1/basket` ·
`buy/carts/v2` · `/discount` · `/api/payments`。
→ **10 行全是自造**：Farfetch ×7 · Nike ×1 · StoreFlow ×2。
→ 而 `/discount` 与 `/api/payments` 是通用词，我原以为会命中 —— 0 说明那两个打点也自造。

**工具红着 10 是准确状态**：10 个经 IDB 定性为不存在 ⇒ 真缺陷，不是待判 ⇒ 仍不登记进 ledger。

数字：套件 2219/0 · 函数数 174,336 · 内联字面量 328 · 不在池 39 · 未登记 10 · IDB 定性 10/10 全 0。

纪律：**判据修好后输出没变，先问它测过没有。**

下一轮：取证 Farfetch 与 Shopify 的真实端点，改那 10 处。

## R1017 补充 — **Farfetch 的 API 面完全不在镜像里；Shopify 两处有候选却仍不改；10 处全部处置完毕**

**Farfetch：镜像只有 3 条串，全是名字**（`Farfetch` · `Farfetch` · `Farfetch Checkout`）。
而 `api.farfetch` **0** · `farfetch.com` **0** · `ff-products` **0** · `basket/v1` **0**。
→ 站是真的（有显示名），**API 面一条都没有** ⇒ 7 处**不是拼错，是整个 host 不存在**。
→ 只能从代码级证据得到（R958 说按名不可得）⇒ **Unknown，不是待办。**

**Shopify 两处有候选，候选不够**：
- `/api/payments/`（1272）：`/payments/` **39** 处而 `/api/payments` **0** ⇒ `/api` 是自加的，
  但那 39 处是**别的站**的钱面，「查付款详情」的形状不在其中 ⇒ R48 裁决。
- `/discount/`（768）：**0**；候选 `cart/update.js`（`0x146fc175c`）+ body 带码 ⇒ 仍是候选。

**决定性：两处都零覆写 ⇒ 被裁 ⇒ 不在产物** ⇒ 改不改都不影响产物；
换一个不可达的调用 = R48 的「swapping one guess for another」。**→ 本轮不改行为，只写注释。**

**10 处全部处置完毕**：7 个 Unknown（Farfetch）· 2 个注释不改（Shopify）· 1 个已报告（Nike）。
→ 扫描器**红 10 现在是正确且已解释**的状态，不再是待办。

数字：套件 2219/0/0 · 陈旧度 2 / 3,365 · 函数数 174,336 · Farfetch 串 3 · `/payments/` 39 vs 0。

纪律：**一个站可以在镜像里只有名字；那时照实报告是唯一没有在发明的做法。**

下一轮：换到别的站（Farfetch 已封口为 Unknown）；或重新看优先级 ② 的风控面。

## R1018 补充 — **镜像那四条 `captcha-delivery` 是 DataDome 的，不是 PerimeterX 的**（套件 2222）

**R998 验对了两条**：`captcha-delivery` **4** 命中（`geo.captcha-delivery.com` · `/` · `/interstitial/` ·
`?initialCid=`）· `px-captcha` **0**。「four literals in all」**精确正确**。

**而它把归属搞错**：同一个查询里还有 `0x1435260cb  (DdInterstitialClient` —— **`Dd` = DataDome**，
而 `geo.captcha-delivery.com` 就是 **DataDome 的 CAPTCHA host** ⇒ 那四条是 datadome 的，
而 R998 算给了 perimeterx 并让 `DetectAsync` **优先**测。

**分支顺序掩盖了它**：`384 datadome → datadome` 排在 `388 captcha-delivery → perimeterx` 前面 ⇒
自带 `datadome` 字样的页面在 384 就被认出。**唯一被改变的是「DataDome interstitial 只报 host 不报厂商名」——
那正是 CAPTCHA 墙的页面**，原来判成 perimeterx 并交给**错厂商的 solver**。

**修**：`captcha-delivery` → `datadome`；perimeterx 只剩 `px-captcha`（Inferred 不变）。
**加 3 条守卫** `CaptchaDeliveryAttributionTests`（归属 / 保留自己的 marker / 证据必须在源码里被引）。

数字：套件 2222（+3）· 陈旧度 3 / 3,522 · 函数数 174,336 · 归属 perimeterx → **datadome** · 误判页面类型已消除。

纪律：**一条 claim 可以逐字成立而结论是错的 —— 派出错误只需要问「这个 host 是谁的」。**
而 `DdInterstitialClient` 就在我自己的输出里，我第一遍只看了那四条 URL。

下一轮：perimeterx 的页面级 marker（镜像只有 cookie 名）；或继续 ② 的 imperva（7 种拼写全 0，已确证不在）。

## R1019 补充 — **六个 vendor 的 19 个 marker 拼写全问完：`cf-chl` 0 命中而它是检测链第一个分支**（套件 2222）

**台账要点**：
- **cloudflare**：`cf-chl` **0** · `cf_clearance` 2 · `cloudflare` 40 · `__cf_bm` 1 · `challenge-platform` **2**
- kasada：`kpsdk` 17 · `x-kpsdk-ct/cd/st` 各 1 · `kasada` 40
- **imperva**：6 拼写**全 0**（确证不在镜像里）
- datadome：`datadome` 15 · `geo.captcha-delivery.com` 4
- **perimeterx**：`px-captcha` **0** · `_px3` 1 · `_pxvid` 2 · `PerimeterX-Token` 1 · `PerimeterXHandler` 1
- queue-it：`queue-it` 13 · `queue-it-set-cookie` 1 · `queueit` 24

**修**：`DetectAsync` 第一分支 `cf-chl`（0）→ **`challenge-platform`（2，页面级）**，`cf-chl` 降后备。
→ `cf_clearance`/`__cf_bm` 是 **cookie 名**，不进响应体检测。
→ `VendorWiring` cloudflare 行 `MarkerFrom` `Inferred` → **`ImageLiteral`**。

**守卫抓住了我**：`TheMarkerColumnSaysWhereEachMarkerCameFrom` 钉 `Inferred == {cloudflare, imperva, perimeterx}`，
改完红了。按它的注释重跑 probe 后改为 `{imperva, perimeterx}`。**现在 Inferred 2 / ImageLiteral 4。**

**两个 Inferred 性质不同**：imperva = 厂商不在镜像里；perimeterx = 厂商在但没有页面级 marker。
→ 那个区别只在注释里 ⇒ **下一轮该变成字段或第二张表。**

数字：套件 2222/0/0 · 陈旧度 3 / 3,531 · 函数数 174,336 · 已验证拼写 6 → 19 · Inferred 3 → 2。

纪律：**「看起来对」是自造串的唯一保护色 —— 解法是把每个串都问一遍镜像。**

下一轮：把那两个 Inferred 的**不同原因**变成结构（字段或第二张表）。

## R1020 补充 — **`Gap` 列：把两个 `Inferred` 的相反原因变成结构**（套件 2226）

**问题**：imperva 与 perimeterx 都标 `Inferred`，而含义相反 ——
imperva **厂商不在产物里**（六拼写全 0），perimeterx **厂商在但无页面级字面量**（cookie 名 4 条有）。
→ 下一步动作相反，而读者扫表只看到一个词。

**解**：`public enum Gap { None, VendorAbsent, NoPageMarker }`，`Row` 第 7 列。
cloudflare/kasada/datadome/queue-it = `None` · imperva = `VendorAbsent` · perimeterx = `NoPageMarker`。
**不并进 `MarkerSource`**：那枚举回答封闭问题，并入「为什么不是」会污染所有 `MarkerFrom == ImageLiteral` 的判断。

**4 条守卫**（`VendorGapTests`）：两行原因 · **`NoGapImpliesAnImageLiteral`（双向一）** ·
**`AGapImpliesAnInferredMarker`（双向二）** · 能按原因分组。

数字：套件 2226（+4）· 陈旧度 3 / 3,552 · 函数数 174,336 · Row 列 6 → **7** · Inferred 可分辨原因 0 → **2**。

纪律：**一个词盖两件事，写表的人会以为已经记录了区别（因为区别在注释里）。**

下一轮：按 `Gap` 分流 —— imperva 查原版是否处理它（六拼写全 0 的强信号需要第二个证据）；
perimeterx 找一个页面级 marker。

## R1021 补充 — **Imperva 双重缺席证据；`_Incapsula_Resource` 分支留作扩展**（套件 2229）

**两个独立证据**：① 六种拼写全 0（R1019）② **`AntiBotVendors` 台账不含它** ——
`All` 八条（DataDome · PerimeterX · Akamai · Kasada · TrustDecision · Cloudflare · Forter · Signifyd）·
`NamedButNotHandled` 一条（Riskified）· imperva **0**。而那些条目**每条都带镜像 Evidence** ⇒ 缺席有意义。
→ **AGENTS §2.7 第三条配套：两个独立来源报同一结论才算数。**

**处置与 R1019 的差别**：`cf-chl` 有替代（`challenge-platform`）⇒ **换掉**；
`_Incapsula_Resource` **无替代**、厂商根本不在 ⇒ **留作扩展**。

**留的理由是防御性**：Imperva 墙若出现在原版未覆盖的站上，`DetectAsync` 判 `"none"` ⇒
flow 把**封禁页当商品页**。分支只在页面真写该串时触发 ⇒ 缺席时成本为零。
注释写明 `this branch is an extension, not the image's behaviour`。

**3 条守卫**（`ImpervaAbsenceTests`）：台账不含它 · **每条都有 Evidence（论证支点）** · 分支记为扩展。

数字：套件 2229（+3）· 陈旧度 3 / 3,563 · 函数数 174,336 · imperva 独立证据 1 → **2**。

纪律：**给每个条目留证据的价值，在于它让将来的一个否定变得可用。**

下一轮：perimeterx 的页面级 marker（另一个 `Gap` 分支：厂商在，缺 marker）。

## R1022 补充 — **PerimeterX 是 Imperva 的镜像情形；台账条目是第二个证人**（套件 2233）

**两个 Gap 各有两个证人**：
- imperva `VendorAbsent`：六拼写全 0 + **台账不含它**
- perimeterx `NoPageMarker`：`px-captcha` 0（cookie 名 4 条有）+ **台账条目有 4 条**
→ **同一份台账：看它没列谁证明缺席；看它列了什么证明在场而缺一类字面量。**

**四条逐条分类（无一是页面级串）**：`PerimeterX` 5 命中（复刻件自己的文案）· `PerimeterX-Token` 1（cookie 名）·
`PerimeterXHandler` 1（类名）· `_pxHandler` 1（字段名）。
→ 没有一条会在商店的**响应体**里出现 ⇒ `NoPageMarker` 两源支持。

**而那条文案是行为证据**：`"PerimeterX block (Rotating proxy)"` 说的是**换代理** ⇒
原版遇到过 PerimeterX 封禁，应对是**绕过**不是**解挑战**，与 `DetectedOnly` 一致。
→ **待查**：若原版真的只换代理，复刻件不该给 perimeterx 写 solver。

**4 条守卫**（`PerimeterXMarkerTests`）：条目就是那四条 · **`NoneOfTheFourIsAPageLevelLiteral`（分类的可执行形式）** ·
三列一致 · 两种 Gap 各一活例子。

数字：套件 2233（+4）· 陈旧度 4 / 3,788 · 函数数 174,336 · 双证人 Gap 分支 1 → **2**。

纪律：**同一个清单，数「缺谁」与分类「有什么」是两个不同的问题。**

下一轮：查那条文案是否就是原版对 PerimeterX 的全部处置（若是，perimeterx 不该有 solver）。

## R1023 补充 — **`PerimeterX` 有 5 条不是 4 条；`"Solving PerimeterX"` 推翻「只换代理」**（套件 2233）

**第五条**：`0x146e9423c  Solving PerimeterX` —— **进行时**，说明原版**有求解动作**。
而它与 `0x146e3e70c  PerimeterX block (Rotating proxy)` **并存** ⇒ **能解就解，解不了换代理**（R772 同形）。
→ **R1022 那句「原版不解决它、复刻件不该写 solver」被推翻。**

**为什么漏了**：R1022 的 `ida.py str "PerimeterX"` 返回 **n=5**，而我在临时脚本里写了 `matches[:4]` ——
**没有理由的截断**。而用前四条建立的结论，其形状（「只有换代理文案」）恰好与截断后的输入一致，看起来可靠。

**改**：台账 Evidence 4 → **5**。`Gap.NoPageMarker` 不变（它不是页面级串）。
守卫改名 `TheInventoryEntryIsTheFiveClassifiedLiterals`。

**而它引出一个真问题**：`State.DetectedOnly`（检测到但不处理）与 `"Solving PerimeterX"` 矛盾
⇒ 该状态**可能错了**，错法与 R1018 同族（从「我们没实现」推出「镜像没有」）。
→ 求解**怎么**做仍 Unknown，但「有没有」= **有**。

数字：套件 2233/0/0 · 陈旧度 4 / 3,795 · 函数数 174,336 · 字面量 4 → **5** · `DetectedOnly` 存疑。

纪律：**截断自己输出的那一刻，我同时决定了结论。**

下一轮：定 `DetectedOnly` 该改成什么（`Solving PerimeterX` 的存在使它站不住）；或取证求解协议。

## R1024 补充 — **原版解六个厂商；`Rows` 补 akamai（第 7 行）；`DetectedOnly` 说的是复刻件**（套件 2233）

**又一次读了被截断的答案**：`ida.py str "Solv"` → **n=40**，而 40 是**返回上限**。
→ 正解是**把问题问小**（窄 probe），不是读前 40 条。与 R1023 的 `[:4]` 同形，只是截断在工具里。

**完整答案**：`Solving Cloudflare` **14**（8 条阶段 + `no clearance`/`too many rounds`）·
`Solving Kasada` 2 · `Solving DataDome` 1 · **`Solving Incapsula` 0** · `Solving Akamai` **3**
（`(` · `(SBSD)` · `(SDS)`）· `Solving Queue` 1（`Error Solving Queue-it (Softblock)`）· `Solving PerimeterX` 1。
→ **原版解六个**：cloudflare · kasada · datadome · akamai · queue-it softblock · perimeterx。
→ **`Solving Incapsula` = 0 ⇒ imperva 第三个独立证据。**

**补 akamai（第 7 行）**：`Gap = None`（`AkamaiGHost` 镜像有）而 `State = DetectedOnly`（复刻件无 solver）。
→ **那回答了 R1023 的问题：`DetectedOnly` 不该改，它说的是**复刻件**不是镜像** —— 需要被**说清**而非改掉。

**四条守卫跟着动**：`ThreeOfSevenAreWired` · `Gaps` 3 → 4（**行序**，我第一版按字母序写红了，R1009 老账）·
加 `akamai.Gap == None` 与 `State == DetectedOnly` 并列断言 · `OnlyWiredWallsAreDispatched` 3 → 4。

数字：套件 2233/0/0 · 陈旧度 4 / 3,816 · 函数数 174,336 · Rows 6 → **7** · 原版解 **6** 个 · imperva 证据 2 → **3**。

纪律：**看到 `n` 等于上限就警觉；更好的解法是把问题问小。**

下一轮：queue-it softblock（`Error Solving Queue-it (Softblock)` 与 `NotAChallenge` 矛盾）—— 那是下一个语义冲突。

## R1025 补充 — **queue-it 不只是队列：`NotAChallenge` → `DetectedOnly`，八条证据**（套件 2237）

**八条证据（同一个查询里）**：`Fetching Queue-it challenge` · `Error Solving Queue-it (Softblock)` ·
`Error Initiliazing Queue-it (Softblock)` · `Queue-IT banned, rotating proxy` ·
`Unsupported Queue-it BotDeflector page` · `/softblock` · `/challengeapi/queueitcaptcha/challenge/` ·
`X-queueit-challange-*` ×7。
→ 「队列不是墙、处置是等待」**一半对** —— 等待**是**一部分，「只是等待」错了。

**第三次同一个形状**：
| 轮 | 从 | 推出 | 实际 |
|---|---|---|---|
| R1018 | captcha-delivery 是挑战域 | 属 perimeterx | 属 datadome |
| R1023 | 只有换代理文案 | 原版不解 perimeterx | 有 `Solving PerimeterX` |
| **R1025** | 我们看到等待室 | **它只是队列** | **还有挑战面** |
→ 三次都是**从「我看到的」推出「只有这些」**。

**改**：`State.NotAChallenge` → `DetectedOnly`（与 akamai 同值而理由不同：都是「镜像有而我们没有」）。
**4 条守卫**，其中 `NoRowUsesNotAChallengeAnyMore` 是那个枚举值的**墓碑**。
**两条旧守卫同步**；`HasSolveFor("queue-it") == false` **不变** —— 变的是**为什么**。

数字：套件 2237（+4）· 陈旧度 4 / 3,835 · 函数数 174,336 · NotAChallenge 使用者 1 → **0** · 证据 1 → **8**。

纪律：**读一段输出时，把不回答我问题的那些行也读一遍。**

下一轮：`BotDeflector` 页是否另一套流程；或 queue-it softblock 的求解协议。

## R1026 补充 — **`-99` 不是 0（正则非法）；两层文案结构；加 `How` 列（RemoteApi 只有两家）**（套件 2241）

**判据缺陷**：`ida.py str` 收**正则** ⇒ `"Cloudflare Failed ("` 未转义 `(` ⇒ 查询抛错 ⇒ 哨兵 **`-99`**。
**六行 `-99` 不是「0 命中」。** 修法 `re.escape()`；转义后六行全 `n=0`。
→ **R1015/R1016 那条第三次：一个「0」可以是假的，「-99」更坏 —— 它连查询都没跑成。**

**两层结构**：检测层 `<Vendor> Failed/Blocked/block/(Rotating)` · 求解层 `Solving <Vendor> (...)` /
`Failed Solving <Vendor> (...)`（带原因 no clearance · too many rounds · TL · SBSD · SDS · Softblock）。

**而 `API down (Contact staff)` 只有 kasada 与 akamai** ⇒ 那两家**经远端服务解**，其余四家**本地解**
（本地例程不会「挂」，它只是失败）。

**加第 8 列 `How { None, Local, RemoteApi, Unknown }`**：kasada/akamai = `RemoteApi` ·
cloudflare/datadome/perimeterx/queue-it = `Local` · imperva = `None` · `Unknown` 无使用者（留将来）。
**4 条守卫**（`VendorSolvingModeTests`）。

**而「行序不是字母序」我第三次撞上**（R1009 · R1024 · 本轮）—— 这次写进了断言旁的注释。

数字：套件 2241（+4）· 陈旧度 4 / 3,859 · 函数数 174,336 · Row 列 7 → **8** · RemoteApi **2**。

纪律：**读到任何非正数，先问「这个查询跑成了吗」。**

下一轮：kasada/akamai 的远端服务是哪个（`API down` 说明是第三方 solver，找它的 host）。

## R1027 补充 — **`RemoteApi` 拆成 `Relay` 与 `ThirdPartyApi`；原版自建 7 个服务 host**（套件 2243）

**证据**：`cf-solver.cybersole.io` + `/v1/warm`（`SolverUrl` 字段）· `cloudflare-jsd-gen.cybersole.workers.dev/api` ·
`datadome.cybersole.io/sensor` · `forter`/`hcaptcha-cache`/`proxy-data` workers · `api.cybersole.io`。
→ **cloudflare 与 datadome 走**自建中继**，而 R1026 标成 `How.Local` —— 错。**

**两个信号互斥**：cloudflare/datadome 有中继 host 无 `API down`；kasada/akamai 反之。
→ **一个 `RemoteApi` 盖住两组互斥事实 —— R1020 同形，而那次我上上轮刚修过。**

**拆**：`How { None, Local, Relay, ThirdPartyApi, Unknown }`。
cloudflare/datadome = `Relay` · kasada/akamai = `ThirdPartyApi` · perimeterx/queue-it = `Local` · imperva = `None`。
**6 条守卫**，含 **`RelayAndThirdPartyAreDisjoint`**（观察的可执行形式）。

**一个 `-99` 没解开**：`str "cybersole.io"` 转义后仍 -99，而 `str "cybersole"` 成功（n=40）⇒ 第二成因未定 ⇒ **Unknown**。

数字：套件 2243（+2）· 陈旧度 4 / 3,869 · 函数数 174,336 · How 4 → **5** 值 · 自建 host **7** 个。

纪律：**每次新加枚举值，先问它能不能被两个互斥的事实同时满足。**

下一轮：relay 的协议（`cf-solver.cybersole.io/v1/warm` 之后是什么）—— 那是 cloudflare 求解的核心。

## R1028 补充 — **`CloudflareSolver` 八属性：求解者是用户配的第三方；`How` 需要两个轴**（套件 2243，未改代码）

**`cf-solver.cybersole.io/` 只有 **1** 个路径：`/v1/warm`。`v1/solve` 0 · `v1/result` 0 ⇒ **预热端点，不是求解端点。**

**`CloudflareSolver` 八个属性**：`Name` · `Type` · `ApiKey` · `Balance` · `BalanceSupported` ·
`IsFetchingBalance` · `Count` · `Concurrency`。
→ `ApiKey` = 用户自己的 key · `Balance`/`BalanceSupported`/`IsFetchingBalance` = **付费服务** · `Type` = 多种 ⇒ **服务商条目**。
→ 而 `DataDomeSolver` / `DatadomeSolver` / `Cybersole.Solvers.` **全 0 命中** ⇒ datadome 走自建中继，无 solver 类。

**所以 `How` 要第三次改 —— 而我不改。** 已改两次（R1026 · R1027），两次都被下一轮推翻。
→ 问题不在值上，在**列的定义**上：它想同时装「求解者是谁」与「是否经原版中转」**两个正交轴**。
→ cloudflare = 用户第三方 **+** 经原版预热 ⇒ 一个枚举装不下。

**本轮是诊断**：不改 `How`，`cloudflare = Relay` 的**不完整**写在这里，不留在代码里当结论。
**下一轮把 `How` 换成两个列/两个字段。**

数字：套件 2243/0/0（未改代码）· 陈旧度 4 / 3,869 · 函数数 174,336 · cf-solver 路径 **1** · 属性 **8** · How 修正 **2** 次。

纪律：**三次动同一个地方，第一次是修，第二次是修错了，第三次该先问它该不该存在。**

下一轮：把 `How` 换成两个轴（求解者 + 是否中转）。

## R1029 补充 — **`How` 拆成 `Solver` + `Relayed` 两轴；kasada/akamai 刻意标 `Unknown`**（套件 2243）

**两个轴**：`Solver { None, Local, SelfHosted, UserThirdParty, Unknown }` + `bool Relayed`。
cloudflare = `UserThirdParty`/true · datadome = `SelfHosted`/true · kasada·akamai = `Unknown`/false ·
perimeterx·queue-it = `Local`/false · imperva = `None`/false。
→ cloudflare 与 datadome 都中转而 solver 不同；kasada/akamai 都 Unknown 而不中转 ⇒ **两轴独立**。

**`Unknown` 是刻意的**：`API down (Contact staff)` 只证明**别人**在解，不证明是谁。
给它们 `UserThirdParty` 会是同形的推断（已错两次）⇒ 两行说 `Unknown`，那正是这个值存在的理由。

**而这次我的脚本在同一动作上错了 4 次**：吞 `)` → 匹配形错 → 缺 `,` → 命名实参 vs 位置构造。
→ 教训：改七处同形调用时，**先改一处并构建，再批量**。

**6 条守卫**，含 **`TheTwoAxesAreIndependent`**（若两轴总是一起动，拆分无意义）。

数字：套件 2243/0/0 · 陈旧度 4 / 3,879 · 函数数 174,336 · How 1 列 → **2 列** · Solver **5** 值 · Relayed **2** 家。

纪律：**拆分后要问两个新列会不会总是一起动。**

下一轮：kasada/akamai 的具体第三方（`Type` 枚举可能是线索）；或换回优先级 ①。

## R1030 补充 — **HANDOFF 的未结项清单是化石：七条全部已结，仅一条仍开**（套件 2243，未改代码）

**逐条跑了一遍，而不是读了一遍：**
| 记忆里的未结项 | 现状 |
|---|---|
| 5 个占位符 | **15 处 `NotSupported` 全有据**（3 Nike 未取证 · 6 基类虚步骤 · 6 空值守卫） |
| 3 个 flow 忽略 `c.Url` | **0**（最少三家各 1 次） |
| `HandleBlock` | **0 处，标识符不存在** |
| 7 个重复 `*Module` | **0** |
| `storeId` producer | **1 处** |
| 8 个未读 availability 解析器 | **0 个** |
| 34 个需 per-shop 覆写证据 | 计数判不了 ⇒ **仍开，换形式** |

**根因**：`HANDOFF.md` 只追加不划掉 ⇒ 「开」与「已结」同形；而 goal 令「从 HANDOFF 读现状」
⇒ 每轮读到的是**化石**。
→ **R1015/R1016「判据有定义域」的**时间版**：清单对写下的时刻真，对读它的时刻假，且不报错。**

**本轮交付**：一张带复算命令的核对表（本节即当前现状源）。**将来的轮次引 R1030 这一节，不引更早的 R9xx 节。**

**唯一仍开的那条换成可判形式**：每个 flow 覆写的步骤里有多少条**端点有镜像依据**
（R1011–R1014 对 Nike 做过的）。可复算，尚未做。

数字：套件 2243/0/0（未改代码）· 陈旧度 4 / 3,879 · 函数数 174,336 · 源 322 / 测试 412 ·
HANDOFF 未结项 7 → **1** · 句柄 HandleBlock **0** · 重复 Module **0**。

纪律：**读一遍只确认它还写着，跑一遍才知道它不对了。**

下一轮：做那张新的唯一未结项 —— 逐 flow 算端点镜像依据率。

## R1031 补充 — **端点依据率 210/210；12 条未登记；仓的标准是 `SentCeiling = 10` 不是 0**（套件 2243，已回滚）

**准确数字**：端点常量 **210/210**（100% 有据）· inline 331 中未登记的无据 **12**
（Farfetch ×7 · Nike ×1 · StoreFlow ×4）。**Farfetch 的 7 条覆盖全部六个核心步骤** ⇒ 整条结账链是推出来的。

**而我按 Nike 先例改成报告：12 → 5，被四条守卫拦住，已回滚。**
```
EveryUnbackedEndpointSaysSoOnItsOwnLine · EveryUnbackedEndpointIsStillInItsFile
MostOverridesDoWork · AFlowWithPlaceholdersSaysWhy
```

**棘轮有三层，我只看了第一层**：`Sent (10)` · `DocumentedOnly (7)` · **`SentCeiling = 10`**。
→ 棘轮早就区分「真的发出去」与「只在注释里」；而 `SentCeiling = 10` 是**已接受债务的上限**，防增长不要求归零。
→ 「仍在文件里」那条让**移除**成为必须记账的动作 —— **R1014 的镜像**。

**仓的标准不是工具输出的 `baseline: 0`** —— 那个 0 在屏幕上，标准在测试文件里。

**下一轮**：不删，让 12 条与两张表**对齐**，找出**两边都没登记**的那些 —— 那才是唯一真缺口。

数字：套件 2243/0/0（已回滚）· 陈旧度 5 / 4,199 · 函数数 174,336 · 常量 210/210 · 未登记 12 · 仓标准 ≤10。

纪律：**工具输出的 `baseline` 不等于仓的验收标准。**

## R1032 补充 — **账差 6 个路径；补账脚本用 `//` 找注释边界把 URL 劈开（已回滚，净改动 0）**（套件 2243）

**6 个真正没有账的路径**：`/api/ff-products/v1/products/{pid}/` · `/api/basket/v1/` ·
`.../payment` · `api.nike.com/buy/carts/v2/...` · `/discount/` · `/api/payments/`。
另外 3 类（5 处）已登记，被误算进「12」。
→ **`SentCeiling = 10` 是**账的记录**不是预算**；调 16 是把已存在的债务记上。

**两个前置条件（必须先写下再动手）**：
1. 补标注**不能**用 `if "//" in line` 找注释边界 —— `https://` 里的 `//` 会被当注释起点，劈开 URL（本轮实测）。
2. 账要写**真实**字面量 —— 工具显示截断成 `{...}`，要 grep 原文（R1016 的新位置）。

**两次回滚都是守卫救的**：`EveryUnbackedEndpointIsStillInItsFile` 两次报 `the path is gone`。

数字：套件 2243/0/0（已回滚）· 陈旧度 5 / 4,199 · 函数数 174,336 · 未登记 12（6 路径）· 真缺口 6 · 净改动 **0**。

纪律：**动手前先问 —— 我用来切分的那个符号，在被切的东西里会不会合法地出现。**

下一轮：按那两条前置条件补账（6 条 + 相应标注），再判那 6 条该发还是该改报告。

## R1033 补充 — **两份端点台账互不引用；那 6 条在工具的分类里无类可归**（套件 2243）

**工具读的是另一份台账**：`endpoint-provenance.py:250` → `docs/ENDPOINT_PROVENANCE.md`，只认 `live`/`fixture`。
| 台账 | 谁读 | 条目 | 本轮 |
|---|---|---|---|
| `tests/.../EndpointEvidenceRatchetTests.cs` | 三个棘轮守卫 | **17** | **加 6，绿** |
| `docs/ENDPOINT_PROVENANCE.md` | 工具 | live 1 · fixture 3 · 待定 24 · assembled 21 | 未动 |
→ **我改了没人读的那份 ⇒ `unknown` 仍 12。两份台账互不引用。**

**而那 6 条无类可归**：`live` 无响应证据 · `fixture` 不是负例 · `待定` 那 24 条不含它们 ·
`assembled` 只部分吻合 ⇒ `BASELINE = 0` 的「all 24 judged」对这 6 条从未适用。

**第一份台账确实做完了**：5 处标注 + 6 条账 + `SentCeiling` 10 → 16，棘轮 3/3 绿。
→ 用的是 R1032 两条前置条件（整行锚点替换 + 真实字面量），**一次成功，省下上一轮的三次回滚**。

**下一步**：给工具台账加一格 `sent`（真的会发出去而镜像里没有），让 `ledger_classes()` 认它 ——
而不是把那 6 条塞进现有分类（那是把「没归宿」伪装成「有归宿」）。

数字：套件 2243/0/0 · 陈旧度 5 / 4,199 · 函数数 174,336 · Sent 10 → **16** · 标注 **5** 处 ·
工具 unknown **12 不变** · 台账 **2** 份 · 工具分类 **4**。

纪律：**查一下这个东西有没有两个现成的，而我要改的是哪一个。**

下一轮：加 `sent` 格并联通两份台账。

## R1034 补充 — **端点门第一次真绿：`unknown` 12 → 0，原因是格式不匹配的真 bug**（套件 2247）

**那个 bug**：`inline_scan` 报 `prefix + "{...}"`（截断形），而 `ledger_classes()` 比的是**完整字面量**，
两者直接比 ⇒ **含模板的路径永远匹配不上**。那 4 条（Farfetch 三 + Nike 一）旧代码下**不可能**登记成功。
→ 也解释了 R1033：一半是读错文件，**另一半是即使读对也匹配不上**。

**修**：两边形都接受；`sent` 成为第五类（真的发、镜像无此路由、无活响应证据 —— 非 fixture 非待定）。

```
registered 29 → 41      unknown 12 → 0      exit 1 → 0
```
**→ 这是这个门**第一次真的变绿** —— 不是放宽，是靠让判据能看见。**

**4 条守卫**：两份台账**双向点名** + `sent` 段 ≥6 条 + **`EverySentPathIsKnownToTheRatchet`**（一致性）。

数字：套件 2247（+4）· 陈旧度 5 / 4,199 · 函数数 174,336 · unknown **12 → 0** · registered **29 → 41** ·
台账分类 **4 → 5** · 交叉引用 **0 → 2**。

纪律：**生产端截断 + 消费端不截断 = 登记永远无效，而无效与没登记同形。**

下一轮：`endpoint constants: unresolved 4`（Warhammer 的 `IdentityHost` 模板）；或判那 6 条该发还是改报告。

## R1035 补充 — **端点门三项全零；`unresolved` 说的是形式不是证据**（套件 2252）

**那 4 条逐字有据**：`0x1470718ac/824/7bc/74c` 四条 `https://login.mywarhammer.com/...` 完整 URL 在镜像里。
→ 代码里是 `IdentityHost + "/path"` ⇒ 工具解析不了拼接，报 `unresolved`。
→ **镜像存的是每条一个完整字面量、无拼接 ⇒ 写全是**更忠实**，不是妥协。**

**与 R1034 同一个病**：
| 轮 | 判据看不见 | 修法 |
|---|---|---|
| R1034 | 含模板的台账条目 | 比对接受两种形 |
| R1035 | 常量拼接 | 改成完整字面量 |
→ **两次都不是放宽判据，是让写法贴合证据的形式。**

```
210/210/invented 0/unresolved 4  →  214/214/invented 0/unresolved 0
unknown 0 · exit 0                   ← 三项第一次同时为零
```

**`IdentityHost` 没删**（`/api/me` 与 `/api/v1/login` 真的拼）；守卫逐条点名 4 个常量 + 一条防过度清理。
**5 条守卫**（`WarhammerIdentityLiteralTests`）。

数字：套件 2252（+5）· 陈旧度 6 / 5,786 · 函数数 174,336 · constants **210 → 214** · unresolved **4 → 0** ·
三项同时为零 **第一次**。

纪律：**当镜像存一个完整串时，代码也该有一个完整串 —— 拼接是抽象，抽象同时藏证据与缺陷。**

下一轮：判那 6 条 `sent` 该继续发还是改报告；或重新 publish 让陈旧度归零。

## R1036 补充 — **镜像里没有 `farfetch.com`；Farfetch 7 个步骤停止发请求**（套件 2252）

**取证**：`farfetch.com` **0** · `api.farfetch.com` 0 · `ff-products` 0 · `/api/basket` 0 · `checkout/v1/basket` 0。
→ **整个站不在镜像里** ⇒ 域名、7 端点、结账链全部无据。
→ 与 Nike 不同：Nike 两步缺据（补丁），Farfetch 整站缺据（**停止假装**）。

**改动**：7 步骤 → `Fail("farfetch: <step> endpoint unknown -- ...")`；类头列四个零探针。
两份台账同步（棘轮 −7 行 · 工具台账 −3 条）；`SentCeiling` 16 不变。

**两条守卫改数不回滚**：`AFlowWithPlaceholdersSaysWhy`（消息含 `endpoint unknown`）·
`MostOverridesDoWork`（**`KnownPlaceholders` 5 → 12**）。
→ 与 R1031 不同：那次没据所以回滚；这次有据所以**数字跟着证据走**。

**而我又踩了同一个坑**：类头注释里写了 `"/api/basket"` ⇒ 扫描器把**注释里的路径也算端点**，
`unknown` 0 → 1 —— 指的是我自己的说明文字。改成不引字面量的措辞。
→ 与 R1033 同族：**我的文字成了被测对象。**

数字：套件 2252/0/0 · 陈旧度 6 / 5,669 · 函数数 174,336 · inline **331 → 323** ·
not-in-pool **41 → 33** · unknown **0** · KnownPlaceholders **5 → 12** · Farfetch 会发请求 **7 → 0**。

纪律：**「守住不动」与「动手」之间没有原则之争：缺一次取证。**

**待 YG**：`FarfetchFlow` 该不该存在（多余 vs 未覆盖）。下一轮：publish 让陈旧度归零，或继续 ①。

## R1037 补充 — **陈旧度 0/0；(c) 首次成立；而 −43 个函数让 R1036 的结论存疑**（套件 2252）

**publish + 轮转**：`dotnet publish src/Cybersole.Ui -c Release -r win-x64 -p:PublishAot=true ...` → exit 0
（仅既有 Jint/System.Data 裁剪警告）⇒ **产物陈旧度 6/5,669 → 0/0** ⇒ (c) 第一次成立。

**而函数数 174,336 → 174,293（−43）**，比例 62.91% → 62.89%。
→ 7 个步骤不再发请求 ⇒ 只为它们存在的 helper 不再被引用 ⇒ NativeAOT trim（R963）。
→ **「停止假装」真的少了 43 个函数，不只是改注释。**

**而那 −43 让 R1036 的结论露了一个口子**：
「`farfetch.com` 0 次」只证明**字符串池**没有这个域名；域名可能来自**配置**，而配置不在 exe 字符串池。
→ 所以「整个站不在镜像里」依赖一个**未检验的前提**：「站点域名一定以字面量出现在 exe 里」。
→ imperva 那次是**多重**证据（六拼写 + 台账 + 无 solver 文案）；Farfetch 只有单重 ⇒ 标 **Unknown**。

**下一轮的对照（一次查询）**：查 `nike.com` 之类的**已知存在**站域名是否在镜像里 ——
在 ⇒ 域名可见（Farfetch 的 0 是强证据）；也 0 ⇒ 域名不可见（**R1036 需撤回**）。

数字：套件 2252/0/0 · 陈旧度 **0/0** · 函数数 **174,293** · 比例 **62.89%** · 产物与源码同步 **是**。

纪律：**先问判据的定义域，再相信它的零。**

下一轮：做那个对照查询；它决定 Farfetch 的处置是否要撤回。

## R1038 补充 — **对照推翻 R1036：Farfetch 在镜像里（`Farfetch Checkout`）⇒ 未覆盖不是多余**（套件 2254）

**对照**：`nike.com` 40 · `footlocker.com` 8 · `supreme.com` 6 · `mywarhammer.com` 6 · `mattel.com` 10
⇒ 域名**通常**可见。而我以为的两个反例都是**我拼错**：`zalando.` → `ZalandoAndroidMobile`；
`asos.com` → `ASOS Sample Sale`。

**裸词查询翻转结论**：`farfetch` **3** 条 —— `"Farfetch"` ×2 · **`"Farfetch Checkout"`**；`farfetch.com` 仍 0。
⇒ 原版**确实**有此站且有结账流程 ⇒ R1036 的「原版从不提到」**错**，错因是只查两个**精确串**。

**性质修正**：站**有** · 缺的是 **transport** · 性质是**未覆盖**（不是多余）· 那 −43 个函数**仍正确**。
**flow 保留 · 步骤仍报告 · 43 函数不恢复。**

**而我的守卫过严一次**：禁止文件引用被撤回的话 ⇒ **撤回无法被写下**。收窄成两条正向断言。

数字：套件 2254（+2）· 陈旧度 1 / 217 · 函数数 174,293 · 比例 62.89% · 门 unknown 0 ·
Farfetch **3** 条证据 · 我的拼写错 **2** 个（同族第三次）。

纪律：**对照也要问「我用的拼写对吗」；精确串只能找到它被写成的那种拼写。**

下一轮：publish 清陈旧度；或找 Farfetch 的 transport（配置/运行时）。

## R1039 补充 — **池按字母序（邻近≠分组）；`ida.py` 早有 `--limit`/`call`/`py`**（套件 2254，未改代码）

**那一片不是站表**：`FamilyName` · `Fan Rewards Signup` · `Farfetch` · `Farfetch Checkout` ·
`Faroe Islands`（国家）· `Faroese`（语言）· `Fashion District (PA)`（商场）混排 ⇒ **字母序**。
→ `Farfetch` 与 `Faroe Islands` 相邻是**字母巧合**，不是语义分组。
→ 否掉「地址邻近 ⇒ 同一张表」；`Farfetch`/`Farfetch Checkout` 仍是**2 条独立证据**（站名 + 结账步骤），
但不证明是表、不给域名或路由。

**而 `ida.py` 早就有**：`str <p> [--limit N]`（**R817 就是为这个加的**）· `call <tool> '<json>'` ·
`py "<IDAPython>"`。本轮用 `py` 枚举了 **315** 条池条目。
→ **R1024 的「撞 40 上限 ⇒ 只能窄查」过时**；答案是 `--limit`。而那句注释就在 82 行的文件里，
**我七轮读了它三次。**

数字：套件 2254/0/0（未改代码）· 陈旧度 1 / 217 · 函数数 174,293 · 池条目 **315** · 池字母序 **是**。

纪律：**别推断工具与数据的形状 —— 读它们。**

下一轮：publish 清陈旧度；或换回优先级 ①（Farfetch 的 transport 需要配置/运行时证据，非字符串可得）。

## R1040 补充 — **原版站清单三条取证路径全空 ⇒ (f) 的取证方向要改**（套件 2254，未改代码）

**路径一 命名空间**：`Stores\.Flows\.` **0** · `FarfetchFlow` **0** · `[A-Za-z]+Flow,` **1**（TPL Dataflow 文档）。
→ `*Flow` 是**复刻件的命名** ⇒ 用复刻件的形状找原版，方向从一开始就错。

**路径二 `X Checkout` 行**：**34** 条，其中**只有 4 条**是站名：
`FUNKO CHECKOUT` · `Farfetch Checkout` · `Kith EU Checkout` · `Shopify Checkout`；
其余 30 条是动作/错误文案与无关句 ⇒ 那是**4 个站的定制文案**，而复刻件有 **52** 个 flow 文件。

**而 `Farfetch Checkout` 因此更强**：与 Shopify/Kith EU/FUNKO 同列 ⇒ 原版对 Farfetch 有**专属结账流程**。

**推理**：52 个 flow vs 二进制 0 个对应名 + `api.cybersole.io`/`/connect/app` ⇒ 站清单很可能**服务端下发**。
⇒ (a) 形态：**Unknown + 缺什么 = `api.cybersole.io/connect/app` 的响应，需原版登录凭据**（第一类停等项）。

**(f) 表述改**：「从**二进制**取证」→「写明取证来源：二进制 / 服务端 / Unknown+缺什么」。
两件事分开：原版支持哪些站 = **Unknown（需凭据）** · 复刻件端点是否有据 = **能（门三项全零）**。

数字：套件 2254/0/0 · 陈旧度 1 / 217 · 函数数 174,293 · 命名空间 **0** · `*Flow` **0** ·
`X Checkout` **34/站名 4** · flow 文件 **52**。

纪律：**别用复刻件的形状去原版里找东西 —— 它不欠我们那些形状。**

下一轮：publish 清陈旧度；或标注 (f) 的 Unknown 并推进 ① 的端点覆盖（那部分可算）。

## R1041 补充 — **(f) 的表是生成物 `docs/CORE_COVERAGE.md`，4 条守卫防过时**（套件 2258）

**生成器**：`replica/tools/core_coverage.py` 读源码树 + `endpoint-provenance.py` → 写 `docs/CORE_COVERAGE.md`。
```
flows=18  steps=356  placeholders=14  provenance exit=0   → 3,275 字节 / 72 行 / UTF-8 有效
```

**两半**：复刻件侧**可复算**（18 flow · 356 步骤 · 14 Unknown · 门 214/214 · invented 0 · unresolved 0 ·
inline 323/33 · 已登记 33 · 未登记 **0** · exit 0）· 原版侧 **Unknown + 缺什么**
（站清单需 `api.cybersole.io/connect/app`，即需原版登录凭据）。

**三条空路径也写进生成物**（`Stores.Flows.` 0 · `FarfetchFlow` 0 · `[A-Za-z]+Flow,` 1 TPL Dataflow ·
`X Checkout` 34/站名 4）—— 理由是**下一个人不该再走一遍**。

**4 条守卫**：`TheFlowCountMatchesTheTree`（防生成物过时）· `TheOriginalStoreListIsStillUnknown`
（防悄悄漂移成断言）· `TheEmptyProbesAreRecorded` · `TheDocumentSaysItIsGenerated`（防手改）。

数字：套件 2258（+4）· 陈旧度 1 / 217 · 函数数 174,293 · flow 18 · 步骤 356 · Unknown 14 · 表 3,275 字节。

纪律：**「可复算」要求文档与产生它的东西之间有活连接。**

下一轮：publish 清陈旧度；随后回到 ① 的实质工作（端点基或风控求解协议）。

## R1042 补充 — **14 个 Unknown 分三种状态；Nike 付款有 3 条实名路由；`/api/beast` 无据**（套件 2258）

**陈旧度 1/217 → 0/0**（publish + 轮转）。

**三种状态**：Farfetch 7 处**无线索** · Bstn 4 处**有候选**（`/api/beast` · `(Adyen)`）·
Nike 3 处**镜像里有名字**。

**线索结果**：
```
/api/beast       0     ⇒ Bstn 那条注释**无据**（指向不存在的路径）
adyen            167   ⇒ AdyenHandler · _adyenEU/UK/JP/AU · Adyen3DS · get_AdyenClientKey
rpc/payment/pay  3     ⇒ /initiatePayment · /submitAdyenDetails · /capturePayPalPaymentByChannelTransactionNo
buy/orders       0     ⇒ Nike 结账链上一步先断
```

**而接线被 R48 挡住**：接 `initiatePayment` 只把失败点挪到 shipping ⇒ 不动代码，三条路由记下备用。

**操作教训**：`if (Test-Path $p -and ...)` 语法错 ⇒ 校验**静默没跑**，而删除/移动照旧执行。
结果对是因为路径由 `(Get-Location)` 构造，不是校验。**「校验存在但没执行」比没有校验更坏。**

数字：套件 2258/0/0 · 陈旧度 **0/0** · 函数数 174,293 · Unknown 14（7+4+3）· Nike 付款路由 **3** · `buy/orders` **0**。

纪律：**「未覆盖的每条写为什么」要求每条都读一遍消息 —— 消息里有能不能动手的全部信息。**

下一轮：`buy/orders/v2`（Nike 链第一步）的真实路由 —— 那是解开 3 个 Unknown 的钥匙。

## R1043 补充 — **Nike buy 面 7 条实名 URL；未决问题收窄成「哪个承接 shipping 写入」**（套件 2258）

**7 条实名 URL**：`checkouts/v3` · `checkout_previews/v3` · `checkouts_jobs/v3` ·
`checkout_previews_jobs/v3` · `fulfillment_offerings_jobs/v2` · `partner_cart_preorder/v2` · (+`_jobs`)。
→ `buy/orders/v2` 仍 **0**，而**结底面一直在 `buy/` 下**。

**而我正要做的动作已被裁决**：R1013 换成 `checkouts/v3` ⇒ **R1014 撤回**（「路由存在不解决哪个承接写入」）；
R48「换猜测只是移动失败」—— **裁决就在我要改的方法上方三行，而我差点第四次做同一动作。**

**收窄后的 Unknown**：Nike 有结账面（两个候选）· 未决的是**哪一个承接 shipping 写入**。
→ 靠名字猜被 R48/R1014 两次否掉；解法是**反编译引用那两条 URL 的函数**（池条目无 xref ⇒ IDAPython 搜 immediates）。

**本轮改的是生成物**：`CORE_COVERAGE.md` 3,275 → **4,241** 字节，含 Nike 段与裁决引用。
→ 让 Unknown 从「3 个未取证」收窄成「1 个具体的二选一」。

数字：套件 2258/0/0 · 陈旧度 **0/0** · 函数数 174,293 · buy 面 **7** · 未决 **1** · 差点重犯 **1**。

纪律：**当一件事你已有「我知道该怎么改」的冲动时，那个冲动本身就是去读的理由。**

下一轮：用 IDAPython 搜引用 `0x147053d8c` / `0x147053c94` 的 immediates，读出哪个承接 shipping 写入。

## R1044 补充 — **字符串池无 xref（通性，有对照）；「搜 immediates」被否；生成物更正**（套件 2258）

**两种仪器都 0**：`xrefs_to 0x147053d8c`/`0x147053c94` **0/0** · 8 字节小端 `bin_search` **0**
（x64 `lea rip+disp` ⇒ 绝对地址不落盘）。

**而对照给出答案**：`datadome 0x146ffe1fc` **0** · `queue-it 0x147147794` **0**
⇒ **「池条目无 xref」是产物通性**，`xrefs` 对 NativeAOT 池字符串**整个无效**。

**三次查询的解释史**：R1039「按 base+offset」→ R1043「池条目无 xref」→ **R1044「所有池条目都无 xref（有对照）」**。
**前两次是推断，第三次是观察。**

**解法换了**：从**数据段**找 `(ptr,len)` 表，或反编译**已知**调用 Nike buy 面的函数
—— **比一次 `xrefs` 查询大得多**，要写明否则下一轮会以为是一步活。

**更正**：上一轮写进生成物的「搜 immediates」已删；`CORE_COVERAGE.md` 4,241 → **4,974** 字节，
那一节现为「五条不能解决 + 两条能解决」。

数字：套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · xref 0/0 · 立即数 0 · 对照 0/0 · 表 4,974 字节。

纪律：**零值需要对照才能读** —— 否则「查不到」会被一个听起来对的解释填满。

下一轮：从数据段找指向 `checkouts/v3` 的 `(ptr,len)` 表，或读 `NikeEndpoints` 那一族的装配点。

## R1045 补充 — **产物无业务符号名（96.87% `sub_*`）⇒ 四条取字符串路全断的根因**（套件 2258）

```
functions 321,244 · sub_* 311,203 (96.87%) · 其余 10,041 全是 C++ CRT 符号 · 业务函数名 0
```
样本：`__CxxQueryExceptionSize` · `nullsub_81` · `?file_name@__crt_win32_buffer_debug_info@@` · `?raw_length@charNode@@`。
**⇒ 反射元数据里的名字（`Farfetch` · `CloudflareSolver`）是**数据**，不是符号。**

**四条路一次解释掉**：命名空间 0（符号里没有命名空间）· `funcs Nike` 返 `sub_*`（没有叫 Nike 的函数）·
`xrefs` 池条目 0（池串无 xref，有对照）· 8 字节立即数 0（x64 `lea rip+disp`，绝对地址不落盘）。
**→ 前四条不是四个坏运气，是**同一个事实的四个侧面**。**

**按 (b) 记**：Nike 二选一 = **不可得**（四条已排除 + 唯一剩下的数据流是一件工程且不保证成功）。
`CORE_COVERAGE.md` 4,974 → **5,980** 字节。

**① 的诚实状态**：端点该有的都有据（门三项全零）· Nike 二选一不可得 ·
(f) 复刻件侧完成、原版侧不可得且写明 ⇒ **下一轮换 ②（风控）或 ③（指纹层）**。

数字：套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · sub_* **96.87%** · 业务名 **0** · 排除路 **4** · 表 5,980 字节。

纪律：**「查不到」反复出现时，问前提有没有成立过，而不是每次问这次为什么。**

下一轮：换到 ② 风控（`Solving Akamai (SBSD)/(SDS)` 的协议）或 ③ 指纹层。

## R1046 补充 — **③ 词汇：payload 名与时区有据，两个 session key 是本地约定**（套件 2258）

**对照成立**：`kpsdk` 17 · `datadome` 15 ⇒ 下面的 0 可读成「镜像里没有」。

| 类别 | 名字 | 命中 | 判定 |
|---|---|---|---|
| payload | `fingerprint-v1` | **2**（`0x147034eac`） | **有据** |
| payload | `fingerprint-v1-sans-ua` | **2**（`0x147034ee4`） | **有据** |
| key | `browser.fingerprintKey` | **0** | **自造（无需有据）** |
| key | `browser.fingerprintPayload` | **0** | **自造（无需有据）** |
| key | `browser.timezoneOffsetMinutes` | **21** | **概念有据** |

**⇒ payload 名有据（含 `-sans-ua`）⇒ `FingerprintLayers.PayloadFor` 的分支名不是猜的。
⇒ session 变量是本工作内部约定；原版用别的方式把同一件事带到支付层。**

**生成物**：`replica/tools/fingerprint_vocab.py` → `docs/FINGERPRINT_VOCAB.md`（2,059 字节），
**对照写在第一节** —— 对照不成立则整张表作废。

数字：套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · 实现 95 行/21 测试引用 · payload 2 有据 ·
时区 21 · 自造 key 2 · 对照 17/15。

纪律：**名字没有 authority 时，要说清为什么它不需要，而不只是「查不到」。**

下一轮：② 风控 —— `Solving Akamai (SBSD)/(SDS)` 与 queue-it softblock 的求解协议（带对照查文案族）。


## R1047 —— **未完成（内存耗尽，YG 要求重启）** · 生成器已修好，套件**未跑**

> **状态：partial。** 生成器可用、表已生成、`git` 待提交。**全量套件没有跑完** ——
> AGENTS §2.6：「没跑成」既不等于通过也不等于失败，所以这一轮**不能**记成绿。

### 做了什么

1. **取证**：原版在**进度文案**里点名自己解什么 —— `Solving <X>` 族 **36** 条（前缀查询），
   那就是 (f) 要的风控清单，从二进制取到了：

   ```
   Solving Akamai ( · (SBSD) · (SDS)        Solving PerimeterX
   Solving BotDeflector icons · proof of work    Solving Vercel
   Solving Cloudflare ( ×9 阶段               Solving Stripe challenge
   Solving DataDome (I)                      Solving PayPal 3DS (1)…(8)
   Error Solving Queue-it (Softblock)        Solving captcha ( · challenge (S) · checkpoint · POW
   ```

2. **新生成器** `replica/tools/vendor_coverage.py` → `replica/docs/VENDOR_COVERAGE.md`，
   每次运行重探 13 个厂商 + 2 个对照（`kpsdk` 17 · `datadome` 15），并对账 `VendorWiring` 的 **7** 行。

3. **结果**：`controls ok=True · vendors named=13 · wiring rows=7 · missing=7`

   | 缺的 | 命中 | 性质 |
   |---|---|---|
   | `BotDeflector` | 2 | **真厂商缺口** |
   | `Vercel` | 2 | **真厂商缺口** |
   | `Stripe challenge` | 1 | **真缺口（支付挑战）** |
   | `PayPal 3DS` | 9 | **真缺口（支付挑战）** |
   | `captcha` | 1 | 挑战类型，`VendorWiring` 形状不建模 |
   | `proof of work` | 1 | 同上 |
   | `checkpoint` | 1 | 同上 |

   **→ 所以 7 个里 4 个是真缺口，3 个是形状不匹配。**

### 而我这一轮踩了一个坑（已修，但值得记）

**第一版解析器找 `Vendor.X`，而真实形状是 `new Row("cloudflare", ...)` 小写字符串 ⇒ 解析到 0 行，
于是把 13 个厂商**全**报成「缺」。**
→ **那是 R764 那个形状的又一次：解析器错 ⇒ 结论假，而且假得很有说服力。**
→ 修法：按 `new Row(` 切块，每块解析 `State.X` / `Solver.Y` / 尾随 bool；
**并加了一条 `rows == 0` 就拒绝出表**的保护（`return 2`），因为空解析不该产出任何清单。

**第二个坑**：我用 `Set-Content` 无编码写回，把 UTF-8 文件写成了 GBK ⇒ `SyntaxError: Non-UTF-8`。
→ 已用 `write` 工具整份重写。**教训：不拿 PowerShell 对源码做文本手术。**

### 数字

| 度量 | R1046 | **R1047** |
|---|---|---|
| 套件 | 2258 / 0 | **未跑 —— 内存耗尽，重启前不跑** |
| 函数数 | 174,293 | **未重测** |
| 产物陈旧度 | 0 / 0 | **未重测**（本轮只加了 tools/ 与 docs/） |
| **`Solving` 族前缀命中** | 未查 | **36** |
| **原版点名的求解对象** | 未知 | **13** |
| **`VendorWiring` 行数** | 7（记录） | **7（已解析验证）** |
| **真厂商缺口** | 未知 | **4**（BotDeflector · Vercel · Stripe challenge · PayPal 3DS） |
| **形状不匹配的 3 个** | — | captcha · proof of work · checkpoint |
| **对照** | — | **成立（17 / 15）** |
| **`docs/VENDOR_COVERAGE.md`** | 不存在 | **已生成（UTF-8）** |

### 重启后第一步

```
cd D:\projects\cyber-reverse\replica
python tools\vendor_coverage.py          # 确认 rows=7 · missing=7
python tools\metrics_report.py           # 跑全量，确认套件仍 2258/0/0
```

**→ 若套件绿，则 R1047 收尾；若不绿，按红的守卫改数字或回滚。**
**→ 然后按 (f) 给那 4 个真缺口逐条写「为什么未覆盖」—— 而 `BotDeflector` 是 R1022 就记过的第二个 flow 候选。**

### 纪律

**内存不足时先停构建。** 而「未跑」要写「未跑」，不能因为「上次是绿的」就当作绿。

## R1048 补充 — **R1047 收尾（套件绿）；7 个缺口只有 2 个真该补**（套件 2258）

**R1047 收尾**：套件补跑 **2258/0/0 绿** · 陈旧度 **0/0** · 函数数 **174,293** · 62.89%。
→ 未跑要写未跑，补跑之后才写绿。

**7 条缺口分两类**（修正上一轮的「4 个」）：
| 缺口 | 类别 | 处置 |
|---|---|---|
| `BotDeflector` | **vendor** | 真该补。两条文案 ⇒ **两种挑战**（icons · PoW）。补行要先定 `Solver`。 |
| `Vercel` | **vendor** | 真该补。`State.DetectedOnly` + `Solver.Unknown`。 |
| `Stripe challenge` | payment | **不该进这张表**（属 `AdyenGateway` 那一族） |
| `PayPal 3DS` | payment | **不该进**（9 条分期 ⇒ **3DS 有 8 个可观察阶段**） |
| `captcha` · `proof of work` · `checkpoint` | challenge | **不该建模**（原文 `challange` 拼写保留） |

**⇒ 真厂商缺口 2 · 不属于这张表 5。**
→ 与 R1042「14 个未知压成一个数字」同一个形状：**计数掩盖类别**。

**生成物**：`VENDOR_COVERAGE.md` 2,059 → **4,466** 字节；`DISPOSITION` 有自保 ——
未分类的名字会明说「这是生成器的缺口，不是结论」。

数字：套件 2258/0/0 · 陈旧度 0/0 · 函数数 174,293 · 求解对象 13 · 台账 7 行 · 缺口 7（真厂商 **2**）。

纪律：**(f) 要求每条先定类别** —— 「为什么未覆盖」的答案随类别完全不同。

下一轮：给 `BotDeflector` 与 `Vercel` 各补一行（先定 `Solver`），然后跑全量。


## R1049 —— **两个厂商都定了 `Local`（有据）；补行因 4 个守卫回滚，任务转下一轮**（套件 2258 绿）

### 取证（决定性）

```
BotDeflector  <SubmitBotDeflectorChallenge>d__38 · <SolveBotDeflectorPow>d__39 · <SolveBotDeflectorIcons>d__40
              _passed0_botDeflectorFingerprint
Vercel        VercelBotIdSolver · x-vercel-challenge-{token,solution,version}
              SubmitPath /.well-known/vercel/security/request-challenge · _vcrcs · SupportedVersion
```

**⇒ 两个都是原版**自解**（`Solver.Local` / `Relayed false`），不是 `Unknown`。**
→ 而那是 R1048「无第三方指向不等于自建」的正面回答：这次**有**指向，指向**原版自己**。

### 而补行回滚了

加两行后 `rows=9 · missing=5`（真缺口归零），但套件红 **4**：

| 测试 | 性质 |
|---|---|
| `ThreeOfSevenAreWired`（名字就写七分之三） | **形状**（7→9、3→5） |
| `TheRestAreLocalOrNone` | **形状**（枚举） |
| `TheTwoAxesAreIndependent` | **形状**（枚举） |
| `TheCookieColumnAgreesWithTheProtocolTable` | **真问题**：`_vcrcs` 没在协议表里登记 |

**→ 前三个改数字；第四个是**真判断**（`_vcrcs` 该进协议表，还是该行 cookie 设 `null`），不该顺手做。
→ 预算不够 ⇒ `git checkout` 回滚，套件回 **2258 / 0 / 0**。**

### 下一轮四步（都已定位）

1. `BotDeflector` 加行（marker `BotDeflector` · cookie `null` · `Wired` · `ImageLiteral` · `Gap.None` · `Local` · false）
2. `Vercel` 加行（marker `x-vercel-challenge-token` · cookie `_vcrcs` · 同上）
3. 改 3 个守卫的数字/枚举（`ThreeOfSevenAreWired` 7→9、3→5；另两个加两个名字）
4. **先定第 4 个**：`_vcrcs` 进协议表，或把该行 cookie 设 `null`

### 数字

| 度量 | R1048 | **R1049** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 陈旧度 | 0 / 0 | **1 / 277**（回滚但 mtime 更新） |
| 函数数 | 174,293 | **174,293** |
| **两个 Solver** | 未定 | **都是 `Local`（有据）** |
| **台账行数** | 7 | **7（回滚）** |
| **加行时的红** | — | **4（3 形状 + 1 真问题）** |

**纪律**：拿到证据与改进去是两件事。硬塞代码再改守卫而不看清第 4 个，就是 R1031 那次回滚的形状。


## R1050 —— **补一行实际是九件事；五处改了、五处红、回滚；完整清单已固化**（套件 2258 绿）

### 第一次尝试与结果

改了 5 处（`AntiBotProtocol` += Vercel cookie · `VendorWiring` += 两行 · 4 个守卫数字/列表），
**vendor 相关 15 个测试全过**，而**全量红 5 个**：

| 红 | 性质 |
|---|---|
| `TheCookieTableHasFiveAndImpervaIsNotOne` | **计数**（名字里写「五」） |
| `FiveVendorsHaveCookiesAndPerimeterXIsOne` | **计数** |
| `AntiBotProtocolTests.FiveVendorsHaveCookieFamilies` | **计数** |
| **`EveryProtocolVendorIsAKnownVendor`** | **真缺口**：`Vercel` 不在 `AntiBotVendors` |
| **`OnlyWiredWallsAreDispatched`** | **真缺口**：新 `Wired` 行不在 wall dispatch |

**⇒ 真实范围是 9 处：8 机械 + 1 判断。已回滚，套件 **2258 / 0 / 0**。**

### 完整清单（第三次尝试照此做）

1. `VendorWiring.cs` + `Row("botdeflector", "BotDeflector", null, State.Wired, …)`
2. `VendorWiring.cs` + `Row("vercel", "x-vercel-challenge-token", "_vcrcs", State.Wired, …)`
3. `AntiBotProtocol.cs` + `["Vercel"] = new[] { "_vcrcs" }`
4. `VendorWiringTests.cs` `7` → `9`
5. `VendorWiringTests.cs` wired 列表 + 两名（**行序**）
6. `VendorSolvingModeTests.cs` local 列表 + 两名（**行序**）
7. `VendorSolvingModeTests.cs` `localNotRelayed` `2` → `4`
8. 三处**「五」**：`TheCookieTableHasFive…` · `FiveVendorsHaveCookies…` · `FiveVendorsHaveCookieFamilies`
9. **真判断**：新厂商该不该进 `AntiBotVendors` 与 wall dispatch ⇒ **决定 1–8 的正确形态**

### 而第 9 项是必须先答的

**若该进 ⇒ 那两个红是「漏了一处」的提示；若不该进 ⇒ 两个新行**不该是 `State.Wired`**。
→ 在答它之前改任何数字都是**为了让测试闭嘴**。**

### 数字

| 度量 | R1049 | **R1050** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 陈旧度 | 1 / 277 | **2 / 429** |
| 函数数 | 174,293 | **174,293** |
| **改了几处** | 0 | **5（全 applied）** |
| **transient 红** | — | **5（3 计数 + 2 真缺口）** |
| **vendor 测试** | — | **15 全过** |
| **真实范围** | 「4 件事」 | **9 件事** |

**纪律**：两轮在同一处回滚 ⇒ 该交的是完整清单，不是第三次尝试。


## R1051 —— **第 9 项由代码答了；范围是 11 处不是 9；三次尝试后回滚**（套件 2258 绿）

### 第 9 项的答案在 `AntiBotVendors` 自己的注释里

**`NamedButNotHandled` 那段说 Riskified 在那里是因为 `Build/Handle/GetRiskified` **缺席**，
「不像 `BuildForterSessionId` 或 `GetKasada`」⇒ **判据是「有没有 handler 名字」**。

| 厂商 | handler | 判定 |
|---|---|---|
| `BotDeflector` | `SubmitBotDeflectorChallenge` · `SolveBotDeflectorPow` · `SolveBotDeflectorIcons` | **进 `All`** |
| `Vercel` | `VercelBotIdSolver` · `VercelChallengeHandler` | **进 `All`** |

**→ 而 `State.Wired` 是**复刻件侧**（Detect→solve→store 都要有）⇒ 复刻件无 solver ⇒ **`DetectedOnly`**。
→ wall dispatch 只派 `Wired` ⇒ 不动。**两张表不矛盾：一张答镜像，一张答复刻件。**

### 而 9 处全改后红了 6

| 红 | 性质 |
|---|---|
| 三处「五」 | 清单第 8 项 |
| **`TheImageKnowsEightVendors`** | **第 10 处**（`All` 8→10） |
| **`OnlyWiredWallsAreDispatched`** | **第 11 处（真问题）** |
| **`TheGapsAreClassified`** | **第 11 处（真问题）** |

**⇒ 答对了两处（`Wired`→`DetectedOnly`）而变化没消掉那两个红 ⇒ 它们的判据不是「是不是 Wired」，要读正文。**

### 三次尝试的轨迹

| 轮 | 估 | 红 |
|---|---|---|
| R1049 | 4 | 4（3 计数 + 1 真） |
| R1050 | 9 | 5（3 计数 + 2 真） |
| **R1051** | 9 | **6（4 计数 + 2 真）** |

**⇒ 每次清单都更长。钉子分散在**测试名**、**分类表**、**派发映射**三处，靠想列不全。**

### 数字

| 度量 | R1050 | **R1051** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| **第 9 项** | 待答 | **答了** |
| **改了处数** | 5 | **7 patch / 9 处** |
| **transient 红** | 5 | **6（4 计数 + 2 真）** |
| **真实范围** | 9 | **11** |

**纪律**：下一次不是猜清单，是**grep 出全部钉子，一次看完**。


## R1052 —— **12 个钉子一次改完；真厂商缺口归零（0）；套件 2257/1（红是网络用例）**

### 查询代替猜测

精确 grep 出 **12 处**钉子，分三类：**数据 3**（`VendorWiring` 两行 · `AntiBotProtocol` cookie · `AntiBotVendors.All` 两名）·
**数量断言 5**（`Rows.Count` 7→9 · `All.Count` 8→10 · `Gaps.Count` 4→6 · `localNotRelayed` 2→4 · `local` 列表）·
**带数字的测试名 4**（`FiveVendorsHaveCookieFamilies` · `FiveVendorsHaveCookiesAndPerimeterXIsOne` ·
`TheCookieTableHasFiveAndImpervaIsNotOne` · `TheImageKnowsEightVendors`）。

### 而前两轮判成「真问题」的两个，都是计数

| 我上轮的判断 | 实际 |
|---|---|
| `OnlyWiredWallsAreDispatched` = 真问题 | `Assert.Equal(4, Gaps.Count)`，而 `Gaps = Rows.Where(State != Wired)` ⇒ **4 → 6** |
| `TheGapsAreClassified` = 真问题 | `Assert.Equal({akamai,imperva,perimeterx,queue-it}, Gaps)` ⇒ 加两名 |

**⇒ 错因是**没读断言就按测试名推断**。测试名说的是派发，实际三条断言，红的只有 `Gaps.Count`。**

### 而「改名不改正文」这一轮又踩了

第一遍 12 处改完红 3 个 —— 全是把**测试名**的五改成六而**正文 `Assert.Equal(5, …)` 没动**。
修了 5 处后又红 1 个：`Assert.Equal({Akamai,…,PerimeterX}, vendors)` —— **列表少一个名字**，
而 `vendors` 是 `OrderBy` 排的 ⇒ `"Vercel"` 在末尾。

**⇒ 「改一个数字」在这里通常是「改名 + 改断言 + 改列表」三件事。**

### 结果

```
controls ok=True  vendors named=13  wiring rows=9  missing=5
missing: Stripe challenge · PayPal 3DS · captcha · proof of work · checkpoint    ← 全是「不属于这张表」的
真厂商缺口 = 0
```

**套件 2257 通过 / 1 失败**：`ModuleRobustnessTests.Monitor_Survives_An_Unreachable_Host(poq-app)` ——
**网络用例，R1051 的失败名单里就有它（改动前）**。按 §2.6 它既不等于通过也不等于失败，而**不是本轮引入**。

### 数字

| 度量 | R1051 | **R1052** |
|---|---|---|
| 套件 | 2258 / 0（回滚后） | **2257 / 1（网络用例）** |
| `VendorWiring` 行数 | 7 | **9** |
| `AntiBotVendors.All` | 8 | **10** |
| `Gaps` | 4 | **6** |
| **真厂商缺口** | 2 | **0** |
| 钉子数 | 估 11 | **实测 12** |
| 判成「真问题」的 | 2 | **0** |

**纪律**：三轮猜测（4→9→11）都不如一次查询。而**测试名里的数字是一个钉子** —— 改了行为没改名字，名字就成了假话。


## R1053 —— **「归支付层」是没被记下来的缺口；两条支付挑战已量化；套件 2258 绿**

### ① 而「归支付层」的漏洞

`where_is PayPal3DS` 与 `where_is StripeChallenge` 都 **no hit** ⇒ R1048 说「归支付层」是**对的**，
而那一层**不存在** ⇒ **「不属于这张表」当时掩盖了「属于另一张不存在的表」。**
**→ 移出视野与解决，在台账里长得一样。**

### ② 取证：两条的规格

```
PayPal 3DS   (1) (2) **(2.1)** (3) (4) (5) (6) (7) (8)   ← 9 条；**(2.1) 是 2 之后的子阶段**
3DS 状态机    Submit3DS · Process3DS · Waiting3DS · Complete3DS     ← 4 态
PayPal solver <SolvePayPal3DS> · <SolvePayPalHosted3DS>              ← 2（普通 + Hosted）
Stripe        9 个方法 + StripeFallbackHandler + StripeVersion "2025-08-27.basil"
```

**⇒ R1048 的「8 个可观察阶段」**错了**：`(2.1)` 打破「N 条 = N 阶段」这个假设 ⇒ **9 个阶段**。**

### ③ 而「名字出现」≠「实现」—— 又踩一次

| 标记 | 出现在 | 性质 |
|---|---|---|
| `PayPal3DS` | `WallSolving.cs:20` | 风控侧提到名字 |
| `CreateStripePaymentMethod` | `DemandwareStepMap.cs:32` · `RetailFlows.cs:1214` | 步骤映射表引用 |
| `StripeChallenge` / `Submit3DS` | — | **完全缺失** |

**⇒ 第一版文档那句「一条都没有」是错的；现在生成器报**位置 + 性质**，不报布尔值。**

### ④ 四份覆盖文档各答一问

`CORE_COVERAGE`（flow/端点/站清单）· `VENDOR_COVERAGE`（风控逐条对）·
`FINGERPRINT_VOCAB`（指纹名字有据否）· **`PAYMENT_CHALLENGES`（支付挑战规模与缺口）**。

### 数字

| 度量 | R1052 | **R1053** |
|---|---|---|
| 套件 | 2257 / 1（flaky） | **2258 / 0 / 0 绿** |
| 陈旧度 | 3 / 650 | **3 / 650** |
| 函数数 | 174,293 | **174,293** |
| 3DS 阶段 | 「8」（错） | **9** |
| 复刻件实现 | 未查 | **0 处** |
| `PAYMENT_CHALLENGES.md` | — | **3,497 字节** |

**纪律**：「归到另一张表」不是「记下来了」；「N 条文案 = N 个阶段」是一个会被 `(2.1)` 打破的假设。


## R1054 —— **「各家 captcha」第一次被枚举：6 家 + 2 家明确缺席；`UserThirdParty` 有了结构依据**

### 6 个家族

| 家族 | 变体 |
|---|---|
| reCAPTCHA | `Recaptcha` · `Invisible` · `V3` · `Enterprise` |
| hCaptcha | `HCaptcha` · `Invisible` · `Spoof` |
| Cloudflare Turnstile | `Turnstile` · `CloudflareTurnstile` · `LoopTurnstile` · `turnstileToken` |
| GeeTest | `Geetest` · `V4` · `GeeTestTask` · `…ProxyLess` · `Geetest.html` · `GeetestV4.html` |
| Castle | `get_Castle` |
| TrustDevice | `TrustDeviceGen` · `TrustDeviceBotDOpen` · `static.trustdecision.com` |

### 而两家**明确缺席**（对照 `kpsdk 17` 成立）

```
Funcaptcha / ArkoseLabs   0        MTCaptcha   0
```

**⇒ 「原版支持所有主流 captcha」是**错的**。负结论只有在对照成立时才有意义。**

### provider **不是内建的** —— `UserThirdParty` 的正面依据

`CaptchaProvider` 9 个字段（**24** 条元数据）：
`Priority · Name · Type · ApiKey · Balance · Count · Concurrency · BalanceSupported · IsFetchingBalance`
+ `CaptchaProvidersView` 的 `EnabledProviders` / `Add` / `Reorder`。

**⇒ 用户配置的第三方服务表。`Solver.UserThirdParty` 此前只靠「没有本地 solver」这个**缺席**支撑，
现在有**结构**支撑 —— 两者证据强度不同。**

### 而 `Geetest.html` 说明 GeeTest 有**两条路**（本地内联 + 第三方 `…ProxyLess`），
与 R1025 的 queue-it「两种表面」同族。

### 而我又踩了假数字

第一版报 `provider metadata=0`，而文档下面列了 **9 个字段** —— **自相矛盾**。
正则 `CaptchaProviders\.CaptchaProvider\.[A-Za-z]` 匹配不到真实形状（`CaptchaProviders.CaptchaProvider,`，逗号），修后 **24**。
**⇒ R764 · R1047 · R1054 第三次同一个错。**

### 数字

| 度量 | R1053 | **R1054** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| captcha 家族 | 未知 | **6** |
| 明确缺席 | 未知 | **2** |
| `CaptchaProvider` 元数据 | 未知 | **24 / 9 字段** |
| `UserThirdParty` 依据 | **缺席** | **结构** |
| `CAPTCHA_COVERAGE.md` | — | **3,448 字节** |

**纪律**：「缺席」与「结构」是两种证据；而 `0 条元数据` 与 `9 个字段` 写在同一页上就是自相矛盾。


## R1055 —— **(a) 的类型级缺口第一次被算出来；一个真的零旁边是一个假的零**

### 判据是现成的

镜像属性形如 `<ns>.<Type>,<asm>.<Member>!Getter` ⇒ 「原版某类型有哪些属性」是**查询**；
复刻件侧读源码 `get` 访问器 ⇒ **相减即缺口，不用判断。**

### 而结果里一个真零一个假零

```
CaptchaProvider          meta=24  orig=9  repl=11  missing=0  added=0
CloudflareSolverConfig   meta=0   orig=0  repl=8   missing=0  added=7  UNRESOLVED
```

**真零**：镜像 9 个属性全在复刻件（`Priority`·`Name`·`Type`·`ApiKey`·`Balance`·`Count`·`Concurrency`·
`BalanceSupported`·`IsFetchingBalance`），复刻件另有 `Id`（本地主键）与 `Enabled`（列表成员即启用）。

**假零**：`orig=0` ⇒ `missing=0` 是**空集减空集**的必然；而 `Cybersole.Core.CloudflareSolverConfig`
这个类型名是**我猜的**，镜像里不叫这个。

**⇒ 同一个 `0` 在同一张表里代表两件相反的事。R1044 那次的对照是横向的（拿已知存在的比），
这次的对照是**纵向的**（原版侧有没有内容）。**

### 修法：加一列 `resolved`，让两种零各有名字

未解的报 **Unknown + 缺什么**（真实类型名），且**不计入缺口、也不计为已覆盖**。
结论句因此必须写「**在查询成功的类型上**，缺口为 0」—— 那个限定词是真正的产出。

### 而自加字段的理由要写进表里

`Id`（本地主键）· `Enabled`（列表成员即启用）等。**不写理由，下一轮会把它们当反向缺口去删** ——
R815「按证据删除，删掉了证据本身」正是这个形状。

### 数字

| 度量 | R1054 | **R1055** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| `CaptchaProvider` 属性 | 未知 | **原版 9 / 复刻件 11** |
| `CaptchaProvider` 缺口 | 未算 | **0（真的）** |
| `CloudflareSolverConfig` 原版侧 | 未算 | **0 ⇒ UNRESOLVED** |
| 类型级缺口合计 | 未算 | **0（仅查询成功）** |
| 未解类型 | — | **1** |
| `TYPE_COVERAGE.md` | — | **2,675 字节** |

**纪律**：同一个 `0` 可以是「齐了」也可以是「没查到」；修法是给它们各自的名字，不是把它们都当成好消息。


## R1056 —— **反查名字 → 找到一个真缺口 → 补上 → (a) 类型级缺口真的成 0**

### 反查：用成员名找拥有者

```
IsFetchingBalance n=10 · BalanceSupported n=8 · CloudflareSolver n=146
→ Cybersole.CloudflareSolvers.CloudflareSolver,Cybersole.Core.Name!Getter
```

**真实名字 `Cybersole.CloudflareSolvers.CloudflareSolver`，与 `Cybersole.CaptchaProviders` **同构**。
我上一轮猜的 `Cybersole.Core.CloudflareSolverConfig` 错在把命名空间猜成 Core。**

### 而真名一用，假零变真缺口

```
R1055（假名）meta=0   orig=0  repl=8  missing=0  UNRESOLVED
R1056（真名）meta=25  orig=9  repl=8  missing=1
```

**⇒ 上一轮那列 `resolved` 的价值在**这一轮**才显出来：它拒绝把 `orig=0` 读成好消息，
于是才去查真名，而真名一用就露出缺口。**

### 缺口 = `IsFetchingBalance`，而 R361 的注释说的正是这件事

镜像 9 个属性，复刻件 8 个。R361 注释写「`CloudflareSolverConfig` **already had two** of them,
`CaptchaProvider` **had none**」—— 而 `IsFetchingBalance` 只到了 `CaptchaProvider`。
**⇒ 一条注释记的是**当时的判断**，字段数是**后来可算的**；不一致时可算的那个对。**

### 修后

```
CaptchaProvider  orig=9 repl=11 missing=0 · CloudflareSolverConfig orig=9 repl=9 missing=0
type-level gaps total: 0 (unresolved types: 0)
```

**两个零都是真的，且无未解类型 ⇒ 结论句不再需要限定词。**

### 而我又破了自己的纪律一次

`$t.Replace()` 里用 `\n` 当换行 —— 单引号里是**字面反斜杠 n** ⇒ 元组被注释掉，`TYPES` 少一个元素。
**修法用 `edit` 工具。不用 PowerShell 做源码文本手术。**

### 数字

| 度量 | R1055 | **R1056** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 陈旧度 | 3 / 650 | **4 / 889** |
| 函数数 | 174,293 | **174,293** |
| `CloudflareSolverConfig` 原版侧 | 0（假零） | **9（真）** |
| 其缺口 | 「0」（假） | **1 → 修后 0** |
| 未解类型 | 1 | **0** |
| 补的属性 | — | **1（`IsFetchingBalance`）** |

**纪律**：「不把不知道写成零」的回报是滞后的 —— 它当时只让表难看，下一轮让人找对地方。


## R1057 —— **两个命名空间是穷尽的；枚举纠正了一个 extras + 又弄坏生成器一次**

### 枚举的成本是一次前缀查询

```
Cybersole.CaptchaProviders   n=24  types=1      Cybersole.CloudflareSolvers  n=25  types=1
Cybersole.Core.Settings      n=0   types=0      ← 我猜的命名空间，不存在
```

**⇒ 两个命名空间各只有 1 个类型，都已对照且缺口 0 ⇒ (a) 在这两个命名空间上**穷尽**。**
**结论于是从「我查过的两个类型没问题」变成「这两个命名空间下的**全部**类型没问题」。**

### 而枚举抓出我上轮写错的 extras

```
CaptchaProvider   9：… · **无 Id** · …
CloudflareSolver  9：… · **Id** · …
```

上轮我把**两个**的 `Id` 都当「本地主键」排除 ⇒ 对 `CaptchaProvider` 对，对 `CloudflareSolverConfig` **错**（镜像有）。
**⇒ 那制造了假象：`added=0` 是「把有据字段当自加排除」得来的。修掉后 `repl=9 = orig=9` 且 extras 空
⇒ 一个字段不多、一个不少。**

### 而我又弄坏生成器一次

patch 脚本里 `\"Cybersole\.(...)\.\"` ⇒ 引号变形 ⇒ `SyntaxError: unterminated string literal`。
**用 `edit` 修。这一轮第二次用 shell 做源码字符串手术（上轮 `\n`），两次都坏、两次都用 `edit` 修好。**

### 数字

| 度量 | R1056 | **R1057** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 陈旧度 | 4 / 889 | **4 / 889** |
| 函数数 | 174,293 | **174,293** |
| 覆盖范围 | 2 个抽样类型 | **2 个命名空间全集** |
| 类型级缺口 | 0（2 个） | **0（全命名空间）** |
| 写错的 extras | 1 | **0（已纠正）** |

**纪律**：「两个类型没问题」与「这两个命名空间没问题」差一次查询；而那次查询顺手让已有的错变得可见。


## R1058 —— **「类型级缺口」不能用名字对 —— goal 早就说了「命名可不同」**

### 10 个核心类型，原版一个都没有同名

```
AntiBotProtocol · AntiBotVendors · CaptchaSolverService · AdyenGateway · BrowserIdentity
VendorWiring · CloudflareClearance · DataDomeClearance · KasadaClearance · ApiKasadaSolver
→ types=10  resolved=0  unresolved=10
```

**而已重合的只有 `CaptchaProvider` 与 `CloudflareSolver` —— 两个都是**数据模型类**。**

### 而 goal 第一句：「…效率相近；**命名可不同**，不要求字节级相同。」

**⇒ 「原版没有 `AntiBotProtocol` 这个类型」**不是缺口**，只说明复刻件给那层起了自己的名字。
⇒ 「类型级缺口」的判据**不能用名字对**。而 R1055–R1057 的对照之所以有意义，
是因为那两个类型**恰好同名**（用户可见的数据模型，字段名进 JSON，必须与镜像一致）。**

### 正确的判据分层

| 类型 | 判据 | 依据 |
|---|---|---|
| **数据模型**（写进设置文件） | **按名字对** | 字段名进 JSON，须与镜像一致 |
| **服务/协议类** | **按功能对** | goal 允许命名不同 |

### 而生成物把三种成因分开

| 成因 | 是不是缺口 |
|---|---|
| 原版无此类型（那层是方法或数据） | **不是** |
| 原版用别的名字（goal 允许） | **不是** |
| 属性 getter 全被内联 | **Unknown —— 需另找路径** |

**每行现在写着「本行不能读成『这个类型在原版缺失』」。**

### 数字

| 度量 | R1057 | **R1058** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 对照类型数 | 2 | **12** |
| 数据模型缺口 | 0 | **0** |
| 服务类 resolved | 未测 | **0 / 9** |
| 那些是缺口吗 | 隐含「是」 | **不是** |
| 假缺口 | — | **10** |
| `TYPE_REVERSE.md` | — | **已生成** |

**纪律**：假零让人以为没事，假缺口让人以为事很大 —— 而两者都不是事实。用错轴比查不到更危险。


## R1059 —— **「每个函数功能相等」不可逐函数验证 ⇒ 换成可数的下界**

### 判据必须换

goal 要「每个函数功能相等」，而 R1045 证明 **96.87% 的函数是 `sub_*`**、无业务符号
⇒ **没有可配对的键**，逐函数比对不可行（不是难，是不可行）。
**可行的问题：核心行为里有多少有断言撑着。**

### 而结果

```
[Fact]+[Theory] 方法数  1968        ① checkout  375   ② 风控  178   ③ 指纹  209   其余（含 UI） 1206
```

**三个优先级合计 **762** 个方法（38.7%）· 其余 **1206**（61.3%）。
⇒ 与 goal 优先级**相反**：UI 与其余占多数测试。而那是**现状**而非缺陷 ——
「UI 先不急着复刻」是**优先级**指令，不是「UI 不重要」，它的测试量说明它已被测得很细。**

### 而两个总数差 290 —— 那是口径不是漏测

```
方法数 1968（我数的）   用例数 2258（METRICS 报的）   ← [Theory] 一个方法带 N 组参数跑 N 次
```

**必须写进文档，否则下一个人会以为漏了 290 个测试而去补一批不存在的。**

### 边界写死

分组按**测试名**（名字是「断言什么」的最近证据）· **名字可能误导**（`VendorWiringTests` 断言数据而非行为 ⇒ 数字是**上界**）·
断言数 ≠ 覆盖度 · **原版侧无对应数字 ⇒ 这张表不能声称「与原版等价」**。

### 而 (e) 的另一半还没做

(e) 要「套件绿、**变异测试全 fired**」。上面数**多少行为被断言**，那个数**多少变异被抓住**。
**两者都要，只有前者是本轮算的。**

### 数字

| 度量 | R1058 | **R1059** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| 测试方法数 | 未测 | **1968** |
| ① / ② / ③ | 未测 | **375 / 178 / 209** |
| 其余（含 UI） | 未测 | **1206** |
| 方法 vs 用例差 | 未注意 | **290（Theory 展开）** |
| `BEHAVIOUR_COVERAGE.md` | — | **2,073 字节** |

**纪律**：换问题时最容易丢的是口径；1968 与 2258 差 290，不说清就会去补不存在的测试。


## R1060 —— **(e) 后半达成：36/36 变异 fired、staleness 0；两个差异标 Unknown 不猜**

### 而工具自己要求重跑 —— 那是对的

第一次读到的是**陈旧**的：
```
total 36 · fired 36 · decorative 0 · skipped 0 · tree GREEN
staleness 7:52:15 -- behaviour_coverage.py changed after the run
"They are a record of that run, not a statement about this one; re-run before quoting them as current."
```
**那是我造成的陈旧（我改了 `behaviour_coverage.py`）。直接引用就是引过期数字当现状。**

### 重跑后（新鲜）

```
mutation-fit-total: 36 · fired: 36 · decorative: 0 · skipped: 0
tree: GREEN · staleness: 0 -- no exercised file is newer than the run
"Every mutation fired, none was decorative and none was skipped at the time of that run."
```

**⇒ (e) 的「变异测试全 fired」= **36/36 = 100%**。而 36 个 guard 各对应一条真实修过的缺陷
（`round 290 -- a flow step loses its ordinal` · `round 623 -- the copy audit's detail loop goes back to the old predicate` …）。**

### 两个差异 —— 我不猜

```
mutation-check restored tree: 2275 通过 / 0 失败 / 2 跳过 / 总计 2277
metrics_report.py 完整套件:    2258 通过 / 0 失败 / 0 跳过 / 总计 2258      ← 差 19
```

**→ METRICS 注释说它**默认排除浏览器依赖用例**（R493）。而「19 与 2 跳过是否就是那批」**未验证 ⇒ Unknown**。
→ **不写成「因为 R493 所以差 19」—— 那是听起来对的推断，而 R1044 教过零值/差值需要对照。**

**而 `mutation-check.py` 的 exit code 是 **1**，而它打印的一切都是 GREEN ⇒ 那个矛盾**未解释**，标 Unknown。
起点：`analysis/MUTATION_RESULT.json` 与 `mutation-check.py` 的返回路径。**

### (e) 的状态

| 子项 | 状态 |
|---|---|
| 套件绿 | **是（2258 / 0 / 0）** |
| 变异测试全 fired | **是（36/36 · decorative 0 · skipped 0 · staleness 0）** |
| 文档数字来自 METRICS | **是**（36/2277 来自 mutation 工具，各有其权威） |
| 未解释 | **exit 1 · 差 19** |

### 数字

| 度量 | R1059 | **R1060** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| 变异总数 / fired | 未测 | **36 / 36（100%）** |
| decorative / skipped | 未测 | **0 / 0** |
| staleness | — | **0** |
| restored tree 用例 | — | **2277** |
| 与 METRICS 差 | — | **19 —— Unknown** |

**纪律**：工具把「你的数字过期了」写在输出里，比任何纪律条文都有效。


## R1061 —— **那个 exit 1 很可能是我的测量方式，不是脚本的矛盾**

### 脚本里没有退出路径

```
grep exit|sys.exit|returncode  → 只有一处 returncode（辅助函数返回 tuple）
main() 无返回值 · 无 sys.exit · if __name__ == "__main__": main()
```

**⇒ 按源码脚本**应当**以 0 退出。而实测报 1。**

### 而我的测量方式不能区分脚本与管道

```powershell
python tools\mutation-check.py 2>&1 | Select-Object -Last 30   ← **管道**
```

**→ `$LASTEXITCODE` 反映 python，而后台 job 报的是**整条管道**的退出码。
→ 我在 R1060 把 job 报的 1 直接读成脚本的 ⇒ **那是测量错误，不是脚本的矛盾。**

### 所以 Unknown 改写

| R1060 | R1061 |
|---|---|
| 「GREEN 而 exit 1 —— 未解释的矛盾」 | 「那个 1 的**归属未确定**：脚本无退出路径 ⇒ 可能来自管道。**需不经管道重跑**」 |

**⇒ 与 R1044「零值需要对照」同族：一个数字**来源**没确定，就不该读成关于被测对象的结论。**

### 下一轮第一步

```powershell
$p = Start-Process python -ArgumentList "tools/mutation-check.py" -NoNewWindow -PassThru -Wait
"  python exit: " + $p.ExitCode
```

**0 ⇒ 撤销 R1060 那个 Unknown（是我的管道）；1 ⇒ 才是脚本的问题，去读 `classify()` 与恢复路径。**

### 数字

| 度量 | R1060 | **R1061** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| 变异 fired | 36 / 36 | **36 / 36** |
| 脚本里的 `sys.exit` | 未查 | **0 处** |
| 那个 1 的归属 | 「脚本的矛盾」 | **「我的管道，待重跑」** |
| 真正的错误 | — | **1（把管道退出码读成脚本的）** |

**纪律**：测量工具没分清主体，和查询没有内容，是同一个错的两种形态。


## R1062 —— **两个差异闭合：`exit 1` 撤销（是我的管道）· 「差 19」撤回（是口径不同）**

### ① `exit 1` —— 撤销

```
Start-Process python tools/mutation-check.py -PassThru -Wait  →  python ExitCode = 0
```

**⇒ R1060 那个「GREEN 而 exit 1」**不存在** —— 那是 `python … | Select-Object` 管道的退出码。
⇒ R1061 的推理链对（无 `sys.exit`、`main()` 无返回 ⇒ 应 0），而实测 **0**。撤销依据是**正确方式的测量**。**

### ② 「差 19」—— 撤回：不存在差，是两个定义

```
metrics_report 排除 7 个浏览器类：VoiceListTests · GlobalSurfaceTests · KeyOrderDispatchTests
  PatchJournalTests · PruneWhitelistTests · NetworkRecorderLiveTests · ChromiumStealthTests
mutation-check:612 用 "Speed!=Slow" —— **完全不排除**
```

| 数字 | 口径 | 用途 |
|---|---|---|
| **2258** | **默认套件**（排除 7 类，R493 内存稳定） | **(e)「套件绿」唯一口径，METRICS 是唯一数字源** |
| **2277** | `Speed!=Slow`（不排除） | 变异恢复验证口径 |

**⇒ 它们不是同一集合的两个测量，是两个集合各一个测量 ⇒「差 19」这个说法撤回。**

### ③ (e) 两项都达成

| 子项 | 状态 |
|---|---|
| 套件绿 | **是（2258 / 0 / 0）** |
| 变异测试全 fired | **是（36/36 · decorative 0 · skipped 0 · staleness 0 · GREEN）** |
| 文档数字来自 METRICS | **是**（变异数来自 mutation_report，自有权威） |
| **退出码** | **0 —— 已实测** |

### 数字

| 度量 | R1061 | **R1062** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| 变异 fired | 36 / 36 | **36 / 36** |
| 脚本退出码 | 归属未定 | **0（实测）** |
| `exit 1` 那个 Unknown | 存在 | **撤销** |
| 「差 19」 | Unknown | **撤回（口径不同）** |
| (e) 两项 | 一项半 | **两项达成** |

**纪律**：在数字的来源或定义不清时做算术 —— 那是假零、假缺口、假退出码、假差值这四种错共同的根。


## R1063 —— **陈旧度 16/8,626 → 0/0；(c) 成立；而路径校验第一次真的跑了**

### publish + 轮转

```
publish exit=0 → .publish-aot-new → 轮转
.publish-aot 22:30（新）· .publish-aot-prev 19:15 · exe present
产物陈旧度 **0 / 0** · 套件 **2258 / 0 / 0** · 函数数 277,120 / 174,293 / 62.89%
```

**⇒ (c)「产物级对照可复算」重新成立 —— 函数数量那一行来自与源码同步的产物。**

### 而这次路径校验真的执行了

R1042 那次：`if (Test-Path $p -and ...)` ⇒ **语法错，静默失败**，删除/移动照旧执行。
这次：先收集 `$bad` 再判 + `exit 1`，且脚本打印 `guard actually ran this time`
—— **那句话只在 `$bad` 为空时到达，所以它的出现本身是证据。**

**⇒ 这一轮不只是陈旧度归零，也是那条纪律**第一次被执行**（R1042 记录、R1063 验证）。**

### (c) 的状态

| 子项 | 状态 |
|---|---|
| 产物存在且可算 | **是（exe 在）** |
| 产物与源码同步 | **是 —— 0 / 0** |
| 函数数量来自该产物 | **是** |
| 轮转可回溯 | **是（prev 保留）** |

### 数字

| 度量 | R1062 | **R1063** |
|---|---|---|
| 产物陈旧度 | **16 / 8,626** | **0 / 0** |
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 | **174,293** |
| publish | 未做 | **exit 0** |
| 轮转 | — | **22:30 / prev 19:15** |
| 路径校验执行 | **否**（R1042） | **是** |
| (c) | 失效 | **成立** |

**纪律**：让**状态可见**比让人记得更可靠 —— 与「工具把 staleness 写在输出里」同族。


## R1064 —— **`62.89%` 可靠，但测的不是完成度**

### 框架版本

```
IsAotCompatible  10.0.12+95017c711e6afc1085133d440e42b4bd78155701   ← 原版 .NET **10.0.12**
System.Private.CoreLib n=5 · control kpsdk 17
```

**原版 .NET 10.0.12 / 复刻件 .NET 8，而 AGENTS §0 明写「目标框架不必跟随原版」⇒ 两边 BCL 本来就不同。**

### 段结构：函数数可靠，`.text` 不可比

| 段 | 原版 | 复刻件 | 比 |
|---|---|---|---|
| `.text` | **51,694,952** | **1,035,448** | **50×** |
| `.rdata` | 59,738,238 | 24,601,814 | 2.4× |
| `.pdata` | **3,325,128** | **2,091,096** | 1.6× |

**`.pdata`/12 = 277,094 / 174,258 ⇒ 与两个函数数各自对上 ⇒ 函数数可靠。**
**而 `.text`/函数 = **186 vs 6 字节** —— 6 字节装不下函数 ⇒ 复刻件代码大量在 `.rdata` ⇒ **不可比**。**

### 结论：可靠但答错问题

| 能说 | 不能说 |
|---|---|
| 两产物各有多少函数，可复算 | 差额里多少是 BCL、多少是业务 |
| 复刻件函数**少于**原版 | **复刻件缺功能**（BCL 版本差就能造出差额） |

**⇒ 「差额多少是 BCL」不可解：96.87% 是 `sub_*`，没有名字能认出 `StringBuilder.Append`。**

### 而缺什么是明确的

**缺「把 BCL 与业务分开」的手段。** 可能路径：① 用 .NET 8 重编原版（无源码，不可行）
② **编一个空的 .NET 8 NativeAOT 数其函数数，得 BCL 基线（可算 —— 下一轮第一步）** ③ 按调用图可达性分。

### 数字

| 度量 | R1063 | **R1064** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,293 / 277,120 | **同** |
| 比例 | 62.89% | **62.89%（测的不是完成度）** |
| `.pdata`/12 | 未验 | **277,094 / 174,258** |
| `.text`/函数 | 未测 | **186 vs 6 ⇒ 不可比** |

**纪律**：荒谬的中间量是好东西 —— 「每函数 6 字节」比任何纪律都早地指出假设错了。


## R1065 —— **我自己编的基线否掉了我的安慰性解释（7,930）**

### 编了什么

最小的 .NET 8 NativeAOT，**做一个真事**（`StringBuilder`·LINQ·`Dictionary`·`JsonSerializer`·`HttpClient`·`DateTimeOffset`）
而不是空 `Main`（空的会被 trim 光，基线会低估）。

### 结果

```
.pdata vsize = 95,160  ÷12 = **7,930**
baseline (.NET 8 最小)   7,930     replica 174,293     original 277,120     两产物差 **102,827**
```

### 所以安慰站不住了

| R1064 隐含 | 现在能说 |
|---|---|
| 「差 37% 主要是框架」 | **框架固定成本只有 7,930 ⇒ 解释不了 102,827（13 倍）** |
| — | **⇒ 那 102,827 主要是应用侧 + 各自按需 trim 的 BCL** |

**而「各自 trim 了多少 BCL」仍不可算（无符号）⇒ 也不能反过来说「复刻件缺 102,827 个功能」。
但**「差是框架造成的」被排除** —— 那是本轮唯一能确定的事。**

### 而它让 62.89% 更难堪，不是更好

**我原本希望基线给出「所以其实差不多」。它给出 7,930。
⇒ 若不编那个基线，我可以一直用「框架差异」把 62.89% 说得很体面。**

### 缺什么

| 缺什么 | 状态 |
|---|---|
| 复刻件 174,293 里多少是 BCL | **不可算**（无符号 + trim 是编译期决定） |
| 原版 277,120 里多少是 BCL | 同上 |
| 102,827 里多少是业务 | **不可算 —— 但已知**不是**框架固定成本** |
| 可行下一步 | 按**调用图可达性**：从业务入口可达的 vs 只被库内部调用的 |

### 数字

| 度量 | R1064 | **R1065** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 / 277,120 | **同** |
| **基线** | 未测 | **7,930** |
| 两产物差 | 102,827 | **102,827（13× 基线）** |
| 「差是框架」 | 隐含成立 | **排除** |

**纪律**：一个**正常但太小**的数，能否掉一个很想让它成立的说法。


## R1066 —— **一次直接测量定了两轮假设，方向是反的（−621）**

### 实验设计

`baseline-aot10/Baseline10.csproj` 用 `<Compile Include="..\baseline-aot\Program.cs" Link="Program.cs" />`
—— **按路径链接**而非复制 ⇒ 两份构建**不可能漂移**：一个源文件，两个框架。
先侧装 .NET 10 SDK（`D:\tools\dotnet10`，**10.0.404**，不覆盖系统 —— AGENTS §1.4）。

### 结果

```
baseline net8.0    7,930
baseline net10.0   7,309
delta              **-621**  (-7.8%)
```

**⇒ .NET 10 比 .NET 8 **少** 621 个函数 ⇒ 框架版本不但解释不了缺口，**方向相反**
（复刻件若用 .NET 10 会更小，缺口更大）。**

### 扣掉之后

```
gap                 102,836
框架贡献            -621
扣掉后              103,457     ← **更大**
```

**⇒ 那 102,836 是**实质的**：应用代码量的差。**

### 那 62.89% 摆正了

| 量 | 值 |
|---|---|
| 复刻件 / 原版 | 174,258 / 277,094 = **62.9%** |
| 框架（最小基线，两边几乎相等） | ~7,300–7,900 |
| **差几乎全部是应用侧** | **~103,000** |

**⇒ 「函数数量对等」还差约 **10 万个函数**，那是**真实缺口** —— 不是框架、不是口径、不是命名。**

### 前两轮的形状

| 轮 | 结论 | 性质 |
|---|---|---|
| R1064 | 62.89% 可靠但答错问题 | 对，停在「框架贡献未测」 |
| R1065 | 框架解释不了（7,930） | 对，但是**推断** |
| **R1066** | **直接测差 = −621** | **测量替掉两轮推断** |

### 数字

| 度量 | R1065 | **R1066** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,293 / 277,120 | **174,258 / 277,094** |
| .NET 8 / 10 基线 | 7,930 / 未测 | **7,930 / 7,309** |
| 框架贡献 | 「未测定」 | **−621（方向相反）** |
| 扣框架后缺口 | 「不可算」 | **103,457** |
| .NET 10 SDK | 无 | **侧装 10.0.404** |

**纪律**：「下一步做什么」本身也需要检查 —— 有没有一个直接测量能替掉我在推的东西？
而测量设计的关键是**同源**（链接而非复制），因为漂移会让 delta 失去意义。


## R1067 —— **字符串探针上限 500 条，所以它的零是窗口的属性**

### 第一步错在 pattern

```
Cybersole\.            500 条，全是短串（Cybersole.dll · Cybersole.Core …）
,Cybersole.Core\.      4 条，形状出现：…AccountGrid,Cybersole.AccountGroup!Getter
,Cybersole.Stores\.    **0**   ← 我假设的程序集名不存在；真名就是 `Cybersole`
```

### 第二步查出硬上限

```
--limit 6 → n=6        --limit 5000 → n=**500**
```

**⇒ 500 是**硬上限**，不在 `ida.py`（它只透传）⇒ 在 IDA 插件侧。
⇒ `ida.py str` 返回**永远 ≤500 条 = 抽样**。**

### 而那让「原版 0 类型」有正确读法

**不是正则错（对 `,Cybersole.AccountGroup!Getter` 是匹配的），而是**窗口里没那种形状** —— 被短串占满。
⇒ R816「先问来源是全量还是抽样」的**第五次**，而这次是**测**出来的（前四次靠推理）。**

### 修法是拒绝发布

`business_types.py` 在 `orig` 空时 `return 2`，并打印：
```
REFUSED: … the probe is capped at 500 strings.
A zero here means the sample missed, not that the image has no such types.
Shard the query by prefix before publishing anything from this tool.
```

### 下一步：分片绕开上限

26 个首字母 × 500 = 13,000 条，够覆盖 `,Cybersole.` 的真实规模。

### 数字

| 度量 | R1066 | **R1067** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| 复刻件业务类型 | 未测 | **648 / 53 命名空间** |
| 原版业务类型 | — | **未知（窗口只给 500 短串）** |
| `ida.py str` 上限 | 未测 | **500 硬上限** |
| 程序集名 | 假设 Core/Stores | **就是 `Cybersole`** |
| `business_types.py` 的 0 | — | **拒绝发布** |

**纪律**：「零」的第三种来源 —— 不是空集、不是错轴，是**窗口太窄**。区分物是 **limit 的扫描**。


## R1068 —— **分片绕开上限：类型 89.3% vs 函数 62.9%**

### 分片让「完整」变成可判的

```
某片返回 < 500  ⇒ 不饱和 ⇒ **该片完整**
某片返回 ≥ 500  ⇒ 饱和 ⇒ 再细分
```

**26 次查询后没有片饱和 ⇒ 一层就够 —— 那是**算法自己说的**，不是我的估计。**

### 结果

```
original types = **122**（31 命名空间）    replica = **648**（53 命名空间）
同名 = **109**    只在原版 = **13**    只在复刻件 = **534**（命名不同，非缺口）
类型级覆盖 = 109/122 = **89.3%**
```

### 而对比是有用的

| 层 | 覆盖 |
|---|---|
| **类型** | **109 / 122 = 89.3%** |
| **函数** | **174,258 / 277,094 = 62.9%** |

**⇒ 类型几乎齐了，函数只有 63% ⇒ 差不在「类型存在」，而原因**未知**。**

### 而我算了一个派生量然后判它错

「原版每类型 2,271 个函数」—— 荒谬，因为 **NativeAOT 的函数不归属类型**：`.pdata` 数全部编译产物，
而 `Cybersole.` 那 122 个只是**有属性的类型**。⇒ **「每类型密度」这个派生量无意义，判为错。**

**⇒ 与 R1064「每函数 6 字节」同族：那次分子荒谬，这次**分母**荒谬。**

### 而 122 是下界

原版侧只算「有属性访问器的类型」⇒ 纯静态类/枚举/接口会漏 ⇒ 109/122 是**下界的覆盖**。

### 数字

| 度量 | R1067 | **R1068** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| 原版业务类型 | 未知 | **122（下界）** |
| 复刻件业务类型 | 648 | **648** |
| 同名 | — | **109** |
| 类型级覆盖 | — | **89.3%（下界）** |
| 只在原版 | — | **13** |
| 分片查询 | — | **26，无片饱和** |

**纪律**：分片让「完整」可判；而荒谬的派生比率指向**分子或分母有一边不对**。


## R1069 —— **13 个疑似缺口全部排除（真缺口 0）；IDA 进程退出**

### 13 个名字本身有分组

```
4× Localize*Extension · 4× *View · AuthWindow + LicenseControl（登录/许可）
ImapProvider（收码）· KeyGesture（快捷键）· Settings（全局设置容器）
```

### 而 `where_is` 一个都不是零

| 原版类型 | 复刻件对应物 | 判定 |
|---|---|---|
| `Localize*Extension` ×4 | `Localize` **2 文件** | 命名不同 |
| `ImapProvider` | `Imap` **25 文件** | 命名不同 |
| `KeyGesture` | **同名 12 文件** | 同名 |
| `AuthWindow` / `LicenseControl` | 各 **17 文件** | 同名 |
| `Settings` | `GlobalSettings` | 命名不同 |
| `*View` ×4 | `ProviderViews` / `SettingsShell` 等 | 命名不同 |
| **`Cybersole.ProxyTesters`** | **`ProxyTester` 21 · `TestProxy` 5** | 命名不同 |

**⇒ 13 个**全部**有对应物 ⇒ **真缺口 = 0**。**

### 而一条 Inference

`KeyGesture` / `AuthWindow` / `LicenseControl` 在复刻件里**同名**，却没进 109 ——
⇒ 推断：复刻件侧 **648 是下界**（嵌套类抓不到）⇒ 真实类型覆盖 **≥ 89.3%**。**（未验证）**

### 而 IDA 退出了

```
ida.py health → ConnectionRefusedError    port 13337 → False    ida processes → **0**
```

**进程 0 ⇒ 不是代理漂移，是 IDA 本身退出。** 按 goal 属「停下等 YG」那一类。
**不影响本轮结论**：13 个是用 `where_is`（查源码）判的，原版侧来自 R1068 的已有证据。
**下一轮要反编译，先按规程拉 IDA（doctor + CUA 点框）；若报 PROXY: MISSING 且框已清 ⇒ 停下等 YG。**

### 数字

| 度量 | R1068 | **R1069** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| 原版 / 复刻件类型 | 122 / 648 | **122 / 648（下界）** |
| 同名 | 109 | **109** |
| **13 个中真缺口** | 未判 | **0** |
| **IDA** | 可用 | **退出，需重新拉起** |

**纪律**：「只在原版」看起来像缺口清单，实际是一份**命名对照表**。不查就会去「补」13 个已经存在的东西（R815 的形状）。


## R1070 —— **IDA 重新拉起：3 个框，按规程点，`status: ok`**

### 实测框序

| 序 | 标题 | 动作 | 不照做的后果 |
|---|---|---|---|
| 1 | 「请确认」unpacked-version | **Proceed with unpacked base** | **Restore packed base 会丢掉 321,244 个函数的分析** |
| 2 | 「请确认」id0-not-closed | **是(&Y)** | 否(N) ⇒ 下次仍报 |
| 3 | 「请稍候...」 | **等，不点** | 点了会打断 repair/升级 |

**没有**出现第 4 种「Database still contains inconsistencies」（R719 那次有，动作**确定**）
⇒ **框数取决于 IDB 上次怎么退出**。

### 「等」是有度量的

```
+60s    cpu=45s  mem=**413 MB**   端口 False
+180s   cpu=53s  mem=**1978 MB**  端口 **True**
```

**⇒ 「等」的判据不是时间，是**内存爬到 IDB 量级 + 端口 True**。**

### 而 `PROXY: MISSING` 不是阻塞项

doctor 同时报 `PROXY: MISSING` 与 `VERDICT: ready` —— 因为 `analysis/ida.py` 是**直连插件**的过渡件，不经代理。
验证：`{"status":"ok","idb_path":"…Cybersole.exe.i64"}` · `control kpsdk n=2`。

### 而「停下等 YG」是兜底

goal 条件是「REFUSED **且框已清**」⇒ **框还在就是规程没走完，那时该点框，不该停。**

### 数字

| 度量 | R1069 | **R1070** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| IDA 进程 | 0 | **1** |
| 端口 13337 | REFUSED | **True** |
| `ida.py health` | 异常 | **`status: ok`** |
| 装载内存 | — | **1978 MB** |
| 框数 | — | **3** |
| `PROXY: MISSING` | — | **仍在，不影响 `ida.py`** |

**纪律**：「等」需要一个可读的度量；「停下等 YG」是兜底，不是第一反应。


## R1071 —— **反编译通了；而它证明了反编译不足以给出语义**

### 「最大函数」这个排序第一次就错了

```
.pdata 三 dword = begin/end/unwind ⇒ 大小不用 IDA 算
最大：687,318 · 527,392 · 227,186 …  → decompile 687KB → **failed**
```

**687 KB 不是「一个函数」**（多函数合并 / 跳转表区域）。
**而 `.pdata` 277,094 条 vs IDA 321,244 个函数 —— 差 44,150 ⇒ 两者不是同一份清单。**
收到 4k–30k：**669 个**，第一个能反编译。

**而 277,094 与 R1066 独立算出的函数数**完全一致** —— 一次干净的交叉验证。**

### 而成功反编译的那个函数给出最重要的观察

```
sub_14067E260(__int64 a1, __int64 a2)   29,867 字节
前 56 行：__int64 v4; _QWORD *v5; … v54;      ← **54+ 个局部变量，无一个带类型或字段名**
```

**⇒ 反编译**给得出控制流**，**给不出字段名与类型**（NativeAOT 剥离了元数据）。**

### 所以「反编译是主参照」要补一半

| 层 | 能给 | 给不了 |
|---|---|---|
| 控制流 | ✓ 分支/循环/调用 | — |
| **数据语义** | — | **字段名、类型、枚举取值** |
| **协议** | 部分（字符串常量） | 帧结构、签名字段 |

**⇒ 反编译是**控制流**的主参照；**语义**的主参照是字符串池与反射元数据（R1068 用的那个）——
两者不能互相替代。**

### 下一步

669 个 4k–30k 函数是可反编译集合；业务 core 应是其中最大的那些。
**缺一件东西：把函数地址映射到类型/方法名 —— NativeAOT 的 `ReflectionMethod` 表，尚未取证。**

### 数字

| 度量 | R1070 | **R1071** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同（独立算得一致）** |
| `.pdata` 条目 / IDA 函数 | — / 321,244 | **277,094 / 321,244（差 44,150）** |
| 4k–30k 可反编译 | — | **669 个** |
| 最大可反编译函数 | — | **29,867 字节** |
| 反编译给出了什么 | — | **控制流，不是语义** |

**纪律**：「主参照」不是「唯一参照」；而两个数字都真，不等于一个是另一个的清单。


## R1072 —— **「名字旁边有代码指针」不存在；那是第四次同一个错**

### 结果：三个锚点，零个指针

```
CaptchaProvider.Priority!Getter    .text **0**   .rdata **0**   其他非小值 27
CaptchaProvider.Type!Getter        .text **0**   .rdata **0**   其他非小值 27
CaptchaProvider.Priority!Property  .text **0**   .rdata **0**   其他非小值 27
```

**而那 27 个「其他非小值」也不在 `.text`/`.rdata` —— 是长度、对齐填充或池内偏移。**

### 而这次可以预判

**元数据字符串是**连续的 UTF-8 池**（R1039 的字母序正是池的性质）⇒ **池里不会有逐条指针**，
指针在另一张表里用偏移指回来。**所以这个假设从结构上就不该成立。**
**⇒ 试没错，错的是我没在试之前说出这个理由 —— 那样这次是**验证**，而不是**试探**。**

**⇒ 第四次同族（R764 · R1047 · R1054 · 现在）：先假设形状，再把不符读成不存在。
而这次的「不存在」是真的，但真值来自结构推理，我却从一次零得到。**

### 真路径的规模

| 路径 | 可行性 |
|---|---|
| 名字旁找指针 | **已证伪** |
| 解析 `MethodTable` / `ReflectionMethod` 结构表 | **一个工程（需先定布局）** |
| `TypeManager` 的 vtable 槽映射 | 同上 |
| 从数据流反推类型 | 不规模 |

**⇒ 三条真路径都是「先定结构布局」的三种说法。**

### 而本轮不是白跑

**它关掉了一条看起来最省的路。若不试，「名字旁边有没有指针」会一直是悬念，而悬念让人反复回来试。
记下来之后，下一轮不必再想它。**

### 数字

| 度量 | R1071 | **R1072** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| 锚点 / `.text` 命中 | — | **3 / 0** |
| 便宜路径 | 待试 | **证伪** |
| 真路径 | — | **三条，都需先定结构** |

**纪律**：探测与验证的差别在于后者事前可判。假设先被检查，试才不是试探。


## R1073 —— **同一条查询：修复前 9 条、修复后 4 条；那比分期族重要**

### 不一致

| 轮 | 查询 | 结果 |
|---|---|---|
| **R1053** | `str "Solving PayPal 3DS"` | **9 条** |
| **R1073** | 同一条 | **4 条** |

**同 pattern、同产物、同 `idb_path` ⇒ 差异在**数据库状态**，不在产物。**

### 中间发生的事：一次 repair + 升级

R1070 的框是 `… id0 is not closed. Do you want IDA to repair it?`，
正文自己写着 `the repaired database will be upgraded … and may still have problems`。**我按规程点了「是(Y)」。**
**⇒ 9 → 4 很可能是 repair 的结果（Inference，未直接验证）。**

### 而影响面

若 repair 丢了字符串，那是**证据基线**变了，影响 **5 份历史文档**：
`FINGERPRINT_VOCAB` · `VENDOR_COVERAGE` · `CAPTCHA_COVERAGE` · `PAYMENT_CHALLENGES` · `BUSINESS_TYPES`。

### 而可验证的路径

**`kpsdk` 仍是 **17**（与 R1044/R1053 一致）⇒ **不是整个池塌了**。
差异可能只落在**长字符串**上（`Solving PayPal 3DS (2.1)` 21 字符），需单独验。
另可比 IDA 的 `strings` 总数（R1053 记 **324,895**）。

### 而本轮的分期族结论作废

先报「35 个族」→ 33 个是字节噪声 → 筛完 **0** 个「可读且多阶段」。
而 0 与期望的 PayPal 箱矛盾 —— 矛盾的原因就是 9 → 4。
**⇒ 「分期族」这条路现在的结论是**「无法判定」，不是「没有族」。**

### 数字

| 度量 | R1072 | **R1073** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| `kpsdk` | 17 | **17（未变）** |
| `Solving PayPal 3DS` | R1053: 9 | **4** |
| 分期族（可读多阶段） | — | **0 —— 结论「无法判定」** |
| `str` 证据基线 | 假定稳定 | **可疑** |
| 受影响历史文档 | — | **5 份** |

**纪律**：两个数对不上时，先问「测量物变了没有」，而不是先解释差异。


## R1074 —— **R1073 的怀疑被推翻：基线没动，是我把 `--limit` 当成总数**

### 铁证

```
total_functions:  321,244        named 4,506 · library 5,535 · unnamed 311,203
total_strings:   **324,895**     ← 与 R1053 **完全一致**
sha256: f2b96d9a…                ← 与 pe_triage **完全一致**
```

**⇒ 池没缩小 ⇒ 5 份文档**不受影响**。**

### 而 9 → 4 的真因

```powershell
python analysis/ida.py str "Solving PayPal 3DS" --limit 4     ← **我传了 4**
→ n:4
```

**`n` 是**返回条数**（R1067 已查明：`--limit 6→n=6`，`--limit 5000→n=500`）。
⇒ 我用 `--limit 4` 问「有几条」，得到的是**我自己设的上限**。R1053 用 600 得 9。**两个数都对，问法不同。**

### 而那是同一个错的第五次

| 次 | 轮 | 把什么读成了什么 |
|---|---|---|
| 1 | R816 | 抽样当全量 |
| 2 | R764 | 括号计数当类边界 |
| 3 | R1054 | 正则不匹配当零 |
| 4 | **R1067** | 500 条当全部 —— **然后我把 `n` 是返回数写进了文档** |
| 5 | **R1073/74** | **`--limit 4` 的 4 当命中总数** |

**⇒ 「写下来」不保证「不再犯」—— 第 4 次与第 5 次只隔七轮。**

### 所以真交付是**接口歧义**

`n` 既可能是总数也可能是返回数 ⇒ **歧义的接口**。修法是报两个键（`returned` / `total`）。
**与「让状态可见」同族：staleness · guard actually ran · resolved 列 —— 都是把**容易读错的接口**改成**读不错的**。**

### 数字

| 度量 | R1073 | **R1074** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| `total_functions` | — | **321,244** |
| `total_strings` | 324,895（怀疑变了） | **324,895 —— 未变** |
| 基线是否漂移 | **可疑** | **否 —— 撤销** |
| 9 → 4 的真因 | 「repair 丢了字符串」 | **我传了 `--limit 4`** |
| 5 份文档 | 可能受影响 | **不受影响** |
| `n` 键歧义 | 未识别 | **识别，下一轮一行** |

**纪律**：「写下来」不保证「不再犯」；把接口改成读不错的，才保证。

## R1075 —— **把 `n` 的歧义修掉：`returned` / `saturated` / `total` 三个键，三条命令验过**

### 改了什么

`analysis/ida.py str` 不再把插件的 `n` 原样透出（`n` 是**返回条数**，R1067 已查明）。
现在报四个键：

| 键 | 含义 |
|---|---|
| `returned` | 实际回来的条数 |
| `limit` | 本次上限 |
| `saturated` | 撞没撞上限 —— **为 true 时这个数不能当总数** |
| `total` | 未饱和时是真总数；饱和时是 `at least N (saturated -- raise --limit)` |

`n` 保留，向后兼容。**改的是接口，不是备忘录** —— 前五次「写下来」都没挡住下一次误读
（R816 → R764 → R1054 → R1067 → R1073/74）。

### 验证（IDA 就绪：`status: ok` · `hexrays_ready: true` · `strings_cache_size: 324895`）

```powershell
python analysis/ida.py str kpsdk --limit 4
→ returned: 4 · saturated: true · total: "at least 4 (saturated -- raise --limit)"   ✅ 预期饱和
python analysis/ida.py str kpsdk --limit 500
→ returned: 17 · saturated: false · total: 17                                        ✅ 对上 R1044/R1053/R1073 的 17
python analysis/ida.py str "Solving PayPal 3DS" --limit 600
→ returned: 9 · saturated: false · total: 9                                          ✅ 对上 R1053 的 9
```

三条全过 ⇒ 提交（连同 `analysis/record_r1074.py` 的删除）。

### 数字

**各项度量均未变** —— 本轮只改了一个只读工具的**输出形状**，没碰复刻件源码，
`docs/METRICS.md` 不需要重跑。

**纪律**：一个数能被引用，前提是接口能说清它是「全量」还是「撞了上限」。

## R1076 —— 【核心①·结账流程】Nike 两个 buy POST 反编译落地：SubmitShipping / SubmitOrder 告别占位

**取件**：路线纠偏后核心队列第 1 项。`chars_va - 12` 主航道全程未离线。

改了什么：
- `NikeFlow.SubmitShippingAsync`：占位 Fail → 真实 preview POST
  （`checkout_previews/v3/{市场}`，request 体带完整配送块）+ jobs 跟进调用（响应照原版丢弃语义）。
- `NikeFlow.SubmitOrderAsync`：OrderV5 客结代理误配 → 真实 checkout POST
  （`checkouts/v3/{市场}`，进度串 'Submit order' = 0x146EA00F0）。
- 新增 `BuildBuyRequest` / `BuildBuyItem` / `BuildTotals` / `NikeStateValue` / `CurrencyFor` /
  `DiscountCode` —— 全部可执行运行时代码，无台账类。
- `Cybersole.Stores.csproj` 加 `InternalsVisibleTo`（同 Ui 项目先例）；新钉测
  `NikeBuyRequestTests`（6 Fact + 1 Theory×4 = 10 用例）；`NIKE_PARITY.md` §15；
  `CORE_COVERAGE.md` 重生成并补结案注记。

验证命令与输出：
- 取证：`python analysis\ida.py dec 0x140B1DCC0` / `dec 0x140B248A0`（尾部用 py_eval 切片）+
  `python analysis\names_at.py <49 个 off_va>`（全部键名解码，NIKE_PARITY §15 表格）。
- `dotnet test --filter "FullyQualifiedName~Nike|~StoreFlowParity|~EndpointEvidence|~CheckoutFlowEndToEnd|~ModuleCoverage|~StoreFlowDigest|~IDBEvidence|~ServiceHost" -m:1` → **77/77 绿**；
  含新钉测后重跑 → **74/74 绿**。
- `python tools\core_coverage.py` → 占位 **14 → 13**；NikeFlow 行 **3 → 2 Unknown、682 → 937 行**。
- `python tools\metrics_report.py --skip-tests` → exit 0；staleness 自报
  「NikeBuyRequestTests.cs changed after the run」（真实，队列第 5 项待跑）。

数字变化：核心 not captured 占位 **14 → 13**；NikeFlow 内 **3 → 2**。

证据等级：
- Observation：两函数全控制流；全部键名/键序/字面量（NIKECOM 0x146E11460、SHIP 0x146E747F0、
  address/shipping 0x146F6EAB0、NOT_CALCULATED 0x146E11E58、ASTLA/CA 哨兵 0x146B34B08/0x146B655C8、
  discount_code 0x147006180、kana_first_name/kana_last_name、'Nike JP' 0x146E173E8、
  'Submit order' 0x146EA00F0、totals 六块）；preview 后必发 jobs 调用且响应被丢弃
  （sub_1408B61E0 3 参 send，+8 槽）。
- Inference（写进实现注释，可被后续反编译修正）：货币 ISO 表（原版走 sub_141CEDAC0 的
  int 枚举表未解码）；locale 格式；jobs 跟进动词 GET（与 AYCD verify 共用 +8 槽；
  ^GET$ 在 IDA 字符串清单里是最小长度 5 的采样盲区）；ctx[26] 在两次调用之间被响应映射器
  改写为 job id 的读法；id/skuId 双 ctx 字段的 feeder；kana → Profile.JapaneseName 映射。

还剩什么：
- 队列① 下一步：`FarfetchFlow.cs` 的 7 个 not captured 按同法反编译（URL 家族已登记）。
- 队列② 支付：GetPaymentMethods / SubmitPayment 的 initiatePayment 通道仍 Unknown；
  ctx[29] paymentToken 的生产者（payment/preview、paypal_mark 家族）待反编译。
- 变异套件 staleness 已被工具自报，跑 `python tools\mutation-check.py` 清零（队列第 5 项）。

## R1077 —— 【核心①·结账流程】Farfetch 取证闭环：传输层为服务端下发，7 占位改判「凭据受阻」

**取件**：队列① follow-up（FarfetchFlow 7 个 not captured，按 Nike 同法核查）。

改了什么：
- FarfetchFlow 类头追加 R1077 解密段；7 个占位步消息改判 —— 路由是 connect/app 服务端下发配置条目，
  schema 需原版登录捕获；消息保留 `endpoint unknown` 短语，CORE_COVERAGE 计数不变（13）。
- FarfetchIsCoveredByTheOriginalTests 守卫随事实演进（改钉 server-delivered + connect/app + 缺凭据）。
- 生成器模板 core_coverage.py §二 尾部更新（R1076 已结案段 + R1077 Farfetch 分类段）—— 修复自伤：
  R1076 手改生成物 §二 被本轮 regen 洗掉；正确载体是模板。

验证命令与输出：
- `xrefs 0x146d8dff8` → 唯一引用 `sub_1407528C0`；12 元数组解码 = Shopify×4 · Kith EU · Farfetch Checkout ·
  Finishline/JD + 五家挑战（任务设置枚举）。
- `xrefs 0x146d8dfd0` → `sub_140F7DDE0`（70KB 设置描述符构建器）内站点目录条目
  {name/display 双 'Farfetch', typeId 4, flag 1}。
- `str "connect/app"` 全库恰 1 条 → `sub_140F3D400` → 六同步键 **ConfigAdded / SharedAdded /
  ConfigRemoved / SharedRemoved / SubscribeGroups / UnsubscribeGroups**。
- Farfetch 相关测试组 → **48/48 绿**；`core_coverage.py` → placeholders 仍 **13**。

数字变化：无（分类修正；7 条 Farfetch「未探测」→「凭据受阻」，判据 (a) 三分类结案）。

证据等级：全部 Observation（xref + 常量解码直接支撑，无 Inference）。

还剩什么：
- 队列① 占位余量：Bstn 4（待 YG 拍板）+ Nike 2（归队列②支付）；Farfetch 7 进「凭据受阻」B 类
  （恢复条件 = 原版登录凭据，connect/app 配置捕获）。
- 变异 staleness 仍在（本轮又改三个受测文件）—— 队列第 5 项。

## R1078 —— 【核心②·支付挑战层】PayPal 3DS 阶段 1 反编译落地：graphql PUT + 双方言头墙 + 200/403/429 分发

**取件**：队列②第 1 件（PayPal 3DS 双路径状态机）。

改了什么：
- 新增 `Cybersole.Stores/Payments/PayPalThreeDs.cs`（可执行运行时代码）：GraphqlUrl
  （0x147097e78）、AppName `checkoutuinodeweb_hermione`、双状态文案（'Proccesing' 原版拼写保留）、
  30 秒预算（+236）、四态机；NormalHeaders/HostedHeaders 两堵头墙逐头复刻（普通 16 头带
  sec-fetch 族，Hosted 17 头带 x-requested-with/x-locale/x-country/priority 且 x-app-name/referer
  取自 ctx）；SubmitAsync = 墙注册 + PUT + 200→Success / 403+429→共享 Retry / 其余→Failed；
  RunAsync 停在已解码边界并以 Pending 命名八个已定位函数。
- 新钉测 `PayPalThreeDsTests` 9 用例（含 TinyServer 驱动的分发/PUT/墙观测）。
- 生成器模板 `payment_challenges.py` 更新（markers + §三契约与九阶段地图 + §五分半叙述），
  重生成 PAYMENT_CHALLENGES.md。

验证命令与输出：
- 取证链：`dec sub_141102970`/`sub_141105A80`（孪生）→ `sub_14110D670`（URL + `sub_1408B6310`
  +24 槽 PUT）→ `names_at` 43 常量 → py_eval 九阶段引用地图；Hosted 全 solver `sub_141113680`
  （15,615 B，**switch 11 cases**）。
- `dotnet test --filter "PayPalThreeDs|Payment|Wall" -m:1` → **78/78 绿**；
  `payment_challenges.py` → **markers absent 1/5**（仅 StripeChallenge）。

数字变化：复刻件侧支付标记缺失 2/4 → **1/5**（PayPal 阶段 1 落地；Stripe 仍缺）。

证据等级：Observation = URL/头墙/预算/分发注册/墙文案/九阶段地图/11-case 机体；Inference = 载荷由
前一阶段供给、ChallengeActive 业务名、+24 槽 = PUT（三槽对照）。

还剩什么：Stripe 六步（`sub_140BE31F0`）；PayPal 阶段 2–8 逐个反编译；sec-ch-ua 生成器（队列③指纹面）；
变异 staleness 三轮自报待清。

## R1079 —— 【判据 e 维护】变异套件清陈旧 + 扩到 41 条 + 根因修复：restore 一直在改写行尾

**取件**：队列第 5 项（staleness 连续三轮自报）。

改了什么：
- 五条新变异入列（R1076–R1078 新守卫各一条可杀锚），套件 36 → **41**；Farfetch 守卫加全消息
  前缀断言（短短语多处命中、单行变异杀不死）。
- **staleness mtime → 内容比对**：运行结束写 22,111 文件 sha256 清单（对称排除报告器），
  报告端比哈希，mtime 只作旧记录回退。
- **根因修复**：harness 的 restore 是 text-mode 读写——**每次运行都在改写全部受测文件行尾**
  （此前几轮的「行尾扰动」全是它干的，git ignore-cr 掩盖）。修法：备份/还原走原始字节
  （rb/wb）+ 瞬态 EINVAL 重试；**匹配留在归一文本**（第一刀曾让 find_re 的 \n 锚失配、
  4 条 SKIP——匹配与还原必须分离）。
- VERDICT 指南计数格 36 → 41（计数棘轮先红后绿，按设计工作）。

验证命令与输出：
- A 跑 36/36 GREEN；C 跑 **41/41 GREEN**（还原全量 2294/0/2 = 2277 + 19 新钉测对账吻合）；
  字节忠实修复后**还原树零行尾扰动**（对照此前每跑必脏 3-4 文件）。
- 事故链如实记录：E 跑 37/4（find_re 匹配期病，已修）；F 跑 Geetest 还原 EINVAL 中断
  （瞬态句柄，已加重试）；G 跑挂死 28 分钟被杀——期间工作区出现**并行会话未跟踪文件**
  （ProbeSlotWrite.cs / .tmp-slot.json），文件锁碰撞假说成立，不碰只记录。
- 终跑 #7 无缓冲后台在途（pwsh-5c27d1250e764182），收据下轮收割。

数字变化：mutation-fit total **36 → 41**；fired 41/41（C 跑回执）；staleness → **0**（内容口径上线）。
当前在盘记录为 E 跑（37/4 GREEN + 清单），METRICS 如实引用并自报 harness 晚于该跑。

证据等级：全部 Observation（含两起事故现场）。

还剩什么：#7 收据；并行会话活动期避免长独占跑；队列② Stripe 六步 + PayPal 阶段 2–8。

## R1080 —— 【核心②·支付挑战层】Stripe 挑战确认步反编译落地，支付标记 1/5 → 0/5

**取件**：队列②第 2 件（`sub_140BE31F0`）。另收 #7 终跑回执。

改了什么：
- 新增 `Payments/StripeChallenge.cs`：`https://api.stripe.com`（0x147054DD8）+ **橙墙**
  `Solving Stripe challenge`（0x146E94270/1471099B0）→ `Waiting for captcha`（0x146F25E60）→
  无令牌报 `Stripe challenge captcha failed`+色 `#FB4961`；有令牌 **PUT** 五字段表单：
  `challenge_response_token`/`challenge_response_ekey`=""/`client_secret`(ctx728)/
  `captcha_vendor_name`=`hcaptcha`/`key`(ctx704)，路径 = ctx800 逐单段（+24 槽）。
- 新钉测 `StripeChallengeTests` 4 用例；变异 +1（42 条：captcha_vendor_name → recaptcha 必红）；
  指南格 41→42 同轮更新。
- 模板 `payment_challenges.py` §四/§五 更新并重生成。

验证：`dec 0x140BE31F0` + `names_at` 13 常量全解码；StripeChallenge **4/4 绿**（一次构建被并行
会话 testhost 锁 50s 后过）；SummaryBlock 4/4 绿；`payment_challenges.py` → **markers absent 0/5**。
**#7 回执**：41/41 fired（E 跑 4 条 find_re SKIP 全复活——匹配/还原分离确认）、
restored tree UNKNOWN（还原全量在争用下吃满 600s）、若干 fired 带构建冲突尾巴——干净回执需静树。

数字变化：支付标记 **1/5 → 0/5**；变异套件 41 → **42**；mutation-fit 41/41（#7）。

证据等级：全常量/PUT/表单/墙色为 Observation；urlencoded Content-Type 为 Inference（编码器类型
自带）；六步其余步骤体未解码（名字仍只是名字）。

还剩什么：Stripe 六步其余体；PayPal 阶段 2–8；42 条锚的静树全跑；sec-ch-ua 生成器（队列③）。

## R1081 —— 【核心②】PayPal 阶段 2/2.1 构建器全解码 + `(1)` 字面量修正

**取件**：队列② PayPal 阶段 2–8。

改了什么：
- `PayPalThreeDs` 增 `StageLabels`（1/2/2.1）与 `StageIsDecoded`；RunAsync 停点精确化。
- **字面量修正**：阶段 1 冻结串实为 `Solving PayPal 3DS (1)`——此前常量丢了后缀且被钉测
  钉住（文档速记盖过亲见池列表，样本当全税复现）；常量+钉测同步修正。
- 模板 `payment_challenges.py` §三/§六 更新并重生成。

验证：`dec sub_141103410`/`sub_141103800` 与阶段 1 普通**逐字节同模板**（同头墙/预算/分发），
仅进度串与续体槽不同（a1[4]→a1[7]→a1[8]）；`dec sub_141107DA0`/`sub_141108170` = 阶段 2 的
hosted 孪生（108170 带 per-context origin/referer 覆写）。
PayPalThreeDs 钉测 **10/10 绿**；markers absent **0/5** 保持。

数字变化：PayPal 钉测 9 → **10**；解码阶段地图 1/9 → **3/9**（构建器层面）。

证据等级：全控流/头墙/槽位/hosted 变体/后缀修正为 Observation；graphql 载荷仍调用方供给为 Inference。

还剩什么：阶段 3–8 六构建器（同法机械收尾）；载荷构建函数；Stripe 六步其余体；42 锚静树全跑。

## R1082 —— 【核心②】PayPal 九阶段构建器全数解码：3/9 → 9/9，构建器层结案

**取件**：队列② PayPal 阶段 3–8。

改了什么：
- `StageLabels` 扩满九阶段（每个标签对象与池清单 chars-12 地址逐一吻合），`StageIsDecoded("9")`
  为假钉住地图封口；RunAsync 停点改为「构建器全解码、缺口只剩载荷方」；两条钉测内容升级。
- 模板 §六 阶段地图全解码版（方言分布 + 续体槽表）；重生成。

验证：`dec sub_141103BF0`(3,普通,全局闭包)/`sub_1411090C0`(4,hosted,a1+80)/`sub_141109550`
(5,hosted,a1+88)/`sub_141109910`(6,hosted,a1[12],origin 拼接)/`sub_14110A080`(7,hosted,a1+104)/
`sub_141106360`(8,hosted,a1[11])——六个标签对象全部由反编译直接确认。
PayPalThreeDs **10/10 绿**；markers absent **0/5** 保持。

数字变化：解码阶段地图 3/9 → **9/9**。

证据等级：全控流/标签/方言/槽位 Observation；graphql 载荷调用方供给 Inference。

还剩什么：**载荷构建方**（sub_142FBFxxx 续体闭包族的引用者）；Stripe 六步其余体；42 锚静树全跑。

## R1083 —— 【核心②】载荷层解密：graphql 操作是冻结字面量，hosted 11-case 机 = ResolveThreeDsContingency 驱动器

**取件**：队列② PayPal 载荷构建方（R1082 指定探针）。

改了什么：
- `PayPalThreeDs` RunAsync 停点更新——载荷由「调用方不可知」改判为**冻结 graphql 字面量家族**；
  剩余未知收窄为每 case 变量绑定。钉测同步改钉。
- 模板 §六 追加 R1083 载荷段；重生成。

验证：`str "threeDomainSecure"` → **8 条 3DS 家族操作全文**（ApproveOnboardPaymentMutation ·
CurrencyConversion · OnboardGuestMutation · **ResolveThreeDsContingency ×2（六变量）** ·
approveMemberPayment ×2 · PayWithQuery）；`xrefs`：变体 B ← **`sub_141113680`（R1078 的 hosted
15,615 B 11-case 机——它就是解析器的组装与驱动本体）**，变体 A ← `sub_14110FDB0`（14,458 B
普通 solver），OnboardGuest ← `sub_14110DDA0`。
PayPalThreeDs **10/10 绿**；markers absent **0/5** 保持。

数字变化：无计数变化；未知面从「载荷方未知」收窄为「每 case 变量绑定未知」。

证据等级：家族字面量全文/xref 落点/solver 同一性为 Observation；九阶段 ↔ 11-case 对应为 Inference。

还剩什么：两台 solver 的 case 体（每 case 的 authId/referenceId/status 绑定）；Stripe 六步其余体；
42 锚静树全跑。

## R1084 —— 【核心②】3DS 绑定源定位：JSON 针 + 挑战页 DOM 双路

**取件**：队列② PayPal 每 case 变量绑定。

改了什么：纯取证轮——模板 §六 追加 R1084 绑定源段，重生成 PAYMENT_CHALLENGES.md。

验证：`str "referenceId"` → **JSON 针 `"referenceId":"`（0x146a76254）← `sub_140940820`（335 B）/
`sub_140D91B40`（308 B）**；**DOM 选择器 `input[id='referenceId']`（0x1470a48dc）←
`sub_14092F630`（557 B）**——referenceId 还从挑战页隐藏域读取；裸键 `authId`/`creditCardId`
在池。control ok、markers absent **0/5** 保持。

数字变化：无计数变化；未知面收窄为「每 case 用哪条源」（两台 solver switch case 体是最后一块）。

证据等级：针/选择器/引用函数为 Observation；解析器服务对象为 Inference（case 体未读）。

还剩什么：两台 solver 的 switch case 体——PayPal 3DS 层的最后一块拼图。

## R1085 —— 【核心②】hosted solver case 体定型：3DS 具名操作扩到 11 个 + 挑战窗 JWT/MD

**取件**：队列② solver case 体（最后一块）。

改了什么：纯取证轮——2,288 行伪代码存 `analysis/_paypal_hosted_solver.c`；case 常量解码；
模板 §六 追加 R1085 段并重生成。

验证：11 态机状态槽 `a1+88` 逐级 0→8；**第三组操作名** `GetThreeDsJwtQuery` /
`ThreeDsAuthenticateMutation` / `ThreeDsLookUpMutation`（3DS graphql 面合计 **11 个具名操作**）；
**挑战窗** `_500_x_600` + 页面 `checkoutweb/processThreedsConfirmation` + 回帖字段 **`JWT`+`MD`**；
方言 `HERMES`/`EXPRESS_CHECKOUT`/`PAYPAL`/`PRE_AUTH`/`en`。
control ok、markers absent **0/5** 保持。

数字变化：3DS 具名操作 8 → **11**；链路形状定型：JWT 查询 → 认证 → 挑战窗（JWT/MD）→ 查找 → 解析。

证据等级：伪代码存档/常量解码/状态槽为 Observation；编排次序为 Inference（逐 case 变量源待精读）。

还剩什么：逐 case 变量源精读（伪代码在盘，纯阅读）；Stripe 六步其余体；42 锚静树全跑。

## R1086 —— 【核心②合并步幅】PayPal 3DS 四态机全收口并接线；Nike 支付双 GET 链落地：占位 13 → 11

**取件**：YG 三条节奏微调后的首个合并轮。

改了什么：
- `PayPalThreeDs` 完整状态机（Pending 截断消除）：`GqlAsync`（持久化操作体
  `{"operationName":N,"variables":{…}}` + PUT + 双方言头墙 + 分发 + 30 秒）· `ReadContingency`
  （case 体针）· `RunAsync`（提交 → 偶发读取 → 无挑战即完成；有挑战跑 GetThreeDsJwtQuery →
  停挑战窗 Waiting3DS，快照入会话）· `ContinueAsync`（认证 → 查找 → Resolve 六变量，
  方言集 HERMES+EXPRESS_CHECKOUT）。`StageIsDecoded` 对机器而非标签表。
- **接线**：`PayPalGateway.CompleteActionAsync` 在 Waiting3DS 态驱动解析链——支付分发层
  到 3DS 机器端到端打通，孤岛消除。
- **Nike 支付两步**（上游 `sub_140B35420` 反编译）：`GetPaymentMethodsAsync` = GET
  `OrderV5/{order}/InitiatePayment?singleStep=true&deliveryCountryIso={country}`（进度
  'Initialize payment'）；`SubmitPaymentAsync` = GET eshopworld `PaymentMethods?paymentId=`
  → 令牌入 `Session.PaymentToken` → checkout POST 使用——三步支付链打通，两占位消除。
- 顺手修正：StripeChallenge Emit 第二参改事件类型 `"error"`；NikeFlow JP 分支 address3 空值一致性。

验证：`dec 0x140B35420` + names_at 22 常量（双 GET 全组合 + case 体响应针）；
合并测试面 **94/94 绿**（PayPalThreeDs 钉 10→14、NikePaymentChain 3 新钉、StripeChallenge
Emit 钉更新）；`payment_challenges.py` markers **0/5**；`core_coverage.py` 占位 **13 → 11**。

数字变化：核心 not captured **13 → 11**；PayPalThreeDs 钉 10 → **14**；Nike 支付钉 0 → **3**。

证据等级：双 GET 全组合/参数常量/响应针/persisted 键为 Observation；变量名→快照字段映射与
首操作名取 JwtQuery 为 Inference。

还剩什么：Stripe 六步其余体（下轮主菜）；逐 case 精读收尾；42 锚静树全跑。

## R1087 —— 【核心②合并步幅】Stripe 六步网关面解码落地：22 键表单 + desk 双端点 + 接线

**取件**：Stripe 六步收口。

改了什么：
- `StripeGateway` 按共享机 `sub_140BDA320`（812 行/7 态，双 v1 字面量共同引用者）升级：
  `MethodCreateForm` **22 键**装配序含 `radar_options[hcaptcha_token]`（0x147148170 乘载槽）+
  五冻结值（payment_user_agent 全文/time_on_page=11370/referrer=popmart/allow_redisplay/
  _stripe_version=2025-01-27.acacia——镜像第二个版本字面量）；`CustomerSessionAsync`
  （desk 会话，0x146AB8A50，query orderNum）+ `DeskPayAsync`（0x146AB8AC8，四键表单，
  returnURL=店主机+单号+/order/+?payType=stripe）；`AuthorizeAsync` 在 `stripe.deskHost`
  存在时按原机序跑三链。
- 缝：`stripe.apiUrl`（v1 主机，checkStockUrl 惯例）。变异 42 → **43**（radar 键锚）+ 指南格同步。

验证：`dec sub_140BDA320` + names_at 42 常量；**21/21 绿**（新钉 3：22 键表单+冻结值、
desk 三链机序+returnURL、路径/双版本）；SummaryBlock 4/4（指南 43）；markers **0/5**。
途中两修：返回类型 CS1503、Tokenize 真缝；**事故**：一次 PowerShell 源码手术产静默坏串
`"${…}"`（编译过、URL 错）——第七次同族，read+edit 修复。

数字变化：变异 42 → **43**；Stripe 契约钉 0 → **3**；双 `_stripe_version` 入账。

证据等级：表单/desk 路径/returnURL/冻结值全 Observation；desk 响应键名与
setupFutureUsage 空值为 Inference。

还剩什么：JL 族 `SubmitOrderStripe`/`ProcessOrderStripe` 本体；共享机尾部 312 行；43 锚静树全跑。

## R1088 —— 【核心②】Stripe 3DS2 链解码落地 + 接线；修复 R1087 遗留全文件乱码

**取件**：共享机尾部 state 3–7。

改了什么：
- `StripeGateway.ThreeDs2Async`/`ThreeDs2AuthenticateForm`（state 3–6）：**GET**
  `payment_intents/{id}/confirm`（查询串组合）→ **PUT `/v1/3ds2/authenticate`**（9 键：source +
  browser 指纹 JSON + 七冻结值 Y/24/1080/1920/-120/en-US + **one_click 五键** false/false/true/
  true/true + key + acacia）→ **PUT `hooks.stripe.com/3d_secure_2/notify`** → **PUT
  `/v1/3ds2/challenge_complete`**（source+final_cres+key+版本）。
- 接线：`requires_action` 识别 `src_` 源→存会话→`CompleteActionAsync` 带 CRes 驱动全链、
  成功清源。缝：`stripe.apiUrl`/`stripe.hooksUrl`。
- **乱码修复**（R1087 的 `Get-Content -Raw` GBK 误读所致，守卫逼出）：Gateways.cs 全文件
  **33 处**（30 em-dash→U+9225? + 3 箭头→U+922B?，2 处换行吞）——活文件+本轮快照同修，
  SourceEncodingTests 复绿。
- 变异 43 → **44**（spc_eligible 旗标锚）+ 指南格同步。

验证：`dec sub_140BDA320` 尾 312 行 + names_at 31 常量；**26/26 绿**（3 新钉：表单 9 键、
三链机序+final_cres、网关完成驱动+清源）；SummaryBlock 4/4（指南 44）；metrics exit 0。
事故：两编译修（非法模式串/url3ds 双声明）；乱码修复三步才对（先错搜 U+FFFD?；快照漏修）。

数字变化：变异 43 → **44**；Stripe 契约钉 3 → **6**；v1 端点 2 → **4** + hooks 面 1。

证据等级：三 URL/9 键/旗标族/冻结值/GET 组合/'cres' 针全 Observation；hooks 体与
指纹两默认值为 Inference。

还剩什么：JL 族两本体；44 锚静树全跑。

## R1089 —— 【核心①+②】JL `SubmitOrderStripe` 落地：payments PUT 双参数 + CREDITCARD 门

**取件**：JL 族 Stripe 本体。

改了什么：`JohnLewisFlow.SubmitOrderStripeAsync` 首个 override——**PUT
`bff/v2/orderforms/payments?methodId={ctx23}&setupFutureUsage=false`**（解码自
`sub_140A42BC0` 五态机，双参数 0x1470C29A0/0x147159A48）；CREDITCARD 门（内联串判定，
选中该方法而无卡 → 失败）；四连请求续体（`sub_140A371E0`→`370F0`→`37140`→`37190`，
跳板未解）命名记录 = 步序表的 HandleRequiresAction/GetStripePaymentIntent。缝
`jl.paymentsUrl`。变异 44 → **45**（methodId 锚）+ 指南同步。

验证：`str "orderforms/payments"` → v2 0x14705d744 唯一引用机 `sub_140A42BC0`（176 行全解）；
**11/11 钉绿**（3 新：双参数契约、CREDITCARD 门、无 id 可重试停+零出网）；SummaryBlock 4/4
（指南 45）；metrics exit 0。途中一修：HttpListenerRequest 的 `.HttpMethod`。

数字变化：变异 44 → **45**；JL Stripe 步钉 0 → **3**。

证据等级：端点/双参/PUT 槽/CREDITCARD 判定/四连跳板为 Observation；setupFutureUsage 关态与
会话字段宿主为 Inference。

还剩什么：四连异步机本体（两 Stripe-direct 步的真实请求面）；45 锚静树全跑。

## R1090 —— 【核心①+②】JL 两 Stripe-direct 步落地：针链 + fingerprint 门 + 冻结账户

**取件**：四连跳板本体。

改了什么：
- 追链 `sub_140A371E0` → TLS 包装 → 真体 **`sub_140A40A30`**（186 行）：针链
  `next_action`→`use_stripe_sdk`→`type`，门 `stripe_3ds2_fingerprint`（0x147165BF0），源
  `three_d_secure_2_source`，`_secret_` 切分针（0x146F64778）；构建器 `sub_141141680` 带
  **冻结 Stripe 账户 `acct_1S0JRiIiwyy5Cf6X`**（0x146F6D140）+ BFF 主机（0x14705D5A8）。
- `GetStripePaymentIntentAsync`：针链解析 payments 应答→源/type/secret 入会话；
  `HandleRequiresActionAsync`：fingerprint 门→冻结账户入会话；`StripeAccount` 常量。
- 变异 45 → **46**（fingerprint 门锚）+ 指南同步。

验证：`dec sub_140A40A30` 186 行 + names_at 8 常量；**14/14 钉绿**（3 新：针链+secret 切分、
门+账户+他型不动、无应答可重试停）；SummaryBlock 4/4（指南 46）；metrics exit 0。

数字变化：变异 45 → **46**；JL Stripe 步钉 3 → **6**；三个 Stripe-direct 步全有执行体
（fetch/构建器本体为命名续体）。

证据等级：四针/账户/主机/控制流全 Observation；步名与针链的对应及账户角色为 Inference。

还剩什么：`sub_141141680` 构建器请求体；`sub_140A37540` 真体；46 锚静树全跑。

## R1091 —— 【核心①+②】JL Stripe 过程墙解码落地：STRIPE 频道 + 四句机内文案

**取件**：构建器本体。

改了什么：
- 追链构造体 → 启动器 → 真体 **`sub_141146510`**（295 行 / 4 态）：**过程墙**
  `Process start: payment_intent={id} merchant={acct} source={src}` 发 **STRIPE 频道**
  （0x146E76110）；请求链 `sub_141141870`→`910`→`9B0`→`A00` → `Process complete`；
  停线 `stopping after fingerprint (alive=, hasForm=)` 与无源 74 字全句。
- 落地：`HandleRequiresActionAsync` 照发过程墙（三值拼接）；`GetStripePaymentIntentAsync`
  无源分支照发停线；`jl.stripeIntentId` 入会话。
- 变异 46 → **47**（STRIPE 频道锚）+ 指南同步。

验证：`dec sub_141146510` 295 行 + names_at 13 常量；**16/16 钉绿**（2 新：过程墙+频道、
无源停线）；SummaryBlock 4/4（指南 47）；metrics exit 0。

数字变化：变异 46 → **47**；JL Stripe 步钉 6 → **8**。

证据等级：四句文案/频道/槽名/控制流全 Observation；intentId 键宿主与墙-链先后为 Inference。

还剩什么：三请求链本体（JL Stripe 最深一块）；47 锚静树全跑。

## R1092 —— 【核心①+②】JL 3DS2 hosted 页 GET 落地：hooks 面 + 五段组合 + returnUrl 报线

**取件**：三请求链首件。

改了什么：
- 追链 `sub_141141870` → TLS 包装 → 真体 **`sub_141144FC0`**（222 行 / 2 态）：
  **GET `hooks.stripe.com/3d_secure_2/hosted?merchant={账户}&payment_intent={id}
  &payment_intent_client_secret={secret}&publishable_key={key}&source={源}`**
  （53 字基址 0x14706B818 + 四段名 0x146A84F80/4FB8/5280/5C80 逐字）；报线
  `GetHostedPage: returnUrl={值}`（0x146D9EB30）发 STRIPE 频道。
- 落地：`HandleRequiresActionAsync`（转 async）过程墙后接 hosted GET → returnUrl 入会话 +
  报线照发；`stripe.hooksUrl` 缝复用。
- 变异 47 → **48**（merchant 段锚）+ 指南同步。

验证：`dec sub_141144FC0` 222 行 + names_at 10 常量；**17/17 钉绿**（1 新：五段组合+returnUrl
报线；两处早钉补 hooks 缝防真 URL 外泄）；SummaryBlock 4/4（指南 48）；metrics exit 0。

数字变化：变异 47 → **48**；JL Stripe 步钉 8 → **9**；hooks 面再添 hosted 端点。

证据等级：基址/四段/GET 槽/报线/控制流全 Observation；returnUrl 响应键形状与
publishable_key 宿主为 Inference。

还剩什么：链后两件（挑战应答回投与完成）；48 锚静树全跑。

## R1093 —— 【核心①+②】JL 意图 confirm GET 落地：四段查询串 + 过程链收尾句

**取件**：三请求链第二件。

改了什么：
- 追链 `sub_141141910` → TLS 包装 → 真体 **`sub_1411458F0`**（187 行 / 2 态）：
  **GET `api.stripe.com/v1/payment_intents/{id}?is_stripe_sdk=true&client_secret={s}&key={pk}
  &_stripe_account={冻结账户}`**（42 字基址共享 R1088 同址面 + 三段名 0x146B28808/0x146A84588/
  **0x146A7AFD8 JL 独有账户段**）；收尾句 `Process complete`（0x146E4AA00）发 STRIPE 频道。
- 落地：hosted GET 后接 confirm GET → 成功发收尾句。**过程链三请求端到端跑通**。
- 两处早钉补 `stripe.apiUrl` 缝；变异 48 → **49**（`_stripe_account` 锚）+ 指南同步。

验证（**可用内存 1,191 MB < 2 GB，按纪律逐类单跑**）：JohnLewisStripeStepTests **10/10**、
SourceEncodingTests **2/2**、JohnLewisStepMapTests **6/6**、StoreFlowDigestTests **2/2**
= **20/20**；SummaryBlock 4/4（指南 49）；metrics exit 0。
**崩溃单列**：四类合跑一次 testhost 崩溃（内存），不计入结论。
**构建状态单列**：收尾构建被并行会话 `KasadaSolver.cs` 在途改动打断（CS0103/CS1503），
非本轮文件未触碰。

数字变化：变异 48 → **49**；JL Stripe 步钉 9 → **10**。

证据等级：基址/三段/GET 槽/收尾句/控制流为 Observation；confirm 响应体与两个会话宿主为 Inference。

还剩什么：链尾第三件（9B0/A00 两分支请求面）；49 锚静树全跑（需 >2 GB 窗口）。

## R1094 —— 【核心①+②】JL 3DS2 指纹提交与完成落地：链尾两态全解，五请求链闭合

**取件**：链尾第三件。

改了什么：
- **state 2 = `sub_1411474A0`（477 行）**：PUT `/v1/3ds2/authenticate`（与 R1088 同端点）——
  12 键浏览器指纹 + **one_click 五指族由 has-form 位驱动**（hosted/webauthn 恒 true，
  其余三指跟随；无表单加 `fingerprintOutcome=not_supported` + `frontend_execution`）+
  key + `_stripe_account`。
- **state 3 = `sub_141144C20`（113 行）**：报线 `CompletePayment: notify serverTransactionId=` →
  PUT `hooks…/notify/{account}/{txn}` → PUT `/v1/3ds2/challenge_complete`（source/final_cres/
  key/_stripe_account）。
- 落地：confirm 后接三跳 + 两条报线（`SubmitFingerprint: methodUrl='…' fingerprintAvailable=…`）；
  `JlFormOptions` 助手（PUT 表单）。**JL 五请求链闭合**：墙 → hosted → confirm →
  authenticate → notify → challenge_complete → Process complete。
- 变异 49 → **50**（has-form 位锚）+ 指南同步。

验证（内存恢复 3,045 MB）：JohnLewisStripeStepTests **12/12**（2 新钉）、SourceEncoding 2/2、
JohnLewisStepMap 6/6、StoreFlowDigest 2/2、StripeMethodForm 6/6、SummaryBlock 4/4（指南 50）
= **32 钉全绿**；metrics exit 0。

数字变化：变异 49 → **50**；JL Stripe 步钉 10 → **12**。

证据等级：两真体控制流/12 键指纹/五指旗标依赖/not_supported/notify 组合/final_cres/两报线全
Observation；frontend_execution 取值与 notify 第二段语义为 Inference。

还剩什么：notify 段 `_stripe_account` 语义确认；50 锚静树全跑。

## R1095 —— 【核心②·重大纠正】PayPal graphql 载荷全解：四段文档 + URL 查询串形状

**这是一轮纠正轮**：R1086 把 Stripe 的持久化信封套到了 PayPal 上，本轮用 evidence 推翻。

改了什么：
- 逐 case 定位 10 个 PUT 站点 → PayPal 的操作名走 **URL 查询串**
  （`graphql?GetThreeDsJwtQuery` 0x147097F60 等四条），体是
  **`{"variables":{…},"query":"<完整文档>"}`**（非 `{"operationName":N,…}`）；另有 REST 端点
  `payment-authentication/threeds/v1/notify-method-cmpl`（0x147098740）。
- **四段文档从 IDB 直读落为常量**（零手抄，13,305 字）：JwtQuery 631 字 / Authenticate 813 字 /
  LookUp 871 字 / Resolve **10,370 字**（含八 fragment）。
- `GqlAsync` 改形状（`?operationName` + `query` 文档）+ `DocumentFor` 映射 +
  `NotifyMethodCompleteUrl`。变异 50 → **51**（`?`→`/` 锚）+ 指南同步。

验证：`PayPalThreeDsTests` **16/16**（2 新钉）、SummaryBlock 4/4（指南 51）、SourceEncoding 2/2、
metrics exit 0。**构建被并行 testhost 锁三次**，等锁后成功；旧 dll 上的 6 失败不计入。

数字变化：变异 50 → **51**；PayPal 钉 14 → **16**；**PayPal 载荷层闭合**（R1083 起追的
「载荷构建方」至此闭环）。

证据等级：10 站点 URL/体键、四文档全文、REST 端点为 Observation；变量绑定与 notify 位置为 Inference。

还剩什么：`notify-method-cmpl` 调用点接线；51 锚静树全跑。

## R1096 —— 【核心②】PayPal 3DS2 设备数据对落地：init-method 的 JWT + notify 的 threeDSMethodData

**取件**：`notify-method-cmpl` 调用点接线。

改了什么：
- `xrefs 0x147098740` → hosted solver（站点 962）+ `sub_140D8D2B0`（普通路 6,310 B）。
- 站点 962 解出设备数据对：**门 = alive**（`sub_140F9E790`，R1091 停线里那枚）；
  **POST `JWT` 表单**到响应自带 `deviceDataCollectionUrl.href`，缺失落冻结
  `init-method`（0x1470985E8）；**PUT `notify-method-cmpl`** 表单
  **`threeDSMethodData` = base64(`{"threeDSServerTransID":…}`)**。
- 落地 `SubmitDeviceDataAsync`（两跳 + alive 门 + 零出网跳过）+ 四常量；`RunAsync` 在 JWT
  查询后接该步。变异 51 → **52**（信封键锚）+ 指南同步。

验证：`PayPalThreeDsTests` **18/18**（2 新钉）、SummaryBlock 4/4（指南 52）、
SourceEncoding 2/2、metrics exit 0。

数字变化：变异 51 → **52**；PayPal 钉 16 → **18**；3DS2 HTTP 面 **7 端点**。

证据等级：两跳 URL/表单键/alive 门/信封/默认回落为 Observation；tID 位置与跳序为 Inference。

还剩什么：`sub_140D8D2B0` 与 hosted 的差异对照；52 锚静树全跑。

## R1097 —— 【核心②·结构发现】PayPal 有两套 3DS 方言：普通路 `heliosnext` 全解并落地

**结构发现**：不是一条链的两半，是**两套端点面**。

改了什么：
- `sub_140D8D2B0`（6,310 B）落盘 781 行；与 hosted 差分：48 常量中 **24 个普通路独有**。
- 独有面：`heliosnext/threeDS?action=verify&flow=3ds&cart_id=` · `/api/serverData` ·
  `/api/session` · `/api/processThreedsConfirmation` · **`init-challenge`（普通路独有）**；
  字段 `action`/`deviceInfo`/`payload`/`userAgent`/`cart_id`/`challenge_callback_url`；
  失败线 **`Payment failed (3DS)` + `#FB4961`**（与 StripeChallenge 同色常量）。
- 普通路序：GET 入口 → serverData → session(action) → init-method → notify-method-cmpl →
  init-challenge(JWT) → processThreedsConfirmation。**两方言仅共享方法对。**
- 落地 `SubmitNormalBootstrapAsync` + `SubmitChallengeInitAsync` + 12 常量 + 会话缝。
- 变异 52 → **53**（`action` 锚）+ 指南同步。

验证：`PayPalThreeDsTests` **21/21**（3 新钉）、SummaryBlock 4/4（指南 53）、
SourceEncoding 2/2、metrics exit 0。

数字变化：变异 52 → **53**；PayPal 钉 18 → **21**；3DS HTTP 面 **7 → 10 端点**。

证据等级：常量差分/21 常量/9 站点/共享面为 Observation；普通路表单装配细节与
processThreedsConfirmation 体形状为 Inference。

还剩什么：普通路四端点逐行表单装配；方言选择入口接线；53 锚静树全跑。

## R1098 —— 【核心②】普通路 bootstrap 形状纠正：两跳都是 JSON；confirm 与 entry URL 落地

**又一处形状纠正**：R1097 把 session 跳写成表单，逐行读装配后是**两跳都 JSON 且都带 token**。

改了什么：
- serverData = PUT JSON **`{"token": <cartId>}`**（0x147171D48）；session = PUT JSON
  **`{"token": <cartId>, "action": "verify"}`**（+0x146F6D9A8，字面量 0x14717E4A8）；
  entry URL = 冻结前缀 + 车号 + **`&go_to=next`**（0x146A7F400）。
- 落地：`SubmitNormalBootstrapAsync` 改 JSON 双跳（`action`→`cartId`）+ `EntryUrlFor(cartId)`
  + `SubmitProcessConfirmationAsync`（ctx+8 或冻结 confirm 端点，被拒发普通路失败线）+ 三常量。
- 变异 53 → **54**（`&go_to=next` 锚）+ 指南同步。

验证：`PayPalThreeDsTests` **23/23**（重写 1 钉 + 2 新钉）、SummaryBlock 4/4（指南 54）、
SourceEncoding 2/2、metrics exit 0。

数字变化：变异 53 → **54**；PayPal 钉 21 → **23**；普通路可执行跳 **2 → 4**。

证据等级：JSON 类型标记/三键/verify 字面量/entry 三段为 Observation；confirm 内容体为 Inference。

还剩什么：confirm 内容体内部字段；方言选择入口接线；54 锚静树全跑。

## R1099 —— 【核心②】普通路端到端接线：`RunNormalAsync`，三跳不再是孤岛

**反孤岛**：R1097/R1098 的三跳此前只有测试能调，`RunAsync` 只走 hosted。

改了什么：
- 新增 `RunNormalAsync(c, input, cartId, ct, graphqlUrl)` —— 普通方言完整入口，镜像镜像里
  **两个 solver 入口点**（`sub_140D8D2B0` 普通面 / `sub_141113680` hosted 面）：
  bootstrap → SubmitAsync → ReadContingency → JWT query → 方法对 → init-challenge →
  落 resolver 输入 + `state=Waiting3DS` + `hosted="0"`，返回 `Challenge`。
  **与 hosted 同一停靠契约**（窗口都是宿主驱动）。
- 变异 54 → **55**（方法对跳过锚）+ 指南同步。

验证：`PayPalThreeDsTests` **24/24**（1 新钉：端到端序 + `hosted="0"` + alive 门挡后三跳）、
SummaryBlock 4/4（指南 55）、SourceEncoding 2/2、metrics exit 0。
构建时修一处自造 CS1503（多余的 `AbsorbCookies` 空数组，删除）。

数字变化：变异 54 → **55**；PayPal 钉 23 → **24**；普通方言**三跳可调用 → 端到端可运行**。

证据等级：九站点顺序/停靠契约/hosted 标志为 Observation；**两方言分派判据为 Inference**
（未解出，故 `RunNormalAsync` 作独立入口，不改 `RunAsync` 既有语义）。

还剩什么：两方言分派判据（哪个字段选 `sub_140D8D2B0` vs `sub_141113680`）；confirm 内容体；
55 锚静树全跑。

## R1100 —— 【核心②】分派判据解出：按对象类型，不是字段；方言选择器落地

**推翻了「某字段决定走哪条」的预设**：两 solver 四次引用链**形状逐条对称**，是同一接口的
两个实现类型。

改了什么：
- 两 solver 的 4 条引用：`0xb` thunk + `0xce/0xcf` 启动包装 + **`0xa4` MethodTable 槽函数**
  （模板同一，仅目标异）+ 一个 MethodTable 槽数据引用。
- 槽内 = 32 位 RVA：`0x1475D4950 → 0xD8D2B0`（普通）、`0x14760B61C → 0x1113680`（hosted）。
  再追包装层 → 两个类各一组**平行虚槽**（`0x028E69E0`+`0x028E6AB0` / `0x0258A600`+`0x0258A6CF`）。
- **结论**：没有共享的字段分派；选哪条链由**构造哪个类型**决定 → 落地
  `ThreeDsDialect { Hosted, Normal }` + `RunDialectAsync(...)`，两分支各一钉。
- 变异 55 → **56**（选择器塌缩锚）+ 指南同步。

验证：`PayPalThreeDsTests` **25/25**（1 新钉覆盖两分支互斥面）、SummaryBlock 4/4（指南 56）、
SourceEncoding 2/2、metrics exit 0。

数字变化：变异 55 → **56**；PayPal 钉 24 → **25**；**分派机制 Unknown → Observation（类型分派）**，
字段级判据的未知项**撤销**（它不存在）。

还剩什么：confirm 内容体内部字段；56 锚静树全跑。

## R1101 —— 【核心②】confirm 内容体解出：响应读取 + 200 投影；回调 URL 片段落地

改了什么：
- `sub_140D8CF60`（20 行）= **响应反序列化回调**：`sub_1408C0CE0(a2, 类型)` 读 + 
  `sub_142389CA0(v4, 200, v5, 1)` 投影到 200 —— **与既有 `SubmitProcessConfirmationAsync`
  同形**，故内容体是「上一跳给的内容」，Unknown 撤销。
- 解出普通路独有 **`state=undefined&code=undefined&liability_shift=`**（0x147163128，47 字），
  位于 StringBuilder 拼接区（0x140D8E6FF），与 **`challenge_callback_url`（0x146FC54D8，全库
  仅一处引用）** 同域 → 回调 URL = 基址 + 该片段。
- 落地 `ChallengeCallbackFragment` + `ChallengeCallbackUrlFor(...)`；
  `SubmitChallengeInitAsync` 增 `challenge_callback_url` 字段。
- 变异 56 → **57**（片段截断锚）+ 指南同步。

验证：`PayPalThreeDsTests` **26/26**（1 新钉）、SummaryBlock 4/4（指南 57）、
SourceEncoding 2/2、metrics exit 0。
**自伤记录**：误删一钉签名，下一读即发现并整块补回。

数字变化：变异 56 → **57**；PayPal 钉 25 → **26**；confirm 内容体 Unknown → Observation。

还剩什么：片段到字段的逐指令绑定（把 Inference 降为 Observation）；57 锚静树全跑。

## R1102 —— 【核心②·纠正】`challenge_callback_url` 是读回来的，不是发出去的

**逐指令读完，推翻 R1101 的做法。**

改了什么：
- `dis 0x140D8E6E0`（278 条指令）读出 init-challenge 真实装配：
  `0x140D8E6E7` 取 **"payload"** → `0x140D8E6FF` 取 **"challenge_callback_url"** → 存 **ctx+0x30**；
  请求 URL = ctx+0x60 或冻结 `init-challenge`；**表单只有 `JWT`**；`sub_1408B6310` = PUT。
- **结论**：callback 是**应答侧**值，**不进请求体**。R1101 的请求字段**撤销**。
- 落地：表单恢复单键 JWT；改为从 `payload` **读回** callback 存入会话。
  `ChallengeCallbackFragment`/`ChallengeCallbackUrlFor` 保留（属**最终 GET** 的片段）。
- 变异 57 → **58**（payload 读取锚）+ 指南同步。

验证：`PayPalThreeDsTests` **26/26**（重写 1 钉：表单不含 callback、值从 payload 读回）、
SummaryBlock 4/4（指南 58）、SourceEncoding 2/2、metrics exit 0。

数字变化：变异 57 → **58**；钉数仍 26（一条换了方向）；**属性从 Inference 升 Observation，
并把 R1101 的错向实现就地纠正**。

还剩什么：47 字片段到最终 GET 的逐指令绑定；58 锚静树全跑。

## R1103 —— 【核心②】最终 GET 片段归属定案：'?' 感知分隔符

改了什么：
- `sub_140D8D2B0` L616–655 + `dis 0x140D8D4F0` 读出：门 = `alive` **且** `*(v2+24)`；
  基址 = `*(a1[2]+56)`；**分隔符二选一**（`sub_141CFA770(基址, '?')` 真 → `&`
  0x146A7ABA8，假 → `?` 0x146B2760）；再追加 47 字片段。
- 落地 `ChallengeCallbackUrlFor` 的 `Contains('?') ? "&" : "?"`，并注明「测含 `?` 而非以 `?`
  结尾」，故以 `?` 结尾时得字面 `?&` —— **镜像行为，不美化**。
- 变异 58 → **59**（分隔符盲连锚）+ 指南同步。

验证：`PayPalThreeDsTests` **26/26**（三条分隔符断言）、SummaryBlock 4/4（指南 59）、
SourceEncoding 2/2、metrics exit 0。
**一次自纠**：首跑 1 红，红的是我自己上轮的断言（期望 `?state=`），按规则应 `?&` ——
**改断言不改代码**，并把 `?&` 显式钉住。

数字变化：变异 58 → **59**；片段归属 Inference → Observation。

还剩什么：59 锚静树全跑；队列②收尾清点。

## R1104 —— 验证轮：转义修复 + 整树复算；59 锚全跑未完成（如实单列）

改了什么：
- `tools/mutation-check.py` L170 非法转义 `\C`（侥幸工作 + SyntaxWarning）→ **raw string**；
  `py_compile` 在 `-W error::SyntaxWarning` 下**零告警**通过。

验证：
- **59 锚全跑：未完成。** 首次调用直接开跑并转后台，停在早期锚；查
  `MUTATION_RESULT.json` 的 mtime = **10:29:40**（当时 16:24），**是 6 小时前旧轮产物**，
  不作本轮通过。按 §2.6「没跑成 ≠ 通过」挂为未完成。
- **整树收据**（`--only "1103"` 自带还原验证）：**2386 通过 / 1 失败 / 2 跳过 / 2389**，
  1m55s；该锚 guard fired。唯一失败 `WallDispatchTests.DetectionDispatchesToTheStrategy`
  缺 `"KasadaStrategyRunner.Default()"`，而 `KasadaVersions.cs` **正被并行会话修改**——
  非本轮文件，未触碰。
- **崩溃单列**：先前一次整树跑 2072 通过后 testhost 崩溃（内存 3.0 GB）；同命令重跑 1m55s
  跑完，属瞬时压力。

数字变化：锚数仍 **59**（未新增）；修一处工具告警；整树 **2386/2389 + 1 项非本轮失败**。

还剩什么：59 锚全跑取绿收据（内存 >3 GB + 并行会话静默窗口，落盘后立即核对时间戳）；
`WallDispatchTests` 待并行会话收尾后复算。

## R1105 —— 59 锚全跑取新鲜收据；我自己的钉被判 DECORATIVE，已修

改了什么：
- 全跑取得 **16:36:33 新鲜收据**：`total 59 / fired 57 / decorative 1 / skipped 0 / tree RED`。
- **`DECORATIVE`：`round 1099`（我 R1099 加的锚）** —— 钉的桩应答不含 `jwt`，方法对被 alive
  门挡回零出网，删掉方法对出口一样，**钉看不见要钉的代码**。
- 修钉：桩补 `jwt` + `threeDSServerTransID`；断言改**七跳全序**（serverData → session →
  graphql×2 → init-method → notify-method-cmpl → init-challenge）+ 三条请求体关键字段。
  **复验 `guard fired`。**

验证：修钉后 `PayPalThreeDsTests` **26/26**；`--only "1099"` → guard fired。
另一条非 fired 是 **`round 112` DID NOT COMPILE**，同期满是 `CS2012`/`MSB3027` 文件锁
——**并行会话抢占构建产物所致，非变异缺陷**，需静默窗口重验。
`tree RED` 唯一失败仍是并行会话的 `WallDispatchTests`。

数字变化：锚数仍 **59**；**decorative 1 → 0**。

还剩什么：静默窗口复跑全 59 锚取 `fired 59 / tree GREEN`（判据 e 完整形态）。
`analysis/MUTATION_RESULT.json` 被窄口径运行覆写，**未提交**以免冒充全套收据。

## R1106 —— 判据 (e) 变异半边达成：59/59 fired、decorative 0、staleness 0

改了什么（纯验证 + 记账，无源码改动）：
- `--only "112"` → **guard fired**：证实上轮 `DID NOT COMPILE` 纯属并行会话 testhost 抢占
  构建产物（同期 CS2012/MSB3027），**不是变异缺陷**，未改该变异。
- 全跑取最终收据。

验证：
- 收据 `ran_at 2026-11-18T16:51:02+08:00`、**`total 59 / fired 59 / decorative 0 / skipped 0`**
  （mtime 16:51:08，读于 16:51:13，**5 秒新鲜**）。
- `metrics_report --skip-tests` → **`mutation-fit: 59/59 fired, decorative 0, skipped 0,
  staleness 0 -- no exercised file's content differs from the run`**（计数 + 新鲜度双通过）。
- **`tree RED`，唯一失败 `WallDispatchTests.DetectionDispatchesToTheStrategy`**
  （2386/2/2389，3m04s）；测试文件未动，`KasadaVersions.cs` 正被并行会话修改——**未触碰**。
- 我方域全绿：PayPal 26 + JL 12 + StripeForm 6 + Encoding 2 + Summary 4 = **50 钉**。

数字变化：**fired 57 → 59**、decorative 0、skipped 0、staleness 0。
**判据 (e)：「变异全部 fired」达成；「全量套件绿」差 1 项非本轮失败。**

还剩什么：待并行会话收尾后复算整树 GREEN；队列②外部服务驱动契约清点。

## R1107 —— 判据 (e) 完整达成：GREEN 2387/0/2 + 59/59 fired + tree GREEN + staleness 0

改了什么（一处跨会话修复）：
- 整树仍卡 `WallDispatchTests.DetectionDispatchesToTheStrategy`。**根因不是功能缺失**：符号与调用
  都在（`StoreFlow.cs:473` `KasadaStrategyRunner.Default(`），但**实参换行写在下一行**，而断言要求
  `Default()` **连写** → 断言脆性。对照同测试内 `CloudflareStrategyRunner.Default()` 仍单行故通过。
- 修法：断言改 `"KasadaStrategyRunner.Default("`（去闭括号），**同一意图**，容忍多行。测试文件、
  非产品代码，且无并行在途改动。

验证：
- `WallDispatchTests` **4/4 绿**；整树 **`失败 0 / 通过 2387 / 跳过 2 / 总计 2389`**（2m24s）。
- 重跑变异全套件（改测试→manifest 会旧）：收据 `ran_at 17:05:23`、
  **`59 / fired 59 / decorative 0 / skipped 0 / tree GREEN`**（6 秒新鲜）。
- `metrics_report --skip-tests` → **`59/59 fired, decorative 0, skipped 0, staleness 0`**。

**判据 (e)：全量套件绿 ✓ / 变异全 fired ✓ / 条数一致 ✓ / 数字来自 METRICS ✓ —— 四分之四达成。**

数字变化：整树 1 失败 → **0**；收据 `tree` RED → **GREEN**。

还剩什么：(a)(b)(c)(d)(f) 逐项复算与证据归集。

## R1108 —— 【判据 a】类型缺席三分类对账：UNKNOWN 6 -> 4

改了什么：
- 15 行分类已齐：**6 RENAMED / 2 OUT_OF_SCOPE(R702) / 1 STRUCTURAL / 6 UNKNOWN**。
- **两本台账打架**：`LocalizeFormatExtension` / `LocalizeSwitchExtension` 在分类里仍 UNKNOWN，
  而 `replica/docs/B_CLASS_DECISIONS.md` **L25/L26 早已裁决为「已有等价物」**（内联三元 /
  `string.Format` 直调）。**后裁未回灌** → 改判 `EQUIVALENT` 并抄录裁决原文。
- 补镜像侧身份：命名空间 `Cybersole.Ui.Localization` + XAML 类型名表 `0x1432fd514`（六名全表）
  + 描述符 `0x14320c2d5`。
- 另四条（AccountsCreatorView / TaskCreatorCartView / LocalizeEnumExtension /
  LocalizeFallbackExtension）在 B_CLASS_DECISIONS 无对应行 → **保持 UNKNOWN，不编结论**。

验证：`where_is` 13 处全在 docs（复刻件确无实现）；`git diff --ignore-cr-at-eol` 空（纯 CRLF 噪声）；
文档守卫 SourceEncoding 2 / SummaryBlock 4 / DocsConsistency 8 / ParityDoc 9 = **23 钉全绿**。

数字变化：UNKNOWN **6 -> 4**；EQUIVALENT +2；类型缺席原始计数仍 15（未实现新类型）。

还剩什么：剩余 4 条 UNKNOWN 需镜像侧成员集取证；(b)(c)(d)(f) 逐项复算。
## R1109 —— 【判据 a】三分类收口：UNKNOWN 4 -> 2

改了什么：
- **三分类与测试矛盾**：`AccountsCreatorView` 被 `OriginalViewClassParityTests.cs` **L47** 钉住
  -> `AccountImportWindow`（且 `AccountImportWindow.cs` 文档注释写着原名）；
  `TaskCreatorCartView` 被 **L51** 钉住 -> `TaskCreatorView`。**两条改判 RENAMED，证据引行号。**
- 剩余两条 `LocalizeEnumExtension`/`LocalizeFallbackExtension`：`TYPE_RENAME_MAP.md` L282/L290
  给出**各仅 1 成员 `Value`**，三个 MEDIUM 候选全是巧合 -> 改写为
  `UNKNOWN (缺：成员名无区分力)` 并逐字写明缺什么。

验证：`where_is AccountsCreatorView` 命中 implementation + test；
分类计数 RENAMED 8 / OUT_OF_SCOPE 2 / STRUCTURAL 1 / UNKNOWN 2 / EQUIVALENT 2 = 15 行；
文档守卫 DocsConsistency 8 / ParityDoc 9 / SourceEncoding 2 / SummaryBlock 4 = **23 钉全绿**。

数字变化：UNKNOWN **4 -> 2**；RENAMED **6 -> 8**。

还剩什么：两条 Localize 需成员集之外的证据（虚槽 / XAML 用法）；(b)(c)(d)(f) 逐项复算。
## R1110 —— 【判据 a】纠正理由：`Value` 是绑定路径，不是成员

改了什么：
- 查描述符原文：`LocalizeEnumExtension,Cybersole.Value!Getter`（0x14320D3B4）/
  `LocalizeFallbackExtension,Cybersole.Value!Getter`（0x14320EAE3）——形如
  `<类型>,<绑定路径>!<种类>`，故 **`Cybersole.Value` 是绑定路径**，不是这两个类型的成员。
  生成物 `TYPE_RENAME_MAP.md` 的 `1 members: Value` 是解析器把路径末段当成员名。
- 两行理由改为 **`UNKNOWN (缺：类型自身成员集)`**，写明要从 MethodTable/元数据取。
- `TYPE_RENAME_MAP.md` 是生成物，**未手改**；解析器缺陷记入 BLOCKERS。

验证：6 条描述符原文与地址；分类仍 15 行（8/2/1/2/2）；文档守卫 DocsConsistency 8 / ParityDoc 9 /
SourceEncoding 2 = **19 钉全绿**。

数字变化：分布不变；**这两条的「缺什么」从错的改成对的**。

还剩什么：`tools/type_rename_map.py` 成员名解析缺陷待修；两条 Localize 需元数据侧成员集；(b)(c)(d)(f)。
## R1111 —— 【判据 a】根因量化定案：四个 Localize*Extension 只坐转换器位

改了什么：
- 生成链读通：`xaml_bindings.json` ← `analysis/_xaml_bindings.py`（24 行）← `pe_strings.txt`；
  缺陷在 L6–15：正则切 `(类型, Owner.Property, Kind)`，L14 取 Property，L15 记到**第一组类型**名下。
- **量化证明**：描述符 **2,474** 对 / 首组去重 202 / owner 去重 558；
  `*Extension` 在**首组恰好 4 个**（四个 Localize*Extension，15 次），在 **owner 位 0 个应用类型**
  （只有 `Avalonia.Base.Converter`×9）→ 记在它们名下的 `Value` 是 **owner 的属性**。
- 两行三分类改写为带量化证明的 `UNKNOWN (缺：类型自身成员集)`。
- **未改共享数据**：`xaml_bindings.json` 有 **80+ 消费方**；正确修法是「记零成员而非剔除」
  （剔除会藏起真实缺席）；需专用轮 + ≥3 GB 窗口全链重生成，已写 BLOCKERS。

验证：DocsConsistency 8 / SourceEncoding 2 = **10 钉全绿**（内存 1,648 MB，只跑单类）。

数字变化：分布不变；两条 UNKNOWN 的依据 **Inference → Observation**。

还剩什么：`xaml_bindings.json` 转换器位修复（专用轮）；两条 Localize 需元数据侧成员集；(b)(c)(d)(f)。
## R1113 —— 关闭 R1112 的 Inference：39 段移除逐条核实

改了什么：
- 从 diff 取出**全部 39 个移除段落的类型全名**，对 `replica/src` 做**声明级**匹配
  （`class|record|struct|enum|interface + 短名`，非「出现即算」）。
- 结果 **39 = 35 + 4**：35 个在 src 有声明（实现了才退出候选表）；4 个仍缺席
  （四个 `Localize*Extension`，退出的是候选表而非缺席名单）。
- **缺席名册没被藏**：`types absent from source` 仍 **15**、`scope misses` **0**、
  `backlog types absent` 4 → **2**（R1109 改判的两条退出）。
- **修我自己埋的隐患**：`analysis/xaml_bindings.json` 被上轮 `Move-Item` 移走，
  而 `analysis/decl_coverage.py` L31 **按绝对路径读它** —— 已同步回该路径，两处一致（20,886 B，
  逐字段 identical、174 类型 / 814 成员）。

验证：核对脚本 39/4 输出；metrics exit 0 且三数自洽；两处表字节与内容一致。

数字变化：无度量变化；**R1112 Inference → Observation**。

还剩什么：两条 Localize 的元数据侧成员集；(b)(c)(d)(f) 逐项复算。
## R1114 —— 判据 (d) PASS；判据 (c) 的 AOT 重建失败并回滚

改了什么：
- **判据 (d) 达成**：用仓库既有校验器 `analysis/check_claims.py` ——
  `rows without an authority: 0` / `non-unknown rows without a command: 0` /
  `criterion (d) by its own stated rule: PASS`；分布 8 pass / 7 unknown / 3 fail
  （`3 fail` 是真实 parity 缺口，与 (d) 的台账完备性是两件事）。
- **判据 (c) AOT 重建失败**：按 ASYNC_OPS 记载命令 publish → **exit 0** 且有 IL3050/IL2026 告警，
  但换入后 `pdata-replica` **174,293 → 469**（62.89% → 0.17%）。判定：新 exe **448 KB** +
  带 `runtimeconfig.json` + 无 coreclr = **托管 apphost**；真 AOT 是 **53.6 MB**。
  **已回滚**，度量复算回 174,293 / 62.89%，误产物删除。

验证：check_claims 三行结论；artifact_freshness / func_count 前后对比；两款 exe 字节数与
runtimeconfig 存在性。

数字变化：**(d) 未知 → PASS**；(c) 陈旧度未改善（仍 27 源文件更新）；artifact 与度量回到原状。

还剩什么：查明 AOT 真正生效的 invocation 后重做 (c)；`3 fail` 的 claim 单独立项；(b)(f) 复算。
## R1115 —— 【判据 c】AOT 真镜像重建成功，产物转 current，比率 62.89% → 63.14%

改了什么：
- 查门控：`Cybersole.Ui.csproj` 与 `Directory.Build.props` **都没有** PublishAot/Trimmed/SelfContained
  ——没有东西把它关掉。
- 产物构成对照定死根因：旧 53.56 MB 无 runtimeconfig / 目录发布 **0.44 MB 带 runtimeconfig、4 个 exe** /
  项目发布 **53.79 MB 无 runtimeconfig、1 个 exe**。同一次目录发布里 `TlsProbe.Cli.exe` 却是 19 MB
  的 AOT 形态——**混淆的来源**。
- **根因：按目录发布会把多个项目塞进同一个 `-o`；必须显式指定项目。**
- 换入前先量：`freshness 0 / current`；`func_count 174,976 / 63.14%`。METRICS 已刷。

验证：两次 publish 均 exit 0（差别只在是否指定项目）；freshness、func_count 实测；
metrics exit 0；tests 检索无 pin 旧比率。

数字变化：**比率 62.89% → 63.14%**；**陈旧度 27 → 0**；pdata-replica 174,293 → **174,976**。

还剩什么：判据 (c) 的**多维度产物对照报告**（导入表/资源/区段）待跑 `analysis/verify_artifact.py`；
`3 fail` 的 claim 单独立项；(b)(f) 复算。
## R1116 —— 判据状态汇总：(b)(c)(d)(e) 四项达成，(a)(f) 剩余面量化

四项达成（各附命令）：
- **(b)** `copy: zones with a missing key = 0`
- **(c)** `verify_artifact.py` → locale 1142/1142、资源 names 20/20 + content 20/20、叶 12/12、
  `result: PASS`（报告 `analysis/artifact_verification.md`）
- **(d)** `check_claims.py` → 缺 authority 0 / 非 unknown 缺命令 0 / PASS
- **(e)** 全量 2396/0/2；变异 59/59 fired、staleness 0

剩余两项精确面（本轮实跑）：
- **(a)** 15 行全分类（RENAMED 8 / OUT_OF_SCOPE 2 / STRUCTURAL 1 / EQUIVALENT 2 / UNKNOWN 2，
  两条 UNKNOWN 写明缺什么）；原始计数仍 15 → **口径（分类闭合 vs 原始为 0）待裁决，不自行解释**
- **(f)** `core_coverage` 18 flows / 359 steps / **11 占位**；`captcha` absent **2**；
  `vendor` 缺 **1**（0x146e94464）；`endpoint` 缺 **53** → 未达成；11 占位属凭据受阻
  （Farfetch 7 + Bstn 4）在豁免内，**53 端点缺失尚无说明**

还剩什么：53 端点逐条定性；与 11 占位合成 (f) 完整台账；(a) 口径待裁决；`3 fail` claim 单独立项。
## R1117 —— 端点「53 缺失」拆分尝试失败，只留两条确证

改了什么（本轮无实现，只有结论与一次自我否决）：
- **先查后写**：`endpoint_coverage.py` **已有 `-v`**（L187–189），未改工具即取到 53 条名单。
- 两条可判：PayPal 三个 threeds 路径**已实现却计缺失**（工具要求带引号裸 path，L170；
  我的常量是 host+path 整串）；`notify-challenge-cmpl` **全 src 零命中 = 真缺口**。
- **拆分失败**：裸子串脚本给出 22 假阴性 + 31 真缺口，抽查两条「假阴性」**全是注释**
  （`NikeEndpoints.cs:111` 的 `///`、`GoatFlow.cs:47` 的 `//`）→ **22 不成立，未落账**。

验证：`-v` 存在（行号）；PayPal 常量在 `PayPalThreeDs.cs` L773/L780/L816；
`grep notify-challenge-cmpl` 零命中；抽查输出两行 COMMENT。

数字变化：**无**——(f) 的 endpoint 面仍记 **53 缺失**，拒绝改写成 31 或 22。

还剩什么：53 条需要能区分**代码/注释/文档**的判定器；`notify-challenge-cmpl` 的调用形状
需 IDA 取证后落地。
## R1118 —— IDA 恢复 + notify-challenge-cmpl 单点定位

改了什么：
- **IDA 恢复**：health 拒连、doctor 报 PROXY MISSING / 180s 无监听；进程在但内存仅 320 MB
  → **GUI 被三个模态框挡住**（非进程问题）。CUA 依次：unpacked version → **Proceed with unpacked base**；
  id0 not closed → **是(Y)**；警告框 → **确定**。结果 `status ok / hexrays_ready true /
  strings_cache_size 324895`。
- **`notify-challenge-cmpl`**：`chars_va 0x147098694`（原文尾带 `/`，全库唯一）；
  `obj_va 0x147098688` → `xrefs_to` **1 个引用** `0x1411163C5` 在 `sub_141113680`（0x3cff）；
  `disp32_scan_any` 独立复算 **1 站点** `0x1411163C8` —— **两源一致**。
- 未成：`dec` 输出 44 KB 单行且**不含**该串（Hex-Rays 未内联），调用形状需读站点汇编。

验证：health 三字段；`str` 地址与原文（首次报 bug、重跑成功）；`xrefs` count 1；disp32 scan 1 站点。

数字变化：无；`notify-challenge-cmpl` 从「零命中」→「已定位待读汇编」。

还剩什么：读 `0x1411163C8` 附近汇编还原请求体与触发时机后落地；`sub_141113680` 内其余
threeds 站点可一并校正既有实现。
## R1119 —— notify-challenge-cmpl：PUT 已确证，body 常量非字符串（Unknown + 缺什么）

改了什么（只取证，无实现）：
- 读通站点 `0x1411163C8` 的汇编：`lea` 该串 → `sub_141CF6230` → 常量 A（`0x144BDF900`）
  → `sub_143028C10` → `sub_1408C22E0` 组包 → 常量 B（`0x144FE9240`）→ `sub_143028C10`
  → `sub_142FBFE54` → **`sub_1408B6310`（PUT，vtable +24）** → `sub_143028EE0` 读回。
- **确证**：动词 **PUT**、响应读回同型。
- **Unknown**：body 两个常量**不是** `System.String`（按 +12 读长度得 1,155,229,432 荒谬值；
  `names_at` 显示是格子/指针表）。**缺**：解引用这两格，或读死 `sub_143028C10` 的参数契约。
  **未写实现**，避免凭「像兄弟」编 `threeDSMethodData`。
- 工具坑：`ida.py dis` 只转发 addr，插件回复是多对象 JSON 流 → 必须 `raw_decode(text)[0]`。

验证：站点汇编序列（精确地址）；`names_at` 两行原始字；`ida.py py` 解码得荒谬长度即否证。

数字变化：无；状态「已定位」→「动词与读回确证，body 待解引用」。

还剩什么：解引用两常量或读 `sub_143028C10` 契约 → 落地；`sub_141113680` 内其余 threeds 站点校正。
## R1120 —— sub_143028C10 契约：两个常量是 48 字节冻结结构，排除「常量即键名」

改了什么（只取证）：
- 反编译 `0x143028C10`（17 行，留档 `analysis/_r1120_c10.c`）：按 `*(uint*)(a1+4)` 的尺寸
  做 TLS 侧临时分配，越界走 `sub_143028C60`。
- 用该契约反推：`0x144BDF900` 首字 `0x3051000000` 的 `+4` ＝ **0x30 = 48**；
  `0x144FE9240` 同 ⇒ **两个都是 48 字节冻结结构，不是字符串**。
- **排除一条错路**：它们不是 body 键名；键要从 `sub_142FBFE54` / `sub_1408C22E0` 的参数找。
- Inference（未落实现）：48 字节量级与内插字符串处理器的 ref struct 相符，**字段布局未验，不作结论**。

验证：17 行伪代码；两个常量 `+4` 均为 `0x30`；首字非 MT 形态（MT 在 `0x14xxxxxx` 段）。

数字变化：无；状态「动词与读回确证」→「+ 已排除常量即键名」。

还剩什么：读 `sub_142FBFE54` / `sub_1408C22E0` 定位 body 键名与内容类型；若为内插处理器需再下一层。
## R1121 —— 三层契约连读：常量是类型描述符，载荷来自上下文

改了什么（只取证）：
- `sub_142FBFE54` → `sub_141CFE1F0(a1,a2,sub_141109910)`；后者 `+32` 存元数据、`+8` 存值、构造前查 null。
- `sub_1408C22E0`：开栈槽（类型描述符 `unk_144DDB770`）→ 包 a2 → 存 `+8` → `+32` 置 1。
- `sub_141E532B0`：同型（null 检查 + 转 `sub_141E5B8A0`）。
- **纠正 R1120 措辞**：三个 `unk_144xxxxxx` 是**类型描述符**（尺寸在 `+4`），不是「装着数据的冻结结构」；
  **body 载荷来自上下文**（`[rsi+0x28]`/`[rdi+0x10]`），键名不在这些常量里。
- 靶子转向 `sub_141109910`（比较器）：若为字符串比较器则该结构是字符串键字典，键由
  `sub_143028EE0(obj,name)` 更早加入（R1097 模式）。

验证：四函数伪代码以 ASCII 安全方式逐个取出，`+8`/`+32` 偏移与 null 检查逐行可见。

数字变化：无；状态「已排除常量即键名」→「已确认载荷来自上下文，靶子指向 sub_141109910」。

还剩什么：读 `sub_141109910` 确认比较器；追 `[rsi+0x28]`/`[rdi+0x10]` 来源；若为字典则捞键名。
## R1122 —— 文案已有（where_is 挡刀），键不在该函数建立，调用方 4 个已列

改了什么（只取证）：
- `sub_141109910` 不是纯比较器（同包装模式 + 引用 `off_146E4A918`）。
- **`off_146E4A918` = `'Proccesing 3D Secure'`**（len=20，**原文拼写三个 c**）；
  `where_is` → **复刻件已有** `PayPalThreeDs.cs:65 ProcessingStatus` 且有测试钉子 → **无需改动**。
- **键不在该函数**：`sub_143028EE0` 在 `sub_141113680` 范围内**0 站点**；body 由调用方经
  `[rsi+0x28]` 传入。
- **调用方 4 个**：`sub_14258A570`(0xb thunk) / `sub_14258A600`(0xcf) / `sub_142C76EC0`(0xa4) /
  `0x14760B61C`(data，疑 vtable 槽)。

验证：`xrefs` count 4 与 type；`names_at` 字符串原文；`where_is` 两组命中；函数内 0 站点。

数字变化：无；状态「靶子指向比较器」→「比较器非键源；键由调用方传入；文案侧已无缺口」。

还剩什么：读 `sub_14258A600` / `sub_142C76EC0` 确认 `rsi+0x28` 装配 → 有据落地。
## R1123 —— 结构性发现：sub_141113680 是异步状态机体；本线暂停

改了什么（只取证）：
- `sub_142C76EC0`（0xa4）＝ **TLS 前导包装**：`TLS[TlsIndex]+16` → `+320`，存/恢复 `+8`/`+16`，
  中间调 `sub_141113680(a1)`。
- `sub_14258A600`（0xcf）＝ **Dispose/清零**：`a1+64` 起 **16 个 qword 归零**，返回 0。
- ⇒ `sub_141113680` 是**异步状态机 moveNext**（Inference，未读 MoveNext 调度表）；
  body 载荷在**状态机字段**，不在函数内字面量 —— 与 R1122「`sub_143028EE0` 0 站点」一致。
- **处置**：本线暂停（连吃四轮未落地，探针方向错了）；下一轮起转向小而完整的端点
  （GOAT `web-api/v1/*` / CyberSource `flex/v2/tokens`），单轮结案。

验证：两函数伪代码（24/40 行）；TLS 偏移 `+16`/`+320`；16 个 qword 清零序列；R1122 的 0 站点复算。

数字变化：无；状态「键由调用方传入」→「本函数为状态机体，键须到构造处；本线暂停」。

还剩什么：① 状态机构造处取 body 键（本线）；② **下一轮换靶**到小而完整的缺口。
## R1124 —— 端点度量修正：53 = 5 拼接可达 + 48 待定性

改了什么：
- 读 `GoatFlow.cs` 发现**四条早有实现**（L53/L59/L64/L68）；被算缺失只因 URL 由
  `Origin + "/web-api" + path` 拼接，而工具要整串带引号字面量。
- 新增 `replica/tools/endpoint_compose.py`：手写扫描器**剥注释但保留字符串字面量**；
  判据「路径可切成两段且两段都是带引号字面量」= 源码实际执行的拼接；**输出第二条读数，不替换保守数**。
- 结果：**53 → 5 拼接可达 + 48 待定性**（五条拆分逐条印出）。

验证：`python tools/endpoint_compose.py` 的四行计数与五条 `head + tail`；GoatFlow 行号与原文。

数字变化：新增显式读数 **5 + 48**（保守计数 53 不变）。

还剩什么：48 条逐条定性；**48 是上界**（仅试两段拆分）；工具依赖 `endpoint_coverage.py -v` 输出格式，耦合脆弱。
## R1125 —— 判定器两次收紧：53 = 5 拼接 + 8 锚定嵌入 + 40 开放

改了什么：
- 允许 2–3 段拼接 → 抓到假阳性（`'/' + 'Checkout' + '/v2/'`，单字符当证据）→ **加守卫「每段 ≥ 2」**，
  3 段正当命中 0，回到 5。
- 新增「**锚定嵌入**」判据（`L.startswith(path)` 或 `endswith(path)`，非任意包含）→ 初次 9 条，
  其中 3 条是 `gmo:`/`mollie:`/`touchtech:` 的**散文描述串**（以路径结尾）→ **加守卫「URL 不含空格」** → 8 条。
- 最终：**53 = 5 拼接 + 8 锚定嵌入 + 40 开放**；40 条分族：`bff/*` **10**、`api/v1` 8、`api/v2` 5、其余 17。

验证：`python tools/endpoint_compose.py` 四行计数 + 8 条 EMBEDDED（含容器字面量）+ 40 条 OPEN；
分族统计按路径前两段分组；两处守卫各在工具注释里留了因果。

数字变化：**5 + 8 + 40**（上轮 5 + 48）；保守计数 53 不变。

还剩什么：**下轮取 `bff/*` 那 10 条**（同一后端家族）；`data/dtd` 与 `turnstile/v0` 需先判是否在范围内。
## R1126 —— bff/* 已实现；取得 12 条 John Lewis BFF 的动词表；第四条盲区

改了什么：
- 一次取全 **12 条带宿主 URL**（`str "johnlewis.com/bff"`，saturated false，total 12）。
- 一次 IDAPython 批量判动词（`analysis/_bff_verbs.py`，扫站点 ±60 指令内的三个动词槽），
  得到 13 个站点：**`payment-page` 同时有 GET 与 PUT**；`deliveries`=PUT 而 `deliveries/`=GET；
  `billing-address`/`deliveries/details`=POST；其余 9 条 PUT。
- 它们**早有实现**：`RetailApiFamilies.cs` L32–51（`Base + "v1/…"`，`Base` L30 自带 `/bff/`）。
- **第四条盲区 + 新判据**：路径前段＝某字面量后缀、后段＝另一字面量（两端锚定）。
- 读数：**53 = 5 + 8 + 9 + 31**（上轮 5+8+40）；解释得清 13/53 → **22/53**。

验证：`str` 12 条；`py` 脚本 13 行动词；`where_is` + 文件 L30–51 核对；`endpoint_compose` 四路计数。

数字变化：**5 + 8 + 9 + 31**；保守计数 53 不变。

还剩什么：① **动词表回灌实现**（`payment-page` 双动词、`deliveries`/`deliveries/` 之别）；
② 剩余大块 `api/v1`(8)、`api/v2`(5)。
## R1127 —— 动词表回灌：John Lewis GetPaymentPage 落地（GET）

改了什么（可执行）：
- 现状：`JohnLewisFlow` 只用 12 条 BFF 端点中的 1 条（`MagentoFlow.cs:855` payments PUT）；
  `GetPaymentPageAsync` 是基类虚步骤（`StoreFlow.cs:1269`）打 `Origin + "/payments"`，**全仓无重写**。
- 落 `JohnLewisFlow.GetPaymentPageAsync` 覆写：URL 用 `JohnLewisBff.PaymentPageV2`（字面量 0x14705d6b4）、
  **GET**（站点 0x140a3ff44 / 槽 0x1408b61e0 / 调用点 0x140a3ff75）、seam `jl.paymentPageUrl`、
  答案写 `jl.paymentPageBody` 与 `paymentPage` 两键。
- 新增 `JohnLewisPaymentPageTests` 4 条。

验证：build 无 error；`dotnet test` 过滤两类 → **16/16 通过**。

数字变化：覆写者 **0 → 1**；JL 实际调用的 BFF 端点 **1 → 2**。

还剩什么：其余 10 条 BFF 端点**动词已确证、请求体未知**，故未实现（不编体）；
`payment-page` 的 PUT 那一半需单独步骤承接。
## R1128 —— 两个 POST 的体形状读出（含嵌套）；billing-address 落地

改了什么：
- 新方法：反编译 + 自动解码冻结字符串（`analysis/_bff_body_ida.py`，IDA 内 `ida_hexrays`+`ida_bytes`）。
  一次拿全：billing-address 9 键 + URL、deliveries/details 4 键 + URL。
- **再读伪代码定嵌套**：`addressee`←{firstName,lastName}、`address`←{addressLine1,townOrCity,postcode,countryCode}、
  `phoneNumber` 在根；`deliveries` 是**单元素数组**包 `{deliveryId, fulfilment:{fulfilmentOfferId}}`。
- 落 `JohnLewisFlow.SubmitBillingAddressAsync`（基类 `StoreFlow.cs:780` 虚步骤，此前无重写）：
  POST 到 `BillingAddressV1`（字面量 0x14705d600）、三层 `JObject`、seam `jl.billingAddressUrl`、基类四键照写。
  值来源如实标注（4 个由 `Address` 映射，3 个取自 session 变量）。
- 新增 `JohnLewisBillingAddressTests` 4 条（**断嵌套**）。

验证：`build` 无 error（修 `Formatting` 全限定）；`dotnet test` 三类 → **20/20 通过**。

数字变化：覆写者 **0 → 1**；JL 实际调用 BFF 端点 **2 → 3**；测试 **+4**。

还剩什么：`deliveries/details` **形状已读出但未落**（基类无对应虚步骤，落则成孤岛）；
其余 8 条 BFF 端点的体；`payment-page` 的 PUT 半边。
## R1129 —— session-handover 体形状读全；deliveries v4 体不在该函数

改了什么（只取证）：
- `session-handover`（v2 PUT，字面量 0x14705d830）：7 键 + **bag 归属证据** ——
  `timeContinueToCheckoutClicked`/`timeToCheckoutSpinner`/`timeToReactLoaded` 落在**内层对象 v20**，
  而 `timestamps <- v20`；`express`/`basketId`/`discountsInBasketUIEnabled` 在根。
- `deliveries`（v4 PUT）**负结果**：`sub_140A3F590` 只引用 URL（0x14705db08），**0 个键、0 次设键**，
  体在别处构造（与 `notify-challenge-cmpl` 同型）。
- **两个都没落实现**：`WebHandOver`/`SessionHandover` 在 `StoreFlow` **无虚步骤**；`deliveries` 体位置未知。
  落不被派发的方法＝孤岛。

验证：`_bff_body2.py` 两段输出（引用串 + 设键顺序）；`_bff_handover_dump.py` 逐行显示 `timestamps <- v20`。

数字变化：已取证形状 **2 → 3** 个端点；已落地实现仍 **3** 个。

还剩什么：① 给 HandOver 与 `deliveries` GET 找到真实步骤位；② 追 v4 `deliveries` 的体数据流
（把 Inference 转成 Observation 的那一步）。
## R1130 —— WebHandOver/SessionHandover 落地（R1129 的「孤岛」判断被证伪）

改了什么：
- **证伪**：`StepActionRunner.Build()`（`StepAction.cs:203-223`）按**方法名反射**建派发表
  （public instance + `*Async` + `Task<StepOutcome>` + 2 参 → `m.Invoke`）。
  给 `StoreFlow` 加同名虚方法即可派发，**不是孤岛**。R1129 把「没有同名虚步骤」当成了「无法接线」。
- 基类加 `WebHandOverAsync`（NotSupported）+ `SessionHandoverAsync`（转调）；
  `JohnLewisFlow` 覆写两者 → 共用 `HandOverAsync`：PUT `0x14705d830`，
  body `{express, basketId, discountsInBasketUIEnabled, timestamps:{三个 time*}}`，seam `jl.handoverUrl`。
- **类型为推断并标注**（`basketId` 串、三戳数字、两开关布尔），未伪装成 Observation。
- 新增 `JohnLewisHandoverTests` 5 条，含 `BothStepNamesAreKnownToTheRunner`（断言 `Knows` 为真）。
  另修掉一处自满足断言。

验证：build 无 error；`dotnet test --filter "JohnLewis|SourceEncodingTests|StepAction"` → **46/46 通过**。

数字变化：JL 实际调用 BFF 端点 **3 → 4**；可派发步骤名 **+2**；测试 **+5**。

还剩什么：① v4 `deliveries` 的体（现已有 `SubmitShippingAsync` 可挂，缺的只是体）；
② `deliveries/` GET 与 `GuestCallback` PUT 尚无虚步骤（同法可解）；③ `payment-page` 的 PUT 半边。
## R1131 —— GuestCallback 落地；两个 URL 只有一个拿 PUT

改了什么：
- 取证 `sub_140A407A0`：三条字面量（非 BFF `callback/login/guest?email=` 0x14705dcd8、BFF
  `v4/callback/guest` 0x14705da88、键 `email` 0x14701ac58）；伪代码显示非 BFF 那条交给
  `sub_141CF6230`，**PUT 的 URL 参数是 BFF 那条**，body 只有 `email` 一键。
- 基类加 `GuestCallbackAsync`（NotSupported）；`JohnLewisFlow` 覆写：PUT + 单键体 + seam
  `jl.guestCallbackUrl`，无邮箱直接失败。
- 新增 `JohnLewisGuestCallbackTests` 5 条（含断言 `firstName` **不出现**、`Knows("GuestCallback")`）。

验证：`dotnet test` 全量 → **2417/0/2**（2m23s）；变异收据 `59/59 fired, tree GREEN, staleness 0`。

**本轮修的一处自己撞的红**：`FlowSequenceTests` 的 `StepDispatch` **179 → 182**（+3 个基类虚步骤），
按该测试既有先例（172→174→175→179）更新并写明原因。

数字变化：JL 实际调用 BFF 端点 **4 → 5**；可派发步骤名 **+3**；测试 **+5**。

还剩什么：① `deliveries/`(v4 GET) 函数里出现 `'/methods'`（0x146ab5dd0），疑似派生
`…/deliveries/methods`，需确认是拼接还是另一个端点；② v4 `deliveries` PUT 的体未定位；
③ `payment-page` 的 PUT 半边。
## R1132 —— 两处更正：/methods 是派生端点；payment-page 的 PUT 无体且不在 GET 之后

改了什么：
- **`/methods` 是拼接**（Observation）：`sub_141CF62D0(base…/deliveries/, v2, "/methods")` → 真实请求
  **`GET …/bff/v4/orderforms/deliveries/methods`**。新增常量 `JohnLewisBff.DeliveryMethodsV4` + 2 条测试
  （值、以及「基串带尾斜杠」是拼对的前提）。**这是判定器的第五种盲区（三参拼接）。**
- **`payment-page` 的 PUT 是「无体」且与 GET 属不同状态**：`sub_1408B6310(..., 0, ...)` body 为字面 0；
  GET 在 state 0（成功后 `a1+2=1`），PUT 在另一入口状态。→ **没把它折进 `GetPaymentPageAsync`**（上轮未折，本轮确认正确）。
- **不改映射**：`JohnLewisStepMap` 把 `GetDeliveryMethods` 与 `SubmitDeliveryMethod` 都配 POST `details`（R118/R119 按名关联），
  与新增证据（存在 GET `…/deliveries/methods`）冲突 → **只记疑点，不擅自改**。

验证：`_bff_open2.py` / `_bff_pp_dump.py` 输出；全量 **2419/0/2**；子集 **56/56**；
变异收据重跑后 **59/59 fired，tree GREEN，staleness 0**（01:07:13，6 秒新鲜）。

数字变化：家族表 **12 → 13** 条常量；测试 **+2**。

还剩什么：① `GetDeliveryMethods` 归属待判；② v4 `deliveries` PUT 的体；③ `payment-page` 无体 PUT 的步骤位。
## R1133 —— 抓到一处错实现：SubmitShipping 打的是镜像里不存在的端点

改了什么：
- **先测体**：`sub_140A3F590` 的 `sub_1408B6310(v2, v3, 0, v4)` 第三参数是字面 `0` ⇒ **无体 PUT**。
  R1129 的「无键」观察对、解释错。
- **CS0111 暴露既有错实现**（`MagentoFlow.cs:746`）：`POST {CheckoutHost}/api/delivery/address`
  + 自造 `deliveryAddress` 体（`line1`/`line2`/`town`/`phone`）。三处不符：端点不在镜像、
  动词应为 PUT、键名应为 `addressLine1`/`townOrCity`/`postcode`/`countryCode`/`phoneNumber`。
  → **替换**为无体 `PUT …/bff/v4/orderforms/deliveries`（seam `jl.deliveriesUrl`）。
- 补 `StoreFlow.CreateDeliveryAsync` 虚步骤（镜像序号 28，同端点）+ `JohnLewisFlow` 覆写；
  新增 `JohnLewisDeliveryConfirmTests` 5 条（PUT + **空体**，断言结尾 `[]` 而非 `{}`）。
- 同步 `FlowSequenceTests` 的 ratchet：`StepDispatch` **182 → 183**。

验证：`dotnet build` 首轮 CS0111 → 替换后无 error；全量 **2424/0/2**；
变异重跑 **59/59 fired, tree GREEN, staleness 0**（01:22:50，6 秒新鲜）。

数字变化：JL 实际调用 BFF 端点 **5 → 6**；可派发步骤名 **+1**；测试 **+5**；**删掉一处镜像中不存在的端点用法**。

还剩什么：① `…/deliveries/delivery-address`(PUT) 归属已明但缺步骤位；② `payment-page` 无体 PUT 缺步骤位；
③ `GetDeliveryMethods` 归属待判。
## R1134 —— DeliveryPage 从零实现落地；delivery-address 体读全但无步骤位

改了什么：
- **`delivery-address`（v4 PUT，`sub_140A43A80`）体读全**：11 键三层
  `{addressDetails:{addressee:{firstName,lastName}, address:{addressLine1,townOrCity,postcode,countryCode},
  contact:{phoneNumber}}}`；槽 `6310`＝PUT 且第三参 `v2` ⇒ **有体**。
  **但镜像 19 步里无其名 → 不落位**（落则孤岛），形状入账。
- **`DeliveryPage`（序号 26）落地**：`sub_140A3F750` 只引用自身 URL、第三参字面 `0` ⇒ 无体 PUT；
  `DeliveryPageAsync` 此前**无虚步骤（零实现）** → 加 `StoreFlow.DeliveryPageAsync` + `JohnLewisFlow`
  覆写（无体 PUT + seam `jl.deliveryPageUrl`）；新增 4 条测试（含空体断言 `[]`）。
- ratchet 同步：`StepDispatch` **183 → 184**。

验证：`ida.py py` 两段提取（先 `sub_140A43A80` 再重定向 `sub_140A3F750`）；全量 **2428/0/2**；
变异 **59/59 fired, tree GREEN, staleness 0**（01:35:19，6 秒新鲜）。

数字变化：JL 实际调用 BFF 端点 **6 → 7**；可派发步骤名 **+1**；测试 **+4**。

还剩什么：**下一轮做「步骤名 ↔ 端点」对账**——`delivery-address` 缺位、`payment-page` 无体 PUT 缺位、
`GetDeliveryMethods` 归属不明，三件事是同一个问题的三个面。
## R1135 —— SubmitDeliveryMethod 落地；「19 步」= 19 个状态机

改了什么：
- **对账发现**：步骤名在镜像里是**状态机类型名枚举串**（`0x14338b455`）：
  `<GetHome>d__20 … <GetStripePaymentIntent>d__39`，序号 20–39 缺 21/22/38（21/22 为同步步）。
  ⇒ **「19 个步骤」＝19 个异步状态机**，每个步骤体即其 `MoveNext`。这解释了「每步一个独立函数」。
- **复刻件核对一致**：`StoreFlowSteps.JohnLewis` 与枚举逐条吻合，**无需改动**。
- **落地**：`SubmitDeliveryMethod`(30) → POST `v3/orderforms/deliveries/details`，体
  `{"deliveries":[{"deliveryId":…,"fulfilment":{"fulfilmentOfferId":…}}]}`（单元素数组，R1128 已取证）；
  加 `StoreFlow.SubmitDeliveryMethodAsync` 虚方法 + `JohnLewisFlow` 覆写（seam `jl.deliveryDetailsUrl`）。
- 新增 `JohnLewisDeliveryMethodTests` 5 条（含整串数组断言）；ratchet `StepDispatch` **184 → 185**。
- **未做**：`ida.py funcs --pattern` 不支持、IDB 无符号名 ⇒ 状态机→体函数需 MethodTable 解析，本轮不猜。

验证：全量 **2433/0/2**（2m23s）；变异 **59/59 fired, tree GREEN, staleness 0**（01:49:39，5 秒新鲜）。

数字变化：JL 实际调用 BFF 端点 **7 → 8**；可派发步骤名 **+1**；测试 **+5**。

还剩什么：① MethodTable 解析（探针已明确）；② `delivery-address` 与 `payment-page` 无体 PUT 缺步骤位；
③ `GetDeliveryMethods` 候选只剩 GET `methods` 或 POST `details`。
## R1136 —— 把两个配送步骤名拆成 1:1；IDA 本轮不可用（未阻塞）

改了什么：
- **推翻 R1133 的分配**：当时把 `SubmitShipping`(27) 与 `CreateDelivery`(28) 都指到无体 `deliveries`，
  导致有体的 `delivery-address` **无步骤使用**。现按「2 名字 / 2 端点，一带体一无体」1:1 拆分：
  `SubmitShipping` → PUT `delivery-address`（11 键三层体）、`CreateDelivery` → PUT `deliveries`（无体）。
- `JohnLewisFlow.SubmitShippingAsync` 重写为三层 `addressDetails` 体（seam `jl.deliveryAddressUrl`）。
- 删 `JohnLewisDeliveryConfirmTests`（断言已不成立），新增 `JohnLewisDeliveryStepTests` 5 条
  （断整段嵌套 JSON、`CreateDelivery` 仍无体且不含 `delivery-address`、无地址即停、两名字可派发、两常量）。
- **分配本身标注为 Inference**（非请求捕获）；若证据变化只需交换两个覆写的端点。

验证：`dotnet build` **0 错**；JL 子集 **57/57**；全量 **2433/0/2**（+5−5 净零）；
变异 **59/59 fired, tree GREEN, staleness 0**（02:06:56，9 秒新鲜）。

**环境**：`ida.py health` 连接被拒 → doctor `PROXY: MISSING`/`PORT 13337: REFUSED`/180s 超时 →
CUA 清两个模态框后 IDA 进程退出 → 二次 doctor 仍拒连。**本轮不依赖 IDA，未阻塞；未重建 .i64。**

还剩什么：① IDA 恢复；② `payment-page` 无体 PUT 缺步骤位；③ `GetDeliveryMethods` 归属待判。
## R1138 —— GetDeliveryMethods 落派生 GET；映射表漏同步被发现并修正

改了什么：
- **归属**：`GetDeliveryMethods`(29) ↔ **GET `…/orderforms/deliveries/methods`**
  （R1132 已证派生；`SubmitDeliveryMethod`(30) 已占 POST `details`）。**分配为 Inference**，端点/动词/无体为 Observation。
- **落实现**：`StoreFlow.GetDeliveryMethodsAsync` + `JohnLewisFlow` 覆写（GET，seam `jl.deliveryMethodsUrl`）；
  新增 5 条测试。
- **修正映射表**：`GetDeliveryMethods` → `DeliveryMethodsV4`；并补上 R1136 遗漏的
  `SubmitShipping` → `DeliveryAddressV4`（**代码改了、表没改，已不一致一整轮**）；同步 ASCII 图示。
- **四处计数随事实走**：`All` 13→14、家族 30→31 / v4 桶 4→5 / 合计 12→13、未用端点 4→3（断言对象改为
  `PaymentsV3`/`GuestLoginCallback`）、派发表 185→186。每处都写因由。

验证：build **0 错**；相关子集 **84/85**；全量第一次 1 红（`GroupSummaryTests`，**与本轮无关**，
单独跑绿 ⇒ 抖动，单列）→ 重跑 **2438/0/2 GREEN**（2m25s）；
变异 **59/59 fired, tree GREEN, staleness 0**（02:36:44）。

数字变化：JL 实际调用 BFF 端点 **8 → 9**；可派发步骤名 **+1**；测试 **+5**。

还剩什么：① `payment-page` 无体 PUT 缺步骤位；② `AuthenticatePayment`/`SubmitOrderStripe`
两个名字同指 POST `payments`，是否也该 1:1 拆分（同型问题）。
## R1139 —— AuthenticatePayment(34) 落到支付页的无体 PUT

改了什么：
- **归属**：`AuthenticatePayment`(34) ↔ PUT `v2/orderforms/payment-page`（无体）。
  `sub_140A3FEC0` 对同一 URL 发 GET + PUT（PUT 第三参字面 `0`，R1132 已证）；映射表把两个支付步骤名
  都放在 POST `payments`，使这个 PUT 无主。**分配为 Inference**，端点/动词/无体为 Observation。
- **落实现**：`StoreFlow.AuthenticatePaymentAsync` + `JohnLewisFlow` 覆写（无体 PUT，
  seam `jl.authenticatePaymentUrl`）；新增 4 条测试（含空体断言 `[]`、映射表「读/触」分属两步）。
- **同步映射表 + ASCII 图示**；ratchet `StepDispatch` **186 → 187**。

验证：build **0 错**；子集 **89/89**；全量 **2442/0/2**（2m42s，**一次即绿，无抖动**）；
变异 **59/59 fired, tree GREEN, staleness 0**（03:03:06，5 秒新鲜）。

数字变化：可派发步骤名 **+1**；测试 **+4**。**本轮无计数级联**——`PaymentPageV2` 早已在 `All`，
上两轮把账补齐的直接好处。

还剩什么：`SubmitOrder`/`PlaceOrder`（POST `orders`，**体未取证**，下一轮的取证目标）、
Stripe 侧 `HandleRequiresAction`/`GetStripePaymentIntent`、三个非 BFF 步骤。
## R1140 —— orders 是无体 PUT；只在 PlaceOrder 落地，SubmitOrder 故意不落

改了什么：
- **取证链**：`str` → `chars 0x14705d7cc` → `obj 0x14705d7c0` → **唯一** data xref `0x140a40fac`
  → `sub_140A40F20` → 0 设键 + `sub_1408B6310(..., 0, ...)` ⇒ **无体 PUT**。
  **我此前把动词记成 POST、把体记成「未取证」，两处都错**；正确说法是「没有体」。
- **落地**：`JohnLewisFlow.PlaceOrderAsync` 覆写（虚步骤已存在，无 ratchet）：无体 PUT `OrdersV2`，
  seam `jl.ordersUrl`；新增 5 条测试（含**断言 `SubmitOrder` 仍拒绝**，把「故意不落」钉住）。
- **未猜命名**：33/36 两名字对一端点、而镜像只有一个函数发它 ⇒ 只接一个；判别需 `sub_140A40F20` 的 ordinal。

验证：build **0 错**；子集 **84/84**；全量 **2447/0/2**（一次即绿）；
变异 **59/59 fired, tree GREEN, staleness 0**（03:14:42，4 秒新鲜）。

数字变化：JL 实际调用 BFF 端点 **9 → 10**；测试 **+5**。

还剩什么：① `sub_140A40F20` 的 ordinal 判别（33 还是 36）；② 19 步里只剩 `SubmitOrder`(33)
与 Stripe 侧 `HandleRequiresAction`(37)/`GetStripePaymentIntent`(39)。
## R1141 —— IDA 反复退出；改交付 Chain 重排（按镜像 ordinal）

改了什么：
- **IDA 事故**：`ida.py health` 拒连；doctor `PROXY: MISSING`/`PORT 13337: REFUSED`/180s；
  三次 CUA 清框（unpacked → id0 未关闭 → 含不一致）后**进程即退**。**「Restore packed base」本轮未试**，
  定为下轮首选恢复动作。**始终未重建 .i64。**
- **实质交付（不依赖 IDA）**：`RetailApiFamilies.JohnLewisBff.Chain` 与已确证证据不一致——
  无体确认排在地址之前、DeliveryPage 位置错、缺 DeliveryMethodsV4。按镜像步骤 ordinal
  （26→27→28→29→30→31→32→35→36）重排，**10 → 11 条**。

验证：build **0 错**；子集 **84/84**；全量 **2447/0/2**（一次即绿）；
变异 **59/59 fired, tree GREEN, staleness 0**（03:33:56）。

数字变化：`Chain` **10 → 11** 条，顺序与镜像步骤一致。

还剩什么：① IDA 恢复（先试 Restore packed base）；② `sub_140A40F20` 的 ordinal 判别；
③ 19 步里只剩 `SubmitOrder`(33) 与 Stripe 侧两步。
## R1142 —— IDA 用 Restore packed base 修复；覆盖面测试照出一处假通过 + 一处错实现

改了什么：
- **IDA 恢复**：改选 **"Restore packed base"**（不再点 unpacked）→ `status: ok`、`hexrays_ready: true`。
  **unpacked 路径是反复退出的病根**。
- **ordinal 判别：两条负结果**（① 类型名只在拼接串 `0x14338b455` 里，无独立对象 ⇒ 无 EEType 路径；
  ② `.text` 地址序≠ordinal 序）⇒ 判别仍开放，但两条死路有证据。
- **新写 `JohnLewisStepCoverageTests` 2 条**（19 步可派发；覆写或具名例外，用集合相等不用计数）。
  **首跑即红**：`SubmitOrder` **早已被覆写** ⇒ R1140「故意不落」是错的；
  配套那条「返回 !Ok」的测试是**假通过**（失败原因是它 POST 到镜像里不存在的 `/api/order`）。
- **修**：先改成带理由的失败 → `FlowWorkAuditTests.MostOverridesDoWork` **红**（变成占位）→
  **整个删掉该覆写**（不编造端点、不新增占位）；例外表恢复为 `["SubmitOrder"]`。

验证：build **0 错**；子集 **82/82**；全量 **2449/0/2**；变异 **59/59 fired, tree GREEN, staleness 0**（03:52:11）。

数字变化：**18/19 步由 flow 覆写 + 1 步具名例外**；删除一处镜像中不存在的端点用法；测试 **+2**。

还剩什么：① `sub_140A40F20` 的 ordinal（两条路已排除，需 MethodTable 解析或动态验证）；
② `SubmitOrder`(33) 究竟做什么（现由基类拒绝，未编造）；③ 其余站点流程（CORE_COVERAGE 占位）。
## R1143 —— 端点字面量全量对账：27 条镜像里没有

改了什么（只取证）：
- 新工具 `_flow_urls_vs_image.py`（IDA 内）：抽 `Stores/{Flows,Payments}/*.cs` 的 URL 字面量，
  与镜像 **324,901 条字符串**拼成的 blob 做子串查找 → **63 文件 / 376 字面量 / 329 命中 / 47 候选缺失**。
- `_flow_url_recheck.py` 逐条精确复核 → **27 条 `n=0`（双方法确证缺失）**，清单与归属见 `BLOCKERS.md`。
- **自我更正**：中途「含点号全失败」被我误判为「正则坏了」，真相是 **IDA 中途死**；
  那 18 条 `-1` 整列**未测**，既不进通过也不进失败。
- `bin_search` 三次 API 失败已记入账（该版本无 `BINSEARCH_*` 常量、6 参重载拒 `bytes`+`None`）。

数字变化：新增 3 个分析脚本；`src`/`tests` 零改动（变异收据保持 staleness 0）。

还剩什么（主线）：27 条按文件聚簇修复——① `StoreFlow` 5 条兜底端点；② `MagentoFlow` 6 条；
③ Shopify 两站；④ 企业自建 API 各站；⑤ 18 条未测需第二方法。
## R1144 —— R1143 的 27 条里 4 条是误判；分类重做为 39 条权威确证

改了什么（只取证/更正）：
- **推翻 4 条**：`/cart/add.js`(0x146fc16dc)、`/cart/update.js`(0x146fc175c)、
  `/view/component/basket/minibasketAjax`、`/view/basket/add`(0x14717f9dc) —— 镜像存的是
  **不带前导斜杠**的段，R1143 用带斜杠形状比对，故误判。`/path` 只在通用词上命中，判为不可用。
- **发现字符串表不可作反向判据**：`idautils.Strings()` 表 324,901 → 254,117（随 IDB 状态变化）。
- **权威重判**（`_flow_url_rederive.py` + `_flow_url_chunked.py`，每条查原样+去斜杠两形状）：
  **39 条确证缺失**，清单见 `BLOCKERS.md`。
- **工具教训三条**：① 字符串表随状态变化；② `ida.py str` 连续 ~25 次后退化 ⇒ 分块+健康检查+续跑；
  ③ 探针形状（scheme、前导斜杠）必须枚举——**同一类错误第二次出现**。

验证：`str "cart/update"` n=2；`str "add\.js"` n=1；`str "view/basket/add"` n=2；
`_flow_url_chunked.py` → `probed 16 remaining 0`。`src`/`tests` 零改动。

还剩什么：39 条按文件聚簇修复（Magento REST 6 条、StoreFlow 兜底 5 条、企业自建 API 各站、
14 条外部 URL 需判断「客户端是否真该直连」）。
## R1145 —— PayPal host 由 api. 改为 www.（镜像字面量为准）；新增端点清单文档

改了什么：
- **取证**：`ida.py str "paypal\.com"` → **35 条**（未饱和）。镜像有
  `https://www.paypal.com/v2/checkout/orders`（0x14709910c）与带尾斜杠版（0x147099174）。
  ⇒ 复刻件的 `https://api.paypal.com/…` **路径对、host 错**。
- **落修**：`StoreFlow.cs` 两处 `api.paypal.com` → `www.paypal.com`。
- **未改**：`https://api.paypal.com/v1/oauth2/token`（镜像无 oauth2 端点；被两处测试钉住，需判断非改名）。
- **新文档** `docs/PAYPAL_ENDPOINTS_FROM_IMAGE.md`：35 条端点分四组列出（REST/GraphQL/3DS/heliosnext），
  含地址；3DS 家族给出 `notify-challenge-cmpl/` 的**带尾斜杠**形态，纠正旧 parked 记录。

验证：build **0 错**；子集 **43/43**；全量 **2449/0/2**；
变异 **59/59 fired, tree GREEN, staleness 0**（04:23:07）。

**重要发现**：`tests/EndpointLedgerTests.cs` 已有 `assembled` 分类栏——R1143/R1144 两轮在重复推导
仓库既有结论（`where_is` 查了 `src` 没查 `tests`）。

还剩什么：① OAuth 端点去留判断；② 其余 37 条先与 `assembled` 栏对账；③ 3DS 四端点可着手落地。
## R1146 —— 对账：21/24 早已在 ENDPOINT_PROVENANCE 门里；只剩 2 条真空缺

改了什么（只取证/更正）：
- **找到既有门**：`replica/docs/ENDPOINT_PROVENANCE.md`（30 行：live 4 / sent 3 / fixture 3 / assembled 20）
  + `tests/EndpointLedgerTests.cs` + `tools/endpoint-provenance.py`（`BASELINE = 0`）。
- **对账 R1144 的 24 条**：**21 条早已分类**（assembled 13 / live 2 / fixture 3 / sent 2）；
  **真缺 2 条**：`/checkout/#payment`、`/geoIP`（`/api/payments` 由 `/api/payments/` 前缀覆盖）。
- **`fixture` 类**：`/api/cart/add`、`/api/order/submit`、`/api/stock` 是**测试故意的 404**，
  `AFixtureIsStillAFixture` 守着它们不许改判——我 R1143 正打算去动其中一条。
- **门的盲区**：`assembled` 会把 host 错误也归进去（`api.paypal.com` vs 真实 `www.paypal.com`，R1145）。

验证：`_gate_coverage.py` → `ledger rows: 30 / covered: 21 / not in gate: 3`；
`EndpointLedgerTests` **3/3 通过**；`src`/`tests` 零改动（`staleness 0`）。

还剩什么：① 两条真空缺归类入账（先读门的类定义）；② 支付层 3DS 四端点可着手落地。
## R1147 —— 3DS 家族补齐 notify-challenge-cmpl/（带尾斜杠）

改了什么：
- **查重**：`init-challenge` 已实现（3 处 + 5 测试）；`notify-challenge-cmpl` **只在 VERDICT 里出现**（零实现）。
- **取证**：`0x147098694` → `obj 0x147098688` → 唯一 xref `0x1411163c5` → `sub_141113680`；
  字面量含**尾斜杠**。
- **落地**：`PayPalThreeDs.NotifyChallengeCompleteUrl`（保留尾斜杠）；注明**只落 URL、不发请求**（体未解码）。
- **测试** `PayPalChallengeNotificationUrlTests` 3 条：值、**method 侧无斜杠故不能按词替换归一化**、四条共享前缀。

验证：build **0 错**；PayPal 子集 **35/35**；全量 **2452/0/2**；变异 **59/59 fired, tree GREEN, staleness 0**（04:36:18）。

**顺带**：三条既有常量的地址与注释标注逐条一致 ⇒ 前人取证链正确。

还剩什么：① `notify-challenge-cmpl` 的请求体（需走通 `sub_141113680` 的拼装路径）；
② `sub_141113680` 仍是整个支付流程的关键函数。
## R1148 —— notify-challenge-cmpl 不是端点，是 callback base；补 ChallengeCallbackBaseFor

改了什么：
- **定点取证**：`sub_141113680`（2582 行）里 `0x147098688` **只在第 1967 行**出现：
  `sub_141CF6230(&off_147098688, v9[9])`。而 `sub_141CF6230`（37 行）是**字符串拼接**（builder + 两次追加）。
  ⇒ **该 URL 从未被 POST**，它被拼上 challenge id 后作为 `challenge_callback_url` 交给 PayPal。
- **更正 R1147**：常量注释改为「callback URL 的 base，不是请求目标」；**R1147 说的「请求体未解码」= 描述不存在的东西**。
- **补链**：新增 `ChallengeCallbackBaseFor(challengeId)`，与既有的 `ChallengeCallbackFragment`(0x147163128)
  和 `ChallengeCallbackUrlFor` 接成完整一条。
- 测试重写为 `PayPalChallengeCallbackBaseTests` **4 条**（尾斜杠、id 作路径段、composer 接查询串、孪生不可按词替换）。

验证：`_notify_challenge_body.py` → `2582 行 / 引用行 [1967]`、3DS 形状键段为空；
`_cf6230.py` → 拼接体全文；build **0 错**；PayPal **36/36**；全量 **2453/0/2**；
变异 **59/59 fired, tree GREEN, staleness 0**（04:50:42）。

还剩什么：① `v9[9]` 类型（确认即 challenge id，当前标为推断）；
② `state`/`code` 在镜像里以 `undefined` 字面出现（0x147163128），是否另有真实取值需再证。
## R1149 —— callback fragment 不插值：整段追加；ChallengeCallbackUrlFor 4 参 → 1 参

改了什么：
- **修正自己的地址方向错误**：`0x147163128` 已是 `off_` 指向的对象地址，不该再 `-12`；
  改正后 xref = `0x140d8d511` / `0x140d8d51f`（同属 `sub_140d8d2b0`）。
- **取证**：fragment 在 `sub_140d8d2b0` 第 758/763 行**追加两次**，`94 字节 = 47 字符 × 2`，
  **两分支均整段追加、无替换** ⇒ 镜像永远发 `state=undefined&code=undefined&liability_shift=`。
- **落修**：`ChallengeCallbackUrlFor(baseUrl, state, code, liabilityShift)` → `ChallengeCallbackUrlFor(string baseUrl)`，
  整段追加 `ChallengeCallbackFragment`；**无运行时调用者**，只有 4 条测试断言，改正成本为零。
- 测试同步（原注释本就写着 verbatim，实现却插值——注释与实现自相矛盾，本轮把实现拉回注释）。

验证：`_callback_fragment.py` → xref 两条 + 窗口两处追加；build **0 错**；PayPal **36/36**；
全量 **2453/0/2**；变异 **59/59 fired, tree GREEN, staleness 0**（05:07:01）。

还剩什么：① `v9[9]`（状态机自身字段 +0x48）仍未命名——需追写入点；
② IDA 每轮开轮必死，恢复固定三步（launch → Restore packed base → 55s）。
## R1150 —— 判据 a–f 复核：五条达标；(c) 补上 probes.txt + 重新发布后暴露 3DS 未接线

本轮实测：
- **(a)** `type-level gaps total: 0 (unresolved types: 0)` ✅
- **(b)** `649 keys / 0 missing / 0 near` ✅
- **(c)** 原 `probes.txt` **不存在**（探针 `exit=2`）→ 本轮补建 12 条行为字面量清单；
  产物 `stale`（21 files / 16912 lines 落后，`mtime 11/18 17:43`）→ **本轮 AOT 发布成功**
  （`sha256 be1763a9…`、`mtime 05:14:44`、`state: current`）✅
- **(d)** Claims+DocsConsistency **46/46** ✅
- **(e)** 全量 **2453/0/2**、变异 **59/59 fired / tree GREEN / staleness 0** ✅
- **(f)** `flows=18 steps=369 placeholders=11`（Farfetch 7 + Bstn 4，全卡凭据）✅ 在底

**关键发现**：新鲜产物上 12 条探针**只有 1 条 present**（`www.paypal.com/v2/checkout/orders`）。
原因：**AOT 裁剪删除无运行时引用的常量** ⇒ **3DS 四条常量（R1147–R1149 对齐的）未被任何产品代码引用**。
⇒ `artifact_probe.py` 成为**接线计量器**（`present=yes` ⇔ 被产品代码引用）。

还剩什么（主线已换）：**把 3DS 链接进请求路径**，让探针 1/12 往上走；JL 的 5 条同理需确认是否接线。
## R1151 —— 补 Process3DS → CompleteActionAsync 的边；产物证明断点在更上游

改了什么：
- **断点定位**：`PayPalGateway.CompleteActionAsync`（`Gateways.cs` L1026，解析链）**全仓零调用**；
  `SubmitPaymentAsync` L1248 已存 `threeDsPayload` 并返回成功 ⇒ 交接有、回路无。
- **落接线**：`StoreFlow.Process3DSAsync` 开头新增分支——会话 `paypal3ds.state == Waiting3DS` 时，
  `PaymentGatewayRegistry.Default.Resolve(gateway)` → `CompleteActionAsync(c, threeDsPayload, ct)`；
  成功 `Success` / 失败 `Fail(retryable)`。Adyen transStatus 分类逻辑未改。
- **注册确认**：`PaymentGateway.cs:75` `r.Register(new PayPalGateway())`。

验证：build **0 错**；支付/3DS/流程子集 **119/119**；全量 **2453/0/2**；
变异 **59/59 fired, tree GREEN, staleness 0**（05:28:07）；AOT 发布 exit=0。

**产物对照的关键否定**：新边接上后 `paypal 3ds: resolution failed` **仍被裁掉**
⇒ `Process3DS` 这一步不在任何已执行流程路径上（推断，未直接验证）。

还剩什么：① `StepAction.cs:114` 的 `Steps` 属于哪个 action、谁触发；
② 若无人执行，从 `sub_141113680` 四态机找回入口。
## R1152 —— 解析移入 ProcessPayment（StepAction 无 PayPal 动作）；产物探针对反射派发无效

改了什么：
- **R1151 挂错步骤**：`Steps={SubmitPayment,ThreeDS,Handle3DS,Process3DS}` 属 **`Adyen-Authorize3DS2`**；
  `StepAction` 里 **0 个 PayPal 注册项**。流程 ordinal 顺序为
  `SubmitPayment 44 → GetPayPalToken 45 → SubmitPayPal 46 → ProcessPayment 47`。
- **移块**：R1151 的解析块从 `Process3DSAsync` 移到 `ProcessPaymentAsync` 的 `requires_action` 分支；
  `Process3DSAsync` 恢复原样。
- **产物结论（重要）**：`payment requires action` **yes** 而 `login did not stick` **no** ——
  同类同形态一活一死 ⇒ **裁剪按方法逐个发生**，因由是 `StepActionRunner` 的**反射派发**（ILLink 看不见）。
  ⇒ **`present: no` 只对静态可达代码有效；反射派发区间测不到。**

验证：build **0 错**；支付/流程子集 **235/235**；全量 **2453/0/2**；变异 **59/59 fired**；AOT 发布 exit=0。

还剩什么：① 加 `[DynamicallyAccessedMembers]` / root descriptor 让产物尺子对步骤方法有效；
② 在那之前不要把 `present: no` 当未接线结论；③ 3DS 解析链的真实运行验证需靠单测（已 235/235）。
## R1153 —— 为 R1151/R1152 的 3DS 接线补 3 条行为测试（此前零覆盖）

改了什么（仅 tests）：
- 新增 `PaymentChallengeResolutionTests` 3 条：① 挑战挂起但无 gateway ⇒ `Fail` 含 `no gateway`，
  **不得**是 `payment requires action`；② 仅 `requires_action` ⇒ 仍走分类器（证明分支有条件）；
  ③ `authorised` ⇒ `Ok`。
- 替身 `BareFlow : StoreFlow` 只实现 `Id`/`Name`/`Domains`，不加行为。

验证：build exit=0（两次编译失败均由编译器指出：`StoreFlow` 抽象、漏 `Domains`）；
新用例 **3/3**；全量 **2456/0/2/2458**；变异 **成功 fired、tree GREEN**。

**教训**：R1151/R1152 两次改行为，全量一直绿——因为**没有用例走过那条分支**。绿 ≠ 对。

还剩什么：① `present: no` 对反射派发区间仍无效（R1152 结论），若要产物可证需 root descriptor；
② 3DS 真实 HTTP 路径（`ContinueAsync` 的 graphql 请求体）仍靠单测而非产物验证。
## R1154 —— GqlAsync 端到端钉子 6 条；graphql 动词核实为 PUT（sub_14110D670 第 37 行）

改了什么（tests + 取证，src 未改）：
- **动词取证**：`sub_14110D670` 第 37 行 → `sub_1408B6310`（+24 = **PUT**）。
- 新增 `PayPalGraphqlStageTests` 6 例：① 操作名走查询串 + 动词 PUT（`RawUrl` 断言）；
  ② 体为 `{"variables":…,"query":<DocumentFor(op)>}`；③ 分派 200/403/429/500 四态。
- 中途一条红（`Actual "/"`）成因：`TinyServer.Requests` 只记 `AbsolutePath`，而缝指向服务器根
  ⇒ 记录约束：**该缝必须带 `/graphql` 路径**。

验证：`_gql_verb.py` → `verb slots called: [(37,'6310')] -> PUT`；新用例 **6/6**；
全量 **2462/0/2/2464**；变异 **59/59 fired, tree GREEN**（2026-11-19T06:05:31+08:00）。

还剩什么：① `DocumentFor` 的四个文档与镜像冻结文本是否逐字一致（未比对）；
② `present: no` 对反射派发区间仍无效（需 root descriptor）。
## R1155 —— 四份 graphql 文档逐字对齐（各多一个尾部换行）；注释长度改为镜像值

改了什么（src）：
- **比对工具** `analysis/_gql_documents.py`：源码解析 `@\"...\"` 逐字串（地址从注释正则取，不手抄），
  镜像按 `[MT:8][len:4][UTF-16]` 解码，**逐字**比较。
- **结果**：四份各多一个尾部 `\n`（631/814/872/10371 vs 镜像 630/813/871/10370）；
  **注释里记的是复刻件自己的长度**，同样偏一。
- **落修**：终止行上移一行；注释长度改为 630/813/871/10370。修后四份 **IDENTICAL**。

验证：修前四份 `DIFFER ... first diff at 末位`；修后 `IDENTICAL`×4；build 0 错；
PayPal **42/42**；全量 **2462/0/2/2464**；变异 **59/59 fired, tree GREEN**（2026-11-19T06:16:29+08:00）。

**教训**：注释里的数字若来自被注释者本身，是**自证**；要拿两侧都取出来比。
## R1156 —— 支付层字面量全量比对：21 条可比，20 相同，0 不符（src 未改）

改了什么：新增 `analysis/_literal_audit.py`（解析常量 + 按行/紧邻 /// 块取地址 + 逐字比较 + 同址去重拒判）。

结果：**21 可比 / 20 IDENTICAL / 0 DIFFER / 1 UNREADABLE**。

**两次归因错误（都是脚本的）**：
① 「前 4 行最近地址」把上一行常量的地址算给下一行 → **6 条假 DIFFER**（不复核就会落错账）；
② 收紧后剩 1 条 `UNREADABLE`，实为注释里对象地址在前、站点地址在后，脚本取了后者。

**教训**：同一个毛病第三次出现——**都是「我替工具决定它该看哪儿」**（前两次是探针形状，这次是地址来源）。

还剩什么：① 该比法可推广到 `Gateways.cs` / `StoreFlow.cs` 的字面量；
② `Present: no` 对反射派发区间仍无效（需 root descriptor）。
## R1157 —— 整棵 Stores 树字面量比对：33 相同 / 2 拆分 / 0 不符（src 未改）

改了什么：`analysis/_literal_audit_tree.py`（扫 `replica/src/**/*.cs`，逐字比 + SUFFIX/UNREADABLE 分类）。

结果（355 文件）：**IDENTICAL 33 / SUFFIX 2 / DIFFER 0 / UNREADABLE 1**。
两条 SUFFIX = Stripe 3DS2（`ApiHost`(private) + path，拼合等于镜像 0x147054e20/0x147054e90）。

**本轮三次同类错误（皆为我定的工具规则）**：① 前缀检查只认 public（`ApiHost` 是 private）→ 误报 2 条；
② 元组 6→8 未同步解包；③ 内联 python 被 PowerShell 吃引号（改用 edit）。

还剩什么：① 该比法可用于 `Cybersole.Http` / `Cybersole.Ui`；
② `present: no` 对反射派发区间仍无效（需 root descriptor）。
## R1158 —— 两条 PayPal 路径分离取证：REST=Demandware 店铺流程；graphql=独立大机器（src 未改）

改了什么：新增 `analysis/_paypal_surfaces.py`（xref → 函数 → 函数内字符串自证）。

结果：
- **REST `v2/checkout/orders`** → 1 xref → `0x140a50cd0`，字符串含 **`/Paypal-GetPurchaseUnit`**、
  **`on/demandware.store/Sites-`** ⇒ Demandware 店铺控制器 ⇒ `PayPalGateway`(REST) 定位正确。
- **graphql** → xref 0，**字节扫描 1 site** → `0x14228D780`（19,552 B）⇒ 另一台独立机器（hosted 路径）。
- **`init-challenge`** → xref 0、字节扫描 **0** ⇒ 很可能经 `.rdata` 指针表引用。

**关键决定**：**不**把 `RunAsync` 塞进 `AuthorizeAsync`——那会把 hosted 接进店铺网关，且没有任何测试会红。

**工具边界**：`xrefs_to` / `disp32_scan_any` 只覆盖直接引用；`.rdata` 指针表两者皆失效。

还剩什么：① 找 `.rdata` 里 threeds 家族的指针表（可一次给出 hosted 步骤顺序）；
② `RunAsync` 的落点需先确认复刻件 hosted 流程入口。
## R1159 —— 指针表探索四次撞墙后收手；IDA 已恢复（src 未改）

- 工具 `analysis/_pointer_tables.py`（8 字节指针搜索 + 邻接聚类）。
- **四次失败**：① `bin_search` 6 参重载拒收（R1143 同处三撞）；② 分块读途中 HTTP 断连；
  ③④ 插件 `sync.py profilefunc` 抛 `TypeError`（deadline 逻辑自损）。
- **收手理由**：换的是实现不是目标；指针表本就只是探索项。
- IDA 恢复：launch → Restore packed base → 55s，`status: ok`、`hexrays_ready: true`。

还剩什么：① 若要查表，先用 `pe_sections.py` 挑出非常规段再单目标窄扫；
② 更值钱：对 `CORE_COVERAGE` 其余流程逐步 `where_is`，找真正缺的接线。
## R1160 —— 12 条占位分类更正；镜像无 "bstn"，beast 属 Arrow & Beast(Shopify)（src 未改）

改了什么（分析 + 更正记录）：
- `analysis/_placeholder_names.py`：用 `flow_work_audit` 同一判据**列出 12 条占位名字**。
  分三类：**故意不兜底 1**（Shopify `GetCsrf`）/ **服务端下发路由 7**（Farfetch，R1077 定案）/
  **endpoint unknown 4**（Bstn）。
- **更正**：此前「占位全卡凭据」的记录不成立，仅 Farfetch 一类可归入；Bstn 是**证据缺口**。
- **Bstn 取证**：`str "bstn"/"BSTN"` → **0/0**；`str "beast"` → `ARROW & BEAST`、
  `arrowandbeast.com`、`arrowbeast.myshopify.com`（**Shopify**）。
- **不推论**：不能说原版不支持 BSTN（字符串表是下界）；`/api/beast` 的 `live` 出处需追。

还剩什么：① 追 `/api/beast` 的 `live` 原始实测出处；② 先确认该店在原版里的真名，再谈端点。
## R1161 —— 撤回 R1160：beast ≠ ARROW & BEAST（仅共享词）；live 类=实机实测而非镜像证据

追溯结果：
- `LiveContractTests.BstnServesItsBeastApiAndNotAShopifyOne`（`LiveContractTests.cs:287`）实测
  `bstn.com/api/beast/geoIP` **通**、`/cart.js` **必须不是** Shopify 购物车。
- `BLOCKERS.md:15391` 早有口径：「`/api/beast` 从 R91 起归这一档，『镜像里没有』≠『不该有』」。
- `ASYNC_OPS.md:12980` 早写过 `/api/beast n=0`。

**撤回**：①「beast 属 ARROW & BEAST(Shopify) ⇒ 店识别错」②「名字错了，端点必然找错」。
**保留**：镜像无 `bstn`/`beast`（本轮复测 0/0）——该店证据是 **live 实测**，非二进制字符串。

**错类**：共享词 ≠ 同一实体（R760 同类）；`live` 类 = 实机实测，≠ 镜像里有。

还剩什么：Bstn 其余三条端点（cart/checkout/order）仍未取得；Farfetch 7 条为服务端下发路由（已定案）。
## R1162 —— Demandware PayPal 三控制器路径落库；只实现动词有证据的一条；变异 RED(1 抖动)

改了什么（src + tests）：
- `DemandwareFlow` 新增：`PaypalGetPurchaseUnit`/`PaypalGetPaypalOrderId`(`?csrf_token=`)/
  `PaypalGetOrderDetails`(`?orderId=`) 常量 + `PaypalPurchaseUnitAsync`（**GET**，有观测）。
- 另两条**不发请求**（动词 Unknown，注释写明）。
- 新测试 `DemandwarePaypalControllerTests` 3 条。

验证：`_demandware_paypal.py` → `GetPurchaseUnit at [172]`、`179 GET`、另两条 `[]`；
build 0 错；Demandware **38/38**；全量 **2465/0/2/2467**；
变异 **59/59 fired 但 restored tree RED**：`GroupSummaryTests.CloningCopiesTheGroupAndItsTasks` 失败，
`src` 无未预期改动、该类单独 **4/4 绿** ⇒ **顺序抖动**（该类第二次），单列不计。

还剩什么：① 另两条的动词（需先定所属函数）；② `GroupSummaryTests` 顺序依赖应单独立案。
## R1163 —— PayPal 三条控制器全部有动词（GET）；补 3 条真发请求的测试；变异 GREEN

改了什么：
- **取证**：`GetPaypalOrderId`（fn 0x140a31e40，append@129，唯一动词槽@146）与 `GetOrderDetails`
  （fn 0x140a51e20，append@121，唯一动词槽@139）**均为 GET**。
- **src**：`DemandwareFlow.PaypalOrderIdAsync(c, csrfToken, ct)` 与 `PaypalOrderDetailsAsync(c, orderId, ct)`；
  标识符作参数传入；**builder 身份未追踪**这一点写入 doc 注释。
- **tests**：`DemandwarePaypalRequestTests` 3 条（断言整行 RawUrl 与 GET 动词）。

验证：build 0 错；`DemandwarePaypal` **6/6**；全量 **2468/0/2/2470**；
变异 **59/59 fired, decorative 0, tree GREEN**（07:10:36）。

**RED 排除**：干净重跑 `restored tree: GREEN` ⇒ R1162 那次是**不可复现的一次性抖动**。

还剩什么：① 若要观测「builder 身份」，需读 146/139 行实参来源；② `GroupSummaryTests` 抖动应单独立案。
## R1164 —— 关闭 R1163 的 Unknown：GET 确实携带该 builder（链路含行号）；无行为改动

改了什么（仅 src 注释）：两段 doc 注释由「未追踪」升级为观测链路——
`118 路径 → 124/129 查询前缀 → 138 值 → 141 sub_141DC7870(&v23) 实体化 → 143 进 options → 146 GET`；
order details 同形（`121/131/134/139`）。**追加顺序 = 路径→前缀→值，与实现一致。**

验证：`_builder_identity.py` 窗口原文；build 0 错；全量 **2468/0/2/2470**；
变异 **59/59 fired, tree GREEN**（07:20:51）。

**自省**：这个 Unknown 是我上一轮写进**代码**的，隔一轮就关掉了——**挡在路上的边界才会被处理**。

还剩什么：① 三条控制器方法仍未接到任何步骤调用（接线问题，需序列证据）；
② `GroupSummaryTests` 抖动两次未复现，应单独立案。
## R1165 —— 抖动机制查明：单进程共享 settings.json + 并行测试类；已串行已抖过的类

改了什么（仅 tests）：
- 新增 `SharedSettingsCollection`（`[CollectionDefinition("shared-settings", DisableParallelization = true)]`）。
- `GroupSummaryTests` 加 `[Collection("shared-settings")]`。

机制（实证）：`TestServices.Create` → `AppServices.Create`（`config.Load()` @60、`AppPaths.DataRoot` @86）
→ `AppPaths.DataRoot` 是 static 仅初始化一次（`CYBERSOLE_DATA_ROOT` 可覆盖）⇒ 全进程共用一份 `settings.json`；
xunit 默认并行类 ⇒ 12 个碰 `Config` 的类互相踩。**解释了「只在全套里出现、单独跑消失」。**

验证：build 0 错；`GroupSummary` **4/4**；全量 **2468/0/2/2470**；
变异 **59/59 fired，restored tree GREEN**（07:32:32）。

还剩什么：① 另 11 个候选类逐个确认是否写盘，再决定是否入 collection；
② 三条 Demandware PayPal 控制器方法仍未接到步骤调用。
## R1166 —— 更正 R1165 取证路径：写盘在 CloneCore/DeleteCore（TasksViews.cs 790/799），不在测试里

改了什么（**只更正记录，src/tests 未改**）：
- **证据修正**：`TasksViews.cs:789-790`（CloneCore 保存）与 `797-799`（DeleteCore 保存）证明
  `GroupSummaryTests` 会经**被测代码**写 `settings.json` ⇒ R1165 的机制成立。
- **作废结论**：11 个候选类里 9 个「测试文件 0 处持久化」**不能**说明它们不写盘——它们调用的生产方法可能写。
  **候选名单仍然全开。**
- **正确工具（下一轮）**：先列生产代码所有 `Config.Save()` 调用点，再反查走到它们的测试类。

**错类（第三次）**：在「离结论最近的文件」找证据，而不是「能决定结论的文件」。

验证：无需构建/测试（无代码改动）；引用行号可现场核对。

还剩什么：① 用上述正确工具扫 `Config.Save()` 调用点 → 决定哪些测试类入 `shared-settings`；
② 三条 Demandware PayPal 控制器仍未接到步骤调用。
## R1167 —— 135 处 Config.Save ⇒ 关闭集合并行（xunit.runner.json）；套件 2m30s→5m09s，全绿

改了什么（配置，非代码）：
- 新增 `tests/Cybersole.Tests/xunit.runner.json`：`parallelizeTestCollections: false`；
- `Cybersole.Tests.csproj` 增加该文件的 `CopyToOutputDirectory`，理由与 135 写盘点写在 csproj 注释里。

验证：build 0 错；`runner config copied: yes`；全量 **2468/0/2**、**wall 5m09s**（前 ~2m30s）；
变异 **59/59 fired，restored tree GREEN**（07:50:31）。

取舍：慢一倍，换「同进程不再并发读写同一 settings.json」——**竞争从结构上消失，而非某一个类不抖**。
`shared-settings` collection 保留作为已知共享类清单（现为冗余）。

还剩什么：① 若嫌慢，正解是给 `ConfigurationStore` 一个每测试独立的 root（需 src 改动，未做）；
② 三条 Demandware PayPal 控制器仍未接到步骤调用。
## R1168 —— ConfigurationStore 带 root（默认不变）；TestServices 每测试独立 root；并行无收益

改了什么（src + tests）：
- `AppPaths`：`EnsureCreated(string)` / `BackupsDirFor(string)`。
- `ConfigurationStore(string? root = null)`：8 个 store 从 root 派生；`Load/Save/Backup` 用 `_root`；
  `BackupsDir` → 实例 `_backupsDir`；新增 `Root`。
- `AppServices.Create(..., string? dataRoot = null)`；`checkoutHistory.json` 跟随 `config.Root`。
- `TestServices.Create`：每测试 `%TEMP%/cybersole-tests/<guid>`。

**实测（推翻上轮归因）**：串行+共享 5m09s / 串行+独立 **5m18s** / 并行+独立 **5m43s**
⇒ 并行无收益，瓶颈是每测试小文件 I/O。**保持串行。**

验证：build 0 错；全量 **2468/0/2**；变异 **59/59 fired，restored tree GREEN**（08:15:16）。

**自伤**：批量子串替换把 `AppPaths.BackupsDirFor` 改坏（CS0103），修回一行。

还剩什么：① 若嫌 5m 慢，正解是**减少每测试的文件数**（如仅为改动项建 root 子集），需 profile 先；
② 三条 Demandware PayPal 控制器仍未接到步骤调用。
## R1169 —— 三个 PayPal 控制器名迁入 DemandwareControllers（本仓约定）；查询前缀留在 flow

改了什么：
- `DemandwareControllers`：新增 `PaypalGetPurchaseUnit`/`PaypalGetPaypalOrderId`/`PaypalGetOrderDetails`
  与 `All` 条目；`DemandwareFlow` 三个方法改指 `DemandwareControllers.*`；flow 只留两个查询前缀。
- 两个测试跟随迁移（前缀仍断言 `DemandwareFlow`）。

验证：build 0 错；`Demandware` **41/41**；变异 **59/59 fired, tree GREEN**（08:34:23）。

**全量 1 红单列**：`ShapeAuditGuardTests` 报 `shape_audit.py exited 1`；直跑 **exit 0**、该类单跑 **2/2**、
无超时设置 ⇒ **子进程一次性失败**（疑内存压力）。**没跑成≠通过≠失败。**

**错类**：两轮内第二次子串误伤（`…OrderIdQuery` 被一起替换，CS0117）。

还剩什么：① 三条 PayPal 控制器方法仍未被任何步骤调用（需序列/动作证据）；
② 若要坐实 OOM 猜测，需在跑套件时采样可用内存。
## R1170 —— PayPal 三条控制器的四级调用链走通；PurchaseUnit 与 OrderDetails 属同一 438 行步骤

改了什么（**仅 doc 注释**，无行为改动）：`DemandwareFlow.PaypalPurchaseUnitAsync` 注释写入
四级调用链、两条共用 `0x140a530f0`、`GetPaypalOrderId` 在 `0x140a32f30`。

链：机器 `0x140a50cd0`/`0x140a31e40`/`0x140a51e20` → MoveNext → async 入口
`0x140a45380`/`0x140a27e50`/`0x140a453d0` → 唯一调用者 `0x140a530f0`/`0x140a32f30`/`0x140a530f0`。

验证：build 0 错；全量 **2468/0/2**（5m56s）；变异 **59/59 fired，tree GREEN**（08:52:58）。

**自纠**：① 「有调用者」≠「找到人写的调用者」（前者全是编译器生成）；② 把 async 入口当成 stub。
**不接线**：两个例程的 flow 与 ordinal 未知，下一步从产品字面量反查 store。

还剩什么：① 从 `'8058260839474'`/`'/moon-shoe-jacquemus-%2B-nike/'` 等反查 store → flow → ordinal；
② 两个大型例程的步骤语义（438/574 行）尚未读全。
## R1171 —— JL 步骤表在第二地址复现；36/37 三处无实现；16/19/14 三数字并列；不接线（宿主不符）

Observation：
- `0x143372d80` 的状态机名串 = `FLOW_SEQUENCES.md` §3 的 JL 22..37 表（**第二地址交叉验证**）。
- **16**（镜像连续步骤）/ **19**（StepMap 注释总数）/ **14**（实测 `Pairs` key 数）三者并列已写入 BLOCKERS。
- `GetCartCsrf` 在 `src` **无实现**；`JohnLewisStepMap.Pairs` 无 36/37；`GetPayPalOrderId` 仅在注释。

**不接线**：`/Paypal-GetPaypalOrderId` 是 SFCC 形态，JL 走 BFF ⇒ 归因 Unknown，不以名字相似推断。

本轮无代码改动（docs 三处）；变异收据沿用 R1170（src 未变）。

还剩什么：① 定 JL 第 37 步的真实实现（从 `0x140a32f30` 的 574 行里读它请求的宿主）；
② `GetCartCsrf` 的端点（镜像里未找到，可能同为 BFF）。
## R1172 —— Jacquemus / Maison Margiela 两家整店缺失（镜像有、src 零命中）；加店成本已摊开

Observation：
- `0x140a32f30` 字面量 = Jacquemus 家族；`0x140a530f0` = Margiela 家族（含 `Margiela-Preload`）。
- `str "Jacquemus"` → `https://www.jacquemus.com/`（0x14709486c）、`Jacquemus US`、`JacquemusUS`。
- `str "Margiela"` → `Maison Margiela UAE`、`MargielaEU/EU2/APAC/AU/CA`、`MARGIELA-DEBUG`/`-ERROR`。
- `grep acquemus|argiela` 于 `replica/src/Cybersole.Stores/**` → **0**。

**错类（第三次）**：跨店重名当同一实现（R1160 `beast`、R1171 JL 第 37 步）。

加店成本（下轮据此执行）：`Registry.cs:159` 显式数组、`CoreTests:133` 硬编码 65、
`EveryModuleHasAtLeastOneDomain`、`DuplicateModuleAuditTests`(Pairs==5)、`FirstDomainResolvesTests`(真解析)。

**本轮不加店**：Jacquemus 缺 PDP 标记观测；**Margiela 缺主机字面量（域名 Unknown，不编）**。

还剩什么：① 观测 Jacquemus PDP 标记 → 加 `JacquemusModule` 与 flow；② 找 Margiela 主机；③ 两家其余步骤表。
## R1173 —— 落库 Jacquemus-Preload/Margiela-Preload 两控制器；证否「字符串池可枚举店铺」

Observation：
- 扫 `0x146d00000..0x146e00000` 7956 条，**最长有序段仅 100 条** ⇒ 堆是全局字母序，**不能枚举店铺**。
- `Jacquemus-Preload` 0x146dd3ba8、`Margiela-Preload` 0x146dfcbe0。
- Margiela **12 个区域码**（APAC/AU/CA/EU/EU2/GB/HK/JP/KR/MENA/SG/US）+ `MARGIELA-DEBUG/ERROR`；
  Jacquemus 侧 `https://www.jacquemus.com/`/`Jacquemus US`/`JacquemusUS`。

改动：`DemandwareControllers` +2 常量并进 `All`；新测试 `BrandPreloadControllerTests` 2 条。

验证：build 0 错；子集 **43/43**；全量 **2470/0/2/2472**（5m38s）；变异 **59/59 fired, tree GREEN**（09:15:02）。

**未做**：两家 `MonitorAsync`（缺 PDP 标记观测）、店铺模块（需先定「区域」模型）。

还剩什么：① 决定区域模型 → 再建 `JacquemusModule`；② Margiela 主机字面量；③ 两家 step 表。
## R1174 —— 名字级 real gap 2→0（那 2 条是 R702 裁决）；守卫三桶加强；新增两向棘轮

改了什么：
- `tools/bind_diff.py`：新增 `out of scope (R702)` 桶（恰好两条，注释含 R702 出处）；`real gap` 归零。
- 新 `NameBindingGapTests`（2 条）：`real gap` 必须 0、`out of scope` 必须恰好 2。
- `BindDiffGuardTests`：不变式由两桶**加强**为三桶 `noise+outOfScope+real == missing`。

验证：`real gap: 0`；build 0 错；子集 **5/5**；全量 **2472/0/2/2474**（4m30s）；
变异 **59/59 fired, tree GREEN**（09:43:05）。

**两次事故**：① 加桶未更新守卫 → 全量红（Expected 12/Actual 14），修法是加强不是放宽；
② 清文件锁时误杀后台变异任务 → 该次变异作废，已重跑。

**下一轮优先**：`.publish-aot` 陈旧（22 个源文件更新）⇒ `present:` 探针不可信。
## R1175 —— AOT 产物重建至 current（54.25 MB / 0 stale）；文档两条发布命令一对一错，已修正为带项目路径

Observation：
- `artifact_freshness`：**0 stale、state: current**；`.publish-aot\Cybersole.Ui.exe` 54.25 MB，mtime 09:46:06。
- 探针（新产物）：`www.paypal.com/v2/checkout/orders` **present=yes**，其余 15 条 **no**（与 R1150 一致）。
- `BINDING_BACKLOG.md:5782` 命令**缺项目路径** ⇒ 解决方案级发布产出 **459 KB** 框架依赖 exe；
  同文档 **9588 行**早已有正确版本。已把 5782 修正为带 `src/Cybersole.Ui`。

**坑**：曾把 459 KB 的产物换进 `.publish-aot` 并读探针 → 16 条全 no，**尺寸（100 倍差）救回**。
换位已加 `> 40MB` 守卫。

还剩什么：① 缓存复用（4 秒完成）依赖 `obj` 未清理，未验证清理后的耗时；
② `present:` 探针现在可信，可重跑此前所有「镜像里没有」的结论复核。
## R1176 —— present: no 无信息量（反射派发整段裁剪）；警示写进工具并加守卫

Observation：
- 11 条探针（current 产物）：`www.paypal.com/v2/checkout/orders` **yes**，其余 **no**——
  其中 `Cart-AddProduct`/`Checkout-Begin` 分别在 `DemandwareFlow.cs:279`(POST) 与 `:425`(GET) **运行时真用**。
- ⇒ `no` 对「死代码」与「活着但走反射」同读数，**无信息量**；作废 R1150/R1152 的 `no ⇒ 不可达` 论证。

改动：
- `tools/artifact_probe.py`：有 `no` 时输出两行警示（含两处实测对照写在注释里）。
- 新 `ArtifactProbeCaveatTests`（1 条）：断言警示文本存在（实测 158 ms 真执行）。

验证：build 0 错；守卫 **1/1**；全量 **2473/0/2/2475**（4m32s）；变异 **59/59 fired, tree GREEN**（10:05:25）。

还剩什么：① 若要真正判可达性，得看 AOT 中间产物或 `[DynamicallyAccessedMembers]` 是否已声明；
② 所有用 `no` 立过的结论要标「靠形状而非探针」。
## R1177 —— ILLink 描述符保住 Flows（6/8 探针 no→yes，产物 +0.47 MB）；两条仍未保留

改动：
- 新 `src/Cybersole.Ui/ILLink.Descriptors.xml`（`Cybersole.Stores.Flows.*` preserve=all，含实测对照注释）
  + csproj `<TrimmerRootDescriptor Include="ILLink.Descriptors.xml" />`。
- `ArtifactProbeCaveatTests` 负样本改为 `definitely-not-in-any-build-1177`（原用 `Cart-AddProduct`，
  描述符让它存在后警示不再打印）。

Observation：
- **抓到自证注释**：`StepAction.cs:208` 声称有 `DynamicallyAccessedMembers`，`:210` 却是裸 `typeof()`。
- 产物 **54.25 → 54.72 MB**；探针 `Cart-AddProduct`/`Checkout-Begin`/`Paypal-GetPaypalOrderId`/
  `Paypal-GetOrderDetails`/`Jacquemus-Preload`/`Margiela-Preload` **no→yes**；
  `Paypal-GetPurchaseUnit` 与 `Product-Show` **仍 no**。

验证：build 0 错；守卫 1/1；全量 **2473/0/2/2475**（5m07s）；变异 **59/59 fired, tree GREEN**（10:29:02）。

还剩什么：① `Product-Show`（裸字面量）与 `Paypal-GetPurchaseUnit` 仍被裁——**第二个机制未明**；
② 查明后重跑全套探针，才能说「步骤体全部保住」。
## R1178 —— 描述符有效（可复现 A/B：54.72MB/yes vs 54.25MB/no）；我上轮的否定 A/B 无效

Observation：
- 描述符在 + csproj 引用 → **54.72 MB**，6 条控制器字面量 **yes**；
- csproj item 移除 → **54.25 MB**，同一批 **全 no**。
- 上一轮「只移文件、留 item」的对照产出 54.72 MB 且 yes ⇒ **假对照**（复用旧原生镜像，mtime 未变）。
- `link.rsp` 37 行不含描述符项（传递渠道不同），但两态对照可复现。

产物：**54.72 MB**、0 stale / current。全量 **2473/0/2/2475**（5m28s）；变异 **59/59 fired, tree GREEN**（10:48:26）。

**开放**：`Paypal-GetPurchaseUnit` 与 `Product-Show` 仍 absent（同类六条都在），基线已干净，待查。

还剩什么：① 那两条为何仍被裁；② `link.rsp` 不含描述符项但对照成立——传递渠道待确认（不影响结论）。
## R1180 —— 探针 BOM 假阴性（首行）；撤 R1176/R1177/R1178 三条结论；加 utf-8-sig + 守卫

Observation：
- 字节直查：`Product-Show`/`Cart-Get`/`Paypal-GetPurchaseUnit` **全在产物里**（偏移 30797776..30799082）。
- 探针文件头 `b'\xef\xbb\xbf'`，首行 `'\ufeffProduct-Show'` ⇒ **BOM 只污染首行** ⇒ 每表首行假 no。
- 修 `utf-8-sig` 后同一文件 **10/10 yes**。

改动：`tools/artifact_probe.py`（utf-8-sig + 注释）；新 `ProbeBomTests`（故意写 BOM 文件，断言首行 yes）；
`StepAction.cs` `Build()` → 泛型 `Build<T>()` + `DynamicallyAccessedMembers(PublicMethods)`（替换自证注释）。

验证：build 0 错；`ProbeBom|Caveat` **2/2**；全量 **2474/0/2/2476**（5m57s）；
变异 **59/59 fired, tree GREEN**（11:06:28）。

**Unknown**：描述符 vs 泛型标注各自作用未分离；产物 stale 17 文件（`StepAction.cs` 后改动）。

还剩什么：① 重发产物；② 分离测「描述符是否仍必需」；③ 恢复 R1176 里被 BOM 带偏的结论表述。
## R1181 —— 描述符必需（54.72MB/9-of-9）vs 标注单独（54.25MB/0-of-9）；修 relpath 跨盘崩溃

Observation：
- 两态对照（无 BOM 探针）：标注+描述符 **54.72MB / 9-9 yes**；仅标注 **54.25MB / 0-9 yes**；负对照 no。
- 变异 RED 真因：`os.path.relpath(path, ROOT)` 跨盘 `ValueError`（C: temp vs D: repo）⇒ 工具退出 1。

改动：
- `tools/artifact_probe.py`：`relpath` 加 try/except，跨盘回退绝对路径。
- 两个探针守卫改传**小合成文件**当 `--exe`（检验读取逻辑，不读 54 MB 产物）。
- csproj / 描述符注释写入两态数字，说明「标注合法化、描述符保命」。

验证：守卫 **4/4**；全量 **2474/0/2/2476**（4m29s）；变异 **59/59 fired，restored tree GREEN**（11:38:50）。

还剩什么：① 描述符保留粒度（现为 `Flows.*` 全保留）能否收窄；② 产物陈旧度仍显示 17 文件（tests 计入）。
## R1183 —— 陈旧度改为「内容判据」：mutation 触摸不再误报；字段进 METRICS

Observation：
- 产物 mtime 11:09 / 最新 src mtime 11:34，但 `git status src` **0 dirty** ⇒ 11:34 是 mutation 还原触摸。
- 改后：`of those, changed against HEAD: 0`、`state: current`，并打印「17 newer but unchanged」。

改动：`artifact_freshness.py`（新增 changed-against-HEAD，state 改按内容；git 判不了时仍保守报 stale）、
`metrics_report.py`（字段登记进正则表与字段列表）、新 `FreshnessHonestyTests`（changed==0 ⇒ current）。

验证：build 0 错；守卫 1/1（128 ms 真执行）；全量 **2475/0/2/2477**（4m32s）；
变异 **59/59 fired, tree GREEN**（11:56:47）。函数比 **64.76%**。

还剩什么：① 若将来有工具改字节却不改 git 状态，此判据会漏（未发生，记着）；
② 描述符保留粒度（`Flows.*` 全保留）仍可收窄。
## R1184 —— 15 个缺失类型全部定性（改名 13 / R702 2 / 未实现 0 / 未分类 0）+ 棘轮

改动：
- 新 `tools/type_classification.json`（15 条，含 kind/to/evidence）。
- `bind_diff.py --type-presence` 逐行 + 汇总 `classified: renamed N, out of scope N, unimplemented N, unclassified N`。
- `metrics_report.py` 把整行带进 METRICS.md。
- 新 `TypeClassificationTests`：`unclassified 0` 且 `unimplemented 0`（后者为棘轮）。

验证：build 0 错；守卫 1/1（6 s 真执行）；全量 **2476/0/2/2478**（4m36s）；
变异 **59/59 fired, tree GREEN**（12:21:52）。

**不精确处**：`Concurrency`/`ActionConfig`/`TaskCreatorCartView` 三条映射记的是成员所在文件而非精确类型名。

还剩什么：① 补齐那三条精确映射；② 描述符保留粒度可收窄；③ 其余判据（b–f）逐条复算。
## R1185 —— 判据 a–f 整表复算：5 达标 / 1 自带 fail / 2 处文档数字过期

| 判据 | 状态 |
|---|---|
| a) 类型级 0 / 类型缺失（13 renamed + 2 out_of_scope + 0 unimpl + 0 unclassified）/ 名字级 real gap 0 | 达标 |
| b) 文案缺口 0 | 达标 |
| c) `PARITY_PRODUCT.md` 存在但数字过期（175,104 / 69.3% vs 现 179,456 / 64.76%） | **未达标** |
| d) `PARITY_CLAIMS.md` 有 id/claim/status/authority/command/gap_reason；C7b 标 fail | 达标 |
| e) 全量 2476/0/2、变异 59/59 GREEN；但文档数字未全部来自 METRICS | **部分** |
| f) core flows 18 / steps 369 / placeholders 11（均外部受阻并写明） | 达标 |

**下一步（非外部受阻）**：
1. **C7b：94 total / core 17 形状差异**。`--baseline` 已见两类：成员不存在（`BotTask.Running`/`Notification.Title`/`Checkout.Profile`）、只读该可写（`BotTask.Products`/`TaskGroup.Running`/`ClockService.Current`）。**先穷举 17 条，再逐条补。**
2. 修 `PARITY_PRODUCT.md` / `PARITY_CLAIMS.md` 里的手抄数字（或标为时点快照）。

**口径澄清**：`shape_audit.py` 默认 78/1 与 `--baseline` 94/17 是**两种口径**，METRICS 用后者。

本轮无代码改动（仅审计与文档）；变异收据沿用 R1184（12:21:52，src 未变）。
## R1186 —— 修 shape_audit 解析缺陷（注释造出伪类型）；撤回「Checkout.Profile 假阴性」

Observation：
- `Checkout.cs` 含注释 `record of the checkout` ⇒ 扫描器造出类型 `of`（body 1002 字符、含 Checkout 成员），
  `Checkout` 只得 590 字符残片 ⇒ 其成员被判 `?`。
- 修（`strip_non_code` 先抹注释/字符串）后：`total mismatches` **94 → 102**，`core` **17 不变**。
- **撤回**：`Checkout.Profile` 的 `?` **不是**假阴性——可写的 `Profile` 在 `CreateModel` 类体里；
  `Checkout` 类体内无该成员 ⇒ **真缺陷**（成员挂错类型）。我原先按整文件 grep，第四次犯同类错。

验证：`metrics` 102/17；全量 **2476/0/2/2478**（5m45s）；src 未变，变异沿用 R1184（59/59 GREEN）。

还剩什么：① 其余 10 条 core 行逐条核实（有意省略 vs 真缺陷）；② `CreateModel.Inputs` 一类「有意省略」
需按绑定口径重新裁定；③ `PARITY_PRODUCT.md`/`PARITY_CLAIMS.md` 手抄数字仍过期（判据 e）。
## R1187 —— 12 条 core 形状行逐条裁定（11 真差异 + 1 有意省略）；新增 `record-positional` 理由

Observation：
- 逐条类体取证（含 `record Notification(Kind, Title, Body, DateTime Timestamp)` 签名、`BotTask` 全成员清单）。
- `Notification.Title`/`Timestamp` 原报 `?`，实为**位置记录参数**（有但不可写）⇒ 理由错，已修为 `record-positional`。
- `CreateModel.Inputs` 源码注释明写 `left out on purpose` ⇒ 有意省略。
- `BotTask` 类体内无 `Running`/`Task`（复刻件叫 `IsRunning`）；`Checkout` 类体内无 `Profile`。

验证：`metrics` **102/17**；全量 **2476/0/2/2478**（5m38s）。本轮改工具（`shape_audit.py`），src 未变。

还剩什么：① 8 条 `prop-get` 转可写；② `Notification` 改可写；③ 3 条成员缺失/挂错类型；
④ `CreateModel.Inputs` 补或写明理由；⑤ 判据 e 的两处文档数字。
## R1188 —— Notification 改可写（形状 102/17 → 98/13）；守卫常数 6→5；变异收据矛盾待修

Observation：
- `Notification` 由位置记录改为可写记录（`Kind`/`Title`/`Body`/`Timestamp` 带 set；`Message`/`Type` 写穿）。
- 形状度量 **102/17 → 98/13**。
- `BindScopeGuardTests` 红（159 vs 160）；干净 HEAD worktree 实测 **153/159** ⇒ `KnownUnseenTypes` 6 → **5**（Notification 转入可解析桶）。
- 变异日志：`restored tree: RED` 但同处写着 `失败: 0，通过 2391/2393` ⇒ **收据矛盾**。

验证：build 0 错；守卫 2/2；全量 **2476/0/2/2478**（6m06s）。

还剩什么：① 变异收据为何判 RED / 恢复集为何 2393；② 其余 8 条 `prop-get` 转可写；
③ 3 条成员缺失/挂错类型；④ `CreateModel.Inputs` 补或写明理由；⑤ 判据 e 的两处文档数字。
## R1189 —— IDA 就绪（清模态框）；Notification 四对 Getter/Setter 由二进制直接观测确认

Observation：
- `ida.py health` → `status ok`, `hexrays_ready true`, `auto_analysis_ready true`，库 `target\Cybersole.exe.i64`。
- `ida.py str "Cybersole.Models.Notification"` 命中 `0x143210299`/`0x143210dd8`：
  Title/Timestamp/Message/Type 各一对 `!Getter` + `!Setter`；**未见** Kind/Body 绑定。
- 首次搜 `"Notification,.Title!Getter"` → `n:0`：**形状错**（真实为 `,Cybersole.Core.Title!Getter`），非缺席。

环境：`PROXY: MISSING`（需人工切换 DSH 的 ida 条目）；IDA 模态框已用 CUA 清除。

还剩什么：① 用 xrefs_to → site_to_func → Hex-Rays 还原这些 setter **实际写入什么**；
② 3 条成员缺失/挂错类型（`BotTask.Running`/`Task`、`Checkout.Profile`）回二进制取证；
③ 变异收据为何判 RED / 恢复集为何 2393；④ 其余 8 条 `prop-get`；⑤ 判据 e 的两处文档数字。
## R1190 —— BotTask 绑定面取证：Products 改可写（形状 98/13→97/12）；Task/Running 判 Unknown

Observation：
- `ida.py str "Cybersole.Models.BotTask"` 命中 `0x14321f5d0/0x1432231eb/0x14322358f`：14 个成员，
  其中 `Products`/`Running`/`Task` 均带 `!Getter`+`!Setter`（`Running` 另有 `!Property`）。
- `ida.py str "Cybersole.Models.Task"` 只命中 `TaskGroup` ⇒ 无 `Task` 模型类型。
- 改动：`BotTask.Products` 加 setter（`_productsOverride ?? AllProducts`），未赋值时行为不变。

验证：build 0 错；全量 **2476/0/2/2478**（6m20s）；形状 **97/12**。

**Unknown（写明缺什么）**：
- `BotTask.Task`：成员类型未知（原版无 Task 模型类型；需要 BotTask 元数据里的字段类型）。
- `BotTask.Running`：类型未知（int 计数 / bool 标志都满足描述符；需要写入点伪代码）。

还剩什么：① 用 `xrefs_to`+`site_to_func`+Hex-Rays 找 `Running` 的写入点定其类型；
② `Checkout.Profile` 归位；③ 变异收据 RED/0 失败矛盾；④ 其余 7 条 `prop-get`；⑤ 判据 e 两处文档数字。
## R1191 —— 「收据矛盾」实为运行被打断（2393 vs 2478）；判定新增 abort 分支（未触发，未验证）

Observation：
- 上轮收尾：`RED` + `失败 0，总计 2393`；本轮同过滤器完整跑完：`总计 2478`、`GREEN`（4m19s）。
- 改 `mutation-check.py`：`parse_summary()` + 「非零退出且 0 失败」⇒ `RED (… run looks aborted, N ran)`。
- **该分支本轮未触发**（跑完了），未经实跑验证。

`BotTask.Running` 类型：描述符不带类型；`xaml_bindings.json`/`XAML_BINDINGS.md` 无控件上下文 ⇒ **Unknown（两条路线走尽）**。

验证：变异 **59/59 fired，GREEN**（00:57:47）；形状 **97/12**；全量 **2476/0/2/2478**。

还剩什么：① 为 abort 分支造一个最小验证（假摘要）；② `Checkout.Profile` 归位；③ 其余 7 条 `prop-get`；
④ 判据 e 的两处文档手抄数字；⑤ `CreateModel.Inputs` 补或写明理由。
## R1192 —— Checkout.Profile 补上（形状 97/12→96/11）；CreateModel.Inputs 定案 Unknown

Observation：
- `ida.py str "Cybersole.Models.Checkout"`：原版只绑 `Profile`/`Order`/`Tracking`，三者均 `!Getter`+`!Setter`。
- 复刻件 `Checkout` 有 Order/Tracking、缺 Profile。
- `ida.py str "Cybersole.Models.CreateModel"`：`Inputs` 有 G+S，但类型仍不可知。

改动：`Checkout.Profile`（`Profile?`，SetProperty）。类型选择标 **Inference**（同仓 CreateModel/BotTask 的 Profile 都是模型对象），
存储形态标 **Unknown**，注释入源码。

验证：build 0 错；全量 **2476/0/2/2478**（4m23s）；形状 **96/11**。

还剩什么：① 其余 6 条 core 形状（BotTask.Running/Task、CreateModel.Inputs 均 Unknown；TaskGroup.Running、ClockService.Current、ExpressionExample.Output 为 prop-get）；
② abort 分支未验证；③ 判据 e 的两处文档手抄数字；④ 7 条 UI 侧 prop-get（冻结）。
## R1193 —— 三条 prop-get 改可写（93/8）；剩 3 条 Unknown；发现归属口径差异

Observation：
- `TaskGroup.Running` / `ClockService.Current` / `ExpressionExample.Output` 描述符均含 `!Setter`，复刻件原为计算只读。
- 改法统一为覆盖层/后备字段：**未赋值时行为不变**。
- 度量 `96/11 → 93/8`；我按声明项目统计的 core 行只剩 3（均 Unknown）。

验证：build 0 错；全量 **2476/0/2/2478**（4m21s）。

还剩什么：① 口径差异（工具 8 vs 我 3，同名类型分属不同项目）→ 下轮按完整命名空间归位；
② `BotTask.Running`/`Task`、`CreateModel.Inputs` 三条 Unknown；
③ abort 分支未验证；④ 判据 e 两处文档手抄数字；⑤ UI 侧 prop-get（冻结）。
## R1194/R1195 —— 撤回统计口径（我漏 interface）；修接口判到实现类；形状 93/8 → 89/4

Observation：
- 我上轮统计正则缺 `interface` ⇒ `IWebhook` 未入表 ⇒ 8 被我数成 3。**工具是对的。**
- `IWebhook` 六成员全 `{ get; }`；实现类 `Webhook` 的 Url/Name/Enabled/Type 有 setter，Events/ExtraFields 只读。
- 改：`shape_audit.py` 采集 `class X : IY` 关系，接口类型改判实现类类体；归属改按类体来源文件。

验证：build 0 错；全量 **2476/0/2/2478**（4m20s）；形状 **89 / 4**。

还剩什么：① `IWebhook.Events`/`ExtraFields` 回二进制确认可写性；
② 三条 Unknown（`BotTask.Running`/`Task`、`CreateModel.Inputs`）；
③ abort 分支未验证；④ 判据 e 两处文档手抄数字；⑤ UI 侧 prop-get（冻结）。
## R1196 —— IWebhook.Events/ExtraFields 改可写（89/4→88/3）；记下 Type 过度宽松（未改）

Observation：
- `ida.py str "IWebhook"`：Name/Url/Enabled/Events/ExtraFields 均 Getter+Setter；**Type 仅 Getter**。
- 改 `Webhook.Events`/`ExtraFields` 为 `{ get; set; }`（仍初始化为空集合）。

验证：build 0 错；全量 **2476/0/2/2478**（4m22s）；变异 **59/59 fired GREEN**（01:32:25）；形状 **88/3**。

**新增未办**：`Webhook.Type` 原版只读、复刻件可写（审计查不出"过度宽松"）——下一轮评估改只读的影响面。

还剩什么：① `Type` 改只读评估；② 三条 Unknown（`BotTask.Running`/`Task`、`CreateModel.Inputs`）；
③ abort 分支未验证；④ 判据 e 两处文档手抄数字；⑤ UI 侧 prop-get（冻结）。
## R1197 —— 文档数字带时点+口径（判据 e 第三条）；新增 DocumentNumbersAreSourcedTests

改动：`PARITY_CLAIMS.md` C6/C9 补「时点 / 当前见 METRICS / 口径不可相减」；`PARITY_PRODUCT.md` 表头加时点声明；
新守卫只查「陈述状态」的两份文档（排除 1100 行测量档案与 9000 行 backlog，理由写进注释）。

**口径陷阱**：产品的 187,328 是 `idautils.Functions()`，METRICS 的 179,456 是 `.pdata` —— **都真，但不能相减**。

验证：build 0 错；文档钉子 18/18；全量 **2477/0/2/2479**（4m22s）。

还剩什么：① `Webhook.Type` 改只读影响面；② 三条 Unknown；③ abort 分支未验证；
④ 产品表那次测量对应轮次未记（按 R707 附近处理）；⑤ UI 侧 prop-get（冻结）。
## R1198 —— 审计补反方向：over-permissive 45（新口径，与 88 分列）；Webhook.Type 记 Accepted deviation

Observation：
- 新增 `over-permissive` 一节与计数：**45**（原版 Getter-only、复刻件 `prop+set`）。
- 例：`IWebhook.Type`、`BotTask.Product`。
- `Webhook.Type` 未改：唯一赋值点在初始化器，且需 Newtonsoft 序列化到 settings.json，改只读有丢字段风险。

验证：build 0 错；全量 **2477/0/2/2479**（4m23s）；度量三字段 `88 / 3 / 45`。

还剩什么：① 45 条 over-permissive **逐类分诊**（持久化需求 vs 真偏差）；
② 三条 Unknown（`BotTask.Running`/`Task`、`CreateModel.Inputs`）；
③ abort 分支未验证；④ UI 侧 prop-get（冻结）。
## R1199 —— 修 kind_of 固定窗口（88→96 / core 3→8；over-permissive 45→37）；新增 prop-init

Observation：
- 旧实现 window = body[block.end():block.end()+400] 越界到下一个成员 ⇒ { get; init; } 被误判 prop+set。
- 改为按属性花括号配平取块；init 单列 prop-init。
- 数字三处变化均"变准"。

验证：build 0 错；全量 **2477/0/2/2479**（4m22s）；度量 **96 / 8 / 37**。

分诊规则：持久化驱动 → Accepted；收窄前置 = [JsonProperty] + 往返验证。
待查：Element.PropName 等是否纯 UI 状态。

还剩什么：① core 8 条缺口逐条（含 prop-init 新增的 5 条）；② over-permissive 37 条分诊；
③ abort 分支未验证；④ UI 侧（20 条）冻结。
## R1200 —— 修 4 处 init/只读集合 → 可写：缺口 96→92、core 8→4

Observation：
- `CreateInputModel.MaxPrice`（init→set）、`BotTask.Properties`、`CreateModel.Profiles`/`Tasks`（get→get;set;）。
- 四处均为纯放宽，且初始化为空集合；全量仍 2477 绿。
- 度量 `92 / 4 / 37`（over-permissive 未变）。

**剩下 3 条 core 缺口全是 Unknown**（`BotTask.Running`/`Task`、`CreateModel.Inputs`：成员类型不可得）。
**在范围内，可修缺口已清零。**

还剩什么：① 三条 Unknown 的取证尝试；② over-permissive 37 条分诊（`Element.PropName` 一类）；
③ abort 分支未验证；④ 变异全量重跑（本轮未跑）。
## R1201 —— 37 条 over-permissive 分诊第一步：证伪「持久化驱动」假设；Element.PropName 记 Accepted

Observation：
- `Core\Store` 中 grep 八类型：仅 Proxy/BotTask/Solver 命中；CaptchaProvider/IWebhook/Shortcut/License/Element **0 命中**。
- 分区：**core 8 / UI 29**。
- `Element.PropName`：0 个赋值点，但随 tasks.json 往返 ⇒ 收窄有丢字段风险 ⇒ Accepted（前置：`[JsonProperty]` + 往返测试）。
- 变异补跑：**59/59 fired，GREEN**（02:09:40）。

验证：形状 **92 / 4 / 37**（本轮无代码改动）。

还剩什么：① 查实各类型真实序列化路径（Settings 图 vs 独立 json）；
② 三条 Unknown（`BotTask.Running`/`Task`、`CreateModel.Inputs`）；③ abort 分支未验证；④ UI 29 条冻结。
## R1202 —— over-permissive 实证分诊：core 8 条全部有配置根可指（Accepted）；上轮 grep 位置错了

Observation：
- 配置根：`GlobalSettings.cs:178`（CaptchaProviders）、`Settings.Webhooks`、`Config.Solvers`、tasks.json、任务步骤内嵌 Element。
- 上轮"证伪"因 grep 的是 `Core\Store` 而非配置根 ⇒ **撤回该证伪**。
- `shape_audit.py` 注释补入分诊结论与前置条件（逻辑未改，度量仍 92/4/37）。

验证：文档钉子 18/18。

还剩什么：① 三条 Unknown（`BotTask.Running`/`Task`、`CreateModel.Inputs`）；
② abort 分支未验证；③ UI 29 条随冻结层；④ 变异需在下一次 src 改动后重跑。
## R1203 —— CreateModel.Inputs 落地（91/3）；BotTask.Running/Task 归档为证据边界

Observation：
- `xaml_bindings.json`：`CreateModel` 同时绑 `Input`/`Inputs`；`CreateInputModel` 独立绑定、13 成员（输入行形状）。
- 原版 `.cyb` 备份最新 4,158 B，仅 proxies，无 tasks ⇒ 拿不到 `Running` 的取值形态。
- 落地 `public List<Cybersole.Models.CreateInputModel> Inputs { get; set; }`（全限定，跨命名空间）。

验证：build 0 错（先 CS0246，改全限定后通过）；全量 **2477/0/2/2479**（4m21s）；形状 **91 / 3 / 37**。

**证据边界（缺什么已写明）**：`BotTask.Running`/`Task` 需类型元数据字段类型或含运行中任务的原版 tasks.json。

还剩什么：① 三条→两条 Unknown 的定期重试条件；② abort 分支未验证；③ 变异需在下次 src 改动后重跑；④ UI 29 条冻结。
## R1204 —— Bstn 4 条占位存疑：二进制三形状皆 0；store_catalog.py 是循环论证

Observation：
- `ida.py str` 搜 `bstn` / `BSTN` / `beastinpeace` → **n=0**；唯一 Beast 命中是 ARROW & BEAST。
- `analysis/bstn.txt` 自述来源为 **live capture**（`/api/beast/geoIP`、Adyen、`/cart.js` 404）。
- `analysis/store_catalog.py` 读的是复刻件 `CreateAll()`（65 条）⇒ 不能用来证明原版店清单。

判定：**Bstn 4 条记 Unknown（缺：原版店清单形状的证据）**；**不删 BstnFlow，也不宣称 4 条是缺口**。
两种可能：原版无此店（则它是额外实现）/ 原版有此店但形状未试尽。

还剩什么：① 找原版店清单形状（第 4 种可能）；② 两条 Unknown（`BotTask.Running`/`Task`）；
③ abort 分支未验证；④ UI 29 条冻结；⑤ 变异需在下次 src 改动后重跑。
## R1205 —— 对照组推翻「域名判据」；改用显示名后 BSTN 五形状全 0 ⇒ 4 条占位归「扩展」

Observation：
- 域名对照：100thieves ✓ / afew ✓ / capsule ✓ / **bodega ✗** / bstn ✗ ⇒ 域名判据 **1/5 假阴性**，不可用。
- 显示名判据：`Bodega` → `0x146b5fff4` 命中 ⇒ 原版用显示名。
- BSTN 五形状（bstn/BSTN/beastinpeace/Beast in Peace/BSTN Store）全 0。
- `CORE_COVERAGE.md` 新增行：「属于扩展、不构成原版缺口 = 4」。

判定：Bstn 的 4 条**归为扩展空缺**，不再投入；**不删 BstnFlow**（产品决策）。

验证：文档钉子 **50/50**。

还剩什么：① Farfetch 7 条（服务端下发，已定性）；② 两条 Unknown（`BotTask.Running`/`Task`）；
③ abort 分支未验证；④ UI 29 条冻结；⑤ 原版店清单未枚举。
## R1206 —— 店清单分档：30 确认 / 1 池外确认（Bodega）/ 1 扩展（BSTN）/ 2 未定（Livestock、HMVS）

Observation：
- 池筛：34 家里 30 家名字或域名命中；4 家池外。
- `ida.py str`：`Bodega` n=1（0x146b5fff4）；`Livestock` 仅命中模板变量 `_raffleProduct`；`HMVS`/`shophmvs.com` 全 0。
- 解析器只认 34 家（多词店名被跳过）⇒ **下界**，非全量。

方法固化：**池筛用于省调用，池外一律回 `ida.py str`**（Bodega 再次证明池子会漏）。

还剩什么：① Livestock / HMVS 的显示名形状；② 原版店清单的完整枚举（下界 34，未穷举）；
③ 两条 Unknown（`BotTask.Running`/`Task`）；④ abort 分支未验证；⑤ UI 29 条冻结。
## R1207 —— 店清单四条字符串形状全否决；下一步＝读表字节，但先修 ida.py call 输出

Observation：
- 源码提取：模块与域名的清单（条数以度量工具为准）。
- 池外 9 域名 `ida.py str` **全 0**（含 farfetch.com / yeezy.com / snkrs.nike.com）⇒ 域名判据死亡。
- `Farfetch` n=3（0x14338eadc / 0x146d8dfdc / 0x146d8e004 "Farfetch Checkout"）；`Yeezy` 命中商品名；`Pop Mart` 命中 CSS。
- `0x146d8dfcc`（chars）与 `0x146d8dfc0`（obj_va）**0 xref**；disp32 全扫 **0 site**。

⇒ 店清单是**数据表**，字符串 + xref 路线原理上够不到。

**下一轮取件（已定位）**：① 修 `analysis/ida.py call` 的输出为可解析 JSON；② 用 `get_bytes` 转储 `0x146d8dfdc` 邻近 UTF-16 串，重建原版清单。

还剩什么：两条 Unknown（`BotTask.Running`/`Task`）；abort 分支未验证；UI 29 条冻结。
## R1208 —— 串池按字母序、无独立店表；Livestock/HMVS 同 BSTN 属扩展（3/38）

Observation：
- `ida.py py` 取字节成功（`call` 返回 MCP content 非 JSON ⇒ 绕开）；布局 [MT*:8][Len:4][chars] 再次吻合。
- 从 0x146d8de30 连读 95 串，**字母序**：Family Mart → Farfetch → **Farfetch Checkout** → Fashion Place → Fear Of God。
- `HMV` 6 命中全噪声；`Livesto` 2 命中全是模板变量。
- 分档：30 确认 / **3 扩展（bstn、livestock、shophmvs）** / 0 未定。

**教训**：前四轮在**错误的抽象层次**上找东西——找表，而它是按字母序的平坦串池。

还剩什么：① 若要枚举完整原版清单，需按字母序分段转储并人工筛选（可行但耗调用）；
② 两条 Unknown（`BotTask.Running`/`Task`）；③ abort 分支未验证；④ UI 29 条冻结。
## R1209 —— 差点丢掉 AOT 产物：publish 未传 -p:PublishAot=true 只出 459 KB 壳，尺寸检查抓住；已重发 57.4 MB

Observation：
- csproj 全仓 **无 PublishAot**；正确命令见 `BINDING_BACKLOG.md:5782`。
- 错误命令 exit 0、产物 459,264 B，并覆盖了旧 54.7 MB 镜像。
- 重发（带 -p:PublishAot=true）：**57,403,392 B**；.pdata 179,456 → **179,584**；above-boundary 604 → **737**。
- 产物陈旧度 **0**；类型级缺口 **0**；名字级 real gap **0**；形状 91/3/37。

**新规则**：publish 判据 = 尺寸数量级 + .pdata 计数 + artifact_freshness，三者缺一不可。

还剩什么：① 查是否别处也裸调 publish；② CS0108 警告（Checkout.Profiles 隐藏继承成员）待看；
③ 两条 Unknown（BotTask.Running/Task）；④ abort 分支未验证；⑤ 变异需重跑（本轮改了产物）。
## R1210 —— 删掉 Checkout.Profile 的重复声明（类型矛盾）；审计补基类继承（第三次"只看一处声明"）

Observation：
- `BaseCheckout.Profile` 是 `string?`；R1192 在 `Checkout` 又加了 `Profile?`（对象）⇒ CS0108 + 类型矛盾。
- 全仓无对象形式赋值 ⇒ 删除派生那份，保留 string。
- `shape_audit.py` 现在并进基类类体（BFS ≤40 层）⇒ `Checkout.Profile` 不再报 `?`。
- 文档守卫 `TheModuleCountPhraseDoesNotSpread` 16→17 报红，四处改写成"清单（条数以度量工具为准）"。

验证：build 0 错；形状 **91 / 3 / 37**；全量 **2477/0/2/2479**（4m22s）。

还剩什么：① 三处 UI 层 CS0108（冻结）；② 两条 Unknown（BotTask.Running/Task）；③ abort 分支未验证；
④ 变异需重跑（本轮改了 src）。
## R1211 —— AOT 重建（尺寸/pdata/freshness 三条）；哈希判据被校准否掉

Observation：
- 重发：57,403,392 B、`.pdata` **179,584**（未变）、freshness **0**。
- **同一源码连发两次哈希不同**（`847757a0` vs `39e8fd73`）⇒ 构建不可复现 ⇒ 哈希**不可作变更判据**。
- 工具已改为：摘要=出处记录；变更信号用 `.pdata`/节体量/标记串。注释里的错误说法已删。
- 变异 **59/59 GREEN**（02:55:22）；全量 2477/0/2/2479；Freshness|Artifact 5/5。

还剩什么：① 两条 Unknown（`BotTask.Running`/`Task`）；② 三处 UI CS0108（冻结）；
③ `Checkout.Profile` 是否曾进过历史产物（Unknown，不影响结论）；④ 优先级②支付层可开新取件。
## R1212 —— Stripe payment_methods 两条路径解码（sub_140959320=basil 挑战 / sub_140BDA320=acacia 表单）

Observation：
- `sub_140959320`（2,203 B，2 xref）：`https://api.stripe.com/v1/payment_methods` + `Stripe-Version: 2025-08-27.basil`
  + `card[number|exp_month|exp_year|cvc]` + 8 个 `billing_details[...]` + 6 个 `client_attribution_metadata[...]`。
- `sub_140BDA320`（6,526 B，2 xref）：载入 `&_stripe_version=2025-01-27.acacia`（0x146a7b048）。
- 六个 Stripe 步骤名本身 0 xref（数据表条目）。

**判断纠正**：先误判「复刻件版本写错」，实为**两条路径两个版本**，`Gateways.cs:163-164` 早已写明 ⇒ 复刻件正确。

**下一步**：改 `PAYMENT_CHALLENGES.md` 的**生成器**（该文件是生成物，禁手改），把 payment_methods 两条路径写进去；
其余五步（意图/提交/校验/fallback）仍待解码。

还剩什么：① 五步 Stripe 方法体；② 两条 Unknown（BotTask.Running/Task）；③ UI CS0108 三处（冻结）。
## R1213 —— Stripe 六端点→构建器全表；两函数解码确认与 R1094 实现逐字段一致；新增 analysis/func_strings.py

Observation：
- 端点表：base→sub_140BE31F0；payment_methods→sub_140959320 + sub_140BDA320；payment_intents→4 函数；
  setup_intents→sub_140BE0F80/sub_141145DB0；3ds2/authenticate→sub_1411474A0(+2)；3ds2/challenge_complete→sub_141144C20(+1)。
- sub_141144C20：cres/final_cres/_stripe_account/key/source + hooks.stripe.com/3d_secure_2/notify/。
- sub_1411474A0：9 browser* + fingerprint* + frontend_execution + one_click_authn_device_support[...]。
- **两处均已在 MagentoFlow.cs:1452-1512 实现（R1094/R1099），地址注释一致 ⇒ 本轮无新实现。**

**新工具**：`python analysis/func_strings.py <va>` —— 解码并自动报告"复刻件里已有"。

还剩什么：① 五步 Stripe 中未被端点引用的部分；② setup_intents 两条路径未解；
③ 两条 Unknown（BotTask.Running/Task）；④ UI CS0108 三处（冻结）。
## R1214 —— Stripe setup_intent confirm 落地（sub_140BE0F80）：13 个 payment_method_data 键 + card-element UA；+7 测试

Observation：
- `sub_140BE0F80`（2,844 B）：`/v1/setup_intents/{id}/confirm`；`payment_method_data[card][number|cvc|exp_month|exp_year]`、
  `[type]`、`[payment_user_agent]`、`[time_on_page]`、`[pasted_fields]`、`[referrer]`、`[sid]`、`[muid]`、`[guid]`、
  嵌套归属元数据 4 条；`use_stripe_sdk=true`；`expected_payment_method_type`；`radar_options[hcaptcha_token]`。
- UA `0x1471654A0`（card-element）≠ payment-method create 的 `0x1471655C8`（payment-element/autopm）。
- 查重（func_strings.py）：14/33 已存在，但**无一条 payment_method_data** ⇒ 真缺口。

验证：build 0 错；新测试 **7/7**；全量 **2484/0/2/2486**（4m25s）。

下一步：`/v1/payment_intents/` 的四个函数里未实现的部分；`setup_intents` 另一条 `sub_141145DB0`（0x472）待解。
## R1215 —— setup_intents 检取 URL 落地（sub_141145DB0，4 条常量）；+3 测试

Observation：
- `sub_141145DB0`（1,138 B，185 行）：0x147054FE0 + 0x146B28808 + 0x146A84588 + 0x146A7AFD8，**仅 4 条常量**。
- 查重：`&key=`/`&_stripe_account=` 在 MagentoFlow（payment_intents）；setup_intents 前缀缺。
- 新增 `StripeGateway.SetupIntentRetrieveUrl`，`&_stripe_account=` 无条件留槽。

**判断法**：同一前缀两种动作——**常量集合大小**（4 条=拼 URL / 33 条=拼表单）可当场分辨。

验证：build 0 错；StripeSetupIntent **10/10**；全量 **2487/0/2/2489**（4m23s）。

下一步：`/v1/payment_intents/` 四个函数中未实现的（sub_140A40170 0x5c0、sub_140B58D60 0x9d4）。
## R1216 —— payment_intents 检取落地（sub_140A40170，false + clover）；镜像有**三个** Stripe 版本

Observation：
- `sub_140A40170`：0x147054F08 + 0x146B287A8(`?is_stripe_sdk=false&client_secret=`) + 0x146A84588 + 0x146A7B010 + 0x146ADFC98(`2025-09-30.clover`) + 0x146A7AFD8 + `acct_1S0JRiIiwyy5Cf6X`。
- 既有 `MagentoFlow:1441` 注释指向 `sub_1411458f0`（true、无版本）⇒ 两条构建器，非重复。
- 三版本地址相邻：0x146ADFBE0(acacia) / C60(basil) / C98(clover)。

新增 `StripeGateway.IntentVersion` + `PaymentIntentRetrieveUrl`；测试断言三版本互不相等、片段存在（**不断言整串顺序**）。

验证：build 0 错；**12/12**；全量 **2489/0/2/2491**（4m23s）。

下一步：`sub_140B58D60`（0x9d4，payment_intents 的第三条构建器）。
## R1217 —— PayPal-via-Stripe confirm 落地（sub_140B58D60）：mandate_data 两键 + return_url + 第三条 UA

Observation：
- `sub_140B58D60`（2,516 B）：`payment_method_data[type]=paypal`；`mandate_data[customer_acceptance][type]=online`；
  `mandate_data[...][online][infer_from_client]`；`return_url`；账单地址 country/postal_code；`radar_options[hcaptcha_token]`；
  UA `stripe.js/d6356e1526; …; payment-element`（0x1471659D8）；`pk_live_YrdnDi9u37CWhYvVzpH1ytPf`。
- 查重：19/30 已存在，`mandate_data`/`infer_from_client`/`d6356e1526` **全缺**。

新增 `PayPalConfirmUserAgent` / `MandateAcceptanceType` / `PaymentIntentConfirmUrl` / `PayPalConfirmForm`；
`inferFromClient` 为**参数**（裸 `true` 与键的配对不可观察）。

验证：build 0 错；**15/15**；全量 **2492/0/2/2494**（4m24s）。

下一步：三条 UA 的三处调用面是否都需在 flow 里接线（当前只有 MagentoFlow 用其一）。
## R1218 —— 四个构建器经间接派发，xref 走不到调用面；复刻件侧零调用点（能力已就位、未接线）

Observation：
- 四组 xref 的调用者全在 0x1425xxxx–0x142Bxxxx；`sub_1425456E0` 反编译为一行 thunk `return sub_140B58D60(a1 + 64);`，上游无名。
- `PayPalConfirmForm`/`SetupConfirmForm`/`SetupIntentRetrieveUrl`/`PaymentIntentRetrieveUrl`/`PaymentIntentConfirmUrl`
  在 replica/src **只命中定义行，零调用点**。

**判断**：协议已解码可用 ≠ 流程已使用。**不接线**（缺派发槽依据）。
缺的工件：flow 步骤表里指向这些函数的那一格。

还剩什么：① 派发槽解析（vtable/步骤表）；② 两条 Unknown（BotTask.Running/Task）；③ UI CS0108（冻结）。