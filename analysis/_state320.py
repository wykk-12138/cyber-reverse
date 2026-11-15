import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 320 轮：接手简报更新到当前数字，并把"审计脚本"改成跟着棘轮走（不编译）

### 一、简报早就过期了

`docs/RESUME.md` 还写着「1446 通过 / 缺口 33 / 不可达 29（97 个中）」——
而现在是 **1474 / 17 / 31（104 个中）**。三处数字全错。

已更正，并补上新文档的入口：`B_CLASS_DECISIONS.md`、三份 `CONTROL_DESIGN_*.md`。

### 二、审计脚本本身也有硬编码

`_resume_audit.py` 里把「33」「1442」写死了 —— **它检查的是旧世界**。
改成**跟着棘轮走**：

```python
('RESUME states the ratchet value', ratchet in resume)
('backlog title matches ratchet', ('当前 ' + ratchet + ' =') in backlog)
```

这样以后缺口再变，审计脚本不用改。

### 三、验证

```
审计脚本   7 项全 OK，mismatches: none
文档守卫   SummaryBlock / ParityDoc / DocsConsistency   20 通过 / 0 失败（--no-build）
```

### 四、这一轮的一句话

> 上一轮我刚写"简报要机器校验"，这一轮就发现**校验脚本自己写死了旧数字**。

> **校验工具也要被校验 —— 否则它只是在确认"我上次写的世界"还在不在。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 320 轮（`RESUME.md` 同步到 1474 / 17 / 104；审计脚本改成跟着棘轮走）。

---

## 接手简报现在是准的

```
完整套件 1474 通过 / 0 失败 / 2 跳过    缺口 17（real = ceiling）    UI 类 104 / 不可达 31
```

`_resume_audit.py` 不再硬编码数字，改为读 `MaxRealGap` 与账本标题比较 —— 以后缺口变化不用改脚本。

**教训**：校验工具也要被校验，否则它只确认"上次写的世界"还在不在。

## 状态

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R319）
缺口       17
Commit     43.6 GB / 可用 5.1 GB   ← 低于硬线
```

## 下一步（重启后）

1. 全量 `mutation-check`（29 条）；
2. 功能深度：10 条真实发送但无出处的端点（`docs/ENDPOINT_LEDGER.md`）。

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
