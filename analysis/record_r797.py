"""Record R797: hypecommerce exempted on evidence, and the guessed chain named as a separate problem."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 223. `hypecommerce` 进豁免；**同时把"复刻件那条链是猜的"单独立项**

> R797。`ModuleCoverageTests.YardstickDoesNotApply` 加 `hypecommerce`（6 条豁免）。

### 一、镜像里只有 6 条，全是 admin API（Observation）

```
https://admin.hypecommerce.io/api/entries/create
https://admin.hypecommerce.io/api/entries/validate
https://admin.hypecommerce.io/api/payment/methods/store
https://admin.hypecommerce.io/api/settings
（另有主机本身与一个 _hypeApi 前缀标记）
```

**`entries` 是关键词** —— 报名/抽奖提交，**先 validate 再 create**。
**没有任何商品、购物车、运费、支付的店面端点。**

**所以七步尺子不合身，与 goat/popmart/superswipe 同一类。**

### 二、但复刻件那 71% 是**猜出来的**

`HypeCommerceFlow` 有 8 个 override：GetHome / Login / FindProduct / FindVariant /
ScrapeVariantAvailability / AddToCart / SubmitOrder / GetCheckout —— **71%（5/7）**。

**而它的商品/购物车/订单路径在镜像里一条依据都没有。**

**这件事必须分开说**：

- **豁免**回答的是"七步尺子对这个模块合不合身" → **不合身**
- **它不回答"复刻件那条链对不对"** → **那 71% 是猜的，而且没人验过**

**所以豁免的同时把它单独立项**（见第四节），**否则豁免会顺手把一个问题藏起来。**

### 三、豁免文案

```
hypecommerce = "R797: 六条字符串全是 admin.hypecommerce.io/api/* —— entries/create,
entries/validate, payment/methods/store, settings。entries 是报名/抽奖提交，
所以这是 admin 报名 API，不是七步店面结账"
```

### 四、新立项：`HypeCommerceFlow` 的那条链没依据

**待办**：要么按镜像的 entries API 重写它（`entries/validate` → `entries/create`），
要么把它降级成诚实失败。

**判断依据**：镜像里只有 entries，**而 entries 的形状（validate → create）是可以照抄的** ——
**比现在这条猜出来的商品/购物车链更有据。**

**这一轮没做，因为它是另一个决定**（改 8 个 override 的方向），**不是豁免的连带动作。**

### 五、口径

```
resolved 63/63 flows; fully covered 51; exempt 6
```

**分母 58 → 57，`fully covered` 仍 51。**
**这不是覆盖率上升，是分母变化 —— R793 就写过的同一条。**

### 六、验证

```
构建                未改产品代码（只改测试的豁免表）
ModuleCoverageTests hypecommerce 71%（yardstick does not apply）；exempt 6
完整套件            1766 通过 / 0 失败 / 0 跳过
四项度量            4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- **`entries/validate` 与 `entries/create` 的请求体**：**Unknown** —— 端点有，字段没有。
- **`payment/methods/store` 的用途**：**Unknown** —— 存支付方式，但为谁存不明。
- **镜像有没有 hypecommerce 的店面面**：**Unknown** —— 只搜过 `hypecommerce`，
  **可能店面域名不含这个词**（§2.7：先问有几种写法）。
- **`HypeCommerceFlow` 现在那 71% 里有没有一步是对的**：**Unknown** —— 没人验过。
"""

VERDICT = """

---

## 第 797 轮：hypecommerce 进豁免，而它那条链是猜的要单独说

### 镜像里只有 6 条，全是 admin API

```
admin.hypecommerce.io/api/{entries/create, entries/validate, payment/methods/store, settings}
```

**`entries` 是关键词 —— 报名/抽奖提交。没有商品、购物车、运费、支付的店面端点。**

**七步尺子不合身，与 goat/popmart/superswipe 同类。**

### 但复刻件那 71% 是猜出来的

`HypeCommerceFlow` 有 8 个 override，**而它的商品/购物车/订单路径在镜像里没有依据。**

**两件事要分开：**

- **豁免**回答「尺子合不合身」→ **不合身**
- **它不回答「那条链对不对」** → **71% 是猜的，没人验过**

> **所以豁免的同时把它单独立项 —— 否则豁免会顺手把一个隐藏问题一起藏掉。**

### 新立项

**要么按 entries API 重写（`validate` → `create`，形状可照抄），要么降级成诚实失败。**
**这一轮没做，因为那是另一个决定，不是豁免的连带动作。**

### 口径

```
resolved 63/63 · fully covered 51 · exempt 6
```

**分母 58 → 57，`fully covered` 仍 51 —— 不是覆盖率上升，是分母变化。**

### 验证

```
只改测试的豁免表 · hypecommerce 71%（yardstick does not apply）· 整套 1766 / 0 · 度量未变
```

### 仍然 Unknown

`entries` 的请求体 · `payment/methods/store` 用途 · **镜像有没有店面面（只搜过 `hypecommerce` 这一个写法）** · 那 71% 里有没有一步是对的
"""

BACKLOG_ADD = """

## 覆盖 — hypecommerce 豁免，但它的链是猜的（R797）

```
resolved 63/63 · fully covered 51 · exempt 6
分母 58 → 57（不是覆盖率上升，是分母变化）
```

**镜像只有 6 条，全是 `admin.hypecommerce.io/api/*`：`entries/create` · `entries/validate` ·
`payment/methods/store` · `settings`。`entries` = 报名/抽奖提交 → 七步尺子不合身。**

## **新立项：`HypeCommerceFlow` 那条链没依据**

| 现状 | 问题 |
|---|---|
| 8 个 override、71% | **商品/购物车/订单路径在镜像里一条依据都没有** |
| 镜像真实形状 | `entries/validate` → `entries/create`（可照抄） |

**两条出路**：① 按 entries API 重写；② 降级成诚实失败。
**判断倾向**：entries 的形状是**可照抄的**，比现在这条猜的链更有据。

**没做的原因**：这是改 8 个 override 的方向决定，**不是豁免的连带动作。**

| 仍 Unknown | |
|---|---|
| `entries` 请求体 | 端点有、字段没有 |
| `payment/methods/store` 用途 | 不明 |
| **镜像有没有 hypecommerce 的店面面** | **只搜过 `hypecommerce` 一种写法**（§2.7） |
| 那 71% 里有没有一步对 | 没人验过 |
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R797", BLOCKER)
    ensure(RSTATUS, "R797", BLOCKER)
    ensure(RVERDICT, "第 797 轮", VERDICT)
    ensure(BACKLOG, "R797", BACKLOG_ADD)

    ok = True
    for path in (RBLOCK, RSTATUS, RVERDICT, BACKLOG):
        body = io.open(path, encoding="utf-8").read()
        key = "第 797 轮" if path == RVERDICT else "R797"
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R797: hypecommerce is exempted, and the replica's guessed chain is filed as a separate problem\n\n"
         "The image carries six strings for hypecommerce and every one is admin.hypecommerce.io/api/*: entries/create,\n"
         "entries/validate, payment/methods/store and settings. Entries are raffle or drop entries, validated then\n"
         "created, with no product, cart, shipping or payment endpoint anywhere. So the seven-step yardstick does not\n"
         "fit, for the same reason it does not fit goat, popmart and superswipe.\n\n"
         "What that does not settle is the replica's own HypeCommerceFlow, which overrides eight methods and scores\n"
         "seventy-one percent against paths the image gives no support for. Exemption answers whether the yardstick\n"
         "fits; it says nothing about whether those paths are right. Filing the exemption without saying so would let\n"
         "it quietly cover a guessed implementation, so the chain is recorded as its own open item: either rewrite it\n"
         "against the entries API, whose validate-then-create shape can actually be copied, or degrade it to honest\n"
         "failure.\n\n"
         "No product code changed this round. The denominator falls from 58 to 57 while fully covered stays at 51,\n"
         "which is the same arithmetic the R793 exemptions needed saying out loud: the percentage moves because the\n"
         "denominator moved.\n\n"
         "Unknown: the entries request bodies; what payment/methods/store is for; whether the image has a storefront\n"
         "face for hypecommerce that simply does not contain that word; and whether any of the current seventy-one\n"
         "percent is right.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
