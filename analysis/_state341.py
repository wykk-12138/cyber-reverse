import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 341 轮：`ExtraFields` 不是编的 —— 池子里有五把钥匙

### 一、上一轮留下的疑点

R318 依 locale key `Settings.Webhook.ExtraFields` 给了 `IWebhook.ExtraFields`；
R340 在实机把 New Webhook 三个状态走完，**没有任何额外字段出现** —— 看上去像是我编的。

### 二、把 locale 全拉出来看

```
Settings.Webhook.Title / Subtitle / EmptySubtitle / NewWebhook
Settings.Webhook.Events
Settings.Webhook.Event.{Checkouts, Declines, PayPal, PaymentRequests, SmartActions}
Settings.Webhook.ExtraFields                      ← 区块标题
Settings.Webhook.Extra.{Email, Price, CheckoutProxy, ProxyGroup}   ← 四个字段名
Settings.WebhookTest.Title / Message
```

英文值也是现成的：`"Settings.Webhook.Extra.Price": "Price"`、`CheckoutProxy → "Checkout Proxy"` 等。

**所以 `ExtraFields` 是真的**，只是**它的界面不是 New Webhook 弹窗** —— 我的"未证实"应该改成
"界面位置未知"，而不是"可能是编的"。

### 三、落地

`WebhookView.ExtraFieldChoices = { "Email", "Price", "Checkout Proxy", "Proxy Group" }` + 注释写明证据来源
与"位置未知"；`WebhookExtraFieldsTests`（2 条）钉住四个标签，并验证 `Webhook` 确实以键值袋形式承载它们。

### 四、验证

```
WebhookExtraFieldsTests   2 通过
完整套件                  1502 通过 / 0 失败 / 2 跳过
```

### 五、这一轮的一句话

> 上一轮我说"未见即可能不实"；这一轮把 locale 摊开，看到它是**真的、只是不在我打开的那个弹窗里**。

> **"没看到"要分三种：界面没有、界面在别处、我看错了。上一轮我默认了第一种。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 341 轮（`ExtraFields` 证实为真：5 个 locale 键 + 4 个字段名；界面位置仍未知）。

---

## `ExtraFields` 的结论改了

| 轮次 | 结论 |
|---|---|
| R318 | 依 locale key 加 `IWebhook.ExtraFields` |
| R340 | 实机 New Webhook 三态走完，**没看到** → 标"界面未证实" |
| **R341** | locale 摊开：`Settings.Webhook.ExtraFields` + `Extra.{Email, Price, CheckoutProxy, ProxyGroup}`（值就是英文标签）→ **属性是真的，界面位置未知** |

落地：`WebhookView.ExtraFieldChoices`（4 个标签，附证据注释）+ `WebhookExtraFieldsTests`（2 条）。

## 状态

```
完整套件   1502 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
