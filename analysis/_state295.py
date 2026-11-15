import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 295 轮：九个"候选步骤"全部为真 —— 顺带抓到我自己的又一次误判

### 一、先说我上一轮的错误

上一轮我报"复刻件里的 GraphQL 操作名在池子里 **0 命中**"。这一轮重查发现：**是我查法错了** ——
我用"裸名字"去比，而池子里它们是 `<AddToCartGraphQL>d__106` 这种形态。

### 二、正确的结果：9 / 9 全真

```
AddToCartGraphQL            106  d__ ✓
AddToCartPreloadGraphQL     107  d__ ✓
CreateCartGraphql           108  d__ ✓
GetCartAvailabilityGraphql  109  d__ ✓
CompletePayPalPayment       125  d__ ✓
CompletePayPalGuestPayment  126  d__ ✓
CompleteForwardPayment      127  d__ ✓
AddToCartStoreFront         128  d__ ✓
AddToCartPreload            130  d__ ✓
```

而且它们各自标注的"同序号碰撞者"（`CartApiObjectCreate`、`GetUnzerCallback`、`Register`、`SubmitKlaviyoSubscription`…）
**也全部能在池子里找到** —— 说明当年的记录是老实做的。

### 三、加三条测试 `CandidateStepsDigestTests`

1. 9 条候选的 `(名, 序号)` 与记录逐条相同；
2. **它们一个都不得出现在任何 flow 里**（候选 ≠ 步骤）；
3. `Evidence` 里的告示（"ownership unproven / not merged into StoreFlowSteps"）不得被删。

### 四、验证

```
CandidateStepsDigestTests   3 通过 / 0 失败
完整套件                    （见下）
```

### 五、这一轮的一句话

> 我这轮最该记住的不是"9 条全真"，而是**上一轮那个 0 命中是我的错**。

> **同一份数据，查法不同会给出相反结论 —— 所以"未命中"永远要复核一遍再写进结论。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')
