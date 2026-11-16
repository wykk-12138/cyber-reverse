"""Record R763/R764: the catalogue instrument fixed twice, and the rule it produced."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
AG = r"D:\projects\cyber-reverse\AGENTS.md"

BLOCKER = """

---

## 191. 目录清单仪器的三次修正；以及**给扫描器立了一条前置问题**

> R763/R764。改 `analysis/store_catalog.py`（两次）、`AGENTS.md`（新增 §2.7）。未改产品代码。

### 一、22 vs 62 的根因

`StoreModuleCatalog.CreateAll()` **多数条目是 `new FlowStoreModule(new XxxFlow(...))`** ——
**flow 被包成 module**。`store_catalog.py` 只数 `: StoreModuleBase` 子类，**flow 不是 module 子类，40 个不可见**。

**而 `DocsConsistencyTests` 的注释里早就写着「the script now reads only CreateAll()」** —— **仓库指明了做法，我没读。**

### 二、改成解析 `CreateAll()`

```
entries in CreateAll(): 62      ← 与 DocsConsistencyTests 的 catalogue 一致
distinct flow types: 32         ← 与 ParityDocTests 引用的 32 一致
domains claimed by more than one entry: 0
```

**两个交叉数字都对上，这是「可复算」的实际含义。**

### 三、修的过程中又犯两次同类错

| # | 我假设 | 实际 | 症状 |
|---|---|---|---|
| 1 | 字段只在 `: this(...)` 链里 | 也有 `base(...)` | 十几个条目 id 是 `?` |
| 2 | 花括号可按字符计数 | 字符串里的 `{`（JSON 模板/正则）打乱深度 | `ShopifyFlow` 报「class not found」 |

**第 2 条尤其坏**：`class_body` 走飞后返回 `None`，调用方把它翻译成「**class not found**」——
**那个诊断文案报错了因**，而这类类**只有无参条目才会走到**，十几个有内联参数的兄弟条目从不触发，于是活过了一轮。

现在 `class_body` 跳过字符串/字符/注释区域再来数括号。

### 四、给扫描器立了前置问题（`AGENTS.md` §2.7）

> **扫之前先问：这个东西在二进制/源码里有几种写法？**

六次都是同一件事 —— **先假设形状，再把「不符合假设」读成「不存在」**：

| 轮 | 假设 | 后果 |
|---|---|---|
| R753 | 标签形如 `"Startup Page"` | 假缺席 |
| R759 | module 字段形如 `=>` | `?` |
| R760 | 店名以显示名出现 | 7 个站误判可疑 |
| R762 | 只扫一类子类 | 22 vs 62 |
| R763 | 只认 `this(...)` | 十几个 `?` |
| R764 | 花括号按字符数 | 「class not found」 |

配套：**诊断文案要写对因**、**总数对了不等于每行都对**、**交叉验证**、**改文档也用锚点**。

### 五、而写这条规则的同一轮里，我用坏锚点把规则文件改坏了

搬动 §2.7 时用 `find('---')` 定区块边界，**撞上表头分隔线**，
结果：一段孤儿表格留在 §2 里、§2.7 的表头断成两行。**已修**（分两处精确 `edit`），
并把这件事本身作为第七条写进那张表 —— **不是我谦虚，是它最能说明问题。**

结构已核：标题序 0 → 1 → 2 → 2.5 → 2.7 → 3 → 4 → 5，无残留表格碎片，2.7 表体与四条配套都在。

### 六、验证

```
本轮未改产品代码
完整套件保持 1751 通过 / 0 失败（R762 时的值）
store_catalog.py 输出 62 / 32 / 0 冲突
```

### 七、仍然 Unknown

- `shopify` 那条的 `(none)` 域名是否就是原版行为：**Unknown** —— 猜是「按 host 识别、不绑固定域名」，未取证。
- 62 个条目里还有多少是「有 module 无实际 step 实现」：**Unknown** —— 那是判据 f 的下一层。
"""

VERDICT = """

---

## 第 763 轮：仪器修好了，而修的过程里我又犯两次

### 22 vs 62 的根因

`CreateAll()` 里多数是 **`FlowStoreModule(new XxxFlow(...))`** —— flow 被包成 module，
而 flow 不是 `StoreModuleBase` 子类，所以 40 个不可见。

**而 `DocsConsistencyTests` 的注释早写着「the script now reads only CreateAll()」。**

### 现在

```
entries in CreateAll(): 62      ← 与 DocsConsistencyTests 一致
distinct flow types: 32         ← 与 ParityDocTests 一致
domains claimed by >1 entry: 0
```

### 而修的过程里又犯两次

| # | 假设 | 实际 |
|---|---|---|
| 1 | 字段只在 `: this(...)` 链 | 也有 `base(...)` |
| 2 | 花括号按字符数 | 字符串里的 `{` 打乱深度 → 报「class not found」 |

**第 2 条最坏：诊断文案报错了因，而它只在无参条目上触发，所以活过了一轮。**

### 立了规

`AGENTS.md` §2.7：**扫之前先问：这个东西有几种写法？**
外加**诊断文案要写对因**、**总数对了不等于每行都对**、**交叉验证**、**改文档也用锚点**。

### 而写这条规则的同一轮，我用坏锚点把规则文件改坏了

`find('---')` 撞上表头分隔线 → 孤儿表格 + 断开的表头。**已修**，
并把这件事故意写进那张表当第七条。

### 验证

```
产品代码未改；套件 1751 / 0
```
"""


def main():
    for p, marker, text in ((P1, "R763", BLOCKER), (P3, "R763", BLOCKER), (P2, "第 763 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(AG, encoding="utf-8").read()
    old = "### 2.7 扫描器的前置问题（R764 立规，六次踩坑之后）"
    if "R764 立规" in body:
        print("  AGENTS.md already carries 2.7")
    else:
        print("  AGENTS.md: 2.7 heading missing")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R763/R764: the catalogue instrument fixed, and a rule for scanners that would have prevented all of it\n\n"
         "The 22-versus-62 gap came from reading classes that derive from StoreModuleBase while CreateAll() wraps most\n"
         "entries as FlowStoreModule(new XxxFlow(...)). The repo had already said what to do -- DocsConsistencyTests\n"
         "notes that the script reads only CreateAll() -- and I had not looked. The script now parses that initialiser\n"
         "and reports 62 entries and 32 distinct flow types, both agreeing with the two tests that independently\n"
         "count them.\n\n"
         "Fixing it reproduced the same mistake twice more. Some classes carry their identity through base(...) rather\n"
         "than a this(...) chain, so a dozen entries printed as '?'. And the brace walk counted braces inside string\n"
         "literals, so ShopifyFlow -- which holds a { in a template -- was reported as 'class not found' when it is\n"
         "right there. That second one is the worse failure: the diagnostic named the wrong cause, and because only\n"
         "parameterless entries reach that path, a dozen siblings with inline arguments never exercised it.\n\n"
         "AGENTS.md gains section 2.7, which asks the question before any scan: how many forms does this thing take?\n"
         "Six instances are listed, all of them the same shape -- assume a form, then read everything that fails the\n"
         "assumption as absence. Alongside it: name the right cause in diagnostics, a correct total does not mean\n"
         "every row is right, cross-check against a second independent count, and anchor document edits.\n\n"
         "That last rule is there because I broke AGENTS.md while writing it. Moving section 2.7 by finding the next\n"
         "'---' hit a table separator, leaving an orphaned table in section 2 and a truncated header in 2.7. Repaired,\n"
         "and the accident is now the seventh row of the table rather than a footnote.\n\n"
         "No product code changed; suite remains 1751 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
