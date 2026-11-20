"""Log R1285: the captcha provider's read-only members."""

import io

B = """
## R1285 —— `CaptchaProvider.Type` / `BalanceSupported` 的**只读契约**对齐（优先级②）

### 一、取证（descriptor 原文，两处互相印证）

`Cybersole.CaptchaProviders.CaptchaProvider` 的成员块（`1432158BC`…`143215DF5` 与 `14363E0A0`…`14363E3EC`）：

| 成员 | Getter | Setter |
|---|---|---|
| `Type` | ✅ `1432159DC` | **无** |
| `BalanceSupported` | ✅ `143215D50` | **无** |
| `Name` · `ApiKey` · `Balance` · `Count` · `Concurrency` · `Priority` · `IsFetchingBalance` | ✅ | ✅ |

**⇒ `Type` 与 `BalanceSupported` 在镜像里是只读的**；其余可写。这个不对称是镜像自己的，不是我们的选择。

### 二、顺带取证到的两处（下一轮的料，先记下来）

- `14330480F`：`RecaptchaV3" HCaptchaInvisible& RecaptchaEnterprise& CloudflareTurnstile` —— 这是**挑战变体**域，
  与复刻件的 `CaptchaKind{ReCaptcha,HCaptcha,Turnstile,Geetest,Question}` **不是同一层**（变体 4 个 vs 家族 5 个）。
- `14339635D`：`TurnstileSiteKey` + 实值 `0x4AAAAAACm-_-PQVKerNsuH` + `KlaviyoCompanyId` —— 某店铺配置里的字段块。
- `1432258DF` / `143225A55` / `143225B68`：`get_HCaptchaSpoof`、`<HCaptchaSpoof>k__BackingField` ⇒ `HCaptchaSpoof`
  是**某类型上的 bool 属性**（同块还有 `Castle`、`TrustDeviceGen`、`TrustDeviceBotD`），不是独立类型。

### 三、改了什么

1. `CaptchaProviderConfig.Type` / `.BalanceSupported` → **`init`**（构造时可设、之后不可改）；
2. `CaptchaProviderCreatorView` 的保存逻辑重写：**只有新建行**用 `init` 定 `Type`，
   编辑既有行**保留原来源**；Type 下拉在编辑模式 **`IsEnabled = false`**（原版没有那个 setter，UI 也就不该给）。
3. 新测 `CaptchaProviderTypeContractTests`（3 条）：两个成员带 `IsExternalInit` modreq；
   七个可写成员**没有**该 modreq；新建仍能选来源且默认 `humanpresence`。

### 四、验证

`Captcha*` **43/43**；全量 **2468 通过 / 0 失败 / 2 跳过 / 2470**。

**为什么用 modreq 而不是"没有 setter"**：C# 的 `init` 在反射里**仍有** get-setter 方法，
标记它的是返回参数上的 `IsExternalInit` modreq——那正是编译器拒绝构造后赋值的东西，也是镜像"缺 setter"的等价表达。
"""

V = """
---

## 第 1285 轮：captcha provider 只读契约对齐（Type / BalanceSupported）

- 镜像 `Type`、`BalanceSupported` 只有 getter（1432159DC / 143215D50，均无 Setter）；其余七成员双访问器。
- 复刻件改为 `init`；编辑模态框不再改既有行的来源，Type 下拉在编辑时禁用。
- 新测 3 条（`IsExternalInit` modreq 判据）；`Captcha*` 43/43；全量 **2468/0/2/2470**。
- 顺带取到下一轮的证：变体域（4 值）、`TurnstileSiteKey` 实值、`HCaptchaSpoof` 是 bool 属性。
"""

H = """
## R1285 —— 只读契约对齐（Type/BalanceSupported）；全量 2468/0/2/2470

Observation：
- `Type`/`BalanceSupported` 无 Setter（两处 descriptor 互证）；其余七成员可写。
- 变体域 `RecaptchaV3|HCaptchaInvisible|RecaptchaEnterprise|CloudflareTurnstile`（14330480F）与复刻 `CaptchaKind` 不同层。
- `HCaptchaSpoof` 是 bool 属性（backing field 证据），不是独立类型。

改：字段 `init` + 模态框只在新建时定来源 + 3 条契约测试。全量 2468/0/2/2470。

下轮：变体层（`RecaptchaEnterprise` / `CloudflareTurnstile` / `HCaptchaInvisible`）落地——先取协议端点，再写驱动。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
