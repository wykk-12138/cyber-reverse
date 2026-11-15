import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R330：Payment 页 —— 用实机**结掉 R77 留下的悬案**

R77 记过一条 caveat：实机静止时只看到 "Auto Open 3DS"，看不到 "Max Open"，
所以怀疑它"只在 Auto Open 3DS 为 Yes 时才出现"，或者是个孤儿标签 —— 当时下拉点不开，问不下去。

这一轮把它问清楚了（在原版上操作，随后恢复原状）：

| 步骤 | 实机所见 |
|---|---|
| 初始 | `Auto Open 3DS [No]`，其下**没有** "Max Open" |
| 点开下拉 → Down → Enter | `Auto Open 3DS [Yes]`，其下**出现** `Max Open [5]` |
| 再切回 No | "Max Open" **消失** |

**结论：`Max Open` 是条件行，依赖 `Auto Open 3DS == Yes`。** 不是孤儿标签。

### 复刻件的改动（R330）

```csharp
var maxOpen = UiKit.Row("Max Open", auto3dsLimit);
maxOpen.IsVisible = s.AutoOpen3DS;
auto3ds.SelectionChanged += (_, _) => maxOpen.IsVisible = auto3ds.SelectedIndex == 1;
```

之前它一直显示（注释里还写着"藏起来会让这个值没有编辑器"）—— 那条理由在"条件是 Yes"成立后就失效了：
**值仍然有编辑器，只是编辑器跟着开关出现。**

### Payment 页其余控件（实机对照，全部一致）

`External Browser`：Browser Path + Configure / Maximum Browser Tabs `10` / Open Link As `Tab`
`Browser Profiles`：Checkout Profiles `Browser default` + Refresh / Profile Assignment `Round robin`

### 测试

`PaymentViewTests`（2 条）：`AutoOpen3DS=false` 时看不到 "Max Open"；`=true` 时看得到。
（走**逻辑树**，因为未挂载的控件没有视觉树；且判断可见性要连祖先一起看 —— 隐藏行仍持有自己的文本块。）
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE: Payment finding recorded')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 330 轮：在实机上把 R77 的悬案**问完了** —— Payment 的 "Max Open" 是条件行

### 一、悬了什么

R77 记过：实机静止只看到 "Auto Open 3DS"，"Max Open" 不在页面上；
当时**下拉点不开**，所以只能写"要么是条件行，要么是孤儿标签"，并把行留着。

### 二、这一轮怎么问的

在原版上：点下拉 → `Down` → `Enter`：

| 状态 | 实机所见 |
|---|---|
| 初始（No） | 只有 `Auto Open 3DS [No]` |
| 切成 Yes | 其下**出现** `Max Open [5]` |
| 切回 No | **消失** |

**问完了：条件行，依赖 `Auto Open 3DS == Yes`。** 随后已把原版恢复为 No。

### 三、复刻件跟着改

`maxOpen.IsVisible = s.AutoOpen3DS;` + 切换时同步。
R195 当时留行的理由（"藏起来会让这个值没有编辑器"）在条件成立后**失效** ——
值仍有编辑器，只是编辑器跟着开关出现。

### 四、两个测试上的坑（都填了）

1. 未挂载的控件**没有视觉树** → `GetVisualDescendants()` 返回空；改用**逻辑树**；
2. 隐藏的行**仍持有自己的文本块**（`TextBlock.IsVisible` 仍为 true）→ 判断可见性必须**连祖先一起看**。

### 五、验证

```
PaymentViewTests            2 通过
完整套件                    1480 通过 / 0 失败 / 2 跳过
```

### 六、这一轮的一句话

> R77 那条注释里写着"下拉点不开，所以问不下去" —— 今天用键盘把它点开了。

> **当年挡住的不是能力，是工具；工具换了，悬案就该重开。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')
