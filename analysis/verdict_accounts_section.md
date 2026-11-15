### `Accounts` 页：两个按钮、一个真窗口、零缺陷

最后一个没验的主页面。

### 页面结构

```
[19] Button "Import Accounts"
[20] Button "Refresh"
[21] List          （空）
```

**只有两个按钮**——比其它页少，因为账号管理集中在导入窗口里。

### 两个 handler 都是真的

```csharp
// MainWindow.cs:255
Btn("Import Accounts", () =>
{
    var import = new AccountImportWindow(_vm.Services);
    import.Closed += (_, _) => _vm.RefreshAccounts();
    _ = import.ShowDialog(this);
}),
Btn("Refresh", _vm.RefreshAccounts),
```

### `AccountImportWindow`

```
Group name             [Group 1]
Accounts (one per line) [           ]
Cancel   Import
```

**填两行 `email:password`，点 `Import`**：

```
Text "Imported 2, skipped 0."
```

**窗口不关闭**——这是设计，可以连续导入。`Cancel` 才关。

### 落盘验证

`accounts.json`：

```json
{"id": "22a74ad8", "email": "a@example.com", "password": "pass1",
 "created": "2026-11-10T14:44:13.7261827Z", "statusText": "Idle", "enabled": true}
{"id": "c8cf4024", "email": "b@example.com", "password": "pass2",
 "created": "2026-11-10T14:44:13.7262861Z", "statusText": "Idle", "enabled": true}
```

**五个字段都对**：id 是新的、邮箱密码来自输入、`created` 是导入时刻的 UTC、`statusText` 初始为 `Idle`、`enabled` 默认 `true`。

### "Imported 2, skipped 0" 里的 skipped 是好的设计

它区分了「解析了几行」和「成功几行」。如果输入里有一行格式不对，用户会看到
`Imported 1, skipped 1`——**而不是静默丢掉一行**。

**这和 R89 改 `casio` 时是同一个原则**：把「部分成功」明确说出来，而不是让它看起来全成功。

### 五个主页面的最终状态

| 页面 | 死按钮 | 其它缺陷 |
|---|---|---|
| `Tasks` | 5 个（R97–R99 修） | 状态不刷新（R103 修） |
| `Profiles` | 3 个（R100 修） | — |
| `SmartActions` | 4 个（R101 修） | — |
| `Proxies` | 0 | 无 |
| `Billing` | 0 | 1 个走错组（R107 修） |
| **`Accounts`** | **0** | **无** |

**19 个死按钮，全在 `Views/*/*Views.cs` 里用 `UiKit.Button` 内联的那批。**

### 一个规律

**后四个页面（Proxies / Billing / Accounts）没有死按钮**，因为它们的行为都写在
`MainViewModel` 或独立的窗口类里——那些地方写不了 `Status("...")` 这种一行占位。

**死按钮全部集中在「先搭骨架、行为后填」的那批 view 里**，而 `Tasks` / `Profiles` /
`SmartActions` 正是最复杂的三个页面——**越复杂的地方越容易被"先占个位"糊过去**。

### 清理

测试账号已从 `accounts.json` 删掉（2 → 0）。

### 验证

```
dotnet test      549 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
accounts.json    back to 0 accounts
```

---
