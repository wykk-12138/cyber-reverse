import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 411 轮：`Utilities` 族照同样的表格收口（12 → 2）

```
before  Utilities: 12 values not present
after   Utilities: 2 values not present
```

补的 18 条覆盖：页面标题/副标题、商店组标题/副标题、`New Group`、空状态、
右键三项 `Clone {0}` / `Delete {0}` / `Edit {0}`、`Delete {0}?`、
模态四件套（新建/编辑标题、`Group Name`、`Enter a group name`、`Stores`、`Add a store`）、两条校验错误。

剩两条 `Delete.MessageFormat` / `Delete.UsedMessageFormat` —— **池子里被截断**（以反斜杠结尾），
写半句等于编，留白并注明。

```
ProfileCsvCopyTests   11 通过 / 0 失败
```

### 这一轮的一句话

> 两轮之间只是把同一套方法用在新的一族上，**第二次就快得多**。

> **方法的复用，比代码的复用更省时间。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('ProfileCsv 已收 39 条（剩 2 条池中截断）/ Utilities 12 条待补',
                'ProfileCsv 39 条、Utilities 18 条已收（各剩 2 条池中截断）')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
