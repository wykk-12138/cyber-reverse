"""R1303 round record for VERDICT.md and HANDOFF.md (UTF-8, append-only)."""
import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1303 轮：`0x1408a34f0` 不是「未 dump 的逐家表单表」，是一张 28 个发卡行 ACS 主机名的分发表

- **发现方式**：`dec` 出来的 435 行里，`switch (*(_DWORD *)(v6 + 8))` 的 case 值是 `0xC`、`0xD`、`0xE` … `0x28`
  ——**那是 .NET 字符串的长度**，比较用的是 `_mm_cmpeq_epi32` 内联常量。Hex-Rays 把它们印成
  `xmmword_145E88A60`，看不出字面量。
- **两条独立证据对上了**（这轮能成立的关键）：
  1. case 值 = 18 个长度（12,13,14,15,16,17,18,20,21,22,24,25,26,30,31,33,35,40）；
  2. 函数里比较的 `off_146xxxxxx` 是冻结字符串对象，逐个 `names_at` 解出来是 **28 个主机名**，
     它们的长度分布**正好**落在这 18 个值上。
  两边独立算，只有两个解码都对才会一致。测试 `TheCaseLengthsAreTheOnesTheDecompilerPrinted` 就是这条交叉验证。
- **表里有什么**：`acs.apata.io`(12)、`acs2.edb.com`(12)、`3ds.soldo.com`(13)、`acs.touch.tech`/`cacs.icard.com`(14)、
  `acs.revolut.com`(15)、`3dsecure.zen.com`/`verify.monzo.com`(16)、`3dsecure.mbank.cz`/`cacs-v2.icard.com`/`secure4.arcot.com`(17)、
  `acs.capitalone.com`(18)、Modirum 四件套（`acs1/acs2 .3ds/.mpts .modirum.com`，20/21）、`acs-challenge.apata.io`(22)、
  bunq 两件套（24/26）、`3dsecure.starlingbank.com`(25)、Enfuce 两件套（30）、`authentication-acs.marqeta.com`(30)、
  `acs-safekey.americanexpress.com`(31)、`idcheck.acs.touchtechpayments.com`(33)、
  `authentication.cardinalcommerce.com`(35)、`verifiedbyvisa.acs.touchtechpayments.com`(40)。
  复刻件此前只认得 `apata` 与 `touchtech` 的零星字面量，**其余 11 个家族一个都没有**。
- **这条链还带出两件事**：函数开头 `sub_140F46600(&off_146AECBA0 /*"3DS"*/, "Starting 3DS: " + host, 0)`
  是一条类别 `3DS` 的日志；`*(_QWORD *)(*(a1[1] + 24) + 40) = &off_146FC83D8` 把传输指纹**临时**换成
  `chrome_131`，函数尾部再把 `a1[3]`/`a1[4]` 里存的原值写回——即"发卡行跳转 = 换一次指纹，跳完还原"。
- **落码**：`AcsHosts`（`Known` 28 条 / `HostOf` 归一化 / `IsKnown` / `ProfileFor` / `Describe`
  / `CaseLengths`），`ThreeDsTransportHelpers.GetRawAsync` 增加可选 `profile` 参数（在 `ApplyHeaders`
  **之前**设，否则会丢掉由头派生出来的 UA/语言），`CheckoutComGateway.ResolveEswThreeDsAsync` 在抓页之前
  emit `Starting 3DS: <host>`（类别 `3DS`）、写 `checkoutcom.acsHost` / `checkoutcom.acsKnown`、
  并让这一跳跑在 `chrome_131`（`TlsProfile.ByName` 已有映射）。
- **没做的**：每个主机对应的处理器**方法体**没解，所以逐家挑战表单字段仍然不编——挑战完成继续接受
  调用方给的 `checkoutcom.challengeForm`。`AcsHosts` 只回答"这一跳是不是镜像认识的"，不回答"镜像会发它什么"。

### 五要素

- **改了什么**：新增 `replica/src/Cybersole.Stores/Payments/AcsHosts.cs` 与
  `replica/tests/Cybersole.Tests/AcsHostsTests.cs`（6 条）；`ThreeDsTransportHelpers.cs`（`profile` 参数）；
  `CheckoutComGateway.cs`（接线 + 文档改写）；三处文档口径纠正；NativeAOT 重发布；`docs/METRICS.md` 重生成。
- **验证命令与输出**：
  `dotnet test --filter AcsHostsTests` → **6/6**；
  `dotnet test --filter "CheckoutCom|AcsHosts|ThreeDs"` → **65/65**；
  `dotnet publish … -o .publish-aot-new` → exit 0；`artifact_freshness.py` → `state: current`；
  `metrics_report.py` → 全部 exit 0；`mutation-check.py` → 见本轮 METRICS 变异行。
- **数字变化**（均引 `docs/METRICS.md`）：套件 `2518/0/0` → **`2524/0/0`**（+6）；产物
  `61,194,240` → **`61,217,280`** 字节；其余见 METRICS 当前值。
- **证据等级**：Observation —— 18 个 case 长度、28 个冻结字符串对象的内容与长度、
  `"Starting 3DS: "`/`"3DS"`/`"chrome_131"` 三个字面量、尾部把 `a1[3]`/`a1[4]` 写回的两条语句。
  Inference —— 每个分支的处理器构造形态一致（context/owner/flag），差别在类型；
  `chrome_131` 的设定与还原构成"临时换指纹"。Unknown —— 处理器方法体、逐家表单字段、`200`/`400` 之外
  是否还有状态分支。
- **还剩什么**：Komoju `formUrl` 后缀；`ToppsVariant` JSON 键名；Unzer `qword_1472c65a0+8` 终态集与
  `0x14094a870` 谓词；ACS 各处理器方法体；以及路线图原有 33 条店铺长尾 + 77 条支付长尾。
"""

POINTER = """
---

## 第 1303 轮

- `0x1408a34f0` 已从「未 dump 的逐家表单表」改判为**28 个发卡行 ACS 主机名的分发表**（18 个长度 case，
  与字面量长度交叉验证一致），落成 `AcsHosts` 并接进 `CheckoutComGateway.ResolveEswThreeDsAsync`
  （emit `Starting 3DS: <host>` + 该跳跑 `chrome_131`）。
- **仍 Unknown**：每个主机对应处理器的方法体——逐家挑战表单字段还在里面，所以挑战完成仍接受调用方字段。
- 见 `replica/docs/VERDICT.md` 第 1303 轮。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1303 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1303 \u8f6e')
