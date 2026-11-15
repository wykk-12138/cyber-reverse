import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 391 轮：原版备份里的嵌套对象也对上了（`aycdInbox` + 解算器条目）

### 一、两处原本靠猜的地方

```
accounts.aycdInbox   { apiKey, templateId, appGroup, timeoutSeconds, enabled }   ← 是对象，不是列表
solvers[].solvers[]  { proxy, filter, account, settings }
```

复刻件的 `AycdInbox` 五个字段**完全一致**；`Solver` 的四个持久化字段也一致。

### 二、一个需要分清的概念

绑定表说有 `Solver.Name / View / Reload`，而原版备份里**不写**这三个。
这不矛盾：**绑定 ≠ 持久化**。和 `UsagePeriod`（持久化但不绑）正好相反的一对。

| 成员 | 绑定 | 持久化 |
|---|---|---|
| `Solver.Name/View/Reload` | ✅ | ❌ |
| `TaskGroup.UsagePeriod` / `ProxyGroup.UsagePeriod` | ❌ | ✅ |

两条证据都保留，各自按来源使用。

### 三、验证

```
完整套件   1547 通过 / 0 失败 / 2 跳过
LiveSchemaPinsTests  6 个用例全绿
```

### 四、这一轮的一句话

> 这一轮没有发现新缺陷 —— 但把"靠猜对上"变成了"被证据钉住"。**没有缺陷也是一种结论。**

> **验证的价值不只在抓错，还在把"我记得对"换成"有据可查"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 391 轮（原版备份的嵌套对象钉住：`AycdInbox` 5 字段、`Solver` 4 持久化字段）。

---

## 绑定 ≠ 持久化（两个方向都已确认）

| 成员 | 绑定表 | 原版备份 |
|---|---|---|
| `Solver.Name` / `View` / `Reload` | ✅ | ❌ |
| `TaskGroup.UsagePeriod` / `ProxyGroup.UsagePeriod` | ❌ | ✅ |

**判断"该不该有"时，先问是哪一层在说话。**

## 状态

```
完整套件   1547 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
LiveSchemaPinsTests  6 个用例
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
