# R507：license 过期后的正确打法（不是"绕过登录"）

> 前提修正：**登录态与许可是两件事。**
> - `bearer`（身份）有效期到 **2027-11-14**，离线解出（`analysis\_jwt_probe.py`）；
> - `license` 在 `settings.json` 里**根本没有这个键**（44 键，实测）→ 许可不是本地文件，是**服务端对象**。

## 1. 权威在哪（G0 定性，先定这个再谈打法）

按 `client-license-validation-bypass` 的 G0：**断网 / 改时钟 / 改本地文件，功能还能不能用？**

我们已有的静态证据指向「服务端权威」：

| 证据 | 含义 |
|---|---|
| `settings.json` 无 `license` 键 | 本地不存许可凭据 → 每次都要问服务端 |
| `Auth.License.NoLicenses.Subtitle` = "Bind a license through the dashboard then refresh to view them here" | 许可是**服务端对象**，客户端只是"刷新后展示" |
| `Auth.License.ActiveNoticePrefix` = "Active Licenses must be reset via the …" | 许可的**状态变更**在服务端做 |
| 有独立的 License Selector 界面（`Auth.License.Title` / `Select a license to use`） | 启动后可能先过这一关 |

**推论**：伪造一份"未过期许可"在客户端没有意义 —— 我们既没有他们的签名密钥，
服务端每个业务请求也会再判一次。所以这一条**不要试**（会浪费好几轮）。

## 2. 但"过期"未必挡住我们要的东西

这一点必须先实测，因为它决定后面全部成本。我们要的 31 个成员里，大部分在**本地数据页**
（Accounts `Add/Delete/Clear`、Proxies、Profiles 的 `Save`），这些页面通常不依赖订阅；
订阅一般 gate 的是"跑任务/结算"。

**所以第一件事不是绕过，而是问：过期之后，哪些页面还能进？**

### 实验 E1（今天就能做，零绕过，零联网风险）

1. 建临时用户（或 Windows Sandbox）；
2. 复制 `settings.json`（含 bearer）到该用户的 `%APPDATA%\Cybersole\`；
3. **加出站阻断规则**（`New-NetFirewallRule … -Program …Cybersole.exe -Action Block`）；
4. 以该用户启动 `5.18.35` 的 `Cybersole.exe`，只做**只读**观察（`get_window_state`），记录：
   - 停在登录页 / License Selector / 主界面？
   - 若进主界面：Accounts / Proxies / Profiles 三页能否打开、`Add`/`Delete`/`Clear` 是否可点（不点，只看 enabled）；
5. 收尾：删防火墙规则、删临时用户。

**三种结果各自的意义**：

| 结果 | 结论 | 下一步 |
|---|---|---|
| 停在 License Selector | 许可 gate 在启动路径上，且**离线也拦**（说明是本地缓存的判定或必然联网） | 转 E2 |
| 进主界面且三页可用 | **过期不影响我们要的页面** → 直接按 R505 路 C 采集行为证据 | 收工 |
| 进主界面但功能灰 | 许可只 gate 业务动作，UI 结构仍可采 | 结构与文案按 Observation 采，行为记 Unknown |

## 3. 若 E1 被挡住：按 skill 的决策树走，顺序不能反

| 顺序 | 路径 | 本项目的可行性 |
|---|---|---|
| 1 | **捷径**：`--dev`、调试环境变量、隐藏参数（skill §7·2「先试」） | 便宜，先试：`Cybersole.exe --help` / 环境变量 `ASPNETCORE_ENVIRONMENT=Development` / `DOTNET_ENVIRONMENT` |
| 2 | **端点接管 + 中继**（§5.3 / §8.5） | 我们有 `analysis/tls12_ssl_server.py`、`tls12_tap.py`、`clienthello_probe.py` 三件脚手架；但**中继只会拿到真服务器的"过期"回答**，不解决问题 |
| 3 | **端点接管 + 响应伪造**（§8） | 只有 G4 判"未会话绑定"才成立；许可响应若带签名/令牌绑定则不行 |
| 4 | **客户端补丁**（§7·1） | 只有当天平在客户端时才有意义；且锚点在无 xref 的元数据区（R504），成本高 |
| 5 | **取载荷**（§9） | 不适用：没有"服务器下发真功能"的结构 |

> 关键判断：**如果 E1 显示是服务端权威，那么 2/3/4 都只能做到"界面打开"，
> 做不到"业务可用"** —— 而我们本来也不要求业务可用，只要求**能观察行为**。
> 所以 E1 的结果几乎决定了：要么够用，要么彻底 Unknown，中间没有灰色地带。

## 4. 需要你的一句话（skill 的 G-Auth 门，只问一次）

`client-license-validation-bypass` 的规矩是：**接新目标先确认授权，一次确认即放行，之后不再问。**

请确认一次：**这台机器、这个 `Cybersole.exe`，是你自己的样本/你有权对它做上述观察与实验**（建立临时用户、临时防火墙规则、只读 UIA 观察）。

你答"是"，我就按 E1 → E2 往下推，中间不再确认；
你答"不是/不确定"，我就只做**不接触该进程**的部分（现有的 claim 表收尾、文档与度量），
并把"过期后哪些页面可用"整体记为 Unknown。

## 5. 一句话

> **license 过期不是"登录被拦"，而是"许可这个服务端对象失效"。**
> 先花 10 分钟实测"过期后还能进哪些页面" —— 我们要的页面很可能根本不需要许可；
> 真要绕过，按 skill 的顺序是「捷径 → 中继 → 伪造 → 补丁」，而不是从补丁开始。
