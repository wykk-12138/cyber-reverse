import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 316 轮：SmartActions 行家族的设计稿（4 件一起设计），不编译

### 一、为什么四件一起设计

它们在同一命名空间、成员互相咬合：

| 类型 | 成员 |
|---|---|
| `FilterRow` | `Filter`, `Inputs`, `IsFirst`, `Passed`, `Title`, `ValueText` |
| `ActionRow` | `Action`, `IsFirst`, `Result`, `Tooltip` |
| `InputRow` | `Matched`, `Text` |
| `FilterInputEntry` | `Filter`, `Input`, `IsFirst` |

只做其中一件会让另外三件继续挂着，而它们的形状**必须一起定**才自洽。

### 二、设计里的两个关键决定

1. **`FilterRow.Passed` 由构造方传入**，不在行里调 `Filter.Passes(evt)` ——
   行是渲染用的，判定属于引擎；传进来，行就永远可测、不依赖引擎运行。
2. **`InputRow` / `FilterInputEntry` 只做类型 + 测试，不接页面** ——
   目前没有证据说原版哪里显示"匹配列表"，按 R265 的规矩不硬接。

### 三、预测写清楚（并且写明"以实测为准"）

`FilterRow` 3 + `ActionRow` 2 + `InputRow` 1 + `FilterInputEntry` 1 = 7 条，
但其中 `Title`/`Inputs`/`Action`/`Result`/`Text`/`Filter`/`Input` **本来就不在缺口清单里**，
所以实测应为 **26 → 19**。附一句：**如果不是 19，先找差异再改 ceiling。**

### 四、这一轮没有编译

可用内存 5.51 GB。

### 五、这一轮的一句话

> 前三轮我做的都是"一件设计稿 → 一件落地"，这轮第一次**四件一起设计** —— 因为它们的成员互相引用。

> **拆开做省的是这一轮的成本，合起来设计省的是三轮回炉。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 316 轮（SmartActions 行家族 4 件一起设计：`docs/CONTROL_DESIGN_FilterRow.md`；未编译）。

---

## 下一个可执行任务（4 件一次落地）

`docs/CONTROL_DESIGN_FilterRow.md`：

| 类型 | 关键成员 | 接不接页面 |
|---|---|---|
| `FilterRow` | `IsFirst` / `Passed` / `ValueText` / `Title` / `Inputs` | `SmartActionsCreator.FilterRows` |
| `ActionRow` | `IsFirst` / `Tooltip` / `Result` | `SmartActionsCreator.ActionRows` |
| `InputRow` | `Matched` / `Text` | **不接**（无页面证据） |
| `FilterInputEntry` | `IsFirst` / `Filter` / `Input` | 经 `FilterRow.Inputs` 间接接上 |

- **`Passed` 由构造方传入**（行不持事件、不依赖引擎）；
- 6 条验收 + `SmartActionRowTests`（纯逻辑）；
- **预测缺口 26 → 19**，实测为准。

## 状态

```
完整套件   1468 通过 / 0 失败 / 2 跳过（R315，--no-build）
缺口       26（real = ceiling）
Commit     42.8 GB / 可用 5.5 GB   ← 低于硬线
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
