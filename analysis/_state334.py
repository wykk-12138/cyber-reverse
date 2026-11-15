import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R334：Home 页 —— 实机空态与复刻件**有两处不同**（已改）

实机（无数据）与复刻件的差异：

| 项 | 实机 | 复刻件（改前） |
|---|---|---|
| Releases 分页 | **`0 / 0`** | `1 / 1`（`ReleasePages` 用了 `Math.Max(1, …)`） |
| Releases 空态 | `Nothing to see here` + **`There are no upcoming releases`** | 只有前一行，且**整段缺失** |

### 改了什么

1. `ReleasePages` 去掉 `Math.Max(1, …)` —— 没有数据就是 0 页；
2. 新增 `PagerCaption(page, pages)`：`pages <= 0` 时输出 `0 / 0`（否则 `page / pages`）；
3. 新增 `EmptyReleasesBody = "There are no upcoming releases"`，并在卡片为空时渲染两行空态。

### 为什么之前没发现

R73 那次读数**带着数据**（`Palace Skateboards Winter '26 Week 7 / Nov 13`），
分页自然是 `1 / 1`。**空态只有在"没有数据"的账号上才看得到** —— 而这次重启后正好是空库。

> 结论：**同一个小部件有两种状态，只测其中一种等于没测。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 334 轮：Home 页暴露出**两处真差异** —— 都在"空态"里

前四页都是"零差异"，这一页不是。

| 项 | 实机（空库） | 复刻件（改前） |
|---|---|---|
| Releases 分页 | **`0 / 0`** | `1 / 1` |
| Releases 空态 | `Nothing to see here` + **`There are no upcoming releases`** | 只有前一行，第二行**整段缺失** |

### 改动

1. `ReleasePages` 去掉 `Math.Max(1, …)`；
2. `PagerCaption(page, pages)`：`pages <= 0 → "0 / 0"`；
3. `EmptyReleasesBody = "There are no upcoming releases"` + 卡片为空时渲染两行。

### 为什么五轮才撞上

R73 那次读数是**带数据**的（`Palace Skateboards …`），分页自然 `1 / 1`。
**空态只有在空库上才看得到** —— 这次重启后正好是空账号。

> **同一个小部件有两种状态，只测其中一种等于没测。**

### 验证

```
完整套件   1486 通过 / 0 失败 / 2 跳过（21 s）
新增       AnEmptyCarouselReadsZeroOfZeroAndSaysThereAreNoReleases
```
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 334 轮（Home 页空态两处真差异已修：`0 / 0` 分页 + `There are no upcoming releases`）。

---

## 实机核对六页，Home 是第一个查出差异的

| 页 | 结论 |
|---|---|
| Settings / Tasks / Proxies / Accounts / Billing | 零差异 |
| **Home（空库）** | **两处差异已修**：分页 `1 / 1` → **`0 / 0`**；补 `There are no upcoming releases` |

**教训**：R73 的读数带数据（`Palace Skateboards …`），所以分页是 `1 / 1`；
**空态只有空库才看得见**。同一个小部件有两种状态，只测一种等于没测。

## 状态

```
完整套件   1486 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     17.4 GB / 可用 17.8 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
