import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 281 轮（`mutation-check` 加 `--limit/--only` 并冒烟通过：守卫会响、还原后 1442 绿）。

---

## `mutation-check`：现在有廉价入口，成本也量出来了

```bash
python tools/mutation-check.py --limit 1        # 冒烟：1 条 ≈ 1–2 分钟
python tools/mutation-check.py --only "round 136"   # 按名字挑
python tools/mutation-check.py                  # 全量 23 条 ≈ 15–20 分钟
```

**冒烟结果（`--limit 1`）**：`running 1 of 23` → guard fired → 还原 → **全套 1442 绿（23 s）**。
所以：工具能跑、守卫会响、还原干净。

**代价**：单条约 40 s（改 + 增量编译 + 过滤跑）；末尾还原验证是一次全套（23 s）。
→ **全量约 15–20 分钟**（R220 记的"1 小时"偏保守，可能含 IDA/GUI 并行）。

## 未完成（债务清单）

| 项 | 状态 |
|---|---|
| 完整套件 | 绿（1442，R280/R281 两次） |
| `mutation-check` 全量 23 条 | **未跑**（内存 6.84 GB，留到重启后一把跑完） |
| 缺口 33 / 不可达 29 | 已记账（`docs/BINDING_BACKLOG.md`） |

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
