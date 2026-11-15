# R510：Billing 页观测 —— 拿到结构，没拿到落盘

> 目标：建一个 profile，拿 `billing.json` 的样本，好回答「`Profile.Card` 到底是嵌套对象还是平铺」。
> 结果：**结构拿到了，落盘没成功**。下面是 Observation 和卡点，不掺推断。

---

## 1. 前置：原版进程中途没了

R509 结束时原版还在（pid 3104）。R510 开始时 `list_windows` 返回 0 个窗口，`Get-Process` 也查不到。

**最可能的原因**：R508 我用 `set_window_frame(0, 0, 2560, 1400)` 把窗口改到 2560×1400，
而屏幕只有 2560×1440 —— 加上标题栏可能超出，窗口被移出可视区，随后退出。
**这是 Inference（中置信），我没有直接证据**。

**已重启**：`Start-Process $env:LOCALAPPDATA\Cybersole\current\Cybersole.exe` → pid 64596，20 秒后窗口出现，
数据完好（`accounts.json` 仍是 340 B，`Probe Group` 还在）。

**教训**：不要用 `set_window_frame` 把窗口撑到屏幕尺寸 —— 超出屏幕的那部分会让窗口失去可操作性。

---

## 2. Observation：Billing 页（= Profiles 页）的结构

点顶部 `Billing` 标签后：

```
PROFILE GROUPS  [Custom ▾]
  Group 1                      0

Group 1  ⚙
  No Profiles Loaded
  [+ Add Profile]  [Clear Profiles]  [CSV Editor]  [Search profiles]

  列： Profile | Email | Card Holder | Card | Shipping
  空态： "Add some profiles to get started"
```

- 和 Accounts 页同构：左侧组列表、右侧表格、右上 **绿 `Add Profile` / 红 `Clear Profiles`**
- 另有 `CSV Editor` 按钮（Accounts 页没有）
- `billing.json` 里 `Group 1` 的 `profiles` 是空数组

---

## 3. Observation：`Add Profile` 打开的对话框

点绿 `Add Profile` → **New Profile** 对话框：

```
  New Profile                                  [×]
  Profile Name   [Profile 1            ]
  [Payment] [Shipping] [Billing] [Advanced]   ☐ Different Billing
  Card Details
    [4242 4242 4242 4242 ]  [MM/YY]  [CVV]
  Email                     Phone Number
    [user@cybersole.io]     [123 456 7890]
  [              Save              ]
```

左侧还有一个独立的 **Expression Guide** 面板：

```
  Expression | Output
  {c:4}        sjdf      [Copy]
  {C:4}        SJDF      [Copy]
  {num:4}      8374      [Copy]
  {range:5-10} 7         [Copy]
  {range:a-z}  g         [Copy]
  {range:A-Z}  G         [Copy]
  {rand:1,2,3} 2         [Copy]
  {firstName}  John      [Copy]
  Test your expressions here: [Enter expression] [Copy] / [Result will appear here] [Refresh]
```

---

## 4. **关键结构事实**：Card 在 UI 上是平铺的三个字段

描述符表说 `Cybersole.Models.Profile` 有 `Card`（Getter+Setter），而
`Cybersole.Models.Card` 有 `Number` / `Cvv`。

**但对话框里卡号、MM/YY、CVV 是三个并列的独立输入框，不是一个嵌套控件的三个子字段。**

**这直接支持复刻件现在的平铺设计**：`CardNumber` / `CardExpiry` / `CardCvv` / `CardName` 四个独立属性。
也解释了为什么 `Profile.Card` 是个**计算属性**候选（getter 组装、setter 拆回），而不是存储字段。

**所以 R488 那条"结构差异，不改"的判断是对的** —— 加一个嵌套 `Card` 属性反而会和 UI 打架。

---

## 5. 卡点：Save 没有落盘

试了两轮：

| 填了什么 | `billing.json` |
|---|---|
| 只填卡号 `4111111111111111`（自动格式化成 `4111 1111 1111 1111`） | 63 B，未变 |
| 再补 `MM/YY=12/28`、`CVV=123`、`Email`、`Phone` | 63 B，未变 |

`Save` 按钮（`id=SaveButton`，有 UIA invoke）点了两次，无报错弹窗，对话框也不关。

**可能的原因（Inference，未验证）**：
- 某一项校验没过（`MM/YY` 格式？CVV 长度？）
- 或 `Profile Name` 需要唯一/非默认
- 或 Save 只写内存，真正的落盘在关对话框时（而 `Esc` 取消了）

**没解决，也不再耗** —— 这条的价值是拿 `Profile.Card` 的形状，而 §4 已经从 UI 给出了答案。

---

## 6. 当前数据状态

```
accounts.json  340 B   Probe Group / Nike US / 1 个账号（probe3@example.com）
billing.json    63 B   Group 1 / profiles:[]          ← 没被改动
其余 9 个 JSON  与 R507 结束时一致
```

**没有新增无法解释的残留**：profile 没建成，所以 `billing.json` 是干净的。
`accounts.json` 里那个 `Probe Group` 是 R507 留下的测试数据，仍然在。
