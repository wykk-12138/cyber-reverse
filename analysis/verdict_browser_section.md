### `Browser`：功能完整，加一条把「跨线程」变成测试的断言

顶部工具栏最后一个窗口。

### 功能是完整的

```
[5] ←  [6] →  [7] https://example.com/  [8] Go  [9] Refresh
[10] SChannel   [11] Minimise   [12] Exit
Autofill  [13] ComboBox  [14] Copy all as JSON
[16] 页面正文
```

**实测 `Go`**：

```
HTTP 200  577 bytes  http/1.1  855 ms  server=cloudflare
<!doctype html><html lang=en>…<title>Example Domain</title>…
```

**真的发请求、真的渲染、真的报出传输层细节**（`server=cloudflare`、`http/1.1`）。

### 一处静默返回

`Copy all as JSON` 在没选 profile 时：

```csharp
var index = _profilePicker.SelectedIndex;
if (index < 0 || index >= _profiles.Count) return;   // ← 什么都不说
```

**点了没有任何反馈**，在全新安装上看起来就是个坏按钮。

**修**：

```csharp
if (index < 0 || index >= _profiles.Count)
{
    _autofillStatus.Text = _profiles.Count == 0
        ? "No profiles yet — add one on the Billing page."
        : "Select a profile first.";
    return;
}
```

**实测**：`No profiles yet — add one on the Billing page.`

### 更要紧的：把 R121/R122 那一类做成测试

前面两轮各修了一次「continuation 落在池线程」。**修完之后没有办法防止第三处出现。**

新增 `UiContinuationTests`，判据：

1. 扫 `src/Cybersole.Ui/**/*.cs`
2. 找每个 `await ` 语句（括号平衡地走到 `;`，所以跨行参数列表不会被截断）
3. 排除 `async (…) => await X();` 形状——那是**入口**，不是 continuation
4. 只报跨层调用：`await _services.` / `await services.` / `await sp.` / `await Clipboard.`
5. 剩下没 `ConfigureAwait` 的就是问题

**第一版判据太宽**，报了 6 处：

```
MainViewModel.cs:246     await Task.CompletedTask
CustomBrowserWindow.cs:279  await Navigate(...)
MainWindow.cs:56         await dialog.ShowDialog<bool>(this)
MainWindow.cs:61         await _vm.SignOutAsync()
MainWindow.cs:71         await win.ShowDialog<string?>(this)
ProviderViews.cs:761     await Task.CompletedTask
```

**6 处全是假阳性**——`Task.CompletedTask` 已经完成、`ShowDialog` 由 Avalonia 保证回到 UI 线程
（R121 实测过 `3DS code captured` 出现，证明它没跨线程）、`Navigate` 和 `SignOutAsync` 是同程序集方法。

**收紧到「只查跨层的服务/平台调用」后归零。**

### 为什么选「跨层」这个判据

`await` 一个同程序集的方法时，那个方法内部的 `ConfigureAwait` 决定一切——查外层没有意义。
**只有调用到 `Cybersole.Services` / `Cybersole.Http` / Avalonia 平台 API 时，UI 才知道自己会掉到哪个线程。**

**`Services` 层有 73 处 `ConfigureAwait(false)`**，是故意的：它不该关心 UI 线程。
**但每一处跨层 `await` 都是那条边的渡口，UI 必须在渡口上写明「回来时我在哪」。**

### 三个层次的验证

| 层 | 手段 | 覆盖 |
|---|---|---|
| 单个窗口 | CUA 实测 | `Go` 的 200、`Copy all` 的新消息 |
| 一类模式 | **新测试** | 未来新增的跨层 await |
| 全库 | `verify.ps1` | 580 测试 / live / 61 模块 |

### 验证

```
dotnet test      580 通过 / 0 失败 / 2 跳过   (+1 UiContinuationTests)
live contracts   PASS
store modules    PASS 61 registered
bare cross-layer awaits: 0
```

---
