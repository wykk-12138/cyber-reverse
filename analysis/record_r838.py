"""Record R838: PopNow is a nine-method subsystem, all twelve names absent from the replica."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

BLOCKER = """

---

## 262. **PopNow 是一套九方法子系统**，复刻件十二个名字全为 0 —— 而这是三轮里第三次低估

> R838。未改产品代码。

### 一、怎么找到的

R837 留下「三维同一个错、换了三个筛子」的判断。这一轮先按它做：**搜最具体的词。**

`StoreFlow` 的 4 处匹配里有 `<StartPopNowFlow>` —— **POP NOW 是 PopMart 的抽签功能**。
于是搜 `PopNow`：**29 处。**

### 二、这套子系统长什么样

从元数据串里读出来的方法名（`0x14337xxxx` 一带，async 状态机命名表）：

```
<StartSignupFlow>d__57   <StartClearFlow>d__58   <StartInStoreFlow>d__59   <StartPopNowFlow>d__60
<ExtractPopNow>d__83     <SelectPopNow>d__84     <SelectMultiPopNow>d__85  <AddToCartBox>d__86
<FetchTasks>d__187       <StartDailyCheckInTask>d__188
<StartPopNowViewTask>d__189   <FetchPopNowSpuIds>d__190   <ViewPopNow>d__191
```

**所以 PopNow 的流程是：取 SPU id → 抽取 → 选中（单个/多个）→ 加盒到车 → 查看，
外加两个任务：`StartPopNowViewTask`（看抽签）与 `StartDailyCheckInTask`（每日签到）。**

**而 `0x1433090f5` 单独一个 `PopNow` —— 像是一个模式/枚举值。**

**同族的还有 `StartSignupFlow`（注册）· `StartClearFlow` · `StartInStoreFlow`（门店）。**

### 三、复刻件一个都没有

```
PopNow 0 · ExtractPopNow 0 · SelectPopNow 0 · SelectMultiPopNow 0 · AddToCartBox 0
FetchPopNowSpuIds 0 · ViewPopNow 0 · StartPopNowViewTask 0 · StartDailyCheckInTask 0
StartSignupFlow 0 · StartClearFlow 0 · StartInStoreFlow 0
```

**十二个全为 0。**

### 四、三轮三次低估 —— 这才是这一轮真正的发现

| 轮 | 结论 | 下一轮被改成 |
|---|---|---|
| R830 | PopMart「四块未建模」 | R836：**七块** |
| R836 | PopMart 七块 | R838：**一整套九方法子系统 + 三个同族 flow** |
| R837 | 镜像内嵌 DotNetBrowser | （未推翻，但发现路径同样是「换了更具体的词才看见」） |

**每一次我用的词更具体，面就更大。** 这不是精度问题：

> **按词搜索永远给不出「完整清单」——它给的是「含这个词的那些」。
> 而我每次都在用「含这个词的那些」冒充完整清单。**

**判据 (f) 要求「原版站点与风控清单从二进制取证」。按词搜索不满足这个要求。**

**要给出完整清单，得换方法：**

1. **系统走一遍元数据串表，把「形如方法名的串」全部提取并分类**（不是搜关键词，是遍历后归类）
2. **或者走类型图（MethodTable → MethodDesc），枚举某个类的全部方法**

**这两条都不是搜词，本轮都没做。**

### 五、验证

```
ida.py str PopularNow?  不适用
ida.py str PopNow --limit 200   -> 29 matches（含 13 个方法名 + 1 个裸 PopNow）
ida.py str StoreFlow            -> 4 matches，全是 *Flow 后缀的另一类概念
ida.py str NikeFlow/ShopifyFlow/FlowBase -> 全 0（镜像没有按站命名的 Flow 类）
复刻件 grep 上面 12 个名字      -> 全 0
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **`<StartClearFlow>` 是什么**：**Unknown** —— 名字像「清空」（清购物车？清 cookie？），**未判。**
- **`<StartInStoreFlow>` 是什么**：**Unknown** —— 「门店」，可能是线上下单门店自提，**未判。**
- **`<StartDailyCheckInTask>` 是否只服务 PopMart**：**Unknown** —— 名字通用，**可能给所有站用。**
- **镜像的类清单**：**Unknown，且这是当前最关键的一个** ——
  **没有它，判据 (f) 只能靠搜词拼，而搜词已经三轮低估。**

### 七、教训

**「搜 `PopNow` 得 29 处」听起来像完整清单，其实只是「含 PopNow 的那些」。**
**要拿到「PopNow 子系统的全部方法」，得遍历该类的元数据，不是搜名字。**

**而我在三轮里，三次把「含某个词的串」当成「完整的清单」，每次被下一轮推翻。**
**这次不改判据，下一轮还会犯。**
"""

VERDICT = """

---

## 第 838 轮：PopNow 是九方法子系统，复刻件十二个名字全为 0

### 怎么找到的

`StoreFlow` 的 4 处匹配里有 `<StartPopNowFlow>` —— **POP NOW 是 PopMart 的抽签功能**。搜 `PopNow`：**29 处**。

### 子系统形状

```
<StartPopNowFlow>d__60        <FetchPopNowSpuIds>d__190
<ExtractPopNow>d__83          <ViewPopNow>d__191
<SelectPopNow>d__84           <StartPopNowViewTask>d__189
<SelectMultiPopNow>d__85      <StartDailyCheckInTask>d__188
<AddToCartBox>d__86
```

**流程：取 SPU id → 抽取 → 选中（单/多）→ 加盒到车 → 查看；另加两个任务（看抽签、每日签到）。**
**同族还有 `StartSignupFlow`（注册）· `StartClearFlow` · `StartInStoreFlow`（门店）。**

### 复刻件：十二个全 0

### 三轮三次低估 —— 这才是真正的发现

| 轮 | 结论 | 下一轮 |
|---|---|---|
| R830 | 四块 | R836：**七块** |
| R836 | 七块 | R838：**九方法子系统 + 三个同族 flow** |

> **按词搜索永远给不出完整清单 —— 它给的是「含这个词的那些」。而我三次都在用后者冒充前者。**
> **判据 (f) 要「从二进制取证清单」，按词搜索不满足这个要求。**

**要完整清单得换方法**：① 遍历元数据串表后归类，而非搜关键词；② 走类型图枚举某类全部方法。**两条都不是搜词，本轮都没做。**

### 仍然 Unknown

**`StartClearFlow` 是什么**（清购物车？清 cookie？）· **`StartInStoreFlow` 是什么**（门店自提？）·
**`StartDailyCheckInTask` 是否只服务 PopMart** · **镜像的类清单 —— 当前最关键的一条，缺它判据 (f) 只能靠搜词拼，而搜词已三轮低估。**

### 验证

```
str PopNow → 29（13 方法名 + 1 裸 PopNow）· str NikeFlow/ShopifyFlow/FlowBase → 全 0
复刻件 12 个名字 → 全 0 · 产品代码未改
```
"""

BACKLOG_ADD = """

## 优先级 ① — PopNow 子系统（R838，已枚举）

| 方法名 | 镜像 | 复刻件 |
|---|---|---|
| `StartPopNowFlow` · `FetchPopNowSpuIds` · `ExtractPopNow` · `SelectPopNow` · `SelectMultiPopNow` · `AddToCartBox` · `ViewPopNow` | 有（`0x14337xxxx`） | **全 0** |
| `StartPopNowViewTask` · `StartDailyCheckInTask` | 有 | **全 0** |
| `StartSignupFlow` · `StartClearFlow` · `StartInStoreFlow` | 有 | **全 0** |

**流程形状**：取 SPU id → 抽取 → 选中（单/多）→ 加盒到车 → 查看，外加两个任务。

**另：`NikeFlow` / `ShopifyFlow` / `FlowBase` 在镜像里全 0** —— 复刻件按站命名的 Flow 类是自己起的（goal 允许）。

### 三轮三次低估

| 轮 | 结论 | 被改成 |
|---|---|---|
| R830 | 四块 | R836：七块 |
| R836 | 七块 | R838：九方法子系统 + 三同族 flow |

> **按词搜索给的是「含这个词的那些」，不是完整清单。三轮都拿后者当前者。**
> **判据 (f) 要「从二进制取证清单」—— 得遍历元数据后归类，或走类型图枚举，都不是搜词。**

| 仍 Unknown | |
|---|---|
| `StartClearFlow` | 清购物车？清 cookie？ |
| `StartInStoreFlow` | 门店自提？ |
| `StartDailyCheckInTask` 是否通用 | 名字通用，可能所有站都用 |
| **镜像的类清单** | **最关键 —— 缺它 (f) 只能靠搜词拼** |
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R838", BLOCKER)
    ensure(RSTATUS, "R838", BLOCKER)
    ensure(RVERDICT, "第 838 轮", VERDICT)
    ensure(BACKLOG, "R838", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R838" not in h:
        h += ("\n## R838 补充 — PopNow 子系统\n\n"
              "`PopNow` 29 处，读出 13 个方法名：`StartPopNowFlow` / `FetchPopNowSpuIds` / `ExtractPopNow` / "
              "`SelectPopNow` / `SelectMultiPopNow` / `AddToCartBox` / `ViewPopNow` / `StartPopNowViewTask` / "
              "`StartDailyCheckInTask` + `StartSignupFlow` / `StartClearFlow` / `StartInStoreFlow`。\n"
              "**复刻件十二个名字全为 0。** 另：`NikeFlow`/`ShopifyFlow`/`FlowBase` 镜像全 0（复刻件命名自起）。\n"
              "**三轮三次低估（四→七→九方法子系统）** —— 按词搜索给的是「含这个词的那些」，不是完整清单。\n"
              "**判据 (f) 要完整清单：得遍历元数据后归类，或走类型图枚举某类全部方法。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R838"), (RSTATUS, "R838"), (RVERDICT, "第 838 轮"), (BACKLOG, "R838")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R838: PopNow is a nine-method subsystem and all twelve of its names are absent\n\n"
         "R837 concluded that three rounds had made the same mistake with three different filters, and the first thing"
         " this round did was search the most specific word available. StoreFlow's four matches included"
         " StartPopNowFlow -- POP NOW being PopMart's draw -- and searching PopNow returns twenty-nine.\n\n"
         "The metadata names a coherent pipeline: FetchPopNowSpuIds, ExtractPopNow, SelectPopNow, SelectMultiPopNow,"
         " AddToCartBox, ViewPopNow, with StartPopNowFlow starting it and two tasks alongside, StartPopNowViewTask and"
         " StartDailyCheckInTask. A bare PopNow string at 0x1433090f5 looks like a mode value. Related flows carry"
         " StartSignupFlow for registration, StartClearFlow and StartInStoreFlow.\n\n"
         "All twelve names are absent from the replica.\n\n"
         "The finding that matters more than the gap is that this is the third consecutive underestimate. R830 said four"
         " surfaces, R836 corrected it to seven, and now the same site turns out to have a nine-method subsystem plus"
         " three related flows. Each time the search word was more specific and the picture grew, which means the"
         " method itself is the problem: a word search returns the strings containing that word, and I have been"
         " presenting that set as a complete inventory for three rounds.\n\n"
         "Criterion (f) asks for a store and vendor list taken from the binary. A word search does not satisfy that."
         " Producing a complete inventory needs either a walk of the metadata string table followed by classification,"
         " or a type-graph walk that enumerates every method of a class. Neither is a search, and neither was done.\n\n"
         "A side finding: NikeFlow, ShopifyFlow and FlowBase all return nothing, so the image does not name per-store"
         " flow classes that way. The replica's naming is its own, which the goal permits.\n\n"
         "Unknown: what StartClearFlow clears, whether a cart or a session; what StartInStoreFlow means, possibly"
         " buy-online-collect-in-store; whether StartDailyCheckInTask is PopMart-specific given its generic name; and"
         " the image's class inventory, which is now the most valuable single unknown, because without it criterion (f)"
         " can only be assembled by word searches that have been wrong three times.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
