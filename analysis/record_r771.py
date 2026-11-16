"""Record R771: offspring is a three-way mismatch, and I refused to make the number look better."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 198. `offspring` 是**三方错配**；而我没做那个能让数字变好看的改动

> R771。新增 `analysis/flow_wiring_audit.py`。**未改产品代码。**

### 一、先取原版证据：Poq 面比想象的薄

`platform.poq.io` 全池只有 7 条（Observation）：

```
https://platform.poq.io
/clients/office/AtaVerifyCaptcha
/clients/office/recaptcha?trackingId=
/clients/offspring/account/guest-token
/clients/offspring/cart/items
/clients/offspring/checkout/start
/clients/offspring/products?ids=
```

**offspring 只有 4 个 action，office 只有 2 个验证码。没有支付端点，没有下单完成端点。**

**所以 `offspring` 缺的两个步骤里，`checkout/start` 有对应物，支付那一半原版也没有。**
这与 `fanatics` / `yeezysupply` 同类但不同量：**那两个两步全无，这个是一有一无。**

### 二、三方错配

| 侧 | 是什么 |
|---|---|
| **注册表** | `new HybrisFlow("offspring", "Offspring", …)` |
| **已声明但未使用** | `OffspringFlow : MagentoFlow`，身份与注册行**逐字相同** |
| **原版证据** | **Poq**（`platform.poq.io/clients/offspring/…`） |

**三个都不是同一个东西。**

### 三、审计：有多少「声明了却没接线」的 flow

新脚本 `flow_wiring_audit.py`（60 个声明 / 32 个被构造）：

```
叶子 flow 类，无任何条目构造（2 个）：
  GoogleOAuthFlow   不是 StoreFlow，是助手，正常
  OffspringFlow     ← module 'offspring' 存在，却注册成了 HybrisFlow
```

`MagentoFlow` 也在"从未构造"里，但它是**基类**（Kith/Size/Sns/… 都继承它），**正常**。
**所以"从未构造"本身不是问题，"叶子 + 同名 module 存在 + 被别的类顶替"才是。**

### 四、**我没有把注册表改成 `OffspringFlow`**

改了会发生什么：

```
覆盖率  71% → 100%
依据    Poq（有据）→ Magento（无据，只是一个类的名字）
```

**数字变好，证据变差。这类改动我不做。**

`OffspringFlow` 的注释自己写着「Magento 1 style」——**那也是猜的**，与原版的 Poq 冲突。
**所以正确的一步不是换个类，而是按那 7 条证据建一个 Poq 家族** —— 而那是一个更大的活，且
**它建成后最多只能到 6/7**（支付端点原版没有），**这个"更低的分数"才是忠实的。**

### 五、过程中的一次自伤（第三次同类）

`flow_wiring_audit.py` 第一版的第二个检查写成

```python
own = typ[:1].upper() + typ[1:] + "Flow"     # typ 已以 Flow 结尾 → HybrisFlowFlow
if own in declared and typ != own:           # 永远不成立
```

**于是它无论数据如何都报「0 处错配」。** 我是**跑出来看输出才发现**这条是空的 ——
**那个 0 从来不是证据。** 已改为按「叶子 + 同名 module」判定。

**这是本会话第五次仪器失效，且第一次是我"先写结论再算"**（第一版还印了 `(%d)` 而数字在之后才算）。

### 六、验证

```
本轮未改产品代码
完整套件保持 1752 通过 / 0 失败
新增 analysis/flow_wiring_audit.py
```

### 七、仍然 Unknown

- Poq 家族的形状：**Unknown** —— 7 条证据够建 4 个步骤，不够建 7 个。
- `office` 是不是该成为独立 module：**Unknown** —— 它现在被 `offspring` 的域名列表顺带覆盖。
- `checkout/start` 之后由谁收尾（支付）：**Unknown** —— 池子里没有下一步的端点。
"""

VERDICT = """

---

## 第 771 轮：三方错配，而我拒绝了一个让数字变好看的改动

### 原版的 Poq 面比想象薄

```
/clients/offspring/products?ids=
/clients/offspring/cart/items
/clients/offspring/checkout/start
/clients/offspring/account/guest-token
/clients/office/AtaVerifyCaptcha
/clients/office/recaptcha?trackingId=
```

**没有支付端点，没有下单完成端点。** 所以 offspring 缺的两步里，`checkout/start` 有对应物，
**支付那一半原版也没有** —— 与 `fanatics`/`yeezysupply` 同类但不同量。

### 三方错配

| 侧 | 是什么 |
|---|---|
| 注册表 | `new HybrisFlow("offspring", …)` |
| 已声明未使用 | `OffspringFlow : MagentoFlow`，身份逐字相同 |
| 原版证据 | **Poq** |

### 审计结果

60 个声明 / 32 个被构造。**叶子且无构造的只有两个**：`GoogleOAuthFlow`（助手，正常）、
**`OffspringFlow`**（module 存在却被顶替）。`MagentoFlow` 也在"从未构造"里，但它是基类，正常。

### 我没改注册表

```
改 → 覆盖率 71% → 100%，依据 Poq → Magento（猜）
```

**数字变好、证据变差，这类改动我不做。**
`OffspringFlow` 自己注释也写着「Magento 1 style」，同样是猜。
**正确的一步是按那 7 条证据建 Poq 家族 —— 而它建成后最多 6/7，那个更低的分数才是忠实的。**

### 第三次同类自伤

审计脚本第二版的前身写成 `own = typ + "Flow"`（typ 已以 Flow 结尾）→ **永远不成立 → 无论数据如何都报"0 处错配"**。
**我是跑出来看输出才发现这条是空的。那个 0 从来不是证据。**

### 验证

```
产品代码未改；套件 1752 / 0；新增 analysis/flow_wiring_audit.py
```
"""

BACKLOG_ADD = """

## 核心 — offspring / Poq（R771）

**三方错配**：注册表 `HybrisFlow` / 已声明未用 `OffspringFlow : MagentoFlow` / 原版 **Poq**。

**原版 Poq 面（7 条字符串，Observation）**：

```
platform.poq.io/clients/offspring/{products?ids=, cart/items, checkout/start, account/guest-token}
platform.poq.io/clients/office/{AtaVerifyCaptcha, recaptcha?trackingId=}
```

**没有支付端点、没有下单完成端点。**

| 项 | 状态 |
|---|---|
| 建 Poq 家族（4 个步骤有据） | **新立** —— 建成后最多 6/7，**那个分数是忠实的** |
| `office` 是否独立 module | Unknown |
| `checkout/start` 之后的收尾 | Unknown —— 池子里没有下一步 |

**明确否决的改动**：把注册表换成 `OffspringFlow` —— 覆盖率 71%→100%，但依据从 Poq 退成 Magento 的猜测。
**数字变好、证据变差，不做。**

**另记**：`flow_wiring_audit.py` 可复算「声明了却没接线的叶子 flow」，当前只有 `OffspringFlow` 一个真问题。
"""


def main():
    for p, marker, text in ((P1, "R771", BLOCKER), (P3, "R771", BLOCKER), (P2, "第 771 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R771" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += offspring/Poq")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R771: offspring is a three-way mismatch, and I declined the change that would have improved the number\n\n"
         "The Poq surface is thinner than the mismatch suggested. platform.poq.io carries seven strings in total:\n"
         "four offspring actions (products by id, cart items, checkout start, guest token) and two office captcha\n"
         "calls. There is no payment endpoint and no order-completion endpoint, so of the two steps offspring is\n"
         "missing, one has a counterpart in the image and the other does not.\n\n"
         "The mismatch itself is three ways. Registry.cs constructs HybrisFlow(\"offspring\", ...); an OffspringFlow :\n"
         "MagentoFlow exists with a byte-identical identity and is never constructed; and the image's actual surface\n"
         "is Poq. None of the three agrees with the others.\n\n"
         "An audit over the whole registry finds sixty declared flow classes against thirty-two distinct types the\n"
         "entries construct. Three are never constructed, but MagentoFlow is a base class that Kith, Size, Sns and\n"
         "others extend, which is normal. Filtering to leaves leaves two: GoogleOAuthFlow, which is a disposable\n"
         "helper rather than a store flow, and OffspringFlow, whose module id exists and is registered as something\n"
         "else. So the audit is a reusable instrument and OffspringFlow is its only real hit.\n\n"
         "The change I did not make: pointing the registry at OffspringFlow would move the coverage row from 71% to\n"
         "100%, but the justification would move from Poq -- which the binary evidences -- to Magento, which is a\n"
         "class name and a guess. OffspringFlow's own comment says 'Magento 1 style', which is the same kind of guess\n"
         "the image contradicts. Improving the number while weakening the evidence is not a trade worth making, so\n"
         "the honest next step is to build a Poq family from the seven evidenced strings, knowing it can reach at\n"
         "most six of seven steps and that the lower score would be the faithful one.\n\n"
         "Recorded against myself: the first version of the audit's second check compared a type against itself with\n"
         "\"Flow\" appended, so it could never fire and reported zero mismatches regardless of the data. I found that\n"
         "by running it and reading the output, which is the only reason the zero did not become a conclusion. That\n"
         "version also printed the count before computing it.\n\n"
         "No product code changed; suite remains 1752 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
