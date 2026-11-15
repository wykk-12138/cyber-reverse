import io
p = r'D:\projects\cyber-reverse\replica\docs\FLOW_SEQUENCES.md'
t = io.open(p, encoding='utf-8').read()
old = '''### 一个待复核项（不敢下结论）

`0x03388fd2` 在扫描里报"命中 `StoreFlowSteps.cs` 8 个"，但我随后在 `row_groups_wide.json` 里
**没再定位到这个基址**（可能只存在于保守版 `row_groups.json`，或基址打印格式不同）。
**记下来待复核**，不当成结论用。'''
new = '''### 待复核项 **已复核完毕**（R277）

`0x03388fd2` 之前没在 `row_groups_wide.json` 里找到 —— 因为它是 **A 布局**的段（在
`flow_step_sequences.json` 里），不是 B 布局。内容：

```
11:FindProductFlow  12:GetCheckout  13:GetShippingRate  140:SubmitShipping
150:GetStructureToken  16:CreateTransaction  17:SubmitPayment  18:ProcessPayment
```

命中情况：`structure-token-multi` **8/15**、`structure-token-single` **7/12** ——
**它是 structure-token 家族的第三个片段（子集）**，和那两条共享 `CreateTransaction` /
`GetStructureToken` / `ProcessPayment` 等词汇。所以"两边都命中"不是矛盾，是**同族**。

（顺带印证了 R270 的警告：`140` / `150` 这种大序号是**数字粘连的解析产物**，不是真序号。）'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('open item resolved and recorded')
