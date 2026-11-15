import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 273 轮（两种布局合并清点：**18 条流水线 / 141 步**；文档与数据已入库）。

---

## 流量证据：现在有 18 条流水线可对照

| 工具 | 数据 | 规模 |
|---|---|---|
| `tools/flow_dump.py` | `docs/flow_step_sequences.json` | A 布局 69 段 / 320 配对（流水线 15） |
| `tools/row_groups.py` | `docs/row_groups.json` | B 布局保守参数 39 段 / 159 步 |
| `tools/row_groups.py`（宽） | `docs/row_groups_wide.json` | B 布局 ≥2 行/≤0xC0：129 段 / 380 步（流水线 3） |
| `tools/flow_filter.py` | — | 合并去重 → **18 条流水线 / 141 步** |

**过滤判据**：一段里 ≥2 个结账动作名（`AddToCart`/`FindProduct`/`GetCheckout`/`SubmitOrder`/
`SubmitShipping`/`SubmitBilling`/`GetCartCsrf`/`SubmitDiscount`/`EnterRaffle` …）。
没有这条过滤，B 布局会把编辑器的 `Copy/Cut/Paste`、`ConnectionLoop`、`GenerateSensor` 都算进来。

**商店归属**：18 条里只有 9 条能用"独有指纹"定名；其余 9 条只能按步骤形状归档。

**口径提醒**：段内序号不连续 → **"步数" ≠ "序号差"**（John Lewis：15 步，序号 22..37 有跳号）。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 38.96 GB / 可用 7.41 GB   ← 未重启
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
