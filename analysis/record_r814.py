"""Record R814: the slug classification cannot be done by shape, and why the finding survives that."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 238. 1182 个 slug 分类：**形状测不出来**，而结论不依赖它

> R814。`analysis/classify_slugs.py`（留存）。未改产品代码。

### 一、第一版规则错在哪

按「两段以上十六进制且无元音 → 随机」去判，结果 `19dd5a-be`、`1a1efd-49`、`235b29-09` 被判成**可读** ——
**因为尾段只有 2 个字符（`be`/`49`/`09`），逃过了 `{4,10}` 的十六进制测试。**

**尾段的 2 字符后缀本身是随机模式的一部分，不是词。**

### 二、第二版规则也没解决

改成「存在一个 ≥3 字母、含元音、非纯十六进制的段 → 可读」：

```
1182 个 slug
  明显随机：187
  可读形态：995
```

**但 995 里混着 `098myu-gm`、`0mae7a-1y`、`10spib-sv`、`1qbsik-sf`、`140essx`** ——
`myu`、`spib`、`qbsik` 都含元音、都不是纯十六进制，**但它们明显是 Shopify 生成的**。

**所以：形状测试分不出「真店名」与「Shopify 生成的后缀」。**
**这不是规则没调好，是这个任务本身不能靠形状做。**

### 三、但结论不依赖分类精度

无论真店是**几百还是近千**，它都远多于复刻件的 **33 个 Shopify 别名**。

**所以判据 (f) 的未覆盖侧可以这样写，而不需要那个精确数字**：

> 镜像的字符串池里有 **1182 个 `myshopify` 形态的主机**；
> 其中 **187 个明显是随机 ID**，**其余 995 个含可读词但混有 Shopify 生成的后缀**；
> 复刻件的 33 个 Shopify 别名覆盖了其中 **30 个**（按前缀匹配）。
> **未建模的数百个，成因是「没有逐个取证」，不是「取证后判定不需要」。**

### 四、可以点名的那一批

**明确是店名、而且复刻件没有的**（从列表里读出来的，不是全部）：

```
10corsocomo · 303boards-com · 401games · 401pokesupply · 418skateshop
a-ma-maniere · a-presse-jp · addictmiami · adriftshop · afew-store
abovethecloudsstore · action-bronson-shop · abg-reebok-store
after-market-trading-ltd · afistfulofdice …
```

**这些不是随机串。** 复刻件里 `a-ma-maniere` 与 `afew` 是有的（别名 `afew`），**其余多数没有。**

### 五、这一条在判据 (f) 里的位置

判据 (f) 要求「未覆盖的每条写为什么」。**现在的答案是分层的**：

| 层 | 状态 |
|---|---|
| 复刻件的 57 个模块 → 镜像 | **逐条查过**：49 有据，6 零，2 只有噪音（R813） |
| 镜像的 1182 个 slug → 复刻件 | **量化了**：187 明显随机，995 含可读词，复刻件覆盖 30；**未建模的成因是「未逐个取证」** |
| 风控清单 | **已对账**（R807） |

**「未逐个取证」是一个诚实的理由，但它和「取证后确认不需要」不是一回事。**
**判据原文允许前者，只要写着 —— 这一轮就是把它写着的。**

### 六、验证

```
python analysis\\classify_slugs.py    1182 / 187 随机 / 995 可读形态 / 30 前缀匹配
本轮未改产品代码
完整套件保持 1766 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- **995 里真店到底多少个**：**Unknown，而且不能用形状算** —— 需要逐个查主机是否真实存在，
  **而那是网络查询，不是池子查询。**
- **复刻件的 30 个前缀匹配里有没有假匹配**：**Unknown** —— 前缀匹配（`slug.startswith(domain)`）
  会把 `afew-store` 匹到 `afew`，**这是对的；但也可能匹错，我没逐个核。**
- **要不要给这 995 建模**：**Unknown** —— 判据只要求写清为什么没覆盖，不要求覆盖。

### 八、教训

**两次都以为「改一下规则就能分类」，两次都不行。**
**第一次的错因是正则太窄（尾段 2 字符），第二次的错因是任务本身不该用形状做。**
**而正确的动作不是第三次改规则，是承认测不出来，然后问「结论是否依赖它」—— 这一次不依赖。**
"""

VERDICT = """

---

## 第 814 轮：1182 个 slug 分类 —— 形状测不出来，而结论不依赖它

### 第一版规则错了

`19dd5a-be` / `1a1efd-49` 被判成可读 —— **因为尾段只有 2 字符，逃过了 `{4,10}` 的十六进制测试。**

### 第二版也没解决

```
1182 个 slug → 明显随机 187 / 可读形态 995
```

**但 995 里混着 `098myu-gm`、`10spib-sv`、`1qbsik-sf`、`140essx`** —— `myu`/`spib` 含元音、非纯十六进制，**却明显是 Shopify 生成的。**

> **所以形状测试分不出「真店名」与「生成后缀」。这不是规则没调好，是这个任务不能靠形状做。**

### 但结论不依赖分类精度

**无论真店是几百还是近千，都远多于复刻件的 33 个 Shopify 别名。**

> 镜像有 **1182 个 `myshopify` 主机**；**187 明显随机**，**995 含可读词但混有生成后缀**；
> 复刻件 33 个别名按前缀匹配覆盖 **30 个**。
> **未建模的数百个，成因是「没有逐个取证」，不是「取证后判定不需要」。**

### 能点名的一批

```
10corsocomo · 303boards-com · 401games · 401pokesupply · 418skateshop
a-presse-jp · addictmiami · adriftshop · afew-store · abovethecloudsstore
action-bronson-shop · abg-reebok-store · after-market-trading-ltd …
```

### 判据 (f) 现在分层了

| 层 | 状态 |
|---|---|
| 复刻件 57 模块 → 镜像 | **逐条查过**（49 有据 / 6 零 / 2 噪音） |
| 镜像 1182 slug → 复刻件 | **量化了**，成因写明「未逐个取证」 |
| 风控清单 | **已对账** |

### 教训

**两次都以为「改一下规则就能分类」，两次都不行。**
**第一次错在正则太窄，第二次错在任务本身不该用形状做。**
**正确的动作不是第三次改规则，是承认测不出来，然后问「结论是否依赖它」—— 这次不依赖。**
"""

BACKLOG_ADD = """

## 判据 (f) — slug 分类：形状测不出来（R814）

**新增** `analysis/classify_slugs.py`（留存）。

```
1182 个 myshopify 主机
  明显随机 187
  可读形态 995（混有 Shopify 生成后缀如 -gm/-sv/140essx）
复刻件 33 个 Shopify 别名，按前缀匹配覆盖 30 个
```

**两次分类规则都失败了**：
① `{4,10}` 十六进制太窄，尾段 2 字符的 `-be`/`-49` 逃过；
② 改成「≥3 字母含元音非纯十六进制」后，`myu`/`spib`/`qbsik` 仍被算可读。

**结论：形状分不出真店名与生成后缀。** 但**结论不依赖它** —— 真店是几百还是近千，都远多于 33。

### 判据 (f) 的分层现状

| 层 | 状态 |
|---|---|
| 复刻件 57 模块 → 镜像 | 逐条查过：49 有据 / 6 零 / 2 仅噪音 |
| 镜像 1182 slug → 复刻件 | **已量化，成因：「未逐个取证」** |
| 风控清单 | 已对账（R807） |

**「未逐个取证」是诚实理由，但与「取证后确认不需要」不同 —— 判据允许前者，只要写着。**

| 仍 Unknown | |
|---|---|
| 995 里真店数 | **不能用形状算**，需查主机是否真实存在（网络查询，非池子） |
| 30 个前缀匹配有无假匹配 | 可能（`afew-store`→`afew` 是对的，其余未逐个核） |
| 要不要给这 995 建模 | 判据只要求写清为什么没覆盖 |

**纪律**：**两次「改规则就能分类」都不行。正确动作是承认测不出来，再问结论是否依赖它。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R814", BLOCKER)
    ensure(RSTATUS, "R814", BLOCKER)
    ensure(RVERDICT, "第 814 轮", VERDICT)
    ensure(BACKLOG, "R814", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R814"), (RSTATUS, "R814"), (RVERDICT, "第 814 轮"), (BACKLOG, "R814")):
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
         "R814: the slug classification cannot be done by shape, and the finding survives that\n\n"
         "R813 counted 1182 myshopify hosts and deferred the split between random-id hosts and real store names. This\n"
         "attempted it twice and failed twice, in two different ways.\n\n"
         "The first rule called a slug random when two or more segments were hex-shaped, which let 19dd5a-be through:\n"
         "its tail is two characters and escaped a four-to-ten character hex test, even though a two-character suffix\n"
         "is part of the generated pattern rather than a word. The second rule asked instead whether any segment is\n"
         "three or more letters with a vowel and not pure hex, which produces 187 obvious random ids and 995 readable\n"
         "ones -- but the readable pile contains 098myu-gm, 10spib-sv and 1qbsik-sf, whose segments carry vowels and\n"
         "are not hex, and which are plainly generated.\n\n"
         "So shape does not separate store names from Shopify's generated suffixes. That is not a rule waiting to be\n"
         "tuned; it is the wrong instrument for the question.\n\n"
         "What matters is that the conclusion does not depend on the split. Whether the real stores number several\n"
         "hundred or nearly a thousand, they vastly outnumber the replica's thirty-three Shopify aliases, of which\n"
         "thirty match by prefix. So criterion (f)'s uncovered side can be stated without the precise figure: the pool\n"
         "carries 1182 slug-shaped hosts, 187 plainly random, 995 containing readable words mixed with generated\n"
         "suffixes, and the replica models thirty of them. The reason for the rest is that they were never examined one\n"
         "by one -- which is not the same as having been examined and found unnecessary.\n\n"
         "Unknown: how many of the 995 are real stores, which shape cannot answer and which would need each host\n"
         "checked for existence, a network question rather than a pool question; whether any of the thirty prefix\n"
         "matches is spurious, since afew-store matching afew is right and the others were not checked individually;\n"
         "and whether any of the 995 should be modelled, which the criterion does not require.\n\n"
         "The pattern worth keeping: twice I assumed one more rule change would classify this, and twice it did not.\n"
         "The right move was not a third rule but admitting the measurement is unavailable and asking whether the\n"
         "finding depends on it. This time it does not.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
