import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R333：Billing（Profiles）页实机对照 —— 零差异；三个列表页的列头**变成数据**

### Billing 实机结构

```
PROFILE GROUPS   [Custom ⌄]
🔍 Search groups
Group 1                                          0
[New Group +]

[📁] Group 1 [⚙]                        [CSV Editor]  🔍 Search profiles
No Profiles Loaded
[☐]  Profile⇅  Email⇅  Card Holder⇅  Card⇅  Shipping⇅   [Add Profile][Clear Profiles]
```

复刻件 `BillingView.Columns = { "Profile", "Email", "Card Holder", "Card", "Shipping" }` —— **同序同字**；
`CSV Editor` 按钮位置也对（在搜索框**左边**，同在表头右侧一格）。

### 把三页的列头变成"数据"而不是"五次调用"

之前三个网格都是逐行写 `HeaderButton("Site", …)`。现在改成：

```csharp
internal static readonly string[] Headers = { "Site", "Product", "Profile", "Proxies", "Status" };
private  static readonly TaskColumn[] HeaderColumns = { Site, Product, Profile, Proxies, Status };
for (var i = 0; i < Headers.Length; i++)
    grid.Children.Add(HeaderButton(Headers[i], HeaderColumns[i], i + 1));
```

Proxies 同样处理。**好处**：列头顺序成为可测试的数组，而不再埋在五次调用里。

### 新守卫

`ListPageColumnsTests`（3 条）：Tasks / Proxies / Billing 三页列头的文字与顺序，
与实机读数逐一相等（`TasksPageTests` 原本只钉了 Tasks，现在三页同置一处便于对照）。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE updated')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 333 轮：Billing 页实机对照 + 三页列头从"五次调用"变成"一个数组"

### 一、Billing 页：零差异

实机 `[CSV Editor] [Search profiles]` 同在表头右侧，列头 `Profile / Email / Card Holder / Card / Shipping`；
复刻件 `BillingView.Columns` **同序同字**，`CSV Editor` 也在搜索框左边。

### 二、顺手做的一处结构化

三个网格原先各自写五/四次 `HeaderButton("…")`。现在：

```csharp
internal static readonly string[] Headers = { … };
for (var i = 0; i < Headers.Length; i++) … HeaderButton(Headers[i], HeaderColumns[i], i + 1);
```

**列头顺序从"埋在一串调用里"变成"一个能被断言比对的数组"** —— 这正是本轮实机读数能变成测试的前提。

### 三、新守卫

`ListPageColumnsTests`（3 条）：三页列头文字与顺序逐一等于实机读数
（`TasksPageTests` 原来只钉了 Tasks）。

### 四、验证

```
ListPageColumnsTests + TasksPageTests   14 通过
完整套件                                1485 通过 / 0 失败 / 2 跳过
```

### 五、这一轮的一句话

> 前几轮我把"实机看到的文字"写进文档；这一轮把它写进了**数组**，再由测试盯着。

> **文档记的是"我看过"，数组保证的是"它不会变"。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')

p3 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t3 = io.open(p3, encoding='utf-8').read()
lf = t3.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 333 轮（Billing 页零差异；三页列头改为数组 + `ListPageColumnsTests`；全套 1485 绿）。

---

## 实机已核对五页

| 页 | 结论 |
|---|---|
| Settings（导航/General/Payment） | 一致；`Max Open` 条件行 |
| Tasks | 零差异 |
| Proxies | 零差异 |
| Accounts | 零差异；14 平台名逐字同序（已钉测试） |
| Billing（Profiles） | 零差异；列头同序、`CSV Editor` 位置对 |

## 本轮结构化改动

`TaskGrid.Headers` / `ProxyGrid.Headers` 成为**数组**（列头顺序可断言），
新增 `ListPageColumnsTests` 三页同置对照。

## 状态

```
完整套件   1485 通过 / 0 失败 / 2 跳过
缺口       17（real = ceiling）
mutation   29 / 29 fired
Commit     17.4 GB / 可用 17.8 GB
```

'''
out = lf[:i] + head + lf[i:]
io.open(p3, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
