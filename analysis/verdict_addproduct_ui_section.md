### 「Add product」控件接上了

R95 加了 `ExtraProducts` 字段和 round-robin，但 `TaskEditorWindow` 还只有一行 URL。
这轮把控件补上，这条链路完整了。

### 控件

```csharp
Row(2, "More products", extraBlock);
```

`extraBlock` = 动态行容器 + 一个 `+ Add product` 按钮。每行是一对 `TextBox` + `×`：

```csharp
void AddExtraRow(string url = "")
{
    var line = new DockPanel { LastChildFill = true };
    var box = new TextBox { Text = url, Watermark = "https://store.example/products/another" };
    var remove = new Button { Content = "×", Width = 30 };
    remove.Click += (_, _) => { extraHost.Children.Remove(line); _extraBoxes.Remove(box); };

    DockPanel.SetDock(remove, Dock.Right);
    line.Children.Add(remove);
    line.Children.Add(box);

    extraHost.Children.Add(line);
    _extraBoxes.Add(box);
}
```

### 保存时读回

```csharp
// blank rows are dropped rather than kept as empty products: an empty URL would make the
// engine poll "" every other turn
task.ExtraProducts.Clear();
foreach (var box in _extraBoxes)
{
    if (string.IsNullOrWhiteSpace(box.Text)) continue;
    task.ExtraProducts.Add(new Product
    {
        Url = box.Text.Trim(),
        Sizes = task.Product.Sizes.ToList(),
    });
}
```

**新商品继承主商品的尺码列表**——用户填了 `9, 10, 10.5` 再点「加商品」，不该让他重填。

### 三个自己挖的坑

**坑一：`Row()` 按索引定位**

```csharp
void Row(int i, string label, Control input)
{
    Grid.SetRow(l, i); Grid.SetColumn(l, 0);
    ...
}
```

插入 N 行会**把下面所有行重编号**。所以动态行放在一个 `StackPanel` 里，只占一个 Grid 行。

**坑二：`RowDefinitions` 数量**

改完之后有 15 行（0–14），但 `RowDefinitions` 还是 11 个 `Auto`。**多了的行会重叠**。
改成 15 个。

**坑三：`extraBoxes` 是局部变量**

`Save()` 在另一个方法里，看不到它。改成字段 `_extraBoxes`。

### 验证

```
dotnet test (快速)   545 通过 / 0 失败 / 2 跳过
release build        成功
store modules        PASS 61 registered
verify.ps1           VERDICT: all checks passed
```

**注意：这轮没加新测试。** 控件本身没有可断言的逻辑——`AddExtraRow` 是 UI 操作，
`Save()` 的读回逻辑和 R95 的 `ExtraProducts` 测试重叠。

**要真验它，得在跑起来的窗口里点「+ Add product」再保存。那是下一轮的事。**

---
