import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 280 轮（**全套** 1442 通过 / 0 失败 / 2 跳过；13 轮改动全部通过，无残留）。

---

## 验证状态

```
完整套件 Speed!=Slow   1442 通过 / 0 失败 / 2 跳过（21 s）   ← R280 时点，全套
跑完残留               chrome 0 / 临时 profile 0
Commit 39.96 GB / 可用 6.84 GB
```

比 R266（1436）多 6 条：`StoreFlowSourceTests` 3 + `FlowArtifactTests` 3。

## 最大的一笔验证债：`mutation-check`

上次跑是 **R220**（23 条守卫全部 fired），距今约 60 轮。
它会同时拉起全套并逐条改坏代码验证守卫，代价高（R220 实测 ~1 小时、Commit 峰值高）。
**建议重启后专门用一轮跑它**，那时不要同时做别的事。

## 其余口径（供引用时说明）

| 指标 | 值 | 口径 |
|---|---|---|
| 缺口 | 33（real = ceiling） | whole-source + 剥注释 + 排噪 |
| 不可达 UI 类 | 29 | `UnreachedUiTypesTests` |
| 流水线 | 18 条 / 141 步 | A+B 合并去重 |
| 字面量流 | 2 条 | `FlowSource.Literal` |

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
