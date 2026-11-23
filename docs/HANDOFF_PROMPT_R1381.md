# 接手提示词 · R1381 快照（经 R1382 审计纠偏：静态议程未结案）

> **R1382 重要纠偏（2026-11-23）**：本文原稿在 R1381 宣布「65/65 落地、①–③ 静态议程已结案、④ UI 绑定解冻」，经 R1382 逐项源码与工具审计后**已撤回该收口判词**：
> 1. `operation_gap.py` 原统计的是“源码文本里出现同名 GraphQL 文档常量”（65/65 仅代表文本声明），并非生产流程全部可达（大量操作仅在同文件 `DocumentFor` `switch` 中，或挂在全仓无人写入的 `Session.Vars` 旁路键后）；
> 2. `classify_payment_tail.py` 原稿误把含 80 个已实现项的 243 全量支付名当成缺失长尾并拼出“267 残余”，已修正为基于 `ASYNC_TAIL.md` 真实 `absent` 集复算；
> 3. `core_coverage.py`（漏计 Farfetch 7 步与 Saucony 拒绝步）、`vendor_coverage.py`（删表后强行 `missing=0`，而运行时仅 Kasada 接通）、`audit_document_constants.py`（`<200` 盲区放过截断的 `ItemDocument`）、`orphan_documents.py`（自撞/同文件盲区）、`PARITY_CLAIMS.md` C8 八列损坏、以及 `.snapshots` 污染（“65,773 文件”中 98.3% 是历史快照）均已在 R1382 修复；
> 4. **①–③ 仍有明确可做的本机静态任务**（Checkout.com 28 个 ACS 处理器体、Unzer 4 个 `apiKey` 读点、将旁路 GraphQL 族接入真实店铺流程、反爬求解层、DOM/HTTP3、C7c/C8），**④ UI 绑定继续冻结，请勿提前转做 UI**。
>
> **最新实时状态与权威路线请优先以 `docs/HANDOFF.md` 顶部、`docs/METRICS.md` 与 `docs/REMAINING_REPLICATION_ROADMAP.md` 为准。**

> 这份文件保留 R1381 的操作经验与排坑记录（§4–§6、§8 仍具参考价值）；一切数字以**当前仓库与工具输出**为准，出现分歧时以命令输出为准。

---

## 0. 一句话现状（R1382 纠偏版）

- **GraphQL 文本声明 65 / 65，但真实流程接线未收口** —— 跑 `python analysis/operation_gap.py` 查看**三层拆解**（文本声明 / 生产文件调用 / 非旁路可达），不得把“文本声明 65/65”读成“结账流程已完整复刻”。
- **①–③ 静态议程尚未结案**：Phase 1–2 的核心组件与部分店铺/支付能力已真实落地，但站点占位（Farfetch/Saucony/Shopify Billing）、反爬求解（除 Kasada 外均未真接通）、Checkout.com 28 个 ACS 处理器体、Unzer `apiKey` 读取点与长尾异步状态机均待继续推进。
- **④ UI 绑定（`replica/docs/BINDING_BACKLOG.md`）保持冻结**，须严格遵守 `AGENTS.md §2.5`（YG R757 优先级铁律）。

**基线数字**：请直接查看唯一事实源 `docs/METRICS.md`（R1382 刷新版），本文不再硬编码旧快照数字。

---

## 1. 必读（按顺序，别跳）

| 顺序 | 文件 | 为什么读 |
|---|---|---|
| 1 | `AGENTS.md`（仓库根） | 硬规矩：取件优先级、证据规则、编码纪律、生产代码红线、§2.7/2.7b/2.7c/§4.5 |
| 2 | `docs/GOAL.md` | 目标原文、每轮五步循环、完成判据 a–f |
| 3 | `docs/OPEN_ITEMS.md` | **残余项的权威清单**：每条写明缺什么、拿到后怎么验、验完落哪个类 |
| 4 | `docs/METRICS.md` | 唯一事实源（生成物，带时间戳）。**任何文档里的数字都要等于它** |
| 5 | `replica/docs/VERDICT.md` 末 6 节 | 最近 6 轮的第一人称记录：**包括我犯的 5 个错与改正过程** |
| 6 | `docs/BLOCKERS.md` | IDA 反复死亡的处置配方 + 模态框点击顺序 |

## 2. 按需读（做对应工作时才读）

| 工作 | 读 |
|---|---|
| 改站点流程 | `replica/docs/CORE_COVERAGE.md`、`docs/GRAPHQL_DOCUMENTS.md`、`docs/UNATTRIBUTED_OPERATIONS.md` |
| 改支付 | `docs/PAYMENT_CHALLENGES.md`、`docs/PAYPAL_ENDPOINTS_FROM_IMAGE.md` |
| 做 UI 绑定（④，已解冻） | `replica/docs/BINDING_BACKLOG.md` |
| 对齐声明/判据 | `docs/PARITY_CLAIMS.md`（**机器读的表格，见 §6 第 5 坑**） |
| 字符串池 | `docs/C8_STRING_CLASSES.md`、`replica/docs/VENDOR_COVERAGE.md` |
| 长度/函数量 | `docs/MODULE_FUNCTION_CENSUS.md`、`docs/PARITY.md` |

## 3. 已知陈旧、不要当事实源

- `docs/PROGRESS_AND_GAP.md`（停在 R1300）、`docs/REMAINING_REPLICATION_ROADMAP.md` 的路线 A 清单
  （①已完成、②的 C8 已在 R1380 补上）。
- `docs/HANDOFF.md` 的滚动指针是**每轮追加**的，可作为流水，但**不是当前数字**。
- 任何写在文档里的硬编码数字：以 `docs/METRICS.md` 与上表命令为准。

---

## 4. 每轮怎么干（实操版五步，直接从本会话提炼）

1. **取件**：从 `docs/OPEN_ITEMS.md` 或 §7 的队列取**一条**，先 `git status --short` 确认树干净。
2. **查有没有现成的**：`cd replica && python tools/where_is.py <名字>`。
   `implementation` 组里有，就**先读那个文件**再决定写不写（这条救过我多次）。
3. **取证**（顺序固定，任一步能定案就停）：
   `analysis/ida.py str <名>` → `analysis/disp32_scan_any.py <obj_va>`（**两种地址形式都要试**）→
   `analysis/site_to_func.py <site>` → `analysis/dump_dec.py <func>` + `analysis/nates_at.py`（实际名为 `names_at.py`）。
   **无 IDA 时的降级**：`python analysis/pe_read_direct.py str|refs|func <va>`（见 §5）。
4. **落码**：一个族一个类；`snapshot.py` 先快照；**整块锚点替换，禁按行号手术**；
   新方法用 `analysis/insert_into_class.py`（括号配对），**不要用 `rfind('}')`**。
5. **验证 + 记账**：
   ```
   $env:PATH='D:\tools\dotnet8;'+$env:PATH; $env:DOTNET_ROOT='D:\tools\dotnet8'
   dotnet test --filter "FullyQualifiedName~<相关类>" -m:1 --nologo
   python analysis/operation_gap.py ; python analysis/orphan_documents.py
   dotnet publish src\Cybersole.Ui\Cybersole.Ui.csproj -c Release -r win-x64 -p:PublishAot=true \
       -p:UseSharedCompilation=false -m:1 -o .publish-aot-new   # 换目录后跑 artifact_freshness.py
   python tools\mutation-check.py ; python tools\metrics_report.py
   ```
   然后往 `replica/docs/VERDICT.md` 追加**五要素**（改了什么 / 验证命令与输出 / 数字变化 / 证据等级 / 还剩什么），
   往 `docs/HANDOFF.md` 追加指针，提交（`git -c user.name=dsh -c user.email=dsh@local commit`）。

---

## 5. 工具：本会话新增的三个（重要）

| 工具 | 用途 | 为什么有它 |
|---|---|---|
| `analysis/pe_read_direct.py` | `str` 读冻结字符串（`[MethodTable][Length][UTF-16]`，`chars_va-12`）、`refs` 扫 rip-relative 引用、`func` 用 `.pdata` 映射函数起点 | **IDA 在本会话死了 5 次**，每次都死在 publish/变异之后（内存最紧时）。这三问不需要反汇编器 |
| `analysis/c8_string_class_compare.py` | 字符串池四类对照（locale 键 / URL / 错误消息 / dependency），`--write-doc` 生成 `docs/C8_STRING_CLASSES.md` | C8 一直是 `unknown`，理由是"没有工具能做" |
| `analysis/insert_into_class.py` | `class_body_end()` + `insert_before_class_end()`，括号配对并跳过字符串/注释 | `rfind('}')` 是文件最后一个括号，**本项目为它付过三次代价** |

**IDA 起来的标准动作**（`docs/BLOCKERS.md` 有全文）：
`powershell -File D:\projects\vm2api\.dsh\scripts\ida-mcp-doctor.ps1 -Path target\Cybersole.exe`
→ 依次点掉 **加载现有** → **Proceed with unpacked base** → **Repair** → **确定**（inconsistencies）。
**点击要用 `element_token` 的 UIA Invoke**（像素点击会报 `background_unavailable` / `foreground_unavailable`），
**每点一次窗口 id 都会变**。终判据：`python analysis/ida.py health` → `{"status":"ok", ..., "hexrays_ready":true}`。

---

## 6. 我在本会话犯的 5 个错（**不要继承**）

1. **把截断的搜索当成"不存在"** —— `ida.py str X --limit 8` 先返回 8 个 PascalCase 闭包名就停了，
   我据此宣布 `getShippingMethods` 没有独立操作名串；**它就在 `0x14703FA94`**。
   → **反向结论要么不截断，要么换地址直查。**
2. **把 `disp32` 命中当成引用** —— 命中只是字节图案；**只有当那个函数的字面量表里出现这个名字，才算引用**。
   我因此错误地宣称三个 `AddressInput` 字段"有代码引用"。
3. **把字符串表当成构造点** —— 字符串表说"存在什么"，构造点说"用了什么"。
   `AddressInput` 真正的字段是 `line1`/`line2`/`city`（构造点 `0x140AD5B10`），不是我猜的 `addressLine1/2`/`locality`。
4. **读错自己工具的输出三轮** —— `operation_gap.py` 打两个数（"复刻件声明了多少个"vs"镜像 65 个里带了几个"），
   我读错了。**现在工具固定打印 `carried: N of M (absent K)`**；看到两个数时先问哪个回答"覆盖率"。
5. **改 `docs/PARITY_CLAIMS.md` 的表格时给成四格** —— 表头六列，`check_claims.py` 只收 `>= 6` 格，
   行被丢弃 → `claim rows: 21` 与独立计数 22 不符，守卫立刻红。
   → **那份表格是机器读的接口，不是散文。先看消费者怎么读，再改生产者怎么写。**

另外两条**产品红线**（AGENTS §4.5 的推论）：
- **只被测试调用的类会被 AOT 裁掉**（本会话两次：`PaycodeDocument`、`PayPalBrowserSurface` 第一版）。
  证据是**产物尺寸一字未变 + 字面量 0 命中**；接线后才 +6,656/+11,776 字节。
- **字面量缺席不证明任何事**（§4.5）。可用的正向证据只有：**尺寸增长**、**可检出的其他串（如消息串）**、**行为测试**。

---

## 7. 残余队列（R1382 纠偏：按 ①→②→③ 推进，④ 保持冻结）

### ① 站点流程与支付深化（优先级 ①②，本机可做）
- Checkout.com `0x1408a34f0` 下 28 个发卡行 ACS 处理器方法体、Unzer 4 个 `apiKey` 读取点（`sub_14094DEB0` 等）、Komoju `formUrl`；
- 将已落地的 GraphQL 操作家族真正接入对应店铺流程（消除 `operation_gap.py` 检出的零外部调用与无人写入 `Session.Vars` 旁路）；
- 异步名缺失长尾：以 `docs/ASYNC_TAIL.md` 与修正后的 `python analysis/classify_payment_tail.py`（基于缺失集而非全量 243）为准。

### ② 反爬求解与传输/DOM 层（优先级 ②③，本机可做）
- 当前运行时仅 Kasada 接通求解；Cloudflare/DataDome 默认回调为空，Akamai/PerimeterX/Queue-it/BotDeflector/Vercel 未接入 `SolveDetectedWallAsync`（见 `replica/docs/VENDOR_COVERAGE.md`）；
- `AngleSharp` DOM 解析对位与 HTTP/3（`chrome_150`）、`C7c` 报文探针与 `C8` 分类去噪。

### ③ 会话值与外部阻塞（运行期才能拿到，未获条件不编造）
`x-paypal-internal-euat`、`paypal-client-metadata-id`、storefront access token、Cybersource/AO/themeapis 商家端点、`/connect/app`（Farfetch 7 路由）与 `DotNetBrowser` 选型。

### ④ UI 绑定（继续冻结）
`AGENTS.md §2.5`（YG R757）要求 ①–③ 核心项结案或全卡外部条件后才做 ④；**当前未满足解冻条件**，`replica/docs/BINDING_BACKLOG.md` 继续延后。

---

## 8. 明确不要做

- 不要新建 `*Gaps` / `*Wiring` / `*Witness` / `*Coverage` 之类台账类进 `replica/src/`（AGENTS 产品红线）；
  考据一律归 `docs/` 或 `analysis/`。
- 不要把**镜像里的凭据**抄进源码（本会话排除过 storefront token `e927ea99…`，并验证两编码皆无）。
- 不要给测试**写会真的发出去的请求**（`https://payments.braintree-api.com/…` 这类公网端点）——
  本会话差点犯一次（R1352 的 DNS 22 秒、R1360 的 Braintree 端点）。
- 不要写 `%APPDATA%\Cybersole`；日志落 `$env:TEMP`；不要提交 `replica/tools/__pycache__`、
  `.mutation-backup`、`.snapshots`；**禁 `git checkout -- .`**（按字节恢复用 `git show HEAD:<path>`）。

---

## 9. 三分钟自检（接手后先跑这个）

```
cd D:\projects\cyber-reverse
git log --oneline -3
python analysis\operation_gap.py            # 期望: carried: 65 of 65 (absent 0)
python analysis\orphan_documents.py         # 期望: 0
cd replica; python tools\artifact_freshness.py   # 期望: embedded revision 是 HEAD
```

三条都对，说明你接的是干净状态；任一条不对，**先修状态再干活**，不要在半坏的地基上盖楼。
