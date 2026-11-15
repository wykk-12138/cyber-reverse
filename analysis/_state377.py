import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 377 轮：`StoreGroupModal.Delete` / `IsEditing`（缺口 15 → 14）

| 成员 | 实现 |
|---|---|
| `IsEditing` | 只读：构造时传没传 `existing` |
| `Delete` | 从 `Config.Settings.StoreGroups` 移除并保存；新建模式返回 false |

### 三次编译失败，一次比一次具体

1. 文件路径猜错（`Views/UtilitiesViews.cs` → 实际 `Views/Utilities/UtilitiesViews.cs`）；
2. 类里**没有** `_services` 字段（构造参数没存下来）→ 加 `_storeServices`；
3. `Config.StoreGroups` **不存在** → 实际是 `Config.Settings.StoreGroups`。

第 3 条正是 §12.2 说的"写 `Config.X` 之前先 grep"，我又忘了 —— 这次让编译器替我 grep 了一次。

```
完整套件   1536 通过 / 0 失败 / 2 跳过
bind_scope 15 → 14
```

### 这一轮的一句话

> 同一个错误（猜集合路径）今天第二次；区别是这次我**把它写进了这一轮的记录里**，而不是只在脑子里过一遍。

> **错误重复不可怕；重复却不留痕才可怕。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 377 轮（`StoreGroupModal.Delete/IsEditing`；类型级缺口 15 → 14）。

---

## 配置集合的真实路径（血泪版）

| 想写的 | 真实的 |
|---|---|
| `Config.TaskGroups` | ✅ |
| `Config.BillingGroups` | ✅ |
| `Config.Profiles` | ❌ 不存在（在 `BillingGroups[i].Profiles`） |
| `Config.StoreGroups` | ❌ 不存在（是 `Config.Settings.StoreGroups`） |

写之前先 `grep 'List<' src/Cybersole.Core/Settings/GlobalSettings.cs`。

## 状态

```
完整套件   1536 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 14（类型级）
UI 类      104 声明 / 28 不可达
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
