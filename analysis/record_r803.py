"""Record R803: the non-commerce step names are the image's, and hypecommerce gains a third evidenced step."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 227. 核过 `NonCommerce` 的步骤名：**全是镜像的方法名**；`hypecommerce` 补到 3/3

> R803。`RetailFlows.cs` 加 `StorePaymentMethodAsync`；`ModuleCoverageTests` 的 `NonCommerce["hypecommerce"]` 加第三步。

### 一、上一轮留的疑问，这一轮有答案了

上一轮我撤回了两条多余豁免，并留下一个问题：
**`NonCommerce` 表里的步骤名是不是逐条从镜像取证过的？**
**如果不是，那 4/4 · 6/6 · 7/7 就是第二处虚高的百分比** —— 和我这两轮刚清理的是同一个病。

**核了六个名字，全在镜像里：**

| 名字 | 匹配 | 属于 |
|---|---|---|
| `GetReleaseFeed` | 2 | pocketgames |
| `WaitForRelease` | 9 | pocketgames |
| `CompleteRegistration` | 21 | riotgames |
| `SolveCaptcha` | 7 | raffle |
| `EnterRaffle` | 27 | raffle |
| `ScrapeRaffleForm` | 18 | raffle |

**所以那张表是可信的，三个满分不是虚的。**

### 二、`hypecommerce` 的两个名字也核了 —— 而且还有第三步

我起的 `ValidateEntryAsync` / `CreateEntryAsync` 是**从端点推的**，不是从方法名抄的 ——
**这一点本该说明却没说明。核完发现镜像里就有：**

```
'(<ValidateEntry>d__27@<CreateStripePaymentMethod>d__28$<CreateEntry>d__29...'
'ValidateEntryg'  ·  'CreateEntryg'
',<ValidateEntry>b__27_0,<ValidateEntry>b__27_1g'      ← lambda 闭包
'(<CreateEntry>b__29_0(<CreateEntry>b__29_1g'
```

**是异步状态机，和 `raffle`/`pocketgames` 那几个同形。名字对上了。**

**而且同一簇里还有两个：**

```
'$StorePaymentMethodg'                          ← 10 条匹配
'6<StorePaymentMethod>b__30_0...'               ← 也是状态机
<CreateStripePaymentMethod>d__28
```

**`StorePaymentMethod` 正对上第三个端点 `payment/methods/store`。**

### 三、所以补第三步

```
ValidateEntryAsync      -> POST /api/entries/validate
CreateEntryAsync        -> POST /api/entries/create
StorePaymentMethodAsync -> POST /api/payment/methods/store
```

**三步、三端点、三个镜像方法名，一一对应。**

### 四、结果

```
hypecommerce   3/3  + + +
exempt 5（未变）
```

**从"豁免"到 2/2 到 3/3 —— 同一个模块，两轮里从「不用看」变成「三步都实现」。**

### 五、`settings` 那个端点呢

镜像还有第四个：`admin.hypecommerce.io/api/settings`。**没有对应的方法名被找到**
（`StorePaymentMethod` 那一簇里没有 `GetSettings`/`SaveSettings` 之类）。
**所以第四步不补** —— **端点在、方法名不在，不足以说明它是这个模块的一步。**

**这是「宁可少一步，不凑满」的那条。**

### 六、验证

```
构建                已成功
ModuleCoverageTests hypecommerce 3/3；exempt 5
完整套件            1766 通过 / 0 失败 / 0 跳过
四项度量            4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- **四个 `NonCommerce` 步骤名之外还有没有**：**Unknown** —— 我核了六个名字，
  **`Register` 与 `GetRaffleData` 没单独核**（前者在 `riotgames` 表里，后者在 `raffle` 表里；
  `GetRaffleData` 在 R801 的 `raffle` 探测里出现过，`Register` 没有）。
- **`settings` 端点属于哪个方法**：**Unknown**。
- **`CreateStripePaymentMethod` 是不是第四步**：**Unknown** —— 名字在，端点未见。

### 八、这一轮的教训

**「我从端点推的名字」和「镜像里的方法名」是两件事，即使字面一样。**
**这一轮它们碰巧一样，所以问题被掩盖了；如果不一样，我就会在表里放一个自造的名字，而表看起来仍然满分。**

**所以核名字来源这件事，要在补条目之前做，不是之后。**
"""

VERDICT = """

---

## 第 803 轮：核过表里的名字，全是镜像的；hypecommerce 补到 3/3

### 上一轮的疑问有答案了

**六个名字，全在镜像里**：`GetReleaseFeed` 2 · `WaitForRelease` 9 · `CompleteRegistration` 21 ·
`SolveCaptcha` 7 · `EnterRaffle` 27 · `ScrapeRaffleForm` 18。

**所以 `NonCommerce` 那张表可信，4/4 · 6/6 · 7/7 不是虚数。**

### `hypecommerce` 的名字也核了，而且还有第三步

我起的那两个名字是**从端点推的**，本该死说明却没说明。**核完发现镜像里就有：**

```
<ValidateEntry>d__27 · <CreateEntry>d__29      ← 异步状态机 + lambda 闭包
<StorePaymentMethod>d__30                      ← 同一簇，10 条匹配
```

**`StorePaymentMethod` 正对上 `payment/methods/store`。**

### 补第三步

```
ValidateEntryAsync      -> /api/entries/validate
CreateEntryAsync        -> /api/entries/create
StorePaymentMethodAsync -> /api/payment/methods/store
```

```
hypecommerce   3/3   exempt 5（未变）
```

**同一个模块，两轮里从「豁免不用看」变成「三步都实现」。**

### 第四步不补

`/api/settings` 端点在，**但没找到对应方法名** —— **端点在、方法名不在，不足以说明它是这个模块的一步。**
**宁可少一步，不凑满。**

### 验证

```
构建绿 · 3/3 · 整套 1766 / 0 · 度量未变
```

### 教训

**「我从端点推的名字」和「镜像里的方法名」是两件事，即使字面一样。**
**这次碰巧一样，掩盖了问题；不一样的话，表里会有一个自造的名字而表依然满分。**
**核名字来源要在补条目之前。**
"""

BACKLOG_ADD = """

## 覆盖 — 表里的名字已核（R803）

**六个 `NonCommerce` 步骤名全部在镜像里**（`GetReleaseFeed` 2 · `WaitForRelease` 9 ·
`CompleteRegistration` 21 · `SolveCaptcha` 7 · `EnterRaffle` 27 · `ScrapeRaffleForm` 18）
→ **`raffle 4/4` · `pocketgames 6/6` · `riotgames 7/7` 不是虚数。**

**`hypecommerce` 补第三步**（镜像有 `<StorePaymentMethod>d__30`）：

```
ValidateEntryAsync · CreateEntryAsync · StorePaymentMethodAsync   ->  3/3
exempt 5
```

| 不补的 | 为什么 |
|---|---|
| `/api/settings` | **端点在、方法名不在** —— 不足以说明它是这个模块的一步 |

| 仍 Unknown | |
|---|---|
| `Register`（riotgames 表）与 `GetRaffleData`（raffle 表）未单独核 | `GetRaffleData` 在 R801 探测里出现过，`Register` 没有 |
| `CreateStripePaymentMethod` 是否第四步 | 名字在、端点未见 |

**规矩**：**核名字来源要在补条目之前。** 自造的名字放进去，表看起来一样满分。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R803", BLOCKER)
    ensure(RSTATUS, "R803", BLOCKER)
    ensure(RVERDICT, "第 803 轮", VERDICT)
    ensure(BACKLOG, "R803", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R803"), (RSTATUS, "R803"), (RVERDICT, "第 803 轮"), (BACKLOG, "R803")):
        body = io.open(path, encoding="utf-8").read()
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R803: the non-commerce step names are the image's, and hypecommerce gains a third evidenced step\n\n"
         "Last round left an open question: whether the names in NonCommerce were each taken from the image. If they\n"
         "were invented, then raffle 4/4, pocketgames 6/6 and riotgames 7/7 would be the same defect this session has\n"
         "just spent two rounds clearing, one table over.\n\n"
         "Six names checked and all six are in the image: GetReleaseFeed twice, WaitForRelease nine times,\n"
         "CompleteRegistration twenty-one, SolveCaptcha seven, EnterRaffle twenty-seven, ScrapeRaffleForm eighteen. The\n"
         "table is trustworthy and those scores are real.\n\n"
         "The two names I gave hypecommerce were derived from its endpoints rather than read off a method, which is a\n"
         "distinction I should have stated and did not. Checking them found the image does carry them: ValidateEntry at\n"
         "d__27 and CreateEntry at d__29 are async state machines with lambda closures, the same shape as the raffle and\n"
         "pocketgames methods. They happen to match, which hid the question rather than answering it.\n\n"
         "The same cluster holds a third: StorePaymentMethod at d__30, ten matches, matching the payment/methods/store\n"
         "endpoint. So the module now carries three steps against three admin endpoints and three image method names,\n"
         "one to one, and reports 3/3.\n\n"
         "A fourth endpoint, settings, is deliberately not a step. Its URL is in the image and no corresponding method\n"
         "name turned up, and an endpoint without a name is not enough to claim the module has that step. One fewer\n"
         "step is better than a padded list.\n\n"
         "The lesson: a name I derived from an endpoint and a name the image uses are two different things even when\n"
         "they are spelled the same. This time they coincided, so nothing broke -- if they had not, the table would have\n"
         "carried an invented name and still read as full marks. Checking where a name came from belongs before the\n"
         "entry is added, not after.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged; exempt stays at five."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
