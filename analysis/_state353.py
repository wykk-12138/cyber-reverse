import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 353 轮：先建保险，再把 R352 做完（4 个 tab）

### 一、先建保险

上一轮靠 `.mutation-backup/` 救回四个类，这轮**第一件事是加自己的快照**：

```
tools/snapshot.py   →  tools/.snapshots/<时间戳>/…   245 个 .cs 文件
```

### 二、R352 重做（这次只用整块锚点）

| 改动 | 依据 |
|---|---|
| tab 只留 4 个（Delays / Limits / Captcha / Notifications） | locale `TaskGroup.Tab.*` 只有这四个 |
| `General` tab 删除 | locale 里没有它；`Pinned` 属 `TaskView.PinGroups`、`Order` 属 `Settings.TaskGroupOrder` |
| `Manual` tab 删除 | 它误读了 `TaskGroup.TimeSpan.Manual`（那是 "Reset limits after" 的一个选项） |
| `Period start` 移入 **Limits** | locale `TaskGroup.PeriodStart.Tooltip` 就在这块 |

### 三、结果

```
Cybersole.Ui 编译   0 错误
完整套件            1515 通过 / 0 失败 / 2 跳过
bind_scope          TaskGroupView 缺 Close / CloudflareSolvers（原缺 4 个）
```

`TaskGroupView` 的 `CloudflareSolvers` 仍缺 —— 那是 Captcha tab 里的求解器列表，语义清楚，下轮补。

### 四、这一轮的一句话

> 上一轮我用"行号"换来了四个类的损失；这一轮用"整块锚点 + 先快照"，同一步改动一次通过。

> **同一个人、同一件事，工具选对了差别就是"一次过"和"一轮报废"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''

---

## R353：Group Settings 收敛到实机的 4 个 tab

| 项 | 实机 | 复刻件（改后） |
|---|---|---|
| tab | Delays / Limits / Captcha / Notifications | **同** |
| `Group Name` | tab 之上的独立行 | 同（R351） |
| 页脚 | `Delete` / `Save` | 同（R351） |
| `Period start` | 属 **Limits**（locale tooltip 在此） | 已移入 Limits |
| `Pinned` / `Order` / `Manual` | 不在本弹窗 | **已删**（`Pinned`→`TaskView.PinGroups`，`Order`→`Settings.TaskGroupOrder`） |
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('GUI_BASELINE updated')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 353 轮（先建 `tools/snapshot.py` 快照，再把 Group Settings 收敛到实机的 4 个 tab）。

---

## 安全网

```
python tools/snapshot.py   →  tools/.snapshots/<时间戳>/   （245 个 .cs）
```

**改结构前先跑它。** 上一轮靠 `.mutation-backup/` 救回四个类，这一轮起有自己的快照。

## Group Settings 现在与实机一致

| 项 | 状态 |
|---|---|
| 4 个 tab（Delays/Limits/Captcha/Notifications） | ✅ |
| `Group Name` 在 tab 之上 | ✅ |
| 页脚 `Delete` / `Save` | ✅ |
| `Period start` 在 Limits | ✅ |
| `Pinned` / `Order` / `Manual` 移除 | ✅ |

剩 `TaskGroupView.CloudflareSolvers`（Captcha tab 的求解器列表）待补。

## 状态

```
完整套件   1515 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 41（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
