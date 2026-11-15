import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 394 轮：Tasks 页文案清零（10 → 0）

```
before  Tasks: 10 values not present
after   Tasks: 40 key/value pairs, 0 values not present
```

补的十条：右键菜单两条（`Copy URL` / `Move tasks to`）、删除确认三件套、空搜索一句、
`Multiple Products ({0})`、`{0} Selected`、`{0} TASKS SELECTED` / `{0} TASK SELECTED`。

三个按数量切换的辅助：`ProductsCaption` / `SelectionCaption` / `GridSelected`。

```
PageCopyTests   9 通过
完整套件        1565 通过 / 0 失败 / 2 跳过
```

### 这一轮的一句话

> 三个页面（Accounts / Proxies / Tasks）现在文案全部清零 —— **这是第一次有"归零"的区域。**

> **把一个大目标拆成能归零的小清单，进度才看得见。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 394 轮（Tasks 页文案 10 → 0；三个页面文案已清零；套件 1565）。

---

## 文案缺口：已清零的三个区域

| 区域 | 结果 |
|---|---|
| Accounts | 0（R392，10 条） |
| Proxies | 0（R393，6 条） |
| Tasks | 0（R394，10 条） |

命令：`python tools/locale_text_gap.py <Area>`

**下一批**：Profiles 26 / TaskGroup 20 / SmartActions 20 / Data 19 / TaskCreator 33 / Settings 240。

## 状态

```
完整套件   1565 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
