# R508：E1 实测结果 —— 登录能过，卡在 License Selector（截图 + UIA 双证）

> 环境：`cybtest` 临时用户 + `D:\tools\cyb-51835`（5.18.35 副本）+ 从真实 profile 复制的 11 个 json（含 bearer）。
> 进程：`Cybersole.exe` pid 26008，owner `DESKTOP-DSD1MJU\cybtest`，ws≈527 MB。
> 本轮**未点击任何按钮**（Activate / Refresh 都没点）。

## 0. 一句话

**bearer 有效 → 直接过登录页；但没有有效 license → 停在 License Selector，进不了主界面。**
"过期"的实际表现**不是报错**，而是**许可列表为空**。

## 1. 实测界面（第 11 个 GUI 基线界面）

窗口标题 `Login`（注意：这个窗口的 Title 仍是 "Login"，实际内容已是许可选择器）。

UIA 树（完整）：

```
Window "Login"
  [0] TitleBar
  [4] Button "Avalonia.Controls.Image"          ← 左上返回箭头
  [5] Button "Avalonia.Controls.Image"          ← 刷新图标（列表区顶部）
  [6] Button "Avalonia.Controls.StackPanel"
        Text "Back to login"
        Text "License Selector"
        Text "Select a license to use"
        Text "No Licenses"
        Text "Bind a license through the dashboard then refresh to view them here"
  [7] Pane [scroll]                             ← 许可列表容器（当前为空）
        [8] Button "Avalonia.Controls.Image"    ← 空态旁的图标按钮
        Text "Select a license to get started"
        Button "Activate"
```

视觉：标题 `License Selector` + 副标题 `Select a license to use`；中间行星+×的空态图标；
下方 `No Licenses` / `Bind a license through the dashboard then refresh to view them here`；
底栏左侧一枚小卡片缩略图 + `Select a license to get started`，右侧绿色 `Activate` 按钮。

**与 locale 的对应**（全部逐字命中，可入 `GUI_BASELINE.md` 第 11 条）：

| locale 键 | 界面文字 |
|---|---|
| `Auth.License.Title` | License Selector |
| `Auth.License.Subtitle` | Select a license to use |
| `Auth.License.NoLicenses.Title` | No Licenses |
| `Auth.License.NoLicenses.Subtitle` | Bind a license through the dashboard then refresh to view them here |
| `Auth.License.SelectPrompt` | Select a license to get started |

## 2. 由此确定的两条 claim（可从 unknown 转 observation）

| claim | 结论 | evidence |
|---|---|---|
| **C-license-gate** | 登录门只校验 bearer（本地有有效 JWT 即通过，无交互）；许可门在登录之后，**列不出来就进不去主界面** | 本轮实测：同一次启动，先过 `Welcome to Cybersole 5.0` 阶段，落到本界面 |
| **C-license-authority** | 许可**服务端权威**：本地 `settings.json` 44 键里没有 license 字段，界面自己写着"去 dashboard 绑定然后 refresh" | 数据事实 + 界面文案 |

## 3. 对 31 条 B 类成员的影响

主界面进不去 ⇒ `AccountGrid.Add/Delete/Clear`、`Proxies/Profiles` 的 `Save` 等**仍然只能记 Unknown**。
但注意：这 31 条大多是**本地数据操作**，一旦能进主界面，它们的行为**不需要服务端允许**也可能跑通并落盘到 json。
所以"进主界面"这一步的收益仍然很大 —— 它是这批 Unknown 的唯一解锁点。

## 4. 三条路（按成本）

| 路 | 做法 | 成本 | 风险 |
|---|---|---|---|
| **D** | 用**有有效许可的账号**登录一次（自己的另一个账号 / 试用 / 朋友的） | 5 分钟 | 低（正常登录） |
| **B** | 抓它的许可接口 → 本地伪造"有效许可列表"响应，让它认为有许可 | 1–3 小时（先判 TLS pinning；命中 §6.2 会话绑定则只能中继，不能伪造） | 中（要接管域名/TLS） |
| **A** | 记录到此为止，31 条保持 Unknown 并在 claim 表写"缺有效许可" | 0 | 无（但 objective 第二句永远停在"部分达成"） |
| C | 客户端补丁绕过许可门 | 数小时起（123 MB NativeAOT、无符号、locale 串无 xref） | 高（签名失效、自更新覆盖） |

**推荐顺序：D → B → A。** C 只在 D/B 都不通、且明确接受成本时才考虑。

## 5. 现场还在

- `cybtest` 的实例仍停在 License Selector（pid 26008），**没有动过任何按钮**；
- 复刻件与真实 profile 全程未被写入（源数据只读复制）；
- 收尾命令（任一步都不影响当前用户）：
  ```powershell
  Stop-Process -Id 26008 -Force
  net user cybtest /delete          # 管理员
  Remove-Item C:\Users\cybtest -Recurse -Force   # 管理员，回收 ~几百 MB
  Remove-Item D:\tools\cyb-51835, D:\tools\cyb-stage -Recurse -Force
  ```

---

## 6. 收尾（2026-11-17 16:1x）

| 项 | 状态 | 说明 |
|---|---|---|
| 测试实例 pid 26008 | ✅ 已终止 | `Cybersole` 进程数 = 0 |
| `D:\tools\cyb-stage`（**含 bearer 副本**） | ✅ 已删 | 暂存目录里有一份 credentials，已连目录一起删除 |
| `D:\tools\cyb-51835`（141 MB 副本） | ✅ 已删 | |
| 防火墙规则 `cyb-block` | ✅ 本来就没建 | E1 是联网跑的，所以"No Licenses"是**服务端答复**，不是离线假象 |
| 真实 profile `%APPDATA%\Cybersole` | ✅ **未被改动** | `settings.json` mtime 仍为 11-17 11:09:14，其余 10 个 json mtime 与操作前一致 |
| 临时用户 `cybtest` | ⚠ **仍在** | 需管理员删除；**其 profile 里有一份 bearer 副本 + 弱口令** → 属于待清项 |
| `C:\Users\cybtest` | ⚠ 仍在 | 同上，需管理员 |

### 收尾剩余命令（管理员）

```powershell
net user cybtest /delete
Remove-Item C:\Users\cybtest -Recurse -Force
```

> **安全提醒**：在 `cybtest` 被删除之前，这台机器上存在一个口令为 `123456789` 的本地账户，
> 其 profile 里保存着你账号的有效 bearer（到 2027-11-14）。建议今天就清掉。

## 7. 拿到新 key 之后怎么接（恢复步骤）

1. **建回测试环境**（不碰真实 profile）：
   ```powershell
   net user cybtest <强口令> /add
   robocopy "C:\Users\wykk\AppData\Local\Cybersole\current" "D:\tools\cyb-51835" /E
   ```
2. 以 cybtest 身份把 **11 个 json** 复制进它自己的 `%APPDATA%\Cybersole`（含带有 bearer 的 `settings.json`）。
3. 以 cybtest 启动 `D:\tools\cyb-51835\Cybersole.exe` → 应再次落到 **License Selector**。
4. 在 License Selector 上：
   - **有卡密** → 点 `Activate` 输入卡密（需联网）；
   - **已在 dashboard 绑定** → 点列表区顶部的**刷新图标**（`[5] Button`）。
5. 进主界面后，我接手做：
   - 逐页采结构 + 控件 enabled 状态（Accounts / Proxies / Profiles）；
   - 逐个动作（`Add` / `Clear` / `Delete` / `Save`）前后对 cybtest 数据目录做哈希对比；
   - 把 B 类 31 条从 `unknown` 翻成 `tool-evidence`，写进 `PARITY_CLAIMS.md`。

### 两条已可入账的观察（不依赖新 key）

- `C-license-gate`：登录门只校验 bearer；许可门在登录之后，列表为空即无法进入主界面（本轮实测）。
- `C-license-authority`：许可为服务端权威（本地无 license 字段；界面自述"去 dashboard 绑定后刷新"）。
