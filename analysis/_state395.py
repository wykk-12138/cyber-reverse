import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 395 轮：Profiles 页文案清零（13 → 0）

```
before  Profiles: 13 values not present
after   Profiles: 27 key/value pairs, 0 values not present
```

补的十三条：右键菜单五条（`Clone Profiles` / `Create Test Profile` / `Open in CSV Editor` /
`Delete Profiles` / `Edit Profiles`）、删除确认三件套、空搜索一句、页脚单复数两条、
选择计数单复数两条。

```
PageCopyTests   13 通过
完整套件        1572 通过 / 0 失败 / 2 跳过
```

### 这一轮的一句话

> 四个页面（Accounts / Proxies / Tasks / Profiles）文案全部清零，**合计 39 条原文回到界面里。**

> **一条原文就是一个界面细节；39 条就是 39 个"看起来像原版"的理由。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 395 轮（Profiles 页文案 13 → 0；四个页面合计 39 条原文补齐）。

---

## 文案缺口：四个区域清零

| 区域 | 条数 | 轮次 |
|---|---|---|
| Accounts | 10 | R392 |
| Proxies | 6 | R393 |
| Tasks | 10 | R394 |
| Profiles | 13 | R395 |

命令：`python tools/locale_text_gap.py <Area>`

**下一批**：TaskGroup 20 / SmartActions 20 / Data 19 / TaskCreator 33 / Settings 240。

## 状态

```
完整套件   1572 通过 / 0 失败 / 2 跳过
绑定缺口   17（名字级）/ 12（类型级）
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
