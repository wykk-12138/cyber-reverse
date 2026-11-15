import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 404 轮：`BINDING_BACKLOG.md` 早已乱码，重写了一份

### 一、发现

打开账本准备更新类型级数字，看到的是：

```
# 缁戝畾缂哄彛宸ヤ綔璐︽湰锛堝綋鍓?17 = 0 鍙仛 + 17 缁撴瀯...
```

整份文件是**乱码**（早期脚本用非 UTF-8 写出）。内容也已过时：`TaskView` 还列 6 项、
`GroupSummary` 还写"三个语义未定"，而它们早都落地了。

### 二、重写

新文件按当前事实写：

| 段 | 内容 |
|---|---|
| 名字级缺口 | 17（口径与 `BindingGapRatchetTests` 一致） |
| 类型级缺口 | **11 个类型**，逐条写"为什么还没做" |
| 已清零的类型 | 13 行，带轮次 |
| 不可得 | 5 条（三源否证） |
| 纪律 | "有名字 ≠ 知道它做什么" |

### 三、验证

```
BindingGapRatchetTests   3 通过（含 TheBacklogDocQuotesTheCeiling：文档与天花板必须同为 17）
```

### 四、这一轮的一句话

> 这份文档是"接下来该干什么"的唯一清单，而它已经乱码 + 过时 —— **等于没有清单。**

> **账本烂了，进度就散了。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| `bind_diff.py` | 名字级绑定缺口 |',
                '| `bind_diff.py` | 名字级绑定缺口 |\n| `backlog_report.py` | 重算账本数字 |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
