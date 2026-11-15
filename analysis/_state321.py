import io
p = r'D:\projects\cyber-reverse\replica\docs\ENDPOINT_LEDGER.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## R321：GOAT 的 CSRF 端点——**这一次是"账本反过来帮了我"**

查 `/v1/buys` 有没有出处时，顺手看了 GOAT 在池子里到底有什么：

```
web-api                                  7 处
  https://www.goat.com/web-api/get-csrf-token     ← 有出处
web-api/v1/buys                          0 处
web-api/v1/countries                     0 处
buy_bar_data / product_variants          0 处
```

于是两件事同时成立：

1. `/v1/buys` 仍然**无出处**（账本判定不变，GOAT 的 `/web-api/` 前缀有出处，具体路径没有）；
2. 但复刻件取 CSRF token 的方式（cookie `XSRF-TOKEN` 或 meta 标签）**没有用上那个有出处的端点** ——
   已在 `GetHomeAsync` 里加**兜底**：cookie/meta 都拿不到时，GET `/web-api/get-csrf-token` 取回。

**兜底而不是替换**：cookie/meta 是浏览器会话本来就给的，端点只是页面没给时的退路。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('ledger updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 321 轮：从"查无出处"里挖出一个**有出处却没被用上的端点**

### 一、缘起

为了给 10 条"真实发送但无出处"的端点找证据，我去看 GOAT 在池子里到底有什么：

```
web-api                                    7 处
  https://www.goat.com/web-api/get-csrf-token      ← 有出处
web-api/v1/buys                            0 处
buy_bar_data / product_variants            0 处
```

### 二、两件事同时成立

1. `/v1/buys` 仍**无出处**（账本判定不变）；
2. 但复刻件取 CSRF 的方式（cookie `XSRF-TOKEN` / meta 标签）**没有用上那个有出处的端点**。

### 三、改动（兜底，不是替换）

`GoatFlow.GetHomeAsync`：

```csharp
if (string.IsNullOrEmpty(c.Session.CsrfToken))
{
    var token = await GetAsync(c, WebApi(c, "/get-csrf-token"), "goat-csrf", ct);
    if (token is { IsSuccess: true } && !string.IsNullOrWhiteSpace(token.Body))
        c.Session.CsrfToken = token.Body.Trim().Trim('"');
}
```

cookie/meta 是浏览器会话本来就给的，端点只是**页面没给时的退路** —— 所以是兜底。

### 四、验证

```
Cybersole.Stores 编译   0 错误
```

全套未跑（内存 4.6 GB）。

### 五、这一轮的一句话

> 这一轮的收获不是"找到 bug"，而是**账本自己长出了线索**：
> 为了证明一条路径"没有出处"，我把整个 GOAT 的有出处清单拉了出来 —— 里面有一条它没在用。

> **"查无出处"的副产品，往往是"有出处却没用"。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 321 轮（GOAT：把池子里有出处的 `/web-api/get-csrf-token` 加为 CSRF 兜底；全套未跑）。

---

## 本轮改动

`GoatFlow.GetHomeAsync`：cookie `XSRF-TOKEN` 与 meta 标签都拿不到 CSRF token 时，
GET **`/web-api/get-csrf-token`**（池子里有出处：`https://www.goat.com/web-api/get-csrf-token`）。

**兜底不是替换** —— 浏览器会话本来就给 cookie/meta，端点只是页面没给时的退路。

## 账本更新

`docs/ENDPOINT_LEDGER.md` 新增 R321 一节：GOAT 的 `/web-api/` 前缀有出处，但
`/web-api/v1/buys`、`/web-api/v1/countries`、`buy_bar_data`、`product_variants` **仍 0 处** → 那几条判定不变。

## 状态

```
Stores 编译   0 错误
完整套件      **未跑**（内存 4.56 GB）
缺口          17
Commit        44.1 GB / 可用 4.56 GB   ← 需重启后跑全套
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
