"""Record R860: the model layer is complete, and Task.Type is redundant rather than missing."""

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
### 模型层从镜像取全；四个模型复刻件**全部齐备**（R860）

**镜像的模型 schema（按 `类型,Cybersole.Core.属性!访问器` 语法抽取）：**

| 模型 | 属性数 | 属性 |
|---|---|---|
| `BotTask` | 14 | MonitorDelay · MonitorMode · Product · Products · Profile · Properties · ProxyGroup · RetryDelay · Running · StartTime · Status · Store · Task · Timeout |
| `BaseCheckout` | 8 | Image · Price · Product · Properties · Size · Store · Timestamp · **Type** |
| `TaskGroup` | 17 | CaptchaSource · CheckoutLimit · CloudflareSolverId · LinkedDelays · MonitorDelay · Name · NextReset · Pinned · ProfileLimit · RetryDelay · Running · Tasks · Timeout · TotalCheckouts · TotalDeclines · UsageExpiry · Webhooks |
| `WebTask` | 2 | Account · Steps |

**复刻件对照：14/14 · 8/8 · 17/17 · 2/2 —— 全部齐备。**

### 所以 R858 那个「留还是删」有答案了

**镜像的 `Type` 在 `BaseCheckout`（结账记录）上，而**不在** `BotTask` 上（14 个属性里没有 Type）。**

**而复刻件的 `BaseCheckout` 也有 `Type`（8/8）。**

**所以 `Tasks.cs` 里那个没人写的 `Type` 是**冗余声明** —— 正确的那份在 `BaseCheckout` 上，已经有了。**

### 两条对优先级 ② 有用的 Observation

- **`TaskGroup.CaptchaSource`** —— 验证码来源是**任务组**级配置
- **`TaskGroup.CloudflareSolverId`** —— Cloudflare solver 也是任务组级
- **`TaskGroup.ProfileLimit` · `CheckoutLimit` · `TotalCheckouts` · `TotalDeclines`** —— 配额与计数也在组级

**即：风控配置的挂载点是 `TaskGroup`，不是单任务。**
"""

if "模型层从镜像取全；四个模型复刻件**全部齐备**（R860" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: model schema appended")

BLOCKER = """

---

## 284. 模型层**全部齐备**；`Task.Type` 是**冗余**，不是缺

> R860。未改产品代码。**R858 的「留还是删」有答案了。**

### 一、镜像的模型 schema

按 R859 找到的语法抽表：

| 模型 | 属性数 | 备注 |
|---|---|---|
| `BotTask` | 14 | **无 `Type`**；有 `Task`（嵌套）、`StartTime`、`Status` |
| `BaseCheckout` | 8 | **有 `Type`** |
| `TaskGroup` | 17 | **`CaptchaSource` · `CloudflareSolverId` · `ProfileLimit` · `CheckoutLimit` · `TotalCheckouts` · `TotalDeclines`** |
| `WebTask` | 2 | `Account` · `Steps` |

**复刻件对照：14/14 · 8/8 · 17/17 · 2/2。**

### 二、所以 R858 的答案

**镜像的 `Type` 在 `BaseCheckout` 上，不在 `BotTask` 上。**
**而复刻件的 `BaseCheckout` 也有 `Type`（8/8 之一）。**

**所以 `Tasks.cs` 那个没人写的 `Type` 是**冗余声明** —— 正确的那份已经在 `BaseCheckout` 上。**

**这与 R858 的两种猜测都不同：不是「镜像有，该留着并被写」，也不是「镜像没有，该删」，
而是「镜像有，但它在另一个类型上，而这个类型已经有了」。**

**可以删。但本轮仍不删，理由见第四节。**

### 三、两条对优先级 ② 有用的 Observation

**`TaskGroup` 里同时有：**

```
CaptchaSource · CloudflareSolverId · ProfileLimit · CheckoutLimit
TotalCheckouts · TotalDeclines · UsageExpiry · Webhooks
```

**即：验证码来源、Cloudflare solver、配额、成败计数、用量到期、webhook，**全部挂在任务组上，不是单任务上**。**

**这对风控实现意味着：一个组的任务共用同一套 solver 配置与配额 —— 而不是每个任务各自配。
复刻件的 `KasadaSolvers` / `CloudflareClearance` 是怎么挂的，没查，但这一条给了正确的挂载点。**

### 四、为什么本轮仍然不删 `Task.Type`

**因为「可以删」和「现在就删」之间还差一件事：删掉之后有没有东西在读它。**

**我这轮查的是「有没有写它」（0 处），**没查「有没有读它」**。
一个只读不写的字段更糟（永远是空），但它可能被序列化进 `tasks.json` ——
**而那会改变输出文件的结构，属于会影响既有用例的改动。**

**所以下一步是查读点，不是直接删。**

### 五、这个对照的边界（必须写明）

**「14/14、8/8、17/17」是用正则 `\\b<属性名>\\b` 在**整个模型文件**里搜的，**
**不是解析属性声明。所以它证明「这些名字出现过」，不证明「它们都是那个类型的 public 属性」。**

**这比 R816 那种「池子里找不到就判没有」好在方向是对的（正向可用），
但它是**上界宽松**的检查 —— 会把注释里提到、别的类型里有、局部变量同名的都算进去。**

**要收紧，得解析属性声明本身。本轮没做。**

### 六、验证

```
ida.py str Cybersole.Models. / Models.Task / Models.Base / Models.Bot
  13 个声明类型；BotTask 14 · BaseCheckout 8 · TaskGroup 17 · WebTask 2（另有 Account/AccountGroup/Analytics/Checkout/Product/Release/Store/TaskStep/Variant）
replica 对照（正则名搜）: 14/14 · 8/8 · 17/17 · 2/2
本轮未改产品代码
七项度量沿用
```

### 七、仍然 Unknown

- **`BotTask.Task` 是什么类型**：**Unknown** ——
  14 个属性里有个叫 `Task` 的，**如果它是嵌套任务对象，那「种类」可能在里面。**
- **`Task.Type` 有没有读点**：**Unknown** —— **决定能否安全删。**
- **`TaskGroup` 那套 solver 配置复刻件挂在哪**：**Unknown** ——
  **`KasadaSolvers.cs` / `CloudflareClearance.cs` 存在，但挂载点没查。**
- **那个对照是不是上界宽松**：**是（Inference 高）** —— 见第五节。

### 八、教训

**R858 我列了两种可能（镜像有 / 镜像没有），实际是第三种：镜像有，但在另一个类型上。**

**「这个字段存不存在」这个问题，少了一个维度 —— **在哪个类型上**。**
**而补上这个维度的成本极低：R859 已经给出了按类型抽表的语法，这一轮只是把它用到四个类型上。**
"""

VERDICT = """

---

## 第 860 轮：模型层全部齐备；`Task.Type` 是冗余不是缺

### 镜像的模型 schema

| 模型 | 属性数 | 备注 |
|---|---|---|
| `BotTask` | 14 | **无 `Type`**；有 `Task`（嵌套）、`StartTime`、`Status` |
| `BaseCheckout` | 8 | **有 `Type`** |
| `TaskGroup` | 17 | **`CaptchaSource` · `CloudflareSolverId` · `ProfileLimit` · `CheckoutLimit` · `TotalCheckouts` · `TotalDeclines` · `Webhooks`** |
| `WebTask` | 2 | `Account` · `Steps` |

**复刻件：14/14 · 8/8 · 17/17 · 2/2 —— 全部齐备。**

### R858 的答案：第三种

**镜像的 `Type` 在 `BaseCheckout` 上，不在 `BotTask` 上；而复刻件的 `BaseCheckout` 也有 `Type`。**

> **所以 `Tasks.cs` 那个没人写的 `Type` 是**冗余声明** —— 正确的那份已经在 `BaseCheckout` 上。**
> **不是「镜像有该留着写」，也不是「镜像没有该删」。**

### 对优先级 ② 的 Observation

**`TaskGroup` 里同时有 `CaptchaSource` · `CloudflareSolverId` · `ProfileLimit` · `CheckoutLimit` · `TotalCheckouts` · `TotalDeclines`。**

> **验证码来源、Cloudflare solver、配额、成败计数，**全部挂在任务组上，不是单任务上**。**
> **一个组的任务共用同一套 solver 配置与配额。**

### 为什么本轮仍不删

**「可以删」和「现在就删」还差一件事：删掉之后有没有东西在读它。**
**我查的是「有没有写」（0 处），没查「有没有读」。一个只读不写的字段可能被序列化进 `tasks.json` —— 那会改变输出文件结构，影响既有用例。**

**→ 下一步是查读点，不是直接删。**

### 这个对照的边界

**「14/14 · 8/8 · 17/17」是用正则 `\b<属性名>\b` 在**整个模型文件**里搜的，不是解析属性声明。**
**它证明「名字出现过」，不证明「都是那个类型的 public 属性」—— 是**上界宽松**的检查，会把注释里、别的类型里、局部变量同名的都算进去。**

### 仍然 Unknown

**`BotTask.Task` 是什么类型**（**若它是嵌套任务对象，「种类」可能在里面**）· **`Task.Type` 有没有读点**（决定能否安全删）·
**`TaskGroup` 那套 solver 配置复刻件挂在哪**（`KasadaSolvers` / `CloudflareClearance` 在，挂载点没查）

### 教训

> **「这个字段存不存在」少了一个维度 —— **在哪个类型上**。**
> **R858 我列了两种可能，实际是第三种：镜像有，但在另一个类型上。补上这个维度的成本极低，因为 R859 已经给出了按类型抽表的语法。**
"""

BACKLOG_ADD = """

## 判据 (f) — 模型层齐备；`Task.Type` 冗余（R860）

| 模型 | 镜像 | 复刻件 |
|---|---|---|
| `BotTask` | 14（**无 Type**；有 `Task` 嵌套、`StartTime`、`Status`） | **14/14** |
| `BaseCheckout` | 8（**有 Type**） | **8/8** |
| `TaskGroup` | 17（`CaptchaSource` · `CloudflareSolverId` · `ProfileLimit` · `CheckoutLimit` · `TotalCheckouts` · `TotalDeclines` · `Webhooks`） | **17/17** |
| `WebTask` | 2 | **2/2** |

**→ `Tasks.cs` 的 `Type` 是**冗余声明**，正确那份在 `BaseCheckout` 上。**

### 优先级 ② 的 Observation

**solver / 配额 / 计数全挂在 `TaskGroup`，不是单任务** —— **一个组共用同一套 solver 配置。**

### 未删的理由

**查了「有没有写」（0 处），没查「有没有读」。只读不写也可能被序列化进 `tasks.json` → 改输出结构 → 影响用例。**

### 对照的边界

**正则 `\\b<属性名>\\b` 搜**整个模型文件**，不是解析属性声明 → **上界宽松**，会把注释/别的类型/局部变量算进去。**

| 仍 Unknown | |
|---|---|
| `BotTask.Task` 是什么类型 | **若嵌套任务对象，「种类」可能在里** |
| `Task.Type` 有没有读点 | 决定能否安全删 |
| `TaskGroup` solver 配置复刻件挂在哪 | `KasadaSolvers`/`CloudflareClearance` 在，挂载点未查 |

**纪律**：**「字段存不存在」少了「在哪个类型上」这一维。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R860", BLOCKER)
    ensure(RSTATUS, "R860", BLOCKER)
    ensure(RVERDICT, "第 860 轮", VERDICT)
    ensure(BACKLOG, "R860", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R860" not in h:
        h += ("\n## R860 补充 — 模型层齐备，Task.Type 冗余\n\n"
              "**镜像 schema：`BotTask` 14（无 Type，有 `Task` 嵌套）· `BaseCheckout` 8（**有 Type**）· `TaskGroup` 17 · `WebTask` 2。**\n"
              "**复刻件对照 14/14 · 8/8 · 17/17 · 2/2 —— 齐备。→ `Tasks.cs` 的 `Type` 是冗余，正确那份在 `BaseCheckout`。**\n"
              "**优先级 ② Observation：`CaptchaSource` · `CloudflareSolverId` · 配额 · 计数全挂 `TaskGroup`，不是单任务。**\n"
              "**未删理由：查了「有没有写」没查「有没有读」—— 只读不写也可能进 `tasks.json`，改输出结构会动用例。**\n"
              "**对照是上界宽松**（正则搜整个文件，不是解析声明）。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R860"), (RSTATUS, "R860"), (RVERDICT, "第 860 轮"), (BACKLOG, "R860")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R860: the model layer is complete, so Task.Type is redundant rather than missing\n\n"
         "Applying R859's property-accessor syntax to four more types gives the image's model schema: BotTask with"
         " fourteen properties, BaseCheckout with eight, TaskGroup with seventeen, WebTask with two. BotTask's list has"
         " no Type. BaseCheckout's does.\n\n"
         "That answers R858 with a third possibility neither of its two branches covered. The image does have a Type, but"
         " it lives on the checkout record rather than on the task, and the replica's BaseCheckout already carries it."
         " So the unwritten Type in Tasks.cs is a redundant declaration beside a correct one, not a missing field and not"
         " an image field that wants a writer.\n\n"
         "Checking the replica against the four schemas gives fourteen of fourteen, eight of eight, seventeen of"
         " seventeen and two of two. The model layer is complete, subject to one caveat: each check searched the model"
         " file for the property name as a whole word rather than parsing declarations, so it shows the names are"
         " present, not that each is a public property of that exact type. It errs loose and would count a mention in a"
         " comment or a local of the same name.\n\n"
         "A finding worth carrying to priority two came out of the same table. TaskGroup holds CaptchaSource,"
         " CloudflareSolverId, ProfileLimit, CheckoutLimit, TotalCheckouts, TotalDeclines, UsageExpiry and Webhooks all at"
         " once, which means solver choice and quota are configured per group rather than per task. Where the replica"
         " hangs KasadaSolvers and CloudflareClearance was not checked, but this identifies the correct mounting point.\n\n"
         "The field was not removed, and the reason is a distinction that has bitten this session before. I checked"
         " whether anything writes it and found nothing; I did not check whether anything reads it. A field that is only"
         " read is worse than one nobody touches, because it is always empty -- and if it is serialised into tasks.json"
         " then removing it changes an output structure that existing tests may pin. So the next step is to find readers,\n"
         " not to delete.\n\n"
         "Unknown: what type BotTask.Task is, which matters because a nested task object is the most likely home for a"
         " kind discriminator; whether Task.Type has any reader; and where the TaskGroup solver configuration is mounted"
         " in the replica.\n\n"
         "The lesson is that 'does this field exist' was missing a dimension -- on which type. One round ago I listed two"
         " possibilities and the truth was a third, and the cost of catching it was almost nothing because R859 had"
         " already built the table-reading syntax; this round only pointed it at four more types.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
