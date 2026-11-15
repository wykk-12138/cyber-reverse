import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 309 轮：把"B 类 31 个结构差异"从一句话变成**逐类型决定**（不编译）

### 一、为什么现在做

缺口 31 长期被一句"都是结构差异"包着。但**"结构差异"不是结论，是没做决定**。
而绑定表 `docs/xaml_bindings.json` 其实给每个类型都留了**完整命名空间** ——
这让"决定"有了依据。

### 二、21 个类型的完整名，全部来自绑定表

```
Cybersole.Ui.Views.Profiles.Modals.ProfileCsvRow
Cybersole.Ui.Views.SmartActions.{FilterRow, ActionRow, InputRow, FilterInputEntry}
Cybersole.Ui.Controls.ComboBoxEdit
Cybersole.Ui.Views.Tasks.ElementCell
Cybersole.Ui.Localization.{LocalizeSwitchExtension, LocalizeFormatExtension}
Cybersole.Models.{AycdInboxAccount, NotificationSound, User}
Cybersole.Helpers.BrowserProfile
Cybersole.Attributes.Platform
Cybersole.Webhook.IWebhook
Cybersole.Ui.Views.Auth.{AuthWindow, LicenseControl}
Cybersole.Ui.Views.Accounts.{AccountStoreEntry, AccountStoreType}
```

### 三、四种决定

| 决定 | 条数 | 例子 |
|---|---|---|
| **值得抽控件** | **8** | `ProfileCsvRow`、`FilterRow`、`ActionRow`、`InputRow`、`FilterInputEntry`、`ComboBoxEdit`、`ElementCell`、`IWebhook.ExtraFields` |
| 已有等价物 | 12 | `AccountStoreEntry`（账户树节点）、`LocalizeFormatExtension`（`string.Format`）、`AuthWindow`（`UserView.LogOut`） |
| 不可得 | 3 | `Platform` 三值、`User.IsStaff`、`SettingsView.Transition` |
| 纯内部状态 / 重复计数 | 2 | `Filter.Variable`、`FilterRow` 重复 |

### 四、两个"名不副实"被拆穿

1. **`Filter` 在绑定表里指向 `FilterRow`** —— 不是独立类型，是重复计数；
2. **`SettingsView` 指向 `GeneralSettingsView`**，`Transition` 与 R261 那个同名成员是**同名不同类**，
   且没有任何证据说明它控制什么 → 判不可得。

### 五、这一轮没有编译

可用内存 6.9 GB（低于硬线）。全部工作是读绑定表 + 写文档。

### 六、这一轮的一句话

> "31 个结构差异"听着像结论，其实是**31 个还没做的决定**。

> **把它们逐个判成"抽 / 已有 / 不可得"，下一轮才可能真正动手 —— 否则每一轮都要重新想一遍。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 309 轮（B 类 31 个缺口逐个决定，写入 `docs/B_CLASS_DECISIONS.md`；未编译）。

---

## B 类 31：现在有逐类型决定

| 决定 | 条数 | 内容 |
|---|---|---|
| **值得抽控件** | **8** | `ProfileCsvRow` / `FilterRow` / `ActionRow` / `InputRow` / `FilterInputEntry` / `ComboBoxEdit` / `ElementCell` / `IWebhook.ExtraFields` |
| 已有等价物 | 12 | 账户树节点、`string.Format`、`UserView.LogOut` 等 |
| 不可得 | 3 | `Platform` 三值 / `User.IsStaff` / `SettingsView.Transition` |
| 纯内部状态或重复计数 | 2 | `Filter.Variable`（其实是 `FilterRow`）、`FilterRow` 重复 |

**每个类型都有完整命名空间（来自绑定表）+ 决定 + 依据**，见 `docs/B_CLASS_DECISIONS.md`。

两个"名不副实"已拆穿：`Filter` → `FilterRow`（重复计数）；`SettingsView` → `GeneralSettingsView`（`Transition` 同名不同类）。

## 下一步

按"值得抽控件"的 8 条做，**一次一个**，每个都带绑定表依据。第一顺位建议 `ComboBoxEdit`
（token 多选下拉，同族 `ComboBoxToken`/`ComboBoxGroupHeader` 说明这是一个可复用的控件族）。

## 状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R307）
mutation   29 条 / 锚点 29/29
缺口       31（= 8 抽 + 12 等价 + 3 不可得 + 2 重复/内部）
Commit     40.5 GB / 可用 6.9 GB   ← 低于硬线，建议重启
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
