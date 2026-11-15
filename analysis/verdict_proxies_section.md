### `Proxies` 页：三个按钮全是真的

R97–R105 把 `Tasks` 页和任务引擎验完了。这轮查 `Proxies`——它从没被点过。

### 页面结构

```
[19] Edit          （批量导入框）
[20] Button "Import"
[21] Button "Test All"
[22] Button "Refresh"
[23] List
  [24] ListItem "[Group 1] (0) behaviour=RoundRobin"
```

### 三个 handler 都是真的

```csharp
// MainWindow.cs:295-297
Btn("Import", () => { _vm.ImportProxies(); import.Text = string.Empty; }),
Btn("Test All", async () => await _vm.TestProxiesAsync()),
Btn("Refresh", _vm.RefreshProxies),
```

```csharp
// MainViewModel.cs:171
public void ImportProxies()
{
    var parsed = ImportParser.ParseProxies(ProxyImportText);
    if (parsed.Count == 0) { Status = "Nothing to import"; return; }

    var group = _services.Config.ProxyGroups[0];
    foreach (var proxy in parsed) group.Proxies.Add(proxy);

    ProxyImportText = string.Empty;
    _services.Config.Save();
    RefreshProxies();
    Status = $"Imported {parsed.Count} proxy line(s)";
}
```

```csharp
// MainViewModel.cs:190
public async Task TestProxiesAsync()
{
    var proxies = _services.Config.ProxyGroups.SelectMany(g => g.Proxies).ToList();
    if (proxies.Count == 0) { Status = "No proxies to test"; return; }

    Status = $"Testing {proxies.Count} proxies…";
    var results = await _services.ProxyTester.TestAllAsync(proxies, 25).ConfigureAwait(true);
    Status = $"Tested: {results.Count(r => r.Ok)}/{results.Count} ok";
    RefreshProxies();
}
```

**两个都有空集合早退、都真的做事、都调 `RefreshProxies()`。**

### 实测

**Import** —— 填 `127.0.0.1:8080:user:pass`：

```
[24] ListItem "[Group 1] (1) behaviour=RoundRobin"     ← (0) 变 (1)
```

读配置文件确认落盘：

```json
{"id": "0dca77cb", "host": "127.0.0.1", "port": 8080,
 "username": "user", "password": "pass",
 "status": {"color": "#6E7681", "icon": "circle", "text": "Idle"}}
```

**Test All**：

```
Text "Tested: 0/1 ok"
[24] ListItem "   127.0.0.1:8080             Failed   dl=0KB"
```

**失败是预期的**——那个地址上没有 HTTP 代理。重点是它**真的去试了**，
把结果写回 `List`，并更新了状态栏。

### 和前几轮的对比

| 页面 | 结果 |
|---|---|
| `Tasks`（R97–R99） | 5 个死按钮 |
| `Profiles`（R100） | 7 个 status-only，修了 3 个 |
| `SmartActions`（R101） | 4 个 status-only，全修 |
| **`Proxies`（R106）** | **三个全是真的，零缺陷** |

**`Proxies` 是第一个"查了没有缺陷"的页面。**

而这不是巧合：它的三个按钮都走 `MainViewModel`，而 `MainViewModel` 里那些方法
（`ImportProxies` / `TestProxiesAsync` / `RefreshProxies`）**有真实的实现**——
不是 `Status("...")` 那种占位。

**死按钮集中在 `Views/*/*Views.cs` 里用 `UiKit.Button` 直接写的那些**，
也就是"UI 骨架先搭、行为后填"的那批。

### 清理

测试用的 proxy 已经从 `proxies.json` 删掉了（1 → 0），
免得下次 `Test All` 又去连一个不存在的地址。

### 验证

```
dotnet test      549 通过 / 0 失败 / 2 跳过
store modules    PASS 61 registered
verify.ps1       VERDICT: all checks passed
proxies.json     back to 0 proxies
```

---
