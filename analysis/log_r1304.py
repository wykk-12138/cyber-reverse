"""R1304 round record for VERDICT.md and HANDOFF.md (UTF-8, append-only)."""
import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1304 轮：Komoju 的「`[1..56]` formUrl 后缀」是空穴，真正的收获是旁边那台卡支付机

- **先证伪**：`0x140d98f60` 全函数 173 行读完，它做的是**构请求体**——
  `{"authenticity_token", "payment_details":{"type":"konbini","email","store","given_name"}}`
  （`0x146F7C7D8` / `0x14710F7E8` / `0x147175AA8` / `0x1470AFB78` / `0x14701AC58` / `0x147164148` / `0x147040B08`
  七个冻结键逐个解出），然后把请求交给发送器，**URL 取自状态机上下文 `*(*(v3+16)+16)`，不是在这里拼的**。
  所以「`[1..56]` 的后缀表达式」这条记录是空穴，已从三份文档里撤掉；复刻件那段 `komoju.formUrl` 兜底
  仍然保留，但理由换成了真理由——目标由调用方决定。
- **顺带纠正归属**：`store` 字段的值来自 `off_1473CFA90(v15, "convenience_store", &v37)`，默认是**空串对象**
  （`off_146A622F8`，`mt=0x144DB6A40 len=0`），命中才取字典里的值。复刻件现在传的是映射后的店名，属 Inference。
- **真正的收获在兄弟函数 `0x140D994D0`**（4,240 字节，五态）。它是一台完整的 Komoju 卡支付机，三步：
  1. **六个冻结 browser 字段**：`browserTZ=-60`(0x146AA3260)、`browserScreenWidth=1707`(0x146ADB0C8)、
     `browserScreenHeight=1067`(0x146AD56C8)、`browserColorDepth=24`(0x146AE23F8)、
     `browserLanguage=en-US`(0x14701BE60)、`browserJavaEnabled=false`(0x147032068)——
     **是镜像写死的常量，不是采集本机环境**。
  2. **授权体** `{browser_info:{六键}, uuid:"", token}` → POST `https://komoju.com/gpayments_offsite/auth`（0x14706F8E0）。
     `uuid` 是**空串对象而不是省略**（`off_146A622F8`）。
  3. **browser-info 结果**：同样六键摊平 → POST `https://degica.as1.gpayments.net/api/v2/brw/info/result?transId=`
     （0x147062828），transId 直接拼在 `=` 后面。
  另有一台卡凭据体 `{type:"credit_card", name, number, month, year, verification_value}`，`month` 走
  `D2` 格式（`0x146BAE580`），`year` 用 `sub_141CFA1A0(v69, len-2)` **取末两位**——这条已解但**没落码**，
  因为它的目标 URL 在被反编译的窗口里没有配对。
- **落码**：新增 `KomojuGateway`（`AuthUrl` / `BrowserInfoResultPrefix` / `BrowserInfoResultUrl` /
  `BrowserInfo` / `AuthBody` / `AuthorizeAsync` / `CompleteActionAsync`），注册进默认表；
  `TokenizeAsync` **明确拒绝**而不是把卡号发到没证据的地方。测试 6 条，含"授权体确实 POST 出去"这条
  （走 `komoju.authUrl` 这条与全文件其他网关一致的会话缝隙，**绝不指向真 komoju.com**）。
- **一处守卫按事实移动**：`UnmatchedGatewaysTests` 的网关数 14 → 15，测试名一并改
  `TheRegistryHasFifteen`，理由写在测试注释里（R1304 新增 Komoju）。

### 五要素

- **改了什么**：`Gateways.cs`（新增 `KomojuGateway`）、`PaymentGateway.cs`（注册）、
  `ShopifyFlow.cs`（撤掉 `[1..56]` 的 Unknown 并写明真 Unknown）、
  新增 `tests/Cybersole.Tests/KomojuGatewayTests.cs`（6 条）、`UnmatchedGatewaysTests`（14→15）、
  三处文档口径纠正、NativeAOT 重发布、`docs/METRICS.md` 重生成。
- **验证命令与输出**：`dotnet test --filter KomojuGatewayTests` → **6/6**；
  `dotnet test --filter "Gateway|Payment|Konbini|Shopify"` → **137/137**（首轮 136/1，红的正是网关计数守卫）；
  `artifact_freshness.py` → `state: current`；`metrics_report.py` → 全部 exit 0；
  `mutation-check.py` → 见本轮 METRICS 变异行。
- **数字变化**（均引 `docs/METRICS.md`）：套件 `2524/0/0` → **`2530/0/0`**（+6）；
  产物 `61,217,280` → **`61,227,008`** 字节；其余见 METRICS 当前值。
- **证据等级**：Observation —— 七个 konbini 键、六个 browser 冻结值、两个 URL 字面量、
  空串对象 `off_146A622F8`、`D2` 格式串、`len-2` 的取尾两位；Unknown —— konbini 请求体的目标 URL、
  卡凭据请求体的目标 URL。
  Inference —— `store` 字段的取值路径（字典命中才用字典值）、token 来自更早的状态。
- **还剩什么**：Komoju 两个请求体的目标 URL；`ToppsVariant` JSON 键名；Unzer 终态集与 `0x14094a870` 谓词；
  ACS 各处理器方法体；33 条店铺长尾 + 77 条支付长尾。
"""

POINTER = """
---

## 第 1304 轮

- 「Komoju `0x140d98f60` `[1..56]` formUrl 后缀」**已撤**：该函数只构 konbini 请求体，URL 取自状态机上下文。
- 新增 `KomojuGateway`：卡面三步（六个冻结 browser 字段 → `gpayments_offsite/auth` → `brw/info/result?transId=`）
  全部落成常量与可测构建器；卡凭据体已解但**未落码**（目标 URL 未配对）。
- 网关注册数 14 → 15（守卫与测试名同步改，理由写在注释里）。
- 见 `replica/docs/VERDICT.md` 第 1304 轮。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1304 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1304 \u8f6e')
