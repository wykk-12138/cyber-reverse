import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 241 轮（价格检查四成员：`Product.MinPrice/MaxPrice` 补字段 + 创建器两个口径；缺口 52 / real 40；全套 1428 绿）。

---

## 缺口 52（real 40）

```
R234 67 → R240 55 → R241 52        noise 12 不计 → real 40
```

**第一次补字段而不是补名字**：`Product.MinPrice` / `MaxPrice`（`decimal?`）—— 原版 `CreateInputModel` 绑定
`PriceCheck + PriceCheckVisible + TogglePriceCheck + MinPrice + MaxPrice` 五个，复刻件只有开关，没有上下界。

**一处坦白**：`PriceCheckVisible` 的语义是我**读出来**的（开关关了上下界就没意义），注释里写明是解释不是证据。

**剩余 real 40**：
- 卡在模型 10：SmartActionsCreator 5（多动作/Inputs/Behaviour）、Attributes.Platform 3（缺每平台能力值）、其余 2
- 需抽控件 5：ComboBoxEdit 2、FilterRow 3
- 零散单成员 ~25

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
