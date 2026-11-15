import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 268 轮（给"序号不能推断归属"补量化证据：平均每序号 5.58 个候选主人；未编译）。

---

## 六条流的序号缺口：**为什么解不开**（量化版）

| 数字 | 值 |
|---|---|
| 带 lambda 归属的序号 | 153 |
| 其中"至少两个不同方法共用"的 | **88（57%）** |
| 每个序号平均挂多少不同方法 | **5.58** |
| 最挤：序号 34 | 23 个不同方法 |

**结论**：单序号推断不是"不够准"，是**在构造上无效**。

**闭包类也救不了**：序号 29 上是 `AddAutoCartPreload`（lambda）而 `d__29` 是 `EditLine` —— 两类不同源。

**唯一通的路**（R121 已验证）：同一类里 `d__` 连续段 **与该类的 lambda 表共处同一字面量**。
John Lewis 是这么解开的；六条流里其余几条还没走完。

## 状态

```
完整套件 1436 通过 / 0 失败 / 2 跳过（R266 全套）
缺口 33（real = ceiling）    不可达 UI 类 29
Commit 38.84 GB / 可用 7.56 GB   ← 未重启，低于 8 GB 硬线
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
