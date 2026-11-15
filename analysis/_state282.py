import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 282 轮（`--limit 5` 深冒烟：5 条守卫全 fired、树还原 GREEN；**发现 mutation 总数是 24 不是 23**）。

---

## mutation-check 的准确状态

```
总数 24 条（R220 记录的 "23" 已过时 —— 期间加过一条）
已冒烟 5 / 24，全部 fired，restored tree: GREEN
剩 19 条，留到重启后一把跑完（预计 12–15 分钟）
```

已验过的 5 条覆盖：round 136 三条重放路由（contentWindow / createElement / 裸全局）、
round 137 `speechSynthesis`、round 138 单版本读取。

**教训**：连"要跑多少条"这种数字也会变 → **它必须由工具打印（`running N of M`），不能靠我记。**

## 内存：**6.1 GB，已低于硬线，请重启**

跑 5 条把可用从 6.52 压到 6.10 → 全量 24 条在这个水位上不该跑。

## 重启后的执行顺序（照这个来）

1. `python tools/mutation-check.py`（全量 24 条，12–15 分钟，期间不要做别的）；
2. 全套 `dotnet test --filter "Speed!=Slow"`（确认 1442+）；
3. 之后才考虑结构性工作（抽行控件 / B 类 31 个），或按 `docs/BINDING_BACKLOG.md` 继续。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
