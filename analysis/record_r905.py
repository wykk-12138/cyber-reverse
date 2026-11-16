"""Record R905: /shield/ is Paynamics, correcting R903's anti-bot filing."""

import io
import os
import re
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### `/shield/` 是 **Paynamics Shield**，不是反爬 —— R903 分错了类（R905）

**R903 把 `/shield/v1/verify_otp` 标成「优先级 ② 的第一个具体端点」，靠的是路径里那个词。**

**这一轮查了 20 条含 `shield` 的字面量：**

```
ShieldApiUrl   https://nodecde1.paynamics.net/possible
Invalid Paynamics Shield URL
Paynamics Shield error (
https://shield.paynamics.net
shield processor
shield.paynamics.net
<RunShield>d__18 · RunShield · shieldUri · <shieldQuery>5__4
```

**Paynamics 是菲律宾的支付网关。所以 `/shield/` 是**支付环节的 OTP**，与反爬无关。**

### 而这一族的「反爬」标签是我按词猜的

**`AntiBotRelated` 里我还放了 `submitThreeDS2Fingerprint` —— 那是 3DS 指纹，也不是反爬。**

**所以那个子集里现在两条都分错了。R903 那轮的标注是**按名字归类**，而 AGENTS.md §1 的 R730 裁决明写过：
「不要用符号计数/名字替代读代码」。**

### 查到的两件事，都补进产品

| 事实 | 复刻件状态 |
|---|---|
| 镜像有**两个** shield 宿主：`nodecde1.paynamics.net` 与 `shield.paynamics.net` | **只有一个**（`ShieldHost`） |
| `/shield/v1/verify_otp` | **没有** |

**所以这是**同一家支付商的两个宿主**，而设备画像走其中一个、OTP 校验走另一个。**

### 而镜像里有个方法 `RunShield`，复刻件没有

**`recovered_async_methods.txt` 里 `RunShield` 在（1 条）。复刻件 `where_is RunShield` 只有 docs。**

**所以这是一个**原版有、复刻件没有的步骤** —— 比缺一个常量大的缺口，而它现在被记下来了而不是被常量掩盖。**

### 加了什么

| 文件 | 改动 |
|---|---|
| `Payments/Gateways.cs` | +`PublicShieldHost` · +`ShieldVerifyOtp` · +`RecoveredShieldSurface` 公开访问器 |
| `tests/PaynamicsShieldTests.cs` | **新建 3 用例** |

**第三个用例 `TheRecoveredSurfaceIsNotYetCalled` 断言宿主在源码里只出现一次 ——
**将来谁把它接上，这条会红，而红的时候说明「这条常量变成调用了」，需要连同测试意图一起改。****
"""

if "`/shield/` 是 **Paynamics Shield**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R905 appended")

VERDICT = """

---

## 第 905 轮：`/shield/` 是 Paynamics Shield，不是反爬 —— R903 分错了类

### 查证

**20 条含 `shield` 的字面量：**

```
ShieldApiUrl   https://nodecde1.paynamics.net/possible
Invalid Paynamics Shield URL
Paynamics Shield error (
https://shield.paynamics.net
shield processor
<RunShield>d__18 · RunShield · shieldUri · <shieldQuery>5__4
```

**Paynamics 是菲律宾支付网关 → `/shield/` 是**支付环节的 OTP**，与反爬无关。**

### 而 R903 那轮的标注是按名字猜的

**`AntiBotRelated` 里另一条 `submitThreeDS2Fingerprint` 也是 3DS 指纹，同样不是反爬。
**所以那个子集两条都分错了。**

> **而 AGENTS.md §1 的 R730 裁决早写过：「不要用符号计数/名字替代读代码」。**
> **我按路径里的词给它分类，正是那个裁决禁止的事。**

### 两件事补进产品

| 事实 | 复刻件之前 |
|---|---|
| 镜像有**两个** shield 宿主（`nodecde1` 与 `shield.paynamics.net`） | 只有一个 |
| `/shield/v1/verify_otp` | 没有 |

> **同一家支付商的两个宿主：设备画像走一个，OTP 走另一个。**

### 而镜像有方法 `RunShield`，复刻件没有

**`recovered_async_methods.txt` 里在案。复刻件 `where_is RunShield` 只有 docs。**

> **这是**原版有、复刻件没有的步骤** —— 比缺常量大的缺口，而它现在被记下来了，不是被常量掩盖。**

### 3 个用例

**`TheShieldSurfaceHasTwoHostsAndTheyDiffer` · `ThePathStartsWithTheShieldSegmentThatCausedTheMisfiling` ·
`TheRecoveredSurfaceIsNotYetCalled`（**断言宿主在源码里只出现一次** —— 将来接上会红，红时说明常量变成调用了）**

### 教训

> **R903 我给一格 `AntiBotRelated` 列表，两条都是按名字猜的，两条都错。**
> **而错的方式很舒服：路径里有 `shield` 这个词，`shield` 听起来像防护，所以它进了反爬那一格。**
> **「听起来像」不是证据。而这一轮找到的替代是 20 条字面量 —— 成本是三次工具调用。**
"""

BACKLOG_ADD = """

## 优先级 ② 更正 — `/shield/` 是 **Paynamics Shield**，不是反爬（R905，**改产品代码 +3 用例**）

### 查证

**20 条含 `shield` 的字面量 → `ShieldApiUrl https://nodecde1.paynamics.net/possible` ·
`Invalid Paynamics Shield URL` · `Paynamics Shield error (` · `https://shield.paynamics.net` · `shield processor` ·
**`<RunShield>d__18` · `RunShield`** · `shieldUri` · `<shieldQuery>5__4`**

**→ Paynamics 是菲律宾支付网关 → `/shield/` 是支付 OTP，与反爬无关。**

### R903 的 `AntiBotRelated` 两条都错了

**`/shield/v1/verify_otp`（支付 OTP）· `submitThreeDS2Fingerprint`（3DS 指纹）—— 都不是反爬。**
**→ 违反 AGENTS.md §1 的 R730 裁决：「不要用符号计数/名字替代读代码」。**

### 补进产品

| 事实 | 之前 |
|---|---|
| 两个 shield 宿主（`nodecde1` + `shield.paynamics.net`） | 只有一个 |
| `/shield/v1/verify_otp` | 没有 |

**`Gateways.cs` +2 常量 +`RecoveredShieldSurface`；`PaynamicsShieldTests.cs` 3 用例。套件 1802 → 1805。**

### 而 `RunShield` 是原版有、复刻件没有的**方法**

**`recovered_async_methods.txt` 在案；`where_is RunShield` 只有 docs。**

| 仍 Unknown | |
|---|---|
| `RunShield` 做什么 | 只有方法名与状态机名 |
| OTP 请求体/响应 | 无证据 |
| **反爬那一格还剩什么** | **两条都移出后为空** |

**纪律**：**「听起来像」不是证据。给东西分类前先查它的宿主与相邻字面量 —— 成本三次调用。**
"""

BLOCKER = """

---

## 329. `/shield/` 是 Paynamics Shield，不是反爬；同时发现 `RunShield` 是个缺的步骤

> R905。**改产品代码 +3 用例。** 套件 **1805 通过 / 0 失败 / 0 跳过**。

### 一、查证

**20 条含 `shield` 的字面量给出答案：**

```
ShieldApiUrl   https://nodecde1.paynamics.net/possible
Invalid Paynamics Shield URL
Paynamics Shield error (
https://shield.paynamics.net
shield processor
<RunShield>d__18 · RunShield · shieldUri · <shieldQuery>5__4
```

**Paynamics 是菲律宾支付网关 → `/shield/v1/verify_otp` 是**支付环节的 OTP**。**

### 二、R903 的 `AntiBotRelated` 两条都分错了

**`/shield/v1/verify_otp` 与 `submitThreeDS2Fingerprint` —— 一条支付 OTP，一条 3DS 指纹，都不是反爬。**

**而 AGENTS.md §1 的 R730 裁决写过：「不要用符号计数/名字替代读代码」。
我按路径里的词分类，正是那条禁止的事。**

### 三、补进产品

| 事实 | 之前 |
|---|---|
| 两个 shield 宿主（`nodecde1` + `shield.paynamics.net`） | 只有一个 |
| `/shield/v1/verify_otp` | 没有 |

**`Gateways.cs`：+`PublicShieldHost` · +`ShieldVerifyOtp` · +`RecoveredShieldSurface`。
`PaynamicsShieldTests.cs`：3 用例。**

### 四、以及一个更大的缺口

**镜像的方法表里有 `RunShield`，复刻件没有对应方法（`where_is RunShield` 只有 docs）。**

**所以这是**原版有、复刻件没有的步骤**，比缺常量严重，而它现在被记下来了。**

### 五、验证

```
搜 shield 字面量           -> 20 条，含 Paynamics 宿主与 RunShield
recovered_async_methods    -> RunShield 在案
where_is paynamics         -> Gateways.cs 17 处（已有网关，缺 OTP 面）
where_is RunShield         -> 只有 docs
test --filter PaynamicsShield -> 3 通过
metrics_report.py          -> 1805 通过 / 0 失败
```

### 六、仍然 Unknown

- **`RunShield` 做什么**：**Unknown** —— 只有方法名、状态机名 `d__18`、一个 `shieldUri` 与 `<shieldQuery>` 局部。
- **OTP 的请求体与响应**：**Unknown**。
- **反爬那一格现在还剩什么**：**两条都移出后为空** ——
  **所以「优先级 ② 在端点层有具体缺口」这个说法要撤回，至少在这 154 条路径的范围里。**

### 七、教训

**路径里有 `shield`，`shield` 听起来像防护，所以它进了反爬那一格。**

**「听起来像」不是证据。替代它的是 20 条字面量 —— 成本三次工具调用。**

**而这一轮同时暴露了 `RunShield`：一个原版有、复刻件没有的方法。
如果我上一轮就查了那 20 条，这个缺口会早一轮出现。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R905", BLOCKER)
    ensure(RSTATUS, "R905", BLOCKER)
    ensure(RVERDICT, "第 905 轮", VERDICT)
    ensure(BACKLOG, "R905", BACKLOG_ADD)

    note = (
        "\n## R905 补充 — /shield/ 是 Paynamics Shield，不是反爬（改产品代码 +3 用例，套件 1802→1805）\n\n"
        "20 条含 shield 的字面量给出答案：ShieldApiUrl https://nodecde1.paynamics.net/possible · "
        "Invalid Paynamics Shield URL · https://shield.paynamics.net · shield processor · RunShield · shieldUri。\n\n"
        "Paynamics 是菲律宾支付网关 → /shield/v1/verify_otp 是支付 OTP。R903 的 AntiBotRelated 两条都分错。\n\n"
        "补进产品：两个 shield 宿主（nodecde1 + shield.paynamics.net）· /shield/v1/verify_otp。\n\n"
        "以及一个更大的缺口：镜像方法表里有 RunShield，复刻件没有对应方法。\n\n"
        "反爬那一格现在为空 —— 「优先级 ② 在端点层有具体缺口」这个说法要撤回（至少在这 154 条范围内）。\n"
    )
    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R905" not in h:
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h + note)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R905"), (RSTATUS, "R905"), (RVERDICT, "第 905 轮"), (BACKLOG, "R905")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R905: /shield/ is Paynamics, which corrects R903's anti-bot filing, and RunShield is a step we lack\n\n"
         "R903 filed /shield/v1/verify_otp under the anti-bot priority because the path contains the word shield. This\n"
         " round read the twenty literals that carry the word and the classification does not survive: ShieldApiUrl\n"
         " points at nodecde1.paynamics.net, there are strings reading Invalid Paynamics Shield URL and Paynamics Shield\n"
         " error, and there is a host shield.paynamics.net. Paynamics is a payment processor, so the OTP path belongs to\n"
         " a checkout's payment step and not to protection.\n\n"
         "The anti-bot subset R903 created is therefore empty of correct entries: both members were filed by name, and\n"
         " the other one, the 3-D Secure fingerprint submission, is also payment. R730 in AGENTS.md settled this already\n"
         "-- do not let symbol counts or names stand in for reading the code -- and this is the same mistake in a\n"
         " smaller form.\n\n"
         "Two facts did come out of it and both are now in the gateway class: the image holds two Paynamics shield\n"
         " hosts, since device profiling talks to nodecde1 and the OTP path lives on shield.paynamics.net, and the OTP\n"
         " path itself was absent. Constants only; the body, the response and the caller are all unevidenced, so nothing\n"
         " calls it.\n\n"
         "The larger finding is that the image names a method RunShield in its async-method table and the replica has\n"
         " no such method. That is a step the original has and this does not, which matters more than a missing\n"
         " constant, and it is now recorded rather than being hidden behind one.\n\n"
         "Unknown: what RunShield does, of which only the name, the state machine ordinal, a shieldUri and a shieldQuery\n"
         " local are known; the OTP body and response; and what remains in the anti-bot column, which after moving both\n"
         " members out is empty -- so the claim that priority two has a concrete endpoint-level gap has to be withdrawn,\n"
         " at least within these hundred and fifty-four paths.\n\n"
         "The lesson is that sounds-like is not evidence. A word in a path is a hint about where to look, not a\n"
         " classification, and the substitute costs three tool calls.\n\n"
         "Product code changed, two constants and three tests; suite green at 1805."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
