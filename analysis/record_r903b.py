"""Record R903. The product change is already committed; this writes the five documents."""

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
### `hostless` 桶关掉了：**67 / 67 = 100%**（R903）

**R902 补了 `/customer/v1/` 那 10 条，剩下 11 条这一轮补完。**

| 路径 | 干什么 |
|---|---|
| `/checkout/v1/orders` | 平台层下单 |
| `/checkoutshopper/v1/submitThreeDS2Fingerprint?token=` | **3DS2 指纹提交（优先级 ②）** |
| `/commerce/v1/bags` · `/commerce/v1/products` | **平台管购物车叫 bag** —— 复刻件的 cart 类因此从没匹配上 |
| `/legacy/v1/account/login` · `/legacy/v1/users/me` | 旧版 API 的登录与当前用户 |
| `/marketing/v1/verificationcodes` | 验证码（复数形式，与 R902 那条 `/customer/v1/verification/send` 不同） |
| `/payments-vas/v1/card-capture` | 存卡而非扣款 |
| `/product-core/v1/pdp` · `/pdp/sku` | 商品详情页 |
| **`/shield/v1/verify_otp`** | **OTP 校验，在 `/shield/` 下 —— 属防护服务，优先级 ②** |

### 数字

| 度量 | R902 | **R903** |
|---|---|---|
| `hostless` 覆盖 | 56 / 67（83.6%） | **67 / 67（100.0%）** |
| 总缺失 | 95 | **84** |
| 套件 | 1796 | **1802** |

### 而 `store covered` 还是 **3**

**前两轮补的全是**无宿主**那一侧。有宿主那 55 条只覆盖 3 条 —— 那是剩下的前沿，
而它比无宿主侧难：无宿主的路径只要常量就够，有宿主的要先搞清「哪条路径属哪个站」。**

### 两处特意做的标注

1. **`AntiBotRelated` 子集**：`ShieldVerifyOtp` + `ThreeDs2Fingerprint` 单列 ——
   **「优先级 ② 覆盖了多少」可以直接数，不用重读每条路径。**
2. **`ThePlatformWordsArePreserved` 用例**：`bags`（购物车）· `pdp`（商品页）· `shield` · `verificationcodes`（复数）
   **都是镜像的词，不是命名不一致** —— 断言它们，防止将来「规范化命名」把它们改掉。
"""

VERDICT = """

---

## 第 903 轮：`hostless` 桶关闭 —— 67/67 = 100%

### 11 条

**`/checkout/v1/orders` · `/checkoutshopper/v1/submitThreeDS2Fingerprint?token=` · `/commerce/v1/bags` ·
`/commerce/v1/products` · `/legacy/v1/account/login` · `/legacy/v1/users/me` ·
`/marketing/v1/verificationcodes` · `/payments-vas/v1/card-capture` · `/product-core/v1/pdp` ·
`/product-core/v1/pdp/sku` · `/shield/v1/verify_otp`**

### 数字

| 度量 | R902 | **R903** |
|---|---|---|
| `hostless` 覆盖 | 56/67（83.6%） | **67/67（100.0%）** |
| 总缺失 | 95 | **84** |
| 套件 | 1796 | **1802** |

### 而 `store covered` 还是 3

> **前两轮补的全是**无宿主**那一侧。有宿主那 55 条只覆盖 3 条 —— 那是剩下的前沿。
> 而它更难：无宿主的路径只要常量就够；有宿主的要先搞清「哪条路径属哪个站」。**

### 两处特意做的标注

1. **`AntiBotRelated` 子集**（`ShieldVerifyOtp` + `ThreeDs2Fingerprint`）→ **优先级 ② 覆盖可直接数**
2. **`ThePlatformWordsArePreserved`**：`bags`（购物车）· `pdp`（商品页）· `shield` · `verificationcodes`（复数）
   **都是镜像的词，不是命名不一致** —— 防将来「规范化」改掉

### 仍然 Unknown

**这 11 条属哪个站**（同 R902）· **`/shield/v1/verify_otp` 具体校验什么**（**优先级 ② 的第一个具体端点，值得单独查**）·
**`store` 那 55 条里 52 条缺失的清单**（`-v` 能列）· **`bags` 与 `cart` 是不是同一件事的两种叫法**

### 教训

> **两轮补完 21 条，`hostless` 从 68.7% 到 100%。而这个 100% 有个前提：
> **那 67 条里没有一条需要「知道属哪个站」才能补** —— 常量就是路径，路径是观察。**
> **有宿主那 55 条不同：「这条路径属 Nike 的哪个步骤」需要步骤级证据，而镜像对大部分只给了路径与宿主。
> 所以那 52 条缺失不是常量工作，是**归位**工作。**
> **100% 这个数好看，但它好看是因为这一侧的活容易。**
"""

BACKLOG_ADD = """

## 优先级 ① — `hostless` 桶关闭 67/67（R903，**改产品代码 +6 用例**）

### 11 条

**`/checkout/v1/orders` · `/checkoutshopper/v1/submitThreeDS2Fingerprint?token=` · `/commerce/v1/bags` · `/commerce/v1/products` ·
`/legacy/v1/account/login` · `/legacy/v1/users/me` · `/marketing/v1/verificationcodes` · `/payments-vas/v1/card-capture` ·
`/product-core/v1/pdp` · `/product-core/v1/pdp/sku` · `/shield/v1/verify_otp`**

### 数字

| 度量 | R902 | **R903** |
|---|---|---|
| `hostless` | 56/67（83.6%） | **67/67（100.0%）** |
| 缺失 | 95 | **84** |
| 套件 | 1796 | **1802** |

### 而 `store covered` 仍是 3

**无宿主侧补完 ≠ 有宿主侧补完。有宿主 55 条只覆盖 3 条。**

### 两处标注

**`AntiBotRelated`（`ShieldVerifyOtp` + `ThreeDs2Fingerprint`）→ 优先级 ② 可直接数**
**`ThePlatformWordsArePreserved`：`bags`/`pdp`/`shield`/`verificationcodes` 是镜像的词，非命名不一致**

| 仍 Unknown | |
|---|---|
| 11 条属哪个站 | 同 R902 |
| **`/shield/v1/verify_otp` 校验什么** | **优先级 ② 第一个具体端点** |
| store 55 里 52 条缺失清单 | `-v` 可列 |
| `bags` 与 `cart` 是否同义 | 不同站可能同角色 |

**纪律**：**100% 好看，但要问它为什么好看 —— 这一侧只要常量；那一侧要「归位」。**
"""

BLOCKER = """

---

## 327. `hostless` 桶关闭：**67/67 = 100%**；缺失 95 → 84；套件 1802

> R903。**改产品代码 +6 用例。** 套件 **1802 通过 / 0 失败 / 0 跳过**。

### 一、11 条

**`/checkout/v1/orders` · `/checkoutshopper/v1/submitThreeDS2Fingerprint?token=` · `/commerce/v1/bags` ·
`/commerce/v1/products` · `/legacy/v1/account/login` · `/legacy/v1/users/me` ·
`/marketing/v1/verificationcodes` · `/payments-vas/v1/card-capture` · `/product-core/v1/pdp` ·
`/product-core/v1/pdp/sku` · `/shield/v1/verify_otp`**

### 二、数字

| 度量 | R902 | **R903** |
|---|---|---|
| `hostless` 覆盖 | 56/67（83.6%） | **67/67（100.0%）** |
| 总缺失 | 95 | **84** |
| 套件 | 1796 | **1802** |

### 三、而 `store covered` 还是 3

**前两轮补的全是**无宿主**那一侧。有宿主那 55 条只覆盖 3 条 —— 那是剩下的前沿。**

**而它更难：无宿主的路径只要常量就够；有宿主的要先搞清「哪条路径属哪个站」，
而镜像对很多条只给了路径与宿主，没给步骤。**

### 四、两处特意做的标注

1. **`AntiBotRelated` 子集**：`ShieldVerifyOtp` + `ThreeDs2Fingerprint` → **优先级 ② 覆盖可直接数**
2. **`ThePlatformWordsArePreserved`**：`bags` · `pdp` · `shield` · `verificationcodes`（复数）
   **都是镜像的词，不是命名不一致** —— 断言防将来「规范化」改掉

### 五、验证

```
endpoint_coverage.py -v       -> 11 条 hostless 缺失（列出全部）
SharedCommerceEndpoints.cs    -> 新建，11 常量 + OwnerIsUnknown + AntiBotRelated
test --filter SharedCommerce  -> 6 通过
endpoint_coverage.py          -> hostless 67/67 = 100.0%，missing 84，store covered 3
metrics_report.py             -> 1802 通过 / 0 失败
```

### 六、仍然 Unknown

- **这 11 条属哪个站**：**Unknown** —— 同 R902。
- **`/shield/v1/verify_otp` 具体校验什么**：**Unknown** —— 只有路径；
  **而它是优先级 ② 的第一个具体端点，值得下一轮单独查。**
- **`store` 那 55 条里 52 条缺失的具体清单**：**Unknown** —— `-v` 能列，下一轮取。
- **`bags` 与 `cart` 是不是同一件事的两种叫法**：**Unknown。**

### 七、教训

**两轮补完 21 条无宿主路径，`hostless` 桶从 68.7% 到 100%。**

**而这个 100% 有个前提：那 67 条里没有一条需要「知道属哪个站」才能补。
常量就是路径，路径是观察，所以能补。**

**有宿主那 55 条不同：「这条路径属 Nike 的哪个步骤」需要步骤级证据。
所以那 52 条缺失不是常量工作，是**归位**工作。**

**100% 这个数好看，但它好看是因为这一侧的活容易。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R903", BLOCKER)
    ensure(RSTATUS, "R903", BLOCKER)
    ensure(RVERDICT, "第 903 轮", VERDICT)
    ensure(BACKLOG, "R903", BACKLOG_ADD)

    note = (
        "\n## R903 补充 — hostless 桶关闭 67/67 = 100%（改产品代码 +6 用例）\n\n"
        "11 条：/checkout/v1/orders · submitThreeDS2Fingerprint?token= · /commerce/v1/bags · /commerce/v1/products · "
        "/legacy/v1/account/login · /legacy/v1/users/me · /marketing/v1/verificationcodes · /payments-vas/v1/card-capture · "
        "/product-core/v1/pdp · /pdp/sku · /shield/v1/verify_otp。\n\n"
        "数字：hostless 56/67 → 67/67（100%）· 缺失 95 → 84 · 套件 1796 → 1802。\n\n"
        "而 store covered 仍是 3 —— 前两轮补的全是无宿主侧；有宿主 55 条只覆盖 3 条，那是剩下的前沿，"
        "而它需要归位而非常量。\n\n"
        "AntiBotRelated 子集让优先级 ② 可直接数。\n\n"
        "下一轮：store 那 52 条缺失清单（-v）+ /shield/v1/verify_otp 单独查。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R903" not in h:
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h + note)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R903"), (RSTATUS, "R903"), (RVERDICT, "第 903 轮"), (BACKLOG, "R903")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R903 record: the hostless bucket closes at sixty-seven of sixty-seven\n\n"
         "The product change landed in the previous commit; this writes the five documents that record it.\n\n"
         "Eleven paths complete the set R902 began: platform order submission, the 3-D Secure fingerprint whose token\n"
         " travels in the query, the commerce platform's bag and product reads, the legacy login and current-user, the\n"
         " plural verification codes, card capture, two product-detail reads, and the shield OTP check.\n\n"
         "The hostless bucket goes from fifty-six of sixty-seven to all sixty-seven, missing from ninety-five to\n"
         " eighty-four, suite from 1796 to 1802.\n\n"
         "The store bucket stays at three of fifty-five, and the contrast is the point. These sixty-seven needed only\n"
         " constants because a path is an observation; the other fifty-five need to know which step of which flow calls\n"
         " them, and the image mostly supplies path and host and nothing more. So the hundred percent is high because\n"
         " the easy side is finished, and the remaining work is placement rather than transcription.\n\n"
         "Two annotations are for later rounds: an anti-bot subset naming the shield OTP and the 3DS fingerprint so\n"
         " that priority's coverage can be counted directly, and a test that preserves bags, pdp, shield and the plural\n"
         " verificationcodes as the image's words rather than inconsistencies.\n\n"
         "Unknown: which store owns the eleven; what the shield OTP check verifies, which is the anti-bot priority's\n"
         " first concrete endpoint; the fifty-two missing store paths, printable with -v; and whether bags and cart are\n"
         " two names for one role.\n\n"
         "Documents only; suite carries at 1802."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
