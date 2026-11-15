import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 242 轮（用 GUI 找 `Attributes.Platform` 的证据 → **验不了**：下拉点不开，二次复现 R77 的限制）。

---

## `Attributes.Platform` 三个值：**证据到此为止**

- 池子里有成员名（`InputType` / `QuantitySupport` / `QuantityAutoAdjustSupport`），**没有值**；
- GUI 路线也不通：**Store 下拉点不开**，`list_windows` 始终只有主窗口（与 R77 在另一处下拉上的观察一致，本轮二次复现）；
- 所以它不是"待办"，是**已知不可得**。要动它必须先有新证据源（例如运行时反射/内存读）。

## 本轮量到的两件事（原版任务创建器 Setup 标签）

```
Store [Select store]        Size [Select sizes]
Monitor Input [Enter input]
Profiles [Select profile]   Proxies [Select proxy group]
Scheduled Start             Quantity (per profile) [1] [−][+]
                        [Create Task]
```

1. `Quantity` 带 **−/+ 步进器** —— 对上 `CreateInputModel.Plus/Minus`：不是属性，是步进按钮。
2. **Store 为空时 `Size` 与 `Quantity` 已可见** → 这两个输入不按平台能力控制显隐；
   `QuantitySupport` 更可能控制校验/行为。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
