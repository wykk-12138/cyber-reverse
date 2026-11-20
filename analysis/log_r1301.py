"""R1301 round record: append to VERDICT.md and HANDOFF.md in UTF-8.

Written as a script rather than an editor paste because both files are tens of
thousands of lines and the console renders UTF-8 Chinese as mojibake -- a paste
through it is exactly how the defects this round repaired got created.
"""
import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1301 轮：接手 Phase 1/2 基线；指标管道静默改写非 ASCII，守卫两处盲区补齐

- **先验后接**：`8372d0c` 之上的 Phase 2 不是纸面 —— `MailCodeService`（`ImapMailProvider.cs`）、
  `UnzerGateway`/`CheckoutComGateway`（`Gateways.cs`）、`CardinalThreeDs`、`ClickHouseSink`、
  `HttpDebug`、`RootCertificateStore`、`LegacyJarrayBody` 逐个在 `src/` 里找到。
- **查出一个可信度缺陷**：`metrics_report.py` 收子进程输出用的是
  `text=True, encoding="utf-8", errors="replace"`；子进程是 Python 脚本，stdout 编码跟随控制台代码页
  （本机 cp936），于是 `bind_diff.py` 注释里的一个 `§` 以 GBK 字节到达父进程，被替换成 **两个 U+FFFD 写进
  唯一数字源** `docs/METRICS.md`。一个字符变成两个替换符，就是这条链的指纹（`ef bf bd ef bf bd`
  对 `c2 a7`，HEAD 版本是干净的）。
- 修生成器不修生成物：子进程加 `PYTHONIOENCODING=utf-8` + `PYTHONUTF8=1`，父进程按字节收、严格解码；
  仍解不出就转成 `\\xNN` 写进文件并在本次运行里计为失败（`DECODE_WARNINGS`）。静默替换换成看得见的失败。
- **守卫两处盲区，绿着漏过去**：`SourceEncodingTests` 从 `replica/` 起走 `{src,tests,tools,docs}`，
  扩展名只认 `.cs/.md/.json/.ps1`。所以 **仓库根 `docs/`（含 `METRICS.md`）从未被扫**，
  **任何 `.py` 工具脚本也从未被扫**。两处都补；补完立刻红：`mojibake hits: 6` =
  `../docs/HANDOFF.md:500`、`../docs/METRICS.md:129` ×2、`../docs/KASADA/11-jint-runtime.md:2673` ×3。
- 修掉两处**已在 HEAD 里**的缺陷（不是本轮回归，这正是盲区的代价）：
  `HANDOFF.md`「过去一□直在少报」→「一直在少报」；`11-jint-runtime.md` 表头三连替换符 →「打法」
  （由上方两行的「三种打法：」判定，不靠猜字形）。`METRICS.md` 那处**没有手改** —— 生成物靠修好的管道重生。
- **失败信息会喂回文件**：`METRICS.md` 逐字记录测试输出，旧消息把替换符抄了一遍，于是失败的一轮让下一轮
  因为新原因再失败、永不收敛。命中行现在只报码位（`U+FFFD x2`），不报字符本体。
- **顺带解掉一个 `Unknown` 的归属**：反编译 `0x14094c210`（`UnzerGateway` 注释挂在它上面的 prepare 子路径），
  它落的 15 条头是全站浏览器模板（`sec-ch-ua-platform`/`x-requested-with`/`user-agent`/`accept`/`sec-ch-ua`/
  `content-type`/`sec-ch-ua-mobile`/`sec-fetch-site`/`sec-fetch-mode`/`sec-fetch-dest`/`referer`/
  `accept-encoding: gzip, deflate, br, zstd`/`accept-language: en-US,en;q=0.9`/`cookie`/`priority: u=1, i`），
  另有 `Akamai: 1`（`a2+112`）、`+226 = 1`、`200`/`400` 两条处理器；URL 在调用方 `sub_14095B4E0` 内：
  `https://www.casio.com/{storeCode}/rest/V1/stripe/payments/get_stripe_configuration?_=<tick>`，
  响应键 `apiKey`。⇒ **它不是 Unzer，是 Casio Magento 的 Stripe 配置端点**，与同页 `sub_14095c980` 的
  `/stripe/payments/get_requires_action?orderId=` 同族。复刻件里 `get_stripe_configuration` 与
  `webSdkBootstrap` 都还不存在，落码下轮做。

### 五要素

- **改了什么**：`replica/tools/metrics_report.py`（子进程编码 + 解码告警）、
  `replica/tests/Cybersole.Tests/SourceEncodingTests.cs`（扫描面加 `.py` 与仓库根 `docs/`；命中改报码位）、
  `docs/HANDOFF.md` 与 `docs/KASADA/11-jint-runtime.md` 两处既有编码缺陷、
  `docs/REMAINING_REPLICATION_ROADMAP.md` 的 `Unknown` ① 归属纠正、`docs/METRICS.md` 重生成。
- **验证命令与输出**：
  `python analysis/scan_encoding_scope_r1301.py` → 补面前 `hits: 6`；
  `dotnet test --filter FullyQualifiedName~SourceEncodingTests` → 补面后 **红（6 命中）**、修完 **2/2 通过**；
  `python analysis/probe_doc_bytes_r1301.py` → 每个站点打印磁盘字节与 HEAD 字节（`ef bf bd` vs `c2 a7`）；
  `python tools/metrics_report.py` → 全部 exit 0、套件 **2511 通过 / 0 失败 / 0 跳过**。
- **数字变化**（均引 `docs/METRICS.md`）：套件 `2510/1/0` → **`2511/0/0`**（那 1 条是本轮修面过程中的
  编码用例，不是既有红）；`vendor named in image 11 → 13`（IDA 字符串缓存就绪后真值）；
  `datafiles replica-only 2 → 1`；`only in descriptors 137`、`real gap 0`、`missing 14`、`shape 84/1` 不变。
  `.pdata 187,818 / 67.77%`、`section-mass 61.01%`、`steps 378` 是 Phase 2 提交带来的，**不记在本轮**。
- **证据等级**：
  Observation —— `METRICS.md` 的 `ef bf bd ef bf bd` 对照 HEAD 的 `c2 a7`；两处 doc 缺陷的字节位；
  `0x14094c210` 的 15 条头与 `Akamai: 1`；`/stripe/payments/get_stripe_configuration?_=`（`0x146ab93d0`，
  全库仅 1 处）与 `https://www.casio.com/`（`0x147090DF0`）、`/rest/V1`（`0x146AB7298`）。
  Inference —— `0x14094c210` 是「取 Stripe 配置 → 读 `apiKey`」这一步的处理器（由调用方构造 URL + 委托
  + 响应键三处同时吻合推出）；`200`/`400` 两个处理器是成功/失败分支（只有两个状态码，未逐条验证语义）。
  Unknown —— 那两个处理器的具体语义；`+226 = 1` 这个标志位的作用；`webSdkBootstrap` 在何处被调用。
- **还剩什么**：Stripe 配置端点落成可执行步骤并撤掉 `unzer.prepareUrl` 虚构路径；
  `qword_1472c65a0+8` 终态集合、`0x14094a870` 谓词、Checkout.com 逐家表单表、Komoju 后缀、
  `ToppsVariant` JSON 键名 5 项静态 `Unknown`；以及路线图原有 33 条店铺长尾 + 77 条支付长尾。
"""


def append(path, block):
    text = io.open(path, encoding='utf-8').read()
    if '\u7b2c 1301 \u8f6e' in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND)

HANDOFF_POINTER = """
---

## 第 1301 轮（接手第一轮）

- 当前工作区基线 = `8372d0c` + 一批已采纳的 Phase 1/2 文本改动；本轮新增改动只碰
  `metrics_report.py`、`SourceEncodingTests.cs`、两处 doc 编码缺陷与路线图 `Unknown` ① 的归属纠正。
- **`docs/METRICS.md` 现在可信度更高**：它的生成管道曾把子进程的 GBK 字节按 UTF-8 `errors="replace"` 收，
  一个 `§` 会变成两个 `U+FFFD` 写进这个唯一数字源。管道已改成强制子进程 UTF-8 + 严格解码 + 可见告警。
- **编码守卫扩大了两处**：仓库根 `docs/` 与 `.py` 工具脚本现在都在扫描面内（此前都不在）。
- 详见 `replica/docs/VERDICT.md` 第 1301 轮。
"""

append(HANDOFF, HANDOFF_POINTER)
