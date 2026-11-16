# 未声明绑定成员的原始描述符证据（生成文件，勿手改）

> 由 `python analysis/member_descriptors.py` 的索引生成；数据源 `analysis/pe_strings.txt`。
> 重新运行本脚本即可复现整张表。

## 为什么要有这份表

R709 我看了十二个名字，判断「这不像真成员，是提取器造的」，写进了 BLOCKERS。
R710 用字符串池证否了它 —— 原版描述符字面就是 `Cybersole.Models.EditValue`1,Cybersole.Core.HasMultiple_87!Getter`。

**逐条凭印象判，就会重复那次错误。** 所以这里把整个桶的证据一次性铺开：
每一行都是原版自己的编译期 XAML 描述符 `<Namespace.Type>,<Owner>.<Member>!Getter|Setter`，
读者用一条 grep 就能核对任意一行。

## 索引自检

```
pe_strings.txt 里的 Cybersole 描述符 : 1457 条
索引出的 (类型, 成员) 键              : 819
绑定表 xaml_bindings.json 的成员数   : 819
```

**键数 819 与绑定表成员数相等** —— 两个独立来源给出同一个数，是这个索引可用的第一条证据。

## 结论

```
源码未声明、且原版确有描述符 : 42
源码未声明、原版无描述符     : 0
```

## 逐条证据

| 类型 | 成员 | 原版描述符方向 |
|---|---|---|
| `BotTask` | `Running` | Getter/Setter |
| `CreateModel` | `Input` | Getter |
| `CreateModel` | `Inputs` | Getter/Setter |
| `EditValue`1` | `HasMultiple_101` | Getter/Setter |
| `EditValue`1` | `HasMultiple_87` | Getter/Setter |
| `EditValue`1` | `HasMultiple_88` | Getter/Setter |
| `EditValue`1` | `HasMultiple_91` | Getter/Setter |
| `EditValue`1` | `HasMultiple_93` | Getter/Setter |
| `EditValue`1` | `HasMultiple_94` | Getter/Setter |
| `EditValue`1` | `HasMultiple_95` | Getter/Setter |
| `EditValue`1` | `HasMultiple_97` | Getter/Setter |
| `EditValue`1` | `HasMultiple_98` | Getter/Setter |
| `EditValue`1` | `HasMultiple_99` | Getter/Setter |
| `EditValue`1` | `Value_100` | Getter/Setter |
| `EditValue`1` | `Value_92` | Getter/Setter |
| `State` | `Name` | Getter/Setter |
| `AccountGrid` | `Accounts` | Getter |
| `AccountGroupView` | `Save` | Getter/Setter |
| `CreateGroupModal` | `Create` | Getter/Setter |
| `CheckoutView` | `Checkout` | Getter |
| `CheckoutView` | `Properties` | Getter |
| `YoutubeWindow` | `Account` | Getter |
| `NotificationView` | `Clock` | Getter |
| `ExpressionView` | `Expressions` | Getter |
| `ProfileCreatorView` | `BillingView` | Getter |
| `ProxyGroupView` | `Reset` | Getter/Setter |
| `ProxyGroupView` | `Save` | Getter/Setter |
| `ProxyGroupView` | `TimeSpans` | Getter |
| `CustomSizesView` | `View` | Getter |
| `CustomStoresView` | `View` | Getter |
| `CaptchaProviderCreatorView` | `Delete` | Getter |
| `CaptchaProviderCreatorView` | `Properties` | Getter |
| `GoogleAccountEditView` | `Account` | Getter |
| `PayPalAccountCreatorView` | `Model` | Getter |
| `SizeCreatorView` | `Search` | Getter |
| `WebhookView` | `Test` | Getter |
| `SmartActionsView` | `Export` | Getter/Setter |
| `SmartActionsView` | `View` | Getter |
| `TaskDetailsView` | `Task` | Getter |
| `TaskGroupView` | `Link` | Getter/Setter |
| `TaskView` | `Edit` | Getter/Setter |
| `StoreGroupModal` | `Stores` | Getter |

## 说明

- **方向字段不能用来判类型。** 全表实测：Getter **100%** / Property **100%** / Setter **77.9%**，
  只有两种组合（Getter+Property+Setter 638、Getter+Property 181）。**Getter 与 Property 是常量，
  只有 Setter 在变。** R717 专门校准过 Setter 的含义：G+S 组带 `set_` 访问器名的占 56.4%、
  G-only 组占 44.8% —— **没有分开**，所以它既不能读作「有 set 访问器」，也不能读作「双向绑定」。
  **Setter 的含义是 Unknown**，本表因此不再给任何形状建议。
  **R712 本表曾有一列「该做成什么」，那是过度解读；R714 删列，R717 连理由也修正。**

- **能判类型的只有两种证据**：
  ① **基数/排除法** —— `Notification` 原版绑定四个名字、record 四个参数，两两对齐；
  ② **描述符 + 源码形态互证** —— `Close` 是 `Getter` 单方向，且源码里已是 lambda 按钮。
  只有一条证据时，本表不给实现建议。
- 本表只证明**原版绑定过这个名字**，不证明**行为**。行为一律 Unknown。
- `declared-absent` 那 693 条不在此表 —— 它们的源码声明是有的，只是产物里没有独立符号。
