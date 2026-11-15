import io
p = r'D:\projects\cyber-reverse\replica\docs\DEVIATIONS.md'
t = '''# 已知差异清单（复刻件 vs 原版 5.18.32）

这份文档只列**已知且被接受**的差异，每条都写清"为什么接受"。缺口数字（17 / 18）与它不是一回事：
那些是"还没做"，这里是"决定不做或无法做"。

---

## 一、绑定形状：动作是方法，原件是 `ICommand` 属性（272 处）

| 项 | 值 |
|---|---|
| 有访问器证据的成员 | 465（可写 327 / 只读 138） |
| 形状不一致 | **272**（`python tools/shape_audit.py`） |

**为什么接受**：复刻件没有任何 XAML 绑定，动作就是方法，行为等价。
**新规则**：新增动作成员写成 `ICommand` 属性（`docs/METHOD.md` §13）。

---

## 二、UI 结构：少两处、多两处

| 位置 | 差异 | 依据 |
|---|---|---|
| Group Settings | 原件 4 个 tab，复刻件曾多 `General`/`Manual` → **R353 已删** | locale `TaskGroup.Tab.*` 只有四个 |
| `Pinned` / `Order` | 已从该弹窗移除（`Pinned` 属 `TaskView.PinGroups`、`Order` 属 `Settings.TaskGroupOrder`） | 同上 |

---

## 三、文案与 URL

| 项 | 状态 |
|---|---|
| `UserView` 的 `TermsUrl` / `PrivacyUrl` | **inferred**：实机有按钮、没给链接目标 |
| GOAT 的 `/v1/buys` 等三条路径 | **inferred**：池子里查不到出处（该店只有 5 条 `web-api/` 路径有出处，且已全部用上） |
| 4 条 cookie / 4 条查询参数 | **inferred**：无镜像证据，逐行标注 |
| `Settings.Webhook.ExtraFields` 的界面位置 | 未知（属性是真的，5 个 locale 键为证） |

---

## 四、不可得（三源否证）

| 项 | 说明 |
|---|---|
| `Platform.InputType` / `QuantitySupport` / `QuantityAutoAdjustSupport` | 池子只有名、下拉点不开、locale 无 `Platform.*` |
| `User.IsStaff` | 需账号角色信息，本地无来源 |
| `SettingsView.Transition` | 与同名成员不是同一类，且无证据说明它控制什么 |
| `AnalyticsView.OpenRelease` | 无 release 目录、无浏览器服务 |

---

## 五、故意留白（绑定表有名、行为未知）

`TaskView`：`CreateGroup` `LinkChange` `MoveGroup` `PinGroups` `Quicktask` `Toggle`
（R349 找到文案线索："Mass Link Change"、"Launch Quicktask"）

`CreateModel`：`Input` `Inputs` —— **类型不可推断**
`BotTask`：`Task` —— 类型不可推断，且与 `System.Threading.Tasks.Task` 同名
`SmartActionsView`：`Clock` `Export` · `GroupSummary`：`Clone` `Delete` `Edit` ·
`HistoryWindow`：`SmartAction` `View` · `GoogleAccountsView.Edit` · 两个自定义页的 `View`

---

## 六、类型级缺口（18）

`python tools/bind_scope.py` —— 成员没长在该类型上。剩余 18 个类型大多是上面的"留白"项。

---

## 七、怎么用这份文档

判断"是否 1:1"要分三层看：

1. **行为**：套件 1525 通过；8 条字面量流程可对账；错误目录逐字命中 → **这一层最实**；
2. **结构/文案**：七页实机核对，发现的四处差异已修 → **次之**；
3. **形状**（命令属性 vs 方法、tab 数、控件位置）→ **有意保留差异，见上文**。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('DEVIATIONS.md written')
