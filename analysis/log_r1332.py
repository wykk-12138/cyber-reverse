"""R1332 record: the session-key scanner, its calibration, the step it exposed, and an IDA outage."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
BLOCKERS = 'docs/BLOCKERS.md'

ROUND = """
---

## 第 1332 轮：想查"写进会话没人读"，发现会话本身就是日志——但逼出一个"报成功却什么都没发"的步骤

- **工具**：`analysis/unconsumed_session_keys.py`。
- **两次校准，两次被噪音淹没**（都写进脚本头）：
  1. **全仓口径**：350 个键里 224 个"写了没人读"——太假，会话是共享的；
  2. **按类口径**：98 个"本类写本类不读" + **173 个"全仓没人读"**——还是太假，
     因为这些是**遥测键**（`raw`/`product`/`price`/`cart`/`total`/`available`/`lastStatus`/`queue`/`rates`/`stock`/`size`），
     写给 UI 与任务日志的。
- **结论**：**本仓的 `Session.Vars` 同时当状态和事件日志**，所以"写了没人读"多数不是缺陷 ——
  **这条检查不能做成硬性不变量**（与 R1331 的文档孤儿不同，那里的 0 是真 0）。原因写在脚本里，不是我偷懒。
- **它逼出的真缺陷**：`ShopifyFlow.SubmitBillingAsync` 八行 —— 取地址、写两个键、**返回 Success**，
  **中间没有任何请求**。运行日志说账单完成，结账页根本没被碰过，故障要到付款阶段才以"付款失败"冒出来。
- **修报告不编端点**：落 `shopify.billingSubmitted="false"` + 发事件明说"没有发出账单请求，端点未捕获"。
  与 Casio 的 sku 缺口、Warhammer 的安户跳同一种处理：**什么都没做的步骤必须与成功的步骤可区分。**

### 环境故障与修复（本轮额外发生）

- 跑 `metrics_report.py` 时 `核心覆盖（vendor 层）` **exit 2**。`vendor_coverage.py` 自己拒绝写假零：
  `!! controls failed (kpsdk=0, datadome=0) -- IDA is not ready`。**这是工具在对的地方失败。**
- `ida-mcp-doctor.ps1` 报：`PROXY: MISSING`、`PORT 13337: REFUSED`、180 秒无监听。
  用 GUI 依次点掉三个模态框（**Proceed with unpacked base** → **是否修复 .id0 = 是** → **inconsistencies = 确定**），
  `analysis/ida.py health` 恢复 `status: ok`、`hexrays_ready: true`。
- 恢复后重跑：`vendor_coverage.py` → `controls ok=True vendors named=13`；`metrics_report.py` **全部 exit 0**。

### 五要素

- **改了什么**：`ShopifyFlow.cs`（`SubmitBillingAsync` 显性化）；`ShopifyGraphQlTests.cs`（+1 条）；
  新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter ShopifyGraphQlTests` → **10/10**；
  `metrics_report.py` → **全部 exit 0**，套件 **2682/0/0**；
  产物 61,401,600 → **61,402,112**，sha256 `7c0da038…` → `6644662e…`；内嵌 `bbe6af423417`。
- **METRICS 相对上一版的移动，全都有因**：生成时间、套件 +1、产物三行、
  `pdata above boundary replica 15961 → 15962`（新增一个 step）、
  `unknown placeholders 1 → 3`、`vendor: named in image 9 → 13`。
  **后两项是"上一版文件里是旧值"**：vendor 那行在 IDA 掉线期间**拒绝更新**，所以 9 是更早的数字；
  placeholders 的 3 与 R1331 记录一致，说明上一版文件停在更早的一轮。**以生成值为准。**
- **数字变化**：套件 2681 → **2682/0/0**；产物 +512 字节。
- **证据等级**：Observation —— 两次口径的真实计数、遥测键清单、`SubmitBillingAsync` 八行无请求、IDA 三模态框与恢复后的 health。
- **还剩什么**：`AddressInput`；方言条件（blocker）；`CurrencyConversion`(10406) 与 `approveMemberPayment`(5407) 无归宿；
  AO 三个 checkout 体；Saucony 六步路径；Shopify 账单端点。
"""

BLOCK_ENTRY = """
---

## R1332 · IDA 链路掉线的症状与恢复（操作手册补充）

- **症状**：`tools/vendor_coverage.py` 报 `!! controls failed (kpsdk=0, datadome=0) -- IDA is not ready; refusing
  to overwrite docs/VENDOR_COVERAGE.md with false zeros`，`metrics_report.py` 里该行 **exit 2**。
  **这不是指标退化，是环境掉线** —— 而且工具拒绝写假零，这一点是对的。
- **诊断**：`ida-mcp-doctor.ps1` → `PROXY: MISSING` / `PORT 13337: REFUSED` / `TIMEOUT: no listener after 180s`。
- **恢复步骤（本轮实测有效）**：
  1. 用 cua 找 `ida.exe` 窗口，标题是「请确认」/「警告」；
  2. 依次点掉：**Proceed with unpacked base** → **是(Y)（修复 .id0）** → **确定（inconsistencies）**；
  3. `python analysis/ida.py health` 应返回 `status: ok` 且 `hexrays_ready: true`；
  4. 重跑 `vendor_coverage.py`（先跑一次让它 warm，可能第一次报 JSON 解析错，第二次正常）。
- **注意**：DSH 的 `ida` **MCP 代理**报 MISSING 不影响 `analysis/ida.py` —— 后者直连插件 13337。
"""

POINTER = """
---

## 第 1332 轮

- `unconsumed_session_keys.py` 两次口径校准（全仓 224 / 按类 173）**都被遥测键淹没** →
  **`Session.Vars` 同时当状态和日志**，这条检查**不能做成硬不变量**。
- **逼出真缺陷**：`ShopifyFlow.SubmitBillingAsync` 八行无任何请求却返回 Success。已改为记录地址 +
  `shopify.billingSubmitted=false` + 事件明说没发请求。**端点没抓到，不造。**
- **IDA 掉线并修复**：vendor 指标 exit 2（工具拒绝写假零）→ 三个模态框点掉 → health ok →
  `metrics_report.py` 全部 exit 0。步骤记进 BLOCKERS。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1332 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1332 \u8f6e')
append(BLOCKERS, BLOCK_ENTRY, 'R1332 \u00b7 IDA \u94fe\u8def\u6389\u7ebf')
