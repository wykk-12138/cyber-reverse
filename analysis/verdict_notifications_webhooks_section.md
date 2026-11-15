### `Settings` 前两页：一个重复标签，第 20 个死按钮

R101 验过 `General` 和 `Appearance`。这轮查 `Notifications` 和 `Webhooks`。

### `Notifications`：标签重复

读 UIA 树：

```
Text "Notifications"
Text "Enable Notifications"
Text "Allow Checkout Notifications"
Text "Allow Checkout Notifications"      ← 两次
Text "In-Bot Notifications"
Text "Desktop Notifications"
```

源码：

```csharp
return UiKit.Section(
    "Allow " + category + " Notifications",             // 段落标题
    UiKit.Row("Allow " + category + " Notifications",   // 行标题 —— 同一句话
        UiKit.Check(string.Empty, options.Enabled, v => options.Enabled = v)),
```

**`Section` 的标题和第一行的标签用了同一个表达式。**

**修**：段落标题保留类别名，行标题改成 `Enabled`：

```csharp
UiKit.Row("Enabled",
    UiKit.Check(string.Empty, options.Enabled, v => options.Enabled = v)),
```

重跑，树上只剩一个 `Allow Checkout Notifications`。

**这是纯显示缺陷**——不影响功能，但读起来像页面渲染了两次。

### `Webhooks`：`Test` 是第 20 个死按钮

三个按钮：

```csharp
UiKit.Button("Add", ...)      // URL 校验 + 保存 + 刷新  ✅
UiKit.Button("Delete", ...)   // 删除 + 保存 + 刷新      ✅
UiKit.Button("Test", () =>
{
    if (rows.SelectedIndex < 0) { status.Text = "Select a webhook."; return; }
    var target = all[rows.SelectedIndex];
    status.Text = $"Test queued for {target.Url}";   // ❌ 就这一行
}),
```

**「Test queued」——没有队列，没有请求，什么都没发生。**

### 这个措辞比 `Status("...")` 更糟

前面 19 个死按钮至少说的是「我打开了」「我克隆了」——**只是没做**。

这个说的是 **「测试已排队」**——暗示一个异步任务已经启动。**用户会等结果，永远等不到。**

### 修成真的发请求

```csharp
UiKit.Button("Test", async () =>
{
    if (rows.SelectedIndex < 0) { status.Text = "Select a webhook."; return; }
    var target = all[rows.SelectedIndex];

    // "Test queued for {url}" used to be the whole handler — a status line that claimed work
    // it never did. Now it actually posts.
    status.Text = $"Testing {target.Url}…";
    try
    {
        var payload = "{\"content\":\"Cybersole webhook test\",\"username\":\"Cybersole\"}";
        var res = await services.Http.PostJsonAsync(target.Url, payload).ConfigureAwait(true);

        status.Text = res is null
            ? "Test failed: no response"
            : $"Test: HTTP {res.StatusCode} ({res.BodyBytes} B)";
    }
    catch (Exception ex)
    {
        status.Text = "Test failed: " + ex.Message;
    }
}),
```

`UiKit.Button` 收的是 `Action`，所以 `async () =>` 变成 `async void`——**异常必须自己 catch**，
否则会变成未处理异常。

### 实测

加一个 webhook（URL 指向 `127.0.0.1:9`，discard 端口），选中，点 `Test`：

```
Text "Testing http://127.0.0.1:9/hook…"          ← 中间态
Text "Test failed: request failed: http://127.0.0.1:9/hook"   ← 最终态
```

**失败是预期的，重点是它真的发了。**

**中间态也出现了**——证明 `async` 生效，没有阻塞 UI。

### 清理与验证

```
settings.json  webhooks: 1 → 0
```

```
dotnet test      549 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
verify.ps1       VERDICT: all checks passed
```

---
