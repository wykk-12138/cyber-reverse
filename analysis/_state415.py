import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 415 轮：`Checkout` / `Release` 收口，`Monitor` 无处可放

### 一、补的

| 键 | 原文 | 落在 |
|---|---|---|
| `Checkout.OrderFormat` | `Order {0}` | `CheckoutView.Copy` |
| `Checkout.OutForDelivery` | `Out for delivery` | 同上 |
| `Checkout.ScheduledDelivery` | `Scheduled Delivery` | 同上（第一次漏了，补） |
| `Release.AddTasks` | `Add Tasks` | 同上 |
| `Release.Empty.CheckBack` | `Check back later` | 同上 |

结果：`Checkout` 3 → **0**，`Release` 2 → **0**。

### 二、`Monitor` 的 7 条**没有地方放**

复刻件里**没有 `MonitorView` 这个类** —— `Monitor.*` 的 7 条文案（`Monitor Feed`、`Search feed`、
`Available sizes`、`No results`…）属于一个**尚未实现的页面**。

所以这 7 条**不补常量**：没有宿主类的常量，等于把文案藏进一个没人引用的地方。
它们继续留在 `tools/locale_text_gap.py Monitor` 的输出里，作为"这个页面还没做"的证据。

### 三、验证

```
四套 copy 测试   49 通过 / 0 失败
```

### 四、这一轮的一句话

> 同样是"缺 7 条文案"，`Checkout` 的是**待接线**，`Monitor` 的是**没有页面**。

> **同一个数字背后，可能是两种完全不同的工作。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('；Settings 区仍未清点', '；Checkout/Release 已清；**Monitor 页面未实现（7 条文案无宿主）**；Settings 区仍未清点')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
