"""Record R893: families mapped to hosts, on co-occurrence inside one literal."""

import io
import os
import re
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### 族 ↔ 宿主：**45 族 / 28 宿主**，新文档 `docs/ENDPOINT_FAMILY_HOSTS.md`（R893）

**R892 的边界是「56 个族是全镜像的，按站分组还没做」。这一轮做了 —— 而分组的方法不是我起的名，
是**同现**。**

### 方法

**有些路径以完整 URL 出现（`//checkout.johnlewis.com/bff/v2/orders`），一条字面量里同时有宿主与族。
于是判据是：**族与宿主出现在同一条字面量里**。**

**这比「池内邻近」强 —— R876 那次错就是拿邻近当归属。同现是同一个字符串内部的关系。**

### 结果：45 / 56 族有同现宿主

| 宿主 | 族数 |
|---|---|
| **`api.nike.com`** | **11** |
| **`checkout.johnlewis.com`** | **4** |
| `www.vans.com` | 3 |
| `checkoutshopper-live.adyen.com` · `app.midtrans.com` | 各 2 |
| **`prod-hk-actapi.popmart.com`** | **1：`/activity/v1/`** |
| **`challenges.cloudflare.com`** | **1：`/turnstile/v0/`** |
| 其余 20 个宿主 | 各 1 |

### 优先级 ② 的三条落了地

| 宿主 | 族 | 读法 |
|---|---|---|
| **`challenges.cloudflare.com`** | **`/turnstile/v0/`** | **Cloudflare Turnstile 的端点** —— R876 见过 `_turnstileKey` 字段 |
| **`inbox-api.aycd.io`** | `/api/v1/` | **AYCD** 是验证码/OTP 收取服务；对应 `AycdInboxAccount` 模型 |
| `flex.cybersource.com` · `www.paypal.com` · `app.midtrans.com` | `/flex/v2/` · `/threeds/v1/` · `/snap/v1..v2/` | 3DS 与支付重定向 |

### 而它更正了 R835

**`prod-hk-actapi.popmart.com` 只带 `/activity/v1/` 一个族。**

**所以 PopMart 有**三个**路径空间、两个宿主：**

| 宿主 | 前缀 |
|---|---|
| `popmart.com`（`Origin(c.Url)` 拼出） | `/shop/v1/`（41）· `/store/v1/`（5） |
| **`prod-hk-actapi.popmart.com`** | **`/activity/v1/`（2）** |

**R835 当时搜 `activity/v1/exhibit_draw` 找 `StartDrawFlow` 没找到，判「PopMart 没有这个端点」。
现在看：抽签走 `/shop/v1/drawScratch/*`，而 `activity/v1` 是**另一个宿主的另一个空间**。
那次错的形状是「一个站只有一个 API 宿主」——而它有两个。**

### 四条边界，与表一起读

1. **45 / 56**：11 个族没有同现宿主，不在表里。
2. **同现证明「这个族在某宿主上」，不证明「只属于它」**：`/api/v1/` 在 aycd、goat、hbx 三个宿主上都出现。
3. **表里混了两类宿主**：站的 API（`api.nike.com`）与厂商的 API（`challenges.cloudflare.com`）。
4. **本表不说明复刻件有没有实现** —— 那是 R892 的 3 / 21 / 32 分级。
"""

if "族 ↔ 宿主：**45 族 / 28 宿主**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R893 appended")

BLOCKER = """

---

## 317. 族 ↔ 宿主 **45 / 28**，新文档 `ENDPOINT_FAMILY_HOSTS.md`

> R893。**新增文档，未改产品代码。**

### 一、方法：同现，不是邻近

**有些路径以完整 URL 出现（`//checkout.johnlewis.com/bff/v2/orders`），一条字面量里同时含宿主与族。**

**判据：**族与宿主在同一个字符串内部**。**

**这比池内邻近强 —— R876 的错误正是拿邻近当归属。同现是同一对象内部的关系，
邻近是两个对象摆在一起。**

### 二、结果

| 宿主 | 族数 |
|---|---|
| **`api.nike.com`** | **11** |
| **`checkout.johnlewis.com`** | **4** |
| `www.vans.com` | 3 |
| `checkoutshopper-live.adyen.com` · `app.midtrans.com` | 各 2 |
| **`prod-hk-actapi.popmart.com`** | **1（`/activity/v1/`）** |
| **`challenges.cloudflare.com`** | **1（`/turnstile/v0/`）** |
| 其余 20 个 | 各 1 |

**45 / 56 族有同现宿主；11 个没有（相对路径或宿主来自配置），不在表里。**

### 三、优先级 ② 三条落地

**`challenges.cloudflare.com` → `/turnstile/v0/`（Cloudflare Turnstile 端点，R876 的 `_turnstileKey`）·
`inbox-api.aycd.io` → `/api/v1/`（AYCD 验证码/OTP 收取，对应 `AycdInboxAccount`）·
`flex.cybersource.com` · `www.paypal.com` · `app.midtrans.com` → 3DS 与支付重定向**

### 四、更正 R835：PopMart 有**两个**宿主

**`prod-hk-actapi.popmart.com` 只带 `/activity/v1/`。**

| 宿主 | 前缀 |
|---|---|
| `popmart.com` | `/shop/v1/`（41）· `/store/v1/`（5） |
| **`prod-hk-actapi.popmart.com`** | **`/activity/v1/`（2）** |

**R835 搜 `activity/v1/exhibit_draw` 没找到 `StartDrawFlow`，判「PopMart 没这个端点」。
错的形状是「一个站只有一个 API 宿主」—— 而它有两个。**

### 五、四条边界

1. **45 / 56**，11 个族不在表里。
2. **同现证明「在某宿主上」，不证明「只属于它」**：`/api/v1/` 在 aycd、goat、hbx 三处都出现。
3. **混了两类宿主**：站的 API 与厂商的 API。
4. **不说明复刻件有没有实现** —— 那是 R892 的 3 / 21 / 32。

### 六、仍然 Unknown

- **那 11 个没有同现宿主的族属于谁**：**Unknown** ——
  **可能是相对路径（由某个 Base 常量拼），也可能是配置里的宿主。**
- **一个族属于多个宿主时怎么分工**：**Unknown** —— `/api/v1/` 三处，各自的路径子集未分。
- **`www.ibm.com` 带 `/dtd/v11/` 是什么**：**Unknown，且可疑** ——
  **名字像 IBM 文档站，可能是一条被误收的字符串，不是任何站的 API。**

### 七、教训

**R892 我到手的是「32 个族完全没有」，而这一轮把它变成了「45 个族各自属于谁」。

两者的差别不是精度，是**这张表现在能回答问题**：
「Nike 的 11 个族复刻件实现了几个」「Cloudflare Turnstile 的端点在不在」。

而这次判据（同现）比上一轮那个（整条字面量）稳 —— 因为它不假设存储形式。
R892 的错是假设「完整路径存在一个字面量里」；同现只要求「宿主与族在同一字符串里」，
**两种存储形式都满足**。**
"""

VERDICT = """

---

## 第 893 轮：族 ↔ 宿主 45 / 28，新文档 `ENDPOINT_FAMILY_HOSTS.md`

### 方法：同现，不是邻近

**有些路径以完整 URL 出现（`//checkout.johnlewis.com/bff/v2/orders`），一条字面量里同含宿主与族。
判据：**族与宿主在同一个字符串内部**。**

> **这比池内邻近强 —— R876 的错误正是拿邻近当归属。同现是同一对象内部的关系。**
> **也比 R892 的「整条路径是字面量」稳 —— 那个假设了存储形式，这个两种都满足。**

### 结果：45 / 56 族

| 宿主 | 族数 |
|---|---|
| **`api.nike.com`** | **11** |
| **`checkout.johnlewis.com`** | **4** |
| `www.vans.com` | 3 |
| `checkoutshopper-live.adyen.com` · `app.midtrans.com` | 各 2 |
| **`prod-hk-actapi.popmart.com`** | **1（`/activity/v1/`）** |
| **`challenges.cloudflare.com`** | **1（`/turnstile/v0/`）** |
| 其余 20 个 | 各 1 |

### 优先级 ② 三条落地

| 宿主 | 族 | 读法 |
|---|---|---|
| **`challenges.cloudflare.com`** | **`/turnstile/v0/`** | **Cloudflare Turnstile 端点**（R876 的 `_turnstileKey`） |
| **`inbox-api.aycd.io`** | `/api/v1/` | **AYCD 验证码/OTP 收取**（对应 `AycdInboxAccount`） |
| `flex.cybersource.com` · `www.paypal.com` · `app.midtrans.com` | `/flex/v2/` · `/threeds/v1/` · `/snap/v1..v2/` | 3DS 与支付重定向 |

### 更正 R835：PopMart 有**两个**宿主

| 宿主 | 前缀 |
|---|---|
| `popmart.com` | `/shop/v1/`（41）· `/store/v1/`（5） |
| **`prod-hk-actapi.popmart.com`** | **`/activity/v1/`（2）** |

> **R835 搜 `activity/v1/exhibit_draw` 没找到 `StartDrawFlow`，判「PopMart 没这个端点」。
> 错的形状是「一个站只有一个 API 宿主」—— 而它有两个。**

### 四条边界

**45 / 56**（11 个无同现宿主）· **同现证明「在某宿主上」不证明「只属于它」**（`/api/v1/` 在 aycd/goat/hbx 三处）·
**混了两类宿主**（站的 API 与厂商的 API）· **不说明复刻件有没有实现**（那是 R892 的 3/21/32）

### 仍然 Unknown

**11 个无同现宿主的族属于谁** · **一个族属于多宿主时怎么分工** · **`www.ibm.com` 带 `/dtd/v11/` 是什么**（**可疑，可能误收**）

### 教训

> **R892 我拿到的是「32 个族完全没有」，这一轮变成「45 个族各自属于谁」。**
> **差别不是精度，是**这张表现在能回答问题**：「Nike 的 11 个族复刻件实现了几个」「Turnstile 端点在不在」。**
"""

BACKLOG_ADD = """

## 判据 — 族 ↔ 宿主 **45 / 28**（R893，**新文档 `docs/ENDPOINT_FAMILY_HOSTS.md`**）

### 方法：同现（一条字面量内同时有宿主与族）

**比 R876 的「池内邻近」强；比 R892 的「整条路径是字面量」稳（后者假设了存储形式）。**

| 宿主 | 族数 |
|---|---|
| **`api.nike.com`** | **11** |
| **`checkout.johnlewis.com`** | **4** |
| `www.vans.com` | 3 |
| `checkoutshopper-live.adyen.com` · `app.midtrans.com` | 各 2 |
| **`prod-hk-actapi.popmart.com`** | **1（`/activity/v1/`）** |
| **`challenges.cloudflare.com`** | **1（`/turnstile/v0/`）** |
| 其余 20 个宿主 | 各 1 |

### 优先级 ② 三条

**`challenges.cloudflare.com` → `/turnstile/v0/`**（Turnstile，R876 的 `_turnstileKey`）·
**`inbox-api.aycd.io` → `/api/v1/`**（AYCD OTP，`AycdInboxAccount`）·
`flex.cybersource.com` `/www.paypal.com` `/app.midtrans.com` → 3DS 与支付重定向

### 更正 R835：PopMart 有 **2 个宿主**

**`popmart.com` → `/shop/v1/`(41) + `/store/v1/`(5)；`prod-hk-actapi.popmart.com` → `/activity/v1/`(2)**
**→ 错的形状是「一个站只有一个 API 宿主」。**

### 四条边界

**45/56（11 个无同现宿主）· 同现不证明唯一归属（`/api/v1/` 在 3 个宿主）· 混了站与厂商两类宿主 · 不说明复刻件实现情况**

| 仍 Unknown | |
|---|---|
| 11 个无宿主族属谁 | 相对路径或配置宿主 |
| 一族多宿主怎么分工 | `/api/v1/` 三处的路径子集未分 |
| `www.ibm.com` + `/dtd/v11/` | **可疑，可能误收** |

**纪律**：**同现是同一对象内部的关系，邻近是两个对象摆在一起 —— 前者能当归属，后者不能。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R893", BLOCKER)
    ensure(RSTATUS, "R893", BLOCKER)
    ensure(RVERDICT, "第 893 轮", VERDICT)
    ensure(BACKLOG, "R893", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R893" not in h:
        h += ("\n## R893 补充 — 族 ↔ 宿主 **45 / 28**（**新文档 `docs/ENDPOINT_FAMILY_HOSTS.md`**）\n\n"
              "**方法：同现**（一条字面量内同时有宿主与族，如 `//checkout.johnlewis.com/bff/v2/orders`）—— "
              "**比 R876 的池内邻近强，比 R892 的整条路径字面量稳（后者假设存储形式）。**\n"
              "**结果**：`api.nike.com` **11 族** · `checkout.johnlewis.com` **4** · `www.vans.com` 3 · adyen/midtrans 各 2 · "
              "**`prod-hk-actapi.popmart.com` 1（`/activity/v1/`）** · **`challenges.cloudflare.com` 1（`/turnstile/v0/`）** · 其余 20 各 1。\n"
              "**优先级 ② 三条**：Turnstile 端点 · AYCD OTP（`inbox-api.aycd.io`）· 3DS/支付重定向（cybersource/paypal/midtrans）。\n"
              "**更正 R835：PopMart 有 2 个宿主**（`popmart.com` 带 `/shop/v1/`+`/store/v1/`；`prod-hk-actapi.popmart.com` 带 `/activity/v1/`）"
              "→ 错的形状是「一个站只有一个 API 宿主」。\n"
              "**边界：45/56 · 同现不证明唯一归属 · 混了站与厂商 · 不说明复刻件实现情况。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R893"), (RSTATUS, "R893"), (RVERDICT, "第 893 轮"), (BACKLOG, "R893")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R893: forty-five endpoint families mapped to twenty-eight hosts, by co-occurrence not proximity\n\n"
         "R892 left the family table unable to serve criterion (f) because the fifty-six families were the whole"
         " image's and nothing said which store owned which. This round groups them, using a signal the pool provides"
         " directly: some paths appear as full URLs, so a single literal holds both the host and the family.\n\n"
         "That makes the criterion co-occurrence inside one string rather than adjacency in the pool. It is stronger\n"
         " than proximity, which is how R876 mistook a neighbouring name for an owner, and it is steadier than R892's\n"
         " whole-path-as-literal test, which assumed a storage convention and therefore missed the twenty-one families\n"
         " kept as a base plus a tail.\n\n"
         "Forty-five of the fifty-six families have a co-located host. Nike's api host carries eleven, John Lewis's\n"
         " checkout host four, Vans three, Adyen's checkoutshopper and Midtrans two each, and twenty hosts carry one.\n"
         " The eleven without a host are not in the table, which is stated in the document rather than left implicit.\n\n"
         "Three of the results bear on the anti-bot priority directly: challenges.cloudflare.com holds /turnstile/v0/,\n"
         " which is the endpoint for the _turnstileKey field R876 found in a model; inbox-api.aycd.io holds /api/v1/,\n"
         " matching the AycdInboxAccount model in the R883 baseline; and the cybersource, paypal and midtrans hosts\n"
         " carry the 3DS and payment redirect families.\n\n"
         "The grouping also corrects R835. Pop Mart has two API hosts, not one: popmart.com carries /shop/v1/ and\n"
         " /store/v1/, while prod-hk-actapi.popmart.com carries /activity/v1/ alone. R835 searched activity/v1 for\n"
         " StartDrawFlow, found nothing, and concluded Pop Mart lacked that endpoint; the draws live under\n"
         " /shop/v1/drawScratch/ on the other host. The error's shape was assuming a store has one API host.\n\n"
         "Four limits are printed with the table. Eleven families are absent from it. Co-occurrence proves a family\n"
         " appears on a host, not that the host is its only owner, since /api/v1/ shows up on aycd, goat and hbx. The\n"
         " table mixes two kinds of host, store APIs and vendor APIs. And it says nothing about whether the replica\n"
         " implements any of it, which is R892's three-way grading.\n\n"
         "Unknown: which store owns each of the eleven hostless families, where they may be relative paths or\n"
         " config-supplied hosts; how a family shared across hosts divides its paths, since /api/v1/'s twenty-one\n"
         " paths are not yet split by owner; and what www.ibm.com is doing with /dtd/v11/, which looks like a\n"
         " documentation site rather than any store's API and may be a stray string.\n\n"
         "The lesson is that co-occurrence and proximity are different relations. Two things inside one object are\n"
         " related; two objects placed side by side are merely adjacent, and this session has paid for that confusion\n"
         " more than once.\n\n"
         "New document; no product code changed; suite carries at 1783."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
