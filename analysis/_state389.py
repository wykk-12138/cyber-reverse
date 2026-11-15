import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 389 轮：从**原版自己写的备份**里挖出两个真字段

### 一、这一轮的证据是干净的

`Backups\\Backup 14 Nov 08h01m.cyb`：紧凑（无缩进、无空格）+ camelCase。
复刻件在 R388 之前一直写缩进版 —— **这份备份不可能是复刻件写的**。而且它带着真实
`bearer`（JWT）和 `license`（授权码），复刻件从来没有这两个值。

### 二、结构（原版）

```
proxies   [{ id, name, order, maxUsage, behaviour, usagePeriod, usageExpiry, proxies }]
billing   [{ id, name, order, profiles }]
accounts  { accountGroups, payPal, google, imap, aycdInbox }
solvers   [{ left, top, width, height, solvers }]
settings  { bearer, license, quickTaskProxies, quickTaskProfiles, monitorDelay, … }
tasks     [{ id, name, order, usagePeriod, usageExpiry, checkoutLimit, profileLimit,
             monitorDelay, retryDelay, timeout, linkedDelays, pinned, captchaSource,
             cloudflareSolver, webhooks, tasks }]
smartActions []   smartActionUtilities { groups }   analytics { proxies }
```

### 三、发现的两处缺字段

| 类型 | 缺 | 依据 |
|---|---|---|
| `TaskGroup` | `usagePeriod` | 原版每个任务组都写 |
| `ProxyGroup` | `usagePeriod` | 原版每个代理组都写（R54 曾据绑定表断言"没有这个字段"） |

**R54 的结论被推翻**：XAML 只绑 `UsageExpiry`，但**持久化层两个都写**。
持久化证据 > 绑定清单 —— 两者都保留，注释里写清为什么。

### 四、顺带确认

- `SolverView` 的 `left/top/width/height/solvers`：复刻件**本来就对**；
- `settings` 里的 `bearer/license/quickTaskProxies/shopifyBrowserProxy/browserPath`：
  上一轮怀疑是"复刻件多出来的 5 个"，**实为原版真有**（备份里就在）。

### 五、验证

```
完整套件   1546 通过 / 0 失败 / 2 跳过
LiveSchemaPinsTests.TheOriginalBackupFieldsAllExistOnTheModels
    TaskGroup  16 字段 → 缺 0
    ProxyGroup  8 字段 → 缺 0
    SolverView  5 字段 → 缺 0
```

### 六、这一轮的一句话

> 同一份数据，上一轮用它推翻自己，这一轮用它补了两个字段 —— **区别只在于我搞清了作者是谁。**

> **先验证证据的来源，再拿它下结论。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 389 轮（从原版备份补出 `TaskGroup.UsagePeriod` / `ProxyGroup.UsagePeriod`）。

---

## 原版备份给出的结构（可信）

```
tasks[]    16 字段（含 usagePeriod 与 usageExpiry 两个）
proxies[]   8 字段（含 usagePeriod 与 usageExpiry 两个）
solvers[]  left / top / width / height / solvers
settings   44 键（含 bearer / license / quickTaskProxies / shopifyBrowserProxy / browserPath）
```

**R54 的"代理组没有独立 usagePeriod"被推翻**：绑定表只说 XAML 绑了什么，持久化层两个都写。

## 状态

```
完整套件   1546 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
