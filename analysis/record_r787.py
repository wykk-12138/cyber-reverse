"""Record R787: Warhammer's WAF pair and the invented login endpoint."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 213. Warhammer 在 AWS WAF 后面：**两个 token**，一个头一个 cookie

> R787。改 `RetailFlows.cs`（`WarhammerFlow` 加 WAF 常量与 `ApplyWaf`；登录端点从编的换成镜像的）。未加测试。

### 一、先问有几种写法（§2.7）

```
WafHandler      -> 1 match   &WarhammerWafHandler
-waf-auth       -> 1 match   warhammer-com-waf-auth
```

**全镜像只有一个站点级 WAF 处理器，就是 Warhammer 的。没有通用机制可抄。**

### 二、请求头键解出来，风控机制就清楚了

`sub_140E4ABE0`（647 B）是请求构造器，`sub_1408BAD40(容器, 键, 值)` 反复调用。
十五个键用 `off_slot_reader` 一次读全：

```
content-length    sec-ch-ua      sec-ch-ua-platform    sec-ch-ua-mobile
authorization     warhammer-com-waf-auth              x-aws-waf-token
x-trace-id        user-agent     accept                content-type
origin            sec-fetch-site sec-fetch-mode        sec-fetch-dest
```

**`x-aws-waf-token` 与 `warhammer-com-waf-auth` 同时出现** ——
**一个 AWS 自己的 token（作请求头），一个站点自己的（作 cookie，但同样按头发）。**

**所以那个处理器的职责是：拿到第一个，才能出示第二个。**

另外**完整的 client hints（`sec-ch-ua` / `-platform` / `-mobile`）** 也在，那是现代浏览器的指纹面。

**这一条属于第 2 优先级（风控对抗），不是第 1。**

### 三、复刻件缺的两样

```
WarhammerWafHandler      ABSENT
warhammer-com-waf-auth   ABSENT
x-aws-waf-token          ABSENT（这次加的）
usernamepassword         ABSENT
```

**而且 `LoginAsync` 原来发到 `{IdentityHost}/api/login` —— 那是编的。**
镜像里 Auth0 的四步都在：

```
/usernamepassword/challenge
/usernamepassword/login
/oauth/token
/login/callback
```

### 四、改了什么

1. **WAF 常量 + `ApplyWaf(c)`**：从 `Session.Vars["awsWafToken"]` / `["wafAuthCookie"]` 取值，
   **有才设，没有就不动请求头** —— 第五次用「最坏情况等于没改」。
2. **登录端点**：`/api/login` → `/usernamepassword/challenge`（Auth0 流程的第一步）。

**注意**：Auth0 还要 `client_id` / `state` / `nonce`，**这三样都没取证**。
**所以这一步可能只拿到 challenge 而不是 token。代码会如实报错，不假装成功。**

### 五、验证

```
构建                已成功
完整套件            1761 通过 / 0 失败 / 0 跳过（与改动前同数）
四项度量            4 / 0 / 17 / 78 / 0（未变）
Warhammer 覆盖率    未变（这一轮加的是请求头与端点，不是补步骤）
```

### 六、仍然 Unknown

- **AWS WAF token 怎么拿**：**Unknown** —— 产出它的挑战交换不在已取回的字符串里。
- **Auth0 的 `client_id` / `state` / `nonce`**：**Unknown**。
- **GraphQL 的 operation 名**：**Unknown** —— 复刻件仍发 REST，镜像发 GraphQL，**这一轮没解决**。
- `WarhammerWafHandler` 的四个方法各做什么：**Unknown** —— 只读了最小的一个（构造器）。

### 七、一个反复出现的自伤，值得单独记

这一轮我又一次把 `PostJsonAsync` 写成 `PostjsonAsync`、把 `StepOutcome` 写成别的东西。
**但这次构建显示文件里其实是对的** —— 我看到的"坏字"来自工具调用回显，不是文件内容。

**教训是双向的**：坏字会发生（前面几次真坏了），**但不要凭回显判定文件坏了** ——
**要看文件本身**（这次用 `repr()` 打出来才看清）。**判定依据必须是文件内容，不是我对调用的记忆。**
"""

VERDICT = """

---

## 第 787 轮：Warhammer 在 AWS WAF 后面

### 先问有几种写法

```
WafHandler    -> 1 match   &WarhammerWafHandler
-waf-auth     -> 1 match   warhammer-com-waf-auth
```

**全镜像只有一个站点级 WAF 处理器，就是 Warhammer 的。**

### 请求头键解出来

```
content-length · sec-ch-ua · sec-ch-ua-platform · sec-ch-ua-mobile
authorization · warhammer-com-waf-auth · x-aws-waf-token · x-trace-id
user-agent · accept · content-type · origin · sec-fetch-site/mode/dest
```

**两个 token 同行：AWS 自己的作请求头，站点自己的作 cookie（也按头发）。**
**处理器的职责是拿到第一个，才能出示第二个。**

### 复刻件缺的两样，外加一个编出来的端点

`LoginAsync` 原发 `/api/login` —— **编的**。镜像里 Auth0 四步都在
（`usernamepassword/challenge` · `usernamepassword/login` · `oauth/token` · `login/callback`）。

### 改了什么

1. **WAF 常量 + `ApplyWaf`**：从会话取值，**有才设** —— 第五次用「最坏情况等于没改」
2. **登录端点** → `/usernamepassword/challenge`

**Auth0 还要 `client_id`/`state`/`nonce`，都没取证。这一步可能只拿到 challenge —— 代码如实报错。**

### 验证

```
构建绿 · 整套 1761 / 0 · 度量未变 · Warhammer 覆盖率未变
```

### 一个反复出现的自伤

我这轮又以为把 `PostJsonAsync` 写坏了，**但构建显示文件其实是对的** ——
**坏字来自工具调用回显，不是文件内容。**

> **判定依据必须是文件本身（`repr()` 打出来），不是我对调用的记忆。**
"""

BACKLOG_ADD = """

## 风控 — Warhammer AWS WAF（R787）

**镜像里唯一的站点级 WAF 处理器**（`WarhammerWafHandler` 与 `warhammer-com-waf-auth` 各 1 次）。

**两个 token 同行**：

```
x-aws-waf-token          ← AWS 自己的，作请求头
warhammer-com-waf-auth   ← 站点自己的，作 cookie（但按头发）
```

**另有完整 client hints**：`sec-ch-ua` / `sec-ch-ua-platform` / `sec-ch-ua-mobile`。

**已做**：`WarhammerFlow.ApplyWaf(c)` —— 从 `Session.Vars` 取两个 token，有才设。
**登录端点**从编的 `/api/login` 换成镜像的 `/usernamepassword/challenge`。

| 项 | 状态 |
|---|---|
| AWS WAF token 的取得方式 | **Unknown**（产出它的挑战交换不在字符串里） |
| Auth0 的 `client_id` / `state` / `nonce` | Unknown |
| **GraphQL operation 名** | **Unknown —— 复刻件仍发 REST，这是 Warhammer 最大的缺口** |
| 处理器四个方法各做什么 | Unknown（只读了构造器） |

**注意优先级**：这一条是第 2 层（风控对抗），不是第 1 层。

**工具记录**：`off_slot_reader.py` 一次解出 15 个头名 —— R776 为 6 个烧掉五次尝试，现在 15 个一次。
"""


def main():
    for p, marker, text in ((P1, "R787", BLOCKER), (P3, "R787", BLOCKER), (P2, "第 787 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R787" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += Warhammer WAF")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R787: Warhammer is behind AWS WAF, carrying two tokens at once -- and its login endpoint was invented\n\n"
         "Asking first how many spellings exist answers the shape question in one call: WafHandler matches once and\n"
         "-waf-auth matches once. WarhammerWafHandler and warhammer-com-waf-auth are the only such strings in the\n"
         "image, so there is no shared WAF mechanism to copy -- this is one bespoke handler for one site.\n\n"
         "One of its four methods is a request builder, and its fifteen header keys resolve in a single pass with the\n"
         "reader built in R777: content-length, sec-ch-ua, sec-ch-ua-platform, sec-ch-ua-mobile, authorization,\n"
         "warhammer-com-waf-auth, x-aws-waf-token, x-trace-id, user-agent, accept, content-type, origin and the three\n"
         "sec-fetch fields. Two WAF tokens travel together, AWS's as a header and the site's as a cookie that is also\n"
         "sent as a header; the handler's job is to obtain the first so the second can be presented. Full client hints\n"
         "are present too, which is the modern fingerprint surface. This belongs to the second priority, risk control,\n"
         "not the first.\n\n"
         "The replica had neither WAF string, and worse, its LoginAsync posted to {IdentityHost}/api/login, which is\n"
         "invented. The image names Auth0's actual steps. So ApplyWaf now installs both tokens from the session when a\n"
         "caller supplies them -- the fifth use of the pattern where the worst case equals the previous behaviour --\n"
         "and the login endpoint moves to usernamepassword/challenge.\n\n"
         "Auth0 also wants a client_id, state and nonce, none of which are recovered, so that step may return a\n"
         "challenge rather than a token. The code reports that instead of pretending otherwise, and the largest gap\n"
         "remains untouched: the GraphQL operations. The replica still speaks REST where the image speaks GraphQL.\n\n"
         "One recurring self-inflicted error, this time with a useful correction: I believed I had broken\n"
         "PostJsonAsync into PostjsonAsync, but the build showed the file was correct all along. The corruption was in\n"
         "the tool-call echo rather than the file. Both lessons hold -- mistyping does happen, as earlier rounds\n"
         "proved, and what settles it is the file's own bytes, printed with repr, not my memory of the call.\n\n"
         "Suite 1761 pass / 0 fail, unchanged in count; four metrics unchanged; Warhammer's coverage unchanged because\n"
         "this round added headers and a real endpoint rather than steps."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
