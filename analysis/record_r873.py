"""Record R873: four more draw steps, and the rule that decided which four."""

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
### 再写四个：`coverage 3 → 7`，而选哪四个是有判据的（R873）

**判据：R116 配了 14 步端点；其中**查询形状写在常量里**的才可写（GET + 参数名固定）。
其余是 POST，请求体无证据。**

| 步骤 | 端点 | 形状 | 写了吗 |
|---|---|---|---|
| `StartDrawFlow` | `DrawScratchDetail` | `?uniqCode=` | **写了** |
| `FindDraw` | `DrawScratchDetail` | `?uniqCode=` | **写了** |
| `FindDates` | `StoreTicketDates` | 无查询 | **写了** |
| `FindTimeSlots` | `StoreTicketMainPage` | `?uniqID=` | **写了** |
| `EnterDraw` | `DrawScratchDraw` | POST | **没写** —— 请求体无证据 |
| `ChooseGoods` | `DrawScratchChooseGoods` | POST | **没写** |
| `FindMegaDraw` · `EnterDrawEvent` | `MegaDrawHit` | POST | 没写 |
| `RedeemMemberPoints` | `PointsRedeemDraw` | POST | 没写 |
| `RedeemLuckPoints` | `LuckyPointsDraw` | POST | 没写 |
| `EnterExhibit` | `StoreOfflineDrawJoin` | POST | **R872 写了** —— 体 = 上一步响应 |
| `EnterReservation` | `StoreOfflineDrawJoin` | POST | 没写 |

**所以「写了几步」不是均匀推进，是**按证据形状分批**：**
**GET + 固定参数名的先写；POST 一律等请求体有证据。**

### 两个缺参数就失败的步骤

**`StartDrawFlow` / `FindDraw` 要 `uniqCode`，`FindTimeSlots` 要 `uniqID`，全部从 session 取，
而**这个复刻件里没有任何地方往 session 放它们**。所以这三个在当前代码里会明确失败。**

**这不是缺陷，是当前状态的可读表达：**缺什么，失败信息就写什么。
**如果它们发空参数，服务器可能返回 200，而那会被读成「跑通了」。**

### 而 `uniqCode` 这个名字不是猜的

**R850 在镜像里找到 `_uniqCode` · `currentUniqCode` · `storeUniqCode` · `&storeUniqCode=1` 四个记号。
所以参数名有出处，只是**谁来填**没建立。**

### 数字

```
map.Count      168 -> 172
implementable    3 ->   7
sequence.Count  24 不变
```

**测试四数一起钉（172 / 24 / 7 + 七条 `CanRunStep`，每条标着哪一轮加的）。**
"""

if "再写四个：`coverage 3 → 7`" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R873 appended")

BLOCKER = """

---

## 297. 再写四个 —— 而「写哪四个」有判据：`coverage 3 → 7`

> R873。**改了产品代码。** 套件 **1773 通过 / 0 失败 / 0 跳过**。

### 一、判据不是「还没写的就写」

**R116 配了 14 步端点。可写的条件是：**查询形状写在常量里**（GET + 参数名固定）。
其余是 POST，请求体无证据 —— 写出来就是编。**

| 写了 | 端点 | 形状 |
|---|---|---|
| `StartDrawFlow` | `DrawScratchDetail` | `?uniqCode=` |
| `FindDraw` | `DrawScratchDetail` | `?uniqCode=` |
| `FindDates` | `StoreTicketDates` | 无查询 |
| `FindTimeSlots` | `StoreTicketMainPage` | `?uniqID=` |

| 没写 | 为什么 |
|---|---|
| `EnterDraw` · `ChooseGoods` · `FindMegaDraw` · `EnterDrawEvent` · `RedeemMemberPoints` · `RedeemLuckPoints` · `EnterReservation` | **POST，请求体无证据** |

**所以推进不是均匀的，是按**证据形状**分批。这不是保守，是「能证明发什么才发」。**

### 二、三个步骤缺参数会失败，而这是刻意的

**`StartDrawFlow` / `FindDraw` 要 `uniqCode`，`FindTimeSlots` 要 `uniqID`，都从 session 取 ——
而**这个复刻件里没有任何地方往 session 放它们**。**

**所以这三个现在会明确失败。失败信息就是缺什么。**

**如果它们发空参数，服务器可能返回 200 —— 而那会被读成「跑通了」。
这是本会话第八次遇到同一个形态，这次仍然是在写的时候避开的。**

### 三、而 `uniqCode` 这个名字有出处

**R850 在镜像里找到四个记号：`_uniqCode` · `currentUniqCode` · `storeUniqCode` · `&storeUniqCode=1`。
所以参数名不是我起的，只是**谁来填**没建立。**

**这两件事必须分开写：参数名有证据（Observation），填值链路没建立（Unknown）。**

### 四、数字

```
map.Count      168 -> 172
implementable    3 ->   7
sequence.Count  24 不变
```

**测试四数一起钉，而七条 `CanRunStep` 每条标着哪一轮加的** ——
下次有人问「这七步什么时候写的」，测试自己就答了。

### 五、验证

```
PopMartEndpoints 常量形状扫描 -> DrawScratchDetail?uniqCode= / StoreTicketDates（无查询）/ StoreTicketMainPage?uniqID=
                                DrawScratchDraw · DrawScratchChooseGoods（POST，无查询串）
D:\\tools\\dotnet8\\dotnet.exe build ... -> 0 错误
test --filter FlowSequenceTests          -> 7 通过 / 0 失败
python tools\\metrics_report.py           -> 1773 通过 / 0 失败 / 0 跳过
```

### 六、仍然 Unknown

- **`uniqCode` / `uniqID` 从哪来**：**Unknown** ——
  **这是 R873 之后最挡路的一条：三个步骤已写但跑不通，因为没人填这两个值。**
  **下一轮该查的是「镜像里谁 produce 了它们」，不是再写步骤。**
- **那七个 POST 的请求体**：**Unknown** —— 它们的端点有了，形状没有。
- **`StoreOfflineDrawJoin` 也服务 `EnterReservation`**：**Observation（R116）** ——
  **而 `EnterReservation` 的体是什么，与已写的 `EnterExhibit` 是否同形，未查。**

### 七、教训

**这一轮最重要的不是写了四步，是**说清了为什么只写四步**。**

**如果只报「coverage 3→7」，下一轮的人会问「为什么不写完 24 步」。
而答案已经在表里：七个是 POST 无体，十个端点都没配。**

**所以每个进度数字旁边都该有「其余多少、为什么」。**
**R844 那个 16.9% 的错就在这儿 —— 它只有数字，没有旁边的分类。**
"""

VERDICT = """

---

## 第 873 轮：再写四个 —— 而「写哪四个」有判据：coverage 3 → 7

### 判据不是「还没写的就写」

**可写条件：查询形状写在常量里（GET + 参数名固定）。POST 的请求体无证据，写出来就是编。**

| 写了 | 端点 | 形状 |
|---|---|---|
| `StartDrawFlow` · `FindDraw` | `DrawScratchDetail` | `?uniqCode=` |
| `FindDates` | `StoreTicketDates` | 无查询 |
| `FindTimeSlots` | `StoreTicketMainPage` | `?uniqID=` |

| 没写（7 个 POST） | 为什么 |
|---|---|
| `EnterDraw` · `ChooseGoods` · `FindMegaDraw` · `EnterDrawEvent` · `RedeemMemberPoints` · `RedeemLuckPoints` · `EnterReservation` | **请求体无证据** |

> **推进不是均匀的，是按**证据形状**分批。这不是保守，是「能证明发什么才发」。**

### 三个步骤缺参数会失败，刻意

**`uniqCode` / `uniqID` 从 session 取，而**没有任何地方往里放** → 三个步骤现在会明确失败。**

**如果发空参数，服务器可能返回 200 —— 那会被读成「跑通了」。第八次同一形态，仍在写时避开。**

### 而参数名有出处

**R850 在镜像里找到 `_uniqCode` · `currentUniqCode` · `storeUniqCode` · `&storeUniqCode=1`。
参数名是 Observation，**填值链路没建立是 Unknown —— 两件事分开写。****

### 数字

```
map 168 → 172 · coverage 3 → 7 · sequence 24 不变
七条 CanRunStep 每条标着哪一轮加的 —— 下次问「这七步什么时候写的」，测试自己答
套件 1773 通过 / 0 失败
```

### 仍然 Unknown

**`uniqCode`/`uniqID` 从哪来** —— **R873 之后最挡路的一条：三步已写但跑不通。
下一轮该查「镜像里谁 produce 它们」，不是再写步骤** · **七个 POST 的请求体** ·
**`EnterReservation` 的体是否同形于已写的 `EnterExhibit`**

### 教训

> **最重要的不是写了四步，是说清了**为什么只写四步**。**
> **只报「3→7」，下一轮会问「为什么不写完 24 步」；答案已在表里：七个 POST 无体，十个端点没配。**
> **所以每个进度数字旁边都该有「其余多少、为什么」—— R844 那个 16.9% 的错就在这儿：只有数字，没有分类。**
"""

BACKLOG_ADD = """

## 优先级 ① — 再写四个（R873，**已改产品代码**）：coverage 3 → 7

**判据：查询形状写在常量里才可写。7 个 POST 请求体无证据，不写。**

| 写了 | 端点 | 形状 |
|---|---|---|
| `StartDrawFlow` · `FindDraw` | `DrawScratchDetail` | `?uniqCode=` |
| `FindDates` | `StoreTicketDates` | 无查询 |
| `FindTimeSlots` | `StoreTicketMainPage` | `?uniqID=` |

| 没写 | 原因 |
|---|---|
| `EnterDraw` `ChooseGoods` `FindMegaDraw` `EnterDrawEvent` `RedeemMemberPoints` `RedeemLuckPoints` `EnterReservation` | **POST，体无证据** |

### 三个步骤会明确失败（刻意）

**`uniqCode`/`uniqID` 从 session 取，**而没人往里放** → 三步跑不通但报得清楚。
**发空参数可能得 200，那会被读成「跑通了」。**

**参数名是 Observation（R850 的 `_uniqCode`/`storeUniqCode` 记号）；填值链路是 Unknown。**

### 数字

`map 168→172` · `coverage 3→7` · `sequence 24` · **七条 CanRunStep 各标轮次** · 套件 1773 通过。

| 仍 Unknown | |
|---|---|
| **`uniqCode`/`uniqID` 从哪来** | **最挡路：三步已写但跑不通 → 下一轮查「谁 produce 它们」，不是再写步骤** |
| 七个 POST 的请求体 | 端点有，形状没有 |
| `EnterReservation` 体是否同形于 `EnterExhibit` | 未查 |

**纪律**：**每个进度数字旁边都要有「其余多少、为什么」—— R844 的 16.9% 就是只有数字没有分类。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R873", BLOCKER)
    ensure(RSTATUS, "R873", BLOCKER)
    ensure(RVERDICT, "第 873 轮", VERDICT)
    ensure(BACKLOG, "R873", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R873" not in h:
        h += ("\n## R873 补充 — 再写四个（**已改产品代码**）：coverage 3 → 7\n\n"
              "**判据：查询形状写在常量里才可写。**写了 `StartDrawFlow`/`FindDraw`（`?uniqCode=`）· `FindDates`（无查询）· `FindTimeSlots`（`?uniqID=`）。"
              "**7 个 POST 请求体无证据 → 不写。**\n"
              "**三个步骤会明确失败（刻意）**：`uniqCode`/`uniqID` 从 session 取而**没人往里放** —— 发空参数可能得 200，会被读成跑通。\n"
              "**数字：`map 168→172` · `coverage 3→7` · 七条 CanRunStep 各标轮次。套件 1773 通过 / 0 失败。**\n"
              "**下一轮该查「镜像里谁 produce `uniqCode`/`uniqID`」，不是再写步骤 —— 三步已写但跑不通。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R873"), (RSTATUS, "R873"), (RVERDICT, "第 873 轮"), (BACKLOG, "R873")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R873: four more draw steps, and the rule that says why only four\n\n"
         "R116 paired fourteen of Pop Mart's steps with shop endpoints. A step is writable only when the endpoint's"
         " query shape is fixed in the constant itself, because that is what makes the request evidenced rather than"
         " invented. Seven of the fourteen are POSTs whose bodies nothing evidences, so four were written and seven"
         " were not: StartDrawFlow and FindDraw against drawScratch/detail with uniqCode, FindDates against"
         " storeTicket/dateList with no query at all, and FindTimeSlots against storeTicket/mainPage with uniqID.\n\n"
         "Three of the four need a value the replica never supplies. uniqCode and uniqID are read from the session and"
         " nothing puts them there, so those steps fail with a message naming what is missing. That is deliberate: an"
         " empty parameter can still earn a 200, and a 200 from a request carrying nothing is read as success. This is"
         " the eighth time this project has met that shape, and for the second round running it was avoided while\n"
         " writing rather than removed afterwards.\n\n"
         "The parameter names themselves are not guesses. R850 found _uniqCode, currentUniqCode, storeUniqCode and a\n"
         " &storeUniqCode=1 fragment in the image. So the naming is an observation and the supply chain is an unknown,\n"
         " and those two facts belong in separate sentences rather than merged into 'partly done'.\n\n"
         "Coverage moved from three of twenty-four to seven, the map from 168 to 172, and the test pins all four"
         " numbers with each CanRunStep line naming the round that added it, so the question of when these seven\n"
         " arrived is answered by the test itself.\n\n"
         "What matters most this round is not the four steps but the statement of why only four. A bare coverage\n"
         " number invites the question of why the other seventeen are missing; the answer is in the table, where seven\n"
         " are POSTs without bodies and the endpoint families for the rest were never paired. R844's 16.9 percent failed\n"
         " for exactly this reason -- it had the number and not the classification beside it.\n\n"
         "Unknown: where uniqCode and uniqID come from, which is now the most obstructive item since three written steps\n"
         " cannot run without them, and the next round should look for what produces them in the image rather than\n"
         " write more steps; the request bodies for the seven POSTs; and whether EnterReservation's body matches the\n"
         " EnterExhibit body already written, given R116 pairs both with the same join endpoint.\n\n"
         "Product code changed; suite green at 1773."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
