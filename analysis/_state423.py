import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 423 轮：`MonitorView` 出现 —— `Monitor.*` 的 7 条终于有了宿主（Monitor 7 → 0）

### 一、做法（严格区分"有据"与"无据"）

新类 `src/Cybersole.Ui/Views/Monitor/MonitorView.cs`，只有 **locale 明说的东西**：

| 常量 | 出处 |
|---|---|
| `TabLabel = "Monitor Feed"` | `Monitor.Tab.Feed` |
| `SearchPlaceholder = "Search feed"` | `Monitor.SearchPlaceholder` |
| `EmptyHeadline = "Waiting for monitor entries"` | `Monitor.Empty` |
| `EmptySubtitle = "New products and restocks will appear here"` | `Monitor.Empty.Nothing.Subtitle` |
| `NoResultsTitle = "No results"` | `Monitor.Empty.NoResults.Title` |
| `SizesAvailable` / `SizesNone` + `SizesCaption(n)` | `Monitor.Sizes.Available` / `.None` |

**类的注释里写明**：feed 内部的行形状/列/徽标**未经核实**（没有一次 GUI 会话到过这个页面），
所以只做"搜索框 + 列表 + 空状态"，保持最简。

### 二、三个计数守卫如预期红了

新增 UI 类必然触发（这是设计好的）：

| 守卫 | 变化 |
|---|---|
| `UnreachedUiTypesTests` | 基线加入 `MonitorView`（尚未被构造） |
| `SummaryBlockTests` | 指南 104 → **105** 个 UI 类 |
| `ParityDocTests` | `PARITY.md` 84 = 26 + 58 → **85 = 26 + 59** |

三处都按"数字随事实走"更新，没有一处是靠放松断言过掉的。

### 三、验证

```
三个计数守卫   16 通过 / 0 失败
PageCopyTests  22 通过 / 0 失败（含 MonitorView 的七条与 SizesCaption）
locale_text_gap.py Monitor → 0
```

### 四、这一轮的一句话

> 七条文案等了三轮，等来的是一个"只有文案、没有臆造布局"的页面。

> **补页面和补文案的界线在于：文案有据可查，布局必须有据才做。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('**Monitor 页面未实现（7 条文案无宿主）**', 'Monitor 页已建（7 条文案有宿主，布局待核）')
t2 = t2.replace('UI 类      105 声明 / 29 不可达', 'UI 类      105 声明 / 29 不可达（`MonitorView` 尚未被构造）')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
