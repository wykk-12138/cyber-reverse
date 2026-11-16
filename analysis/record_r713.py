"""Record R713: two implemented by elimination, sixteen declined with named reasons."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 142. 18 条 `Getter/Setter` 不是"机械活"：**做 2 条，拒 16 条**，每条都给理由

> R713。改 `NotificationService.cs`。

### 一、上一轮我说错了一件事

R712 结尾我写「先做 18 条 `Getter/Setter`（可写属性，**最机械**）」。
**这句话不成立。** 描述符只给**名字**和**方向**（Getter / Setter），**不给类型、不给含义**。

而 `CreateModel` 里有一条前一轮留下的注释，正好管这件事：

> **R363**：… `Input` / `Inputs` 是**故意**不做的 —— "input" 可能是商品选项、也可能是选项列表，
> **选一个就是猜行为，不是猜数据**。

**那条先例否掉了"照名字加属性"这个做法本身。**

### 二、做的那 2 条，靠排除法不是靠猜

原版在 `Notification` 上绑定的名字**正好四个**：`Title` / `Timestamp` / `Message` / `Type`。
复刻件的 record **正好四个位置参数**：`Kind` / `Title` / `Body` / `Timestamp`。

**两个精确对上**（`Title`、`Timestamp`），剩下两个**必须 1:1** → `Message↔Body`、`Type↔Kind`。
**Inference（高）** —— 依据是基数相等 + 两个已对齐，不是"Message 听起来像 Body"。

实现成**别名**：

```csharp
public string Message => Body;
public NotificationKind Type => Kind;
```

**行为一字未动**：构造调用、代码路径全不变，改的只是"能不能被 `Message` 绑定到"。

### 三、拒掉的 16 条，分三组

| 组 | 条数 | 为什么不做 |
|---|---|---|
| `EditValue\\`1` 的 `Value_92`/`_100`、`HasMultiple_87…_101` | 12 | **语义 Unknown**。加 12 个空属性只为了让 `undeclared` 变小，那是把度量当目标。名字古怪是 Observation，含义不是 |
| `CreateModel.Input` / `Inputs` | 2 | R363 已经判过：候选不唯一，选一个就是发明 |
| `BotTask.Running` | 1 | 同上 —— `Running` 是 bool？是 `TaskState` 的派生？是计时器状态？三个都可能，没有基数能排除 |
| 命令形态的 `Save`/`Create`/`Reset`/`Export`/`Link`/`Edit` | 6 | **`Getter/Setter` 挂在命令名上本身可疑** —— 命令通常是 getter-only。要判定得先看各视图的基类与原版反编译，本轮没做 |

**注意这和 R711 的 `Close` 不同**：`Close` 是 `Getter`（单方向）+ 我在源码里看到它已经是 lambda 按钮，
**两条证据合起来**才够。这里只有一条。

### 四、数字

```
undeclared  44 -> 42        （两条 Notification 成员）
完整套件     1624 通过 / 0 失败
形状差异     78（不变 —— 别名不改变形状）
四项度量     4 / 0 / 17 / 78 / 0（名字级/类型级/类型缺失/形状/文案）
```

### 五、仍然 Unknown

- `EditValue\\`1` 那 12 个名字的语义：**Unknown**，且**不打算靠猜去填**。
- 6 条命令形态的 `Getter/Setter`：是命令还是有 setter 的属性 —— **Unknown**，要反编译。
- 原版 `Notification.Message` 与复刻件 `Body` 的行为是否等价：**Unknown** ——
  这是别名，不是独立实现；如果原版在这两个名字上行为不同，这里是看不见的。

### 六、这一轮的判断

> **拒掉一条缺口，比硬填一条更需要理由 —— 但理由是一样的东西：证据。**

16 条全部保留在 `undeclared` 里，`docs/MEMBER_GAP_EVIDENCE.md` 里有它们每一条的描述符。
**它们不是被遗忘了，是被判定为"证据不够，不填"。**
"""

VERDICT = """

---

## 第 713 轮：18 条里做 2 条，拒 16 条

### 上一轮有句话说错了

R712 结尾我写「18 条 `Getter/Setter`，**最机械**」。**不成立。**
描述符只给名字和方向，**不给类型、不给含义**。

`CreateModel` 里 R363 的注释正好管这个：

> `Input`/`Inputs` 故意不做 —— 可能是选项也可能是选项列表，**选一个就是猜行为**。

### 做的 2 条：排除法，不是猜

原版在 `Notification` 上绑定**正好四个**名字（Title/Timestamp/Message/Type），
复刻件 record **正好四个**参数（Kind/Title/Body/Timestamp）。**两个已对上，剩下必须 1:1。**

```csharp
public string Message => Body;
public NotificationKind Type => Kind;
```

**行为一字未动**，只是让 `Message` 能被绑到。**Inference（高）**。

### 拒的 16 条

| 组 | 数 | 理由 |
|---|---|---|
| `EditValue\\`1` 数字后缀 | 12 | **语义 Unknown**；加空属性只为让度量变小 |
| `CreateModel.Input(s)` | 2 | R363 已判：候选不唯一 |
| `BotTask.Running` | 1 | 三四种可能，没有基数能排除 |
| 命令形态的 G/S | 6 | G/S 挂在命令名上本身可疑，需反编译 |

**与 R711 的 `Close` 不同**：那是 `Getter` 单方向 + 源码里已是 lambda 按钮，**两条证据**才够；这里只有一条。

### 数字

```
undeclared 44 -> 42 · 套件 1624 · 形状 78 · 度量 4/0/17/78/0
```

### 一句话

> **拒掉一条缺口，比硬填一条更需要理由 —— 但理由是一样的东西：证据。**

> 16 条不是被遗忘了，是被判定为「证据不够，不填」，全部留在 `undeclared` 里，
> 每条的描述符都在 `docs/MEMBER_GAP_EVIDENCE.md`。

### 下一轮

攻那 6 条命令形态的 G/S：反编译看它们到底是不是命令。这一步能顺带判掉 `BotTask.Running` 一类。
"""


def main():
    for p, marker, text in ((P1, "R713", BLOCKER), (P3, "R713", BLOCKER), (P2, "第 713 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R713: Notification.Message/Type by elimination; 16 of the 18 declined with reasons\n\n"
         "R712 called the 18 Getter/Setter members mechanical. A descriptor gives a name and a direction,\n"
         "not a type or a meaning, so that was wrong -- and CreateModel already carried R363's note\n"
         "declining Input/Inputs for exactly this reason ('picking one would be a guess about behaviour').\n\n"
         "Done: the original binds four names on Notification (Title, Timestamp, Message, Type) and the\n"
         "record has four positional members (Kind, Title, Body, Timestamp). Two match outright, so the\n"
         "other two correspond one-to-one. Message and Type are aliases over Body and Kind -- behaviour\n"
         "unchanged, only bindability gained.\n\n"
         "Declined 16: the twelve EditValue`1 numbered names (semantics Unknown; filling them would move\n"
         "the metric without implementing anything), CreateModel.Input/Inputs (R363), BotTask.Running\n"
         "(no cardinality narrows it), and six command-shaped Getter/Setter members (a setter on a command\n"
         "name is itself suspicious and needs decompilation).\n\n"
         "undeclared 44 -> 42; suite 1624 pass / 0 fail; shape 78 unchanged."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
