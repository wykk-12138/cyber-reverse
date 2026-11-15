import io
p = r'D:\projects\cyber-reverse\replica\docs\DEVIATIONS.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## 八、复刻件比原版多写的四个设置项（R390）

原版自己写的备份（`Backups/Backup 14 Nov 08h01m.cyb`）里 `settings` 有 **44** 个键，复刻件的
`GlobalSettings` 有 48 个属性 —— 全部 44 个都在，另外 **4 个原版没有**：

| 属性 | locale 有吗 | 判断 |
|---|---|---|
| `EnableClock` / `ClockFormat` | `Settings.General.EnableClock` = "Enable clock" | 原版持久化的只有 `clock`（int，备份里是 0）。这两个可能是复刻件从 locale 反推出来的 |
| `MonitorConcurrency` | 无 | 疑似发明（原版是 `concurrency{ mode, maximum, ratio }`） |
| `StoreGroups` | 无 | 原版有 `customStores` / `customSizes`；复刻件的 `StoreGroupModal.Delete` 用的是这个集合 |

**为什么先不改**：删掉会连带去掉界面功能（时钟开关、分组管理），而"原版不持久化"不等于"原版没有"。
先把差异记下来，等 IDA 恢复后从反编译里定。

**现状**：这四个会被写进 `settings.json`。原版读到不认识的键通常忽略，所以不影响互通，但它们是**多余字节**。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('DEVIATIONS updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 390 轮：把"设置字段"的钉子换成可信版本（43 → 44 键）

### 一、换掉一份脏证据

之前 `LiveSchemaPinsTests.TheSettingsFileFieldsAllExist` 用的是 **43** 个键 ——
那个 `settings.json` 是复刻件自己写的（R387/R388 已证）。现在改用**原版备份**里的 **44** 个键。

差异正是那五个凭据类字段：`bearer, license, quickTaskProxies, shopifyBrowserProxy, browserPath`
—— 它们**在原版里是真实存在的**，只是复刻件自己写的那份文件里是 null 被省略了。

### 二、四个"多出来的"设置项（记进 DEVIATIONS，暂不改）

| 属性 | 判断 |
|---|---|
| `EnableClock` / `ClockFormat` | locale 有 `Settings.General.EnableClock`，但备份里只有 `clock`（int） |
| `MonitorConcurrency` | 原版是 `concurrency{mode,maximum,ratio}` |
| `StoreGroups` | 原版是 `customStores` / `customSizes` |

**不删的理由**：删掉会连带砍掉界面功能，而"原版不持久化"≠"原版没有"。
先记录，等 IDA 恢复后从反编译确认。

### 三、验证

```
完整套件   1546 通过 / 0 失败 / 2 跳过
```

### 四、这一轮的一句话

> 换掉一个数字（43 → 44）看着很小，但它意味着**这条断言终于建立在真证据上**。

> **测试的可信度，取决于它引用的数据是谁写的。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 390 轮（设置字段钉子换成原版备份的 44 键；四个多余设置项记入 DEVIATIONS）。

---

## 待 IDA 恢复后确认的四项

`EnableClock` · `ClockFormat` · `MonitorConcurrency` · `StoreGroups`
—— 原版备份里没有，复刻件会写出去。**没删**（删了会砍功能），记在 `docs/DEVIATIONS.md` 第八节。

## 状态

```
完整套件   1546 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
证据       字符串池/locale/绑定表 + 原版备份（紧凑 camelCase）可信
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
