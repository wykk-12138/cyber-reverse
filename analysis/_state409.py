import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 409 轮：把 locale 里**所有**计数文案清完

### 一、清点

locale 里带 `Loaded*/Count*/Selected*/GroupsLoaded*` 的键共 **31 个**。逐个对到复刻件后，
只剩两个没有对应：

| 键 | 原文 | 处置 |
|---|---|---|
| `ProfileCsv.Menu.SelectedCells` | `{0} CELLS SELECTED` | 新增常量 + `SelectedCells(n)`（网格还没有多选，**只有文案**） |
| `Utilities.StoreGroups.CountFormat` | `{0} stores` | 新增常量 + `StoresCount(n)` |

### 二、验证

```
PageCopyTests   21 通过 / 0 失败
locale_text_gap.py ProfileCsv → 0
locale_text_gap.py Utilities  → 0
```

### 三、这一轮的一句话

> 31 个计数文案，29 个本来就对；剩下 2 个补上后，这条线**清零**。

> **一次把一个小类清到底，比同时开五个小类更容易收口。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')
