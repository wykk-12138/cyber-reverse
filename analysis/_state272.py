import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 272 轮（**发现镜像里两种布局**；用分行式解出 John Lewis 完整 16 步，含 R112 当年缺的五步）。

---

## 六条流的新取证通道：**两种布局**

| 布局 | 形态 | 工具/数据 | 规模 |
|---|---|---|---|
| **A 合并式** | 一行含一批 `d__N` + lambda 表 | `tools/flow_dump.py` / `docs/flow_step_sequences.json` | 69 段 / 320 配对 |
| **B 分行式** | **每个 `d__N` 各占一行**，地址间隔 ~0x30 | `tools/row_groups.py` / `docs/row_groups.json` | **39 段 / 159 步** |

**B 的判据**：连续行，每行恰为 `<方法名>d__序号`（行首可有长度字节残留），地址间隔 ≤ 0x60，≥3 行成段。
**不需要 lambda 互证** —— 所以可以批量解，放宽参数还能扩。

### 解出的 John Lewis（`0x3371cea`）

```
22:Start 24:GetHome 25:FindProduct 26:GetProductHtml 27:FindVariant
28:AddToCartPreload 29:EditLine 30:SubmitEmail 31:GetShippingRate 32:SubmitShipping
33:SubmitBilling 34:SubmitOrder 35:CompleteOrder 36:GetCartCsrf 37:GetPayPalOrderId
```

对比 R112（17 步、缺 23）：这里同样缺 23，但**多出 `31 → 35` 那五步** —— 正是 R112 当年读不到的。

## 教训

**判断"这条路走不通"之前，先确认自己试的是不是全部形态。** 上一轮我拿 A 的钥匙去开 B 的锁。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
