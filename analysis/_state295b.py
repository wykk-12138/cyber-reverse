import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 295 轮（九个候选步骤 **9/9 全真** + 碰撞者也全真；顺带纠正我上一轮的 0 命中误判）。

---

## 候选步骤（`CandidateSteps`）已验证

| 项 | 结果 |
|---|---|
| 9 条候选在池子里 | **9 / 9**（形态 `<Name>d__N`） |
| 它们标注的"同序号碰撞者" | 全部可在池子里找到 |
| 是否出现在任何 flow 里 | **一个都没有**（候选 ≠ 步骤） |
| 守卫 | `CandidateStepsDigestTests`（3 条：9 条序号、不得进 flow、告示不得删） |

**我上一轮的错误**：报"GraphQL 名在池子里 0 命中" —— 是用裸名字去比，而池里是 `<Name>d__N`。

## 验证状态

```
完整套件   1452 通过 / 0 失败 / 2 跳过（R295）
mutation   24/24 fired（R286）
Commit     19.71 GB / 可用 16.73 GB
```

## 账本现状（可以引用的三张）

| 账本 | 数字 |
|---|---|
| 端点 | 89 = 44 逐字 + 23 片段 + 3 URL 包含 + **18 无证据（已标推断）** |
| 八条流 | 8/8 字面量可对账 + 指纹测试 |
| 错误目录 | 13/13 标题 + 13/13 详情逐字命中 |

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
