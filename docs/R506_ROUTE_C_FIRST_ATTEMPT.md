# R506：路 C 的第一次实测 —— 基线拿到了，UI 操作没打通

> 按 R505 裁决执行：先做 §4（读历史数据），再按 YG 授权用 CUA 操作原版做前后哈希对比。
> 结果：**§4 完全成功**；**CUA 那半段卡在点击精度上，一个字节都没有改动**。

---

## 1. §4 成功：原版数据目录的结构基线（Observation，只读）

`%APPDATA%\Cybersole` 顶层 11 个 JSON，全部 `-File` 列出并算 SHA256，基线存在
`%TEMP%\cyb-before.txt`。

**内容全是空库**，这本身是关键约束：

| 文件 | 字节 | 结构 |
|---|---|---|
| `accounts.json` | 152 | `{"accountGroups":[],"payPal":[],"google":[],"imap":[],"aycdInbox":{apiKey:null,templateId:null,appGroup:null,timeoutSeconds:600,enabled:true}}` |
| `tasks.json` | 284 | `[{id:"211e9628",name:"Group 1",order:null,usagePeriod:null,…,captchaSource:7,cloudflareSolver:null,webhooks:[],tasks:[]}]` |
| `proxies.json` | 130 | `[{id:"f5adcc39",name:"Group 1",order:null,maxUsage:null,behaviour:0,…,proxies:[]}]` |
| `billing.json` | 63 | `[{id:"57246c7c",name:"Group 1",order:null,profiles:[]}]` |
| `analytics.json` | 65 | `{"proxies":[{id:"f5adcc39",totalDownload:0,totalUpload:0}]}` |
| `solvers.json` | 287 | `[{left:null,…,solvers:[{proxy:null,filter:null,account:null,settings:{autoBoundingBox:true,…}}]}]` |
| `settings.json` | 2876 | （有 `bearer` / `license` 值） |
| `checkoutHistory.json` | 89554 | （历史记录，非空） |
| `sessions.json` / `smartActions.json` | 2 / 2 | `{}` / `[]` |
| `smartActionUtilities.json` | 13 | — |

### 由此能立刻排除的候选

`accounts.json` 的 `accountGroups` 是**空数组**，而 `tasks.json` / `proxies.json` / `billing.json`
各自都有一个 `Group 1` 且成员数组为空。

- `AccountGrid.Clear` 的候选 ③「清空筛选条件」**不写文件** → 与"文件全空"一致，但**不能证伪 ①/②**。
- `AccountGrid.Add` 的候选「加空行」需要 `accountGroups` 里先有组 → **当前状态无法观测**，必须先建组。

**这正是 R505 说的"历史数据能压候选集"** —— 它把"先做什么"定下来了：**必须先建组，才谈得上 Add/Delete/Clear**。

---

## 2. CUA 那半段：走通了界面，没走通"提交"

按 YG 授权（"需要去 cybersole 里创建 account 或 task 的话，你用 cua mcp 来操作"）操作原版
（pid 3104，5.18.35 —— **注意不是 5.18.32**）。

### 走通的部分（Observation）

| 步骤 | 结果 |
|---|---|
| Accounts 页 | 左侧店铺列表 14 项（Nike / Nike GS / Shopify / … / Warhammer），右下 `New Group`，右侧空态 **"Add a group to get started"** |
| 点 `New Group` | 弹出 **Create Group** 对话框：`Type`(下拉，默认 Nike) / `Store`(组合框，占位 "Select Store") / `Name`(输入框) / `Add Group` 按钮 |
| 填 `Name` | `set_value` 成功，截图确认显示 "Probe Group" |
| 填 `Store` | `set_value` 成功，截图确认显示 "Nike" |
| **点 `Add Group`** | **无效**。`accounts.json` 保持 152 B / SHA256 不变 |

### 为什么没走通

1. `Add Group` 这个 Button **没有 UIA element_index**（树里是裸的 `- Button "Add Group"`，不能 `invoke`）；
2. 改成坐标点击后，`delivery_mode:"background"` 报 `UIA pixel click unavailable`，
   `foreground` 送出的 `SendInput` 落在 `(900,845)` / `(1018,654)` 两个屏幕点，**两次都没有触发按钮**；
3. 用 `Enter`（对话框默认按钮）和 `Escape` 试过，`Enter` 没有提交，`Escape` 正常关闭了对话框。

**推断（Inference，中置信）**：`Store` 是 `ComboBox`，`set_value` 只改了它的 `PART_TextBox`
文本，没有改 `SelectedItem`。截图里显示 "Nike" 是**文本**，不是**选中项** ——
所以提交时校验不过（或者按钮根本没被点到）。

**备择解释**：坐标点在缩放后的客户区上算对了，但 `SendInput` 的落点被 1.25 倍缩放偏移掉了。

### R506 续：查清了 —— **原版是 Avalonia，CUA 的输入对它无效**

YG 提示"store 你要点下拉框啊"之后又试了一轮，全部无效。查窗口类名才找到根因：

```
python -c "debug_window_info(3104)"
  class_name: "Avalonia-91c5ce81-7464-4cc5-8e7e-8f049fcd4261"
  focused_element: { class_name: "TextBox", supported_patterns: ["Value","LegacyIAccessible"] }
```

**原版 5.18.35 也是一份 Avalonia 应用。** 于是所有输入路径都断在这里：

| 尝试 | 结果 |
|---|---|
| `set_value` 到 Name 框 | 返回 ✅ 成功、`ValuePattern` 读到 "Probe Group"，**但应用状态未变** |
| `set_value` 到 Store 的 `PART_TextBox` | 同上，只改文本，不改 `SelectedItem` |
| `click` 坐标（background） | `UIA pixel click unavailable` |
| `click` 坐标（foreground） | `SendInput` 送到 (900,845)/(1018,654)/(1116,654)，**三次都没触发按钮** |
| `click` `action:"expand"` 到 Store | `ExpandCollapsePattern unavailable` |
| `press_key` Tab / Enter / Escape | Escape **有效**（关了对话框），Tab/Enter **无效** |
| `bring_to_front` | 成功（hwnd 变成前台），之后重试仍然无效 |
| 桌面截图核对 | 红色 agent 光标确实停在 Store 上，**界面纹丝未动** |

**结论（Observation）**：Avalonia 自绘窗口不消费 `SendInput` 合成的鼠标/键盘事件；
它的 UIA 提供程序只支持**读**（Value / LegacyIAccessible），不支持**写**。

**所以 `cua-driver` 这条路对这份原版走不通** —— 不是坐标算错，是输入通道不被接受。

**这也顺带解释了一件旧事**：R456 裁决②说"接触运行中原版**有条件允许**（仅 `get_window_state`、不点击）"——
当时那个"不点击"的限制，现在有了技术依据，不只是纪律。


---

## 3. 数据完整性：一个字节都没改（Observation）

操作全部结束后重新算全量哈希，与基线逐项对比：

```
no file changed — data untouched
```

**`%APPDATA%\Cybersole` 仍然是只读的**，纪律没有被破坏。

---

## 4. 结论与下一步

**路 C 本身没被证伪**，卡点是"怎么让原版真的提交一次表单"，而不是"该不该做"。

三个继续的方向，按代价排：

1. **让 `Store` 真正选中**：先点下拉展开（不是 `set_value`），再从弹出的列表项里 UIA `invoke` 一项。
   需要一次带 `query` 的读取确认下拉弹出后的列表结构。
2. **改用 `Tasks` 页**（`tasks.json` 里已有 `Group 1`，不需要先建组）：Tasks 页的 `Add` 可能直接可用，
   比 Accounts 少一步。
3. **请 YG 亲手点那一下**（R505 原方案）：我做好前后哈希，YG 点完我比对。这是最省时间的一条。

**在打通之前，31 条 B 类成员仍按 R505 §3 的格式写"带候选集和判定方法的 Unknown"**，
不写任何猜测实现。

---

## 4bis. 上述 1/2 两条已被 R506 续排除 —— 只剩第 3 条

`debug_window_info` 查明原版是 **Avalonia** 之后，1（UIA 展开）和 2（换页）都不可行：
UIA 提供程序不支持写，`SendInput` 不被消费。**换到 Tasks 页也一样点不动。**

所以**唯一可走的只剩请你亲手点**（R505 原本就推荐的那条）。

### 我这边已经备好的东西

基线哈希在 `%TEMP%\cyb-before.txt`（11 个 JSON 的 SHA256）。你点完之后我跑一个命令就能比对出
"哪个文件、哪个字段变了"。

### 你需要点的（按顺序，约 2 分钟）

| # | 位置 | 动作 | 想结案的成员 |
|---|---|---|---|
| 1 | Accounts → `New Group` → 选 Type/Store，填名 → `Add Group` | 建一个组 | `AccountView.CreateGroup` 的落盘形状 |
| 2 | 新组里点 `Add` | 加账号 | `AccountGrid.Add`（4 条之一） |
| 3 | 加 2 个后选中 1 个点 `Delete` | 删一个 | `AccountGrid.Delete` / `DeleteSelected` |
| 4 | 点一次 `Clear` | — | `AccountGrid.Clear`（R505 §3 的样板） |
| 5 | 任一编辑对话框改字段 → `Save` | 保存 | 6 个 `Save` |
| 6 | Settings 里各页点 `Clear` | — | 6 个 `Clear` |

**做完告诉我一声**，我立刻比对并把这些成员从 Unknown 升级成 Observation。

### 数据完整性（截至现在）

```
11 files unchanged, data untouched
accounts.json: 152 B  0DAF12F8A6F05B36  （与基线逐字节相同）
```

`Esc` 已把 Create Group 对话框关掉，原版回到干净的 Accounts 页。

