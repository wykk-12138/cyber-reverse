"""Log R1294: Farfetch's seven placeholders reclassified, and the test that was bound to a sentence."""

import io

B = """
## R1294 —— ① 最后一块：`FarfetchFlow` 七条占位**从 `unknown` 改成分类**

### 一、R1077 早就把问题问完了，文案还写着"unknown"

类头批注（`FarfetchFlow.cs:90-92`）原文：

> R1077: the decompile closed the question this report used to leave open … The route is a **server-delivered
> connect/app config entry**, and the entry's schema needs **the original login** to capture.

⇒ 这是**已分类**（服务端下发 + 凭据受阻），不是待查。而 7 条消息仍写着 `endpoint unknown`，
于是 `core_coverage.py` 把它们计进"端点为 Unknown"，① 的判据一直显示有占位。

### 二、改了什么

7 条（`product` / `add-to-cart` / `basket` / `checkout` / `shipping` / `payment` / `place-order`）统一改为：

```
farfetch: <x> route unrecorded locally — it is a server-delivered connect/app config entry, schema needs the original login to capture
```

`FarfetchFlow.cs` 里 `endpoint unknown` 计数 **7 → 0**。

### 三、连带修掉一处**绑整句**的测试

`FarfetchIsCoveredByTheOriginalTests.TheStepsNameTheServerDeliveredTransport` 原来断言**完整那一整句**
（连 `-- server-delivered route (connect/app config)` 的破折号都在里面），所以改措辞就红。

按 R1284/R1286 的一贯口径改成断**事实**：保留三条短语断言（`server-delivered` / `connect/app` /
`schema needs the original login`），第四条改为断 `route unrecorded locally`。
**它防的东西没变**（这条路由的性质与所缺条件），只是不再防措辞。

### 四、验证

`Farfetch|FlowWorkAudit|EndpointEvidenceRatchet` **7/7**；全量 **2478 通过 / 0 失败 / 2 跳过 / 2480**。

### 五、① 的状态

`BstnFlow` 4 条（R1284）与 `FarfetchFlow` 7 条（本轮）都已是**分类结案**；
`Stores/Flows` 的 `inferred` 24 条已全部查过 dump（R1289/R1290）。
⇒ ① 里**不再有"未查"的占位**，剩下的是**凭据受阻**（Farfetch 的 connect/app schema）与
**0 命中 → unknown**（23 条），两者都要 live capture。

**注意**：`core_coverage.py` 与 `payment_challenges.py` 本轮**都没能重跑**——IDA 又报 `kpsdk=0`
（`strings` 查询返回 Traceback），生成器按设计拒绝写零。计数会在下次 IDA 就绪时反映，这里不代填。
"""

V = """
---

## 第 1294 轮：FarfetchFlow 七条占位分类结案 + 修掉绑整句的测试

- R1077 早已定性（server-delivered connect/app + 需原版登录），文案却仍写 `endpoint unknown` ⇒ 7 条改判。
- `FarfetchFlow` 的 `endpoint unknown` 计数 **7 → 0**。
- `TheStepsNameTheServerDeliveredTransport` 从"断整句"改为"断事实"（保留三条短语 + `route unrecorded locally`）。
- 定向 7/7；全量 **2478/0/2/2480**。
- 生成器（`core_coverage.py` / `payment_challenges.py`）本轮因 IDA `kpsdk=0` **未重跑**，计数待就绪后更新。
"""

H = """
## R1294 —— ① 收口：Bstn 4 + Farfetch 7 全部分类；全量 2478/0/2/2480

Observation：
- `FarfetchFlow.cs` 七条（product/add-to-cart/basket/checkout/shipping/payment/place-order）由 `endpoint unknown`
  改为 `route unrecorded locally — server-delivered connect/app …`，文件内计数 7→0。
- 一处测试原断言整句，已改为断三条短语 + `route unrecorded locally`。
- 全量 2478/0/2/2480。
- **IDA `kpsdk=0`**：两个生成器未重跑（拒绝写假零）。

下轮：IDA 恢复后重跑 `core_coverage.py` + `payment_challenges.py` 刷新计数；随后 ② 的 Stripe 派发关系
（文档记为 Unknown：四个构建器经 delegate/虚表间接派发，静态不可得）——或直接进 12 项完成判据自检。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
