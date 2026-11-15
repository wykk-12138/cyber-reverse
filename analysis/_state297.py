import io
p = r'D:\projects\cyber-reverse\replica\docs\ENDPOINT_LEDGER.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## R297：cookie 名也查了 —— 5 个里 2 个有证据，3 个已标推断

| cookie 名 | 证据 | 使用方式 |
|---|---|---|
| 2 个 | 池子里有 | 直接用 |
| `NIKE_COMMERCE_COUNTRY` | **0 命中** | `Cookies.TryGetValue` 可选读，读不到只是不设 `country` 变量 |
| `ffid` | **0 命中** | 只出现在 Farfetch 的文档注释里（"client id issued on first page load"） |
| `sbsd` | **无同名 cookie** | 池子里有 `/sbsd` 与 `_sbsdContext`，所以当年看着像真的 |

三条都已标 `inferred: no image evidence (R297)`，并由 `CookieEvidenceRatchetTests` 看着（2 条断言：条数不增长 + 每条仍在用且仍带标记）。

**性质**：三条都是**可选读**，缺失只会退化、不会崩 —— 所以保留，但标清楚。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('ledger updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 297 轮：cookie 名审计 —— 5 个里 2 个有证据，3 个已标推断

### 一、结果

| cookie | 池子 | 影响 |
|---|---|---|
| `NIKE_COMMERCE_COUNTRY` | **0 命中** | 可选读；读不到只是不设 `country` 变量 |
| `ffid` | **0 命中** | 只在一句文档注释里出现 |
| `sbsd` | 无同名 cookie（池里有 `/sbsd`、`_sbsdContext`） | 写 cookie + 记变量 |

三条都标了 `inferred: no image evidence (R297)`，并新增 `CookieEvidenceRatchetTests`（2 条断言）。

### 二、为什么保留而不是删

三处都是**可选读/可选写**：缺失只会让行为退化，不会崩。删掉反而会改变既有流程的写法。
**账本负责让它们可见。**

### 三、验证

```
CookieEvidenceRatchetTests   2 通过 / 0 失败
完整套件                     见下
```

### 四、这一轮的一句话

> `sbsd` 这条最能说明问题：池子里有 `/sbsd` 和 `_sbsdContext`，**看起来完全合理** —— 但"看起来合理"不是证据。

> **假证据比没证据更危险，因为它会让人停止怀疑。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')
