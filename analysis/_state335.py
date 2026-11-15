import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R335：Home 的 Spend 段 —— 又两处真差异（文案 + 金额格式）

实机点过 `Spend` 段：

| 项 | 实机 | 复刻件（改前） |
|---|---|---|
| 大数字 | **`$0`** | `0`（只有 `(int)Math.Round(spent)`，无货币符号） |
| 数字下的说明 | **`Money Spent`**（大写 S） | 一行代码写 `"Money spent"`，**紧接着另一行又覆盖成 `"Spend"`** |

### 改了什么

1. `SegmentCaption(index)` 成为唯一出处：`0 → "Checkouts"`，`1 → "Money Spent"`；
2. `SpendFigure(decimal)` → `"$" + 四舍五入`；**多位数格式标 `inferred`**（实机只给了空态的 `$0`）；
3. 两处旧赋值（117 行与 298 行）都改成调用这两个方法 —— 之前它们**互相矛盾**。

### 顺带确认

Spend 段的空态文案**与 Checkouts 段相同**：`Nothing to see here` / `You haven't made any checkouts for this period`
（没有改成 "spent"）—— 复刻件复用同一个 `EmptyPeriodBody`，一致。

### 测试

`TheSpendSegmentSaysMoneySpentAndPrintsADollarFigure`：
`SegmentCaption(0) == "Checkouts"`、`SegmentCaption(1) == "Money Spent"`、`SpendFigure(0m) == "$0"`。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 335 轮：Home 的 Spend 段 —— 两处真差异，其中一处是**自相矛盾**

### 一、实机 vs 复刻件

| 项 | 实机 | 复刻件（改前） |
|---|---|---|
| 大数字 | **`$0`** | `0`（无货币符号） |
| 说明文字 | **`Money Spent`** | 117 行写 `"Money spent"`，**298 行又覆盖成 `"Spend"`** |

第二行是最难看的那种缺陷：**同一个标签在两个地方被赋了两个不同的值**，
后赋的赢，所以界面上一直是 `Spend` —— 而两个值都不是实机的 `Money Spent`。

### 二、改法

- `SegmentCaption(index)`：唯一出处，`0 → "Checkouts"`，`1 → "Money Spent"`；
- `SpendFigure(decimal)`：`"$" + 四舍五入`，**多位数格式标 inferred**（实机只给了空态的 `$0`）；
- 两处旧赋值都改成调用，重复与矛盾一并消失。

### 三、顺带确认（一致的）

Spend 段的空态文案与 Checkouts 段**相同**，没有改成 "spent" —— 复刻件复用 `EmptyPeriodBody`，本来就对。

### 四、验证

```
HomePageParityTests   6 通过
完整套件              1487 通过 / 0 失败 / 2 跳过
```

### 五、这一轮的一句话

> 前六页里五页是"零差异"，Home 一页却连续两轮查出问题 —— 因为它有**两种状态**（Checkouts / Spend）
> 和**两种数据状态**（空 / 有）。

> **差异不在显眼处，在"第二个状态"里。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 335 轮（Home 的 Spend 段两处差异已修：`$0` + `Money Spent`；全套 1487 绿）。

---

## Home 页（两种段 × 两种数据状态）查出 4 处差异，全部已修

| 轮次 | 差异 |
|---|---|
| R334 | Releases 分页 `1 / 1` → **`0 / 0`**；补 **`There are no upcoming releases`** |
| R335 | Spend 段大数字 `0` → **`$0`**；说明文字 `Spend` → **`Money Spent`**（并且 117/298 两处赋值互相矛盾，已合并为一处） |

其余五页（Settings / Tasks / Proxies / Accounts / Billing）实机对照**零差异**。

## 状态

```
完整套件   1487 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     22.1 GB / 可用 15.4 GB
```

## 下一步候选

Home 的 Checkout Feed 有数据时的行格式；或 `ChangeChart` 的另外三个图
（`Money spent` / `Spend by store` / `Timeline (last 12h)`）在实机上的标题。

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
