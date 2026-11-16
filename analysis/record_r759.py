"""Record R759: IDA brought up, three findings, and one method that failed."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 187. 核心取证第一轮：`-12` 规则再中一次；**求交法失败**；而 10 个店名里 7 个在原版无字面量

> R759。新增 `analysis/store_catalog.py`（复刻件侧结构化清单）、`analysis/find_store_registry.py`（失败的方法，保留）。

### 一、IDA 例程按 goal 走通了，而且 `PROXY: MISSING` **不是阻塞项**

```
ida.exe "请确认" → IDA has found an unpacked version of database … → Proceed with unpacked base
ida.exe "请确认" → Database for …Cybersole.exe.id0 is not closed … → 是(Y)
ida.exe "请稍候..." → 进度条，等
```

**两框 + 一个进度条，与 YG 说的一致。** 之后：

```json
{"status":"ok","idb_path":"…\\target\\Cybersole.exe.i64","imagebase":"0x140000000",
 "auto_analysis_ready":true,"hexrays_ready":true}
```

**doctor 仍报 `PROXY: MISSING`，但 `analysis/ida.py` 直连插件，所以不影响。**
**纠正：上一轮我请 YG 去开关 MCP 条目 —— 不必。** 那一行只说明 DSH 没起代理进程，
而插件本身在 13337 上应答就够了。

### 二、`-12` 规则第三次中

查 `https://www.supremenewyork.com`（`0x14709ada4`）：
- 直接 xrefs → **0 条**
- `0x14709ad98`（chars − 12）→ **3 条**，落在 `sub_140D59870` / `sub_140D5A850`

**NativeAOT 的代码 `lea` 指向对象头，不是字符。** 这条已经写进若干脚本，但每次手查都要记得。

### 三、顺带挖到原版的 **captcha 页契约**（对风控复刻直接有用）

`0x143ca8507` 是一整页 HTML（Supreme 主题），关键三行：

```html
<script src="https://www.google.com/recaptcha/enterprise.js?render=%sitekey%"></script>
grecaptcha.enterprise.execute(document.Solver.Captcha.Sitekey,
                               { action: document.Solver.Captcha.Action })
  .then(onCaptchaSuccess)        // → document.Solver.Captcha.Solve(response)
```

以及两个测试按钮 `Test reCAPTCHA` / `Test hCaptcha`。

**这是"页面 JS ⇄ 宿主 solver"的回调契约**：站点键与 action 由宿主注入，**解出的 token 通过
`document.Solver.Captcha.Solve(response)` 交回**。**这是 Observation，不是推断。**

### 四、**求交法失败**，以及为什么

思路：取几个不会重名的店名，各自 `-12` 取 xref，**求交**，交集即注册表。

实际：

```
Footpatrol   literals=1  → sub_14117C4E0 (687,318 B)
Warhammer    literals=2  → 9 个函数（含 sub_14117C4E0 与 sub_140F7DDE0 70,719 B）
John Lewis   literals=2  → 18 个函数（同上两个）
Superswipe / Pocket Games / JB Hi-Fi / Yeezy Supply / END. / Notre / Offspring  → literals=0
交集：sub_14117C4E0
```

**`687,318 字节`不是函数** —— 那是 IDA 在没有 `.pdata` 边界时把整片并成一个符号的产物。
**所以"交集"给出的是一个 blob，方法在这个目标上不成立。** 脚本保留，标为失败方法（同 R719 的处理方式）。

### 五、而更值得注意的是那 7 个 `literals=0`

复刻件有 22 个 module，其中 **`Superswipe` / `Pocket Games` / `JB Hi-Fi` / `Yeezy Supply` /
`END.` / `Notre` / `Offspring` 这 7 个的显示名，在原版里找不到任何字面量。**

**这不是"原版没有这些站"的证明** —— 名字可能是拼出来的、来自资源、或我搜的方式不对。
**但它是一个必须回答的问题**：**复刻件的 store 清单，有多少是从原版取证来的，有多少是照名字猜的？**

**判据 f 要的正是这件事，而现在它给出的第一个结果是不舒服的。**

### 六、复刻件侧的结构化清单（判据 f 的右半边）

`analysis/store_catalog.py` 按声明抽取，**不靠子串**：

```
modules: 22      域名重复: 0      无域名: 1（ShopifyModule，见下）
```

**它自己有缺陷**：`ShopifyModule` 的 `Id`/`Name`/`Domains` 是**构造函数链里赋的**
（`public ShopifyModule() : this("shopify", "Shopify", new[] {…})`），而脚本只认 `=>` 表达式体，
**于是它输出 `?`**。**这与 R753「`(i)  Startup Page` 报假缺席」是同一类错误：扫描器假设了声明形式。**
已记，未修完（补丁写坏一次，下轮重做）。

### 七、验证

```
本轮未改产品代码
完整套件保持 1745 通过 / 0 失败
新增分析脚本 2 个（1 个方法失败但保留）
```

### 八、仍然 Unknown

- 原版**实际**的 store 清单：**Unknown** —— 求交法失败，需要换锚点（候选：module id 字符串、
  或注册函数里的数组初始化模式）。
- 那 7 个店名在原版里是否存在：**Unknown** —— 无字面量既不证明有也不证明没有。
- `sub_14117C4E0` 那片 687 KB 是什么：**Unknown**（IDA 未建立边界）。
- `document.Solver.Captcha` 其余成员：**Unknown** —— 只读到一个页面，未系统枚举。
"""

VERDICT = """

---

## 第 759 轮：核心取证第一击 —— 一个方法失败，一个发现不舒服

### IDA 按 goal 的例程走通了

两个「请确认」+ 一个「请稍候…」，与 YG 说的一致。**而且 `PROXY: MISSING` 不是阻塞项**——
`ida.py` 直连插件。**上一轮我请你去开关 MCP 条目，不必了。**

### `-12` 规则第三次中

Supreme 基址直接 xrefs = 0；`chars − 12` = 3 条。**NativeAOT 的 `lea` 指向对象头。**

### 顺带挖到 captcha 页契约

```js
grecaptcha.enterprise.execute(document.Solver.Captcha.Sitekey,
                               { action: document.Solver.Captcha.Action })
  .then(() => document.Solver.Captcha.Solve(response))
```

**站点键与 action 由宿主注入，token 经 `Solve(response)` 交回。** 这是 Observation。

### 求交法失败

交集落在 **`sub_14117C4E0`，687,318 字节** —— **不是函数，是 IDA 无边界时的并片。**
脚本保留，标为失败方法。

### 而不舒服的是另一半

10 个店名里 **7 个在原版里 `literals=0`**：`Superswipe` / `Pocket Games` / `JB Hi-Fi` /
`Yeezy Supply` / `END.` / `Notre` / `Offspring`。

**这不是"原版没有"的证明**。**但它提出了一个必须回答的问题**：

> **复刻件的 22 个 store，有多少是从原版取证来的，有多少是照名字猜的？**

**判据 f 要的正是这件事 —— 而它给出的第一个结果是不舒服的。**

### 复刻件侧清单也有一处自伤

`store_catalog.py` 输出 22 modules、域名零重复，但 `ShopifyModule` 显示 `?` ——
因为它的字段在**构造函数链**里赋，脚本只认 `=>`。

**这与 R753 那次「`(i)  Startup Page` 报假缺席」是同一类错误：扫描器假设了声明形式。**

### 验证

```
产品代码未改；套件 1745 / 0
```

### 下一轮

换锚点找原版注册表（候选：module id 字符串 / 数组初始化模式）；
并修 `store_catalog.py` 的构造函数形式。
"""


def main():
    for p, marker, text in ((P1, "R759", BLOCKER), (P3, "R759", BLOCKER), (P2, "第 759 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R759: IDA up, one method that failed, and an uncomfortable first result for criterion f\n\n"
         "Brought IDA up following the routine now written into the goal: two confirmation dialogs, then a\n"
         "progress window to wait on, then health reports auto_analysis_ready and hexrays_ready. The doctor's\n"
         "PROXY: MISSING line turned out not to matter -- analysis/ida.py talks to the plugin directly, so the\n"
         "request I made of YG last round to toggle the MCP entry was unnecessary and is retracted.\n\n"
         "The -12 rule held again: querying https://www.supremenewyork.com returns no cross-references, while\n"
         "the object header twelve bytes earlier returns three, landing in two functions. NativeAOT code\n"
         "addresses the header, not the characters.\n\n"
         "One incidental find is directly useful for the risk-control work: the binary embeds the captcha page\n"
         "the solver loads, and its script shows the contract -- recaptcha enterprise executes with a sitekey\n"
         "and action injected by the host, and the token comes back through document.Solver.Captcha.Solve.\n\n"
         "The store-registry method failed. Intersecting the functions that name several stores lands on\n"
         "sub_14117C4E0 at 687,318 bytes, which is not a function but IDA merging a region where it found no\n"
         "boundaries. The script is kept and marked as a failed approach, like R719's fan-in criterion.\n\n"
         "The uncomfortable half: seven of the ten store names tried have no literal anywhere in the original.\n"
         "That does not prove those stores are absent -- a name can be assembled -- but it turns criterion f\n"
         "into a question about the replica rather than only about coverage: how much of its 22-store catalogue\n"
         "was taken from the binary, and how much was named by guess.\n\n"
         "The replica-side extractor reports 22 modules with no duplicate domains, but shows ShopifyModule as\n"
         "'?' because that class assigns Id, Name and Domains through a chained constructor while the script\n"
         "only accepts expression-bodied overrides. Same class of mistake as R753's false absence."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
