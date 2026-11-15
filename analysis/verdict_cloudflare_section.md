### `Cloudflare Providers`：落盘是对的，但表单被忽略了

和 `Captcha Providers` 同构，所以先查 R113 那两层 bug 有没有复刻。

### 落盘：没有复刻

```csharp
s.CloudflareSolvers.Add(new CloudflareSolverConfig { ... });
services.Config.Save();
```

**`s` 就是 `services.Config.Settings`**，`CloudflareSolvers` 是被序列化的字段——
不存在 R113 那种「改 A 保存 B」的问题。

**实测确认**：

```json
"cloudflareSolvers": [
  {"id": "9a1ced7f", "name": "my-cf-solver", "type": "uncaptcha.io",
   "apiKey": "cf-key-1", "concurrency": 7, "balance": 0.0}
]
```

### 但表单是装饰品

```csharp
UiKit.Button("Add", () =>
{
    s.CloudflareSolvers.Add(new CloudflareSolverConfig
    {
        Name = Providers[0],      // 硬编码
        Type = Providers[0],      // 硬编码
        Concurrency = 5,          // 硬编码
    });
    …
}),
…
UiKit.Row("Name",      UiKit.Text(watermark: "uncaptcha.io")),
UiKit.Row("Provider",  UiKit.Combo(Providers)),
UiKit.Row("API Key",   UiKit.Text(password: true)),
UiKit.Row("Concurrency", UiKit.Number(5)),
```

**表单有四个字段，`Add` 读了零个。**

用户填 `my-solver` + key + `concurrency=7`，点 Add，得到的是 `uncaptcha.io / 5 / 无 key`。

**这比死按钮更难发现**：按钮真的做了事，列表真的变了，**只是变的和填的无关**。

### 修

把四个控件提成变量，`Add` 读它们：

```csharp
var nameBox = UiKit.Text(watermark: "uncaptcha.io");
var providerCombo = UiKit.Combo(Providers);
var keyBox = UiKit.Text(password: true);
var concurrencyBox = UiKit.Number(5);
```

```csharp
var type = providerCombo.SelectedItem as string ?? Providers[0];
var name = nameBox.Text?.Trim();

s.CloudflareSolvers.Add(new CloudflareSolverConfig
{
    Name = string.IsNullOrWhiteSpace(name) ? type : name,
    Type = type,
    ApiKey = keyBox.Text is { Length: > 0 } ? keyBox.Text : null,
    Concurrency = int.TryParse(concurrencyBox.Text, out var cc) && cc > 0 ? cc : 5,
});
```

**列表行也加了 key 状态**：

```
my-cf-solver  (uncaptcha.io)  concurrency=7  key=set
```

原来只显示 `concurrency`，看不出 key 有没有配。

### `Fetch balance` 加了前置检查

```csharp
if (cf.ApiKey is not { Length: > 0 })
{
    status.Text = $"{cf.Name}: no API key, so no balance to ask for.";
    return;
}
```

原来会拿着 `ApiKey = null` 去问 API。

### `Add Provider` 改成聚焦

它原来只写一句话（「用任务组的 Captcha 页选它」）——**那是建议型死按钮，和 R110 的
`Add Accounts` 同类**。改成 `keyBox.Focus()` + 说明。

### 实测

填 `my-cf-solver` / `cf-key-1` / `7` → 点 `Add`：

```
[40] ListItem "my-cf-solver  (uncaptcha.io)  concurrency=7  key=set"
```

**三项都来自表单。** 落盘确认：

```json
{"name": "my-cf-solver", "type": "uncaptcha.io", "apiKey": "cf-key-1", "concurrency": 7}
```

### 这一轮的新类型：**表单被忽略**

| 类型 | 例子 | 特征 |
|---|---|---|
| 死按钮 | `Status("...")` | 点了没反应 |
| 保存不落盘 | `Captcha Providers` | 重启就丢 |
| **表单被忽略** | **`Cloudflare Providers`** | **填了没用，但按钮真的做了事** |

**第三种最隐蔽**：列表多一行、状态栏有回执、文件也写了——**只是写的是默认值。**

只有对着「我填了什么」和「存了什么」逐项比对才能发现。

### 验证

```
dotnet test      551 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
settings.json    cloudflareSolvers 已清回 0
```

---
