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
源码未声明、且原版确有描述符 : 44
源码未声明、原版无描述符     : 0
```

## 逐条证据

| 类型 | 成员 | 原版描述符方向 | 该做成什么 |
|---|---|---|---|
| `BotTask` | `Running` | Getter/Setter | 可读写属性 |
| `CreateModel` | `Input` | Getter | 只读属性（或 ICommand） |
| `CreateModel` | `Inputs` | Getter/Setter | 可读写属性 |
| `EditValue`1` | `HasMultiple_101` | Getter/Setter | 可读写属性 |
| `EditValue`1` | `HasMultiple_87` | Getter/Setter | 可读写属性 |
| `EditValue`1` | `HasMultiple_88` | Getter/Setter | 可读写属性 |
| `EditValue`1` | `HasMultiple_91` | Getter/Setter | 可读写属性 |
| `EditValue`1` | `HasMultiple_93` | Getter/Setter | 可读写属性 |
| `EditValue`1` | `HasMultiple_94` | Getter/Setter | 可读写属性 |
| `EditValue`1` | `HasMultiple_95` | Getter/Setter | 可读写属性 |
| `EditValue`1` | `HasMultiple_97` | Getter/Setter | 可读写属性 |
| `EditValue`1` | `HasMultiple_98` | Getter/Setter | 可读写属性 |
| `EditValue`1` | `HasMultiple_99` | Getter/Setter | 可读写属性 |
| `EditValue`1` | `Value_100` | Getter/Setter | 可读写属性 |
| `EditValue`1` | `Value_92` | Getter/Setter | 可读写属性 |
| `Notification` | `Message` | Getter/Setter | 可读写属性 |
| `Notification` | `Type` | Getter/Setter | 可读写属性 |
| `State` | `Name` | Getter/Setter | 可读写属性 |
| `AccountGrid` | `Accounts` | Getter | 只读属性（或 ICommand） |
| `AccountGroupView` | `Save` | Getter/Setter | 可读写属性 |
| `CreateGroupModal` | `Create` | Getter/Setter | 可读写属性 |
| `CheckoutView` | `Checkout` | Getter | 只读属性（或 ICommand） |
| `CheckoutView` | `Properties` | Getter | 只读属性（或 ICommand） |
| `YoutubeWindow` | `Account` | Getter | 只读属性（或 ICommand） |
| `NotificationView` | `Clock` | Getter | 只读属性（或 ICommand） |
| `ExpressionView` | `Expressions` | Getter | 只读属性（或 ICommand） |
| `ProfileCreatorView` | `BillingView` | Getter | 只读属性（或 ICommand） |
| `ProxyGroupView` | `Reset` | Getter/Setter | 可读写属性 |
| `ProxyGroupView` | `Save` | Getter/Setter | 可读写属性 |
| `ProxyGroupView` | `TimeSpans` | Getter | 只读属性（或 ICommand） |
| `CustomSizesView` | `View` | Getter | 只读属性（或 ICommand） |
| `CustomStoresView` | `View` | Getter | 只读属性（或 ICommand） |
| `CaptchaProviderCreatorView` | `Delete` | Getter | 只读属性（或 ICommand） |
| `CaptchaProviderCreatorView` | `Properties` | Getter | 只读属性（或 ICommand） |
| `GoogleAccountEditView` | `Account` | Getter | 只读属性（或 ICommand） |
| `PayPalAccountCreatorView` | `Model` | Getter | 只读属性（或 ICommand） |
| `SizeCreatorView` | `Search` | Getter | 只读属性（或 ICommand） |
| `WebhookView` | `Test` | Getter | 只读属性（或 ICommand） |
| `SmartActionsView` | `Export` | Getter/Setter | 可读写属性 |
| `SmartActionsView` | `View` | Getter | 只读属性（或 ICommand） |
| `TaskDetailsView` | `Task` | Getter | 只读属性（或 ICommand） |
| `TaskGroupView` | `Link` | Getter/Setter | 可读写属性 |
| `TaskView` | `Edit` | Getter/Setter | 可读写属性 |
| `StoreGroupModal` | `Stores` | Getter | 只读属性（或 ICommand） |

## 说明

- **`Getter` 不等于「必须是属性」**：Avalonia 的 `ICommand` 也走 Getter。
  已有先例（`CheckoutView.Previous`/`Next`/`OpenTracking`）就是 `ICommand` 属性。
- 本表只证明**原版绑定过这个名字**，不证明**行为**。行为一律 Unknown。
- `declared-absent` 那 693 条不在此表 —— 它们的源码声明是有的，只是产物里没有独立符号。
