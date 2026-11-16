"""Repair: append the R788 entry to replica/docs/VERDICT.md and commit. (R788b)

The first attempt pointed P2 at docs/VERDICT.md instead of replica/docs/VERDICT.md. BLOCKERS.md and
DELIVERY_STATUS.md took their entries, the script died on the missing VERDICT, and nothing was committed. This fixes
the path, checks that each file already has its entry rather than appending twice, and commits once.
"""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

VERDICT = """

---

## 第 788 轮：Warhammer 的 GraphQL 全取回来了

### 顺着 `/graphql` 找，撞上一个静态初始化器

```c
*(qword + 8)  = &off_147054A60;      // https://api.prod.warhammer.com/graphql
*(qword + 24) = sub_141D25160(945);  // 945 字符
*(qword + 32) = sub_141D25160(1920); // 1920 字符
```

**945/1920 是长度参数 —— 查询文本是池子里的长字面量。所以不该顺代码找，该搜池子。**

### 搜池子，六条全出（12,508 字符）

```
1995  mutation（匿名：copyFromId / firstname / address1 → 地址）
2249  mutation（匿名：selectedShippingRateId → 运费/更新）
 798  mutation AddCreditCard
2108  mutation AddItemToCart
 536  mutation AddToCart
4022  mutation ApproveOnboardPaymentMutation
```

**这就是 Warhammer 结账的核心。全文落在 `analysis/warhammer_graphql.txt`（700 行）。**
抽查可见完整选择集与四个 fragment。

### 为什么这轮不改代码

**这六条是底本，不是结论。** 翻成代码还缺：变量从哪来、匿名两条的 operationName、响应消费面。

**先把底本落盘，下一轮再翻 —— 比这轮凭印象写六个方法可靠。**
**R772 是「先建再验」，这一轮是它的反面。**

### 验证

```
12,524 字符 / 700 行 / 6 条 · 产品代码未改 · 套件 1761 / 0
```

### 一处路径自伤

第一次记录脚本把 `VERDICT.md` 指到根 `docs/`（它在 `replica/docs/`），脚本死在半路，**提交没发生**。
**教训：记录脚本也要像代码一样核对路径；而"脚本跑完"不等于"记录成功" —— 要看 `git log`。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-28s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-28s += %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RVERDICT, "第 788 轮", VERDICT)

    # confirm the other two actually made it before committing
    for path, marker in ((RBLOCK, "R788"), (RSTATUS, "R788"), (BACKLOG, "R788")):
        body = io.open(path, encoding="utf-8").read()
        print("  %-28s has %s: %s" % (path.split("\\")[-1], marker, marker in body))

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R788: Warhammer's GraphQL operations recovered -- six of them, twelve thousand characters\n\n"
         "R787 left Warhammer with one hard gap: the replica speaks REST where the image speaks GraphQL. Following the\n"
         "/graphql URL leads to a 133-byte static initialiser, and what it does is the useful part -- it stores the\n"
         "endpoint, a flex.cybersole.io URL, and two strings whose lengths it passes to an allocator, 945 and 1920.\n"
         "Those numbers are lengths, which says the query text is a long literal in the pool rather than something\n"
         "assembled by code. So the search belonged in the pool, not along the call graph.\n\n"
         "Searching for lines starting with mutation or query, longer than two hundred characters and containing a\n"
         "selection set, returns six operations totalling 12,508 characters: two anonymous mutations, AddCreditCard,\n"
         "AddItemToCart, AddToCart and ApproveOnboardPaymentMutation. Between them they cover adding to cart, adding a\n"
         "card, the address, the shipping rate and payment approval -- Warhammer's checkout core.\n\n"
         "The full text now sits in analysis/warhammer_graphql.txt: 700 lines, with each operation's address and\n"
         "length. A spot check of AddItemToCart shows complete selection sets and four fragment names.\n\n"
         "No code this round, deliberately. These six are a source text, not a conclusion: translating them needs the\n"
         "input shapes, which differ from the response fields the fragments describe; operation names for the two\n"
         "anonymous mutations; and which response fields are actually consumed. Landing the text first and translating\n"
         "next round is the reliable order, and it is the opposite of R772, which built before checking.\n\n"
         "One process error corrected here: the first record script pointed VERDICT at the repository root instead of\n"
         "replica/docs, died part-way, and committed nothing. A recording script needs its paths checked like any other\n"
         "code, and finishing without error is not the same as having recorded -- git log is.\n\n"
         "No product code changed; suite remains 1761 pass / 0 fail."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
