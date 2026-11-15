import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 392 轮：新增"文案缺口"度量，一个页面补回十条

### 一、新工具：`tools/locale_text_gap.py`

它不问"这个键被引用了吗"，而问**"这句原文在复刻件里出现过吗"**：

```
python tools/locale_text_gap.py Accounts
    Accounts: 35 key/value pairs, 10 values not present in the source
```

（另有 `tools/locale_coverage.py` 给出全局覆盖：**582 个 locale 键，复刻件引用 99 个 = 17%**。）

### 二、Accounts 页缺的十条（全部来自 locale）

| 常量 | 原文 |
|---|---|
| `DeleteConfirmTitleFormat` | `Delete {0} accounts?` |
| `DeleteConfirmMessageFormat` | `Are you sure you want to delete {0} accounts?\\nYou cannot undo this action.` |
| `DeleteConfirmActionFormat` | `Delete ({0}) accounts` |
| `EditPasswordTitleFormat` | `Edit ({0})` |
| `NoResultsSubtitle` | `There are no accounts matching your search` |
| `DeleteGroupLabel` | `Delete Group` |
| `GroupsLoadedFormat` / `GroupsLoadedOne` | `{0} Account Groups Loaded` / `1 Account Group Loaded` |
| `SelectedManyFormat` / `SelectedOneFormat` | `{0} ACCOUNTS SELECTED` / `{0} ACCOUNT SELECTED` |

配两个按单复数切换的辅助方法（`GroupsLoaded(n)` / `SelectionCaption(n)`）。

### 三、验证

```
AccountCopyTests   7 通过（单复数各一组 Theory）
完整套件           1554 通过 / 0 失败 / 2 跳过
```

### 四、这一轮的一句话

> 我一直用"绑定缺口"和"类型缺口"衡量进度，**但界面上的文字从来没被度量过。**

> **能度量的东西才会被修好。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 392 轮（新增文案缺口工具；Accounts 页补回十条原文；套件 1554）。

---

## 现在有四条度量线

| 度量 | 工具 | 现状 |
|---|---|---|
| 名字级绑定缺口 | `tools/bind_diff.py` | 17 |
| 类型级绑定缺口 | `tools/bind_scope.py` | 12 |
| 成员形状差异（已接受） | `tools/shape_audit.py` | 272 |
| **文案缺口** | **`tools/locale_text_gap.py` / `locale_coverage.py`** | **582 键中引用 99（17%）** |

文案缺口是新的一层：按键统计 17%，但**按原文匹配**能直接列出"这句界面文字复刻件里没有"。

## 状态

```
完整套件   1554 通过 / 0 失败 / 2 跳过
缺口       17 / 12 /（文案未全面清点）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
