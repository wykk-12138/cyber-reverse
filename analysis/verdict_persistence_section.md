### 补两处落盘验证 + 把「保存不落盘」扫一遍

R113 的教训是：**`Config.Save()` 成功、写了文件、什么都没变**。
之后补了两个当时没验的页面，再把这一类扫一遍。

### `Custom Stores`：落盘

输入 `shop.example.com` → `Add` → 列表显示 `1 Preset`。

`settings.json`：

```json
"customStores": [
  {"id": "fce7ae6c", "name": "shop.example.com",
   "url": "https://shop.example.com/", "currency": "USD"}
]
```

**落盘了，而且 URL 被规范化**（补了 `https://`、补了尾 `/`）、`name` 从 host 推导、
`currency` 默认 `USD`。

### `Webhooks`：落盘

输入 `persist hook` + `https://hooks.example.com/x` → `Add` → 列表显示
`persist hook — https://hooks.example.com/x  enabled=True`。

`settings.json`：

```json
"webhooks": [
  {"id": "d495c5a0", "url": "https://hooks.example.com/x", "name": "persist hook", "enabled": true}
]
```

**落盘了。**

### 扫描：所有 `Config.Save()` 调用点

写了个文本扫描，找「调了 `Save()` 但方法体里没有赋值给任何持久字段」的方法。

```
files with Config.Save(): 18
methods that save without touching a persisted field: 13
```

**13 处，逐个看完全部是假阳性**：

| 方法 | 为什么是假阳性 |
|---|---|
| `OpenEditor()` / `OpenProfileEditor()` / `OpenActionEditor()` | 在 `Closed` 事件处理器里调 `Save()`，那时数据已变 |
| `BuildProfilesColumn()` / `BuildStoresColumn()` / `Block()` | 在 lambda 里，捕获了外部变量 |
| `SignOutAsync()` / `VerifyAsync()` / `OnFrameworkInitializationCompleted()` | 改的是 `Auth` / `License` 状态，不是 `Settings` |
| `SmartActionEditorWindow.Save()` | 改的是 `_selected`，它本身就是 `Config.SmartActions.Actions` 里的对象 |
| `MainViewModel.SaveSettings()` | 走 `var settings = Config.Settings; settings.X = …`，我的正则只认 `Config.Settings.X = …` |

**最后一个尤其值得记**：`var s = Config.Settings; s.MonitorDelay = …` 和
`Config.Settings.MonitorDelay = …` 在语义上完全一样，**在文本上不一样**。

> **文本扫描找的是"看起来像"，而"保存了没有"是运行时的事。**

13 处全假阳性，说明**这个类别的真 bug 只有 R113 那一个**——而且它是被 GUI 操作发现的，
不是被扫描发现的。

### 三处落盘验证的对照

| 页面 | 文件 | 结果 |
|---|---|---|
| `Proxies: Import`（R106） | `proxies.json` | ✅ 落盘 |
| `Accounts: Import`（R108） | `accounts.json` | ✅ 落盘 |
| `Billing: Add profile`（R107） | `billing.json` | ✅ 落盘 |
| **`Custom Stores: Add`（R114）** | `settings.json` | ✅ 落盘 |
| **`Webhooks: Add`（R114）** | `settings.json` | ✅ 落盘 |
| `Captcha Providers: Add`（R113） | `settings.json` | ❌ **曾经不落盘，已修** |

**六个「添加」操作里，只有打码 provider 那一个是坏的。**

### 为什么只有它坏

**其它五个都是往「配置对象的集合」里加**——`Config.ProxyGroups[0].Proxies`、
`Config.Accounts.AccountGroups`、`Config.BillingGroups`、`Config.Settings.CustomStores`、
`Config.Settings.Webhooks`。这些对象**本身就是被序列化的**。

**打码 provider 不一样**：视图操作的是 `CaptchaProviderRegistry`（一个纯内存容器），
而序列化的是 `GlobalSettings.CaptchaProviders`（另一个对象）。**两者之间没有连线。**

> **「改了 A 保存 B」是这个 bug 的完整形状。** 而 A 和 B 的类型还不一样
> （`CaptchaProviderConfig` vs `CaptchaProvider`），所以连"顺手把 A 塞进 B"都做不到——
> 得先给 B 补三个字段。

### 验证

```
dotnet test      551 通过 / 0 失败 / 2 跳过
live contracts   PASS
store modules    PASS 61 registered
settings.json    webhooks 和 customStores 都已清回 0
```

---
