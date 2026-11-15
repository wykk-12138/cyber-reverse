import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 393 轮：Proxies 页文案清零（6 → 0）

```
before  Proxies: 6 values not present
after   Proxies: 0
```

补的六条：删除确认三件套（标题/正文/按钮）、`{0} Proxies Loaded`、`{0} PROXIES SELECTED` / `{0} PROXY SELECTED`，
外加 `Loaded(n)` 与 `SelectionCaption(n)` 两个单复数辅助。

```
页面文案        AccountCopyTests(7) + PageCopyTests(5) 全绿
完整套件        1559 通过 / 0 失败 / 2 跳过
```

### 这一轮的一句话

> `locale_text_gap.py` 把"界面文案"变成了一个**可以归零的清单**。

> **能归零的清单，才是任务；不能归零的，只是感慨。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 393 轮（Proxies 页文案 6 → 0；套件 1559）。

---

## 文案缺口进度（`python tools/locale_text_gap.py <Area>`）

| 区域 | 缺 | 状态 |
|---|---|---|
| Accounts | 10 | ✅ 已补（R392） |
| Proxies | 6 | ✅ 已补（R393） |
| Tasks | 10 | 待补 |
| Profiles / Settings / TaskCreator / SmartActions / TaskGroup / Data / … | 未清点 | 待补 |

## 状态

```
完整套件   1559 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
