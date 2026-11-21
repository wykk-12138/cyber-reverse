"""R1340 record: the technique's precondition, and the endpoint pair it did produce."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1340 轮：把"主机引用列表"用在已实现的店上——发现它有个**前提条件**，并顺手钉住一对端点

- **假设**：R1339 用"扫主机字符串的引用列表"一次拿到 Highsnobiety 全店 8 个发送方，那么对 Warhammer/Casio
  也该能列出"我实现的步骤全不全"。
- **实测（Warhammer `https://api.prod.warhammer.com/graphql`，`0x147054A60`）**：
  ```
  对象头 0x147054A60 -> 2 site(s)
  字符地址 0x147054A6C -> 1 site(s)
  唯一函数 0x140E4AE90（133 字节）：
      +8  &off_147054A60  "https://api.prod.warhammer.com/graphql"（38 字符）
      +16 &off_147066CC0  "https://flex.cybersource.com/flex/v2/tokens"（43 字符）
      +24 一个 945 字符的串   +32 一个 1920 字符的串
  ```
  **这是一个静态初始化器**，把端点收进一个共享配置对象，发送方**从参数拿 URL**。所以引用列表给的是**助手**，不是**步骤**。
- **结论（要记住的前提）**：**"扫主机枚举步骤"只在"每个发送方各自内嵌主机"时成立。**
  对把端点集中起来的店，步骤枚举只能靠**操作名**（也就是已有的 GraphQL 文档清单）。
  **这不是失败，是这把钥匙的适用边界 —— 试第二家店才发现的。**
- **顺带拿到的可检验事实**：两个端点属于**同一份配置**，复刻件必须逐字都有 —— 它有
  （`CybersourceFlex.TokensUrl`、`WarhammerFlow.ApiHost`），本轮把这**一对**钉进测试。
  新增 `WarhammerSurface`（`ApiHost` + `GraphQlPath`）作为公开陈述，避免为测试把 flow 的私有常量放开。
- **一个我自己算错的数字**：先按"57 字符"断言，实际是 **38**（`host + /graphql`）。测量值纠正常量 —— 已改并写进注释。

### 五要素

- **改了什么**：`RetailFlows.cs`（+`WarhammerSurface`）；`WarhammerGraphQlTests.cs`（+1 条，共 12）；
  新增 3 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`WarhammerGraphQlTests` → **12/12**；`orphan_documents.py` → 0；
  `disp32_scan_any` 双地址 → **2 / 1** site；`names_at` → 38 / 43 字符的两个端点；
  产物尺寸 61,526,016 字节（两个字符串本就在镜像里，新类只是把它们的长度关系钉住）；内嵌 `a9c9daa0bbbc`。
- **数字变化**：套件 +1。产物尺寸不变（新增的两个常量与既有字面量折叠）。
- **证据等级**：Observation —— 两个站点数、唯一函数、四个字段与两个端点长度、945/1920 两个未定长串。
  Unknown —— 那 945 与 1920 字符的串是什么（**没有猜**）。
- **还剩什么**：Warhammer/Casio 的步骤核对改用**操作名**口径；Highsnobiety 的 payment/billing/shipping/order 四步；
  `/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1340 轮

- **"扫主机枚举步骤"有个前提**：**只在每个发送方各自内嵌主机时成立**（Highsnobiety 是那样）。
  Warhammer 把端点收进一个静态初始化器（`sub_140E4AE90`），发送方从参数拿 URL —— 引用列表给的是**助手**不是**步骤**。
  这类店只能用**操作名**口径枚举。
- 同一份配置对象里带着 **Warhammer GraphQL（38 字符）** 与 **CyberSource Flex（43 字符）** 两个端点 ——
  已新增 `WarhammerSurface` 并在测试里把这对钉住。
- 配置里还有 **945** 与 **1920** 字符的两个串，**是什么不知道，没有猜**。
- 我把长度算错过一次（57 → 实测 38），按测量值改的。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1340 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1340 \u8f6e')
