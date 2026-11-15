import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 310 轮：把"已有等价物"这一列也逐条核实（又不编译）

### 一、为什么

上一轮我把 12 条判成"已有等价物"。但**"已有等价物"如果不去查，它和"结构差异"是同一句空话** ——
只是听起来更像结论。

### 二、逐条核实结果：8 / 8 全部存在

| 声称的等价物 | 实际 |
|---|---|
| `AccountStoreEntry.IsSelected` → 账户树节点选中 | ✔ 2 处 |
| `LocalizeFormatExtension.Value2` → `string.Format` | ✔ 2 处 |
| `AycdInboxAccount.TaskCount` → Aycd 计数 | ✔ 4 处 |
| `NotificationSound.SoundLocation` | ✔ **其实叫 `NotificationOptions.Path`**（`Profiles.cs:175`），`SelectSound`/`ResetSound` 写它 |
| `BrowserProfile.DisplayName` → `BrowserProfileAssignment` | ✔ 15 处 |
| `AuthWindow.Logout` → `UserView.LogOut()` | ✔ 2 处（R259 加的） |
| `LicenseControl.Authenticate` → `LoginControl` | ✔ 15 处 |
| `AccountStoreType` → `IStoreModule` | ✔ 7 处 |

### 三、一次"我一开始以为没有"

`SoundLocation` 我 grep 了 `SoundPath|SoundLocation|NotificationSound` —— **0 命中**，
差点判成"其实没实现"。再看才发现复刻件里它叫 **`Path`**（`NotificationOptions.Path`）。

**这是 R295 那条教训的第三次应验：未命中先复核查法。**

### 四、这一轮没有编译

可用内存 6.85 GB。全部工作是读源码 + 写文档。

### 五、这一轮的一句话

> 上一轮我把 31 条分成四类；这一轮验证了其中"已有等价物"那 12 条**确实存在**。

> **把"我判过了"变成"我查过了"，才是这两轮真正的差别。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 310 轮（逐条核实"已有等价物" 8/8 存在；`SoundLocation` 其实是 `NotificationOptions.Path`）。

---

## B 类决定：已核实，不只是判断

| 决定 | 条数 | 核实状态 |
|---|---|---|
| 值得抽控件 | 8 | 待做（下一步主任务） |
| **已有等价物** | 12 | **8/8 已逐条查证存在**（R310） |
| 不可得 | 3 | 三源否证 / 无来源 |
| 内部状态或重复计数 | 2 | 已说明 |

**一处纠正**：`NotificationSound.SoundLocation` 不是"没实现"，复刻件里叫 **`NotificationOptions.Path`**
（`Profiles.cs:175`），`SelectSound`/`ResetSound` 都写它。

**教训第三次应验**：未命中先复核查法（R295 → R310）。

## 状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R307）
mutation   29 条 / 锚点 29/29
缺口       31
Commit     40.7 GB / 可用 6.85 GB   ← 低于硬线，强烈建议重启
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
