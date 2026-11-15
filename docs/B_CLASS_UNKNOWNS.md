# B 类 31 条的约束式 Unknown（R505 §3 格式）

> 按 R505 裁决：`Unknown` 不等于"什么都不写"。每条必须有**结构证据 / 相邻成员 / 数据约束 /
> 候选语义（排序）/ 判定所需的最小观测 / authority**。
>
> 这里的"数据约束"来自 R506 拿到的真实基线 —— `%APPDATA%\Cybersole` 顶层 11 个 JSON 的结构和哈希
> （见 `docs/R506_ROUTE_C_FIRST_ATTEMPT.md` §1）。**这是 Observation，不是推断。**

---

## 0. 共同的上下文证据（Observation）

原版数据目录当前是**空库但有默认组**：

```
accounts.json   {"accountGroups":[], ...}                       ← 组为空
tasks.json      [{name:"Group 1", …, tasks:[]}]                 ← 一个组，无任务
proxies.json    [{name:"Group 1", …, proxies:[]}]               ← 一个组，无代理
billing.json    [{name:"Group 1", …, profiles:[]}]              ← 一个组，无 profile
```

`AccountGrid` 的完整绑定描述符（`0x14320c54d`）：

```
Add!Getter / Add!Setter / Clear!Getter / Clear!Setter /
Edit!Getter / Edit!Setter / Delete!Getter / Delete!Setter
```

**八个成员全是可读写属性** —— 也就是说它们在原版里都是"绑定到 `ICommand` 的槽"，
具体行为在那个 `ICommand` 的 `Execute` 里，而 `Execute` 的委托初始化点无 xref（R504）。

---

## 1. `AccountGrid.Clear`（完整样板）

```
成员:      AccountGrid.Clear
结构证据:  描述符 0x14320c54d 里 Clear 有 Getter 和 Setter → 是可绑定命令，不是普通字段
相邻成员:  同一块描述符里还有 Add / Edit / Delete / DeleteSelected，以及 Account.Email/Password/Created；
           该页的空态文案是 "Add a group to get started"（说明页面按"组"组织）
locale:    Accounts 页可见文案里没有 "Are you sure" / "confirm" 一类（R506 截图观察）
数据约束:  accounts.json 的模型是 {accountGroups: [ {..., accounts: [...] } ], payPal, google, imap, aycdInbox}
           当前 accountGroups 为空 → 在空库上点 Clear 不会有任何可观察差异
候选语义（按可能性排）:
           ① 清空当前选中项（grid 里最常见的 Clear 语义；不改文件）
           ② 清空当前组的全部账号（破坏性；若无确认框则与本页 locale 观察矛盾）
           ③ 清空搜索/筛选条件（不改文件）
判定所需的最小观测:
           先建一个组并加 ≥2 个账号（让 accounts.json 非空），然后点一次 Clear，比对 accounts.json：
             - 文件不变           → ① 或 ③（再用"是否有选中"区分）
             - 某个组的 accounts 变空 → ②
authority: unknown（缺运行期观测；结构侧已确认）
```

---

## 2. `AccountGrid.Add` / `Delete` / `DeleteSelected`（同页，同一轮可一起观测）

```
成员:      AccountGrid.Add
结构证据:  同一描述符块，Getter+Setter
相邻成员:  Clear / Edit / Delete / DeleteSelected
数据约束:  账号挂在组内（accountGroups[].accounts[]），空库下 Add 无处可加
候选语义:  ① 在当前选中组里加一个空账号行  ② 打开"添加账号"对话框  ③ 从剪贴板批量导入
判定观测:  先建组 → 点 Add → 看 accounts.json 是否立刻多出一条（立刻=①；无变化=②需再填表单）
authority: unknown

成员:      AccountGrid.Delete
结构证据:  同上
候选语义:  ① 删除选中的账号（写文件，accounts.json 数组变短）
           ② 只从视图移除（不写文件）
判定观测:  组内有 ≥2 个账号时删 1 个，比对 accounts.json 的数组长度
authority: unknown

成员:      AccountGrid.DeleteSelected
结构证据:  同上（与 Delete 并存，说明二者语义不同）
候选语义:  ① DeleteSelected 删"当前选中"，Delete 删"全部"或"当前行"
判定观测:  同一条观测里同时看"删掉几个"
authority: unknown
```

---

## 3. 六个 `Save`（模式一致，可一次观测完）

```
成员:      ProfileGroupView.Save / CloudflareSolverCreatorView.Save /
           GoogleAccountEditView.Save / PayPalAccountCreatorView.Save /
           WebhookCreatorView.Save / StoreGroupModal.Save
结构证据:  六个类型在描述符表里都有 Save 的 Getter+Setter
共同点:    都出现在"编辑对话框"上（Create Group / Create Solver / Edit Account / …）
数据约束:  落盘目标分别是 billing.json(profiles) / solvers.json / accounts.json(google|payPal) /
           settings.json(webhooks) / 自定义店铺组
候选语义:  ① 校验 → 写对应 JSON → 关对话框  ② 只写内存，靠外层再提交  ③ 写临时文件后合并
判定观测:  打开任一编辑对话框，改一个字段，点 Save，比对**全部 11 个 JSON** 的哈希：
           哪个变了、变在哪个数组的第几项 —— 一次就能定位这 6 个的共同模式
authority: unknown
```

---

## 4. 六个 `Clear`（其余五个）

```
成员:      NotificationView.Clear / CustomSizesView.Clear / CustomStoresView.Clear /
           GoogleAccountsView.Clear / ImapView.Clear
结构证据:  各自描述符块里 Clear 有 Getter+Setter
数据约束:  它们对应 settings.json 里的 notificationOptions / customSizes / customStores /
           google 账号列表 / aycdInbox 配置
候选语义:  ① 清空该列表（settings.json 里对应数组变 []）
           ② 恢复默认值（数组变成出厂默认，不是空）
判定观测:  各页点一次 Clear，看 settings.json 里对应键是 `[]` 还是"默认值" —— 这一条能同时区分 ①②
authority: unknown
```

---

## 5. `OpenUrl` 两个

```
成员:      UserView.OpenUrl / HelpView.OpenUrl
结构证据:  各自的 setter 在描述符表里
已有事实:  两个类里都已经有 `System.Diagnostics.Process.Start(new ProcessStartInfo{...})`
           （UserView L366 附近 / HelpView L1011 附近），且 `UserView` 里有三个常量
           DashboardUrl / TermsUrl / PrivacyUrl
候选语义:  ① OpenUrl 是不带参命令，打开某个**固定** URL（哪个？三个常量之一）
           ② OpenUrl 带参（但描述符说它是属性，属性不能带参 → 排除）
判定观测:  在 UserView 上点一次，看**哪个 URL 被打开**（任务栏/浏览器标签），
           与三个常量比对
authority: unknown（`Process.Start` 的存在是 Observation，"点哪个开哪个"仍未观测）
```

---

## 6. 其余（`StartAll` / `StopAll` / `ToggleFilterBehaviour` / `AddInput` / `CloneStoreGroup` 等）

这些全部落在 `SmartActions` / `TaskView` / `UtilitiesView` 上，共享同一套观测方法：

```
判定模板:  在对应页面执行一次动作 → 比对 tasks.json / smartActions.json / settings.json 的差异
一次能覆盖: TaskView.StartAll + StopAll（tasks.json 里 tasks[].status 字段的变化）
           UtilitiesView.CloneStoreGroup / CreateStoreGroup / DeleteStoreGroup（settings.json 里 customStores）
           SmartActionsCreator.AddInput / ToggleFilterBehaviour（smartActions.json 的结构）
authority: unknown
```

---

## 7. 这份文档的定位

它**不是**"待办清单"，而是"每条缺什么证据、以及一次观测能同时回答几条"。

**共 31 条，按最小观测划分只需要 6 次动作**：

| 观测 | 一次能结案 |
|---|---|
| 建组 + 加 2 个账号 → 点 Add/Delete/Clear | `AccountGrid` 的 4 条 |
| 打开任一编辑对话框改字段点 Save | 6 个 `Save` |
| 各设置页点 Clear | 6 个 `Clear` |
| UserView 点 OpenUrl | 2 个 `OpenUrl` |
| Tasks 页 StartAll/StopAll | 2 条 |
| Utilities + SmartActions 各一次 | 其余约 11 条 |

**前提是先把"点得动"这件事解决**（R506 §2 的卡点）。
