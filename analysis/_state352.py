import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 352 轮：一次**把文件切坏**的经历，以及它怎么被救回来

### 一、我做错了什么

想删掉 `BuildGeneral` / `BuildManual` 两个方法，用"行号 + 找下一个声明"的脚本切文件。
结果切掉了：

- `TaskDetailsView`（整个类）
- `GroupSummary`（整个类）
- `TaskGroupListView`（整个类）
- `TaskGroupView` 的 `Save` / `Reset`

**一行 `end` 变量算错，四个类就没了。** 而这台机器上没有 git，没有还原点。

### 二、怎么救的

`replica/tools/.mutation-backup/TasksViews.cs` —— **变异测试工具留下的备份**（今天 07:57 的快照）。
复制回来：五个类全在，编译通过（0 错误）。

然后把今天做过的两处改动**重做一遍**：R345（`GroupSummary.StartAll/StopAll`）、
R351（名字在 tab 之上、`Delete`/`Save` 页脚、`DeleteGroup`）。

### 三、代价与结果

```
恢复后   701 行 / 5 个类 / 编译 0 错误
重做     完整套件 1515 通过 / 0 失败 / 2 跳过
丢失     本轮想做的 R352（4 tab）没做成 —— 它正是切坏文件的那一步
```

### 四、这一轮的教训（比任何重构都重要）

1. **`.mutation-backup/` 是我的保险丝** —— 变异测试工具每轮都留一份；这次是它救了四个类。
2. **没有版本控制时，任何"按行号切文件"的操作都是在赌**。正确做法：整段替换（R340 已经学过，又犯）。
3. **切完立刻编译**，不要连着切两处再编译 —— 这次连着切，报错时已经分不清哪一刀切坏的。

> **工具救我一次，是运气；下次要靠"不切文件"而不是"再被救一次"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\METHOD.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''

### §11 没有版本控制时，禁止"按行号切文件"（R352）

这一轮我用"行号 + 下一个声明"的脚本删两个方法，**切掉了四个类**（`TaskDetailsView`、`GroupSummary`、
`TaskGroupListView`、以及 `TaskGroupView.Save/Reset`），现场无 git、无还原点。

救回来靠的是 `tools/.mutation-backup/`（变异测试工具的快照）。

**规则**：

1. 改结构一律**整段/整方法替换**，用前后锚点文本，不用行号；
2. 一次只切一处，**切完立刻编译**；
3. `tools/.mutation-backup/` 是唯一保险，**不要清空它**；
4. 如果非切不可，先手工把整文件复制成 `*.cs.bak` 再动手。
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('METHOD §11 added')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 352 轮（**切坏文件 → 从 `tools/.mutation-backup/` 恢复**；R345/R351 重做完毕，1515 绿）。

---

## 事故与恢复（务必记住）

| 项 | 内容 |
|---|---|
| 事故 | 用"行号切文件"删两个方法，切掉 `TaskDetailsView` / `GroupSummary` / `TaskGroupListView` / `TaskGroupView.Save+Reset` |
| 现场 | 无 git、无还原点 |
| 恢复 | `replica/tools/.mutation-backup/TasksViews.cs`（07:57 快照）复制回来 → 编译 0 错误 |
| 重做 | R345（`GroupSummary.StartAll/StopAll`）、R351（名字在 tab 之上 / `Delete`+`Save` 页脚 / `DeleteGroup`） |
| 结果 | 完整套件 **1515 通过 / 0 失败 / 2 跳过** |
| 未完成 | R352 的 4 tab（正是切坏文件的那一步） |

## 新规矩（`docs/METHOD.md` §11）

1. 改结构**整段替换**，不用行号；
2. 一次只切一处，**切完立刻编译**；
3. **不要清空 `tools/.mutation-backup/`** —— 它是唯一保险；
4. 非切不可时，先手工复制一份 `*.cs.bak`。

## 状态

```
完整套件   1515 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 41（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
