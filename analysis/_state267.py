import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 267 轮（`X-Shopify-Generated-Cart-Token` 判为"静态不可判定"，写明需运行时抓包；未编译）。

---

## 待办清单的三种状态（现在都写清了）

| 状态 | 例子 |
|---|---|
| **可做** | A 类 2 个（`UseTemplate` / `OpenTracking`），都缺数据源 |
| **不可得** | `Attributes.Platform` 三值（池子/界面/locale 三源否证） |
| **静态不可判定** | `X-Shopify-Generated-Cart-Token` 的方向 —— 头名在镜像里只出现 1 次、与标准响应头排在一起；**要定方向必须运行时抓包** |

**教训**：把待办写成"不可判定 + 需要什么才能判定"，比让它一直挂着有用 —— 否则下次又从零查一遍。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 时点，全套）
缺口 33（real = ceiling = 账本标题）   不可达 UI 类 29
Commit 38.9 GB / 可用 7.35 GB   ← 低于 8 GB 硬线，未重启
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
