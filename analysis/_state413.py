import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 413 轮：`SmartActions` 族 13 条（→ 0）

```
before  SmartActions: 13 values not present
after   SmartActions: 0
```

补的包括：

```
Smart Actions ({0})            ← 页面标题带计数
New Action                     ← 新建按钮
Search Smart Actions           ← 搜索占位
{0} ({1} more)                 ← 动作列表的折叠摘要
Triggered {0} ({1})            ← 上次触发
Publish {0}                    ← 右键发布
Change Trigger? / Changing the trigger will reset all filters and actions. Are you sure?
Add some smart actions to get started / There are no results matching your search
No Filters / 1 Filter / {0} Filters
```

配 `FiltersCaption(n)`：0 → "No Filters"、1 → "1 Filter"、n → "{0} Filters"。

### 一次编译失败

`FiltersCaption` 里我直接写了 `FiltersNone` / `FiltersOne`（以为它们是常量），
但这一族是**表格键**不是常量 → `CS0103`。改成 `Text("FiltersNone")` 等。

```
TaskCreatorCopyTests / PageCopyTests   29 通过 / 0 失败
```

### 第四族收口

| 族 | 条数 | 剩余 |
|---|---|---|
| `ProfileCsv` | 39 | 2（池中截断） |
| `Utilities` | 18 | 2（池中截断） |
| `TaskCreator` | 19 | 0 |
| **`SmartActions`** | **13** | **0** |

### 这一轮的一句话

> 表格法第 4 次使用；这次唯一的坑是"表格键"和"常量"混用。

> **同一套方法用得越熟，越容易在细节上想当然。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('ProfileCsv 39 / Utilities 18 / TaskCreator 19 条已收（前两族各剩 2 条池中截断）',
                'ProfileCsv 39 / Utilities 18 / TaskCreator 19 / SmartActions 13 条已收（前两族各剩 2 条池中截断）')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
