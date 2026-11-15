import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 270 轮（段→商店：独有指纹绑上 9/69，邻居法 0/69 死；发现"连续段"说法有误）。

---

## 六条流：现在的准确状态

| 结论 | 依据 |
|---|---|
| 段内**顺序**可信 | 段内 `d__` 与 `b__N_M` 同段互证（69 段 / 320 配对） |
| 段内**连续性不可信** | `0x03398963` = `5:CheckRaffleStatus, 68:GenerateVariables` —— 元数据顺序可跳号 |
| 序号 > 200 需复核 | `0x03380d89` 出现 `356:SubmitPayment`（数字粘连的解析产物） |
| 段→商店：**独有指纹** | 绑上 **9 / 69**，看着都对（Shopify 3、Demandware 4、Popmart 1、Nike 0） |
| 段→商店：**邻居字面量** | **0 / 69 —— 死路** |
| 段→商店：John Lewis 锚点 | 未做 |

**「连续段」这个说法已作废**，改为「同一类方法的元数据顺序」——这也解释了 Nike 的 45/47 缺口是助手方法。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 38.8 GB / 可用 7.56 GB   ← 未重启
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
