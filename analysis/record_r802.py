"""Record R801/R802: a second yardstick existed all along, and hypecommerce moved onto it."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 226. 仓库里**一直有两套尺子**；我把两家不该豁免的塞进了豁免，然后撤回

> R801/R802。`ModuleCoverageTests.cs`：撤两条豁免；`hypecommerce` 从豁免移到 `NonCommerce`；
> `RetailFlows.cs`：`SubmitOrderAsync` 拆成 `ValidateEntryAsync` + `CreateEntryAsync`。

### 一、我先做错了一件事

查 `raffle` / `pocketgames` / `riotgames` 的镜像面，看到三家都不是七步结账，
**于是给 `raffle` 与 `pocketgames` 补了豁免条目。**

**跑完测试，输出里露出了一段我从没看过的东西**：

```
resolved 63/63 flows; fully covered 51; exempt 8
   raffle                  4/4  + + + +
   pocketgames             6/6  + + + + + +
   riotgames               7/7  + + + + + + +
```

**仓库早就有第二套尺子**：`NonCommerce` 字典，每个非结账模块**自带一组步骤名**，
另有一张表按那组步骤单独评。

**而这三家在那套尺子上全是满分。**

**所以我的两条豁免是多余的** —— 我把「已经在正确尺子上满分」的模块，
塞进了「尺子不适用」的名单。**撤回了，`exempt` 回到 6。**

**这是 §2.7 的又一次，而且是我自己踩的**：**假设只有一套矩阵，看到七步得分低就当成缺口。**

### 二、那 `hypecommerce` 呢 —— 它该被**测量**，不该被豁免

镜像给它两个端点：`entries/validate` 与 `entries/create`。**两个都有 builder，形状明确。**
**豁免是「没法量」，而它是「能量的」。**

所以：

1. `SubmitOrderAsync` 拆成 **`ValidateEntryAsync`** + **`CreateEntryAsync`**（两个具名步骤，对应两个端点）
2. `NonCommerce["hypecommerce"] = [ValidateEntryAsync, CreateEntryAsync]`
3. **从 `YardstickDoesNotApply` 里撤掉**

### 三、结果

```
resolved 63/63 flows; fully covered 51; exempt 6 -> 5
hypecommerce   - - - - - - +   14%   (non-commerce — see below)
   hypecommerce            2/2  + +
```

**一条豁免被换成了 2/2 的实测。**

**七步表里它仍是 14%（只有 `SubmitOrderAsync` 那一步），但那个数字现在带 `(non-commerce)` 标注**，
**而它真正的分数在下面那张表里 —— 满分。**

### 四、为什么这是进步

| 状态 | 读者看到的 |
|---|---|
| R797 的豁免 | 「这个模块不用看」 |
| R802 的 NonCommerce | **「这个模块有 2 步，两步都实现了」** |

**豁免是信息真空；测量是信息。** 同样一个模块，后者能被核。

### 五、验证

```
构建                已成功
ModuleCoverageTests exempt 5；hypecommerce 2/2（非结账表）
完整套件            1766 通过 / 0 失败 / 0 跳过
四项度量            4 / 0 / 17 / 78 / 0（未变）
```

### 六、仍然 Unknown

- **`raffle` / `pocketgames` / `riotgames` 的步骤名是谁定的**：**Unknown** —— 它们在那张表里，
  但**是不是逐条从镜像取证过，我没查**（这是下一步该查的）。
- **`hypecommerce` 的 `entries` 请求体**：**Unknown**。
- **`NonCommerce` 里还有没有别的模块该被这样核一遍**：**Unknown**。

### 七、这一轮的教训

**在加一条豁免之前，先确认没有别的尺子。**
**「豁免」和「另一套标准」看起来都是在处理同一件事，但一个抹掉信息、一个产生信息。**
**我这轮先选了抹掉，是被测试输出里一张自己没看过的表纠正的。**
"""

VERDICT = """

---

## 第 801–802 轮：仓库一直有两套尺子

### 我先做错了一件事

给 `raffle` 与 `pocketgames` 补了豁免。**跑完测试，输出里露出一张我从没看过的表：**

```
raffle        4/4  + + + +
pocketgames   6/6  + + + + + +
riotgames     7/7  + + + + + + +
```

**`NonCommerce` —— 每个非结账模块自带一组步骤名，单独评。三家在那套尺子上全是满分。**

**所以我的两条豁免多余。撤回了，`exempt` 回到 6。**

> **§2.7 又一次，我自己踩的：假设只有一套矩阵，看到七步得分低就当成缺口。**

### 那 `hypecommerce` 该被**测量**，不该被豁免

镜像给它两个端点（validate / create），**两个都有 builder —— 这是能量的。**

1. `SubmitOrderAsync` 拆成 **`ValidateEntryAsync`** + **`CreateEntryAsync`**
2. 注册进 `NonCommerce`
3. 从 `YardstickDoesNotApply` **撤掉**

### 结果

```
exempt 6 -> 5
hypecommerce   - - - - - - +   14%   (non-commerce — see below)
   hypecommerce            2/2  + +
```

**一条豁免换成了 2/2 的实测。**

### 为什么这是进步

| 状态 | 读者看到 |
|---|---|
| R797 的豁免 | 「这个模块不用看」 |
| R802 的 NonCommerce | **「它有 2 步，两步都实现」** |

> **豁免是信息真空；测量是信息。**

### 验证

```
构建绿 · exempt 5 · hypecommerce 2/2 · 整套 1766 / 0 · 度量未变
```

### 教训

**加豁免之前，先确认没有别的尺子。**
**「豁免」和「另一套标准」看着都在处理同一件事，但一个抹掉信息、一个产生信息。**
"""

BACKLOG_ADD = """

## 覆盖 — 两套尺子的区别（R801/R802）

**仓库有两套矩阵：`Required`（七步）与 `NonCommerce`（每模块自带步骤）。**

- 七步得分低 ≠ 缺口，**先看它在不在 `NonCommerce`**
- **已在 `NonCommerce` 且满分的，不要再加豁免**（R801 我犯过）

**本轮结果**：

```
exempt 6 -> 5
hypecommerce  -> NonCommerce，2/2（ValidateEntryAsync + CreateEntryAsync）
raffle 4/4 · pocketgames 6/6 · riotgames 7/7（都在非结账尺子上满分）
```

| 待查 | |
|---|---|
| `raffle`/`pocketgames`/`riotgames` 的步骤名是否逐条取证过 | **没查** —— 它们在表里，但来源未核 |
| `hypecommerce` 的 entries 请求体 | Unknown |
| `NonCommerce` 里其余模块是否也该这样核一遍 | Unknown |

**判据**：**豁免 = 信息真空；另一套尺子 = 信息。** 能后者就不前者。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R802", BLOCKER)
    ensure(RSTATUS, "R802", BLOCKER)
    ensure(RVERDICT, "第 801–802 轮", VERDICT)
    ensure(BACKLOG, "R801/R802", BACKLOG_ADD)

    ok = True
    for path, key in ((RBLOCK, "R802"), (RSTATUS, "R802"), (RVERDICT, "第 801–802 轮"), (BACKLOG, "R801/R802")):
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
         "R801/R802: the repository had a second yardstick all along, and hypecommerce moves onto it\n\n"
         "Probing raffle, pocketgames and riotgames showed none of them is a seven-step checkout, so I exempted the\n"
         "first two. Running the suite then printed a table I had never read: NonCommerce, where each non-commerce\n"
         "module carries its own step list and is scored against that instead. raffle was 4/4, pocketgames 6/6 and\n"
         "riotgames 7/7. The exemptions were therefore redundant, and both are reverted, taking exempt back to six.\n\n"
         "That is section 2.7 committed by me, against myself: I assumed one matrix existed, saw a low seven-step\n"
         "score, and read it as a gap rather than as a module being measured by the wrong ruler.\n\n"
         "hypecommerce is the opposite case and deserved different treatment. The image gives it two endpoints,\n"
         "entries/validate and entries/create, each with a builder, so it can be measured rather than excused.\n"
         "SubmitOrderAsync is split into ValidateEntryAsync and CreateEntryAsync, both registered in NonCommerce, and\n"
         "the exemption is removed. It now reports 2/2 on its own yardstick, and its 14% on the seven-step table\n"
         "carries the non-commerce annotation.\n\n"
         "The distinction worth keeping is that an exemption is a hole in the information and a second yardstick is\n"
         "information. The same module reads as 'do not look at this' under the first and 'two steps, both done' under\n"
         "the second.\n\n"
         "Unknown: whether the step names in NonCommerce were each evidenced from the image, which I have not checked;\n"
         "the entries request bodies; and whether other modules in that table deserve the same audit.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
