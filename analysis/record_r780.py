"""Record R780: Casio and HypeCommerce cannot be closed by adding steps either."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 206. `casio` 与 `hypecommerce` 也补不了两步 —— 一个是字段名不是端点，一个是抽奖面

> R780。未改产品代码。

### 一、`casio` 的原版面（15 条字符串，Observation）

```
CasioRegion
CasioAU · CASIO · CASIO Australia · Casio · Casio Login · Casio SG · Casio US
casio.com · casiostore.bhawar.com
casio_can_purchase · casio_dob · casio_gender · casio_image_url · casioid
adyen:  _adyenOrderId   （与 RecaptchaSiteKey 同处一条配置记录）
```

**读出来的是：分区（AU / SG / US）+ 登录 + 五个蛇形商品字段 + 一个 Adyen 订单号字段。**
**没有任何结账端点。**

**而 R767 我把它算进"有 2 个结账面 URL"，那两条其实是 `_adyenOrderId` 与 Square PCI hydrate ——
后者是全站共用的支付层，前者是字段名。** **所以那个分类是我数错了。**

### 二、复刻件这一侧：它其实用了镜像证据

`CasioFlow` 有 8 个 override（GetHome / GetCaptcha / SolveCaptcha / FindProduct / FindVariant /
ScrapeVariantAvailability / AddToCart / SubmitOrder / GetCheckout），**71% = 5/7，缺的正是 shipping + payment。**

**而它的 `RecaptchaSiteKey = "6LfeU4ofAAAAAHTDXnfN1V9EroVWvwEPeqrXybdj"`
正是原版 Casio 配置记录里那一串。**

**但 `CasioRegion` / 五个 `casio_*` 字段 / 三个区域名 / `casiostore` 在复刻件里全部 ABSENT。**
**所以 Casio 的缺口不是"缺两步"，是"镜像给的整张配置面没用上"** —— 那比缺两步更值得做，
**但它也不是补两个方法能解决的。**

### 三、`casio` 的支付步为什么补不了

**原版说是 Adyen（`_adyenOrderId`），但那是字段名，不是端点。**
**知道用哪家、不知道往哪发 —— 这不是缺口，这是信息不足。**
**拿一个猜出来的 URL 去补，正是 R772 的错。**

### 四、`hypecommerce` 是抽奖面

```
admin.hypecommerce.io/api/entries/create
admin.hypecommerce.io/api/entries/validate
admin.hypecommerce.io/api/payment/methods/store
admin.hypecommerce.io/api/settings
```

**`entries/validate` + `entries/create` 是「先校验再提交一次报名」** —— 抽奖形状，不是七步结账。

而 `HypeCommerceFlow` 有 8 个 override，**5/7 = 71%**，缺 shipping + payment。
**它和 `raffle` / `pocketgames` / `riotgames` 属于同一类：七步尺子不合身。**

### 五、所以 R765 那张"12 个下不了单"的表，逐条查完之后是这样

| 站 | 判定 |
|---|---|
| scheels · hbx | **已补齐到 100%**（R766/R767，端点本来就在镜像里） |
| fanatics · yeezysupply | **不是缺口** —— 原版没有结账面（R769，已进豁免） |
| offspring | 两种表面；网页 Hybris 已 100%，App 面另建（R779） |
| casio | **缺的不是两步，是整张配置面**；支付家数已知、端点未知 |
| hypecommerce | **抽奖面，尺子不合身** |
| warhammer | **Unknown** —— GraphQL，mutation 未取证 |
| goat · popmart · superswipe | 抽奖面，尺子未定 |
| bstn | **原版 0 字符串** —— 复刻件多出来的 |

**12 个里：2 个真补齐、2 个证明不是缺口、1 个拆成两件事、其余 7 个是"尺子或信息"问题。**
**"12 个下不了单"这个说法本身，现在看是过于笼统的。**

### 六、验证

```
本轮未改产品代码
完整套件保持 1752 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- `casio` 的 Adyen 端点：**Unknown** —— 只有字段名。
- `casio` 的五个蛇形字段如何取用：**Unknown** —— 只知道名字。
- `hypecommerce` 的 `entries/create` 请求体：**Unknown**。
- `goat` / `popmart` / `superswipe` 的尺子：**Unknown**。
"""

VERDICT = """

---

## 第 780 轮：逐条查完之后，「12 个下不了单」这个说法站不住了

### casio

镜像给的是**分区 + 登录 + 五个蛇形字段 + 一个 Adyen 订单号字段**，**没有结账端点**。
**而 R767 我把它算成"有 2 个结账面 URL"—— 那两条一个是字段名，一个是全站共用的 Square PCI。数错了。**

复刻件这一侧：8 个 override，71%（缺 shipping + payment），
**而且它确实用了镜像证据**（`RecaptchaSiteKey` 就是 Casio 配置里那串）。
**但 `CasioRegion` 与五个 `casio_*` 字段全 ABSENT** —— 缺的是整张配置面，不是两步。

**支付步补不了**：知道是 Adyen，**但 `_adyenOrderId` 是字段名不是端点**。
拿猜的 URL 去补，正是 R772 的错。

### hypecommerce

`entries/validate` + `entries/create` —— **先校验再报名，抽奖形状。**
与 `raffle`/`pocketgames`/`riotgames` 同类：**七步尺子不合身。**

### R765 那张表的最终样子

| 站 | 判定 |
|---|---|
| scheels · hbx | 已补齐到 100% |
| fanatics · yeezysupply | **不是缺口**（原版没有结账面） |
| offspring | 两种表面，网页已 100%，App 面另建 |
| casio | 缺整张配置面；支付家数已知、端点未知 |
| hypecommerce | 抽奖面，尺子不合身 |
| warhammer | Unknown（GraphQL mutation 未取证） |
| goat · popmart · superswipe | 抽奖面，尺子未定 |
| bstn | 原版 0 字符串 |

> **12 个里：2 个真补齐、2 个证明不是缺口、1 个拆两件事、7 个是「尺子或信息」问题。
> 「12 个下不了单」本身是个过于笼统的结论。**

### 验证

```
产品代码未改；套件 1752 / 0；度量未变
```
"""

BACKLOG_ADD = """

## 核心 — R765 那张表的最终裁定（R780）

| 站 | 判定 | 下一步 |
|---|---|---|
| scheels · hbx | ✅ 已 100% | — |
| fanatics · yeezysupply | ✅ 不是缺口（已进豁免） | — |
| offspring 网页 | ✅ 100% | — |
| offspring App 面 | ✅ 已建 `poq-app`（57%） | 待定任务类型 |
| **casio** | 缺**整张配置面**（`CasioRegion` + 5 个 `casio_*` + 3 区域 + `casiostore`） | **可做**：把镜像的配置面用上 |
| casio 支付 | **信息不足**（Adyen，`_adyenOrderId` 是字段名不是端点） | 未取证 |
| **hypecommerce** | **抽奖面**（`entries/validate` + `entries/create`） | 尺子待定 |
| warhammer | Unknown（GraphQL mutation） | 需读调用方 |
| goat · popmart · superswipe | 抽奖面 | 尺子待定 |
| bstn | **原版 0 字符串** | 待裁决 |

**方法论提醒**：R767 把「字段名 + 共用支付层字符串」数成了「该站有 2 个结账 URL」。
**数 URL 之前先看它是不是那个站自己的端点** —— 这是 §2.7 的又一次。
"""


def main():
    for p, marker, text in ((P1, "R780", BLOCKER), (P3, "R780", BLOCKER), (P2, "第 780 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R780" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += 最终裁定表")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R780: Casio and HypeCommerce cannot be closed by adding steps either -- and the '12 modules' framing was too broad\n\n"
         "Casio's surface in the image is fifteen strings: a region field, three region names (AU, SG, US), a login,\n"
         "five snake-case product fields, a store host, and an Adyen order-id field that sits in the same configuration\n"
         "record as its reCAPTCHA site key. There is no checkout endpoint among them. So R767's classification of casio\n"
         "as having two checkout URLs was wrong: one of those two is a field name and the other is a Square PCI string\n"
         "shared across every store.\n\n"
         "The replica's CasioFlow does use image evidence -- its reCAPTCHA site key is exactly the one from that\n"
         "record -- and its eight overrides give five of seven. But CasioRegion, the five casio_ fields, the three\n"
         "region names and the store host are all absent, so what it is missing is the whole configuration surface\n"
         "rather than two methods. And the payment step cannot be added: the image says Adyen, but _adyenOrderId is a\n"
         "field name rather than an endpoint, so the vendor is known and the target is not. Inventing a URL there\n"
         "would repeat R772.\n\n"
         "HypeCommerce is a raffle surface. entries/validate then entries/create is check-then-enter, which puts it\n"
         "with raffle, pocketgames and riotgames: modules where the seven-step commerce yardstick does not fit.\n\n"
         "That leaves R765's table in a different shape than it started. Two are genuinely closed, two are proven not\n"
         "to be gaps because the original has no checkout either, one splits into two problems, and seven are questions\n"
         "of yardstick or missing information rather than unfinished work. 'Twelve modules cannot place an order' was\n"
         "too broad a reading of a percentage column.\n\n"
         "No product code changed; suite remains 1752 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
