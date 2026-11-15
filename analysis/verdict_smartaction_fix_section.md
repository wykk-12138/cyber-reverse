### 4 个 SmartActions 死按钮修完，白名单从 15 降到 12

R100 把 status-only 按钮扫出 23 个、修了 7 个。这轮修掉 SmartActions 的最后 4 个。

### `TemplateView` 三个按钮

它们原来写的是：

```csharp
UiKit.Button("From scratch", () => _status.Text = "Starting from a blank action."),
UiKit.Button("From template", () => _status.Text = list.SelectedItem is null
    ? "Select a template."
    : "Seeding from " + list.SelectedItem),
UiKit.Button("Blank", () => _status.Text = "Blank template."),
```

**「Seeding from X」这条尤其糟**——它读起来像真的从模板复制了，实际只把名字打进状态栏。

**修**：三个都打开 `SmartActionEditorWindow`。

```csharp
private void OpenEditor()
{
    var owner = TopLevel.GetTopLevel(this) as Window;
    if (owner is null) { _status.Text = "No owner window — cannot open the editor."; return; }

    var editor = new SmartActionEditorWindow(_services);
    editor.Closed += (_, _) => { _services.Config.Save(); };
    _ = editor.ShowDialog(owner);
    _status.Text = "Smart-action editor opened.";
}
```

`TemplateView` 的构造参数 `services` 之前没存成字段，补上 `_services`。

### 一个诚实的缺口

`From template` 和 `Blank` 现在打开的编辑器和 `From scratch` 一样——**空的**。

因为 `SmartAction` 模型里没有模板字段：

```csharp
public string Id / Name / Trigger / Kind / Target / StoreFilter ...   // 没有 IsTemplate
```

**所以「从模板复制」这个动作无处可写。** 在方法注释里写明了这一点，
而不是让它看起来能用。

### `Publish` 改成说明为什么不能

```csharp
UiKit.Button("Publish", () => Status("Templates are not implemented: SmartAction has no "
    + "template flag, so publishing would have nowhere to write.")),
```

### 测试立刻抓出了白名单里的过期条目

改完跑 `DeadButtonTests`：

```
status-only buttons: 12 (known: 15)
  STALE: Views/SmartActions/SmartActionViews.cs:From scratch
  STALE: Views/SmartActions/SmartActionViews.cs:From template
  STALE: Views/SmartActions/SmartActionViews.cs:Blank
```

**`EveryKnownEntryStillExists` 正是为此存在的。** 三个按钮已经变成真的了，白名单还留着它们——
删掉之后：

```
status-only buttons: 12 (known: 12)
live: 12, known: 12
```

**如果只有「没有新的」那一个断言，这三个过期条目会一直留着，
下一次真的新增死按钮时就会藏在里面。**

### 顺带查了 Settings 的 18 个导航按钮

点 `General` 时右侧没变——**差点误判成死按钮**。

看源码：

```csharp
var id = section.Id;
b.Click += (_, _) => Navigate(id);
```

**是真的。** 没变的原因是 `General` 本来就是当前页（`Navigate(initial ?? "general")`）。

改点 `Appearance` 验证：

```
[37] Pane
  Text "Customize scrollbar appearance and sizing"
  [38] Button "Reset Defaults"
  Text "Scrollbar" / "Scrollbar Width" / [39] Slider / [42] Edit value="5"
  Text "Corner Radius"   / [43] Slider / [46] Edit value="2"
  Text "Scrollbar Color" / [47] Edit value="#29293A"
  Text "PREVIEW" / [48] Pane / [49] Button "Save"
```

**内容换了。导航是真的。**

### 一个方法上的教训

**「点了一下没变化」不等于「按钮是死的」。**

R97 的 `Creator` 是真死（源码里只有 `Status(...)`）。
这轮的 `General` 是活的，只是点的是当前页。

**判据不是「有没有可见变化」，是「源码里有没有做事」。** 前者用来发现嫌疑，后者用来定罪。

### 验证

```
dotnet test      547 通过 / 0 失败 / 2 跳过
dead buttons     12 live / 12 known（从 23 降下来）
release build    0 errors
store modules    PASS 61 registered
verify.ps1       VERDICT: all checks passed
```

---
