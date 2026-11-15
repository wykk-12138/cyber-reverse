import io
p = r'D:\projects\cyber-reverse\replica\docs\ENDPOINT_LEDGER.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## R298：查询参数名 —— 42 个里 38 有证据，4 个已标推断

| 参数 | 池子 | 备注 |
|---|---|---|
| `json` | 无 `json=` | 验证码驱动用 |
| `orderID` | 只有 `dwfrm_billing_paypal_paypalOrderID`（**含**它，但不是它） | Demandware |
| `siteId` | 只有 `get__siteId`（是 getter 名） | Demandware |
| `productTemplateId` | **0 命中** | GOAT；当前只在文档里作为一句话存在 |

四条都已标 `inferred: no image evidence (R298)`，由 `QueryParamEvidenceRatchetTests` 看着。

**`orderID` / `siteId` 这两条正是最危险的那类**：池子里有"包含它"的长名字，
读起来像有证据，其实那是别的东西的名字。

---

## 三类的合并账（R296–R298）

| 类别 | 总数 | 有证据 | 已标推断 |
|---|---|---|---|
| 端点 | 89 | 67 | **18**（+4 已改名/内部诊断单列） |
| 请求头 | 16 | 13 | 1（改名已修） |
| cookie | 5 | 2 | **3** |
| 查询参数 | 42 | 38 | **4** |

**四类合计：152 个"会发出去的东西"，25 个已标推断。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('ledger updated with params + the merged ledger')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 298 轮：查询参数名 —— 42 个里 38 有证据，4 个已标推断

### 一、结果

| 参数 | 池子情况 |
|---|---|
| `json` | 无 `json=` |
| `orderID` | 只有 `dwfrm_billing_paypal_paypalOrderID` —— **含**它，但不是它 |
| `siteId` | 只有 `get__siteId`（getter 名） |
| `productTemplateId` | **0 命中**（GOAT 只在文档里说过一句） |

### 二、`orderID` / `siteId` 是最危险的那种

池子里有"包含它"的长名字 —— **读起来像有证据，其实是别的东西的名字。**
这正是 R297 那句"假证据比没证据更危险"的又一例。

### 三、四类合并账

| 类别 | 总数 | 有证据 | 已标推断 |
|---|---|---|---|
| 端点 | 89 | 67 | 18 |
| 请求头 | 16 | 13 | 1（改名已修） |
| cookie | 5 | 2 | 3 |
| 查询参数 | 42 | 38 | 4 |

**合计 152 个"会发出去的东西"，25 个已标推断。**

### 四、验证

```
QueryParamEvidenceRatchetTests   2 通过 / 0 失败
完整套件                         见下
```

### 五、这一轮的一句话

> 四轮下来，我把"我可能编过的东西"从**零散怀疑**变成了**152 条有分类、有清单、有棘轮的账**。

> **这才是我能给 YG 的'诚实'：不是保证没编过，是编过的地方都点着灯。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')
