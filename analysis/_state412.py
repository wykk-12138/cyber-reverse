import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 412 轮：`TaskCreator` 族 19 条（→ 0）

```
before  TaskCreator: 19 values not present
after   TaskCreator: 0
```

这套文案全是**多值占位语**：

```
Select store / Select profile / Select proxy group / Select sizes / Set start time
Multiple stores / Multiple profiles / Multiple proxy groups / Multiple sizes / Multiple start times
Multiple inputs                       ← 监控输入行
Create {0} Tasks / Save {0} Tasks      ← 数量大于一时的按钮
```

正是"三个 tab 合成一个对话框"之后最容易漏的一类：**单值时的提示写了，多值时的提示没写。**

```
TaskCreatorCopyTests / ProfileCsvCopyTests / PageCopyTests   39 通过 / 0 失败
```

### 四轮下来，表格法已覆盖三族

| 族 | 条数 | 剩余 |
|---|---|---|
| `ProfileCsv` | 39 | 2（池中截断） |
| `Utilities` | 18 | 2（池中截断） |
| `TaskCreator` | 19 | **0** |

### 这一轮的一句话

> 同一套方法第三次用，从"想怎么做"变成"照着做"。

> **第一次是发明，第三次是流水线。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('ProfileCsv 39 条、Utilities 18 条已收（各剩 2 条池中截断）',
                'ProfileCsv 39 / Utilities 18 / TaskCreator 19 条已收（前两族各剩 2 条池中截断）')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
