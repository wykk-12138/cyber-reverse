import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 289 轮：最后两条也验完了 —— **八条流全部字面量可对账**

### 一、Nike：字面量分在**两处**

| 地址 | 内容 |
|---|---|
| `0x03385576` | `StartEcomSession 41, Authorize 42, GetAccessToken 43, FindVariant 44` |
| `0x0338562c` | `CreateBasket 46, SubmitCustomer 48, … GetPaymentMethods 57, SubmitOrder 58`（12 步） |

拼起来 **16 步，名字与顺序与复刻件完全一致**；序号差异只是粘连（`498→49`、`502→50`、`516→51`、`526→52`、`560→56`）。

### 二、John Lewis：字面量 + **lambda 行**

| 地址 | 内容 |
|---|---|
| `0x0338a655` | 17 步：`GetHome 20, WebHandOver 23, SessionHandover 24 … GetStripePaymentIntent 39` |
| `0x0338af47` | `<<FindProduct>g__Available|21_3`、`<AddToCart>b__22_0` —— **正是 R112 当年手推的两步** |

复刻件的 19 步把 `FindProduct(21)`、`AddToCart(22)` 恰好放在 `GetHome(20)` 之后 —— **位置与序号全对**。

### 三、于是：**8 条流全部 `Literal`，endpoint 桶清空**

| 流 | 证据 |
|---|---|
| structure-token-multi | `0x034b14b8` |
| structure-token-single | `0x034b23a5`（R287 改正内容） |
| popmart | `0x0337b9e5` |
| demandware-classic | `0x034ac0f3` |
| demandware-dual | `0x0336f0bd` |
| collectplus-app | `0x033929ec` |
| nike | `0x03385576 + 0x0338562c` |
| johnlewis | `0x0338a655 + 0x0338af47` |

守卫也跟着反过来：`StoreFlowSourceTests` 现在断言 **`endpoint` 为空、`literal` 恰好 8 条**。

### 四、验证

```
Stores 编译                     0 错误
StoreFlowSourceTests + 流程测试   13 通过 / 0 失败
完整套件                         1441 通过 / 0 失败 / 2 跳过（22 s）
```

（条数从 1442 变 1441，是因为我把 `StoreFlowSourceTests` 里两条断言合并成了一条，不是丢了测试。）

### 五、这一轮的一句话

> 八条流从"6 条可信 + 2 条叙述"变成**八条都能逐条对账**，靠的不是新数据，是**把字面量拼起来**。

> **"找不到一条完整的"不等于"没有证据"—— 它可能只是分了两段。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 289 轮（nike/johnlewis 也验完 → **八条流全部 Literal**，每条都有地址；endpoint 桶清空）。

---

## 八条流的字面量地址（全部可逐条对账）

| 流 | 证据地址 |
|---|---|
| structure-token-multi | `0x034b14b8` |
| structure-token-single | `0x034b23a5` |
| popmart | `0x0337b9e5` |
| demandware-classic | `0x034ac0f3` |
| demandware-dual | `0x0336f0bd` |
| collectplus-app | `0x033929ec` |
| nike | `0x03385576 + 0x0338562c`（两条拼接，16 步同序） |
| johnlewis | `0x0338a655 + 0x0338af47`（d__ 行 + lambda 行，19 步同序） |

`StoreFlowSourceTests` 现在断言：**endpoint 为空、literal 恰好 8 条**。

## 验证状态

```
全量 mutation-check   24 / 24 fired（R286）
完整套件              1441 通过 / 0 失败 / 2 跳过（R289；1442→1441 是合并了两条断言）
Commit 15.59 GB / 可用 19.14 GB
```

## 下一步

1. 这八条流的**顺序**已可信，但"哪些序号是助手方法"仍按 R119 规则判；
2. B 类 31 个缺口仍是结构差异（`docs/BINDING_BACKLOG.md`）；
3. 若有新证据源，可再扩 14 条未定名流水线。

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
