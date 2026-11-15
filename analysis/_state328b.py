import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 328 轮（重启后：mutation 29/29 fired、全套 1478 绿、**GOAT 四端点落地**）。

---

## 这一轮清掉的两笔债 + 一件新活

| 项 | 结果 |
|---|---|
| mutation 锚点审计 | 29 → 发现 1 条死锚（round 164，R312 把 `83` 改 `84` 时漂的）→ 修好 **29/29** |
| 全量 mutation-check | **29 / 29 全部 fired**，restored tree: GREEN |
| 完整套件 | **1478 通过 / 0 失败 / 2 跳过**（22 s） |
| GOAT 四端点 | `LoginAsync` / `SendOtpAsync` / `GetAddressesAsync` / `GetBillingInfosAsync` 全部落地 |

## GOAT 现在是"5 条有出处路径全在用"

`/web-api/{get-csrf-token, v1/login, v1/users/send_otp_token, v1/addresses, v1/billing_infos}`

- **路径有出处、请求体没有** → 四个方法的注释与 `GoatAccountSurfaceTests` 都盯着这条区分；
- 接入点：`SubmitOrderAsync` 先 `EnsureAddressAsync`。

## 测试形态限制（记住）

`NetClient` 是 **sealed 且方法非虚** → flow 的 HTTP 缝**无法伪造**。
`GoatAccountSurfaceTests` 因此是**源码级断言**，弱于行为测试，已在注释里写明。

## 状态

```
完整套件   1478 通过 / 0 失败 / 2 跳过
缺口       17（绑定表口径，real = ceiling）
mutation   29 / 29 fired
Commit     15.9 GB / 可用 18.9 GB   ← 健康
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
