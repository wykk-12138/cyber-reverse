### 稳定性检查抓出两个「一直红着的测试」

上轮的判断是「这个环境有间歇性失败」。连跑三次 `Speed=Slow`，结果推翻了这个判断：

```
run 1: 失败 2，通过 248
run 2: 失败 2，通过 248
run 3: 失败 2，通过 248
```

**不是间歇性，是稳定的 2 个失败。**

### 它们为什么一直没被发现

因为 `verify.ps1` 和日常开发都用 `--filter "Speed!=Slow"`，**这两个测试带 `Trait("Speed","Slow")`**。

它们从被加进来那天起就没跑过——直到这轮手工跑全量。

### 失败一：`nike-gs` 漏在白名单外

```
Assert.Equal() Failure: Values differ
Expected: Error
Actual:   Blocked
```

`ModuleRobustnessTests` 检查「不可达主机不能看起来像有货」，并给有风控门的模块单独断言：

```csharp
if (id is "nike" or "superswipe")
    Assert.True(result.Status is MonitorStatus.Blocked or MonitorStatus.Captcha, ...);
```

**`nike-gs` 继承 `NikeFlow`，所以它也走 Kasada 门，也返回 `Blocked`** —— 但不在白名单里，
走了默认断言 `Assert.Equal(MonitorStatus.Error, ...)`。

**修**：白名单加 `nike-gs`。

### 失败二：Shopify 清单没跟上三次改注册

```
in registry, not in probe list: footpatrol.co.uk, footpatrol.com, jbhifi.com.au,
                                size.co.uk, sizeofficial.com, ...
in probe list, not in registry: bstn.com, converse.com
```

`ShopifyWrappingTests` 有一份 `WrappedHosts` 数组，用来对照 registry 里实际是
`ShopifyFlow` 的模块。**它落后了四次改动**：

| 变化 | 轮次 | 清单是否更新 |
|---|---|---|
| `footpatrol` / `size` → Shopify | R47 | ❌ |
| `jbhifi` → Shopify | R57 | ❌ |
| `supreme` → Shopify | R76 | ❌ |
| `bstn` → `BstnFlow` | R48 | ❌（该删没删） |
| `converse` → Demandware | R46 | ❌（该删没删） |

**修完**：加 8 个域名，删 2 个。

### 两次修正之后

```
Speed=Slow（排除可达性扫描）：  250 通过 / 0 失败
Speed!=Slow（日常）：           541 通过 / 0 失败
```

**全量 250 个里没有一个失败。**

### 这次检查的真正收获

不是修了两个测试，是发现了**一个系统性盲区**：

> **`verify.ps1` 只跑 `Speed!=Slow`。带 `Speed=Slow` 的测试有 250 个，从来没进过门禁。**

那 250 个包括：

- `LiveContractTests`（9 个，R70 加的，只有 `-Live` 才跑）
- `ShopifyWrappingTests`（真去探测 31 个站点的 `/cart.js`）
- `ModuleRobustnessTests`（61 个模块 × 两个场景）
- `ModuleReachabilityTests`（61 个域名的可达性）
- 各种性能测试

**它们的价值恰恰在于「打真实站点」，而它们从来没被自动跑过。**

### 一个可以加的门禁

`verify.ps1 -Live` 已经跑 `LiveContractTests`。可以再扩一层：

```powershell
pwsh -File tools\verify.ps1 -Full    # 加上全部 250 个 Slow 测试（约 3 分钟）
```

**但那 3 分钟里有 1.5 分钟是 `ShopifyWrappingTests` 打 31 个站点**——那和 CI 的频率不匹配。

**更实际的做法**：在 README 里写明「`Speed=Slow` 的 250 个测试需要手动跑，建议每次改动注册表后跑一次」。

---

### 一个反思

**我在 R70 加了 `LiveContractTests` 并说「现在那八个结论各有一条 live 断言守着」——
但那些断言从来没在常规流程里跑过。**

这一轮才发现，同样的情况发生在**所有** `Speed=Slow` 测试上。

**「有测试」和「测试在跑」是两件事。** 后者才叫验证。

---
