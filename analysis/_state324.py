import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 324 轮：GOAT 账号四端点的设计稿（不编译）

### 一、证据与现状对照

池子里 GOAT 有 5 条 `/web-api/...`，复刻件只用 1 条。而 `GoatFlow` 的步骤只有
`GetHome → FindProduct → FindVariant → ScrapeVariantAvailability → AddToCart → GetCart → GetCheckout → SubmitOrder`
—— **没有登录、没有 OTP、没有地址/账单**。也就是说 GOAT 现在是"游客结账"，
而原版显然有账号体系。

### 二、设计里的关键判断

1. **不塞进 `IStoreModule`** —— 它的契约只有 `Monitor / Checkout / CreateChallenge`（`Stores.Abstractions.cs:95`），
   登录不属于结账流程；
2. 新建 `GoatAccountApi` 四个方法（Login / SendOtp / GetAddresses / GetBillingInfos），
   复用流程已有的 HTTP 通道；
3. **路径有出处，请求体没有** —— 请求体字段名按名字直译并在注释里标 `inferred`；
   **这两件事不能混为一谈**；
4. 最小接入点：`SubmitOrderAsync` 缺 `goat.addressId` 时调 `GetAddressesAsync` 取第一条；
   登录/OTP **只提供能力，不自动触发**（属于任务编排层）。

### 三、预测：缺口数字**不变**

这四条路径不在绑定表里（绑定表只管 UI 成员），所以 `MaxRealGap` 不动 ——
**明确写下来，避免下一轮误把 ceiling 改小。**

### 四、这一轮没有编译

可用内存 4.58 GB。

### 五、这一轮的一句话

> 这是第一次为"**功能缺口**"（而不是"绑定缺口"）写设计稿。

> **绑定表能告诉我界面缺什么；它告诉不了我流程缺什么 —— 那要靠池子里的路径清单。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 324 轮（GOAT 账号四端点设计稿：`docs/CONTROL_DESIGN_GoatAccount.md`；未编译）。

---

## 下一个可执行任务（功能缺口，不是绑定缺口）

`docs/CONTROL_DESIGN_GoatAccount.md`：

- 新建 `GoatAccountApi`：`LoginAsync` / `SendOtpAsync` / `GetAddressesAsync` / `GetBillingInfosAsync`；
- **不进 `IStoreModule`**（它只有 `Monitor / Checkout / CreateChallenge`）；
- **路径有出处、请求体没有** → 请求体字段名标 `inferred`；
- 最小接入：`SubmitOrderAsync` 缺 `goat.addressId` 时取地址；
- 5 条验收 + `GoatAccountApiTests`（假 `HttpCaller`，不联网）；
- **缺口数字不变**（这四条不在绑定表里）。

## 状态

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R322）
缺口       17（绑定表口径）
Commit     44.4 GB / 可用 4.58 GB   ← 低于硬线
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
