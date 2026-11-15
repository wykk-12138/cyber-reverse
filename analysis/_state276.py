import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 276 轮（用复刻件当字典找归属 → 否证；18 条里 2 条被证实、14 条属未建模商店）。

---

## 流程序号这条线的收益已吃干（R269–R276 收束）

| 结论 | 状态 |
|---|---|
| 两种布局（A 合并式 69 段 / B 分行式 129 段） | 已提取、已入库、有工具 |
| 18 条流水线 / 141 步 | `docs/flow_step_sequences.json` + `row_groups_wide.json` + `tools/flow_filter.py` |
| `structure-token-multi`(15/15) / `-single`(12/12) | **被证实是字面量派生** → `FlowSource.Literal` + 守门测试 |
| 其余 6 条复刻件流 | 端点派生（`FlowSource.Endpoint`，默认值） |
| 14 条恢复流水线 | **复刻件未建模的商店**，归属需外部知识 |

**待复核**：`0x03388fd2` 报"命中 StoreFlowSteps 8 个"但未能在宽版里重新定位 —— 不当结论用。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套；R275 起为子集）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 39.26 GB / 可用 7.19 GB   ← 未重启
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
