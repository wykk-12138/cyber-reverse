import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 332 轮（Proxies + Accounts 实机对照零差异；**14 个平台名钉成测试**；全套 1482 绿）。

---

## 实机已核对四页（`docs/GUI_BASELINE.md` R329–R332）

| 页 | 结论 |
|---|---|
| Settings（导航 / General / Payment） | 一致；`Max Open` 是**条件行**（结掉 R77 悬案） |
| Tasks | 零差异（四色药丸色值与顺序、列头、六键 3+3） |
| Proxies | 零差异（含 `Custom` 排序、两个流量计数、gear） |
| Accounts | 零差异；**14 个平台名逐字同序** → 已加 `AccountStoreListTests` 钉住 |

## 新守卫

`AccountStoreListTests`：14 个名字 + 顺序全等；`Nike/Nike GS`、`Demandware/Demandware (Funko)`
两对必须互异（只差后缀、最容易在重构里被合并）。

## 状态

```
完整套件   1482 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     17.4 GB / 可用 17.8 GB
```

## 下一步候选

Billing 页实机对照；或 Home 页的 Releases 轮播；或回到功能侧继续补有出处的端点。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
