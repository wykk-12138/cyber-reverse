import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 264 轮（把 60 多轮的做法收成 `docs/METHOD.md` 七节；未碰功能代码）。

---

## 先读这一份：`docs/METHOD.md`

它把散在各处的纪律收成七节：三种证据分工 / 测量纪律 / 计数纪律 / 改动纪律 / 推进顺序 /
"死窗口"清单 / 内存纪律。**下一轮开工先看它**，比翻 VERDICT 快得多。

## 当前状态

```
缺口 33（real = ceiling = 账本标题）    不可达 UI 类 29
全套 1434 通过（R256 时点）；此后只跑过相关子集
Commit 38.1 GB / 可用 8.05 GB   ← 未重启，正卡在 8 GB 硬线
```

## 下一步（按 `docs/BINDING_BACKLOG.md`）

A 类剩 2：`SmartActionsCreator.UseTemplate`（缺模板源）、`CheckoutView.OpenTracking`（缺运单源）。
B 类 31 全是结构差异 —— 要么抽控件（行控件 8 个），要么保持记录。

**建议**：下一次重启后先跑一次完整套件（确认 1434+ 仍绿），再从 B 类的"抽行控件"开一轮。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
