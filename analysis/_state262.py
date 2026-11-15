import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 262 轮（账本更新到 36 = 4+32；新增"账本↔棘轮"交叉校验测试；未跑全套）。

---

## 棘轮当前值：`MaxRealGap = 36`，账本标题必须与它相同（有测试盯着）

`BindingGapRatchetTests.TheBacklogDocQuotesTheCeiling` 断言 `docs/BINDING_BACKLOG.md` 标题里的
"当前 NN =" 等于 ceiling —— **两份记录互相校验**，任何一边单独改动都会红。

## 缺口 36 全貌（`docs/BINDING_BACKLOG.md`）

| 类 | 数 | 内容 |
|---|---|---|
| A | 4 | `SmartActionsCreator.DeleteParam`（可做）/ `UseTemplate`（缺模板源）/ `CheckoutView.OpenTracking`（缺运单源）/ `AnalyticsView.OpenRelease`（**不可得**） |
| B | 32 | 行控件 8 / `Platform` 3（不可得）/ `ComboBoxEdit` 2 / `Store` 2 / `CreateInputModel` 2（有 GUI 证据）/ 本地化扩展 2 / 其余各 1 |

## 内存

可用 **8.13 GB**、未重启。本轮只跑了 1 个测试类（3 条），**没有跑全套**。
下轮若还要动代码，建议先重启。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
