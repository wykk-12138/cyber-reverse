import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 305 轮：给"新加的三条守卫"补变异 —— 结果**抓出一条装饰性守卫**

### 一、先给护栏加护栏

R287–R303 新增了三条守卫（流指纹、推断标记、错误目录），但它们从没被 mutation-check 检验过。
按惯例：**没被打破过的守卫不算守卫。** 于是给 `mutation-check.py` 加三条：

| 变异 | 目标守卫 |
|---|---|
| 把 `structure-token-single` 的 `CalculateTaxes` 序号 45 改成 44 | `StoreFlowDigestTests` |
| 去掉 GoatFlow 的 `inferred: no image evidence (R294)` 标记 | `EndpointEvidenceRatchetTests` |
| 把错误目录 `[General] Rate Limit` 改成 `[General] Rate limiting` | `ErrorCatalogDigestTests` |

### 二、结果：两条 fired，**一条是装饰性的**

```
guard fired                                   round 290 -- a flow step loses its ordinal
guard fired                                   round 292 -- an error catalogue title is rewritten
GUARD IS DECORATIVE -- tests stayed green     round 294 -- an unbacked endpoint loses its marker
```

**我自己的新守卫是假的。**

### 三、为什么假：断言比变异松

第一版断言是"**这个文件里**出现过 `inferred: no image evidence`"。
而 `GoatFlow.cs` 里有**两处**标记（R294 与 R298）—— 删掉一处，另一处还在，测试依然绿。

改成"**每一行**用到该路径的代码行都必须带标记"后，又连着抓出三处真实漏标：

```
/api/checkout/v1/basket/{basketId}/payment   (FarfetchFlow)
/v1/buys/{c.Session.CartId}                  (GoatFlow，两处)
/api/beast/                                  (BstnFlow 的错误消息字符串里)
```

补齐后重跑该变异：**`[guard fired]`**。

### 四、这条链上的三个教训

1. **新守卫必须立刻做变异检验** —— 否则它只是"看起来在管"；
2. **断言要落在"行"上，不是"文件"上** —— 文件级的 `Contains` 太容易被别的行满足；
3. **同一个方法会被多处调用** —— 一处标了不等于都用处标了。

### 五、验证

```
EndpointEvidenceRatchetTests   3 通过
完整套件                       1458 通过 / 0 失败 / 2 跳过（22 s）
mutation（27 条全量）          见下一段
```

### 六、这一轮的一句话

> 我给守卫加变异检查，**第一个被它抓出来的守卫就是我自己刚写的那条。**

> **"守卫写完了"和"守卫真的在守"，差别就藏在那一次故意打破里。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended (round text)')
