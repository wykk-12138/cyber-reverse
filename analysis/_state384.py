import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 384 轮：备份文件的键名对不上 —— 一个"能写不能读"的真缺陷

### 一、证据

实机的 `Backups\\Backup 14 Nov 08h01m.cyb` 是**明文 JSON**，顶层键正好九个：

```json
{ "proxies": …, "billing": …, "accounts": …, "solvers": …, "settings": …,
  "tasks": …, "smartActions": …, "smartActionUtilities": …, "analytics": … }
```

复刻件的 `BackupDocument` 写的是 `Version / CreatedUtc / Settings / Accounts / TaskGroups /
ProxyGroups / BillingGroups / Solvers / Analytics / SmartActions`：

- **键名不同**（`tasks` vs `TaskGroups`、`proxies` vs `ProxyGroups`、`billing` vs `BillingGroups`）；
- **少一个** `smartActionUtilities`；
- **多两个** `Version` / `CreatedUtc`。

**后果：复刻件写的备份，原版读不了；原版写的备份，复刻件也读不了。**

### 二、修复

九个属性各加 `[JsonPropertyName]`，名字严格照实机；补 `SmartActionUtilities`；
删掉 `Version` / `CreatedUtc`（实机没有）。

### 三、钉住

`LiveSchemaPinsTests.TheBackupFileUsesTheImagesKeyNames` —— 把实机九个键与
`BackupDocument` 的属性映射对差集，**必须完全相等**。

```
完整套件   1542 通过 / 0 失败 / 2 跳过
```

### 四、这一轮的一句话

> 这是这一程第一个"**格式级**"缺陷 —— 不是少个方法、多个按钮，而是**文件互不兼容**。

> **功能对得上、界面对得上，文件格式对不上，那还是两个程序。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 384 轮（备份文件键名与实机对齐：`BackupDocument` 九个 `[JsonPropertyName]`）。

---

## 文件格式已对齐（这一轮最重要）

实机 `.cyb` 顶层键 = `proxies, billing, accounts, solvers, settings, tasks, smartActions, smartActionUtilities, analytics`。
复刻件原来用 PascalCase 且少一个、多两个 → **两边备份互不兼容**，已修并用测试钉住。

## 已核对的实机文件格式

| 文件 | 复刻件对应 | 状态 |
|---|---|---|
| `settings.json` | `GlobalSettings` | 43 键全中 |
| `tasks.json` | `TaskGroup` | 10 键全中 |
| `solvers.json` | `Solver` + `SolverSettings` | 4 + 7 全中 |
| `checkoutHistory.json` | `CheckoutEvent` | 9 键全中 |
| `Backups\\*.cyb` | `BackupDocument` | **R384 修好并钉住** |

## 状态

```
完整套件   1542 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
