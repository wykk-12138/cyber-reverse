import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 430 轮：文档体检（不是"看着像维护了"，而是逐项核对）

### 一、清掉的垃圾

`D:\\projects\\cyber-reverse\\VERDICT.md` 是 **0 字节**的空文件（真正的编年史在 `replica/docs/VERDICT.md`，1.17 MB）。
两处同名会让人误读，**已删**。

### 二、抓到三处陈旧数字（当前状态类文档，不是历史记录）

| 文件 | 旧 | 新 | 说明 |
|---|---|---|---|
| `BINDING_BACKLOG.md` | 11 个类型 | **10** | 并把表格重写成当前的 10 项（`ProfileCreatorView` 清零、`MonitorView` 的五个绑定补入） |
| `RESUME.md` | `**11 个类型**`、`1575 通过` | **10 个类型**、**1606 通过** | 交接文件里的数字必须等于度量输出 |
| `SESSION_STATE.md` | "12 个类型级缺口里…" | **10** | 同一句话里的第二个数字也错 |

`VERDICT.md` 里同样有旧数字，但那是**按轮次排列的编年史**，改它等于篡改历史 —— 不动。

### 三、顺带补上漏掉的一条文案

总表（`copy_audit_report.py`）一直显示 `Accounts 1 missing`，而分区工具显示 0 —— 因为
`Accounts.Group.DeleteConfirm.MessageFormat` 里的 `the {0} account group` 在源码中"近似存在"。

```
Are you sure you want to delete the {0} account group?\\nYou cannot undo this action.
```

已加 `AccountView.DeleteGroupConfirmFormat` + `DeleteGroupConfirm(group)`，并加断言。
**19 个区现在只剩 5 条"池中截断"**（ProfileCsv 2 / Utilities 2 / Settings 1）。

### 四、验证

```
文档类守卫（Docs/Parity/Guide/Summary/Ratchet）  65 通过 / 0 失败
PageCopyTests + LiveSchemaPins                  33 通过 / 0 失败
```

### 五、这一轮的一句话

> "文档维护好了吗"这个问题，只有拿工具复算才有答案 —— 我一扫就到三处陈旧数字和一条漏掉的文案。

> **文档的"看起来对"，和"数字等于度量输出"，是两件事。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('文案       19 个区已清；剩 5 条池中截断（ProfileCsv 2 / Utilities 2 / Settings 1）',
                '文案       19 个区全清；剩 5 条池中截断（ProfileCsv 2 / Utilities 2 / Settings 1）')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
