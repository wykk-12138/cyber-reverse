### `Data`：五个假按钮 + 一个假的拖拽框

这一页是「导入/导出/备份/日志」的全部入口，也是假实现密度最高的一页。

### 原状

```csharp
var export = UiKit.Button("Export", () => status.Text = $"Exporting: {exportKind.SelectedItem}.");
var reset  = UiKit.Button("Reset",  () => status.Text = "Reset requested - this clears the selected data set.");
```

```csharp
UiKit.Button("View Backups", () => status.Text = backups.ItemCount + " backup(s) on disk.")
UiKit.Button("Restore", () => { status.Text = "Restore from " + backups.SelectedItem; })
UiKit.Button("View Logs", () => status.Text = "Opening the log folder.")
```

**五个按钮，全是状态栏文字。**

`Backup Now` 和 `Save` 是真的——**所以这一页看起来半真半假，用户会以为其它按钮也在工作。**

### 第六个：拖拽框

```csharp
var dropZone = new Border
{
    Child = new TextBlock { Text = "Drag and drop to import, or click to select file" },
};
```

**一个 `Border` 里放了一段 `TextBlock`。没有 `DropHandler`，没有 `PointerPressed`。**

**它长得像可交互控件，说得像可交互控件，但它是张图片。**

### 补 `ConfigurationStore.Restore` / `Export` / `ResetSettings`

`Backup()` 早就有了，但**没有任何读回备份的代码**——备份是单向门。

```csharp
public bool Restore(string path)
{
    if (string.IsNullOrWhiteSpace(path) || !File.Exists(path)) return false;

    BackupDocument? doc;
    try { doc = Json.Deserialize<BackupDocument>(File.ReadAllText(path)); }
    catch { return false; }

    if (doc?.Settings is null) return false;

    // field by field so a partial file leaves the untouched collections alone
    Settings = doc.Settings;
    Accounts = doc.Accounts ?? Accounts;
    TaskGroups = doc.TaskGroups ?? TaskGroups;
    …
    Save();
    return true;
}
```

```csharp
public void Export(string targetPath, string? kind)
{
    object payload = (kind ?? "All data").Trim() switch
    {
        "Tasks" => TaskGroups,
        "Profiles" => BillingGroups,
        "Proxies" => ProxyGroups,
        "Accounts" => Accounts,
        "Settings" => Settings,
        _ => <the same shape a backup uses>,
    };
    File.WriteAllText(targetPath, Json.Serialize(payload));
}
```

**`"All data"` 导出成和备份一样的 `BackupDocument`**——所以导出的文件能被 `Restore` 读回。
一个导出格式如果不能被自己导入，那它只是个日志。

`ResetSettings()` 单独存在，因为 `Settings` 的 setter 是 `private set`，
`DataView` 没有赋值权。

### 修后的五个按钮

**`Export`**——走平台文件选择器：

```csharp
var picked = await sp.SaveFilePickerAsync(new FilePickerSaveOptions
{
    Title = "Export " + kind,
    SuggestedFileName = $"Cybersole {kind} {DateTime.Now:yyyy-MM-dd}.json",
});
services.Config.Export(picked.Path.LocalPath, kind);
status.Text = $"Exported {kind} ({size / 1024} KB).";
```

**`Reset`**——先确认，再清，且**拒绝 `All data`**：

```csharp
default: status.Text = "Pick one data set to reset — All data is too broad."; return;
```

**`"All data"` 能导出，但不能重置。** 一个下拉框同时服务于两个方向，而两个方向的风险不对等——
导错只是多写一个文件，重置错就没有了。

**`Restore`**——先自动备份，再恢复：

```csharp
services.Config.Backup();          // the safety net
if (services.Config.Restore(full))
    status.Text = $"Restored {file}. Your previous state was backed up first.";
```

**`View Backups`**——真的选中最新那条，不只是报数。

**`View Logs`**——真的用 `Process.Start` 打开 `LogsDir`。

### 拖拽框现在真的能拖

```csharp
dropZone.PointerPressed += async (_, _) => { … OpenFilePickerAsync … };
DragDrop.SetAllowDrop(dropZone, true);
dropZone.AddHandler(DragDrop.DropEvent, async (_, e) =>
{
    var dropped = e.Data.GetFiles()?.FirstOrDefault();
    if (dropped is not null) await ImportFromFileAsync(dropped.Path.LocalPath);
});
```

`.cyb` 走 `Restore`；`.json` 明确说「还没接」而不是假装导入了。

### 实测

| 操作 | 结果 |
|---|---|
| `Restore` 选 `Backup 10 Nov 23h19m.cyb` | **`Restored Backup 10 Nov 23h19m.cyb. Your previous state was backed up first.`** |
| 恢复后 `settings.json` | `keybinds=True`、`captchaProviders=11` ✅ |
| 恢复后备份数 | 4 → **5**（自动安全备份生效）✅ |
| `Reset` | 弹 `Window "Reset All data"` + 确认文案 ✅ |
| `Reset` → `Cancel` | **`Reset cancelled.`** ✅ |
| `View Backups` | **`5 backup(s) on disk; newest selected.`**，列表选中第一行 ✅ |

### 这一页的特殊之处

**前 27 个假按钮分散在 15 个页面里，这一页一个页面就有 6 个（5 按钮 + 1 拖拽框）。**

**因为它是最容易「写个状态栏就算完」的页面**——导出需要文件选择器、恢复需要反序列化、
重置需要确认框、拖拽需要事件处理器。**每一个都比一行 `status.Text = "..."` 贵。**

> **假实现不是随机分布的，它集中在「实现成本高」的地方。**

### 验证

```
dotnet test      579 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
Backups/         已清空（5 个测试备份）
```

---
