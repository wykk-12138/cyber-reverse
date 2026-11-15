import io
p = r'D:\projects\cyber-reverse\replica\docs\FLOW_SEQUENCES.md'
t = io.open(p, encoding='utf-8').read()
add = '''
## 十、**关键进展**：镜像里有两种布局，第二种把 John Lewis 完整解出来了（R272）

### 1. 两种布局

| 布局 | 形态 | 例子 |
|---|---|---|
| **A 合并式** | 一行里塞一批 `d__N` + lambda 表 | 69 段 / 320 配对（R269） |
| **B 分行式** | **每个 `d__N` 各占一行**，行地址间隔 ~0x30 | John Lewis、以及另外 38 段 |

上一轮我按 A 的形态去找 John Lewis，找不到 —— 因为它用的是 B。

### 2. B 的判据（可复算）

> 连续若干行，**每行内容恰好是 `<方法名>d__序号`**（行首可能有一个长度字节的残留字符），
> 且**行地址间隔 ≤ 0x60**；凑够 3 行以上即为一段。

`tools/row_groups.py` → `docs/row_groups.json`（39 段 / 159 步）。

### 3. 解出来的 John Lewis（0x3371cea，16 步）

```
22:Start 24:GetHome 25:FindProduct 26:GetProductHtml 27:FindVariant
28:AddToCartPreload 29:EditLine 30:SubmitEmail 31:GetShippingRate 32:SubmitShipping
33:SubmitBilling 34:SubmitOrder 35:CompleteOrder 36:GetCartCsrf 37:GetPayPalOrderId
```

**与 R112 读到的 17 步表对比**：缺 `23`（R112 也发现 20 跳到 23），且这里多了
`31:GetShippingRate / 32:SubmitShipping / 33:SubmitBilling / 34:SubmitOrder / 35:CompleteOrder` ——
**这正是 R112 当年没读到的那几步**，现在从镜像里直接读出来了。

### 4. 意义

B 布局的段**不需要 lambda 互证**，判据简单（相邻行 + 命名形态），所以可以用它把**所有**这类类都解出来。
39 段 / 159 步只是起点 —— 提高"地址间隔"与"最少行数"的容忍度还可以扩。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('FLOW_SEQUENCES.md: layout B documented with the John Lewis result')
