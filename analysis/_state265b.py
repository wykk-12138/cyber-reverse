import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 265 轮（用 locale 作第三个来源确认 `Platform` 三值不可得；未改代码）。

---

## `Attributes.Platform` 三值：**三个独立来源否证**

| 来源 | 结论 |
|---|---|
| 字符串池（R225） | 只有成员名，**没有值** |
| GUI（R242，两次复现） | Store 下拉点不开，**切不了平台** |
| **locale（R265）** | **`Platform.*` 零键**；`TaskCreator.Size/Quantity` 是字段名不是能力 |

推论：那三个布尔控制的是**校验/行为**而不是显隐，所以既不进文案、也不可从界面观察。
**以后不要再试。** 已写进 `docs/BINDING_BACKLOG.md`。

## 行控件家族（`FilterRow` / `ProfileCsvRow` / `ActionRow`）判为结构差异

locale 里没有它们的文案键（`SmartActions.Filters.*` 只有计数，没有 `Passed`/`ValueText`）→
说明这些成员是**纯内部状态**，复刻件的行是即时求值、没有"先 Passed 再显示"的两步。

## 状态

```
缺口 33（real = ceiling = 账本标题）      不可达 UI 类 29
Commit 38.26 GB / 可用 7.85 GB   ← 仍低于 8 GB 硬线，未重启
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
