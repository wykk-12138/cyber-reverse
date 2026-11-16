"""Record R877: the best-covered sequence has no flow class, which inverts the priority."""

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
### 覆盖最高的一条序列，**没有任何店类**（R877）

**`DrawStores` 的 12 步，与 `StoreFlow` 的 172 个虚方法按名字对：**

| 步骤 | 在 `StoreFlow` 里 |
|---|---|
| `GetHome` `CheckLogin` `Register` `CompleteRegistration` `GetCart` `ClearCart` `FindProduct` `AddToCart` | **有（8 个）** |
| `Start` | **没有裸名** —— 但有 `StartDrawFlow` / `StartPayment` / `StartPayPal`，与 `Init` |
| `CheckVerification` | **没有** —— 最近的是 `VerifySession` |
| `SubmitSaleRegistration` | **没有** |
| `ReplaceProduct` | **没有** |

**所以 8 / 12 精确对上。**

### 而这条顺序该倒过来读

| 序列 | 覆盖 |
|---|---|
| **`DrawStores`（无店类）** | **8 / 12** |
| PopMart（有类，写了 7 步） | 7 / 24 |
| Nike（有类，0 步） | 0 / 16 |

**覆盖最高的那条序列，是唯一一条**连流程类都没有**的。**

**原因不是它更完整，是它更普通：**`GetHome` / `GetCart` / `FindProduct` / `AddToCart` 是所有流程共用的步骤**，
而 `DrawStores` 只在这上面加了注册/登录。所以它「覆盖高」是因为它**大部分是通用步骤**。

**这条要小心读：8/12 不说明 `DrawStores` 已实现，只说明它的步骤名大多是通用的。**

### 两个近似，但我没算进去

| 镜像 | 最近 | 为什么不算 |
|---|---|---|
| `Start`（21） | `Init` | **首步同名是一件推断** —— 镜像里别的序列首步都叫 `Start`，而 `StoreFlow` 叫 `Init` |
| `CheckVerification` | `VerifySession` | **「验证会话」与「验证账号」不是一件事** |

**如果把这两个算成对上，就会得到 10/12 —— 而那个数字是编的。**

### 而它为什么没有店类

**`Registry.cs` / `RetailModules.cs` 里搜 `DrawStore` / `drawstore` / `draw-store`：无输出。**

**所以 `DrawStores` 不是一个站，是一个**流程概念** —— 与 R855 那五条变体同类。**

**而 R849 说「Pop Mart 的 14 个抽签端点全在」。现在看：**
**`DrawStores` 是「门店发售注册」，PopMart 是「抽签」—— 两个不同的东西被同一个端点族服务。**
"""

if "覆盖最高的一条序列，**没有任何店类**（R877）" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R877 appended")

BLOCKER = """

---

## 301. 覆盖最高的一条序列没有店类 —— 而这个数字要小心读

> R877。未改产品代码。

### 一、`DrawStores` 12 步对 `StoreFlow` 172 个虚方法

| 步骤 | 结果 |
|---|---|
| `GetHome` `CheckLogin` `Register` `CompleteRegistration` `GetCart` `ClearCart` `FindProduct` `AddToCart` | **有（8）** |
| `Start` | **无裸名**（有 `StartDrawFlow`/`StartPayment`/`StartPayPal`/`Init`） |
| `CheckVerification` | **无**（最近 `VerifySession`） |
| `SubmitSaleRegistration` | **无** |
| `ReplaceProduct` | **无** |

**8 / 12 精确对上。**

### 二、这条顺序该倒过来读

| 序列 | 覆盖 |
|---|---|
| **`DrawStores`（无店类）** | **8 / 12** |
| PopMart（有类，写了 7 步） | 7 / 24 |
| Nike（有类，0 步） | 0 / 16 |

**覆盖最高的序列，是唯一一条连流程类都没有的。**

**但原因不是它更完整，是它更普通 —— `GetHome` / `GetCart` / `FindProduct` / `AddToCart`
是所有流程共用的步骤，而它只在这上面加了注册/登录。**

> **所以 8/12 不说明 `DrawStores` 已实现，只说明它的步骤名大多是通用的。
> 一个「覆盖率高」的数字，可以只是「这个序列没什么特别的」的同义词。**

### 三、两个近似我没算进去

| 镜像 | 最近 | 为什么不算 |
|---|---|---|
| `Start`(21) | `Init` | **首步同名是推断**（别的序列首步叫 `Start`，`StoreFlow` 叫 `Init`） |
| `CheckVerification` | `VerifySession` | **「验证会话」≠「验证账号」** |

**算进去就是 10/12 —— 而那个数字是编的。**

**这与 R871 那个 `GetOrders` 的处理相反：那次我核完确认归属，于是用了；
这次我核完确认是近似，于是没用。同一个动作，两种结论。**

### 四、它为什么没有店类

**`Registry.cs` / `RetailModules.cs` 搜 `DrawStore` / `drawstore` / `draw-store`：无输出。**

**所以 `DrawStores` 不是站，是**流程概念** —— 与 R855 那五条变体同类。**

**而结合 R849（Pop Mart 14 个抽签端点全在）：**
**`DrawStores` 是「门店发售注册」，PopMart 是「抽签」—— 两个不同的东西被同一个端点族服务。**

**这解释了为什么 `/_shop/v1/storeOfflineDraw/*` 与 `/shop/v1/drawScratch/*` 并存：
它们是两件事。**

### 五、验证

```
where_is CheckVerification     -> implementation 无（只有 docs）
where_is SubmitSaleRegistration -> implementation 无
where_is CheckLogin            -> implementation 3（StepAction.cs · StoreFlow.cs · MagentoFlow.cs）
where_is CompleteRegistration  -> implementation 3（StepAction.cs · RetailFlows.cs · StoreFlow.cs）
where_is ReplaceProduct        -> implementation 无
StoreFlow 虚步骤计数           -> 172
DrawStores 12 步匹配           -> 8 有 / 4 无
Registry 搜 DrawStore          -> 无输出
```

### 六、仍然 Unknown

- **`DrawStores` 该不该建一个流程类**：**Unknown，而这是本轮之后最该判的一条。**
  **建了它，8 步立刻能跑；但它是流程概念不是站，所以 `Id` / `Domains` 无从写。**
- **`Start` 与 `Init` 是不是同一件事**：**Unknown（推断，未证）** ——
  **这是 8/12 与 9/12 之间那一步。**
- **`ReplaceProduct` 与 `AddToCart` 的关系**：**Unknown** —— 名字像「替换商品」，
  **但 `EditLine` 已经在 `StoreFlow` 里，`ReplaceProduct` 可能是它的另一种叫法。**

### 七、教训

**一个覆盖率数字看着像进展，其实可能是「这条序列没什么特别的」。**

**8/12 比 7/24 高得多，而 7/24 那条里有七步是我真写了、有端点证据的；
8/12 这条一步都没写，只是名字大多通用。**

**所以「覆盖率」和「完成度」不是一回事，而我把它们放在同一张表里时差点读混。**

**下次比较序列覆盖时，该同时报两个数：名字对上的，和真正实现的。**
"""

VERDICT = """

---

## 第 877 轮：覆盖最高的一条序列没有店类 —— 而这个数字要小心读

### `DrawStores` 12 步 vs `StoreFlow` 172 个虚方法：**8 / 12**

| 有了 | `GetHome` `CheckLogin` `Register` `CompleteRegistration` `GetCart` `ClearCart` `FindProduct` `AddToCart` |
|---|---|
| **没有** | `Start`（无裸名，有 `Init`）· `CheckVerification`（最近 `VerifySession`）· `SubmitSaleRegistration` · `ReplaceProduct` |

### 这条顺序该倒过来读

| 序列 | 覆盖 |
|---|---|
| **`DrawStores`（无店类）** | **8 / 12** |
| PopMart（有类，真写了 7 步） | 7 / 24 |
| Nike（有类，0 步） | 0 / 16 |

**但原因不是它更完整，是它更普通 —— 大部分是通用步骤。**

> **一个「覆盖率高」的数字，可以是「这条序列没什么特别的」的同义词。**
> **8/12 那条一步都没写；7/24 那条里有七步是我真写了、有端点证据的。**
> **所以「覆盖率」和「完成度」不是一回事 —— 下次比较该同时报两个数。**

### 两个近似我没算进去

| 镜像 | 最近 | 为什么不算 |
|---|---|---|
| `Start`(21) | `Init` | 首步同名是推断 |
| `CheckVerification` | `VerifySession` | 「验证会话」≠「验证账号」 |

**算进去就是 10/12 —— 而那是编的。**

> **这与 R871 的 `GetOrders` 相反：那次核完确认归属，于是用了；这次核完确认是近似，于是没用。同一个动作，两种结论。**

### 它为什么没有店类

**Registry / RetailModules 搜 `DrawStore`：无输出 → 不是站，是**流程概念**（与 R855 五条变体同类）。**

**结合 R849：`DrawStores` 是「门店发售注册」，PopMart 是「抽签」—— 两个不同的东西被同一端点族服务。
这解释了 `/storeOfflineDraw/*` 与 `/drawScratch/*` 为什么并存。**

### 仍然 Unknown

**`DrawStores` 该不该建流程类**（**本轮之后最该判的一条：建了 8 步能跑，但它是流程概念不是站，`Id`/`Domains` 无从写**）·
**`Start` 与 `Init` 是否同一件事**（**这是 8/12 与 9/12 之间那一步**）·
**`ReplaceProduct` 与 `EditLine` 是否同一件事**

### 教训

> **一个覆盖率数字看着像进展，其实可能是「这条序列没什么特别的」。**
> **而我把「覆盖率」和「完成度」放在同一张表里时，差点读混。**
"""

BACKLOG_ADD = """

## 判据 — 覆盖最高的一条序列没有店类（R877）

### `DrawStores` 12 步 vs `StoreFlow` 172 虚方法：**8 / 12**

**有**：`GetHome` `CheckLogin` `Register` `CompleteRegistration` `GetCart` `ClearCart` `FindProduct` `AddToCart`
**没有**：`Start`（有 `Init`）· `CheckVerification`（最近 `VerifySession`）· `SubmitSaleRegistration` · `ReplaceProduct`

### 顺序要倒过来读

| 序列 | 覆盖 | 真写了 |
|---|---|---|
| **`DrawStores`（无店类）** | **8/12** | **0** |
| PopMart | 7/24 | **7** |
| Nike | 0/16 | 0 |

> **覆盖率 ≠ 完成度。8/12 那条一步没写，只是名字大多通用；7/24 那七步真有端点证据。**

### 两个近似没算（算进去就是编的 10/12）

**`Start`≈`Init`（推断）· `CheckVerification`≈`VerifySession`（不同概念）**
**→ 与 R871 的 `GetOrders` 相反：那次核完确认归属就用，这次核完确认是近似就不用。**

### `DrawStores` 无店类

**Registry 搜 `DrawStore` 无输出 → 流程概念，不是站（同 R855 五条变体）。**
**→ `DrawStores`=门店发售注册，PopMart=抽签，**两个不同的东西共用同一端点族**。**

| 仍 Unknown | |
|---|---|
| **`DrawStores` 是否建流程类** | **最该判：8 步能跑，但 `Id`/`Domains` 无从写** |
| `Start` vs `Init` | 8/12 → 9/12 的那一步 |
| `ReplaceProduct` vs `EditLine` | 可能同一件事 |

**纪律**：**报序列覆盖时同时报两个数 —— 名字对上的、真正实现的。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R877", BLOCKER)
    ensure(RSTATUS, "R877", BLOCKER)
    ensure(RVERDICT, "第 877 轮", VERDICT)
    ensure(BACKLOG, "R877", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R877" not in h:
        h += ("\n## R877 补充 — 覆盖最高的一条序列没有店类\n\n"
              "**`DrawStores` 12 步 vs `StoreFlow` 172 虚方法 = 8/12**：有的 8 个是 `GetHome` `CheckLogin` `Register` `CompleteRegistration` `GetCart` `ClearCart` `FindProduct` `AddToCart`；"
              "缺 `Start`（有 `Init`）· `CheckVerification`（最近 `VerifySession`）· `SubmitSaleRegistration` · `ReplaceProduct`。\n"
              "**⚠ 覆盖率 ≠ 完成度**：`DrawStores` 8/12 但**一步没写**（名字大多通用）；PopMart 7/24 但**七步真有端点证据**。**报覆盖时同时报两个数。**\n"
              "**两个近似没算**：`Start`≈`Init`（推断）· `CheckVerification`≈`VerifySession`（不同概念）—— 算进去就是编的 10/12。\n"
              "**`DrawStores` 在 Registry 里无模块 → 流程概念不是站**（同 R855）。**`DrawStores`=门店发售注册 vs PopMart=抽签，共用同一端点族。**\n"
              "**最该判的一条：`DrawStores` 要不要建流程类 —— 建了 8 步能跑，但 `Id`/`Domains` 无从写。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R877"), (RSTATUS, "R877"), (RVERDICT, "第 877 轮"), (BACKLOG, "R877")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R877: the best-covered sequence has no flow class, and the number wants careful reading\n\n"
         "DrawStores' twelve steps against StoreFlow's 172 virtuals match eight by exact name: GetHome, CheckLogin,"
         " Register, CompleteRegistration, GetCart, ClearCart, FindProduct and AddToCart. Four do not: Start has no bare"
         " name though Init exists, CheckVerification's nearest is VerifySession, and SubmitSaleRegistration and"
         " ReplaceProduct have nothing.\n\n"
         "Read as a ranking this inverts the picture: the sequence with the best coverage is the only one with no flow"
         " class at all, ahead of Pop Mart at seven of twenty-four and Nike at zero of sixteen. But the reason is not\n"
         " that it is more complete. It is more ordinary. GetHome, GetCart, FindProduct and AddToCart are the steps every"
         " flow shares, and DrawStores adds registration and login on top of them. So eight of twelve means the sequence"
         " is unremarkable, not that it is implemented -- nothing in it was ever written.\n\n"
         "That distinction nearly slipped past me because both numbers sat in one table. Coverage and completion are not\n"
         " the same measure and a sequence report should carry both: names that match, and steps that were actually\n"
         " written with endpoint evidence behind them.\n\n"
         "Two near misses were deliberately excluded. Start at ordinal 21 against Init, and CheckVerification against\n"
         " VerifySession. Counting either would give ten of twelve, and both are inference: every other sequence's first"
         " step is called Start while this replica calls it Init, and verifying a session is not verifying an account.\n"
         " This is the mirror of R871, where checking GetOrders confirmed the attribution and so it was used; here\n"
         " checking confirms an approximation and so it is not. Same action, opposite conclusions.\n\n"
         "Searching Registry and RetailModules for DrawStore returns nothing, so DrawStores is a flow concept rather\n"
         " than a store, of the same species as the five variants R855 identified. Combined with R849's finding that"
         " every Pop Mart draw endpoint exists, the picture resolves: DrawStores is in-store sale registration while\n"
         " Pop Mart is drawing, two different things served by one endpoint family, which is why storeOfflineDraw and\n"
         " drawScratch both exist.\n\n"
         "Unknown: whether DrawStores should become a flow class at all, which is now the judgement to make, since eight\n"
         " steps would run immediately but the class needs an Id and Domains and it is a concept rather than a store;"
         " whether Start and Init are the same step, the difference between eight of twelve and nine; and whether\n"
         " ReplaceProduct is another name for EditLine, which already exists.\n\n"
         "The lesson is that a coverage figure can look like progress while meaning that the sequence is unremarkable.\n"
         " Seven of twenty-four contained seven steps written against real endpoints; eight of twelve contained none.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
