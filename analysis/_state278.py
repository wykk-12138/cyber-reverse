import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 278 轮（机器对账：账本/棘轮/三个 json 全部一致；R269–R277 的四条教训并入 METHOD.md）。

---

## 文档一致性：第一次**机器对账**

| 检查 | 结果 |
|---|---|
| 账本标题「当前 33」 vs `MaxRealGap` | 33 = 33 ✅ |
| `flow_step_sequences.json` | 69 段 ✅ |
| `row_groups.json` / `_wide.json` | 39 / 129 段 ✅ |
| 「18 条」「141 步」 | 两份文档说法一致 ✅ |

对账脚本思路：读文档 + 读 json + 比数字（`analysis/_docaudit.py` 可重跑）。

## METHOD.md 新增四条

1. 同一个东西可能有两种存法（A/B 布局）→ 判"不通"前先确认试全了形态；
2. 一张表可能混着两类证据（literal/endpoint）→ `Flow.Source`，默认取更弱者；
3. 子集家族会让"同时命中"像矛盾 → 先想"同族第三个"；
4. 数字粘连是常态 → 序号 >200 复核；"步数"≠"序号差"。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 39.15 GB / 可用 7.34 GB   ← 未重启
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
