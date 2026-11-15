import io
p = r'D:\projects\cyber-reverse\replica\docs\FLOW_SEQUENCES.md'
t = io.open(p, encoding='utf-8').read()
add = '''
## 八、又两条路被排除（R271）

### 1. 段内**方法名里从不出现商店名**（0 / 69）

扫了 20 个商店名（Nike / Popmart / Shopify / Footlocker / Demandware / Magento / Goat / Scheels /
HBX / Casio / Farfetch / Warhammer / Supreme / Adidas / Yeezy / Snkrs / Amazon / Target / Walmart），
**任何一段的方法名里都没有它们** —— 方法名是纯动作名（`AddToCart`、`SubmitOrder`），不带品牌。

### 2. 想用"复刻件自己的商店模块"生成指纹 —— 也走不通

复刻件的商店模块**不是一个模块一个文件**（`src/Cybersole.Http/Stores/` 下只有一个
`Stores.Abstractions.cs`，模块是数据驱动的），所以"每个模块的独有方法"这个思路没有对象可切。

### 3. 一个有用的统计

```
段内方法名总数 216    只出现在一段里的 172（80%）
```

**80% 的方法是"某一段独有"的** —— 这意味着指纹法**理论上限很高**，
真正的瓶颈不是"名字不够独特"，而是**我不知道哪个独特名字属于哪家店**。

## 九、所以段→商店这条线的真实边界

| 路 | 结果 |
|---|---|
| 通用动作名指纹 | 27 段命中但不可判 |
| 独有动作名指纹（人工列的 4 组） | 9 段绑上 |
| 方法名含商店名 | **0** |
| 段邻近字面量含商店名 | **0** |
| 复刻件模块独有方法 | 无对象可切 |
| John Lewis 锚点 | 未做（唯一剩下的路） |

**结论**：段→商店**只能靠外部知识**（我知道 `Get6Js` 是 Nike 的、`GetLotteryForm` 是 Popmart 的），
镜像是**不会自己说的**。这条线到此为止，除非用 John Lewis 段把锚点扩出来。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('FLOW_SEQUENCES.md: two more routes excluded, with the boundary stated')
