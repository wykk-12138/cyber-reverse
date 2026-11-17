# R506：要不要「绕过登录」—— 不需要，本地已经有一份有效会话

> 全部结论来自**离线**读取 `%APPDATA%\Cybersole\settings.json`（只读），没有任何网络请求。
> 下面**不复制任何令牌内容**，只写结构与时间字段。

## 1. 事实（可复现，`python analysis\_jwt_probe.py`）

```
文件             C:\Users\wykk\AppData\Roaming\Cybersole\settings.json   (2854 B, mtime 2026-11-17 11:09)
顶层键           44 个（autoOpen3DS … language 等）
bearer           存在，609 字符
  header         { alg: HS256, typ: JWT }
  claims         exp / aud / iss / role / name / nameidentifier / SecurityStamp
  exp            2027-11-14T08:07:53Z   → 距现在约 362 天
license          不存在（键都不在）
```

**两条附带纠正**：

- `BLOCKERS.md` §4 写的「`license` 有值」**不成立** —— 44 个键里没有 `license`。
- 09:53 那次保留的副本是 **43 键、无 bearer**（登录前状态），当前是 **44 键、有 bearer**（登录后状态）。
  两份的差集正好是"多了一个 bearer 键"。

## 2. 结论：不需要绕过登录

登录态是**本地持有的长效令牌**（还有 362 天）。所以"打开原版进主界面"这件事不需要破解，
需要的是**给它一个私有数据根**，让它读到自己的 `settings.json`：

| 现状 | 问题 |
|---|---|
| `%APPDATA%\Cybersole` 是**你正在用的真实数据目录**（只读红线） | 直接跑会写它 |
| 原版只有一条固定路径 | 没有文档化的 `--data-root` 参数（`CYBERSOLE_DATA` 那个串 xref=0，未证实） |

## 3. 三条可行路线（风险从低到高）

### 路线 C（零风险，首选）：你点，我只读比哈希

见 `R505_DECISIONS.md` 的路 C。**不启动第二个实例、不复制令牌、不联网**。
代价：你花 2–3 分钟点 Add / Delete / Clear / Save。

### 路线 A（推荐用于"必须自己跑"）：独立 Windows 用户 + 复制 settings.json

```
# 1) 建临时用户（需管理员）
net user cybtest <密码> /add
# 2) 以该用户登录一次（或用 runas / Start-Process -Credential）让 profile 生成
# 3) 把原版的 settings.json 复制到 C:\Users\cybtest\AppData\Roaming\Cybersole\
# 4) 以该用户启动 C:\Users\wykk\AppData\Local\Cybersole\current\Cybersole.exe
```

- **你的真实数据目录零写入**（写的是 `cybtest` 的 profile）；
- 凭据是**原版自己的**会话，不是我们的程序冒充；
- 用完 `net user cybtest /delete` 即可。

### 路线 B：Windows Sandbox（若专业版且已启用）

更彻底（一次性容器），代价是要把 123 MB exe + Velopack 目录搬进去，启动慢。

## 4. 为什么**不建议**静态补丁绕过登录

| 理由 | 证据 |
|---|---|
| 登录判定的锚点在**无 xref 的元数据区** | `Welcome to Cybersole 5.0` 这类串在 locale blob 里；R504 与我的抽查（该区 12 条字符串 12/12 xref=0）都证实 |
| 有 Authenticode 签名 | `security` 目录存在（`pe_triage` 实测），改一个字节签名即失效 |
| Velopack 会自更新覆盖 | 它会写 `%LOCALAPPDATA%\Cybersole\current\`，补丁随时被换掉 |
| **完全没必要** | 令牌还有 362 天有效期 |

> 也就是说：补丁的收益是"省一次登录"，成本是"在无符号二进制里盲找分支 + 签名失效 + 被自更新覆盖"。

## 5. 一个额外可做的"零外联"实验（顺带回答鉴权是不是离线判定）

在路线 A 的基础上再加一条出站阻断：

```powershell
New-NetFirewallRule -DisplayName "cyb-block" -Direction Outbound -Program "C:\Users\wykk\AppData\Local\Cybersole\current\Cybersole.exe" -Action Block
# 跑完删除
Remove-NetFirewallRule -DisplayName "cyb-block"
```

- 若**离线也能进主界面** → 鉴权是本地判定，且整轮实验零外联；
- 若离线进不去 → 说明启动时强制在线校验，这条也值得写进 claim 表（对复刻件的鉴权设计有直接约束）。

## 6. 需要你点头的两件事

1. **建临时 Windows 用户**跑一次（路线 A）—— 需要管理员，且会短暂多一个用户 profile；
2. **加一条临时出站防火墙规则**（第 5 节）—— 需要管理员，跑完即删。

若两条都不想动，就走**路线 C**：你点几下，我只读比哈希。三条路都能拿到行为证据，
差别只是「谁在启动那个进程」。
