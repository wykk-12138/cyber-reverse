### 三个账号类页面：一处纯假，一处措辞不准

`Email Accounts` / `Google Accounts` / `PayPal Accounts` 三页，13 个按钮。

### 逐个对照

**`ImapView`（Email Accounts，5 个）**

| 按钮 | 实现 |
|---|---|
| `Add Accounts` | ❌ **只写一行提示文本** |
| `Clear Accounts` | ✅ 清空 + 保存 + 刷新 |
| `Save` | ✅ 真的保存 |
| `Delete Selected` | ✅ 真的删 |
| `Connect` | ⚠️ 真的设 `aycd.Enabled = true` 并保存，但文案说「requested」 |

**`GoogleAccountsView`（4 个）**

| 按钮 | 实现 |
|---|---|
| `Add Account` | ✅ `AddViaSignIn` —— 真的跑 `GoogleOAuthFlow.BeginAsync` / `CompleteAsync`，5 分钟超时 |
| `Clear Accounts` | ✅ |
| `Add Manually` | ✅ 校验邮箱、加进列表 |
| `Delete Selected` | ✅ |

**`PayPalAccountsView`（5 个）** —— 全部真的（`Add` / `Edit` / `Delete` / `Toggle` / `Clear`）。

### 第 21 个假按钮

```csharp
UiKit.Button("Add Accounts", () => status.Text =
    "Fill in the provider, email address and password, then Save."),
```

**它的全部行为是给出填写建议。** 建议本身没错——下面确实有三个输入框——但按钮名叫 `Add Accounts`，用户点了会期待一个输入行出现。

**修**：把焦点放到第一个输入框。

```csharp
UiKit.Button("Add Accounts", () =>
{
    provider.Focus();
    status.Text = "Enter the host, email and password below, then Save.";
}),
```

**实测**：点完之后 `Select or enter host` 有蓝色聚焦框，光标在里面。

**这不是把假功能变真功能**——`Add Accounts` 本来就没有"批量添加"这回事，输入是单条表单。
**但它现在把用户送到该去的地方，而不是只说一句「你去填吧」。**

### `Connect` 的措辞改了

```csharp
aycd.Enabled = true;
services.Config.Save();
Refresh();
status.Text = "AYCD Inbox connect requested.";   // ← 暗示发了网络请求
```

**实际只翻了开关。** 改成：

```csharp
status.Text = "AYCD Inbox enabled. Save to keep it.";
```

**`Connect` 这个名字本身就有点大**——它连的不是 AYCD 服务，是本地的启用位。但改名会动 UI 文案，
先改状态栏那句更直接的。

### 这一轮的分类和前面不同

| 类型 | 例子 | 处理 |
|---|---|---|
| 纯假 | `Add Accounts` | 改成真的做事（聚焦） |
| 做了但说大了 | `Connect` | 改文案 |
| 真的 | 其它 11 个 | 不动 |

**「做了但说大了」是这轮新出现的类型。** 前面 20 个都是「完全没做」，
`Connect` 是「做了 A，说成做了 B」。

### 验证

```
dotnet test   549 通过 / 0 失败 / 2 跳过
release build 0 errors
verify.ps1    VERDICT: all checks passed
```

---
