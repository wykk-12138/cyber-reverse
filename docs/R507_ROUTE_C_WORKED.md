# R507：路 C 打通了 —— Accounts 页三个成员从 Unknown 变成 Observation

> YG 指出"你要点右边的箭头啊"之后继续试，最终查明：**`SendInput` 一直是好的，
> 之前全部无效是因为 Cybersole 被 IDA 窗口遮挡，点击落在了 IDA 上。**
> 把 Cybersole 提到前台后，第一个动作就成功了。

---

## 0. 卡点的真正原因（这比结论更重要）

前面两轮我试了 `set_value` / 坐标点击 / `expand` / Tab / Enter，全部无效，并写下了
"原版是 Avalonia，UIA 只读、SendInput 不被消费"的结论 —— **那个结论是错的**。

真相是：

```
bring_to_front(pid 3104) 之后立刻点击  ->  成功
```

在此之前，桌面截图显示 **IDA Pro 占着前台**，Cybersole 在它下面。
`SendInput` 按屏幕坐标投递，落点当然进了 IDA。

**教训**：`delivery_mode:"foreground"` 只是"把事件送到前台"，**它不保证目标窗口是前台**。
必须先 `bring_to_front`，且**中间不能插入任何会改变前台的操作**。

---

## 1. `AccountView.CreateGroup`（Observation）

**操作**：Accounts → `New Group` → Type=Nike / Store=Nike US / Name=`Probe Group` → `Add Group`

**落盘**（`accounts.json` 152 B → 236 B）：

```json
{"accountGroups":[{"id":"fb289b39","name":"Probe Group","store":"Nike US","type":"Nike","accounts":[]}], ...}
```

**结论**：
- 组对象字段：`id`（8 位小写十六进制）、`name`、`store`、`type`、`accounts`（空数组）
- `store` 与 `type` **分开存**（`type:"Nike"` / `store:"Nike US"`）—— Type 是店铺大类，Store 是具体站点
- 建组后界面标题变成 `Nike US - Probe Group`，右侧出现 `Add Accounts` / `Clear Accounts`

---

## 2. `AccountGrid.Add`（Observation）

**操作**：点绿色 `Add Accounts`

**界面**：弹出 **Add Accounts** 对话框：
- 一个大文本框，占位符 **`Enter accounts as account:password`**
- 拖放区 **`Or drag and drop a .txt file here`**
- 底部按钮，标题**实时计数**：`Import (0) New Accounts` → 输入两行后变 `Import (2) New Accounts`

**输入**：
```
probe1@example.com:pass1234
probe2@example.com:pass5678
```

**点 `Import (2) New Accounts` 后落盘**（236 B → 445 B）：

```json
{"email":"probe1@example.com","password":"pass1234",
 "created":1794673532854,"properties":{},"data":null}
```

**结论**：
- `Add` **不是"加空行"**，是**批量导入**：一行一条，格式 `account:password`，支持拖 `.txt`
- 账号对象字段：`email` / `password` / `created`（13 位毫秒时间戳）/ `properties`（空对象）/ `data`（null）
- 两条记录的 `created` **完全相同**（`1794673532854`）→ 整批用同一个时间戳
- 界面上 `Password` 列显示为 `••••••••`，`Added` 列显示格式化时间 `11/15/2026 0:25:32`

---

## 3. `AccountGrid.Clear`（Observation）—— R505 §3 那个样板的答案

**操作**：点红色 `Clear Accounts`

**先弹确认框**：

```
Delete 2 accounts?
Are you sure you want to delete 2 accounts?
You cannot undo this action.
[Delete (2) accounts]   [Cancel]
```

**点确认后落盘**（445 B → 236 B）：

```json
{"accountGroups":[{"id":"fb289b39","name":"Probe Group","store":"Nike US","type":"Nike","accounts":[]}], ...}
```

**结论 —— 直接命中 R505 §3 的候选②**：

| R505 当时的候选 | 结果 |
|---|---|
| ① 清空当前选中项（不改文件） | ❌ 文件变了 |
| ② 清空当前组的全部账号（破坏性，通常要确认框） | ✅ **正确，且有确认框** |
| ③ 清空筛选条件（不改文件） | ❌ 文件变了 |

**并且**：**组本身保留** —— `id`/`name`/`store`/`type` 一个字段都没动，只有 `accounts` 变回 `[]`。
确认框里的文案是 **"Delete N accounts?"**（不是 "Clear"），说明 UI 的 Clear 语义就是"删光"。

---

## 4. `AccountGrid.Delete` / `DeleteSelected`（Observation）

### `Delete`（行尾垃圾桶，单条）

3 条 → 点第 1 行垃圾桶 → **2 条**（`probe1` 消失），550 B → 445 B。
**没有确认框。**

### `DeleteSelected`（右键菜单）

勾选 1 条 → 在行上右键 → 菜单：

```
1 ACCOUNTS SELECTED
  Copy Password
  Copy Account
  Move accounts to  >
  Delete Accounts
```

点 `Delete Accounts` → **2 条**变 **1 条**（`probe2` 消失），445 B → 340 B。**同样没有确认框。**

**同一个菜单还证实了三件旧事**：
- `Copy Password` / `Copy Account` ↔ R491 做的 `CopyPassword` / `CopyAccounts`
- `Move accounts to >` ↔ R491 做的 `MoveGroup`
- 菜单标题 **`N ACCOUNTS SELECTED`** 随勾选数实时变化

### 四个成员的确认框分布（这个差异很重要）

| 成员 | 入口 | 确认框 | 写入 |
|---|---|---|---|
| `Delete` | 行尾垃圾桶 | **无** | 删一条 |
| `DeleteSelected` | 右键菜单 `Delete Accounts` | **无** | 删勾选的 N 条 |
| `Clear` | 右上红色 `Clear Accounts` | **有**（"Delete N accounts?"） | 清空本组全部 |
| `Add` | 右上绿色 `Add Accounts` | 无（对话框本身是输入界面） | 批量导入 |

**注意**：UI 上三个"删除"操作的文案分别是 `Delete` / `Delete Accounts` / `Clear Accounts`，
但 `Clear` 的确认框里写的是 **"Delete N accounts?"** —— 说明底层是同一个删除动作，只是作用域不同。

---

## 5. 操作手册（这轮代价换来的，下一轮直接用）

**输入通道的可靠性排序**：

| 方式 | 效果 |
|---|---|
| `click` `delivery_mode:"background"` + `element_token` | ✅ 走 UIA Invoke，最可靠（`Add Accounts` / `Import` / 复选框都用这个） |
| `right_click` 窗口坐标 + 然后 `get_window_state query` 拿菜单项 token + `click foreground` + token | ✅ 菜单类控件唯一可用路径 |
| `set_value` + `element_token` | ✅ 文本框可用（`ValuePattern`） |
| `click` `foreground` + 窗口坐标 | ❌ 坐标三层换算不可靠 |
| `click` `target:desktop` | ❌ 要求精确 HWND，弹出菜单永远失败 |
| `press_key` Tab/Enter/Delete | ❌ 对 Avalonia 无效（Escape 有效） |

**必须先 `bring_to_front`**，否则点击落在遮挡窗口上（这轮前两轮全废的原因）。

**判据不看截图看数据**：`get_window_state` 的截图会返回旧帧（同一 sha256 多次），
`%APPDATA%\Cybersole\*.json` 才是真相。

---

## 6. 当前数据状态

原版数据目录里有一个测试组（账号已删到 1 条）：

```
accounts.json  340 B
accountGroups: [ {id:"fb289b39", name:"Probe Group", store:"Nike US", type:"Nike",
                  accounts:[{email:"probe3@example.com", …}]} ]
```

我把这个组删掉（用组名旁的 ⚙），还是留着给下一轮继续测？

---

## 7. 下一轮可以直接拿的（同样的路子）

### R514 补：Settings 页的 `Add Size(s)` 与 `Clear Sizes`

**`Custom Sizes` 页**（Settings → ADVANCED → Custom Sizes）：

```
0 Custom Sizes                      [Clear Sizes]  [Add Size(s)]
  ☐ Name
  空态： "Add some size presets to get started"
```

**`Add Size(s)` 点开的是「Add Custom Sizes」对话框**：

```
Enter product URL   [https://cybersole.io/]  [Clear]
                    "Nothing to see here / Search a valid product URL"
[            Search            ]
```

**所以 `CustomSizesView.Add` 不是「手填一个尺码」，是「按商品 URL 去搜尺码」** ——
它需要联网抓商品页，才能列出可选尺码。

**`Clear Sizes` 在 0 条时**：点了**没有确认框**，`settings.json` **一个字节没变**
（2876 B / `C6DFD42AE1EF8942`，与基线相同）。空库直接返回。

**有数据时有没有确认框**：**Unknown** —— 要造出尺码必须先成功搜索一个商品 URL，这一轮没做。

### 6 个 `Clear` 的落盘目标（Observation）

`settings.json` 里对应的六个键，当前全是空数组：

```
customSizes        []
customStores       []
captchaProviders   []
cloudflareSolvers  []
webhooks           []
notificationOptions  { "Checkout": { enabled, centre, desktop, sound, … }, … }
```

前五个是数组，清空后应回到 `[]`；`notificationOptions` 是**对象**，所以它的 "Clear" 更可能是
「把每一项的开关复位」而不是置空 —— **这条是 Inference（中置信），未观测**。

---

### R515 补：Proxies 页 —— `Add` / `Clear` / `More` 三件

**页面结构**（Proxies → `Group 1`）：

```
0 B current download        0 B current upload
[Add Proxies]  [Clear All]  [More]
  ☐ IP | Port | Username | Status
  空态： "Add some proxies to get started"
```

#### `Add Proxies`

对话框和 Accounts 的**同构**，多一个目标组下拉：

```
Add Proxies   in [Group 1 ▾]
Proxies
  [Enter proxies as ip:port:username:password]
  [↓]  Or drag and drop a .txt file here
[        Import (0) New Proxies        ]
```

输入 `127.0.0.1:8080:probeuser:probepass` 后按钮变 `Import (1) New Proxies`。
导入后 `proxies.json` 130 B → **208 B**：

```json
{"host":"127.0.0.1","port":8080,"username":"probeuser","password":"probepass"}
```

- **`port` 是数字**（不是字符串）
- 字段名是 `host`（不是 `ip`），与输入格式 `ip:port:…` 不一致 —— 照抄，不改
- 组对象的其余字段 `id`/`name`/`order`/`maxUsage`/`behaviour`/`usagePeriod`/`usageExpiry` 不变

#### `Clear All`

**有确认框**，文案和 Accounts 的 `Clear` 完全同构：

```
Delete 1 proxies?
Are you sure you want to delete 1 proxies?
You cannot undo this action.
[Delete (1) proxies]   [Cancel]
```

注意 **`1 proxies`** —— 原版的单复数没处理，照抄。
确认后 208 B → **130 B**，`proxies: []`，**组对象一个字段没动**。

#### `More` 菜单（UIA 读到的四项）

```
[1] MenuItem "Test All On"
[2] MenuItem            ← 无可见名字
[3] MenuItem "Clear Failed"
[4] MenuItem "Clear Over"
```

**这直接钉死了三个绑定名的 UI 归属**：

| 绑定名 | UI 位置 |
|---|---|
| `ProxyView.TestAll` | `More → Test All On` |
| `ProxyView.ClearFailed` | `More → Clear Failed` |
| `ProxyView.ClearOver` | `More → Clear Over` |

**`[2]` 无名项是什么：Unknown** —— UIA 读不到它的名字，截图里也只是一个图标行。
R58 提过 locale 有 `Proxies.More.TestAllOn` 和 `Proxies.More.SelectSite`，所以它可能是
"Test All With / Select Site"，但**没有证据，不猜**。

---

### R516 补：Tasks 页 —— 六个按钮的映射

**页面结构**：

```
[Group 1 ▾]  [...]   [✓0] [✗0] [◷0] [↻0]        [Search tasks]
  ☐ Site | Product | Profile | Proxies | Status                    0 Tasks
  空态： "Add some tasks to get started"

[Task Creator +]  [Clear Tasks 🗑]   [Start Tasks ▶]  [Stop Tasks ⏹]   [Edit Tasks ✏]  [Captcha Solver ⊞]
```

**六个底部按钮的绑定名映射**：

| 绑定名 | UI 文案 |
|---|---|
| `TaskView.Add` | `Task Creator` + |
| `TaskView.Clear` | `Clear Tasks` 🗑 |
| `TaskView.StartAll` | **`Start Tasks`** ▶ |
| `TaskView.StopAll` | **`Stop Tasks`** ⏹ |
| `TaskView.Edit` | `Edit Tasks` ✏ |
| `TaskView.OpenSolver`（或同类） | `Captcha Solver` ⊞ |

**注意 `Start Tasks` / `Stop Tasks` 都是复数** —— 它们是**整组**操作，不是单条。
这和绑定名 `StartAll` / `StopAll` 里的 "All" 一致。

**顶部四个计数徽章**（绿勾 / 红叉 / 紫漏斗 / 蓝箭头，各带 0）：
**含义 Unknown** —— 没找到文案，只有图标和数字。不猜。

#### 空组上的两个动作（Observation）

| 动作 | 结果 |
|---|---|
| `Clear Tasks` | **无确认框**，界面无变化（`tasks.json` 未写） |
| `Start Tasks` | **无提示**，`tasks.json` **一个字节没变**（284 B / `EB5A4BC776705B6E`，与基线相同） |

**有任务时 `Start Tasks` 会做什么：不做。** 那会真的启动监控线程、按 `monitorDelay` 去轮询店铺，
属于"会对外发请求"的动作。`ProxyView.TestAll` 同理（R474 已记明确不做）。



| 待观测 | 操作 | 预计能一次结案 |
|---|---|---|
| `Delete` / `DeleteSelected` | 重新导入 2 条 → 选 1 条点行尾垃圾桶 → 再看全选后点 `Clear` 的差异 | 2 条 |
| 6 个 `Save` | 任一编辑对话框改字段 → Save → 比对 11 个 JSON 哈希 | 6 条 |
| 6 个 `Clear`（Settings 各页） | 各页点 Clear | 6 条 |
| `OpenUrl` ×2 | UserView 里点一次，看哪个 URL 被打开 | 2 条 |
| Tasks 页 `StartAll`/`StopAll` | tasks.json 里已有 `Group 1` | 2 条 |

**关键操作纪律**（本轮代价换来的）：

```
1. bring_to_front(pid, hwnd)
2. 立刻执行动作，中间不做任何读窗口的操作
3. 动作后用 pwsh 读 %APPDATA% 的数据文件 —— 数据才是真相，截图可能是旧帧
```
