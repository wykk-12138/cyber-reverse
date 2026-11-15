import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 306 轮：把 R305 的教训推到**另外两条守卫**上 —— 又抓出十处漏标

### 一、为什么

R305 证明：**文件级的 `Contains` 会被同一个文件里别的标记行满足**，那条守卫是装饰性的。
而 cookie 与查询参数那两条守卫，写的是**同一个模式**：

```csharp
Assert.Contains("inferred: no image evidence (R297)", text);   // text = 整个文件
```

所以它们大概率也是假的 —— 改成**逐行绑定**（代码行里出现该名字，就必须带标记）。

### 二、改完立刻红了，抓出十处漏标

| 名字 | 文件 | 未标代码行 |
|---|---|---|
| `json=` | `ThirdPartyDrivers.cs` | 1（第二个 `…&json=1` 网址） |
| `ffid` | `FarfetchFlow.cs` | **3**（读 cookie、写 Vars、错误消息） |
| `sbsd` | `StoreFlow.cs` | **3**（写 cookie、错误消息、再写 Vars） |
| `productTemplateId` | `GoatFlow.cs` | **5**（正则、Vars 写、Vars 读、错误消息、查询串） |

**原来只有"一处被标了"，而这个方法在文件里被用了好几次。** 这正是 R305 第 3 条纪律说的情形。

### 三、补齐后再做一次反向验证（证明不是新装饰）

手动删掉 `GoatFlow` 的 `productTemplateId` 标记与 `FarfetchFlow` 的 `ffid` 标记：

```
QueryParamEvidenceRatchetTests.EachOneIsStillUsedAndMarked   [FAIL]
CookieEvidenceRatchetTests.EachOneIsStillUsedAndStillMarked  [FAIL]
```

**两条都响了**，然后恢复标记、全套转绿。

### 四、验证

```
三个证据棘轮   7 通过 / 0 失败
完整套件       1458 通过 / 0 失败 / 2 跳过（21 s）
```

### 五、这一轮的一句话

> 上一轮修好一条假守卫后，我以为"教训已经写下来了"。这一轮才发现：
> **同一个错误模式写在别的文件里，它不会自己消失。**

> **修一条守卫的收益，是把同类守卫全找出来重写一遍。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 306 轮（cookie / 查询参数两条守卫也改成逐行绑定 → 抓出 **10 处漏标**，反向验证两条都会响）。

---

## 三条证据棘轮：全部逐行绑定、都做过反向验证

| 守卫 | 绑定 | 反向验证 |
|---|---|---|
| `EndpointEvidenceRatchetTests` | 每条路径的**每个代码行** | R305 mutation fired |
| `CookieEvidenceRatchetTests` | 每个 cookie 的**每个代码行** | R306 手删标记 → 红 |
| `QueryParamEvidenceRatchetTests` | 每个参数的**每个代码行** | R306 手删标记 → 红 |

R306 因此补标 **10 处**：`json=` 1、`ffid` 3、`sbsd` 3、`productTemplateId` 5（含重叠）。

**规律**：同一个方法在文件里被调用多次时，只标一处等于没标。

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R306）
mutation   27 / 27 fired（R305）
Commit     36.62 GB / 可用 8.85 GB   ← 接近 8 GB 硬线
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
