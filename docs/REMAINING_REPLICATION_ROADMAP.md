# 完整复现剩余工作路线图（Phase 1 + Phase 2 收口基线）

> **记录日期**：`2026-11-20` · **代码基线**：`main` `4da6712`（Phase 1 8/8 本地缺口 + Phase 2 Waves 2A–2D 已落地，NativeAOT 产物已重发布且状态为 `current`，5 步最终验收门禁全绿）。
> **唯一动态指标源**：`docs/METRICS.md`（由 `python tools/metrics_report.py` 生成）
> **关联权威档案**：`docs/MODULE_FUNCTION_CENSUS.md` · `docs/PROGRESS_AND_GAP.md` · `docs/SHAPE_GAPS.md` · `docs/PARITY_CLAIMS.md`
> **口径说明**：下文引用的函数与覆盖统计均为 `2026-11-20`（`4da6712`）时点快照观测值；实时动态数值一律以 `docs/METRICS.md` 最新生成输出为准。

---

## 一、本机仍可继续推进的静态逆向与工程工作（不依赖新凭据或商业库）

这部分工作完全依托现有 `target/Cybersole.exe`（5.18.32）、`target/Cybersole.exe.i64`（IDA Pro MCP）、`target-alt/Cybersole-5.18.35.exe` 与复刻工程源码，可在本机直接反编译并落地为可执行代码。

### 1. `Cybersole.Stores` 站点流程与支付状态机深化（最大核心业务缺口）

- **体量差距观测**（`docs/MODULE_FUNCTION_CENSUS.md` 2026-11-20 快照）：原版仅靠字符串种子 + 保守 2 跳调用图传播即已归因 **`5,090`** 个 `Cybersole.Stores` 函数（`4.41 MiB`），复刻件全部 `Cybersole.Stores` 为 **`3,403`** 个 `.pdata` 函数（`829 KiB` / `848,939` 字节，代码字节比约 **5.44 倍**）。
- **异步状态机名长尾**：
  - 店铺流程异步名：原版 `103` 个名（`408` 次实现）已在 `replica/src/` 覆盖 `70/103`（对应 `375/408` 次出现），仍有 **`33` 个长尾步骤名**待反编译补全或逐一核实去向；
  - 支付/3DS 异步名：原版 `124` 个名（`195` 次实现）已覆盖 `47/124`（`118/195` 次出现），仍有 **`77` 个细分支付方法**待进一步对位。
- **4 处已定位但尚未穷举的静态 `Unknown` 子分支**（见 `docs/PROGRESS_AND_GAP.md`）：
  1. ~~**Unzer 3DS**：`0x14094c210` prepare 精确子路径~~ —— **R1301 已解且归属纠正，R1302 已落码**：
     `0x14094c210` 不是 Unzer，它是**发请求前的配置委托**（`sub_1408B61E0` 里 `(*(a3+32))(a3[1], v6)` 就在
     `sub_1408B5EB0` 发送之前调用它），落的 15 条头是全站浏览器模板，另有 `Akamai: 1`（`a2+112`）、
     `+226 = 1`、`200`/`400` 两条状态处理器；URL 在调用方 `sub_14095B4E0` 内：
     `https://www.casio.com/{storeCode}/rest/V1/stripe/payments/get_stripe_configuration?_=<tick>`。
     **R1302 落成** `StripeGateway.FetchConfigurationAsync`（+ `StoreConfigUrl` / `StoreConfigHeaders`），
     在 `AuthorizeAsync` 里按 `sub_140F9E790` 的「还没取到才取」条件接入；`UnzerGateway.PreparePaymentAsync`
     与 `unzer.prepareUrl` 那条人供虚构路径已删除。**仍 Unknown**：`a2+112` 那个集合到底是不是 cookie
     （`Akamai`/`1` 因此未发送）；`apiKey` 的读取方不在本条链上——`0x146F7544C` 的 4 个引用者是
     `sub_14094DEB0`、`sub_1409F2A60`、`sub_140ECF2B0`、`sub_14117B6C0`。**Unzer 侧两项 R1306 已结案**：`0x14094a870` = 两个 `IndexOf(OrdinalIgnoreCase)`（`unzer.com` / `heidelpay`）→ `IsUnzerThreeDsUrl`；
     `qword_1472c65a0+8` **不是哈希表**，它的懒初始化器 `sub_14094AB00` 分配一个十元 `string[]` 装十句失败措辞 → `TerminalPhrases` / `IsTerminalFailure`，
     并已在 `RunUnzerThreeDsAsync` 起点接入（页面说「declined」就此结束，不再跟跳）；
  2. **Checkout.com**：分派层 **R1303 已完成**——`0x1408a34f0` 是按发卡行 ACS 主机名切分的 switch（**28 个主机名 / 18 个长度分支**），开头打 `"Starting 3DS: <host>"`（类目 `3DS`）、把传输指纹临时换成 `chrome_131`、建对应处理器、再把原指纹写回；已落成 `AcsHosts`（`Known` / `HostOf` / `IsKnown` / `ProfileFor` / `Describe`与 `CheckoutComGateway.ResolveEswThreeDsAsync` 接线）。**仍 Unknown**：每个主机处理器的方法体（逐家挑战表单字段在其中）；
  3. **Komoju**：`0x140d98f60` 的「`[1..56]` `formUrl` 后缀」**R1304 已撤回**——该函数只构建 `{authenticity_token, payment_details:{type:konbini, email, store, given_name}}`（与复刻件已有的体一致），URL 取自状态机上下文 `*(*(v3+16)+16)`。同时新解并落码了兄弟机 `0x140D994D0` 的卡面（`KomojuGateway`）。**仍 Unknown**：`formUrl`（konbini 与卡凭证两个请求体的目标）；
  4. **`Topps`**：**R1305 已结案形状面**——`off_1449B8EB0` 是 JSON 类型句柄，不是键名表；类形从镜像的反射元数据读出（`ToppsCommerceProduct`：`PriceAmount` / `ProductImage` / `ProductVariant` / `SelectedOption` / `VariantImage` / `ToppsCommerceProductUrl` / `JToken`，加 `ListToppsCommerceProduct` 等 4 个列表承载名），已落成 `ToppsCdn.Parse` 并接回 `FindProductCdnAsync`。**仍 Unknown**：序列化键的大小写（响应两种写法都能读）。


  5. **长尾名单已落成表**（R1307）：`docs/ASYNC_TAIL.md` 是生成的，把镜像 801 个 `<名字>d__NN` 状态机名
     按 declared / mentioned / absent 三态对上复刻件源码。**支付家族 110 个名里 66 个 absent**，
     店铺家族 74 个里 34 个 absent。**取件优先从这张表的 absent 列里挑**，不要再用「剩 77」这个没有出处的数字。
     定位方法已探明：状态机名按类编号且成串出现（如 `0x14338377d` 是
     `<GetStripeConfiguration>d__87` … `<SubmitUnzerOrder>d__100` 一张序列表），可据此按类枚举方法。
### 2. UI 绑定形状与交互语义收口（`docs/SHAPE_GAPS.md`）

- 名字级与类型级绑定缺口虽已归零（`real gap=0`、`types with scope misses=0`、`unclassified=0`），但成员形状仍存在 **`84` 条差异**（其中 core 差异 `1` 条）：
  - **`39` 条「需要选择模型」**：复刻件实现为带参方法，原版为可绑定属性（如 `AnalyticsView.ChangeChart`、`AnalyticsView.OpenRelease`、`CaptchaProvidersView.Reorder`、`CustomBrowser.Back` 等），需在引入列表“当前选中项”后驱动 `ICommand`；
  - **`22` 条通用名撞名项**（如 `Delete`、`Save`、`Create`）：机械扫描无法消歧，需逐类反编译原版对应视图确认是否真实具备该本地动作；
  - **`17` 条结构差异不补**、`4` 条计算属性、`1` 条弱改名；
  - **`1` 条真缺**：`CustomBrowser.Autofill`（与嵌入式浏览器引擎耦合）。
- **结构确定但语义仍标 `Unknown` 的 UI / 契约项**：
  - `MonitorView` 3 条未定语义命令（`OpenUrl`、`LinkChange`、`Quicktask`，见 `docs/PARITY_CLAIMS.md` §3.5；当前仅保留显式空钩子）；
  - `ProxyTester.Name`、`SmartActionsView.Export`、`Cybersole.Providers.IDataProvider` 契约落地；
  - 原版专用的 `AvaloniaEdit` 代码编辑器控件与独立的 `TaskCreatorAdvancedView`（复刻件已合并至 `TaskCreatorView`）。

### 3. 传输层（HTTP/3、生产级自定义 TLS 指纹）与 HTML 解析栈对位

- **网络传输对位**：复刻件当前生产路径为 BCL `SocketsHttpHandler` + `SslStream`（Phase 1 已证实原版 BCL `Http3Support="false"`，无 `System.Net.Quic`/`msquic`），自研 `BouncyTls` 明确标注为实验传输；而原版针对店铺请求包含 Go 移植自定义传输栈（默认 `chrome_131`，且 ASICS 路径启用支持 HTTP/3 的 `chrome_150`）。若需要完整网络指纹与 HTTP/3 生产级对等，需继续补齐生产级自定义 TLS 握手与 QUIC/HTTP3 传输层。
- **HTML DOM 解析栈**：原版内嵌 `AngleSharp`（`154` 个已归因函数）处理 HTML 表单/选择器解析，复刻件目前以轻量字符串/正则解析为主，复杂页面解析鲁棒性可进一步对位。

### 4. 行为等价与字符串分类验收升级

- 闭合 `docs/PARITY_CLAIMS.md` 中长期记为 `unknown` 的两项高层判据：
  - **`C7c`（核心函数行为等价）**：从核心店铺与支付函数出发，建立“同输入 → HTTP 请求报文 / 状态转移”级可复算行为探针，替代单纯的覆盖率/签名对照；
  - **`C8`（字符串池分类对照）**：建立按 locale 键、URL 端点、错误消息三类切分的原版 ↔ 复刻 AOT 产物自动化比对工具。

---

## 二、必须先补齐外部条件才能推进的工作（`External Blocked`）

这部分逻辑或数据不存在于离线可执行文件本体中，或依赖受限外部设施，未获外部条件前**严禁猜测或编造实现**：

1. **需要原版有效登录账号 / 许可**
   - **服务端配置下发与线上站点目录**：捕获 `https://api.cybersole.io/connect/app` 的 `SignalR` 通道（原版 `SignalR` `51` 函数、`35` 个 `*Dto` + `21` 个 `Remote*`，含 `ConfigAdded` / `SharedAdded` / `ConfigRemoved` / `SharedRemoved` / `SubscribeGroups` / `UnsubscribeGroups` 6 键），方能解锁 `FarfetchFlow` 7 条服务端下发路由与完整线上站清单（见 `replica/docs/CORE_COVERAGE.md`）；
   - **云同步 / 队列 / 认证 / 更新基础设施**：`RabbitMQ.Client`（`12` 函数）消息协议、`MSAL`（`Microsoft.Identity.Client` `57` 函数，含 Outlook OAuth2 交互令牌刷新）、`Velopack`（`23` 函数，当前 `cdn.cybersole.io/releases/` 返回 404）；
   - **主界面实机观察与完整备份**：实机触发并观察 B 类 31 条 UI 本地动作（`docs/R508_LICENSE_GATE.md`）、`MonitorView` 3 条命令动作；并获取**包含非空 `profiles` 的原版 `.cyb` 备份**，以闭合 `Profile.Card` / `Username` 的落盘结构（`docs/PARITY_CLAIMS.md` §5）。
2. **需要真实站点流量抓包（Live Capture）**
   - 闭合 `Stores/Flows` 中 **23 条 `inferred` 0 命中项**（R1266 已证 NativeAOT 部分字面量逐字节不可搜），以及真实结账环境下 Unzer / Cardinal / Checkout.com / 便利店与各站接口的实机报文对齐。
3. **需要决定嵌入式浏览器引擎方案**
   - 原版使用商业授权的 **`DotNetBrowser 4.3.5.8591` + 外部 Chromium**（`DOTNETBROWSER_CHROMIUM_DIR`），对应 `DotNetBrowser.*`（`653` 归因函数）与 `Cybersole.Web.BrowserHandlers`（`IBrowserSessionView`、`PaymentAutofill`、`CustomBrowser.Autofill` 等）。
   - 复刻件 `CustomBrowser` 目前仅为无浏览器内核的 Avalonia 占位窗口；必须拍板选择“接入商业 DotNetBrowser 授权”还是“使用开源 WebView2/CEF 重构等价宿主”。

---

## 三、不必盲目追平的“结构性非等价噪声”

后续验收不得把 `docs/METRICS.md` 里的 `.pdata` 函数总数比追到 `100%` 作为完成判据，原因如下：

1. **.NET 10 NativeAOT vs .NET 8 NativeAOT 运行时差异**：原版与复刻件主目标框架不同，BCL、NativeAOT CRT、PE 节布局（`6` 节 vs `9` 节）、以及原版静态 Brotli 库 39 个导出（`docs/GOAL_VERIFICATION.md` `C2/C3/C4`）天然不同。
2. **AOP 编译织入 vs 手写通知**：原版依赖 `Metalama.Framework`（`33` 函数）做编译期属性通知织入，复刻件采用手写 `ObservableObject` + `RelayCommand`。
3. **函数体量构成悬殊**：复刻件 `.pdata` 中 **`86.48%`** 为 `System.*` / Avalonia / CRT，`Cybersole.*` 自研业务代码仅占 **`3.17%`**（`5,956` 函数 / `1.52 MiB`，`docs/MODULE_FUNCTION_CENSUS.md`）。度量应聚焦 **`Cybersole.*` 业务函数覆盖与实机请求等价**，而不是被外部运行时与 UI 框架分母带偏。

---

## 四、分条件推荐推进顺序

| 条件前提 | 推荐优先路线 | 说明 |
|---|---|---|
| **路线 A（无新凭据 / 无商业引擎授权）** | 本机静态深化路线 | ① 沿 `chars_va - 12` 清零 4 处支付/流程 `Unknown` 子分支 + 33 条店铺长尾异步步骤；② 推进核心请求报文等价探针（`C7c`）与分类串比对（`C8`）；③ 按需引入 `AngleSharp` 与生产级 TLS/HTTP3；④ 评估收口 `SHAPE_GAPS` 选中项模型与 `MonitorView` |
| **路线 B（获得原版有效许可 + 备份 + 抓包）** | 外部阻塞解锁路线 | ① 抓一次 `/connect/app` 解锁 `FarfetchFlow` 7 条路由与 SignalR 云同步模型；② 闭合 23 条 `inferred` 实机报文与真支付响应；③ 导入非空 `profiles` `.cyb` 闭合 `Profile.Card` 与 B 类 31 条 UI 本地动作（见 `docs/R508_LICENSE_GATE.md`） |
| **路线 C（需完整内置浏览器可用）** | 浏览器引擎拍板路线 | 先由项目负责人决策商业 `DotNetBrowser` vs 开源 WebView2/CEF 方案，再落地 `Cybersole.Web.BrowserHandlers` 与 `CustomBrowser.Autofill` |
