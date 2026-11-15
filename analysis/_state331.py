import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R331：Tasks 页 —— 实机逐项对照，**没有差异**

实机（5.18.32，Settings → Tasks）读到的结构：

```
[🗂 Group 1 ⌄]  [...]    [🟢0][🔴0][🟣0][🔵0]              [🔍 Search tasks]     0 Tasks  ← 表头右侧
[☐]  Site⇅   Product⇅   Profile⇅   Proxies⇅   Status⇅                          0 Tasks
                            （空态）Nothing to see here / Add some tasks to get started
[Task Creator +]  [Clear Tasks 🗑]      [Start Tasks ▶] [Stop Tasks ■]      [Edit Tasks 🖊] [Captcha Solver ⧉]
```

与复刻件逐项对照（`TaskView.cs` / `TaskGrid.cs`）：

| 实机 | 复刻件 | 结论 |
|---|---|---|
| 分组下拉 `Group 1 ⌄` + 独立 `...` 按钮 | `_groups` ComboBox + `_groupMenuButton` | 一致 |
| 四色药丸 🟢🔴🟣🔵 = 0,0,0,0 | `Pill(Success,"#27AE60")`、`Pill(Failed,"#C0392B")`、`Pill(Declined,"#8E44AD")`、`Pill(Running,"#2980B9")` | 一致（顺序与颜色都对） |
| `Search tasks` | `_search`，占位文案相同 | 一致 |
| 列头 `Site / Product / Profile / Proxies / Status` 各带排序双箭头 | `HeaderButton("Site"/"Product"/"Profile"/"Proxies"/"Status")`，同序 | 一致 |
| 右下 `0 Tasks` | `CountCaption` = `"{0} Tasks"` | 一致 |
| 底部六键 3+3，Start/Stop 居中 | 文档里 R73 已记，代码同构 | 一致 |
| 空态两行 | `EmptyView` 的 headline + 第二行 | 一致 |

**Tasks 页无需改动。** 这一条与设置页一样，是"看出来的"而不是"读出来的"。

### 顺带纠正我自己的一次误判

我先在 `TaskGrid.cs` 里找四色药丸，没找到，差点记成"复刻件缺药丸"。
实际它在 `TaskView.cs:301-304` —— **`TaskGrid` 只画列表，工具条在 `TaskView`**。
又一次印证：**"未命中"先复核查法**（R295/R310 同一条）。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE: Tasks verified')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 331 轮：Tasks 页实机对照 —— **零差异**

### 一、实机读到的结构

```
[Group 1 ⌄] [...]   [🟢0][🔴0][🟣0][🔵0]        [Search tasks]      0 Tasks
[☐] Site⇅ Product⇅ Profile⇅ Proxies⇅ Status⇅                       0 Tasks
[Task Creator +][Clear Tasks 🗑]  [Start Tasks ▶][Stop Tasks ■]  [Edit Tasks 🖊][Captcha Solver ⧉]
```

### 二、逐项对照（全部一致）

| 实机 | 复刻件 |
|---|---|
| 分组下拉 + 独立 `...` | `_groups` + `_groupMenuButton` |
| 四色药丸 绿/红/紫/蓝 | `#27AE60` / `#C0392B` / `#8E44AD` / `#2980B9`（顺序也对） |
| 列头 Site/Product/Profile/Proxies/Status | `HeaderButton(...)` 同序 |
| `0 Tasks` | `CountCaption` = `"{0} Tasks"` |
| 六键 3+3、Start/Stop 居中 | 同构 |
| 空态两行 | `EmptyView` |

**Tasks 页不需要改。**

### 三、我自己的一个误判（当场纠正）

我先在 `TaskGrid.cs` 里找四色药丸，没找到，差点记成"缺药丸"。
**它其实在 `TaskView.cs:301-304`** —— `TaskGrid` 只画列表行，工具条归 `TaskView`。

> 这是 R295（未命中先复核查法）与 R310（`SoundLocation` 其实是 `Path`）之后的**第三次同类自纠**。

### 四、这一轮的一句话

> 两轮 GUI 交叉验证的结论都是"**没有差异**" —— 而这恰恰是有价值的结论：
> 它把"我读代码觉得对"升级成"我在原版上看过"。
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')
