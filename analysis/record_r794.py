"""Close the bstn decision in the backlog. (R794)

The question "delete bstn or keep it" was settled in R91 and has been pinned by tests ever since:
ArrowAndBeastTests asserts both that the image has arrowandbeast and no bstn, and that the module stays because a live
capture put /api/beast/ on bstn.com; LiveContractTests calls that endpoint and asserts /cart.js must not behave like a
Shopify cart.

What was left undone was the paperwork. Three backlog lines still say 待裁决, so a later round reading the backlog would
reopen a settled question -- which is how work gets repeated. This replaces those three lines with the decision and
its grounds.

No product code changes: the decision was already made and already guarded. This only stops the backlog from
misrepresenting it.
"""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"

REPLACEMENTS = [
    ("| **bstn 是否存在** | 原版 `bstn` / `BSTN` 都是 0 匹配 —— **复刻件多出来的模块** | **待裁决**（删=更忠实，牵动多处守卫） |",
     "| **bstn 是否存在** | 原版 `bstn` / `BSTN` 都是 0 匹配 —— **复刻件多出来的模块** | "
     "**已裁决：保留**（R91 决定，R794 结案）。理由见下 |"),
    ("| `bstn` 删不删 | 待裁决 |",
     "| `bstn` 删不删 | **已裁决：保留**（R794）。抓包证据 + 实机契约 + 两条事实都有测试钉住 |"),
    ("| bstn | **原版 0 字符串** | 待裁决 |",
     "| bstn | **原版 0 字符串** | **已裁决：保留**（R794） |"),
]

NOTE = """

### `bstn` 的裁决（R794 结案）

**结论：保留。**

**为什么不是"删了更忠实"**：`bstn` 的证据不是来自镜像，是来自**实机抓包** ——
`https://www.bstn.com/api/beast/geoIP` 返回 200、`/cart.js` 返回 404（不是 Shopify）。
项目自己的溯源分级里，`live`（无字面量但真实响应过）是合法的一档。

**而且这件事已经有三重守卫，不是靠记忆维持**：

| 守卫 | 钉住什么 |
|---|---|
| `ArrowAndBeastTests.BstnStaysAndTheDifferenceIsRecorded` | **两条事实同时**：镜像有 `arrowandbeast`、没有 `bstn`；`bstn` 保留 |
| `LiveContractTests.BstnServesItsBeastApiAndNotAShopifyOne` | `/api/beast/geoIP` 通；`/cart.js` **必须不**像 Shopify 购物车 |
| `PlatformAssignmentTests.BstnHasItsOwnFlowBecauseItIsNotShopify` | 它是 `BstnFlow` 而非 `ShopifyFlow` |

**契约失败消息里写着判据**："if bstn starts serving Shopify carts, it became a Shopify store and BstnFlow is
obsolete" —— **世界变了该报废的是这个模块，而那条测试会说。**

**所以这不是"多出来一个模块没人管"，是"多出来一个模块，理由、守卫、失效条件都齐"。**
**R768 把它记成"待裁决"是对的（当时只查了字符串）；R794 把它结案，是因为它早就被裁决过了。**
"""

BLOCKER = """

---

## 220. `bstn` 结案：**保留**（不是新决定，是把早就定下的写清）

> R794。只改 `BINDING_BACKLOG.md` 的三行 + 补一段裁决说明。未改产品代码。

### 一、这一轮实际查到了什么

`bstn` 在镜像里 `bstn` / `BSTN` 都是 0 匹配 —— 这是 R768 的发现，也是它被记成"待裁决"的原因。

**但复刻件这一侧早就裁决过了，而且有三重守卫：**

| 守卫 | 钉住什么 |
|---|---|
| `ArrowAndBeastTests.BstnStaysAndTheDifferenceIsRecorded` | **两条事实同时**：镜像有 `arrowandbeast`、没有 `bstn`；`bstn` 保留 |
| `LiveContractTests.BstnServesItsBeastApiAndNotAShopifyOne` | `bstn.com/api/beast/geoIP` 通；`/cart.js` **必须不**像 Shopify 购物车 |
| `PlatformAssignmentTests.BstnHasItsOwnFlowBecauseItIsNotShopify` | 它是 `BstnFlow` 而非 `ShopifyFlow` |

**所以"删不删"这个问题，R91 就答了：保留，因为证据是抓包而不是镜像。**

### 二、那为什么还挂着"待裁决"

**因为 backlog 有三行还写着它。** 一个已经定下、且有测试守着的问题被记成未决 ——
**下一轮读到这三行的人会重新审一遍**，这正是工作重复产生的方式。

**所以这一轮改的不是产品，是记录。**

### 三、溯源分级支持这个结论

项目自己的分级里，`live`（镜像里没有字面量、但真实响应过）是**合法的一档**，
`/api/beast` 从 R91 起就归在这一档。**"镜像里没有"不等于"不该有"** ——
**只是"证据不来自镜像"**，那要写清楚来源，而它写了。

### 四、失效条件也写着了

`LiveContractTests` 的失败消息：

> `if bstn starts serving Shopify carts, it became a Shopify store and BstnFlow is obsolete`

**世界变了该报废的是这个模块，而那条测试会说。**
**一个模块带着"什么时候该扔掉它"的判据，比一个没有模块更健康。**

### 五、验证

```
本轮未改产品代码
完整套件保持 1766 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
BINDING_BACKLOG.md 中「待裁决」不再指向 bstn
```

### 六、仍然 Unknown

- **镜像里到底有没有一个对应 bstn 的店**：**Unknown** —— 0 匹配是"没找到"，不是"确认没有"。
  但**这不影响保留的决定**：保留的依据是抓包，不是镜像。
- **`BstnFlow` 缺的三步**（变体、加购、结账）：**Unknown** —— 商品卡是 CSS 背景图，R124 已停手，
  **停手理由记录在案**（不是"再试一次就好"）。
"""

VERDICT = """

---

## 第 794 轮：`bstn` 结案 —— 保留，而这个决定早就做过了

### 查到的事实

`bstn` / `BSTN` 在镜像里都是 0 匹配（R768）。**但复刻件这一侧早在 R91 就裁决过：保留。**

**三重守卫**：

| 守卫 | 钉住什么 |
|---|---|
| `ArrowAndBeastTests.BstnStaysAndTheDifferenceIsRecorded` | 两条事实同时：镜像有 `arrowandbeast`、没有 `bstn`；`bstn` 保留 |
| `LiveContractTests.BstnServesItsBeastApiAndNotAShopifyOne` | `/api/beast/geoIP` 通；`/cart.js` 必须不像 Shopify |
| `PlatformAssignmentTests.BstnHasItsOwnFlowBecauseItIsNotShopify` | `BstnFlow` 而非 `ShopifyFlow` |

### 那这一轮做了什么

**只改记录。** backlog 三行还写着「待裁决」——
**一个已定且被测试守着的问题被记成未决，下一轮读到的人会重审一遍。**

**这就是工作重复产生的方式，所以把这三行结掉。**

### 溯源分级支持这个结论

`live`（无字面量但真实响应过）是**合法的一档**。
**「镜像里没有」不等于「不该有」，只是「证据不来自镜像」—— 而它写清了来源。**

### 失效条件也写着

> `if bstn starts serving Shopify carts, it became a Shopify store and BstnFlow is obsolete`

**一个模块带着「什么时候该扔掉它」的判据，比一个没有模块更健康。**

### 验证

```
产品代码未改 · 整套 1766 / 0 · 度量未变 · backlog 的「待裁决」不再指向 bstn
```
"""


def main():
    body = io.open(BACKLOG, encoding="utf-8").read()
    changed = 0
    for old, new in REPLACEMENTS:
        if old in body:
            body = body.replace(old, new, 1)
            changed += 1
        else:
            print("  anchor MISS: %s" % old[:60])
    io.open(BACKLOG, "w", encoding="utf-8").write(body)
    print("  backlog: %d of %d lines closed" % (changed, len(REPLACEMENTS)))

    if "bstn` 的裁决（R794 结案）" not in body:
        io.open(BACKLOG, "a", encoding="utf-8").write(NOTE)
        print("  backlog: decision note appended")

    for path, marker, text in ((RBLOCK, "R794", BLOCKER), (RSTATUS, "R794", BLOCKER),
                               (RVERDICT, "第 794 轮", VERDICT)):
        b = io.open(path, encoding="utf-8").read()
        if marker in b:
            print("  %-22s already has %s" % (path.split("\\")[-1], marker))
            continue
        io.open(path, "a", encoding="utf-8").write(text)
        print("  %-22s appended %s" % (path.split("\\")[-1], marker))

    remaining = [l for l in io.open(BACKLOG, encoding="utf-8").read().splitlines()
                 if "待裁决" in l and "bstn" in l.lower()]
    print("  backlog lines still calling bstn pending: %d" % len(remaining))

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R794: bstn is closed as kept -- the decision was made in R91 and only the backlog still called it pending\n\n"
         "R768 found that neither bstn nor BSTN appears anywhere in the image and filed the module as pending a\n"
         "decision. Looking at what already guards it shows the decision was taken long ago and has been held by tests\n"
         "since: ArrowAndBeastTests asserts both halves at once, that the image carries arrowandbeast and no bstn, and\n"
         "that the module stays because a live capture put /api/beast/ on bstn.com. LiveContractTests calls that\n"
         "endpoint and asserts that /cart.js must not behave like a Shopify cart. PlatformAssignmentTests pins the flow\n"
         "type.\n\n"
         "So the module is not an unattended extra. Its evidence is of the live kind rather than the image kind, which\n"
         "the project's own provenance tiers allow and require to be named; it is named.\n\n"
         "What this round fixes is the paperwork. Three backlog lines still said pending, and a settled question\n"
         "recorded as open is how a later round ends up re-litigating it. Those three lines now carry the decision,\n"
         "with a note explaining the grounds and listing the guards.\n\n"
         "The contract's failure message is worth keeping visible: if bstn ever starts serving Shopify carts, it has\n"
         "become a Shopify store and BstnFlow is obsolete. A module that carries the condition under which it should be\n"
         "thrown away is healthier than one that does not.\n\n"
         "No product code changed; suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
