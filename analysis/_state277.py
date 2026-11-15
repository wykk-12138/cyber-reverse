import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 277 轮（结掉"待复核"项：`0x03388fd2` 是 A 布局段、属 structure-token 家族第三片段）。

---

## 待复核项已清零

`0x03388fd2`：**A 布局**的段（上一轮我在 B 布局文件里找，当然找不到）。

```
11:FindProductFlow 12:GetCheckout 13:GetShippingRate 140:SubmitShipping
150:GetStructureToken 16:CreateTransaction 17:SubmitPayment 18:ProcessPayment
```

命中 `structure-token-multi` 8/15、`structure-token-single` 7/12 —— **同族子集**，不是矛盾。
顺带印证 R270 的"大序号是数字粘连"警告（这里出现 `140`/`150`）。

## 流程序号线的最终账（R269–R277）

| 项 | 值 |
|---|---|
| 布局 A（合并式） | 69 段 / 320 配对（流水线 15） |
| 布局 B（分行式） | 39 段（保守）/ 129 段（宽） |
| 合并去重流水线 | **18 条 / 141 步** |
| 被证实的字面量流 | **2 条**（`structure-token-multi` 15/15、`-single` 12/12）→ `FlowSource.Literal` |
| 其余复刻件流 6 条 | `FlowSource.Endpoint`（默认） |
| 恢复流水线归属 | 2 条定名 + 14 条属未建模商店（需外部知识） |

**这条线到此为止**，除非有新的证据源。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 39.14 GB / 可用 7.31 GB   ← 未重启
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
