import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 序号扫描找到了名字，但不能证明归属（第 120 轮）

R119 学到：步表跳过某个序号时，去读**同一个类的 lambda 字面量**。
R120 试了更省事的办法 —— 扫全库的 `<Name>d__N`，按序号归堆。**它失败了，原因值得记下来：**

> **序号是「每个类各自编号」的。**

同一个序号 126 上同时挂着三个类的方法：

```
126  CompletePayPalGuestPayment   ← 支付类
126  Register                     ← 账户类
126  SubmitKlaviyoSubscription    ← 营销类
```

所以裸序号**说不出一个名字属于哪个类**。扫描结果只能是**候选**，不能并进 `StoreFlowSteps`。

### 九条候选（三个族）

| 序号 | 名字 | 同序号还有 |
|---|---|---|
| 106 | `AddToCartGraphQL` | `CartApiObjectCreate` |
| 107 | `AddToCartPreloadGraphQL` | `GetUnzerCallback` |
| 108 | `CreateCartGraphql` | `FetchTokensFromBrokerAsync` |
| 109 | `GetCartAvailabilityGraphql` | — |
| 125 | `CompletePayPalPayment` | — |
| 126 | `CompletePayPalGuestPayment` | `Register`、`SubmitKlaviyoSubscription` |
| 127 | `CompleteForwardPayment` | `WriteAttributeTextBlockAsync` |
| 128 | `AddToCartStoreFront` | — |
| 130 | `AddToCartPreload` | `WriteRawWithCharCheckingAsync` |

### 其中两族值得用「字面量法」再查一次

1. **GraphQL 购物车族（106–109）** 与 R101 那 6 个 `persisted?operationName=` 相互印证 ——
   这是 Nike 那条链的购物车半边，而 R96 已证明 replica 完全没有 GraphQL 购物车。
2. **PayPal / forward payment 族（125–127）** 与 R118 那条「某店直接打支付商主机」相互印证。

`CandidateStepTests.NoCandidateWasPromotedToAStep` 断言：
**候选与步表必须互不相交** —— 谁把候选当步用，测试就红。

> 这一轮的价值不在「找到了九个名字」，在**「证明了序号扫描不能用来证明归属」**。
> 否定一种方法，和找到一条证据一样有用 —— 只是它看起来不像进展。
'''

if "## 序号扫描找到了名字" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("candidate section documented")
else:
    print("already present")
