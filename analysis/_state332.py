import io
p = r'D:\projects\cyber-reverse\replica\docs\GUI_BASELINE.md'
t = io.open(p, encoding='utf-8').read()
add = '''

---

## R332：Proxies 页与 Accounts 页 —— 实机对照，并把商店清单**钉成测试**

### Proxies（零差异）

```
PROXY GROUPS   [Custom ⌄]
🔍 Search groups
Group 1                                                          0
[New Group +]

[📁] Group 1 [⚙]                      ● 0 B current download   ● 0 B current upload
No Proxies Loaded
[☐]  IP⇅  Port⇅  Username⇅  Status⇅        [Add Proxies] [Clear All] [More]
```

复刻件逐项有：`PROXY GROUPS`、`Custom`（六种排序之一，默认选中）、`Search groups`、
分组列表、`New Group`、`No Proxies Loaded`、两个流量计数（`current download` / `current upload`）、
`Add Proxies` / `Clear All` / `More`、列头 `IP/Port/Username/Status` 同序、空态两行。

### Accounts（零差异，且**顺序逐字相同**）

实机左栏 14 个平台，自上而下：

```
Nike · Nike GS · Shopify · Footlocker (Asia) · Farfetch · Demandware (Funko)
Demandware · Magento · Casio · HBX · Popmart · Goat · Scheels · Warhammer
```

复刻件 `StoreCatalog.Platforms` **逐字相同、顺序相同**（含 `Demandware (Funko)` 与 `Demandware` 并列、
`Footlocker (Asia)` 的括号、`Popmart` 的小写 m）。

其它：`ACCOUNT GROUPS` 标题、搜索框占位是 **"Search stores"**（注意不是 `Search groups`）、
`New Group +`、空态 `Add a group to get started` —— 全部一致。

### 新增守卫

`AccountStoreListTests`（2 条）：把 14 个名字与顺序**钉死**，并断言
`Nike/Nike GS`、`Demandware/Demandware (Funko)` 两对**保持互异**（这四行最容易在某次重构里被合并）。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('GUI_BASELINE: proxies + accounts recorded')

p2 = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''
---

## 第 332 轮：Proxies + Accounts 实机对照，并把商店清单钉成测试

### 一、Proxies：零差异

实机：`PROXY GROUPS [Custom ⌄]` / `Search groups` / 分组列表 / `New Group +` /
`[folder] Group 1 [gear]` + `No Proxies Loaded` + `● 0 B current download` `● 0 B current upload` /
`[☐] IP⇅ Port⇅ Username⇅ Status⇅ [Add Proxies][Clear All][More]` / 空态两行。

复刻件逐项都有（`PROXY GROUPS`、`Custom`、`Search groups`、`No Proxies Loaded`、
两个流量计数、三键、列头同序、gear 在 `ProxyView.cs:385`）。

### 二、Accounts：14 个平台名**逐字同序**

```
Nike · Nike GS · Shopify · Footlocker (Asia) · Farfetch · Demandware (Funko)
Demandware · Magento · Casio · HBX · Popmart · Goat · Scheels · Warhammer
```

复刻件 `StoreCatalog.Platforms` 与之**逐字一致**，包括括号、空格、小写 m。
搜索框占位是 `Search stores`（不是 `Search groups` —— 这一点也一致）。

### 三、新守卫

`AccountStoreListTests`（2 条）：

1. 14 个名字与顺序全等；
2. `Nike / Nike GS`、`Demandware / Demandware (Funko)` 两对保持互异。

第 2 条针对的是**最容易在某次重构里被"合并"的四个名字** —— 它们只差一个后缀，
代码里看着像重复，界面上却是两行。

### 四、验证

```
AccountStoreListTests   2 通过
完整套件                1482 通过 / 0 失败 / 2 跳过
```

### 五、这一轮的一句话

> 四页 GUI 对照（Settings / Tasks / Proxies / Accounts）结论都是"没有差异"，
> 但我把其中**最容易漂的那一列文本**变成了测试。

> **"我核对过"会过期；"有测试盯着"不会。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('VERDICT appended')
