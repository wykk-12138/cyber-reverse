# 接手提示词 · R1381 快照（静态议程已结案）

> 这份文件是**给下一位 agent 的指令**，不是进度散文。读完它，你应该能在 15 分钟内知道
> **现在到哪、哪些已结案、下一步只有哪几条路、以及怎么证明你说的每个数字**。
> 一切以**当前仓库与工具输出**为准；本文的数字都标了出处命令，出现分歧时以命令输出为准。

---

## 0. 一句话现状

- **GraphQL 操作覆盖 65 / 65（absent 0）** —— `python analysis/operation_gap.py` 打印
  `carried: 65 of 65 image operations (absent 0)`。
- **静态议程已结案**：端点族（会话 / `api/graphql` / 哈希 / Magento / Cybersource / Braintree /
  themeapis / AO / Saucony 3DS / PayPal 两方言 + 浏览器面）全部落地；
  **两条异步名长尾都已量化**（店铺 30、支付 243），结论一致：**按名不可追**。
- 剩余工作只有两类：**①267 个异步名需按地址逐条反编译**（独立队列，不在 handoff 取件判据内）；
  **②会话值类输入**（`x-paypal-internal-euat`、`paypal-client-metadata-id`、storefront token 等，属运行期）。

**基线数字（2026-11-22 / R1381，全部可复算）**

| 项 | 值 | 出处 |
|---|---|---|
| 操作覆盖 | **65 / 65（absent 0）** | `python analysis/operation_gap.py` |
| 全量套件 | **2866 通过 / 0 失败 / 2 跳过** | `dotnet test --filter "Speed!=Slow" -m:1` |
| 度量套件 | **2849 / 0 / 0，exit 0** | `python tools/metrics_report.py` |
| 变异套件 | **59 fired / 0 decorative / 0 skipped / GREEN** | `python tools/mutation-check.py` |
| 产物 | **62,092,288 字节**，`embedded source revision` = HEAD | `python tools/artifact_freshness.py` |
| 文档常量孤儿 | **0** | `python analysis/orphan_documents.py` |
| 编码扫描 | 65,773 文件 **0 命中** | `python analysis/scan_encoding_scope_r1301.py` |
| claims 审计 | **5 tables / 22 rows** | `python analysis/check_claims.py` |

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

## 7. 残余队列（只有这些，别自己发明）

### ① 267 个异步名：按地址逐条反编译（独立队列）
- 店铺 30 个（R1367 量）：**1 可追（`AddAddress`，且零引用）/ 29 只有 `<Name>d__NN`**。
- 支付 243 个（R1381 量，`python analysis/classify_payment_tail.py`）：
  **6 可追**（`GetPaymentIntent`/`GetSetupIntent`/`GetThreeDsJwtQuery`/`PlaceOrder`/`RefreshToken`/`SendTokenRequestAsync`）
  **/ 237 只有元数据**。数据落 `analysis/.payment_tail.json`。
- **判据**：这一队列**不在 handoff 的取件判据内**（取件是"每轮一条核心能力待办"，而操作与端点族已结案）。
  要做就**单独立账**，且**每个名字是一个独立工作单元**，不要按"一轮几个"估。

### ② 会话值（运行期才能拿到）
`x-paypal-internal-euat`、`paypal-client-metadata-id`、storefront access token、Cybersource/AO/themeapis 的商家端点。
**形状全部已在码里**，缺的只是值 —— **不要编，缺则拒绝并说明缺哪个**。

### ③ ④ UI 绑定（解冻条件已满足）
handoff 规定 ①–③ 结案后才做 ④；**静态 ①–③ 已结案**，所以 `replica/docs/BINDING_BACKLOG.md` 现在可以取件。
`push`/`pull` 走真实数据，不写死。

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
