import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 285 轮（审计 `docs/RESUME.md` 里每个数字 vs 磁盘产物：**7 项全对，0 处漂移**）。

---

## 接手简报的数字已机器校验

| 检查 | 结果 |
|---|---|
| RESUME「缺口 33」 / 棘轮 / 账本标题 | 三处一致 |
| RESUME「1442 通过」 | 与 R280/R281 全套一致 |
| RESUME「24 条 mutation」 | 与工具实况一致 |
| A 布局 69 段 / 宽版 B 129 段 | 与 json 一致 |

**7 项全对，0 处漂移。**（RESUME 里出现的三位以上数字只有 141 / 1442 / 9072，前两个对得上，9072 是历史泄漏目录数。）

## ⚠ 内存：5.72 GB（连续 6 轮低于 8 GB 硬线，未重启）

| 指标 | 值 |
|---|---|
| Commit | 42.17 GB |
| 可用物理 | **5.72 GB** |
| 残留进程 | dotnet / chrome / Cybersole / ida 均 0 |

**能做的轻活已接近用尽**（文档、审计、锚点修复都做完了）。剩下的大件全部需要重启：

1. 全量 `mutation-check`（24 条，12–15 分钟，会同时拉全套）；
2. 结构性工作（抽行控件 / B 类 31 个）；
3. 若要继续 GUI 交叉验证，还要再开原版窗口（更吃内存）。

## 状态

```
完整套件 1442 通过 / 0 失败 / 2 跳过（R280/R281）
mutation anchors 24/24 活；全量未跑
缺口 33（real = ceiling）    不可达 UI 类 29
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
