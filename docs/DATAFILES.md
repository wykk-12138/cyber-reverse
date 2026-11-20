# 数据文件名对照（自动生成：`python tools/datafiles_diff.py`）

> **事实源是数据目录本身**（`%APPDATA%\Cybersole`，只读列举）。
> 镜像里的 UTF-16 字面量只是次要信号：它**漏掉运行时拼接出来的名字**，也**会拣到不是文件的名字**（URL 路径、MIME 类型）。
> R600 曾只用字面量，把 `checkoutHistory.json` 误报为「仅复刻件有」—— 那个文件真实存在（89,554 B）。
> `*.csproj` 声明的 `<EmbeddedResource>`（如 `Cybersole.Locales.*.json`、`Cybersole.ProfileValidation.en.json`）属程序集内嵌资源，不落盘，已自动排除。

| 项 | 值 |
|---|---|
| 数据目录 | `C:\Users\wykk\AppData\Roaming\Cybersole` |
| 目录内 .json 文件 | 11 |
| 镜像 .json 字面量 | 23 |
| 内嵌资源排除（`*.csproj` `EmbeddedResource` + 模板） | 6 |
| 复刻件引用（非内嵌资源） | 12 |

| 集合 | 名字 |
|---|---|
| 两侧都有（目录 ∩ 复刻件） | `accounts.json`, `analytics.json`, `billing.json`, `checkoutHistory.json`, `proxies.json`, `sessions.json`, `settings.json`, `smartActionUtilities.json`, `smartActions.json`, `solvers.json`, `tasks.json` |
| **原版目录有、复刻件没写** | — |
| **复刻件自写、两侧都查不到（written-by-replica-only）** | — |
| 只读探测候选（read-only fallback candidate，R702 范围外） | `license.json` |
| 只是字面量、不是文件 | `CreateToken.json`, `__data.json`, `config.json`, `graphql.json`, `meta.json`, `popDraw.json`, `products.json`, `prop.json`, `public.json`, `shipping_rates.json`, `sku-stores.json`, `system.text.json.serialization.json`, `wpt.json` |
