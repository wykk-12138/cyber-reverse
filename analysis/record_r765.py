"""Record R765: the coverage matrix already existed, and what it says about placing an order."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 192. 判据 f 的下一层不用新写仪器：`ModuleCoverageTests` 早算过了；**12 个 module 下不了单**

> R765。未改产品代码。读现有测试的输出，不重造仪器。

### 一、先查有没有现成的，结果有

`ModuleCoverageTests`（R25 起）用**反射**算每模块的七步覆盖矩阵，而且它自己的注释就写明
为什么反射优于文本扫描：**「a text scan also cannot see through inheritance —— 继承来的 `FindProduct` 也该算实现」**。

**所以我这轮的"下一层"问题（有 module 无实际 step 实现？）早就有答案，只是没人把它读出来。**

### 二、62 个条目 × 七步，分桶

```
100%   47
 71%   12
 29%    2   pocketgames, riotgames
  0%    1   raffle
```

**这 15 个不是同一种事**：`pocketgames` / `raffle` / `riotgames` 是**非电商形态**（抽奖/发号），
测试自己就把它们单列在 `NonCommerce` 里按各自的步骤计分 —— **拿七步尺子量它们，量的是尺子。**

### 三、真正的问题在中间那 12 个

```
bstn  casio  fanatics  goat  hbx  hypecommerce
offspring  popmart  scheels  superswipe  warhammer  yeezysupply
```

**七个步骤里缺的始终是同一对**：

```
SubmitShippingAsync   -
SubmitPaymentAsync    -
```

**含义：能找商品、能选规格、能加购、能进结账页，但交不了运费与支付 —— 下不了单。**
**这正是 YG 说的"各网站自动下单"里"下单"那一步。**

### 四、一个交叉印证，以及它的边界

我另外按文件 grep 这 12 个 flow，看那两个方法在不在：

```
MagentoFlow / OffspringFlow   有
其余 11 个                    无
```

**而 `offspring` 在矩阵里也是 71%** —— 因为注册的是 **`new HybrisFlow("offspring", "Offspring", …)`**，
不是 `OffspringFlow`。**`HybrisFlow` 没有那两个步骤，`MagentoFlow` 有。**

**边界（必须写清）**：**"方法名不在文件里"不等于"没实现"**，可能是继承来的。
**所以矩阵是权威（反射看得穿继承），我的 grep 只是印证。** 两者在这 12 个上一致。

### 五、验证

```
ModuleCoverageTests   4 / 4 通过（既有测试，未改）
完整套件              本轮未跑全量（未改产品代码）
原始输出              analysis/coverage_raw.txt（本轮采集，供复算）
```

### 六、仍然 Unknown

- 这 12 个站**原版到底有没有** shipping/payment 步骤：**Unknown** —— 需要按站取证。
  **有可能其中几个在原版里也是不完整的**（例如只做抽奖登记的 `popmart`、只做抢购的 `yeezysupply`），
  **不能假定"原版都有"。**
- `raffle` 的 0% 是否正常：**Inference（高置信）** —— 它是纯抽奖，七步全不适用；`NonCommerce` 已单列，未取证。
- `SuperswipeFlow` 在矩阵里 71%，而它是「跑在 Shopify 店内的抽奖应用」——
  **七步尺子对它同样不合身**，可能与那三个 29% 同属一类。**Unknown，待判。**
"""

VERDICT = """

---

## 第 765 轮：这一层不用新仪器

### 先查有没有现成的 —— 有

`ModuleCoverageTests` 从 R25 起就用**反射**算每模块七步覆盖，注释里写着为什么反射优于文本扫描：
**继承来的实现也该算**。**所以"有没有 module 只是壳"这个问题早就有答案。**

### 62 × 七步

```
100%   47
 71%   12
 29%    2   pocketgames, riotgames
  0%    1   raffle
```

### 真正的问题在中间那 12 个

```
bstn casio fanatics goat hbx hypecommerce
offspring popmart scheels superswipe warhammer yeezysupply
```

**缺的始终是同一对：`SubmitShippingAsync` / `SubmitPaymentAsync`。**

> **能加购、能进结账页，交不了运费与支付 —— 下不了单。**

**这正是"各网站自动下单"里"下单"那一步。**

### 交叉印证与它的边界

grep 这 12 个 flow：`MagentoFlow`/`OffspringFlow` 有那两个方法，其余 11 个没有。
`offspring` 的 71% 是因为它注册的是 **`HybrisFlow("offspring", …)`**，不是 `OffspringFlow`。

**"方法名不在文件里" ≠ "没实现"**（可能继承）—— **矩阵是权威，grep 只是印证。**

### 验证

```
ModuleCoverageTests 4/4；原始输出存 analysis/coverage_raw.txt 供复算
```

### 下一轮

按站取证这 12 个在原版里是否真有 shipping/payment —— **不能假定"原版都有"**。
先做最可能有的一两个（`goat` / `scheels` 这类标准电商），`popmart`/`superswipe` 这种非电商形态另判。
"""

BACKLOG = """

## 核心 — 结账收尾（R765 发现）

| 模块 | 缺的步骤 | 状态 |
|---|---|---|
| bstn, casio, fanatics, goat, hbx, hypecommerce, offspring, popmart, scheels, superswipe, warhammer, yeezysupply | `SubmitShippingAsync` + `SubmitPaymentAsync` | **未结案** |

来源：`ModuleCoverageTests` 的反射矩阵（`analysis/coverage_raw.txt` 是采集的原始输出）。
**不要用 grep 判"有没有实现"** —— 继承会骗人；矩阵看得穿继承。

取证前提：**先确认该站在原版里是否真有这两个步骤**，再实现。
`popmart` / `superswipe` 是非电商形态（抽奖应用），七步尺子对它们不合身，要先判定它们该用什么尺子。
"""


def main():
    for p, marker, text in ((P1, "R765", BLOCKER), (P3, "R765", BLOCKER), (P2, "第 765 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R765 发现" in body:
        print("  BINDING_BACKLOG already has the item")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG)
        print("  BINDING_BACKLOG += 结账收尾")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R765: the coverage matrix already existed -- and it says twelve modules cannot place an order\n\n"
         "The question for this round was whether any of the sixty-two catalogue entries is a shell with no steps\n"
         "behind it. ModuleCoverageTests has answered that by reflection since R25, and its own comment explains\n"
         "why reflection beats a text scan: an inherited step counts as implemented, and grepping cannot see that.\n"
         "So this round read an existing instrument instead of building a new one, which is what the method rule\n"
         "asks for and what I had skipped in the two rounds before it.\n\n"
         "Across sixty-two modules and the seven commerce steps: forty-seven at 100%, twelve at 71%, two at 29%\n"
         "and one at 0%. The three lowest are raffle, pocketgames and riotgames, which are not commerce shapes at\n"
         "all and which the test already scores on their own step lists -- measuring them with the commerce\n"
         "yardstick measures the yardstick.\n\n"
         "The twelve in the middle are the finding. They all miss the same pair: SubmitShippingAsync and\n"
         "SubmitPaymentAsync. In plain terms they can find a product, pick a size, add to cart and reach the\n"
         "checkout page, but cannot submit shipping or payment, so they cannot place an order -- which is the half\n"
         "of per-site checkout the current priority is actually about.\n\n"
         "A grep cross-check agrees on eleven of them, and the twelfth explains itself: offspring registers a\n"
         "HybrisFlow, not an OffspringFlow, and HybrisFlow lacks the two steps while MagentoFlow has them. The\n"
         "matrix stays authoritative because it sees through inheritance; the grep is corroboration only, and the\n"
         "distinction is written down so the next round does not invert it.\n\n"
         "Recorded as Unknown and not assumed: whether the original has these steps for those twelve stores. Some\n"
         "may not, since popmart and superswipe are raffle apps rather than shops, and the seven-step yardstick\n"
         "may not fit them any better than it fit the 29% group.\n\n"
         "No product code changed. Raw matrix output kept in analysis/coverage_raw.txt so the numbers are\n"
         "recomputable."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
