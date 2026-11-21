"""R1344 record: the reachability checker, its calibration, and the one candidate it fixed."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'

ROUND = """
---

## 第 1344 轮：把 R1343 的教训做成检查器——但它**不能**变成硬不变量，而且当场就有反例

- **检查器**：`analysis/unreachable_types.py` —— 每个 public 类型，**别的文件引用了几次**，零次的报出来。
  全仓 **183 / 643**。
- **校准（必须做，否则又是一张假清单）**：183 个里绝大多数是**模型**（`AycdInboxAccount`、`NotificationSound`、
  `SmartActionTriggerLabel`…）—— 它们由 JSON 反序列化、XAML 绑定、框架实例化，**本来就不会有 C# 具名调用**。
  有信息量的是 `Cybersole.Stores` 那一片。
- **当场抓到一个**：`ShopAppProduct`（上一轮刚加的）**只被自己的测试引用**。
- **但反例就在同一份产物里**：源码层面零调用，**产物里 `query ProductDetails` 与 `server.shop.app` 都在**（UTF-16 各 1）。
  所以 **"源码无调用者" ≠ "会被裁"** —— 这与 R1343 那次不同：那次是**差分测量**（加类尺寸不变 + 两编码皆无 → 接线后 +41,984 且命中），
  这次是**静态推断被产物否定**。
  **结论：这张清单是候选，不是判决，不能做成硬不变量。** §4.5 讲的是产物，而产物说这个类型活着。
- **于是做的是决断不是检查**：`ShopAppProduct` 在复刻件的流程里没有消费者，**等运气不是设计**。
  给它一个：`ShopifyFlow.FindProductAsync` 在会话提供 `shopapp.brokerId` 时走 Shop app 查询
  （`server.shop.app`，与本店的 `/products/<handle>.js` 是**两条不同 API**，所以是分支不是替换），
  并把结果落进 `product`/`productId`。缺这些键就**照旧**走门店查询。
- **产物**：`query ProductDetails` 仍命中 1、`shopapp` 命中 **7**；尺寸 61,672,960 → **61,676,032**。
  清单里 `ShopAppProduct` **已消失**（不再是零引用）。

### 五要素

- **改了什么**：`ShopifyFlow.cs`（Shop app 分支）；`tests/ShopifyGraphQlTests.cs`（+2 条，共 12）；
  新增 `analysis/unreachable_types.py`、`analysis/wire_shop_app_product.py`、`analysis/add_shop_app_branch_tests.py`；
  重发布；METRICS 重生成。
- **验证命令与输出**：`ShopifyGraphQlTests` → **12/12**；`unreachable_types.py` → 183/643（`ShopAppProduct` 已不在其中）；
  产物 `query ProductDetails` UTF-16 命中 1、`shopapp` 7；尺寸见上。
- **数字变化**：套件 +2；产物 +3,072 字节。
- **证据等级**：Observation —— 183 个零引用类型、模型占多数、`ShopAppProduct` 的源码零引用**与**产物在场（两者同时为真）。
  Unknown —— 产物为何保留它（静态推断解释不了，**没有编原因**）。
- **还剩什么**：`Stores` 里其余候选（`AdyenPayPalFlow`、`CasioProduct`、`AccountAndAuthFamilies`、`ServiceHosts`…）；
  43 个未覆盖操作；`approveMemberPayment` 两方言；浏览器侧结账面；`/cartApi/checkout` 归属；`AddressInput`；
  方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1344 轮

- `analysis/unreachable_types.py`：public 类型在**别的文件**里零引用 → 全仓 **183/643**，绝大多数是模型（JSON/XAML 驱动）。
  有信息量的是 `Cybersole.Stores` 那片。
- **它不能做成硬不变量**：`ShopAppProduct` 源码零调用，**产物里却在**（`query ProductDetails`、`server.shop.app` 各 UTF-16 命中 1）。
  **"源码无调用者" ≠ "会被裁"** —— 与 R1343 的**差分测量**不是一回事。清单是候选不是判决。
- 决断而非检查：给 `ShopAppProduct` 一个消费者 —— `ShopifyFlow.FindProductAsync` 在有 `shopapp.brokerId` 时走
  `server.shop.app`（与门店 `/products/<handle>.js` 是两条 API，分支不替换），否则照旧。
- 产物：`shopapp` 命中 7，尺寸 61,672,960 → 61,676,032；清单里 `ShopAppProduct` 已消失。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1344 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1344 \u8f6e')
