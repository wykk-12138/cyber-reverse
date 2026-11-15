import io
p = r'D:\projects\cyber-reverse\replica\docs\ENDPOINT_LEDGER.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## R296：请求头也查了一遍 —— 16 个里 13 有证据，1 个改了名，2 个是内部诊断

用同样的方法查复刻件里的**头名字面量**（16 个）：

| 结果 | 数量 | 说明 |
|---|---|---|
| 池子里逐字命中 | **13** | 直接用 |
| 内部诊断（**不是发出去的**） | 2 | `X-Cyb-Transport` / `X-Cyb-Alpn` —— 写在 `result.Headers[...]` 上，是**响应侧记录**"这条请求走了哪条 TLS/ALPN"，不进请求 |
| 改名的 | 1 | `X-CSRF-Token` |

### 那一处改名（真缺陷，已改）

- 复刻件原来发 `X-CSRF-Token`；
- 池子里**没有**这个拼写，只有小写 `x-xsrf-token`；
- 已把 `StoreFlow.cs` 里发送的名字改成 **`x-xsrf-token`**（两处），
  `GoatFlow.cs` 的文档注释也从 "X-CSRF-TOKEN" 对齐到同一拼写。

> GOAT 的 cookie 名仍是 `XSRF-TOKEN`（那是 **cookie**，不是请求头），保持不变。

### 教训

`X-Cyb-*` 那两个名字看着吓人（像是自己编的、会暴露指纹），查了才发现**它们挂在响应对象上**，
根本不发出去。**"头形状的字符串" ≠ "请求头"** —— 判方向比判存在更重要。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('ENDPOINT_LEDGER updated with the header section')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 296 轮：查请求头 —— 16 个里 13 有证据，**发现并修掉一处真缺陷**

### 一、三个"没命中"逐个查方向（这一步才是关键）

| 字面量 | 方向 | 判定 |
|---|---|---|
| `X-Cyb-Transport` / `X-Cyb-Alpn` | 写在 `result.Headers[...]` 上 —— **响应侧记录**（这条请求走了哪条 TLS / ALPN） | **不发出去**，不是指纹问题 |
| `X-CSRF-Token` | 写在 `c.Session.Headers[...]` —— **真的会发** | **缺陷** |

### 二、缺陷是什么

池子里没有 `X-CSRF-Token`，只有小写 **`x-xsrf-token`**。
复刻件却用大写拼写发送 —— 名字不对，服务器可能直接忽略这个头。

已改：`StoreFlow.cs` 两处改为 `x-xsrf-token`；`GoatFlow.cs` 的注释从 "X-CSRF-TOKEN" 对齐到同一拼写。
（GOAT 的 cookie 名 `XSRF-TOKEN` 是 **cookie**，不是请求头，保持不变。）

### 三、验证

```
Stores 编译     0 错误
完整套件       1452 通过 / 0 失败 / 2 跳过（21 s）
```

### 四、这一轮的一句话

> 三个"没命中"里，两个是**吓人的假警报**，一个是**真错**。

> **"名字长得像头" 不等于 "会被发出去" —— 判方向比判存在重要。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 296 轮（请求头审计：16 个里 13 有证据；`X-CSRF-Token` → **`x-xsrf-token`** 真缺陷已修）。

---

## 请求头审计（新账）

| 结果 | 数量 |
|---|---|
| 池子逐字命中 | 13 |
| 内部诊断（不发） | 2 —— `X-Cyb-Transport` / `X-Cyb-Alpn`，写在响应对象上 |
| **改名（已修）** | 1 —— `X-CSRF-Token` → **`x-xsrf-token`**（池里只有小写形态） |

`GoatFlow.cs` 的注释已对齐；cookie `XSRF-TOKEN` 保持不变（那是 cookie）。

**教训：`头形状的字符串 ≠ 请求头`，判方向比判存在重要。**

## 验证状态

```
完整套件   1452 通过 / 0 失败 / 2 跳过（R296）
Commit     19.71 GB / 可用 16.7 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
