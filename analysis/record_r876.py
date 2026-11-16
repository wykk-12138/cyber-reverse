"""Record R876: the DrawStores model's field set and its own step sequence."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### 顺着 `_uniqCode` 往上读，读到一整个模型和它自己的序列（R876）

**R875 说请求体键不在端点旁。下一处自然是模型字段旁 —— `_uniqCode` 在 `0x1433803a5`。**

**`0x143380300`–`0x143380900` 有 51 条串，分三段：**

**① 一个模型的后备字段表（3 字节对齐，紧凑排布）：**

```
_turnstileKey  _userCouponId  _mpUserCouponId  _setNo  _boxes
_drawid  _uniqCode  _hasDrawEntry  _winner  _drawLogId  _drawGoodsId
_luckAlias  _memberAlias  _eventId  _dates  _slots  _blockedSlots  _startTime
_uuidRegex  _rpcFingerprint  _rpcAddressId  _rpcFreightExpressId  _rpcFreightAmount
_rpcPayAmount  _rpcWarehouse  _rpcAdyenPayId  _rpcAdyenClientKey  _rpcPayPalPayId  _tasks
```

**② 四个枚举/属性名：`AppMode` · `TimeZone` · `DrawLocation` · `DrawIdentityType` · `IsRpc`**

**③ 一条带 ordinal 的步骤序列，前面就是它的归属名：**

```
0x143380392  DrawStores                      ← 模型名
0x143380569  <Start>d__21                     21
0x143380581  <GetHome>d__23                   23
0x14338059b  <CheckVerification>d__24         24
0x1433805d0  <SubmitSaleRegistration>d__25    25
0x14338060a  <CheckLogin>d__26                26
0x143380676  <Register>d__27                  27
0x143380753  <CompleteRegistration>d__28      28
0x143380833  <GetCart>d__30                   30
0x14338085d  <ClearCart>d__31                 31
0x1433808c3  <FindProduct>d__32               32
0x1433808e2  <AddToCart>d__33                 33
0x1433808ff  <ReplaceProduct>d__34            34
```

**这是第九条序列，而它有名字：`DrawStores` —— R869 说「5 条序列没有落点」，这一条现在有了。**

### 它回答了两个问题，但都不是完整的

**① 请求体键可能是字段名去掉下划线。**
`_drawid` → `drawId`? · `_drawGoodsId` → `drawGoodsId` · `_eventId` → `eventId` · `_memberAlias` → `memberAlias`

**这是 Inference，不是 Observation。**字段名叫 `_drawid` 而 JSON 键可能叫 `drawId`、`DrawId` 或别的。
**就像 R859 那条：属性语法是 `Cybersole.Models.<Type>,Cybersole.Core.<Prop>!Getter`，
名字能对上但大小写和形态要另外证。**

**② `DrawStores` 是一个独立流程，不是 PopMart 的别名。**
它的序列从 21 开始（PopMart 的从 104 开始），前几步是 `CheckVerification` / `SubmitSaleRegistration` /
`CheckLogin` / `Register` / `CompleteRegistration` —— **是注册/登录流程，不是抽签流程。**

**所以 `DrawStores` 这个名字有误导性：它带的序列是「门店/发售注册」，不是「抽签」。**

### 两条排除掉的路

| 探针 | 结果 |
|---|---|
| 12 个 `/shop/v1` 端点是否都在 `PopMartEndpoints` | **12/12 都在，39 个端点无缺口** |
| draw 端点附近有没有请求体键 | **没有 —— 那一段全是按字母序的路径表** |

**所以剩下的工作不是端点发现，而是「键名与形态」。**
"""

if "顺着 `_uniqCode` 往上读，读到一整个模型和它自己的序列（R876）" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R876 appended")

BLOCKER = """

---

## 300. 读到第九条序列，而它有名字：`DrawStores`

> R876。未改产品代码。

### 一、两条路排除了，第三条给出了东西

| 探针 | 结果 |
|---|---|
| 12 个 `/shop/v1` 端点是否都在 `PopMartEndpoints` | **12/12 都在；39 个端点无缺口** |
| draw 端点附近（`0x146ab82xx`）有没有请求体键 | **没有 —— 全是按字母序的路径表** |
| **模型字段附近（`0x1433803xx`）** | **51 条：模型字段表 + 枚举名 + 一条带 ordinal 的序列** |

### 二、模型字段表

```
_turnstileKey  _userCouponId  _mpUserCouponId  _setNo  _boxes
_drawid  _uniqCode  _hasDrawEntry  _winner  _drawLogId  _drawGoodsId
_luckAlias  _memberAlias  _eventId  _dates  _slots  _blockedSlots  _startTime
_rpcFingerprint  _rpcAddressId  _rpcFreightExpressId  _rpcFreightAmount
_rpcPayAmount  _rpcWarehouse  _rpcAdyenPayId  _rpcAdyenClientKey  _rpcPayPalPayId
```

**`_turnstileKey` 值得单独看一眼 —— Turnstile 是 Cloudflare 的验证控件（优先级 ② 的东西），
它作为**模型字段**出现，说明 token 是存在模型里而不是临时变量。**

**`_rpc*` 一族（Adyen / PayPal / Freight / Warehouse）说明这个模型同时承载支付与运费 ——
它不是「抽签模型」，是一个**结账上下文**。**

### 三、第九条序列，有名字

```
0x143380392  DrawStores
21 Start  23 GetHome  24 CheckVerification  25 SubmitSaleRegistration
26 CheckLogin  27 Register  28 CompleteRegistration
30 GetCart  31 ClearCart  32 FindProduct  33 AddToCart  34 ReplaceProduct
```

**R869 说「5 条序列没有落点」。这一条现在有名字了：`DrawStores`。**

**而名字有误导性：**这串步骤是注册/登录/购物车，不是抽签。**
`CheckVerification` / `SubmitSaleRegistration` / `CheckLogin` / `Register` / `CompleteRegistration` ——
**这是「发售注册流程」，不是「抽签流程」。**

**它不是 PopMart 的别名：PopMart 的序列从 104 起，这条从 21 起。**

### 四、请求体键可能是字段名，但这是 Inference

| 字段 | 可能的键 |
|---|---|
| `_drawid` | `drawId`? `DrawId`? |
| `_drawGoodsId` | `drawGoodsId` |
| `_eventId` | `eventId` |
| `_memberAlias` | `memberAlias` |

**这是 Inference 不是 Observation。**R859 的教训正好适用：属性语法能对上名字，
**但大小写与形态要另外证。**

**所以我没有拿这些字段去写那七个 POST 步骤 —— 那会把 Inference 当 Observation 用。**

### 五、验证

```
idautils.Strings() @0x146AB8200–0x146AB8600 -> 13 条，全是 /shop/v1/... 路径表（无请求体键）
idautils.Strings() @0x143380300–0x143380900 -> 51 条 = 字段表 + 枚举名 + 序列（含 DrawStores 与 21–34）
PopMartEndpoints 对比 12 个端点          -> 12/12 HAVE，共 39 个端点
本轮未改产品代码
```

### 六、仍然 Unknown

- **`DrawStores` 在复刻件里对应哪个类**：**Unknown** ——
  **它的步骤名（`CheckVerification` / `SubmitSaleRegistration` / `CompleteRegistration`）
  在 `StoreFlow` 里有没有？没查。这是下一轮第一件事，一条 `where_is` 就有答案。**
- **请求体键的真实形态**：**Unknown** —— 字段名去掉下划线是 **Inference**。
- **`_turnstileKey` 属于哪个验证流程**：**Unknown** ——
  **它作为模型字段出现，说明 token 存进模型；但谁产生、什么时候清，未查。**

### 七、教训

**我先猜「请求体键在端点旁」，错了；再猜「在字段旁」，对了一半 ——
对的不是请求体键，是模型字段表和一条序列。**

**而这两样里，序列是**意外收获**：我去找请求体，找到了 `DrawStores`。**

**所以「顺着一个名字读它周围」这个动作，回报不在预期之处是常态。
而它这次回报的东西，正好填了 R869 留的一个空洞 —— 那条洞我以为要专门去找。**
"""

VERDICT = """

---

## 第 876 轮：读到第九条序列，而它有名字 —— `DrawStores`

### 两条路排除了，第三条给出东西

| 探针 | 结果 |
|---|---|
| 12 个 `/shop/v1` 端点是否都在 `PopMartEndpoints` | **12/12 都在；39 个端点无缺口** |
| draw 端点附近（`0x146ab82xx`）有没有请求体键 | **没有 —— 全是按字母序的路径表** |
| **模型字段附近（`0x1433803xx`）** | **51 条：字段表 + 枚举名 + 一条带 ordinal 的序列** |

### 模型字段表

```
_turnstileKey  _userCouponId  _setNo  _boxes
_drawid  _uniqCode  _hasDrawEntry  _winner  _drawLogId  _drawGoodsId
_luckAlias  _memberAlias  _eventId  _dates  _slots  _blockedSlots  _startTime
_rpcFingerprint  _rpcFreightAmount  _rpcAdyenPayId  _rpcAdyenClientKey  _rpcPayPalPayId
```

> **`_turnstileKey` 是 Cloudflare Turnstile 的 token，而它作为**模型字段**出现 ——
> 说明 token 存在模型里而不是临时变量。这是优先级 ② 的一条线索。**
> **`_rpc*` 一族（Adyen/PayPal/Freight/Warehouse）说明这个模型是**结账上下文**，不是「抽签模型」。**

### 第九条序列，有名字

```
0x143380392  DrawStores
21 Start  23 GetHome  24 CheckVerification  25 SubmitSaleRegistration
26 CheckLogin  27 Register  28 CompleteRegistration
30 GetCart  31 ClearCart  32 FindProduct  33 AddToCart  34 ReplaceProduct
```

**R869 说「5 条序列没有落点」，这一条现在有名字了。**

**而名字有误导性：这串步骤是注册/登录/购物车，不是抽签。
`CheckVerification` / `SubmitSaleRegistration` / `Register` / `CompleteRegistration` = **发售注册流程**。
它不是 PopMart 的别名（PopMart 从 104 起，这条从 21 起）。**

### 请求体键可能是字段名 —— 但那是 Inference

| 字段 | 可能的键 |
|---|---|
| `_drawid` | `drawId`? `DrawId`? |
| `_drawGoodsId` | `drawGoodsId` |
| `_eventId` | `eventId` |

> **这是 Inference 不是 Observation。R859 的教训适用：属性名能对上，大小写与形态要另外证。**
> **所以我没有拿这些去写那七个 POST 步骤 —— 那会把 Inference 当 Observation 用。**

### 仍然 Unknown

**`DrawStores` 在复刻件里对应哪个类**（**它的步骤名在 `StoreFlow` 里有没有？没查 —— 下一轮一条 `where_is` 就有答案**）·
**请求体键的真实形态**（去下划线是 Inference）· **`_turnstileKey` 谁产生谁清**

### 教训

> **我先猜「请求体键在端点旁」，错了；再猜「在字段旁」，对了一半 —— 对的不是请求体键，是字段表和一条序列。**
> **而序列是**意外收获**：我去找请求体，找到了 `DrawStores`。**
> **所以「顺着一个名字读它周围」这个动作，回报不在预期之处是常态。而它这次回报的东西，正好填了 R869 留的一个空洞。**
"""

BACKLOG_ADD = """

## 判据 — 第九条序列有名字：`DrawStores`（R876）

### 三条探针

| 探针 | 结果 |
|---|---|
| 12 个 `/shop/v1` 端点 vs `PopMartEndpoints` | **12/12 HAVE，39 个端点无缺口** |
| draw 端点附近（`0x146ab82xx`） | **13 条全是路径表，无请求体键** |
| **模型字段附近（`0x1433803xx`）** | **51 条 = 字段表 + 枚举名 + 序列** |

### 字段表要点

**`_turnstileKey`（Cloudflare Turnstile token，**作为模型字段存在**）· `_drawid` `_uniqCode` `_winner`
`_drawLogId` `_drawGoodsId` `_eventId` `_memberAlias` `_luckAlias` `_dates` `_slots` `_startTime`
`_rpcFingerprint` `_rpcAdyen*` `_rpcPayPal*` `_rpcFreight*`** → **这是结账上下文模型，不是抽签模型。**

### 第九条序列，有名字

```
DrawStores: 21 Start · 23 GetHome · 24 CheckVerification · 25 SubmitSaleRegistration
            26 CheckLogin · 27 Register · 28 CompleteRegistration
            30 GetCart · 31 ClearCart · 32 FindProduct · 33 AddToCart · 34 ReplaceProduct
```

**→ R869「5 条序列无落点」里的一条现在有名字。**
**⚠ 名字误导：这串是**发售注册流程**，不是抽签。也不是 PopMart 的别名（104 vs 21）。**

| 仍 Unknown | |
|---|---|
| **`DrawStores` 对应复刻件哪个类** | **下一轮一条 `where_is` 就有答案** |
| 请求体键真实形态 | 去下划线是 **Inference**（R859 教训） |
| `_turnstileKey` 谁产生谁清 | 未查（优先级 ② 线索） |

**纪律**：**顺着名字读周围，回报常在预期之外 —— 这次要请求体，拿到了 `DrawStores`。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R876", BLOCKER)
    ensure(RSTATUS, "R876", BLOCKER)
    ensure(RVERDICT, "第 876 轮", VERDICT)
    ensure(BACKLOG, "R876", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R876" not in h:
        h += ("\n## R876 补充 — 第九条序列有名字：`DrawStores`\n\n"
              "**两条探针空手**：12 个 `/shop/v1` 端点 12/12 已在 `PopMartEndpoints`（39 个无缺口）；draw 端点附近全是路径表，**无请求体键**。\n"
              "**第三条给东西**（`0x1433803xx`，51 条）：模型字段表（`_drawid` `_uniqCode` `_winner` `_drawGoodsId` `_eventId` `_memberAlias` `_slots` `_startTime` "
              "`_turnstileKey` `_rpcAdyen*` `_rpcPayPal*`）**+ 第九条序列**：\n"
              "**`DrawStores`: 21 Start · 23 GetHome · 24 CheckVerification · 25 SubmitSaleRegistration · 26 CheckLogin · 27 Register · 28 CompleteRegistration · 30 GetCart · 31 ClearCart · 32 FindProduct · 33 AddToCart · 34 ReplaceProduct**\n"
              "**→ 名字误导：这是**发售注册流程**不是抽签；也不是 PopMart 别名（104 vs 21）。**\n"
              "**`_turnstileKey` 作为模型字段存在 —— 优先级 ② 的一条线索。**\n"
              "**下一轮第一件事：`where_is` 那几个步骤名，看 `DrawStores` 在复刻件里有没有落点。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R876"), (RSTATUS, "R876"), (RVERDICT, "第 876 轮"), (BACKLOG, "R876")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R876: the ninth sequence has a name, and the name misleads\n\n"
         "Two probes came back empty. All twelve shop endpoints in the region R873 drew from are already present in"
         " PopMartEndpoints, which holds thirty-nine with no gap, so the endpoint layer is not where the work is. And"
         " the region around the draw endpoints holds thirteen strings, every one a sorted path, with no request-body"
         " keys among them -- so bodies are not adjacent to endpoints either.\n\n"
         "Reading around _uniqCode instead produced fifty-one strings in three groups: a model's backing fields, four"
         " enum or property names, and a step sequence with compiler ordinals.\n\n"
         "The field list carries _drawid, _hasDrawEntry, _winner, _drawLogId, _drawGoodsId, _luckAlias, _memberAlias,"
         " _eventId, _dates, _slots, _blockedSlots and _startTime, which are draw-shaped, alongside _rpcFreightAmount,"
         " _rpcAdyenPayId, _rpcAdyenClientKey and _rpcPayPalPayId, which are checkout-shaped. So this is not a draw"
         " model but a checkout context that happens to carry draw fields. And _turnstileKey is a Cloudflare Turnstile"
         " token sitting in the model rather than in a local, which is a lead for the anti-bot priority.\n\n"
         "The sequence is the ninth and it has a name: DrawStores, with ordinals 21 through 34 -- Start, GetHome,"
         " CheckVerification, SubmitSaleRegistration, CheckLogin, Register, CompleteRegistration, GetCart, ClearCart,"
         " FindProduct, AddToCart, ReplaceProduct. R869 noted five sequences had no flow class claiming them; this is"
         " one of those five and it now has a name.\n\n"
         "The name misleads, and that is worth saying plainly. These steps are registration and login and cart, not"
         " drawing: CheckVerification, SubmitSaleRegistration, Register and CompleteRegistration describe a sale"
         " registration flow. Nor is it an alias for PopMart, whose sequence starts at ordinal 104 while this one"
         " starts at 21.\n\n"
         "It is tempting to treat the field names as the request-body keys the seven unwritten POST steps need, by\n"
         " stripping the underscore. That would be inference dressed as observation -- the same mistake R859 documented"
         " when property syntax matched names but not their shapes -- so the fields are recorded as candidate keys and"
         " the POST steps remain unwritten.\n\n"
         "Unknown: which class in the replica, if any, corresponds to DrawStores, which one where_is call will answer"
         " since the question is whether StoreFlow already declares CheckVerification, SubmitSaleRegistration or"
         " CompleteRegistration; the true form of the request-body keys; and who produces and clears _turnstileKey.\n\n"
         "The lesson is that reading around a name pays out somewhere other than where you were looking. I went for"
         " request bodies and found a sequence -- and it filled a hole R869 left, one I had assumed would need its own\n"
         " round to find.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
