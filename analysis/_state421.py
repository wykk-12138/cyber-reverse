import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 421 轮：一张总表揭出两个我漏看的区（Auth 16 / HistoryWindow 9）

### 一、新工具 `tools/copy_audit_report.py` → `docs/COPY_QUEUE.md`

一次跑 19 个区域，输出"键数 / 原文缺失 / 近似错误"三列。它立刻显示：

```
Auth            27 keys   16 missing
HistoryWindow   17 keys    9 missing
Monitor         15 keys    7 missing   ← 无宿主页面
```

**`Auth` 我此前只当它"3 条近似错误"，实际有 16 条原文缺失** —— 因为之前只按"近似"看，没按"缺失"看。

### 二、补的

| 区 | 条数 | 落的类 |
|---|---|---|
| `Auth` | 15 + 1（`Back to login`） | `LoginControl.Copy` |
| `HistoryWindow` | 8 + 1（`Clear History`） | `HistoryWindow.Copy` |

`Auth` 覆盖许可证选择器整套（标题/副标题/空态/`Ending in {0}`/`Active Licenses must be reset via the`）
与登录失败四种错误句；`HistoryWindow` 覆盖四种空态、`Search history`、`Hover over each step…`。

### 三、一次命名冲突

`LoginControl` 里**已经有 `Text` 成员** → `CS0111`。表格取值器改名 `CopyText`，注释写明原因。

```
Auth 16 → 0   HistoryWindow 9 → 0   Monitor 仍 7（无宿主）
copy 测试 12 通过 / 0 失败
```

### 四、这一轮的一句话

> 我不是没查 `Auth`，我是**只查了一种口径**。

> **换个口径重查一遍，比在新区域瞎找更有用。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')
