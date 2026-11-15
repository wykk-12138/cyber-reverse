import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 414 轮：`Data` 族 14 条（→ 0），第五族收口

```
before  Data: 14 values not present
after   Data: 0
```

补的覆盖四条流程的**标题 + 正文**：备份成功、导入成功/失败/不支持（JSON 与 JSON/CSV 两种措辞）、
恢复成功/失败、`This will clear all data.`

```
TaskCreatorCopyTests   9 通过 / 0 失败
```

### 五族收口情况

| 族 | 条数 | 剩余 |
|---|---|---|
| `ProfileCsv` | 39 | 2（池中截断） |
| `Utilities` | 18 | 2（池中截断） |
| `TaskCreator` | 19 | 0 |
| `SmartActions` | 13 | 0 |
| **`Data`** | **14** | **0** |

### 这一轮的一句话

> 文案这条线，从"完全没度量"到"五族清零、两族各剩 2 条截断"，用了六轮。

> **度量的价值不在于数字好看，而在于它让"还剩多少"变成一句能回答的话。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('ProfileCsv 39 / Utilities 18 / TaskCreator 19 / SmartActions 13 条已收（前两族各剩 2 条池中截断）',
                'ProfileCsv 39 / Utilities 18 / TaskCreator 19 / SmartActions 13 / Data 14 条已收（前两族各剩 2 条池中截断）；Settings 区仍未清点')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
