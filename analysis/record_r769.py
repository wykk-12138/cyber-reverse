"""Record R769: two of the eleven 'gaps' are not gaps."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 196. **R765 的「12 个下不了单」里，至少两个不是缺口** —— 原版也没有

> R769。新增 `analysis/store_surface_probe.py`。未改产品代码。

### 一、按形式问，而不是按 URL 问

`AGENTS.md` §2.7 要求先问「这东西有几种写法」。结账面至少有四种（Observation 支撑的分类）：

```
① 店铺自己主机上的路径        hbx.com/checkout/pay
② 第三方平台主机 + client     platform.poq.io/clients/offspring/checkout/start
③ API hub 上的 action         apihub.scheels.com/frontastic/action/cart/checkout
④ GraphQL mutation，不是 URL  api.prod.warhammer.com/graphql
```

**所以「没有 URL 路径」不等于「没有结账」。** 探针把三件事分开报：结账词、GraphQL、平台名。

### 二、结果

```
fanatics     strings=9   urls=7   checkout=0   graphql=0   platform=0
             全部是 id.fanatics.com/api-internal/{oauth2/*,login/factor-request}
warhammer    strings=17  urls=9   checkout=0   graphql=1   platform=0
             api.prod.warhammer.com/graphql + login.mywarhammer.com/oauth/token
yeezysupply  strings=1   urls=1   checkout=0   graphql=0   platform=0
             只有 https://www.yeezysupply.com
```

### 三、判定（逐条写「为什么未覆盖」）

| 站 | 判定 | 依据 |
|---|---|---|
| **fanatics** | **不是缺口 —— 原版只有账号面** | 7 条 URL 全是 oauth2/login，**0 个结账词**，无平台名 |
| **yeezysupply** | **不是缺口 —— 原版几乎不认识这个站** | **整池只有 1 条字符串**（裸域名） |
| **warhammer** | **Unknown —— 有 GraphQL，但结账是否在其中无证据** | 1 条 graphql，**0 个结账词**；mutation 名不在字符串里 |

**这条比"补两步"重要**：**R765 把「七步里缺两步」当成缺口，而对 `fanatics` / `yeezysupply` 来说，
缺的正是原版也没有的。** 那不是复刻偏差，那是忠实。

**复刻件反而是多做的**（与 `bstn` 同类：`bstn` 原版 0 字符串，`yeezysupply` 原版 1 条）。

### 四、为什么不顺手改覆盖率测试

`ModuleCoverageTests` 有 `NonCommerce` 豁免机制（`raffle` / `pocketgames` / `riotgames`）。
**把 `fanatics` / `yeezysupply` 加进去是合理的技术动作，但它改的是"数字来源"**，
按 `AGENTS.md` §3 该单独一轮做，并且要跑全量。**本轮只判定，不动数字。**

**`warhammer` 不进豁免** —— 它是 Unknown，不是"不是缺口"。

### 五、验证

```
本轮未改产品代码
完整套件保持 1751 通过 / 0 失败
新增 analysis/store_surface_probe.py
```

### 六、仍然 Unknown

- `warhammer` 的 GraphQL 里有没有 checkout mutation：**Unknown** ——
  需要读 `api.prod.warhammer.com/graphql` 的调用方或请求体，字符串层看不到。
- 复刻件的 `WarhammerFlow` 是 REST 形态，**而原版是 GraphQL** —— 这与 `offspring`（Hybris vs Poq）
  是同一类形态错配，**未取证到 ops 名，故未动手。**
- `fanatics` 的账号面复刻件有没有对应：**未查。**
"""

VERDICT = """

---

## 第 769 轮：至少两个「缺口」不是缺口

### 按形式问，不按 URL 问

结账面至少有四种写法：店铺主机路径 / 第三方平台主机 + client / API hub action / **GraphQL mutation（不是 URL）**。
**所以「没有 URL 路径」≠「没有结账」。**

### 结果

```
fanatics     9 串 / 7 URL / checkout 0 / graphql 0 / platform 0   → 全是 oauth2 登录
warhammer   17 串 / 9 URL / checkout 0 / graphql 1                → graphql + oauth
yeezysupply  1 串 / 1 URL / checkout 0                            → 一条裸域名
```

### 判定

| 站 | 判定 |
|---|---|
| **fanatics** | **不是缺口 —— 原版只有账号面** |
| **yeezysupply** | **不是缺口 —— 原版整池只有 1 条字符串** |
| **warhammer** | **Unknown —— 有 GraphQL，结账是否在其中无证据** |

> **R765 把「七步缺两步」当成缺口，而对这两站来说，缺的正是原版也没有的。**
> **那不是复刻偏差，那是忠实。**

**反倒是复刻件多做了**（与 `bstn` 同类）。

### 为什么不顺手改覆盖率测试

`ModuleCoverageTests` 有 `NonCommerce` 豁免机制。**加进去是合理动作，但它改的是"数字来源"**，
按 §3 该单独一轮并跑全量。**本轮只判定，不动数字。`warhammer` 不进豁免 —— 它是 Unknown。**

### 验证

```
产品代码未改；套件 1751 / 0；新增 analysis/store_surface_probe.py
```

### 仍然 Unknown

- `warhammer` 的 GraphQL 里有没有 checkout mutation（字符串层看不到）
- 复刻件 `WarhammerFlow` 是 REST，**原版是 GraphQL —— 与 offspring 同一类形态错配**
- `fanatics` 的账号面复刻件有没有对应（未查）
"""

BACKLOG_ADD = """

## 核心 — 覆盖率的口径修正（R769）

`ModuleCoverageTests` 的七步尺子对以下模块**不合身**，但**本轮只判定、未改测试**（改的是数字来源，按 §3 单独一轮）：

| 模块 | 判定 | 依据 |
|---|---|---|
| `fanatics` | **不是缺口** —— 原版只有 oauth2 账号面 | 7 URL 全登录，0 结账词 |
| `yeezysupply` | **不是缺口** —— 原版整池 1 条字符串（裸域名） | — |
| `warhammer` | **Unknown** —— GraphQL 存在，结账是否在内无证据 | 1 graphql，0 结账词 |
| `bstn` | **原版 0 字符串** —— 复刻件多出来的模块 | R768 |
| `offspring` | **API 家族错配**：Hybris ↔ Poq | R768 |
| `goat` / `popmart` / `superswipe` | 抽奖面，尺子待判定 | R765/R766 |

**下一步（单独一轮）**：把已判定为"不是缺口"的加入 `NonCommerce` 式豁免，**并写清每条的依据**；
`warhammer` 与 `goat` 这类 Unknown 不豁免。
"""


def main():
    for p, marker, text in ((P1, "R769", BLOCKER), (P3, "R769", BLOCKER), (P2, "第 769 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R769" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += 口径修正")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R769: at least two of the eleven 'gaps' are not gaps -- the original has no checkout there either\n\n"
         "R765 read the coverage matrix and named twelve modules that cannot place an order. Two have since been\n"
         "closed by pointing missing steps at endpoints the image already carried. This round asked the prior\n"
         "question for three others: does the original carry a checkout surface for them at all?\n\n"
         "The form question mattered. A checkout can be a path on the store's own host, an action on a third-party\n"
         "platform host with a client segment, an action on an API hub, or a GraphQL mutation -- which is not a URL\n"
         "at all. So the probe reports checkout words, GraphQL and platform names separately, rather than deciding\n"
         "absence from the absence of a URL path.\n\n"
         "The answer changes the finding. fanatics carries nine strings, seven of them URLs, all of\n"
         "id.fanatics.com/api-internal/oauth2 or login/factor-request, with no checkout word anywhere: the image\n"
         "integrates Fanatics accounts and not its checkout. yeezysupply has exactly one string in the whole pool, a\n"
         "bare domain. For both, the two steps the matrix calls missing are steps the original does not have, so\n"
         "71% was the yardstick applied to the wrong object -- the replica is faithful, and if anything it has extra.\n\n"
         "That is the same shape as bstn, which has no strings at all, and the opposite of a gap.\n\n"
         "warhammer stays Unknown rather than resolved. It carries api.prod.warhammer.com/graphql plus an oauth\n"
         "login surface, so a checkout may exist as a mutation, but no string names one. It also reveals a second\n"
         "form mismatch of the kind offspring has: the replica's WarhammerFlow speaks REST where the original speaks\n"
         "GraphQL.\n\n"
         "The coverage test was deliberately left alone. ModuleCoverageTests already has a NonCommerce exemption for\n"
         "raffle, pocketgames and riotgames, and adding fanatics and yeezysupply to it would be reasonable -- but that\n"
         "changes a number source, which per the coding rules deserves its own round with the full suite. Verified\n"
         "conclusions only this round; warhammer must not be exempted because it is unresolved, not excluded.\n\n"
         "No product code changed; suite remains 1751 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
