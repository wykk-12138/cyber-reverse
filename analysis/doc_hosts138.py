import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_PROVENANCE.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 正式缺口：Kasada `Api` 那条路**没有地址**（第 138 轮）

第 136/137 轮证明原版有「取 Kasada」（远端服务）这条路，第 137 轮给了它注入入口但**没有地址**。
这一轮把原版自己的主机表整个捞出来，终于能把这条缺口写清楚。

### `*.cybersole.io` 十五个主机

```
amazon-waf    analytics   api        castle       cdn
cf-solver     datadome    forward    images       match
pop4          proxy       support    telemetry    text-captcha
```

**没有 `kasada.cybersole.io`。**

### 所以缺口是确定的，不是没查

| 事实 | 依据 |
|---|---|
| 存在远端「取 Kasada」这一路 | `Getting Kasada (1)`、`Failed getting Kasada (Rotating)` |
| 那条路的后端**就是原版自己的服务** | `Kasada API down (Contact staff)` —— 「请联系客服」是自家后端挂了才说的话 |
| **没有任何 Kasada 专用主机** | 十五个主机里没有 |
| 最可能的候选 | **`api.cybersole.io`** —— 唯一剩下的后端 |

`CybersoleHosts.KasadaApiCandidate` 把它记成**推断**，`KasadaApiEvidence` 明写
`no kasada.cybersole.io exists … inferred … no capture`，并有测试守着这句话。

> **这是本会话第一次把「原版有、我们缺」写成正式条目**，而不是让它在代码里沉默。

### 顺带：四个 solver 主机，和同一个「服务 vs 本地」分野

| 主机 | 解什么墙 |
|---|---|
| `amazon-waf.cybersole.io` | Amazon WAF |
| `cf-solver.cybersole.io` | Cloudflare |
| `datadome.cybersole.io` | DataDome |
| `text-captcha.cybersole.io` | 文字验证码 |

还有一句把分野说白的话：

```
Cloudflare solver refused the token, solving in-bot
```

—— **服务拒了，就在机器人内部解**。这和 Kasada 的 `Api` → `Local` 是**同一条策略的两个实例**。

设置页那组名字也在：`CloudflareSolvers`、`CloudflareSolverId`、`CloudflareSolver.Default`、
`CapSolver`、`CloseSolver`、`EmptySolver.html`。
'''

if "## 正式缺口：Kasada `Api` 那条路" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("gap documented in the ledger")
else:
    print("already present")
