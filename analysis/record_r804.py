"""Record R804: casio's ceiling is the image, not the effort."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 228. `casio` 的 71% 是**镜像的天花板**，不是没做完

> R804。未改产品代码。这一轮是把「能不能补」这个问题问到底。

### 一、先排除了一个可能：不是共用 flow 的问题

12 个模块缺 `SubmitShipping`/`SubmitPayment`。**如果它们共用一个未完成的基类，补一处就够。**

查了一遍：**`DemandwareFlow` 已经有全部三步**（10 个 override，覆盖 `GetHome` 到 `SubmitOrder`），
用的是 `convey` 与 `demandware` 两个模块，**都是 100%。**

**所以那 12 个都是各自的 flow，不是一个共享缺口。** 没有「补一处、修十二处」的便宜。

### 二、`casio` 这一侧的字符串，可以数清

三个探测，结果小得可以直接列完：

```
bhawar                                    2 条
  casiostore.bhawar.com
  https://casiostore.bhawar.com

casio.*(cart|order|checkout|payment|shipping|address)      0 条
(cart|order|checkout|payment|shipping|address).*casio      1 条
  _adyenOrderId*https://www.casio.com RecaptchaSiteKeyP6LfeU4...

```

**就这些。零个端点路径。**

**镜像给 `casio` 的是：一个主机、一个 Adyen 订单号字段名、一个 casio.com 站点名、一个 reCAPTCHA key。**
**没有 `/cart/add`，没有 `/checkout`，没有支付端点。**

### 三、所以 5/7 是天花板

复刻件现有的 5 步（home / product / variant / add-to-cart / checkout）**是照实机抓包写的**，
**而镜像只提供了主机名与字段名 —— 连一步的路径都没有。**

**这意味着**：

- **补 `SubmitShipping`/`SubmitPayment` 需要端点**
- **端点在镜像里不存在**（三个探测都是 0 或只有字段名）
- **所以这两步不能从镜像取证**

**这不是「没做完」，是「来源里没有」。**

### 四、为什么**不**豁免它

`YardstickDoesNotApply` 的定义是**「原版没有结账面，无需复刻」**。
**`casio` 有结账面** —— 它有购物车、有 Adyen、有 reCAPTCHA，**只是路径不在池子里。**

**把它放进豁免，就是用「来源不全」冒充「尺子不合身」** ——
**那正是 R801 我刚犯过的错，只是换了个方向。**

**所以它留在 5/7，并**在这里写清天花板**。**

### 五、这一条对完成判据 (f) 的意义

判据 (f) 要求「未覆盖的每条写为什么」。
**`casio` 的两条理由现在是最硬的一种**：**不是"还没查"，是"查了三个写法，都是 0"。**

### 六、仍然 Unknown

- **`casio` 的端点在镜像里是否以别的形式存在**：**Unknown** ——
  我搜了 `bhawar` 与四对「动作词 × casio」的组合，**但没有搜「动作词 × bhawar」**。
  **这是下一个该试的写法**（§2.7：先问有几种写法）。
- **`_adyenOrderId` 是字段名这件事**：**Observation**，R773 已定。
- **12 个模块里其余的端点可得性**：**没查** —— 每个都要单独探。

### 七、验证

```
本轮未改产品代码
完整套件保持 1766 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
casio 仍 71%（5/7），但它的缺口现在有据可查
```
"""

VERDICT = """

---

## 第 804 轮：casio 的 71% 是镜像的天花板

### 先排除一个可能

**`DemandwareFlow` 已有全部三步**（10 个 override），`convey`/`demandware` 两个模块都是 100%。
**所以那 12 个缺 shipping/payment 的都是各自的 flow —— 没有「补一处修十二处」的便宜。**

### casio 这一侧的字符串可以数清

```
bhawar                                   2 条（主机 + https 形式）
casio.*(cart|order|checkout|payment|…)   0 条
(动作词).*casio                          1 条（_adyenOrderId + casio.com + reCAPTCHA key）
```

**零个端点路径。**

**镜像给的是：一个主机、一个 Adyen 字段名、一个站点名、一个 reCAPTCHA key。**

### 所以 5/7 是天花板

**补那两步需要端点；端点在镜像里不存在。这不是「没做完」，是「来源里没有」。**

### 为什么**不**豁免它

`YardstickDoesNotApply` 的意思是「原版没有结账面」。
**`casio` 有结账面 —— 有购物车、有 Adyen、有 reCAPTCHA，只是路径不在池子里。**

> **把它放进豁免，就是用「来源不全」冒充「尺子不合身」—— 那正是 R801 我刚犯过的错，只是换个方向。**

### 对判据 (f) 的意义

**`casio` 的两条理由现在是最硬的一种：不是「还没查」，是「查了三个写法，都是 0」。**

### 仍然 Unknown

**「动作词 × bhawar」这个组合我没搜** —— 这是下一个该试的写法（§2.7：先问有几种写法）。
"""

BACKLOG_ADD = """

## 核心 — casio 的天花板（R804）

**5/7 是镜像能支撑的上限，不是没做完。**

```
bhawar                                   2 条（casiostore.bhawar.com + https 形式）
casio.*(cart|order|checkout|payment|…)   0 条
(动作词).*casio                          1 条（_adyenOrderId + casio.com + reCAPTCHA key）
```

**镜像只给了主机名、Adyen 字段名、站点名、reCAPTCHA key —— 零个端点路径。**

| 决定 | 理由 |
|---|---|
| **不补** `SubmitShipping`/`SubmitPayment` | 端点不存在，无法取证 |
| **不豁免** | `YardstickDoesNotApply` 是「原版无结账面」；**casio 有结账面**，只是路径不在池子里 |

**「来源不全」≠「尺子不合身」** —— 前者该记天花板，后者才是豁免（R801 的教训反向用）。

**同时排除的**：`DemandwareFlow` 已是满的（10 override），**12 个缺口各是各自的 flow，没有共享基类可补。**

| 下一个该试 | |
|---|---|
| `动作词 × bhawar` 组合 | **没搜过**（§2.7：先问有几种写法） |
| 其余 11 个模块的端点可得性 | 每个都要单独探 |
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R804", BLOCKER)
    ensure(RSTATUS, "R804", BLOCKER)
    ensure(RVERDICT, "第 804 轮", VERDICT)
    ensure(BACKLOG, "R804", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R804"), (RSTATUS, "R804"), (RVERDICT, "第 804 轮"), (BACKLOG, "R804")):
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
         "R804: casio's 71% is the image's ceiling, not unfinished work\n\n"
         "Twelve modules are missing SubmitShipping and SubmitPayment, so the first question was whether they share a\n"
         "base class that needs finishing. They do not: DemandwareFlow already carries all three steps across ten\n"
         "overrides and its two modules score 100%. Each of the twelve is its own flow, so there is no single fix.\n\n"
         "Casio's own surface is small enough to enumerate. Two strings mention bhawar, both the host. Nothing matches\n"
         "an action word paired with casio, and the other direction yields one concatenated blob carrying _adyenOrderId,\n"
         "the casio.com site name and a reCAPTCHA key. Zero endpoint paths. The image gives this store a host, a field\n"
         "name, a site name and a captcha key, and nothing to call.\n\n"
         "So five of seven is the ceiling. The five steps the replica has were written from a live capture, and the\n"
         "image never supplied even one path for them.\n\n"
         "It is deliberately not exempted. YardstickDoesNotApply means the original has no checkout to replicate; casio\n"
         "has one -- a cart, Adyen, a captcha -- it simply keeps its paths out of the pool. Exempting it would be using\n"
         "'the source is thin' to stand in for 'the yardstick does not fit', which is the same error R801 committed in\n"
         "the opposite direction. It stays at 71% with its ceiling written down.\n\n"
         "That also makes casio the strongest kind of entry for completion criterion (f): its two missing steps are\n"
         "explained not by 'not looked at yet' but by three probes that all came back empty.\n\n"
         "Unknown: the combination of an action word and bhawar, which has not been tried and is the next variation to\n"
         "test; and the endpoint availability of the other eleven modules, each of which needs its own probe.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
