import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 398 轮：新工具找出 21 处"近似错误"，但我**一处都没改**

### 一、`tools/locale_near_miss.py`

它不找"缺"，找**"几乎对但不等"**：拿 locale 原文与复刻件里的字符串做相似度匹配，≥0.75 且不相等就报出来。

```
Settings: 179 locale values, 21 near-matches (ratio >= .75) that are NOT equal
```

抽样：

| 相似度 | 键 | locale | 复刻件 |
|---|---|---|---|
| 1.00 | `Settings.Data.ViewLogs` | `View Logs` | `View logs` |
| 0.84 | `Settings.CustomSizes.AddButton` | `Add Size` | `Add Size(s)` |
| 0.76 | `Settings.CloudflareSolvers.EmptySubtitle` | `Add a Cloudflare provider to get started` | `Add some proxies to get started` |
| 0.96 | `Settings.CustomSizes.CountOne` | `1 Custom Size` | `Custom Size` |
| 0.78 | `Settings.Google.NoProxy` | `No proxy` | `Move proxy` |

### 二、我先改了两条，然后**全撤回**

改完 `Add Size(s)` → `Add Size`，守卫 `ThePagePrintsTheLiveChromeAndNothingElse` 立刻红了 ——
它的文档注释里记着**实测**的 Chrome：`[Clear Sizes]  [Add Size(s)]`。

- **实测**（那个按钮在那一页上，亲眼看到）vs **locale 键**（叫 `AddButton`，但不知道是哪个按钮）
- 同样的道理，`Settings.Data.ViewLogs` 属于 **Data 页**，而 `View logs` 那处在 **Smart Actions 页**

**两条都撤回。** 这一轮的产出是"21 条待核对清单"，不是 21 处修改。

### 三、为什么这是对的做法

R397 我刚因为"两个空状态混淆"踩过一次；这次同样的坑在前面，我停手了。

```
完整套件   1574 通过 / 0 失败 / 2 跳过
```

### 四、这一轮的一句话

> 工具能指出"这里可能不对"，但**不能告诉我这句话该在哪个界面上**。

> **发现差异 ≠ 有权修改；先确认位置，再动手改字。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 398 轮（新增"近似错误"检测工具；21 条候选，**一处未改**，全部留待位置确认）。

---

## 近似错误队列（`python tools/locale_near_miss.py Settings`）

21 条 locale 与复刻件"几乎相同但不相等"的文案。**未修改**，因为：

- 有些位置已被**实测**固定（`Add Size(s)` 就是实测的 Chrome）；
- 有些 locale 键属于别的页面（`Settings.Data.ViewLogs` vs Smart Actions 页的按钮）。

**处置原则**：先确认这句文案在哪个界面、那个界面是否实测过；两者都有据才改。

## 状态

```
完整套件   1574 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
文案       4 区清零；Settings 区 21 条近似错误待核对
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
