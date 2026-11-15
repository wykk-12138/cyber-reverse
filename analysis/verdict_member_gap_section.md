### 方法级对比：UI 层零重叠是架构差别，不是缺口

上一轮比了**类型**，这轮比**成员**（属性/命令/方法）——那才直接对应「函数数量对等」。

### 结果

```
原版有成员的类型: 207
replica 有成员的类型: 113
零重叠: 199
部分重叠: 0
```

**「零重叠 199 个」看着像灾难，但它是一个测量错误。**

### 用 `DataView` 验证

**原版的成员**（从元数据直接读）：

```
Cybersole.Ui.Views.Settings.DataView,Cybersole.DataProviders!Getter
Cybersole.Ui.Views.Settings.DataView,Cybersole.Reset!Getter / !Setter
Cybersole.Ui.Views.Settings.DataView,Cybersole.Export!Getter
Cybersole.Ui.Views.Settings.DataView,Cybersole.ViewBackups!Getter
Cybersole.Ui.Views.Settings.DataView,Cybersole.Backup!Getter
Cybersole.Ui.Views.Settings.DataView,Cybersole.Restore!Getter / !Setter
```

**replica 的成员**：

```
DataView(AppServices)
ExportKinds / BackupIntervals / RetentionTimes
IndexOfInterval / IntervalOf / IndexOfRetention / RetentionOf
```

**零重叠是真的。功能却一个不少。**

### 原因：MVVM 与 code-behind

原版是 MVVM：

```csharp
public ICommand Reset { get; set; }      // 绑定到一个 Button
```

replica 是 code-behind：

```csharp
var reset = UiKit.Button("Reset", async () => { … });
```

**同一件事，一个写成属性，一个写成 lambda。**

**操作清单对照**：

| 原版命令属性 | replica 按钮 | 对上 |
|---|---|---|
| `Export` | `Export` | ✅ |
| `Reset` | `Reset` | ✅ |
| `Backup` | `Backup Now` | ✅ |
| `Restore` | `Restore` | ✅ |
| `ViewBackups` | `View Backups` | ✅ |
| `ViewLogs` | `View Logs` | ✅ |
| `DataProviders` | — | ❌ |

**六个操作全对上，第七个（`DataProviders`）是新的。**

### 所以「函数数量对等」在 UI 层不适用

R125 的对比表说「实现体 872 / 872」。**那个数字是对的，但它数的是 Core / Services / Stores 层**——
那些层的架构两边一致（服务类 + 方法），方法名可以直接比。

**UI 层的架构不同**：

- 原版：`Type` + `ICommand` 属性 + `Avalonia.Xaml` 绑定
- replica：`Type` + 构造时内联的 lambda

**同一个窗口，原版可能只有一个 `Reset` 属性，replica 有一整个方法体。**
数字上 replica 更「多」，行为上完全一致。

> **「函数数量对等」是一个有意义的标准，但只在架构相同的层上有意义。**

### 唯一的新发现：`IDataProvider`

```
Cybersole.Providers.IDataProvider
    Name  !Getter
DataView.DataProviders  !Getter      ← 一个只读集合
```

**上下文**（元数据里的相邻顺序）：

```
DataProviders (Getter)
  → IDataProvider.Name (Getter)
Reset (Getter/Setter)
Export (Getter)
```

**这是 Avalonia 编译绑定生成的元数据**：`DataProviders` 绑到某个列表，`IDataProvider.Name` 是显示文本。

**但整个镜像里没有第二个 `IDataProvider` 实现类名。** 说明：

- 要么实现类被 NativeAOT 裁剪（只留接口）
- 要么它们根本没有反射元数据（不需要绑定的话）

**已知：一个叫 `Data Providers` 的列表存在，每项有 `Name`。**
**未知：这个列表里有什么。**

**证据等级 C。不补。** 按 R90 定的标准，C 级证据不足以改变任何注册或新增任何类——
**凭空造一个 `IDataProvider` 加上几个猜的名字，只会让「对等」这个说法变得更不诚实。**

### 结论

| 层 | 可比的单位 | 状态 |
|---|---|---|
| Core / Services / Stores | 方法名 + 方法体 | 872 / 872 ✅ |
| UI（code-behind vs MVVM） | 操作清单 | 6 / 7 对上，第 7 个证据不足 |

**这轮没有修改代码。** 它的产出是一条边界：**「对等」在哪些层可测、在哪些层不可测。**

### 验证

```
dotnet test      583 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
```

---
