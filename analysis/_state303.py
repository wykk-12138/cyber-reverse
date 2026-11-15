import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 303 轮：`CheckoutView.OpenTracking` —— **A 类清零**（缺口 32 → 31），顺手拆掉一个装饰按钮

### 一、先看那个按钮原来是什么

```csharp
UiKit.Button("Open tracking", () => Status("Opening tracking URL.")),
```

**写一句话，什么也不做。** 而且它早就被列进 `DeadButtonTests` 的账本里 —— 是"已知的假按钮"。

### 二、为什么以前做不了

`CheckoutView` 操作的是 `CheckoutEvent`，而 `CheckoutEvent` 里**根本没有 URL 字段**：

```csharp
record CheckoutEvent(Store, Product, Size, Price, Success, OrderNumber, Profile)
```

但下游早就有：`CheckoutOutcome.TrackingUrl`（`Stores.Abstractions.cs:73`）——
Shopify 流程会从 `order_status_url` 里取。**断在"没传上来"这一段。**

### 三、补上的链路（三段）

```
CheckoutOutcome.TrackingUrl  →  CheckoutEvent.TrackingUrl  →  Launcher.LaunchUriAsync
   (流程已有)                     (R303 新增, init)            (R303 实现)
```

`OpenTracking()` 的行为：没有选中项 → 提示；没有 URL → 提示"这个结账没有运单链接"；
平台不能开链接 → 提示；否则打开并回报。**四种情况都有话可说，不再是一句空话。**

### 四、守卫跟着动了两处

- `DeadButtonTests`：把 `Open tracking` 从"已知假按钮"里删掉，并写明它为什么不再假；
- `BindingGapRatchetTests`：ceiling **32 → 31**，账本标题改成「当前 31 = 0 可做 + 31 结构（A 类清零）」。

### 五、又见那个老 flake

第一次全套跑红了一条 **`GlobalSurfaceTests.NoNameIsAdvertisedWithoutAProperty`**，
单独跑通过、再跑全套也通过 —— 与 R236 记录的是同一个 flake（第二次出现）。
**按纪律：不改测试，只记录。** 现在有两次记录，下次再出现就该查它依赖了什么全局状态。

### 六、验证

```
绑定缺口    32 → **31**（A 类清零）
完整套件    1458 通过 / 0 失败 / 2 跳过（21 s，第二次跑）
```

### 七、这一轮的一句话

> A 类清零的意义不是"缺口变小 1"，而是**"缺数据源"这个借口被证伪了一条** ——
> 数据一直在下游，只是没接到界面上。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 303 轮（`OpenTracking` 打通三段链路，缺口 **32 → 31**，**A 类清零**）。

---

## 缺口 31 = 0 可做 + 31 结构

| 项 | 值 |
|---|---|
| `MaxRealGap` / 账本标题 | **31** |
| A 类（类存在、只差成员） | **0** —— 清零 |
| `AnalyticsView.OpenRelease` | 不可得 |
| B 类结构差异 | 31 |

**`OpenTracking` 的三段链路**：`CheckoutOutcome.TrackingUrl`（流程已有）→ `CheckoutEvent.TrackingUrl`（R303 新增）
→ `Launcher.LaunchUriAsync`（R303 实现）。原按钮只写一句"Opening tracking URL."。

## 复发 flake（第二次）

`GlobalSurfaceTests.NoNameIsAdvertisedWithoutAProperty`：全套第一次跑红、单独跑绿、再跑全套绿。
与 R236 是同一个。**按纪律不改测试，只记录**；若第三次出现，需查它依赖的全局状态。

## 验证状态

```
完整套件   1458 通过 / 0 失败 / 2 跳过（R303）
mutation   24/24 fired（R286）
Commit     26.9 GB / 可用 13 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
