"""Record R830: the replica's PopMart /shop/v1 surface is image-backed, and three other surfaces are not modelled."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

BLOCKER = """

---

## 254. PopMart：**复刻件的 13 个 `/shop/v1` 端点全部有镜像对应**；而镜像另有三个面没建模

> R830。未改产品代码。**这一轮差点写出一个假缺口。**

### 一、我是怎么差点搞错的

R294 在 `PopMartEndpoints.cs` 留了一句自注：

```csharp
"/api/cart/add", "/api/order/submit", "/api/stock",   // inferred: no image evidence (R294)
```

**验证它 —— 三个都 0 匹配，自注正确：**

```
api/cart/add     0
api/order/submit 0
api/stock        0
popmart         38
```

**然后我搜 `popmart` 拿到 16 条 URL 形态的串，里面是 `prod-*-api.popmart.com`、`/web/v2?partner=`、
`activity/v1`、`popDraw.json` —— 而我在复刻件里逐个查，全是 0：**

```
prod-apac-api 0 · prod-global-api 0 · prod-hk-api 0 · prod-na-api 0 · prod-uk-online 0
appKey 0 · activity/v1 0 · exhibit_draw 0 · popDraw 0
RpcHandler 0 · PopMartBrowser 0 · PopMartField 0 · PopMartProductType 0
```

**那时候结论已经成形：「镜像有一整套 PopMart 接口，复刻件一个都不知道」。**

**而它是错的。**

### 二、为什么错

**我搜的是 `popmart` 这个词，于是只拿到「串里含 popmart」的那些。**
**而复刻件的端点串是 `/shop/v1/box/box_set/preview` 这种 —— 不含 `popmart`。**

**查一次 `/shop/v1/` 就够了：**

```
/shop/v1/     41 matches
0x146ab803c   /shop/v1/box/boxCart/addBoxListToCart
0x146ab809c   /shop/v1/box/box_set/extract
0x146ab80ec   /shop/v1/box/box_set/preview
0x146ab813c   /shop/v1/box/box_spu/detail
0x146ab818c   /shop/v1/box/extract
0x146ab81cc   /shop/v1/box/goodsListV2
0x146ab861c   /shop/v1/order/pre/v2/buyNow
```

**复刻件那 13 个端点全部有镜像对应。它没错。**

### 三、真正成立的结论

**复刻件模型的是 `/shop/v1` 这条店铺面，镜像里有它 —— 而且镜像另外还有三块复刻件没有的：**

| 面 | 镜像证据 | 复刻件 |
|---|---|---|
| **6 个区域 API 主机** | `prod-apac-api` / `prod-global-api` / `prod-hk-api` / `prod-mo-api` / `prod-na-api` / `prod-uk-online-api` `.popmart.com` | **0** |
| **appKey 认证的 web API** | `/web/v2?partner=popmart&appKey=` | **0** |
| **活动抽签 API** | `https://prod-hk-actapi.popmart.com/activity/v1/activity/sample_info?key=`<br>`…/activity/v1/exhibit_draw/draw?` | **0** |
| **抽签数据源** | `https://cdn-global.popmart.com/global-activities/json/popDraw.json?t=` | **0** |
| **GraphQL buynow** | `0x14713e034`: `query buynow { buynow(item: {sku: "", qty: 1, quote_id: "1", type: "Simpl…` | 未查 |
| **类型** | `PopMartRpcHandler` · `PopMartHandler` · `PopMartBrowser` · `PopMartField` · `$PopMartProductType` | **0** |

**所以 PopMart 这一站的形态是：店铺面（`/shop/v1`，复刻件有）+ 区域 API + 活动抽签 + GraphQL —— 后三块复刻件没有。**

### 四、这个缺口该怎么定性

**不是「复刻件搞错了」，是「复刻件只做了一面」。**
**而 `PopMartFlow` 在覆盖矩阵里算「已实现」—— 那个「已实现」现在要理解为「`/shop/v1` 这面实现了」。**

**这不是缺陷声明，是覆盖面的事实。**

### 五、验证

```
python analysis\\ida.py str "/shop/v1/"          -> 41 matches，含复刻件那 13 个的原文
python analysis\\ida.py str "api/cart/add"       -> 0（复刻件自注正确）
python analysis\\ida.py str "prod-na-api"        -> 有；复刻件 0
本轮未改产品代码
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 六、仍然 Unknown

- **那三块面是否属于「下单流程」**：**Unknown** —— 区域 API 与 appKey 很像下单路径，
  **但活动抽签是另一条业务线（抽签买盒），可能不属于 checkout。**
  **这一条要用 R829 的路线（xrefs → MoveNext）去看哪个函数用它们。**
- **`PopMartBrowser` 是什么**：**Unknown** —— 名字暗示浏览器路径，**可能与 captcha 有关（优先级 ②）。**
- **区域 API 与 `/shop/v1` 的关系**：**Unknown** —— 是同一后端的两个入口，还是不同的主机分工，**没查。**

### 七、教训

**我搜 `popmart`，于是只找到含 `popmart` 的串；复刻件的串不含它，于是「复刻件全无」这个结论凭空成立。**

**这已经是同一族的第 N 次：先按一个词搜，再把「这个词没搜到」读成「不存在」。**
**而这一次的错更大 —— 它会把一个基本正确的实现说成「一个都不知道」。**

**挡住它的动作只有一个：搜镜像时用「复刻件实际写的那个串」，不用「站名」。**
"""

VERDICT = """

---

## 第 830 轮：PopMart 的 `/shop/v1` 全部有镜像对应 —— 我差点写出假缺口

### 差点搞错的过程

R294 自注「`/api/cart/add` 等无镜像证据」→ **验证：三个都 0，自注正确。**

然后搜 `popmart` 得 16 条 URL，逐条在复刻件里查——**全是 0**：

```
prod-*-api.popmart.com · /web/v2?partner=&appKey= · activity/v1 · popDraw.json · PopMartRpcHandler …
```

**结论已经成形：「镜像有一整套 PopMart 接口，复刻件一个都不知道」。而它是错的。**

### 为什么错

**我搜的是站名 `popmart`，而复刻件的端点串是 `/shop/v1/box/box_set/preview` —— 不含站名。**

```
/shop/v1/  41 matches，含 0x146ab803c addBoxListToCart / 0x146ab861c buyNow 等
```

> **复刻件那 13 个端点全部有镜像对应。它没错。**

### 真正成立的结论

**复刻件做的是 `/shop/v1` 店铺面（镜像有），而镜像另外还有三块它没有：**

| 面 | 复刻件 |
|---|---|
| 6 个区域 API 主机 `prod-{apac,global,hk,mo,na,uk-online}-api` | **0** |
| appKey web API `/web/v2?partner=popmart&appKey=` | **0** |
| 活动抽签 `activity/v1/sample_info` · `exhibit_draw/draw` · `popDraw.json` | **0** |
| GraphQL `query buynow {...}`（`0x14713e034`） | 未查 |

**定性：不是「搞错了」，是「只做了一面」。** 覆盖矩阵里 PopMart 的「已实现」应读作「`/shop/v1` 这面实现了」。

### 仍然 Unknown

**那三块是否属于下单流程**（区域 API 与 appKey 像，但抽签是另一条业务线）· **`PopMartBrowser` 是什么**（可能与 captcha 有关）· **区域 API 与 `/shop/v1` 的主机分工**

### 教训

**我搜站名，于是只找到含站名的串；复刻件的串不含它，于是「复刻件全无」凭空成立。**

**挡住它的动作只有一个：搜镜像时用「复刻件实际写的那个串」，不用「站名」。**
"""

BACKLOG_ADD = """

## 优先级 ① — PopMart：`/shop/v1` 已覆盖，另有三块未建模（R830）

**复核件自注（R294）正确**：`/api/cart/add` · `/api/order/submit` · `/api/stock` 在镜像里**都是 0**。

**复刻件的 13 个 `/shop/v1/...` 端点全部有镜像对应**（`/shop/v1/` 共 41 matches，
含 `0x146ab803c addBoxListToCart`、`0x146ab861c buyNow` 等）。

### 未建模的三块（镜像有、复刻件 0）

| 面 | 镜像证据 |
|---|---|
| 6 个区域 API 主机 | `prod-{apac,global,hk,mo,na,uk-online}-api.popmart.com` |
| appKey web API | `/web/v2?partner=popmart&appKey=` |
| 活动抽签 | `prod-hk-actapi.popmart.com/activity/v1/activity/sample_info` · `…/exhibit_draw/draw` · `cdn-global…/popDraw.json` |
| GraphQL | `0x14713e034`: `query buynow { buynow(item: {sku: "", qty: 1, quote_id: "1"…` |

**类型名（复刻件全 0）**：`PopMartRpcHandler` · `PopMartHandler` · `PopMartBrowser` · `PopMartField` · `$PopMartProductType`

**定性**：不是「搞错了」，是「只做了一面」。覆盖矩阵里 PopMart 的「已实现」= `/shop/v1` 这面。

| 仍 Unknown | |
|---|---|
| 三块面是否属下单流程 | 区域 API/appKey 像；**抽签是另一条业务线** |
| `PopMartBrowser` 是什么 | 可能与 captcha 有关（优先级 ②） |
| 区域 API 与 `/shop/v1` 分工 | 未查 |

### 纪律（重要）

**搜镜像时用「复刻件实际写的那个串」，不要用「站名」。**
搜 `popmart` 只得到含站名的串；复刻件的 `/shop/v1/...` 不含它 —— **于是「复刻件全无」凭空成立**。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R830", BLOCKER)
    ensure(RSTATUS, "R830", BLOCKER)
    ensure(RVERDICT, "第 830 轮", VERDICT)
    ensure(BACKLOG, "R830", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R830" not in h:
        h += ("\n## R830 补充 — PopMart 覆盖面\n\n"
              "复刻件的 13 个 `/shop/v1/...` 端点**全部有镜像对应**（`/shop/v1/` 41 matches）。"
              "自注「`/api/cart/add` 等无证据」也正确（0 匹配）。\n"
              "**镜像另有四块未建模**：6 个 `prod-*-api.popmart.com` 区域主机 · `/web/v2?partner=&appKey=` · "
              "`activity/v1` 抽签 + `popDraw.json` · GraphQL `query buynow`。\n"
              "**教训：搜镜像用「复刻件实际写的那个串」，不要用「站名」** —— 用站名会凭空得出「复刻件全无」。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R830"), (RSTATUS, "R830"), (RVERDICT, "第 830 轮"), (BACKLOG, "R830")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R830: PopMart's /shop/v1 surface is image-backed, and I nearly recorded a false gap\n\n"
         "PopMartEndpoints carries a note from R294 that three endpoints have no image evidence. They do not: api/cart/add,"
         " api/order/submit and api/stock are all absent, so the note is right.\n\n"
         "Then I searched the image for `popmart`, got sixteen URL-shaped strings -- six regional prod hosts, an appKey web"
         " path, activity draw endpoints, a popDraw feed -- and searched the replica for each, finding zero everywhere."
         " The conclusion had already formed: the image has a whole PopMart surface the replica knows nothing about. That"
         " conclusion was wrong.\n\n"
         "It was wrong because I searched for the site name. The replica's endpoints read /shop/v1/box/box_set/preview and"
         " the like, containing no `popmart` at all. One search for /shop/v1/ returns 41 matches including"
         " addBoxListToCart at 0x146ab803c and buyNow at 0x146ab861c -- every one of the replica's thirteen endpoints is"
         " present in the image. The replica is right about the surface it models.\n\n"
         "What actually holds is narrower and more useful. The replica models the /shop/v1 shop surface; the image has"
         " that plus four things it does not model: six regional prod-*-api hosts, an appKey-authenticated web path at"
         "/web/v2?partner=popmart&appKey=, an activity draw surface with sample_info, exhibit_draw/draw and a popDraw"
         " JSON feed, and a GraphQL buynow query visible at 0x14713e034. The types PopMartRpcHandler, PopMartHandler,"
         " PopMartBrowser, PopMartField and PopMartProductType are absent from the replica entirely.\n\n"
         "So this is not a wrong implementation but a partial one, and the coverage matrix's entry for PopMart should be"
         " read as /shop/v1 being implemented rather than the site being covered.\n\n"
         "Unknown: whether the regional API and appKey paths belong to checkout, since they look like order paths while"
         " the activity draw is a separate business line; what PopMartBrowser is, which by its name may touch captcha and"
         " therefore priority two; and how the regional hosts divide work with /shop/v1.\n\n"
         "The lesson is mechanical and I have now hit its family many times: searching by site name only finds strings"
         " containing the site name, and the replica's strings do not contain it, so absence of evidence looked like"
         " evidence of absence for an implementation that is largely correct. Search using the string the replica"
         " actually writes.\n\n"
         "No product code changed; four metrics unchanged at 4 / 0 / 17 / 78 / 0."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
