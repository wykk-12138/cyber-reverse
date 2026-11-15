import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 269 轮（**找到解开六条流序号缺口的路**：段内归堆 → 69 段 / 320 条"方法+序号"配对）。

---

## 六条流的序号缺口：路找到了，数据也捞出来了

`docs/FLOW_SEQUENCES.md` + `docs/flow_step_sequences.json` + `tools/flow_dump.py`

**做法**：找"同时含 `d__` 连续段 **且** 含同批方法 `b__N_M` lambda 表"的字面量 —— 段内两表互相印证序号。

```
69 段     320 条"方法 + 序号"配对
样例 0x03385140: 8:Login 9:FindProduct 10:AddToCart 11:GetCheckout 12:SubmitShipping 13:SubmitRate
样例 0x0336dea7: 33:GetCsrf 34:GetCheckout 35:GetCheckoutHtml 36:AddToCart 37:AddToCart2
                 38:SubmitDiscount 39:SubmitShipping 40:SubmitOrder   ← 一条完整结账流水线
```

**为什么与 R268 不矛盾**：R268 的"序号不可推断"针对**全库归堆**（平均 5.58 个候选主人）；
**段内归堆**只有一类的声明顺序，可信。R121 的 John Lewis 就是这么解开的。

## 下一步：把段绑定到商店

三条候选：① 段邻近字面量 ② 方法名指纹（`GetLotteryForm`→Popmart、`Get6Js`→Nike）③ 用已解开的 John Lewis 段当锚点。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling = 账本标题）    不可达 UI 类 29
Commit 38.83 GB / 可用 7.56 GB   ← 未重启
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
