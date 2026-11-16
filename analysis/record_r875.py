"""Record R875: the fragment is a table entry with a fixed value, not part of one URL."""

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
### `&storeUniqCode=1` 是**查询片段表里的一条**，不是某个 URL 的拼接（R875）

**R874 说「找到它拼在谁后面，就知道哪个页面带它」。查了那一段（`0x146a85000`–`0x146a8C000`）：

**`335` 条，按字母序排列，全是查询片段：**

```
&paypal_client_cfci=   &pid=        &pl=5        &plannedCartLines=   &pm=no
&provider=             &quantity=   &quantity=1  &redirect_uri=       &referer=
&response_type=code&…  &returnUrl=  &rt_api=     &scope=              &sessionToken=
&shipping_address[zip]=               &shop=      &sitekey=            &sku=
&storeId=              &storeKey=    &storeUniqCode=1   &successURL=   &tempSaveID=
```

**这是一张**查表**：代码要拼查询串时从这里取片段，不是每条都绑在某个特定 URL 上。**

**所以 R874 那条路走不通 —— 不是「没找到宿主」，是**没有宿主**。**

### 而它带来一个更重要的更正

**`&storeUniqCode=1` 的值**写死为 `1`**。它是一个**标志位**（「要带 store uniq code」），
而不是一个计算出来的编码。**

**R850 把它和 `_uniqCode` / `currentUniqCode` / `storeUniqCode` 归成「draw 参数记号」，四者并列。
现在看它们**不是同一类东西**：**

| 记号 | 性质 |
|---|---|
| `_uniqCode` | **属性后备字段** —— 值在运行时 |
| `currentUniqCode` · `storeUniqCode` | **属性名** —— 值在运行时 |
| **`&storeUniqCode=1`** | **固定标志位** —— 值恒为 1，无需来源 |

**所以「`uniqCode` 从哪来」这个问题，因为这条被排除而变窄了：它不是三个未知里最难的那个，
它是**两个运行时属性**的问题，而第三个根本不需要来源。**
"""

if "`&storeUniqCode=1` 是**查询片段表里的一条**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R875 appended")

BLOCKER = """

---

## 299. 那张表推翻了我的计划：`&storeUniqCode=1` **没有宿主，它值恒为 1**

> R875。未改产品代码。

### 一、R874 那条路走不通，而原因具体

**R874 写：`&storeUniqCode=1` 一定拼在某个 URL 后面，找到宿主就知道哪个页面带它。**

**查 `0x146a85000`–`0x146a8C000`：335 条串，**按字母序排**，全是查询片段 ——**

```
&paypal_client_cfci=  &pid=  &pl=5  &plannedCartLines=  &pm=no  &provider=
&quantity=  &quantity=1  &redirect_uri=  &referer=  &response_type=code&…
&returnUrl=  &rt_api=  &scope=  &sessionToken=  &shipping_address[zip]=
&shop=  &sitekey=  &sku=  &storeId=  &storeKey=  &storeUniqCode=1  &successURL=
```

**这是一张**查表**，不是某个 URL 的碎片。**没有宿主这一说。**

### 二、而它带来更重要的东西：那四个记号不是同一类

**`&storeUniqCode=1` 的值**写死为 1**。**

**R850 把四个记号并列成「draw 参数记号」：`_uniqCode` · `currentUniqCode` · `storeUniqCode` · `&storeUniqCode=1`。**

| 记号 | 性质 | 需要来源吗 |
|---|---|---|
| `_uniqCode` | 属性后备字段 | **要**，运行时 |
| `currentUniqCode` · `storeUniqCode` | 属性名 | **要**，运行时 |
| **`&storeUniqCode=1`** | **固定标志位** | **不要** |

**所以「`uniqCode` 从哪来」不是三个未知里最难的那个 —— 它是一个**两个运行时属性**的问题，
第三个根本不需要来源。**

**这条把一个看起来更重的 Unknown 削小了一部分，而这只有把四个记号拆开看才能做到。**

### 三、而这次拆开，与我前面几轮的做法相反

**R850 把它们并列，是因为它们在同一个搜索里一起出现。
R874 把它们并列，是因为它们在同一个问题里一起出现。**

**两次都是**因为位置相近而当成同类**。而它们的**性质**不同：两个是字段，一个是常量。**

**这是本会话里同一个错误的第 N 次形态：把「一起出现」当成「同一件事」。**

### 四、剩下的是什么

**「`_uniqCode` 的写入点」仍然 Unknown，原因仍是属性写入静态拿不到（R504/R874）。**

**但范围变小了：**
- **不需要找 `&storeUniqCode=1` 的来源**（它恒为 1）
- **需要找 `_uniqCode` 与 `currentUniqCode` 的来源** —— 那是两个属性写入

**而这个范围缩小没有让路变通，只是让待办更准。**

### 五、验证

```
idautils.Strings() 在 0x146a85000–0x146a8C000 之间 -> 335 条，字母序，全是 &xxx= 形式的查询片段
  含 &storeUniqCode=1（值恒为 1）· &storeId= · &storeKey= · &successURL= 等
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **`_uniqCode` / `currentUniqCode` 的写入点**：**Unknown** —— 属性写入，静态拿不到。
- **那 335 条片段表是给谁用的**：**Unknown** ——
  **它是「拼查询串」的通用工具，还是某一个流程专用的？看名字它覆盖了 PayPal / OAuth / Shopify / 运输 ——
  应该是通用的。但「通用」也是推断，没证。**
- **端点的查询串是不是也来自这张表**：**Unknown** ——
  **`/shop/v1/drawScratch/detail?uniqCode=` 里那个 `?uniqCode=` 是端点自带的，
  而 `&storeUniqCode=1` 要另外拼。两者是不是同一套机制，没查。**

### 七、教训

**我把「一起出现」当成「同一件事」，这已经是本会话的固定错误了 —— 而每次形态不同：**

| 轮 | 一起出现的是 | 其实是 |
|---|---|---|
| R830/R836 | 站名与 URL 形状 | 两种表面 |
| R863 | 「拿不到行为」与「UI」 | 两种断点（结构/工具） |
| **R875** | **四个 uniqCode 记号** | **两个字段 + 一个常量** |

**共同点：我在**位置**附近找**类别**。而位置相近只说明它们曾被同一个人写在附近。**

**这条要能防住，得在每次「并列」时问一句：它们需要来源吗？会被写吗？还是恒定的？**
"""

VERDICT = """

---

## 第 875 轮：`&storeUniqCode=1` 没有宿主，它值恒为 1

### R874 那条路走不通，原因具体

**查 `0x146a85000`–`0x146a8C000`：335 条串，**按字母序排**，全是查询片段：**

```
&paypal_client_cfci=  &pid=  &quantity=  &redirect_uri=  &returnUrl=
&sessionToken=  &shipping_address[zip]=  &shop=  &sitekey=  &sku=
&storeId=  &storeKey=  &storeUniqCode=1  &successURL=  &tempSaveID=
```

**这是一张**查表**，不是某个 URL 的碎片 —— 没有宿主这一说。**

### 更重要的：那四个记号不是同一类

| 记号 | 性质 | 需要来源吗 |
|---|---|---|
| `_uniqCode` | 属性后备字段 | **要**，运行时 |
| `currentUniqCode` · `storeUniqCode` | 属性名 | **要**，运行时 |
| **`&storeUniqCode=1`** | **固定标志位（值恒 1）** | **不要** |

> **所以「`uniqCode` 从哪来」不是三个未知里最难的那个 —— 它是**两个运行时属性**的问题，第三个根本不需要来源。**

**这条把一个看起来更重的 Unknown 削小了一部分，而这只有把四个记号拆开看才能做到。**

### 而这次拆开，与我前面几轮的做法相反

**R850 并列它们，因为它们在同一搜索里出现；R874 并列它们，因为它们在同一问题里出现。
**两次都是因为位置相近而当成同类。而它们的性质不同：两个字段，一个常量。****

| 轮 | 一起出现的是 | 其实是 |
|---|---|---|
| R830/R836 | 站名与 URL 形状 | 两种表面 |
| R863 | 「拿不到行为」与「UI」 | 两种断点（结构/工具） |
| **R875** | **四个 uniqCode 记号** | **两个字段 + 一个常量** |

### 剩下的是什么

**`_uniqCode` 的写入点仍 Unknown（属性写入静态拿不到）。但范围变小了：不需要找 `&storeUniqCode=1` 的来源。**

**这个缩小没让路变通，只是让待办更准。**

### 仍然 Unknown

**`_uniqCode`/`currentUniqCode` 写入点** · **那 335 条片段表给谁用**（看名字覆盖 PayPal/OAuth/Shopify/运输，**「通用」也是推断**）·
**端点的 `?uniqCode=` 与 `&storeUniqCode=1` 是否同一套机制**

### 教训

> **我在**位置**附近找**类别**。而位置相近只说明它们曾被同一个人写在附近。**
> **要防住，得在每次「并列」时问一句：它们需要来源吗？会被写吗？还是恒定的？**
"""

BACKLOG_ADD = """

## 判据 — `&storeUniqCode=1` 没有宿主（R875）

**`0x146a85000`–`0x146a8C000`：335 条串，字母序，全是 `&xxx=` 查询片段 —— 是一张**查表**，不是 URL 碎片。**
**`&storeUniqCode=1` 值**恒为 1** → 固定标志位，**不需要来源**。**

### 四个记号不是同一类（修正 R850）

| 记号 | 性质 | 需来源 |
|---|---|---|
| `_uniqCode` | 属性后备字段 | **要** |
| `currentUniqCode` · `storeUniqCode` | 属性名 | **要** |
| **`&storeUniqCode=1`** | **固定标志位** | **不要** |

**→ 「`uniqCode` 从哪来」变成**两个运行时属性**的问题，范围变小。**

### 同一形态第 N 次

| 轮 | 一起出现的 | 其实是 |
|---|---|---|
| R830/R836 | 站名与 URL 形状 | 两种表面 |
| R863 | 「拿不到行为」与「UI」 | 两种断点 |
| **R875** | **四个 uniqCode 记号** | **两个字段 + 一个常量** |

| 仍 Unknown | |
|---|---|
| `_uniqCode`/`currentUniqCode` 写入点 | 属性写入，静态拿不到 |
| 335 条片段表给谁用 | 「通用」是推断 |
| 端点 `?uniqCode=` 与 `&storeUniqCode=1` 是否同一机制 | 未查 |

**纪律**：**每次「并列」都问一句 —— 需要来源吗？会被写吗？还是恒定的？**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R875", BLOCKER)
    ensure(RSTATUS, "R875", BLOCKER)
    ensure(RVERDICT, "第 875 轮", VERDICT)
    ensure(BACKLOG, "R875", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R875" not in h:
        h += ("\n## R875 补充 — `&storeUniqCode=1` 没有宿主\n\n"
              "**`0x146a85000`–`0x146a8C000` 有 335 条字母序串，全是 `&xxx=` 查询片段 —— 是一张**查表**，不是 URL 碎片。"
              "`&storeUniqCode=1` 值**恒为 1** → 固定标志位，**不需要来源**。**\n"
              "**→ 修正 R850 的四记号并列**：`_uniqCode`(字段) / `currentUniqCode`·`storeUniqCode`(属性名) 需要来源；`&storeUniqCode=1` 不需要。"
              "**「uniqCode 从哪来」范围变小：两个运行时属性，不是三个。**\n"
              "**同一形态第 N 次：把「一起出现」当成「同一件事」（R830/R836 · R863 · R875）。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R875"), (RSTATUS, "R875"), (RVERDICT, "第 875 轮"), (BACKLOG, "R875")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R875: the fragment has no host because it is a table entry with a fixed value\n\n"
         "R874 planned to find what &storeUniqCode=1 is appended to. Reading the region it lives in shows there is"
         " nothing to find: 0x146a85000 to 0x146a8C000 holds 335 strings in alphabetical order, every one a query"
         " fragment of the form &name=. It is a lookup table from which code takes fragments when building a query"
         " string, not debris from one particular URL. There is no host.\n\n"
         "That turns out to matter more than the dead end. The fragment's value is literally 1 -- a fixed flag meaning"
         " 'carry the store uniq code', not a computed identifier. So the four markers R850 collected together are not"
         " one kind of thing: _uniqCode is a backing field, currentUniqCode and storeUniqCode are property names, and"
         " &storeUniqCode=1 is a constant needing no source at all. The question of where uniqCode comes from is"
         " therefore about two runtime properties rather than three, which is a smaller question than it looked.\n\n"
         "The pattern is worth naming because it keeps recurring. R850 grouped the four because they surfaced in one"
         " search; R874 grouped them because they belonged to one question. Both times proximity was read as"
         " sameness, and the properties differ: two need a source and one does not. Earlier rounds did the same with"
         " site names and URL shapes in R830 and R836, and with 'behaviour unavailable' and 'UI' in R863.\n\n"
         "What is left is not easier, only more accurately stated. The write site for _uniqCode and currentUniqCode"
         " remains unavailable statically for the reason R504 gave -- setters are inlined -- and that wall covers every"
         " property write rather than only UI ones.\n\n"
         "Unknown: the write sites for _uniqCode and currentUniqCode; who consumes the 335-entry fragment table, where"
         " the names span PayPal, OAuth, Shopify and shipping and so suggest a general utility, though general is an"
         " inference rather than an observation; and whether the ?uniqCode= inside the detail endpoint and the separate"
         " &storeUniqCode=1 flag are two mechanisms or one.\n\n"
         "The lesson is a question to ask whenever listing things together: does this one need a source, will it be"
         " written, or is it constant? Proximity says only that one author put them near each other.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
