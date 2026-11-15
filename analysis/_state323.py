import io
p = r'D:\projects\cyber-reverse\replica\docs\ENDPOINT_LEDGER.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## R323：把"有出处但没被用上"的路径列出来（每个商店一张）

方法是 R321 顺出来的：**为了证明某条路径没出处，先把该商店在池子里有出处的清单拉全**。

### GOAT（`www.goat.com`，5 条有出处）

| 有出处的路径 | 复刻件用了吗 |
|---|---|
| `/web-api/get-csrf-token` | ✔ R321 加了兜底 |
| `/web-api/v1/addresses` | **✘** |
| `/web-api/v1/billing_infos` | **✘** |
| `/web-api/v1/login` | **✘** |
| `/web-api/v1/users/send_otp_token` | **✘** |

复刻件的 GOAT 用的是 `/v1/buys`、`/v1/buys/{id}`、`/v1/product_variants/buy_bar_data` —— **这三条都无出处**。

**含义**：GOAT 的"登录 / 地址 / 账单信息"这三块在原版里是有明确端点的，
而复刻件根本没建模它们 —— 这是**功能缺口**，不只是"路径没出处"。

### Farfetch / Magento / Scheels

- `farfetch.com/api` 在池子里 **0 处** → Farfetch 那 4 条无出处路径，连"该域名下有出处的路径"都不存在；
- `magento` 关键字 **0 处** → Magento 相关的 3 条同样无从对照（Magento 是自建站，域名各不相同）；
- `preorder` 只有 **Nike 的 `partner_cart_preorder`** 和 purpledotprice 两条，与 `/api/preorder/entry` 无关。

### 于是 10 条无出处端点分两类

| 类 | 条数 | 说明 |
|---|---|---|
| **同店有出处清单可用** | 4（GOAT 那 4 条未用的） | 可以照着做功能，不是"编的" |
| **店里没有任何出处** | 10 | Farfetch 4 / Magento 3 / PopMart 1 / Retail 1 / StoreFlow 1 |

**下一步**：优先做 GOAT 的 `addresses` / `billing_infos`（提交订单时需要），
而 `/api/beast` 那类"店里零出处"的保持标 `inferred` 不动。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('ledger: evidenced-but-unused section added')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 323 轮：把"有出处但没被用上"的路径逐店列出来（不编译）

### 一、方法来自 R321

**为了证明某条路径没出处，先把该商店在池子里有出处的清单拉全** —— 副产品往往更有价值。

### 二、GOAT：5 条有出处，只有 1 条在用

| 有出处 | 复刻件 |
|---|---|
| `/web-api/get-csrf-token` | ✔（R321 兜底） |
| `/web-api/v1/addresses` | **✘** |
| `/web-api/v1/billing_infos` | **✘** |
| `/web-api/v1/login` | **✘** |
| `/web-api/v1/users/send_otp_token` | **✘** |

而复刻件实际用的 `/v1/buys`、`/v1/buys/{id}`、`/v1/product_variants/buy_bar_data` **三条都无出处**。

**这不只是"路径没出处"，是功能缺口**：GOAT 的登录 / 地址 / 账单信息在原版有明确端点，
复刻件根本没建模。

### 三、其它店：连"有出处清单"都没有

- `farfetch.com/api` **0 处**；`magento` **0 处**；`preorder` 只有 Nike 的 `partner_cart_preorder`（与 `/api/preorder/entry` 无关）。

### 四、于是 10 条无出处端点分成两类

| 类 | 条数 | 处理 |
|---|---|---|
| 同店有出处清单可用 | 4（GOAT 未用的那 4 条） | 可以照着做**功能**，不是编的 |
| 店里零出处 | 10 | 保持 `inferred`，不再深挖 |

### 五、这一轮没有编译

可用内存 4.51 GB。

### 六、这一轮的一句话

> 账本原本只回答"这条路径有没有出处"；这一轮它开始回答**"这个商店本该有什么，我还缺什么"**。

> **审计做到深处，产出的是路线图，不是清单。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 323 轮（"有出处但没被用上"逐店列出：GOAT 有 5 条、只用 1 条 → 是**功能缺口**）。

---

## 新的功能路线图（`docs/ENDPOINT_LEDGER.md` R323 节）

**GOAT**：池子里 5 条有出处，复刻件只用 1 条（R321 的 `get-csrf-token`）：

| 缺的 | 用途 |
|---|---|
| `/web-api/v1/login` | 账号登录 |
| `/web-api/v1/users/send_otp_token` | OTP |
| `/web-api/v1/addresses` | 收货地址 |
| `/web-api/v1/billing_infos` | 账单信息 |

而复刻件实际用的 `/v1/buys`、`/v1/buys/{id}`、`buy_bar_data` **三条都无出处**。

**Farfetch / Magento / Scheels**：池子里连"该店的有出处清单"都没有（`farfetch.com/api` 0 处、`magento` 0 处）。

## 状态

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R322）
缺口       17
Commit     44.5 GB / 可用 4.51 GB   ← 低于硬线
```

## 下一步（重启后）

1. 全量 `mutation-check`（29 条）；
2. GOAT 功能补齐：`login` / `send_otp_token` / `addresses` / `billing_infos`（都有出处）。

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
