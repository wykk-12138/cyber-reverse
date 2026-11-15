import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 416 轮：`Settings` 族一次收 54 条（→ 1，且该 1 条池中截断）—— 但**没编译通过验证**

### 一、做了什么

`python tools/locale_text_gap.py Settings` 报 **54** 个值不在源码里（不是 240 —— 240 是"未引用键"的口径）。
用脚本从池子直接生成表格：

```
missing 54 | capturable 52 | excluded 2（值被截断 / 超长）
+ 手补 2 条 delete-confirm（含 \\n 的整句）
= 54
```

结果：

```
Settings: 242 key/value pairs, 1 values not present
   Settings.General.MonitorConcurrency.Tooltip   ← 池中截断（以反斜杠结尾）
```

### 二、**没验证**

写完表格后，`Cybersole.Ui` 编译**曾通过**（exit=0，缺 2 条 delete-confirm 时）。
补完那 2 条再跑测试时：

```
Commit 93.79 / 94.03 GB      available 1.38 GB
error MSB6006: "csc.dll" 已退出，代码为 -1073741502
```

**编译器在内存耗尽时崩溃**（0xC0000142 = DLL 初始化失败）。所以本轮最后一处改动
**未经编译验证**。

### 三、下一轮第一件事

内存恢复后先 `dotnet build` 一次，确认那两条字符串的语法（`\\n` 转义）没问题，
再跑 copy 测试。

### 四、这一轮的一句话

> 这一轮我写下了"已收 54 条"和"但没验证"两句话，并让它们并列。

> **不确定的进度，必须和不进度一样明确。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('## 当前状态')
head = '''## ⚠ 未验证的改动（下一轮先做这个）

R416 给 `SettingsShell.Copy` 补了最后两条 `Sizes/Stores.DeleteConfirm.Message`，
**编译未通过验证**（当时 `available 1.38 GB`，`csc.dll` 崩溃）。恢复后先：

```
dotnet build src/Cybersole.Ui/Cybersole.Ui.csproj -c Debug
dotnet test --filter "FullyQualifiedName~TaskCreatorCopyTests"
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE flagged')
