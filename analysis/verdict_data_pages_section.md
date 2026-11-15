### 三个数据页：两处聚焦，一处真的去查磁盘

`Custom Stores` / `Custom Sizes` / `Payment` 三页，14 个按钮。

### 发现三处假

| 按钮 | 原实现 |
|---|---|
| `Custom Sizes: Add Size(s)` | 只写「Search a product URL, then add the sizes you want.」 |
| `Payment: Configure` | 只把当前 `BrowserPath` 回显一遍 |
| `Payment: Refresh` | **只回显 `settings.BrowserProfiles` 里已有的内容**，从不看磁盘 |

### 前两处：改成聚焦

和 R110 的 `Add Accounts` 同一处理——**建议是对的，就送用户到该去的地方**：

```csharp
UiKit.Button("Add Size(s)", () =>
{
    productUrl.Focus();
    status.Text = "Paste a product URL, press Search, then Add Selected.";
}),
```

```csharp
var configure = UiKit.Button("Configure", () =>
{
    browserPath.Focus();
    status.Text = s.BrowserPath is { Length: > 0 }
        ? "Editing the path below. Current: " + s.BrowserPath
        : "Paste the full path to chrome.exe or msedge.exe below.";
});
```

**`Configure` 没有改成"打开文件选择框"**——这个应用里没有文件选择对话框，**造一个假的比没有更糟**。
注释里写明了这一点。

### 第三处：真的写了一个扫描器

`Refresh` 的语义是「重新检测浏览器 profile」。回显设置里的旧值等于什么都没做。

新增 `Cybersole.Services.BrowserProfileScanner`：

```csharp
public static List<string> Scan()
{
    foreach (var (label, roots) in Candidates)     // Chrome / Chrome Beta / Edge / Brave
    {
        if (!Directory.Exists(root)) continue;
        foreach (var dir in Directory.EnumerateDirectories(root))
        {
            var name = Path.GetFileName(dir);
            var looksLikeProfile = name.Equals("Default", OrdinalIgnoreCase)
                                   || name.StartsWith("Profile ", OrdinalIgnoreCase);
            if (!looksLikeProfile) continue;

            // a real profile has preferences; an empty leftover directory does not
            if (!File.Exists(Path.Combine(dir, "Preferences"))) continue;

            found.Add($"{label}: {name}");
        }
    }
    return found.Distinct().OrderBy(...).ToList();
}
```

**判据和 Chrome 自己用的一样**：`Default` 或 `Profile N`，且有 `Preferences` 文件。
所以 `Guest Profile` / `System Profile` / `Crashpad` 自动被排除，**不需要硬编码它们的名字**。

**排序**：`Distinct().OrderBy(...)`，保证两次调用结果一致——否则 combo 的选中项会跳。

### `Refresh` 现在也重建 combo

```csharp
s.BrowserProfiles = found;
services.Config.Save();

checkoutProfile.ItemsSource = new[] { "Browser default" }.Concat(found).Distinct().ToList();
checkoutProfile.SelectedIndex = 0;
```

**只改设置不改 combo 的话，用户刷新完还得重启才能选到新 profile。**

### 实测

独立用 Python 数一遍：

```
EXISTS C:\Users\wykk\AppData\Local\Google\Chrome\User Data
   profile: Default, Profile 2, 5, 8, 9, 11, 12, ...   （25 个）
EXISTS C:\Users\wykk\AppData\Local\Microsoft\Edge\User Data
   profile: Profile 2                                   （1 个）
missing C:\Users\wykk\AppData\Local\BraveSoftware\...
```

**共 26 个。**

点 UI 的 `Refresh`：

```
Text "26 profile(s): Chrome: Default, Chrome: Profile 11, Chrome: Profile 12,
      Chrome: Profile 14, Chrome: Profile 15, Chrome: Profile 18"
```

**数字对上了。**

### 这一轮三种处理的区别

| 按钮 | 处理 | 理由 |
|---|---|---|
| `Add Size(s)` | 聚焦 | 建议对，动作缺失 |
| `Configure` | 聚焦 + 改文案 | 没有文件选择器，不造假 |
| `Refresh` | **真的实现** | 它能做到，只是没做 |

**判据是「这件事在这个应用里做得到吗」。** 做得到就实现（`Refresh`），做不到就诚实
（`Configure`），只是没做就该做（`Add Size(s)`）。

### 验证

```
dotnet test      549 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
browserProfiles  back to 0
```

---
