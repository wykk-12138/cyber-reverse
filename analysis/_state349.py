import io
p = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t = io.open(p, encoding='utf-8').read()
t = t.replace('| `TaskView` | `CreateGroup` `LinkChange` `MoveGroup` `PinGroups` `Quicktask` `Toggle` | 绑定表有名字，**不知道具体做什么**；快捷键页给了一部分线索（`Ctrl+M` Link Change、`Ctrl+Q` Quicktask、`Ctrl+G` New Group） |',
              '| `TaskView` | `CreateGroup` `LinkChange` `MoveGroup` `PinGroups` `Quicktask` `Toggle` | 绑定表有名字；**R349 找到文案线索**：`Monitor.LinkChange` = "Link Change"、字面量 **"Mass Link Change"**（批量改链接）、`Monitor.LaunchQuicktask` = "Launch Quicktask"、`Settings.General.QuicktaskSettings`。机制仍未知 |')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('backlog updated with label evidence')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 349 轮：从文案里挖出两条线索，并把导出提示换成 locale 原文

### 一、留白项的证据搜索（池子里的文案）

| 名字 | 池子里的线索 |
|---|---|
| `TaskView.LinkChange` | `Monitor.LinkChange` = **"Link Change"**，外加字面量 **"Mass Link Change"** → 是**批量改链接** |
| `TaskView.Quicktask` | `Monitor.LaunchQuicktask` = **"Launch Quicktask"**、`Settings.General.QuicktaskSettings` |
| `SmartActionsView.Clock` | `Settings.General.EnableClock` = **"Enable clock"** + `.Tooltip` → 是被设置项控制的**时钟显示** |
| `DataView.Export` | `Data.Export.Fail.Title` = **"Export Fail"**、`.Message` = **"Failed to export data."**，另有 Success 一对 |

**机制仍未恢复**，所以三个 `TaskView` 操作继续留白；但线索已记进 backlog，下轮不必再找。

### 二、能立刻落的一条：导出提示

复刻件原来写 `"Export failed: {ex.Message}"`。现在失败行以 **`Export Fail — Failed to export data.`** 开头
（locale 原文），成功行用 `Export Success`。常量写在 `DataView` 上，`DataExportCopyTests` 钉住。

### 三、验证

```
DataExportCopyTests   1 通过
完整套件              1515 通过 / 0 失败 / 2 跳过
```

### 四、这一轮的一句话

> 留白不是终点：**池子里的文案就是下一轮的路标**。
> "Mass Link Change" 这四个字，比我再猜十轮都值钱。
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 349 轮（导出提示改为 locale 原文；留白项挖到文案线索："Mass Link Change" 等）。

---

## 留白项的文案线索（下次不用再找）

| 名字 | 线索 |
|---|---|
| `TaskView.LinkChange` | `Monitor.LinkChange`="Link Change"、字面量 **"Mass Link Change"** → 批量改链接 |
| `TaskView.Quicktask` | `Monitor.LaunchQuicktask`="Launch Quicktask" |
| `SmartActionsView.Clock` | `Settings.General.EnableClock`="Enable clock" + `.Tooltip` → 受设置控制的时钟显示 |
| `DataView.Export` | `Data.Export.Fail.Title`="Export Fail" / `.Message`="Failed to export data." |

## 本轮落地

`DataView.ExportSuccessTitle` / `ExportFailTitle` / `ExportFailMessage` 三个常量 + 失败行改用 locale 原文；
`DataExportCopyTests` 钉住。

## 状态

```
完整套件   1515 通过 / 0 失败 / 2 跳过
名字级缺口 17；类型级缺口 41
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
