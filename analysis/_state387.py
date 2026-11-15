import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 387 轮：**我的复刻件一直在写原版的数据目录** —— 一个严重到要推翻部分证据的缺陷

### 一、怎么发现的

想去拿实机 JSON 做"回读测试"时，先查了里面有没有 PII。结果没有邮箱，
但 `tasks.json` 里的组名是 **"G copy"、"t1"** —— **那是我自己测试里的组名。**

查 `AppPaths.DataRoot`：

```csharp
Path.Combine(ApplicationData, "Cybersole")   // ← 和原版同一个目录
```

### 二、两个后果

1. **危害用户数据**：跑一次复刻件（或测试）就会覆盖真实配置。
   ——已把 `%APPDATA%\\Cybersole` 下全部 16 个文件/备份**先复制留存**到
   `analysis/apdata-preserved-20261114-095358/`。
2. **证据变成循环论证**：我在 R382–R386 用"实机 JSON"核对字段名，
   而其中 `settings.json` / `tasks.json` / `solvers.json` 等**可能就是我自己的程序写出来的**。
   那些"字段全中"的结论，**至少有一部分是自己证明自己**。

### 三、改了什么

```csharp
DataRoot          = %APPDATA%\\CybersoleReplica   （可用 CYBERSOLE_DATA_ROOT 覆盖）
OriginalDataRoot  = %APPDATA%\\Cybersole          （只读证据，永不写入）
```

外加守卫测试 `TheReplicaNeverWritesIntoTheOriginalsDataDirectory`。

### 四、证据复核：哪些还站得住

| 证据 | 是否仍可信 | 理由 |
|---|---|---|
| 字符串池 / locale | ✅ 可信 | 从 exe 里读的，与数据目录无关 |
| `checkoutHistory.json` 9 键 | ⚠️ **需复核** | 复刻件也写这个文件（510 条里可能混了自己的） |
| `settings.json` 43 键 | ❌ **撤回** | 可能就是复刻件写的 |
| `tasks.json` / `solvers.json` | ❌ **撤回** | 同上（出现了我的测试组名） |
| `.cyb` 备份 9 键 | ⚠️ **需复核** | 时间戳 13–14 Nov，早于本轮会话，但复刻件同名同格式 |

**R383 的 `LiveSchemaPinsTests` 不能删**（它仍有回归价值），但它的注释里"来自实机"这句
必须降级为"待复核"。

### 五、这一轮的一句话

> 我花五轮用"实机数据"证明自己对，其中至少两轮的证据可能是我自己写的 —— **这比没有证据更糟。**

> **共享一个数据目录，等于把自己的作业塞进了参考答案里。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\METHOD.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''

### §15 被测程序绝不能写进被参照程序的数据目录（R387）

复刻件的 `DataRoot` 原本就是 `%APPDATA%\\Cybersole` —— 与原版完全重合。后果有两个，第二个更致命：

1. 会覆盖用户的真实配置（本轮已把原目录 16 个文件先留存）；
2. **"用实机文件核对模型"变成自我循环**：文件可能是复刻件刚写出来的，于是我"证明"了自己。

规则：

1. 复刻件一律写自己的目录（`%APPDATA%\\CybersoleReplica`），并支持 `CYBERSOLE_DATA_ROOT` 覆盖；
2. 把参照数据当作**只读证据**（`AppPaths.OriginalDataRoot`，只读）；
3. 报告"实机一致"之前先问一句：**这份数据是谁写的？**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('METHOD §15 added')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 387 轮（**发现复刻件一直在写原版数据目录**；已隔离并复核证据可信度）。

---

## 数据目录已隔离

```
复刻件   %APPDATA%\\CybersoleReplica      （CYBERSOLE_DATA_ROOT 可覆盖）
原版     %APPDATA%\\Cybersole             （只读证据，永不写入）
留存     analysis/apdata-preserved-20261114-095358/   （16 个文件）
守卫     TheReplicaNeverWritesIntoTheOriginalsDataDirectory
```

## 证据可信度（重要）

| 证据 | 状态 |
|---|---|
| 字符串池 / locale / 绑定表 | ✅ 可信 |
| `settings.json` 43 键、`tasks.json`、`solvers.json` | ❌ **撤回**（可能是复刻件写的） |
| `checkoutHistory.json`、`.cyb` 备份 | ⚠️ 待复核 |

`LiveSchemaPinsTests` 保留（回归价值），但注释里的"来自实机"按待复核处理。

## 状态

```
完整套件   1545 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
