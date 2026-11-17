import io
p = r"D:\projects\cyber-reverse\docs\R508_LICENSE_GATE.md"
t = io.open(p, encoding='utf-8').read()
t += '''
---

## 6. 收尾（2026-11-17 16:1x）

| 项 | 状态 | 说明 |
|---|---|---|
| 测试实例 pid 26008 | ✅ 已终止 | `Cybersole` 进程数 = 0 |
| `D:\\tools\\cyb-stage`（**含 bearer 副本**） | ✅ 已删 | 暂存目录里有一份 credentials，已连目录一起删除 |
| `D:\\tools\\cyb-51835`（141 MB 副本） | ✅ 已删 | |
| 防火墙规则 `cyb-block` | ✅ 本来就没建 | E1 是联网跑的，所以"No Licenses"是**服务端答复**，不是离线假象 |
| 真实 profile `%APPDATA%\\Cybersole` | ✅ **未被改动** | `settings.json` mtime 仍为 11-17 11:09:14，其余 10 个 json mtime 与操作前一致 |
| 临时用户 `cybtest` | ⚠ **仍在** | 需管理员删除；**其 profile 里有一份 bearer 副本 + 弱口令** → 属于待清项 |
| `C:\\Users\\cybtest` | ⚠ 仍在 | 同上，需管理员 |

### 收尾剩余命令（管理员）

```powershell
net user cybtest /delete
Remove-Item C:\\Users\\cybtest -Recurse -Force
```

> **安全提醒**：在 `cybtest` 被删除之前，这台机器上存在一个口令为 `123456789` 的本地账户，
> 其 profile 里保存着你账号的有效 bearer（到 2027-11-14）。建议今天就清掉。

## 7. 拿到新 key 之后怎么接（恢复步骤）

1. **建回测试环境**（不碰真实 profile）：
   ```powershell
   net user cybtest <强口令> /add
   robocopy "C:\\Users\\wykk\\AppData\\Local\\Cybersole\\current" "D:\\tools\\cyb-51835" /E
   ```
2. 以 cybtest 身份把 **11 个 json** 复制进它自己的 `%APPDATA%\\Cybersole`（含带有 bearer 的 `settings.json`）。
3. 以 cybtest 启动 `D:\\tools\\cyb-51835\\Cybersole.exe` → 应再次落到 **License Selector**。
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
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('R508 appended: cleanup + resume steps')

# 让新会话一眼看到恢复入口
p2 = r"D:\projects\cyber-reverse\AGENTS.md"
t2 = io.open(p2, encoding='utf-8').read()
if 'R508_LICENSE_GATE' not in t2:
    t2 = t2.replace('## 3. 改代码的纪律', '''## 2.9 等新 key 的暂停项（R508）

B 类 31 条"行为 Unknown"卡在**有效许可**上：登录能过（bearer 有效到 2027-11-14），但
License Selector 列表为空 → 进不了主界面 → 本地动作（Add/Delete/Clear/Save）无法观察。

- 已实测并落账：`C-license-gate`（许可门在登录之后）、`C-license-authority`（服务端权威）。
- 恢复步骤与环境收尾清单在 **`docs/R508_LICENSE_GATE.md` §6–§7**。
- 拿到新 key 之前，这 31 条保持 `unknown`，**不要替它们编实现**。

## 3. 改代码的纪律''', 1)
    io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
    print('AGENTS.md 增加 §2.9 暂停项说明')
else:
    print('AGENTS.md 已有该节')
