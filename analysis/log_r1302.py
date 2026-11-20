"""R1302 round record for VERDICT.md and HANDOFF.md (UTF-8, append-only)."""
import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1302 轮：把上一轮解开的 `Unknown` 落成可执行步骤，并撤掉它挂在 Unzer 上的那段虚构路径

- **落码的那一步**：`StripeGateway.FetchConfigurationAsync`（+ `StoreConfigUrl` / `StoreConfigHeaders`），
  URL 与调用方 `sub_14095B4E0` 组合的一模一样：`{origin}/{storeCode}/rest/V1/stripe/payments/get_stripe_configuration?_=<tick>`。
  三处冻结字面量各归其位：`0x147090DF0`（`https://www.casio.com/`）、`0x146AB7298`（`/rest/V1`）、
  `0x146AB93D0`（路径，且那个 `?_=` 后面直接拼 tick，不是参数名）。状态两条：`"Preparing payment"`
  （`0x146E49298`，白/`StatusInfo`）与 `"Error preparing payment"`（`0x146D0F904`）。
- **头模板按字面量落，不按形状猜**：`0x14094C210` 在 `a2+80` 装的 15 条里，11 条是字面量（`x-requested-with`、
  `accept`、`content-type`、`sec-ch-ua-mobile`、`sec-fetch-site/mode/dest`、`accept-encoding`、
  `accept-language`、`priority`、`referer`），3 条是构建时算出来的（`user-agent` / `sec-ch-ua` /
  `sec-ch-ua-platform`，复刻件由 TLS profile 承载，不重复写在字典里），1 条是 null（`cookie`，由会话 cookie 罐承载）。
  测试按**键值对**断言而不是按键数，因为"11 条"任何 11 条都能过。
- **没落的那一处，写清楚为什么**：`0x14094C210` 还往 `a2+112`（不是 `a2+80` 那个头字典）写 `Akamai` = `1`，
  并置 `a2+226` 为 1。那个集合到底是 cookie、另一类头，还是请求标志，没有证据；**往 Akamai 前置的站点发一个
  `Akamai` 头是线上猜测，不是复刻**，所以两条都没发，只在注释里留下偏移与"未定"。
- **接线用的是镜像自己的判据**：`sub_140F9E790` 只在"计数器为 0"时返回 `session+120` 那个标志位，
  也就是"还没取到才取"。复刻件用「流声明了这家店（`stripe.storeCode`/`stripe.storeOrigin`）且 publishable key 为空」
  当同一个条件，接在 `AuthorizeAsync` 的入口。这同时修掉一个真缺陷：key 为空时下面的 `form["key"]`
  会以空值发到 Stripe；现在在本地就补上了。
- **删掉的**：`UnzerGateway.PreparePaymentAsync`、`CasioFlow.SubmitPaymentAsync` 里那段 `unzer.prepareUrl` 调用，
  以及 Unzer 文档里挂在 `0x14094c210` 上的那条 `Unknown`。那段路径**从来没有过证据**，它只是为了让
  "Preparing payment" 有地方落而存在。
- **自我限定的边界**：`apiKey` → `stripe.publishableKey` 这一步标 `Inference`，因为该字面量的 4 个引用者
  （`sub_14094DEB0`、`sub_1409F2A60`、`sub_140ECF2B0`、`sub_14117B6C0`）没有一在 `0x14095xxxx` 这条链上；
  注释里写明这是复刻件的选择，后面若找到真正的读取方可以搬。

### 五要素

- **改了什么**：`replica/src/Cybersole.Stores/Payments/Gateways.cs`（新增配置抓取三步 + `AuthorizeAsync` 接线 + 删除
  Unzer prepare）、`replica/src/Cybersole.Stores/Flows/RetailFlows.cs`（撤掉虚构调用）、
  新增 `replica/tests/Cybersole.Tests/StripeStoreConfigTests.cs`（7 条）、
  `docs/REMAINING_REPLICATION_ROADMAP.md` / `docs/HANDOFF_PROMPT_antigravity.md` / `docs/PROGRESS_AND_GAP.md`
  三处措辞纠正、NativeAOT 产物重发布、`docs/METRICS.md` 重生成。
- **验证命令与输出**：
  `dotnet test --filter FullyQualifiedName~StripeStoreConfigTests` → **7/7 通过**（首轮 6/7，URL 归一化漏了 `///` 的情形，
  修 `TrimEnd('/') + "/"` 后过）；
  `dotnet test --filter "Unzer|Stripe|Casio|Gateway"` → **111/111 通过**；
  `dotnet publish -c Release -r win-x64 -p:PublishAot=true -p:UseSharedCompilation=false -m:1 -o .publish-aot-new` → exit 0，
  `python tools/artifact_freshness.py` → `state: current`；
  `python tools/metrics_report.py` → 全部 exit 0、套件 **2518 通过 / 0 失败 / 0 跳过**；
  `python tools/mutation-check.py` → 见本轮 METRICS 的变异行。
- **数字变化**（均引 `docs/METRICS.md`）：套件 `2511/0/0` → **`2518/0/0`**（+7 = 新测试文件）；
  产物 `61,192,704` → **`61,194,240`** 字节；section-mass `31,541,760 → 31,542,784`（`61.01% → 61.02%`）；
  `pdata above boundary replica 15,359 → 15,366`；其余（`real gap 0`、`missing 14`、`shape 84/1`、
  `descriptors 951/215/137`、`flows 18 / steps 378`、`vendor 13`）不变。
- **证据等级**：Observation —— 三个字面量的地址与其内容；15 条头逐条（含 3 条计算项与 1 条 null）；
  两条状态文本；`sub_140F9E790` 的返回表达式。Inference —— 响应 `apiKey` 即后续 `form["key"]`；
  200/400 两个处理器是成功/失败分支。Unknown —— `a2+112` 那个集合的性质（`Akamai`/`1` 因此未发）、
  `a2+226` 标志位作用、`apiKey` 的真正读取方、`webSdkBootstrap` 的调用点。
- **还剩什么**：Unzer 的 `qword_1472c65a0+8` 终态集与 `0x14094a870` 谓词；Checkout.com 逐家 ACS 表单表；
  Komoju `formUrl` 后缀；`ToppsVariant` JSON 键名；路线图原有的 33 条店铺长尾 + 77 条支付长尾。
"""

POINTER = """
---

## 第 1302 轮

- `0x14094c210` 这条 `Unknown` 已从「解出来」推进到「落成代码」：`StripeGateway.FetchConfigurationAsync`，
  在 `AuthorizeAsync` 入口按镜像自己的判据（还没取到才取）接入；`UnzerGateway.PreparePaymentAsync`
  与 `unzer.prepareUrl` 一并删除。
- 头模板按**键值对**落，不按键数；`Akamai`/`1` 与 `a2+226` 因性质未定**未发送**，注释里留着偏移。
- 见 `replica/docs/VERDICT.md` 第 1302 轮，与 `docs/METRICS.md` 的当前值。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1302 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1302 \u8f6e')
