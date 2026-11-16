"""Record R774: the app surface is a request identity, not a flow family."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 200. App 面不是 flow 家族，是**一套请求身份** —— 上一轮的方向错在层级

> R774。未改产品代码。

### 一、先问该先问的问题

上一轮我被 `PlatformAssignmentTests` 驳回后才意识到：**该先问「原版有没有把 Poq 当作平台」**。
这一轮就查这个。平台名在原版里是一族词（`Demandware` / `Hybris` / `Magento`），
**如果 `Poq` 在这族里，建 flow 才有结构依据。**

### 二、结果：不在那一族里，而在**请求头**里

`^Poq` 与 `^poq` 各 7 条（Observation）：

```
Poq-Native-iOS-App          ← User-Agent
poq-app-id
poq-app-identifier
poq-country-identifier
poq-currency-identifier
poq-slot-conditions
poq-user-id                 ← 5 个自定义请求头
```

**原版冒充的是 Poq 的 iOS App。** 这不是「一个新平台类型」，是**一个请求身份** ——
**所以它属于第 3 优先级（请求与指纹层），不属于第 1（站点 flow）。**

**上一轮我把它当成第 1 层的东西去建，层级就错了。** 驳回我的那个测试说的是网页面的平台，
而这一族字符串说的是 App 面的身份 —— **两条证据不在同一层，所以并不矛盾。**

### 三、复刻件现状（Observation）

```
poq                    Registry.cs(1)  ← 只是我上一轮加的那条注释
Poq                    CanvasTable.Generated.cs(1)  ← 无关
Poq-Native-iOS-App     ABSENT
poq-app-id             ABSENT
poq-slot-conditions    ABSENT
poq-user-id            ABSENT
```

**整套 App 身份在复刻件里一处都没有。**

身份层的现有落点：`BrowserIdentity.cs`（95 行，会话级浏览器身份）、
`BrowserFingerprint.cs`（193 行）、`BrowserProfile.cs`（15 行）、`BrowserShim.cs`（204 行）。

### 四、**为什么这一轮仍然不写代码**

有两个理由，都指向同一个动作：

1. **写一个没有任何调用方的 `PoqAppIdentity` 类，就是新的死代码** ——
   上一轮我删掉 `PoqFlow` 用的正是这条理由，这一轮不能反过来用它。**前后要一致。**
2. **「原版有没有一条驱动 App 面的任务类型」仍然是 Unknown。**
   `Poq-Native-iOS-App` 出现在池子里，**说明原版会发这个 UA**，但**发在哪个环节、由哪种任务触发，不知道**。
   **没确认就建，正是上一轮犯的错。**

**所以本轮交付的是判断，不是代码：这套东西的归属层级确定了，落点也有了，缺的是「谁用它」。**

### 五、验证

```
本轮未改产品代码
完整套件保持 1752 通过 / 0 失败
```

### 六、仍然 Unknown

- **驱动 App 面的任务类型**：**Unknown** —— 这是唯一挡在实现前面的问题。
  候选查法：找发送 `Poq-Native-iOS-App` 的调用点（`-12` 处取 xref），看它属于哪条路径。
- `poq-app-id` 等头的**取值**：**Unknown** —— 只有头名，没有值。
- `poq-slot-conditions` 的语义：**Unknown** —— 「slot」在 Poq 里可能指投放位或时段条件。
- `office` client 与 `offspring` client 的头是否不同：**Unknown**。
"""

VERDICT = """

---

## 第 774 轮：层级搞错了，不是方向搞错了

### 先问该先问的问题

上一轮被测试驳回后我才想到：**该先查「原版有没有把 Poq 当作平台名」**。平台名在原版里是一族词。

### 结果：不在那一族，在请求头里

```
Poq-Native-iOS-App      ← User-Agent
poq-app-id · poq-app-identifier · poq-country-identifier
poq-currency-identifier · poq-slot-conditions · poq-user-id
```

**原版冒充 Poq 的 iOS App。这不是新平台，是一个请求身份。**
**所以它属于第 3 优先级（请求与指纹层），不属于第 1（站点 flow）。**

**上一轮的错在层级：** 驳回我的测试说的是网页面（Hybris），这一族字符串说的是 App 面身份 ——
**两条证据不在同一层，并不矛盾。**

### 复刻件现状

整套 App 身份**一处都没有**。身份层现有落点是 `BrowserIdentity` / `BrowserFingerprint` / `BrowserShim`。

### 为什么这轮仍然不写代码

1. 写一个没有调用方的 `PoqAppIdentity` 就是新的死代码 —— **上一轮删 `PoqFlow` 用的正是这条理由，这轮不能反过来用。**
2. **「谁发这个 UA」仍是 Unknown。** 出现在池子里说明原版会发，**但由哪种任务、在哪个环节，不知道。**

**所以本轮交付的是判断：归属层级确定了，落点有了，缺的是「谁用它」。**

### 仍然 Unknown

**驱动 App 面的任务类型** —— 唯一挡在实现前面的问题。
查法：找发送 `Poq-Native-iOS-App` 的调用点（`-12` 取 xref），看它属于哪条路径。
"""

BACKLOG_ADD = """

## 请求与指纹层 — Poq App 身份（R774）

**证据（Observation）**：`Poq-Native-iOS-App`（UA）+ `poq-app-id` / `poq-app-identifier` /
`poq-country-identifier` / `poq-currency-identifier` / `poq-slot-conditions` / `poq-user-id`（请求头）。

**归属**：第 3 优先级（请求与指纹层），**不是**站点 flow —— 上一轮错在这一层，见 R772/R773。

**复刻件现状**：整套身份**一处都没有**。

| 项 | 状态 |
|---|---|
| **谁发送这个 UA** | **Unknown —— 唯一挡在实现前面的事** |
| 查法 | 对 `Poq-Native-iOS-App` 在 `chars-12` 处取 xref，读调用点属于哪条路径 |
| 头的取值 | Unknown（只有头名） |
| `poq-slot-conditions` 语义 | Unknown |
| `office` 与 `offspring` 的头是否相同 | Unknown |

**实现前提**：确认调用链之后，把这套身份加进 `BrowserIdentity` / `BrowserFingerprint` 一族，
**不要建独立死类**（R772 的教训）。
"""


def main():
    for p, marker, text in ((P1, "R774", BLOCKER), (P3, "R774", BLOCKER), (P2, "第 774 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R774" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += Poq App 身份")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R774: the app surface is a request identity, not a flow family -- last round erred in level\n\n"
         "Last round's mistake was caught by a test, and the right response was to ask the question I had skipped: does\n"
         "the original treat Poq as a platform at all? Platform names form a family in this image -- Demandware,\n"
         "Hybris, Magento -- so if Poq belonged to it, building a flow would have had structural support.\n\n"
         "It does not. Poq appears as a User-Agent string, Poq-Native-iOS-App, together with five custom headers:\n"
         "poq-app-id, poq-app-identifier, poq-country-identifier, poq-currency-identifier, poq-slot-conditions and\n"
         "poq-user-id. The original is impersonating Poq's iOS app. That is a request identity, not a platform\n"
         "family, so it belongs to the third priority -- the request and fingerprint layer -- rather than the first.\n\n"
         "That also reconciles the two pieces of evidence that seemed to conflict. PlatformAssignmentTests is about\n"
         "the web surface and says Hybris with live proof; these strings are about the app surface and describe how\n"
         "to look like the app. They are not on the same level, so nothing is contradicted. Last round erred in level,\n"
         "not in direction.\n\n"
         "The replica has none of this identity anywhere -- not the UA, not one header.\n\n"
         "Still no code this round, for two reasons that point the same way. Writing a PoqAppIdentity class with no\n"
         "caller would be new dead code, which is precisely the argument I used to delete PoqFlow one round earlier;\n"
         "consistency costs something and this is where it costs it. And what remains unknown is which task type sends\n"
         "that User-Agent at all. It sits in the pool, so the original does send it somewhere, but not where or on\n"
         "what trigger. Building before answering that is the mistake of R772.\n\n"
         "So the deliverable is the judgement: the level is settled, the landing place is the BrowserIdentity family,\n"
         "and the open question is who uses it. The next step is an xref at the character-minus-twelve address of the\n"
         "User-Agent, to see which call path owns it.\n\n"
         "No product code changed; suite remains 1752 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
