"""Record R874: where uniqCode comes from is not name-discoverable, and why that is the answer."""

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
### `uniqCode` 是**模型字段**，不是产生者 —— 而「谁填它」静态查不到（R874）

**镜像里带 `uniqCode` 的串只有 5 条，全列出来了：**

| 地址 | 串 | 性质 |
|---|---|---|
| `0x1433803a5` | `_uniqCode` | **属性后备字段**（下划线前缀） |
| `0x146fda6d4` | `currentUniqCode` | 属性名 |
| `0x1471647ac` | `storeUniqCode` | 属性名 |
| `0x146a85e4c` | `&storeUniqCode=1` | 查询串片段（拼在某个 URL 后） |
| `0x146ab82f4` | `/shop/v1/drawScratch/detail?uniqCode=` | 端点 |

**三条是字段名，一条是端点，一条是查询片段。**没有一条是「产生它的那一步」。**

### 所以答案不是「没找到」，是「这个名字层问不出来」

**「谁把值填进 `_uniqCode`」是 setter 的行为。而 R504 已证：**

> 属性 setter 做什么 —— **编译期内联，没有独立函数体**

**所以这条路和 R504 的 B 桶 31 条撞上的是同一堵墙。**

**区别在于：B 桶是 UI 属性，本轮是模型属性 —— 墙一样，作用域一样（都是属性写入）。**

### 这一条把 R873 那个 Unknown 从「未查」变成「查了，原因是 X」

| R873 写的 | 现在 |
|---|---|
| 「`uniqCode`/`uniqID` 从哪来 —— Unknown」 | **Unknown，原因：它是属性写入，静态拿不到；名字层只有字段名** |

**这比「未查」有用：下一轮不该再花时间在同一层搜名字，要搜就得换层（运行期，需凭据）。**

### 三条可走的路，代价不同

| 路 | 代价 | 能拿到什么 |
|---|---|---|
| 继续在字符串池搜别的名字 | 便宜，但**名字层已到顶** | 大概什么也拿不到 |
| 从 `&storeUniqCode=1` 反推它在哪个 URL 后面 | 中 | **可能拿到「哪个页面/接口会带它」** —— 这还没试 |
| 运行期观察 | **需登录凭据** | 真值 |

**第二条是唯一还没试的静态路，而它有具体形态：`&storeUniqCode=1` 后面一定跟着某个 URL 或路径串。**
**本轮没查 —— 那是下一轮第一件事。**
"""

if "`uniqCode` 是**模型字段**，不是产生者" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R874 appended")

BLOCKER = """

---

## 298. `uniqCode` 的产者：**名字层已到顶**，而有一条还没试的静态路

> R874。未改产品代码。

### 一、把 5 条全列出来，答案就清楚了

| 地址 | 串 | 性质 |
|---|---|---|
| `0x1433803a5` | `_uniqCode` | **属性后备字段** |
| `0x146fda6d4` | `currentUniqCode` | 属性名 |
| `0x1471647ac` | `storeUniqCode` | 属性名 |
| `0x146a85e4c` | `&storeUniqCode=1` | 查询片段 |
| `0x146ab82f4` | `/shop/v1/drawScratch/detail?uniqCode=` | 端点 |

**三条字段名、一条端点、一条查询片段。没有一条是「产生它的那一步」。**

### 二、而这不是「没找到」，是「这个名字层问不出来」

**「谁填 `_uniqCode`」是 setter 行为。R504 已经证过：**

> 属性 setter 做什么 —— **编译期内联，没有独立函数体**

**所以这条路和 R504 那 31 条撞的是同一堵墙。区别只是那边是 UI 属性、这边是模型属性 ——
**墙一样，作用域一样（都是属性写入）。**

**这条值得单独写：R504 的结论我前面几轮一直当成「只挡 UI」（R863 收紧过一次）。
这一轮说明它挡的是**所有属性写入**，与是不是 UI 无关。**

### 三、R873 那个 Unknown 现在有了原因

| R873 | R874 |
|---|---|
| 「`uniqCode`/`uniqID` 从哪来 —— Unknown」 | **Unknown，原因：属性写入，静态拿不到；名字层只有字段名** |

**「未查」和「查了，原因是 X」是两句话。前者会被下一轮再查一遍；后者把下一轮引到别的层。**

### 四、还有一条静态路没试，而且它有具体形态

**`&storeUniqCode=1` 这个片段**一定拼在某个 URL 或路径串后面。
**找到它拼在谁后面，就知道「哪个页面会带这个参数」—— 那离产者就更近一步。**

**本轮没查，理由是这一步我要留着下一轮开头做（本轮先把这个边界写清）。**

| 路 | 代价 | 能拿到 |
|---|---|---|
| 继续搜名字 | 便宜，**已到顶** | 大概什么都没有 |
| **从 `&storeUniqCode=1` 反推宿主 URL** | **中** | **「哪个页面/接口带它」** |
| 运行期观察 | **需凭据** | 真值 |

### 五、验证

```
ida.py str storeUniqCode -> 2 matches（&storeUniqCode=1 · storeUniqCode）
ida.py str uniqCode      -> 5 matches（_uniqCode · &storeUniqCode=1 · 端点 · currentUniqCode · storeUniqCode）
三条字段名 + 一条端点 + 一条查询片段；无「产者」形态的串
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **`_uniqCode` 的写入点**：**Unknown，原因见二** —— 属性写入，静态拿不到。
- **`&storeUniqCode=1` 拼在哪个 URL 后**：**Unknown —— 下一轮第一件事，这是唯一还没试的静态路。**
- **`currentUniqCode` 与 `storeUniqCode` 是不是两个不同的东西**：**Unknown** ——
  名字像「当前的」与「店的」，**但可能只是同一属性的两种叫法。**

### 七、教训

**我上一轮把这条写成「最挡路的一条 Unknown」，好像它会一直挡着。
这一轮查完发现它的性质变了：不是**

**wait — 不是「还没查」，而是「在这个层查不出来」。**

**差别在于下一步该做什么。前者让人再搜一遍名字；后者把人引向「反推宿主 URL」或「运行期」。**

**所以一个 Unknown 写下来时，最好同时写清它属于哪一层 —— 名字层、结构层、还是行为层。
这次的教训是：我写在「名字层」，而它其实在「行为层」。**
"""

VERDICT = """

---

## 第 874 轮：`uniqCode` 的产者 —— 名字层已到顶

### 5 条全列出来，答案就清楚了

| 地址 | 串 | 性质 |
|---|---|---|
| `0x1433803a5` | `_uniqCode` | **属性后备字段** |
| `0x146fda6d4` | `currentUniqCode` | 属性名 |
| `0x1471647ac` | `storeUniqCode` | 属性名 |
| `0x146a85e4c` | `&storeUniqCode=1` | 查询片段 |
| `0x146ab82f4` | `/shop/v1/drawScratch/detail?uniqCode=` | 端点 |

**没有一条是「产生它的那一步」。**

### 这不是「没找到」，是「这个名字层问不出来」

**「谁填 `_uniqCode`」是 setter 行为，而 R504 已证 setter 编译期内联、没有独立函数体。**

> **所以它和 R504 那 31 条撞的是同一堵墙。而这一轮说明：那堵墙挡的是**所有属性写入**，与是不是 UI 无关。
> R863 我把 R504 收紧成「只挡 UI」——收得太窄了。**

### R873 那条 Unknown 现在有了原因

| R873 | R874 |
|---|---|
| 「从哪来 —— Unknown」 | **Unknown，原因：属性写入静态拿不到；名字层只有字段名** |

**「未查」会被下一轮再查一遍；「查了，原因是 X」把下一轮引到别的层。**

### 还有一条静态路没试，而且形态具体

**`&storeUniqCode=1` 一定拼在某个 URL 或路径串后面 —— 找到它拼在谁后面，就知道「哪个页面会带这个参数」。**

| 路 | 代价 | 能拿到 |
|---|---|---|
| 继续搜名字 | 便宜，**已到顶** | 大概什么都没有 |
| **从 `&storeUniqCode=1` 反推宿主 URL** | **中** | **「哪个页面带它」** |
| 运行期观察 | **需凭据** | 真值 |

**本轮没做 —— 留着下一轮开头，这是唯一还没试的静态路。**

### 仍然 Unknown

**`_uniqCode` 写入点**（属性写入，静态拿不到）· **`&storeUniqCode=1` 拼在哪个 URL 后**（**下一轮第一件事**）·
**`currentUniqCode` 与 `storeUniqCode` 是否同一属性的两种叫法**

### 教训

> **我上一轮把它写成「最挡路的一条 Unknown」，好像它会一直挡着。这一轮查完，它的性质变了：**
> **不是「还没查」，而是「在这个层查不出来」。**
> **差别在于下一步做什么：前者让人再搜一遍名字；后者把人引向「反推宿主 URL」或「运行期」。**
> **所以写 Unknown 时最好同时写清它属于哪一层 —— 名字层、结构层、还是行为层。这次我写在「名字层」，而它其实在「行为层」。**
"""

BACKLOG_ADD = """

## 判据 — `uniqCode` 产者：名字层已到顶（R874）

**镜像里带 `uniqCode` 的串只有 5 条，全列出：**

| 地址 | 串 | 性质 |
|---|---|---|
| `0x1433803a5` | `_uniqCode` | 属性后备字段 |
| `0x146fda6d4` | `currentUniqCode` | 属性名 |
| `0x1471647ac` | `storeUniqCode` | 属性名 |
| `0x146a85e4c` | `&storeUniqCode=1` | 查询片段 |
| `0x146ab82f4` | `/shop/v1/drawScratch/detail?uniqCode=` | 端点 |

**无「产者」形态的串。**

### 结论：不是「没找到」，是「名字层问不出来」

**「谁填 `_uniqCode`」= setter 行为；R504 已证 setter 内联、无独立函数体。**
**→ 与 R504 那 31 条同一堵墙。而**这堵墙挡所有属性写入，与 UI 无关** —— R863 的「只挡 UI」收得太窄。**

### 还有一条静态路

**`&storeUniqCode=1` 拼在某个 URL 后 → 找到宿主就知道「哪个页面带它」。本轮未做，下一轮第一件事。**

| 路 | 代价 | 能拿到 |
|---|---|---|
| 继续搜名字 | 便宜，**已到顶** | 大概没有 |
| **反推 `&storeUniqCode=1` 宿主** | 中 | **哪个页面带它** |
| 运行期 | **需凭据** | 真值 |

| 仍 Unknown | |
|---|---|
| `_uniqCode` 写入点 | 属性写入，静态拿不到 |
| `&storeUniqCode=1` 宿主 URL | **下一轮第一件事** |
| `currentUniqCode` vs `storeUniqCode` | 可能同一属性两种叫法 |

**纪律**：**写 Unknown 要写清它属于哪一层（名字/结构/行为）—— 这次我写在名字层，它其实在行为层。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R874", BLOCKER)
    ensure(RSTATUS, "R874", BLOCKER)
    ensure(RVERDICT, "第 874 轮", VERDICT)
    ensure(BACKLOG, "R874", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R874" not in h:
        h += ("\n## R874 补充 — `uniqCode` 产者：名字层已到顶\n\n"
              "**5 条全列**：`_uniqCode`(字段) · `currentUniqCode` · `storeUniqCode`(属性名) · `&storeUniqCode=1`(查询片段) · `/shop/v1/drawScratch/detail?uniqCode=`(端点)。**无产者形态。**\n"
              "**→ 不是「没找到」，是「名字层问不出来」：写入是 setter 行为，R504 已证内联。**\n"
              "**而这条修正 R863**：R504 那堵墙挡的是**所有属性写入**，与 UI 无关；我说「只挡 UI」收得太窄。\n"
              "**还没试的静态路：从 `&storeUniqCode=1` 反推宿主 URL → 哪个页面带这个参数。下一轮第一件事。**\n"
              "**纪律：写 Unknown 要写清层次（名字/结构/行为）。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R874"), (RSTATUS, "R874"), (RVERDICT, "第 874 轮"), (BACKLOG, "R874")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R874: where uniqCode comes from is a behaviour-layer question, not a naming one\n\n"
         "R873 called the origin of uniqCode and uniqID the most obstructive open item, since three written steps cannot"
         " run without them. Listing every string containing uniqCode settles what kind of question it is. There are"
         " five: a backing field _uniqCode, two property names currentUniqCode and storeUniqCode, a query fragment"
         " &storeUniqCode=1, and the detail endpoint. Three field names, one endpoint, one fragment. Nothing shaped like"
         " the step that produces a value.\n\n"
         "That is not a failure to find it. Filling _uniqCode is setter behaviour, and R504 established that setters are"
         " inlined and have no body of their own. So this sits behind the same wall as those thirty-one UI members --\n"
         " except that this round shows the wall covers every property write, not only UI ones. R863 narrowed R504 to\n"
         " covering UI members only, and that narrowing was too tight. The wall is about properties, wherever they live.\n\n"
         "So the open item changes character. Unchecked would have meant looking again next round; checked-with-a-reason\n"
         " points somewhere else. One static route remains untried and it has a concrete shape: &storeUniqCode=1 must be\n"
         " appended to some URL, and finding what it is appended to would show which page carries the parameter, which\n"
         " is one step nearer the producer. That is next round's opening move. Beyond it there is only runtime\n"
         " observation, which needs credentials.\n\n"
         "Unknown: the write site for _uniqCode, unavailable statically for the reason above; what &storeUniqCode=1 is\n"
         " appended to; and whether currentUniqCode and storeUniqCode name one property twice or two different things,\n"
         " since the words suggest current and store while the two may be the same field.\n\n"
         "The lesson is about labelling an unknown with its layer. I recorded this one as a naming question when it is a\n"
         " behaviour question, and the label decides what the next round does: a naming unknown sends me back to search\n"
         " strings, a behaviour unknown sends me to structure or runtime. Both are honest; only one is useful.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
