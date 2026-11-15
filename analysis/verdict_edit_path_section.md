### 编辑路径：先丢数据，再修好

R97 验证了「创建」这条路（新增任务 → 落盘）。这轮验证「编辑」——**发现了一个会丢数据的 bug**。

### 打开已有任务，`ExtraProducts` 是空的

点 `Editor`，窗口标题正确（`Edit task — multi-product test`），字段也正确回填：

```
[5]  Edit value="multi-product test"                    Name      ✅
[6]  Edit value="https://example.com/p/primary"        URL       ✅
[11] Edit value="9, 10"                                 Sizes     ✅
[35] Edit value="2500"                                  Monitor   ✅
[36] Edit value="2500"                                  Retry     ✅
[37] Edit value="10"                                    Timeout   ✅
[39] Edit value="1"                                     Quantity  ✅
[40] ComboBox value="Per Task"                          Mode      ✅
[42] Button "Save"                                      ✅（编辑模式不是 Create）
```

**但 `More products` 区只有 `+ Add product` 一个按钮，那一行 `×` + `Edit` 不存在。**

### 这个 bug 比"显示不对"严重

`Save()` 里是这样的：

```csharp
task.ExtraProducts.Clear();
foreach (var box in _extraBoxes) { ... }
```

**`_extraBoxes` 是空的**（因为没有行），所以 `Clear()` 之后什么都没加回去。

**打开 → 什么都不改 → 保存，`extraProducts` 就从文件里消失了。**

### 原因

`AddExtraRow` 只在两个地方被调用：

```csharp
addExtra.Click += (_, _) => AddExtraRow();   // 点按钮
```

**构造函数里从来没为已有的 `ExtraProducts` 建行。**

### 修

```csharp
// Round 97 could create extra products but not show them again: opening an existing task left
// the "More products" block with only the + button, so the rows were invisible and a Save
// would have written the field back empty.
foreach (var extra in existing.ExtraProducts)
    AddExtraRow(extra.Url ?? string.Empty);
```

### 修的过程中撞到 C# 的一个限制

```
error CS0165: 使用了未赋值的局部变量"extraHost"
```

`AddExtraRow` 是局部函数，它引用 `extraHost`；而 `extraHost` 在构造函数后面才 `var` 出来。
**局部函数不能捕获尚未声明的变量**——即使调用点在声明之后也一样，编译器按声明顺序检查。

`_extraBoxes` 没这个问题是因为它早就是字段。把 `extraHost` 也提成字段：

```csharp
private readonly StackPanel _extraHost = new() { Spacing = 4 };
```

### 修好之后重跑，全对

```
Text "More products"
[7] Button "×"
[8] Edit [value="https://example.com/p/extra-one"]   ← 回填了
[9] Button "+ Add product"
```

改成 `extra-two` 再 `Save`，读文件：

```
name        : multi-product test
primary     : https://example.com/p/primary
extra count : 1
  extra url : https://example.com/p/extra-two  |  sizes ['9', '10']
```

**`extra-two` 落盘。编辑路径闭环。**

### 两条路径现在的状态

| 路径 | 验证方式 | 结果 |
|---|---|---|
| 创建 | UI 填 → Create → 读 `tasks.json` | ✅ R97 |
| 编辑 | UI 打开 → 改 → Save → 读 `tasks.json` | ✅ R98 |

**都用真实窗口点击完成，不是读源码推断。**

### 一个值得记下的模式

「创建」和「编辑」是两条**不对称**的路径：

- 创建：从空表单开始，`_extraBoxes` 本来就是空的 —— **正确**
- 编辑：需要从 `existing` 反向填充，**漏了**

**同一个 `Save()` 代码，在两条路径上行为不同。** 这种不对称只有真的走一遍才能发现。

---
