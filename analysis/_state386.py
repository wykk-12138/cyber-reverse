import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 386 轮：把"小文件"也都对齐并钉住（`smartActionUtilities` 是第 6 处修正）

### 一、实机 `smartActionUtilities.json` 只有一个键

```json
{"groups": …}
```

复刻件的 `SmartActionUtilitiesDocument` 里那个属性叫 `Utilities` → 序列化出来是 `utilities`。
**又一个"文件名对、键名错"**。改成 `Groups`。

### 二、新增两个测试

```
TheSmallerDocumentsAlsoUseTheImagesKeyNames
    accounts.json         → accountGroups, payPal, google, imap, aycdInbox
    analytics.json        → proxies
    smartActions.json     → actions, templates
    smartActionUtilities.json → groups
TheGroupFilesCarryAtLeastTheImagesFields
    billing.json → id, name, profiles
    proxies.json → id, name, order, behaviour, proxies, totalDownload, totalUpload
```

这两个测试都是**真的序列化一次再读键**（R385 的教训）。

### 三、验证

```
完整套件   1544 通过 / 0 失败 / 2 跳过
```

### 四、这一轮的一句话

> 文件格式这一层，我原本以为"键名差不多"就行；实机数据告诉我：**差一个字母，就是两个程序。**

> **兼容性不是"看起来像"，是"读得进去"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 386 轮（`smartActionUtilities` 键名 `utilities` → `groups`；小文件格式全部钉住）。

---

## 文件格式对齐情况（六项全部已钉）

| 实机文件 | 复刻件类型 | 测试 |
|---|---|---|
| `settings.json` | `GlobalSettings` | `TheSettingsFileFieldsAllExist` |
| `tasks.json` | `TaskGroup` | `TheTaskGroupFileFieldsAllExist` |
| `solvers.json` | `Solver`/`SolverSettings` | `TheSolverFileFieldsAllExist` |
| `accounts.json` / `analytics.json` / `smartActions.json` / `smartActionUtilities.json` | 各自 Document | `TheSmallerDocumentsAlsoUseTheImagesKeyNames` |
| `billing.json` / `proxies.json` | `BillingGroup`/`ProxyGroup` | `TheGroupFilesCarryAtLeastTheImagesFields` |
| `Backups\\*.cyb` | `BackupDocument` | `TheBackupFileUsesTheImagesKeyNames` |

## 状态

```
完整套件   1544 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
