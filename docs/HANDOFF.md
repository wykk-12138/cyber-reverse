# 交接（2026-11-16 20:40，R826 后）

## 现在在哪

- **轮次**：R826 已提交（`git log` 顶端应为 `drop the record helper` / `R826: NikeFlow reads structurally…`）。
- **内存**：重启后 20.1 GB / 31.71 GB，**全量已复跑：1766 / 0**。
- **IDA**：**已开启并就绪**（`health` = `status=ok / hexrays_ready=true`，13337 LISTENING）。
- **套件**：最后一次确认绿是 R823（`DocsConsistencyTests` 7/7）。**R824–R826 未跑全量**（内存纪律）。
  重启或内存回到 2 GB 以上后先跑一次 `python tools\metrics_report.py`，**期望 1766 / 0**。
- **四项度量**（沿用 R820）：名字级 `real gap 4 / missing 16` · 类型级 `0` · 类型缺失 `17` · 形状 `78` · 文案 `0`。

## 完成判据现状

| 判据 | 状态 |
|---|---|
| (a) 类型级缺口 / 类型缺失 | **已分类完毕**：见 `docs/TYPE_PRESENCE_TRIAGE.md`（2 越界 · 7 改名 · 1 结构性 · 7 契约无判别力） |
| (b) 文案 | **0**，无剩余 |
| (c) 产物级对照 | **PASS** —— `python analysis\verify_artifact.py`：1142/1142 locale · 20/20 资源 · 12/12 叶子 |
| (d) claim 表 | **PASS 规则** —— `python analysis\check_claims.py`：5 行，2 pass / 3 fail，全有 authority |
| (e) 套件 / 变异 / 数字来源 | **待一次全量确认**（内存所限未跑）；数字全部出自 `docs/METRICS.md` |
| (f) 核心覆盖表 | 风控已对账（R807）；站点复刻件→镜像已逐条（49/57 有据 · 6 零 · 2 仅噪音）；**镜像→复刻件未分类** |

## 未结案项（按价值排序）

1. **`RefreshSession` 在镜像元数据里零匹配（R827）** → 方向看起来是删声明。**但 R828 补了一个限定：trimming 可能裁掉未使用的 `async` 方法名，所以这是 Inference 不是 Observation。**
   `HandleBlock` 反过来：**镜像有、复刻件 0 匹配** —— 名字级缺口，且名字暗示「处理封锁」，**与优先级 ② 直接相关，值得单独一轮**。
   `SetRequest` / `HandleResponse` 在镜像里有，调用点待反编译。
2. **长度守卫（R826）**：`ScheelsFlow`（`body.Length > 200`）与 `BstnFlow`（`> 2000`）把「响应体短/空」也判成
   `available=false`。**误报缺货 = 错过 drop，不可重来**，而它由与商品无关的量决定。
   两种改法（明确失败 / 先看 `lastStatus` 判 `Blocked`）**都需要镜像证据**。
3. **8 个未通读的可用性解析**（通读 12/20）：`Hbx` `Hybris` `Magento` `JohnLewis` `PopMart` `YeezySupply`
   `Casio` `Shopify`。**其中还有几个用长度守卫？Unknown —— `BstnFlow` 是偶然撞见的。**
4. **3 个忽略 `c.Url` 的流程**（`NikeFlow` / `PoqAppFlow` / `SuperswipeFlow`，与 `ModuleRobustnessTests`
   例外名单一致）：**待判「忽略是对的还是遗漏」，判据在镜像里。** 工具：`analysis\scan_url_ignoring4.py`。
5. **镜像→复刻件方向**：池子有 1182 个 `myshopify` 主机（**下界**），复刻件 33 个别名覆盖 30。
   **未分类，成因写的是「未逐个取证」。**

## 工具的可信边界（这一条最省时间）

- **`analysis/pe_strings.txt` 是抽样**（180,228 行 vs 镜像 324,895 条串）。**正向可用、反向不可用** ——
  反向结论用 `python analysis\ida.py str <pat>`。见 `AGENTS.md` §2.7b。
- **`ida.py str` 默认 `limit 40`**（已加 `--limit`），**插件侧还有约 500 条上限**。数数要写明是下界。
- **判断「某方法是否被调用」不要用调用图扫描**：委派是**无接收者**调用（`=> FindProductAsync(c, ct)`），
  `\w+\.名字` 一定漏。**用「裸名字总提及次数 = 1 ⇒ 只有声明 ⇒ 真死」这个判据。**（R824 两次扫描都错在这）
- **按花括号或「最近前缀 class」定类边界都会错**（一文件多类 + 字符串里的 `{`）。
  **可用做法**：缩进切类 + 截到下一个成员声明（`scan_url_ignoring4.py`）。
- **文档守卫**：`DocsConsistencyTests` 扫 `replica/docs/VERDICT.md` 正文里所有「数字 + 个模块 / modules」，
  要求全等于 63。**写记录时别把违规字符串抄进去** —— 引号复述等于又写一遍（这个坑踩过三次）。
- **`Get-Content -Raw` 读 1.9 MB 的 `VERDICT.md` 会把中文比错**。判断文件内容**只看字节**
  （`io.open(p, 'rb')` + `decode('utf-8')`）。

## 机器相关

**内存不足导致重启过一次。** 重启后若 `available < 2GB` 只用 `-m:1`；`< 1GB` 停构建。
**IDA 若需重开**：后台跑 `powershell -File "D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1" -Path <目标.i64>`，
同时用 CUA 轮询点掉「请确认」类对话框，**判据是「再读一次没有框」**。
**IDA 未开时不要硬做需要反编译的事** —— 本轮次两次因此挂起（R824、R826 的镜像侧问题）。

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
