import io
# 1) ledger: GOAT now uses all 5 evidenced paths
p = r'D:\projects\cyber-reverse\replica\docs\ENDPOINT_LEDGER.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## R328：GOAT 的 5 条有出处路径**全部在用**

| 路径 | 之前 | 现在 |
|---|---|---|
| `/web-api/get-csrf-token` | ✔（R321 兜底） | ✔ |
| `/web-api/v1/login` | ✘ | **✔ 新增 `LoginAsync`** |
| `/web-api/v1/users/send_otp_token` | ✘ | **✔ 新增 `SendOtpAsync`** |
| `/web-api/v1/addresses` | ✘ | **✔ 新增 `GetAddressesAsync` + `EnsureAddressAsync`** |
| `/web-api/v1/billing_infos` | ✘ | **✔ 新增 `GetBillingInfosAsync`** |

**路径有出处、请求体没有** —— 四个方法的注释都写明了这一点，`GoatAccountSurfaceTests` 也盯着。

接入点：`SubmitOrderAsync` 在确认购买前先 `EnsureAddressAsync`（GOAT 的购买以某个地址为键），
拿不到地址就早失败并给出可读原因，而不是让确认请求 4xx 却不解释。

**测试形态说明**：`NetClient` 是 sealed 且方法非虚，flow 的 HTTP 缝无法伪造（不为此引入接口抽象），
所以 `GoatAccountSurfaceTests` 是**源码级断言**（路径仍在、出处分明、body 标 inferred、地址检查已接上），
不是行为测试。这条限制写进测试注释里。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('ledger updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 328 轮（重启后）：GOAT 四端点落地 —— **该店的 5 条有出处路径全部在用**

### 一、先清债

```
mutation-audit      29 锚点 → 发现 1 条死锚（round 164 UI count，R312 把 83 改成 84 时漂了）
                    修好后 29/29
全量 mutation-check  29 / 29 全部 guard fired，restored tree: GREEN
完整套件             1474 通过 / 0 失败 / 2 跳过
```

### 二、然后照施工图实现

`GoatFlow` 新增四个 private 方法（都走 `StoreFlow` 的 `GetAsync`/`PostJsonAsync`，**不加新抽象**）：

| 方法 | 路径 | 证据 |
|---|---|---|
| `LoginAsync` | `POST /web-api/v1/login` | 路径有出处；body `{email,password}` **inferred** |
| `SendOtpAsync` | `POST /web-api/v1/users/send_otp_token` | 路径有出处；body `{email}` **inferred** |
| `GetAddressesAsync` | `GET /web-api/v1/addresses` | 路径有出处，无 body |
| `GetBillingInfosAsync` | `GET /web-api/v1/billing_infos` | 路径有出处，无 body |

接入点：`SubmitOrderAsync` 先 `EnsureAddressAsync`（缺 `goat.addressId` 时取第一条），
拿不到就早失败并给出可读原因。

### 三、测试形态（诚实说明）

`NetClient` 是 **sealed 且方法非虚** → flow 的 HTTP 缝**无法伪造**，而为一个测试引入接口抽象不值得。
所以 `GoatAccountSurfaceTests` 是**源码级断言**（4 条）：路径仍在、出处分明、body 标 inferred、地址检查已接上。
**它是弱于行为测试的，这一点写在测试注释里**，不假装成行为验证。

### 四、验证

```
GoatAccountSurfaceTests   4 通过
完整套件                  1478 通过 / 0 失败 / 2 跳过（22 s）
```

### 五、这一轮的一句话

> 上一轮我把这笔活写成施工图（还修正了虚构的依赖）；这一轮照图施工，**两轮加起来才叫完成**。

> **设计稿救的不是时间，是"重启之后还记得要做什么"。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')
