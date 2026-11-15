import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 421 轮：一张总表揭出两个我漏看的区（Auth 16 / HistoryWindow 9）

### 一、新工具 `tools/copy_audit_report.py` → `docs/COPY_QUEUE.md`

一次跑 19 个区域，三列：**键数 / 原文缺失 / 近似错误**。它立刻显示我之前没看见的东西：

```
Auth            27 keys   16 missing      ← 我此前只当它"3 条近似错误"
HistoryWindow   17 keys    9 missing
Monitor         15 keys    7 missing      ← 无宿主页面
```

**"没查缺失"和"查了没问题"是两件事。**

### 二、补的

| 区 | 条数 | 落的类 |
|---|---|---|
| `Auth` | 15 + 1（`Back to login`） | `LoginControl.Copy` |
| `HistoryWindow` | 8 + 1（`Clear History`） | `HistoryWindow.Copy` |

`Auth` 覆盖许可证选择器整套与登录四种失败句；`HistoryWindow` 覆盖四种空态、`Search history`、悬停提示。

### 三、两处踩坑

1. `LoginControl` 里**已有 `Text` 成员** → `CS0111`，表格取值器改名 `CopyText` 并注明原因；
2. 总表工具第一版**每个区域开子进程**（38 个），在 1 GB 内存下直接 `E_OUTOFMEMORY`（`8007000e`）；
   改成**单进程遍历一次源码树**后几秒完成。

```
Auth 16 → 0   HistoryWindow 9 → 0   Monitor 仍 7（无宿主）
copy 测试 12 通过 / 0 失败
```

### 四、这一轮的一句话

> 工具崩了不是小事：**它一崩，我就少了唯一能看见"全貌"的那张表。**

> **度量工具本身也要经得起跑。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| `locale_near_miss.py` | "几乎对但不相等"的文案（需人工三分类） |',
                '| `locale_near_miss.py` | "几乎对但不相等"的文案（需人工三分类） |\n| `copy_audit_report.py` | 一张总表：19 区的键数 / 缺失 / 近似（写入 `docs/COPY_QUEUE.md`） |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
