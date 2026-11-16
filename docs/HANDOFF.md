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
