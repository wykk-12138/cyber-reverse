"""Record R768: the label was mine and it lied; bstn is not in the image; offspring is Poq."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"
AG = r"D:\projects\cyber-reverse\AGENTS.md"

BLOCKER = """

---

## 195. `NO-URLS` 这个标签是我编错的；`bstn` 原版没有；`offspring` 是 Poq 不是 Hybris

> R768。新增 `analysis/store_url_dump.py`。未改产品代码。

### 一、先修标签，再看数据

R767 的探针给五个站打了 `NO-URLS`。**这个标签是错的，而且错在我**：

```python
verdict = "CHECKOUT" if co else ("OTHER-SHAPE" if ot else "NO-URLS")
```

**有 URL、但两个关键词都不匹配 → 落入 `NO-URLS`。** 而 `NO-URLS` 读起来是
**「镜像里这个站没有任何 URL」—— 一个比代码实际检查过的强得多的断言。**
`yeezysupply` 从 R757 起池子里就有 `https://www.yeezysupply.com`，**所以这个标签当场就是假的。**

**与 R764 的 `class not found` 同一个形状：诊断文案报错了因。**
**错的原因说明比没有说明更坏 —— 它把下一个读的人送到别处去。**

新脚本先 dump、后分类，并把旧标签混在一起的三件事分开：

```
NO-STRINGS   域名根本不出现
STRINGS      出现，但没有 URL 形状
URLS         出现且带 URL；分类是"报出来"，不是"判出来"
```

### 二、重跑之后

```
bstn         NO-STRINGS   「bstn」整池子都没有；大写 BSTN 也是 0
fanatics     URLS         全是 id.fanatics.com/api-internal/oauth2/* —— 账号面
offspring    URLS         poq.offspring.co.uk + www.offspring.co.uk
warhammer    URLS         api.prod.warhammer.com/graphql + login.mywarhammer.com/oauth/token
yeezysupply  URLS         一条裸域名
```

### 三、`bstn` 在原版里不存在

`str "bstn"` 与 `str "BSTN"` **都是 0 匹配**。

**这是"缺口"的镜像：复刻件多了一个原版没有的模块。**
**判据 f 要求"未覆盖的每条写为什么"，这条是反过来的 —— 覆盖了但没有对应物。**

**未动手**：删一个模块会牵动注册表、域名断言、覆盖率断言与若干守卫；
这是一个产品决定，不是一轮里的顺手改。**先记录，列为待裁决项。**

### 四、`offspring` 的真 API 是 Poq，不是 Hybris

```
https://platform.poq.io/clients/offspring/account/guest-token
https://platform.poq.io/clients/offspring/cart/items
https://platform.poq.io/clients/offspring/checkout/start     ← 结账
https://platform.poq.io/clients/offspring/products?ids=
https://platform.poq.io/clients/office/AtaVerifyCaptcha      ← 同模块的 Office 走 ATA 验证码
https://platform.poq.io/clients/office/recaptcha?trackingId=
```

**所以 `offspring` 的 71% 是真缺口，但根因比"缺两步"深一层**：
`Registry.cs` 把它注册成 **`new HybrisFlow("offspring", "Offspring", …)`**，**而原版走的是 Poq 平台**
（`platform.poq.io/clients/{client}/…`，`client` 是 `offspring` 与 `office` 两个）。

**补两步修不了它** —— 它的整个 API 家族选错了。

### 五、验证

```
本轮未改产品代码
完整套件保持 1751 通过 / 0 失败
新增 analysis/store_url_dump.py
```

### 六、仍然 Unknown

- 删不删 `bstn`：**待裁决**（删=更忠实，代价是牵动多处守卫）。
- Poq 家族要建成什么形状：**Unknown** —— 它是一个多 client 的平台，不是一个站。
- `fanatics` / `warhammer` / `yeezysupply` 的结账面：**Unknown** ——
  现有证据是账号面（oauth/login）与一条 GraphQL，**结账端点可能同样不存在**。
- 这五个站里**有几个的 71% 其实不该算缺口**（原版就没有）：**Unknown，需逐站判定**。
"""

VERDICT = """

---

## 第 768 轮：那个标签是我编错的

### 先修标签

R767 给五个站打了 `NO-URLS`。**错在我**：`verdict = CHECKOUT if co else (OTHER-SHAPE if ot else NO-URLS)`
—— **有 URL 但关键词不匹配就落进 `NO-URLS`**，而它读起来是「镜像里没有任何 URL」。

`yeezysupply` 从 R757 起就有 `https://www.yeezysupply.com`，**所以标签当场是假的。**

> **与 R764 的 `class not found` 同一个形状：诊断报错了因。错的原因比没有原因更坏。**

新脚本先 dump 后分类，把 `NO-STRINGS` / `STRINGS` / `URLS` 三件事分开。

### 重跑

```
bstn         NO-STRINGS   「bstn」「BSTN」都是 0
fanatics     URLS         全是 oauth2/login —— 账号面
offspring    URLS         poq.offspring.co.uk
warhammer    URLS         api.prod.warhammer.com/graphql + oauth/token
yeezysupply  URLS         一条裸域名
```

### `bstn` 原版没有

**这是"缺口"的镜像：复刻件多了一个原版没有的模块。**
删它会牵动注册表、域名断言、覆盖率断言与若干守卫 —— **产品决定，先记录不顺手改。**

### `offspring` 是 Poq，不是 Hybris

```
platform.poq.io/clients/offspring/cart/items
platform.poq.io/clients/offspring/checkout/start      ← 结账
platform.poq.io/clients/offspring/account/guest-token
platform.poq.io/clients/office/AtaVerifyCaptcha       ← 同模块 Office 走 ATA
```

**而 `Registry.cs` 把它注册成 `new HybrisFlow("offspring", …)`。**
**所以补两步修不了它 —— 整个 API 家族选错了。**

### 验证

```
产品代码未改；套件 1751 / 0；新增 analysis/store_url_dump.py
```

### 仍然 Unknown

- 删不删 `bstn`：**待裁决**
- Poq 家族该建成什么形状（多 client 平台，不是一个站）
- `fanatics`/`warhammer`/`yeezysupply` 的结账面是否**原版也没有**
"""

BACKLOG_ADD = """

## 核心 — 待裁决与新立（R768）

| 项 | 内容 | 性质 |
|---|---|---|
| **bstn 是否存在** | 原版 `bstn` / `BSTN` 都是 0 匹配 —— **复刻件多出来的模块** | **待裁决**（删=更忠实，牵动多处守卫） |
| **offspring 的 API 家族选错** | 注册为 `HybrisFlow`，原版走 Poq（`platform.poq.io/clients/offspring/{cart/items,checkout/start,account/guest-token}`） | **新立**，补两步修不了 |
| **Poq 家族** | 多 client 平台（`offspring` / `office`），含 `AtaVerifyCaptcha` | 新立，需先定形状 |
| fanatics / warhammer / yeezysupply | 只有账号面（oauth/login）或一条 GraphQL | **先判"原版有没有结账面"，再决定算不算缺口** |

**方法论提醒**：本站探针的 `NO-URLS` 标签曾把「关键词不匹配」说成「没有 URL」（R768 已修）。
**诊断文案报错因比没有诊断更坏** —— 见 `AGENTS.md` §2.7。
"""


def main():
    for p, marker, text in ((P1, "R768", BLOCKER), (P3, "R768", BLOCKER), (P2, "第 768 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R768" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += 待裁决与新立")

    # the rule file gains the seventh instance: a diagnostic label that named the wrong cause
    body = io.open(AG, encoding="utf-8").read()
    old = "| R764 | 用 `find('---')` 定文档区块边界 | 撞上表头分隔线 | 把规则文件自己改坏了 |"
    new = old + "\n| R768 | `NO-URLS` 表示\"关键词不匹配\" | 读起来是\"镜像里没有 URL\" | 结论被标签误导一轮 |"
    if "R768 | `NO-URLS`" in body:
        print("  AGENTS.md already lists R768")
    elif old in body:
        io.open(AG, "w", encoding="utf-8").write(body.replace(old, new, 1))
        print("  AGENTS.md += R768 row")
    else:
        print("  AGENTS.md: anchor MISS")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R768: the NO-URLS label was mine and it lied; bstn is not in the image; offspring is Poq\n\n"
         "R767's probe reported NO-URLS for five stores. The verdict expression was\n"
         "  CHECKOUT if checkout-hits else (OTHER-SHAPE if other-hits else NO-URLS)\n"
         "so a store whose URLs matched neither keyword fell through to a label that reads as 'the image names no URL\n"
         "for this store' -- far stronger than what the code checked. yeezysupply has carried\n"
         "https://www.yeezysupply.com since R757, so the label was false on its face.\n\n"
         "That is the same shape as R764's 'class not found': a diagnostic that names the wrong cause, which is worse\n"
         "than no diagnostic because it sends the next reader elsewhere. The new script dumps before classifying and\n"
         "separates three things the old label ran together -- no strings at all, strings but nothing URL-shaped, and\n"
         "URLs whose classification is reported rather than decided.\n\n"
         "Re-run, the picture is different from 'no URLs everywhere'. fanatics carries only an oauth2 login surface;\n"
         "warhammer carries a GraphQL API and an oauth token endpoint; yeezysupply a bare domain; offspring a Poq\n"
         "platform host. Only one store is genuinely absent.\n\n"
         "bstn is that store: search_strings finds nothing for 'bstn' or 'BSTN'. That is the mirror image of a gap --\n"
         "a module the replica has and the original does not. Deleting it would touch the registry, the domain\n"
         "assertions, the coverage assertions and several guards, so it is recorded as a decision for a later round\n"
         "rather than bundled in.\n\n"
         "offspring's 71% turns out to be a different kind of gap than 'two steps missing'. The image's offspring\n"
         "surface is platform.poq.io/clients/offspring with cart/items, checkout/start and account/guest-token, plus\n"
         "an office client carrying AtaVerifyCaptcha. Registry.cs registers it as a HybrisFlow, so the API family is\n"
         "wrong -- adding two steps to Hybris cannot fix it.\n\n"
         "No product code changed; suite remains 1751 pass / 0 fail. AGENTS.md section 2.7 gains this as its seventh\n"
         "instance."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
