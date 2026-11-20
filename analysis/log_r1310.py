"""R1310 round record: Square's device fingerprint, generated from the image bytes."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1310 轮：Square 的设备指纹——不是手抄，是从镜像字节生成

- **发现**：Casio 那个类的元数据里并排躺着**同一份 JSON 的两份拷贝**——
  `0x143385527` 起 **1124 字节**（首成员 `"user_agent":"__UA__"`，占位符等人替换）与
  `0x1433859A0` 起 **1102 字节**；两者**只差一个成员**（9 个成员逐字相同）。
  旁边就是 `ComponentsV1` / `ComponentsV1SansUa` 两个名字，以及 `SquareSdkVersion` = `1.83.9`、
  `SquareLocationId` = `L0NR598Z0FFW5`、`_cardNonce`、`_ccType`。
- **数值是店主的测试设备，不是用户的**：分辨率 `5120x1440`（可用 `5120x1392`）、时区偏移 `-120`、
  `Win32`、**5 个** PDF 插件、**35 个**字体、`adblock:false`、`touch_support:[10,false,false]`。
  随机化指纹是与镜像不同的主张，所以这里照抄冻结值。
- **不手抄**：新增 `analysis/extract_square_fingerprint.py`（按大括号计数、带字符串字面量感知地切出 JSON）
  与 `analysis/write_square_browser_data.py`（**从字节生成** `SquareBrowserData.cs`）。
  手抄 1124 字节是"复刻件在某一个字体名上与镜像不同而没人发现"的标准成因。
- **只存一份，另一份派生**：`WithoutUserAgent()` = 从模板里删掉 `"user_agent":"__UA__",`（22 字节）。
  测试断言这个派生**恰好**得到 1102 字节、且两份对象的其余 9 个成员逐字相同。
  存两份会让它们漂移；派生才能证明关系。
- **归属写清楚了**：这是 Square **Web Payments SDK** 的 `card.browserData` 载荷，
  **不是** `SquareGateway.TokenizeAsync` 那个服务端 `/v2/card-nonce` 请求体——所以**没有动那个请求**。
  改动它会是在猜"哪一面读这个字段"。

### 五要素

- **改了什么**：新增 `replica/src/Cybersole.Stores/Payments/SquareBrowserData.cs`（生成，95 行）、
  新增 `replica/tests/Cybersole.Tests/SquareBrowserDataTests.cs`（11 条）、
  新增 `analysis/extract_square_fingerprint.py` 与 `analysis/write_square_browser_data.py`；
  NativeAOT 重发布；`docs/METRICS.md` 重生成。
- **验证命令与输出**：`python analysis/extract_square_fingerprint.py` → 两份模板 `1124 / 1102` 字节、
  `10 / 9` 个成员、`only in the with-UA template: ['user_agent']`、`identical members: 9 of 10`；
  `dotnet test --filter SquareBrowserDataTests` → **11/11**（首轮 10/1，红的是 `JArray.ToString()` 多行渲染）；
  `artifact_freshness.py` → `state: current`；`metrics_report.py` → 全部 exit 0；
  `mutation-check.py` → 见本轮 METRICS 变异行。
- **数字变化**：套件 2576 → 见 METRICS 当前值（+11）；产物 `61,259,776` → 见 METRICS「发布产物」行。
- **证据等级**：Observation —— 两份模板的地址、字节数、成员数、逐成员相同性、8 个设备取值、
  三个常量，全部由字节读出并被测试钉住。Inference —— 该指纹属于 SDK 的 `card.browserData`
  （由 `ComponentsV1` / `SquareSdkVersion` / `_cardNonce` 三个名字推定）。Unknown —— 镜像在哪一步把
  它填进请求（未反编译调用点）。
- **还剩什么**：Adyen 的托管面（`<SetAdyenPayment>d__6` / `<SubmitAdyenOrder>d__7` /
  `<GetAdyenPaymentStatus>d__8` / `<HandleAdyenAction>d__10` 与 `RpcSubmitAdyenDetails` + `_rpcAdyenPayId`）；
  Saucony 六个步骤的 API 路径；其余 absent 支付名。
"""

POINTER = """
---

## 第 1310 轮

- **Square 设备指纹**：镜像里并排两份 JSON（1124 / 1102 字节，只差 `user_agent` 一个成员），
  已**从字节生成** `SquareBrowserData.cs`，另一份由 `WithoutUserAgent()` 派生（删 22 字节），
  测试钉住派生关系与 8 个冻结设备取值（5120x1440 / -120 / Win32 / 5 插件 / 35 字体）。
- 归属：这是 **Web Payments SDK 的 `card.browserData`**，不是服务端 `/v2/card-nonce` 请求体，**没有动那个请求**。
- 顺带记一笔：`str.format` 遇上 C# 的花括号会被当成字段，脚本改了两轮才通——生成器里改用 `%` 格式化。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1310 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1310 \u8f6e')
