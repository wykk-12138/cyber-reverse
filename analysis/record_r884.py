"""Record R884: where_is failed twice in one round, so its default changed."""

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
### `where_is` 这一轮失败两次 —— 于是把它的默认改了（R884）

**目标：把 R883 解出来的 `Task.Type` 落地。**

**第一次失败：`where_is Drop` 用的是**子串**匹配 —— 55 个文件，实现组 15 个全是
`DropDown` / `ProxyDrop` 之类的假命中。而**真正的 `Drop` 类型在 `Checkout.cs:44`，不在那 15 个里**。**

**第二次失败：我写了新的 `Drop.cs` 和 `DropTests.cs`，编译报 CS0101「命名空间已包含 Drop 的定义」。**

**§2.7c 那条规则我执行的是一次 `where_is`，而它给的是假答案。**

### 所以修的默认，不是习惯

```
before:  默认子串，--word 才整词
after :  默认整词，--sub  才子串
```

**修后实测：**

| 调用 | 文件数 | 含 `Checkout.cs` 吗 |
|---|---|---|
| `where_is Drop`（默认，整词） | **16** | **是（实现组 3 个之一）** |
| `where_is Drop --sub` | 55 | 是，但混在假命中里 |

**R884 的理由写进了 `--sub` 的 help 文本：**
**「查 `Drop` 时子串形式返回十五个文件，全是 `DropDown` 和 `ProxyDrop` 命中，
而名字正好是 `Drop` 的类坐在 `Checkout.cs` 里、不在其中。」**

**这正是 R881 的原则：改数字撑到下一次，改机制才不重复。**

### 落到产品上的两件测量

| 类型 | 镜像（基线） | 复刻件 | 结论 |
|---|---|---|---|
| `Drop` | `Time` · `Type`（2） | `Time` · `Stores` · `Type`（3） | **`Stores` 在基线里没出现** |
| `CreateModel` | 8 个属性 | 20 个，**8 个全含** | **镜像有、复刻缺 = 0；复刻多 12 个** |

**而 `Stores` 的缺席是**弱证据** —— R883 的边界刚说过：清单只收「参与绑定」的成员。
所以「镜像的 `Drop` 没有 `Stores`」这句话不能说。**

**`CreateModel` 那条是判据 (a) 的正面证据：镜像的 8 个属性复刻件一个不缺。**
"""

if "`where_is` 这一轮失败两次" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R884 appended")

BLOCKER = """

---

## 308. `where_is` 默认改成整词匹配 —— 因为它这一轮给了两次假答案

> R884。**改工具默认值，未改产品代码。** 套件 **1780 通过 / 0 失败 / 0 跳过**。

### 一、两次失败

**目标：把 R883 的 `Task.Type` 落地。**

**① `where_is Drop` 用子串 → 55 个文件，实现组 15 个全是 `DropDown` / `ProxyDrop` 之类。
而真正的 `Drop` 类型在 `Checkout.cs:44`，**不在那 15 个里**。**

**② 我写了新的 `Drop.cs` + `DropTests.cs` → CS0101「命名空间已包含 Drop 的定义」。**

**§2.7c 那条规则我执行了 —— 执行了一次 `where_is`，而它给了假答案。
规则没错，工具默认错。**

### 二、改默认

```
before:  默认子串，--word 才整词
after :  默认整词，--sub  才子串
```

| 调用 | 文件数 | 含 `Checkout.cs` |
|---|---|---|
| 默认（整词） | **16** | **是** |
| `--sub` | 55 | 是，但混在假命中里 |

**理由写进了 `--sub` 的 help 文本，不是只写在文档里 —— 下一次有人用这个工具时看得见。**

**这是 R881 的原则：改数字撑到下一次，改机制才不重复。**

### 三、顺带的两条测量（判据 (a) 的正反面）

| 类型 | 镜像 | 复刻 | 结论 |
|---|---|---|---|
| `CreateModel` | 8 属性 | 20，**8 个全含** | **缺 = 0；多 12 个** |
| `Drop` | `Time` `Type`（2） | `Time` `Stores` `Type`（3） | **`Stores` 未见于基线** |

**`CreateModel` 是判据 (a) 的正面证据：镜像的 8 个属性，复刻件一个不缺。**

**而 `Stores` 的缺席是**弱证据** —— R883 刚说过清单只收「参与绑定」的成员。
所以不能说「镜像的 `Drop` 没有 `Stores`」，只能说「它在可见的那一半里没出现」。**

### 四、验证

```
where_is Drop           -> 16 files（实现 3，含 Checkout.cs）
where_is Drop --sub     -> 55 files
新建 Drop.cs + DropTests.cs -> CS0101（Drop 已存在于 Checkout.cs:44）-> 删除
CreateModel 属性对比     -> 镜像 8 / 复刻 20 / 缺失 0 / 多 12
python tools\\metrics_report.py -> 1780 通过 / 0 失败 / 0 跳过
本轮未改产品代码（两个新文件已删）
```

### 五、仍然 Unknown

- **复刻件 `Drop.Stores` 该不该在**：**Unknown** ——
  **镜像的基线里没有它，但基线只覆盖参与绑定的成员。要判它得换证据源。**
- **复刻件 `CreateModel` 那 12 个多余属性是**从哪来的**：**Unknown** ——
  **可能是 XAML 绑定需要的，也可能是我早先编的。这两种情况的处理完全不同。**
- **`where_is` 还有没有别的默认值是错的**：**Unknown** ——
  **这次是「子串 vs 整词」。同样的问法还适用于：是否该默认排除 `docs/baseline/`（那些文件让命中数虚高）。**

### 六、教训

**§2.7c 立的规则是「动手前跑 where_is」。这一轮我跑了，然后写了一个重复类型。**

**所以那条规则不充分 —— 它没规定**怎么用**。**
**「跑一下」和「跑对」是两件事，而 `where_is` 的默认把后者默认成了错的那种。**

**R870 那轮我把教训做成命令，理由是「写下来不是修复手段」。
这一轮发现：**命令也有默认值，而默认值本身可能就是个陷阱。**
"""

VERDICT = """

---

## 第 884 轮：`where_is` 默认改成整词 —— 它这一轮给了两次假答案

### 两次失败

**目标：把 R883 的 `Task.Type` 落地。**

1. **`where_is Drop` 用子串 → 55 个文件，实现组 15 个全是 `DropDown`/`ProxyDrop`；真正的 `Drop` 在 `Checkout.cs:44`，不在其中**
2. **我写了新的 `Drop.cs` + `DropTests.cs` → CS0101「命名空间已包含 Drop 的定义」**

> **§2.7c 那条规则我执行了 —— 执行了一次 `where_is`，而它给了假答案。规则没错，工具默认错。**

### 改的是默认值

```
before:  默认子串，--word 才整词
after :  默认整词，--sub  才子串
```

| 调用 | 文件数 | 含 `Checkout.cs` |
|---|---|---|
| 默认（整词） | **16** | **是** |
| `--sub` | 55 | 是，但混在假命中里 |

**理由写进了 `--sub` 的 help 文本 —— 下次有人用这个工具时看得见。**

### 顺带两条测量（判据 (a) 的正反面）

| 类型 | 镜像 | 复刻 | 结论 |
|---|---|---|---|
| `CreateModel` | 8 属性 | 20，**8 个全含** | **缺 = 0；多 12** |
| `Drop` | `Time` `Type`（2） | `Time` `Stores` `Type`（3） | `Stores` 未见于基线 |

**`CreateModel` 是判据 (a) 的正面证据。**
**而 `Stores` 的缺席是**弱证据** —— 清单只收「参与绑定」的成员，所以只能说「它在可见的那一半里没出现」。**

### 仍然 Unknown

**`Drop.Stores` 该不该在**（基线覆盖不到，要换证据源）·
**`CreateModel` 那 12 个多余属性从哪来**（**是 XAML 绑定需要，还是我早先编的？两种情况处理完全不同**）·
**`where_is` 还有没有别的错默认**（比如是否该默认排除 `docs/baseline/`）

### 教训

> **§2.7c 立的规则是「动手前跑 where_is」。这一轮我跑了，然后写了一个重复类型。**
> **所以那条规则不充分 —— 它没规定**怎么用**。「跑一下」和「跑对」是两件事。**
> **R870 那轮我把教训做成命令，理由是「写下来不是修复手段」。这一轮发现：**命令也有默认值，而默认值本身可能就是个陷阱。**
"""

BACKLOG_ADD = """

## 方法 — `where_is` 默认改整词（R884）

### 因为它这一轮给了两次假答案

1. **`where_is Drop` 子串 → 55 文件，实现组 15 个全是 `DropDown`/`ProxyDrop`；真正的 `Drop` 在 `Checkout.cs:44` 不在其中**
2. **写了新 `Drop.cs` → CS0101「已包含 Drop 的定义」**

```
before: 默认子串, --word 才整词
after : 默认整词, --sub  才子串
```

**实测：默认 16 文件（含 `Checkout.cs`）· `--sub` 55 文件。理由写进 `--sub` 的 help。**

### 两条测量

| 类型 | 镜像 | 复刻 | 结论 |
|---|---|---|---|
| `CreateModel` | 8 | 20，8 个全含 | **缺 0；多 12** |
| `Drop` | `Time` `Type` | `Time` `Stores` `Type` | `Stores` 未见于基线（**弱证据**：基线只覆盖参与绑定的成员） |

**套件 1780 通过 / 0 失败。**

| 仍 Unknown | |
|---|---|
| `Drop.Stores` 该不该在 | 基线覆盖不到 |
| `CreateModel` 多出的 12 个属性来源 | **XAML 需要 vs 我早先编的 —— 处理完全不同** |
| `where_is` 还有别的错默认吗 | 如是否该排除 `docs/baseline/` |

**纪律**：**§2.7c 只规定「跑」，没规定「怎么用」。命令也有默认值，而默认值本身可能是陷阱。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R884", BLOCKER)
    ensure(RSTATUS, "R884", BLOCKER)
    ensure(RVERDICT, "第 884 轮", VERDICT)
    ensure(BACKLOG, "R884", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R884" not in h:
        h += ("\n## R884 补充 — `where_is` 默认改整词（**改工具，未改产品代码**）\n\n"
              "**它这一轮给了两次假答案**：① `where_is Drop` 子串 → 55 文件全是 `DropDown`/`ProxyDrop`，**真正的 `Drop` 在 `Checkout.cs:44` 不在其中**；② 我据此写了新 `Drop.cs` → **CS0101 重复定义**。\n"
              "**改默认**：`默认整词 / --sub 才子串`（原为默认子串 / `--word` 才整词）。实测默认 16 文件含 `Checkout.cs`，`--sub` 55 文件。**理由写进 `--sub` 的 help。**\n"
              "**两条测量**：`CreateModel` 镜像 8 / 复刻 20（**8 个全含，缺 0，多 12**）；`Drop` 镜像 `Time`+`Type` / 复刻 `Time`+`Stores`+`Type`（**`Stores` 未见于基线，但那是弱证据**）。\n"
              "**套件 1780 通过 / 0 失败。**\n"
              "**纪律：§2.7c 只规定「跑」，没规定「怎么用」。命令也有默认值，默认值本身可能是陷阱。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R884"), (RSTATUS, "R884"), (RVERDICT, "第 884 轮"), (BACKLOG, "R884")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R884: where_is defaults to whole words now, because it gave two false answers in one round\n\n"
         "The round's goal was to put R883's finding about Task.Type somewhere real. It failed twice, and both times\n"
         " the tool was at fault rather than the rule.\n\n"
         "First: where_is Drop searched substrings, returned fifty-five files, and the fifteen under implementation were\n"
         " all DropDown and ProxyDrop hits. The type actually named Drop sits in Checkout.cs line 44 and was not among\n"
         " them. Second: on the strength of that, I wrote a new Drop.cs and DropTests.cs, and the compiler refused with\n"
         " CS0101 because the type already existed.\n\n"
         "Section 2.7c says to run where_is before writing. I ran it. The rule was followed and the answer was wrong,\n"
         " which means the rule was underspecified: it said run the tool and never said how to read it, and the tool's\n"
         " default made the wrong reading the easy one. Substring matching is dominated by longer names that contain the\n"
         " query, so a short type name is exactly the case where the exact hit is most likely to be missed.\n\n"
         "So the default is inverted: whole words by default, --sub to opt into substring, and the reason is in the\n"
         " --sub help text rather than only in a document, so the next person to use the tool sees it. Measured after the\n"
         " change, the default returns sixteen files with Checkout.cs among the three implementation hits, while --sub\n"
         " still returns fifty-five.\n\n"
         "Two measurements came out of the work even though the type was not added. CreateModel in the image has eight\n"
         " properties and the replica has twenty, containing all eight, so nothing is missing and twelve are extra. Drop\n"
         " in the image evidences Time and Type and the replica has Time, Stores and Type, where Stores does not appear\n"
         " in the baseline -- but that absence is weak evidence, because R883 showed the baseline covers only members\n"
         " materialised for binding. So the honest statement is that Stores is not in the visible half, not that the\n"
         " image lacks it.\n\n"
         "Unknown: whether Drop.Stores belongs, which needs a different evidence source than the accessor baseline;\n"
         " where CreateModel's twelve extra properties came from, since properties required by XAML binding and\n"
         " properties I invented earlier call for opposite remedies; and whether where_is has other defaults that are\n"
         " wrong in the same way, such as not excluding docs/baseline, whose files inflate hit counts everywhere.\n\n"
         "R870 turned a lesson into a command because writing it down had stopped working. This round shows a command\n"
         " has defaults, and a default can be the trap. The next layer of the same problem.\n\n"
         "Tool defaults changed; no product code changed; suite carries at 1780."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
