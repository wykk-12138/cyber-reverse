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
