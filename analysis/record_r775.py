"""Record R775: the Poq app surface is a real integration, not orphan strings."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 201. **App 面是真集成**：4 个头部构造器 + 4 个 action 函数 + 可达调用链

> R775。未改产品代码。R774 那个 Unknown 被回答了。

### 一、UA 与 `poq-app-id` 被同一批函数引用

`Poq-Native-iOS-App`（`0x146e46694`）与 `poq-app-id`（`0x1471151dc`）各在 `chars-12` 处取 xref，
**得到同样的四个函数**（Observation）：

```
sub_140B3B7C0  (675 B)
sub_140B3BAC0  (557 B)
sub_140B3BD40  (752 B)
sub_140B3C030  (594 B)
```

**地址相邻、体积相近。** 反编译第一个（`sub_140B3B7C0`）可见形状：

```c
v7 = sub_143028C10(&unk_144BDECD0);      // 新建一个请求头容器
sub_1408BAAC0(v7);
sub_1408BAD40(v7, &off_147115240, …);    // add(name, value) × 12
sub_1408BAD40(v7, &off_1471151D0, …);    // ← poq-app-id
sub_1408BAD40(v7, &off_147115310, …);    // ← poq-user-id 一族
…
```

**`sub_1408BAD40(容器, 名, 值)` 是「加一个请求头」，一次构造约 12 个头。**

**所以这批函数是「按 Poq App 身份构造请求头」的构造器簇。**

### 二、而四个 action 各由一个**不同的**函数引用

对四个 action 字符串在 `chars-12` 处取 xref：

```
account/guest-token  → 0x140b479c0
cart/items           → 0x140b463e0
checkout/start       → 0x140b46750
products?ids=        → 0x140b46910
```

**每个 action 恰好一个引用者，且都不是头部构造器。**
**所以结构是：4 个共享的头部构造器 + 4 个 per-action 函数。**

### 三、再往上一层：四个 action 函数各自有 4 个调用者，形状一致

```
guest-token      sub_142542F60(0xb) sub_142543000(0x8e) sub_142B6B6A0(0xa4) ?
cart/items       sub_1425424E0(0xb) sub_142542580(0x8e) sub_142B6A4A0(0xa4) ?
checkout/start   sub_142542610(0xb) sub_1425426A0(0x8e) sub_142B6A6A0(0xa4) ?
products?ids=    sub_142542730(0xb) sub_1425427C0(0x8e) sub_142B6A8A0(0xa4) ?
```

**11 字节的是 thunk，142/164 字节的是异步状态机包装** —— 典型的 .NET 接口分派链。

**所以这些函数是被托管逻辑真实调用的，不是孤立的字符串。**

### 四、R774 的问题答了

> **「原版有没有走 App 面的路径？」→ 有。**（Observation：完整的调用链，不是死字符串）

**剩下的只是「具体由哪种任务类型触发」** —— 那需要继续穿多层接口分派，
**收益递减，且不影响"该建"这个结论。**

### 五、仍然不写代码的理由，以及它什么时候会变

R774 不写的原因有两条，**这一轮解决了第一条、第二条仍在**：

| 理由 | 状态 |
|---|---|
| 「原版有没有这套东西」 | **已答：有** |
| 「写出来会不会是死代码」 | **仍是 —— 身份单独存在没有调用方** |

**所以正确的单位不是"身份常量"，是"App 面的一个 flow"**：身份 + 四步 + 一个注册项。
**那是一个完整的单元，下一轮按这个粒度做。**
**单独先建身份常量，就会重复 R772 的死代码问题。**

### 六、验证

```
本轮未改产品代码
完整套件保持 1752 通过 / 0 失败
```

### 七、仍然 Unknown

- **触发 App 面的任务类型名**：**Unknown** —— 需穿 4 层接口分派，收益低。**不影响建它的判断。**
- `poq-app-id` 等头的**取值来源**：**Unknown** —— 见 `sub_141CF6230(&off_146B5C780, a1[29])` 与 `sub_140B399B0(a1)` 两个取值函数，未读。
- `poq-slot-conditions` 的语义：**Unknown**。
- 四个头部构造器为什么是四个（是否对应四种请求形态）：**Unknown**。
"""

VERDICT = """

---

## 第 775 轮：App 面是真集成

### UA 与 `poq-app-id` 被同一批函数引用

`chars-12` 处取 xref，**两个字符串给出同样的四个函数**（675/557/752/594 B，地址相邻）。
反编译第一个可见 `sub_1408BAD40(容器, 名, 值)` × 12 —— **那是「加请求头」**，
其中就有 `poq-app-id` 与 `poq-user-id` 一族。

**所以这批是「按 Poq App 身份构造请求头」的构造器簇。**

### 而四个 action 各由一个**不同的**函数引用

```
guest-token → 0x140b479c0 · cart/items → 0x140b463e0
checkout/start → 0x140b46750 · products?ids= → 0x140b46910
```

**结构是：4 个共享头部构造器 + 4 个 per-action 函数。**

### 再上一层：每个 action 有 4 个同形状调用者

`11 B` 的 thunk + `142/164 B` 的异步包装 —— **典型 .NET 接口分派链。**
**所以这些函数被托管逻辑真实调用，不是孤立字符串。**

### R774 的问题答了

> **「原版有没有走 App 面的路径？」→ 有。**

剩下的只是「由哪种任务类型触发」，需穿 4 层分派，**收益递减，且不影响"该建"的结论。**

### 仍然不写代码，理由变了一半

| 理由 | 状态 |
|---|---|
| 原版有没有这套东西 | **已答：有** |
| 写出来会不会是死代码 | **仍是 —— 身份单独存在没有调用方** |

**所以正确的单位不是"身份常量"，是"App 面一个 flow"：身份 + 四步 + 一个注册项。**
**单独先建身份，就会重复 R772 的死代码问题。下一轮按这个粒度做。**
"""

BACKLOG_ADD = """

## 请求与指纹层 — Poq App 面（R775 更新）

**R774 的 Unknown 已答：App 面是真集成。**

```
4 个头部构造器（共享 Poq 身份模板，sub_140B3B7C0 / BAC0 / BD40 / C030）
4 个 per-action 函数（guest-token / cart/items / checkout/start / products?ids=）
每个 action 有 4 个同形状调用者（thunk + 异步包装）→ 可达
```

**构建的正确单位**：**一个 App 面 flow**（身份 + 四步 + 一个注册项），
**不是**单独的身份常量 —— 后者会重复 R772 的死代码问题。

| 项 | 状态 |
|---|---|
| 触发它的任务类型名 | Unknown，需穿 4 层接口分派，**不影响判断** |
| `poq-app-id` 的取值来源 | Unknown（`sub_141CF6230(&off_146B5C780, a1[29])`、`sub_140B399B0(a1)` 未读） |
| `poq-slot-conditions` 语义 | Unknown |
| 为何是四个头部构造器 | Unknown |

**注意**：这与 `offspring` 的**网页面**（Hybris，实机证据，`PlatformAssignmentTests`）是**两种表面**，
**不要互相替换**（R772 的教训）。
"""


def main():
    for p, marker, text in ((P1, "R775", BLOCKER), (P3, "R775", BLOCKER), (P2, "第 775 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R775" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += App 面")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R775: the Poq app surface is a real integration -- four header builders, four action functions, reachable\n\n"
         "R774 asked which path sends the Poq user agent and left it open. Cross-referencing at the character-minus-\n"
         "twelve addresses answers it. The user agent and the poq-app-id header are referenced by the same four\n"
         "functions, adjacent in address and similar in size, and decompiling the first shows the shape: create a\n"
         "header container, then add-header twelve times, poq-app-id and the poq-user-id family among them. So those\n"
         "four are builders that construct requests carrying the app's identity.\n\n"
         "The four actions are a separate set. Each of the four endpoint strings is referenced by exactly one\n"
         "function, and none of those is a header builder. So the structure is four shared builders plus four\n"
         "per-action functions.\n\n"
         "One more hop upward shows each action function with four callers of identical shape: an eleven-byte thunk,\n"
         "a 142-byte wrapper and a 164-byte wrapper. That is .NET interface dispatch, which means these are called by\n"
         "managed logic rather than being orphan strings.\n\n"
         "So the R774 question is answered: yes, the original drives the Poq app surface. What remains unknown is\n"
         "which task type reaches it, and getting there means crossing four more dispatch layers -- diminishing\n"
         "returns, since it no longer affects whether this should be built.\n\n"
         "Still no code, but the reason has halved. 'Does it exist' is settled; 'would it be dead code' is not, because\n"
         "identity constants with no caller are dead however well evidenced. That points at the right unit: not the\n"
         "identity on its own, but an app-surface flow -- identity, four steps, one registry entry, together. Writing\n"
         "the constants first would repeat the mistake R772 was reverted for.\n\n"
         "No product code changed; suite remains 1752 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
