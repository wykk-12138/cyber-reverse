import io
p = r'D:\projects\cyber-reverse\replica\docs\B_CLASS_DECISIONS.md'
t = io.open(p, encoding='utf-8').read()
old = '| `Cybersole.Models.NotificationSound` | SoundLocation | 已有等价物 | 复刻件的提示音是设置里的路径字符串 |'
new = '| `Cybersole.Models.NotificationSound` | SoundLocation | 已有等价物 | **`NotificationOptions.Path`**（`Profiles.cs:175`，每类一个），`SelectSound`/`ResetSound` 写它（R310 核实） |'
assert old in t
t = t.replace(old, new, 1)
add = '''

## R310：把"已有等价物"这一列也逐条核实了一遍

不能只写"已有等价物"就完事 —— 那和"结构差异"是同一句空话。逐条查了实现：

| 声称的等价物 | 实际存在 | 位置 |
|---|---|---|
| `AccountStoreEntry.IsSelected` → 账户树节点选中 | ✔ | 2 处命中（选中账户字段） |
| `LocalizeFormatExtension.Value2` → `string.Format` | ✔ | 2 处 |
| `AycdInboxAccount.TaskCount` → Aycd 计数 | ✔ | 4 处 |
| `NotificationSound.SoundLocation` → **`NotificationOptions.Path`** | ✔ | `Profiles.cs:175` + `SelectSound` 写它 |
| `BrowserProfile.DisplayName` → `BrowserProfileAssignment` | ✔ | 15 处 |
| `AuthWindow.Logout` → `UserView.LogOut()` | ✔ | 2 处（R259 加的） |
| `LicenseControl.Authenticate` → `LoginControl` | ✔ | 15 处 |
| `AccountStoreType` → `IStoreModule` | ✔ | 7 处 |

**两条"我一开始以为没有"的，其实是名字不同**：`SoundLocation` 在复刻件里叫 `Path`。
又一次印证 R295 那条：**"未命中"要复核查法。**

（`LocalizeSwitchExtension.Condition` 与 `Filter.Variable` 仍按"内联/内部状态"处理 ——
它们本来就不是可指认的成员。）
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('B_CLASS_DECISIONS updated with the verification pass')
