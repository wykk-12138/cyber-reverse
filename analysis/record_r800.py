"""Record R799+R800: hypecommerce rewritten to what the evidence supports, 71% -> 14%."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 225. `hypecommerce` 从 **71% 降到 14%** —— 数字下降是这一轮的目的

> R799/R800。`RetailFlows.cs`：`HypeCommerceFlow` 整块重写。

### 一、原来那 71% 是什么

五个路径**全不在镜像里**：

```
/api/auth/login         ← 没有
GET /api/entries/{slug} ← 镜像只有 POST create/validate
/api/cart               ← 没有
/api/cart/checkout      ← 没有
/checkout               ← 没有
```

**只有主机 `admin.hypecommerce.io` 是对的。**

### 二、R799 的第一次尝试**没有改变数字**

我把那五个换成诚实失败（`NoStorefront("cart")` 之类），**覆盖率仍是 71%。**

**因为矩阵数的是「有没有覆写」，不是「能不能用」。**
**这正是 R772 记过的那条：声明一个覆写就等于一次实现。**

**所以「诚实失败」在矩阵里和「能用的实现」长得一模一样。**

### 三、R800 的做法：**不声明**

把七个覆写删掉，让基类去拒绝。**矩阵于是显示 `-`，模块落到 1/7 = 14%。**

**而理由放在类注释与豁免条目里 —— 那是读的人本来就会看的地方。**

**一个说「只有一步」的数字 + 一段解释，比一个说「五步」而撒谎的数字更有用。**

### 四、R800 也修了 R799 的一次自伤

R799 的替换脚本把 `END` 锚点设成 `"/// <summary>"` ——
**而那个串在我新写的类注释里也有**，所以**第二次运行时区间在 244 字符处就闭合了**，
把文件改成了 `error CS1022`。

**恢复方式**：`git checkout --` 回到 R798 状态。
**修正方式**：`END` 改锚 `"/// <summary>\\n/// Fanatics"`（在区间之外、不会移动），
**并在写盘前加四道前置检查**：区间长度 > 4000、区间必须含 `HypeApi`/`SubmitOrderAsync`/`OpenCheckoutAsync`、
替换后类声明恰好 1 个、替换后不能残留那五个路径或 `NoStorefront`。

**四道都过才写盘。** 这一次全过。

### 五、结果

```
hypecommerce   -  -  -  -  -  -  +   14%
resolved 63/63 flows; fully covered 51; exempt 6
```

**`fully covered` 仍 51** —— 这个模块本来就是豁免的，**所以分母与覆盖数都不动。**
**动的是「这个模块声称自己有几步」。**

### 六、验证

```
构建                已成功
ModuleCoverageTests hypecommerce 14%（此前 71%）
完整套件            1766 通过 / 0 失败 / 0 跳过
四项度量            4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- **`entries/validate` / `entries/create` 的请求体**：**Unknown** —— 现在只发 `{entryId}`，很可能被拒。
- **`payment/methods/store` / `settings` 的用途**：**Unknown**。
- **镜像有没有 hypecommerce 的店面面**：**Unknown** —— 只搜过 `hypecommerce` 一种写法。

### 八、这一轮的教训

**「把错误改得更诚实」可能连数字都不动。**
R799 把五个编的路径换成五个诚实失败，**71% 一分未变** —— 因为矩阵不看内容。

**所以要让数字跟着诚实走，必须改变"声明"本身，而不是声明的内容。**
"""

VERDICT = """

---

## 第 799–800 轮：hypecommerce 从 71% 降到 14%，而数字下降是目的

### 原来那 71% 是五个编的路径

```
/api/auth/login · GET /api/entries/{slug} · /api/cart · /api/cart/checkout · /checkout
```

**全不在镜像里。只有主机 `admin.hypecommerce.io` 是对的。**

### R799 把编的换成诚实失败 —— **数字一分未变**

**因为矩阵数的是「有没有覆写」，不是「能不能用」。** 这正是 R772 记过的那条。

> **「诚实失败」在矩阵里和「能用的实现」长得一模一样。**

### R800 的做法：**不声明**

删掉七个覆写，让基类拒绝。**矩阵显示 `-`，落到 1/7 = 14%。**
**理由放进类注释与豁免条目 —— 读的人本来就会看那里。**

> **一个说「只有一步」的数字 + 一段解释，比一个说「五步」而撒谎的数字更有用。**

### R800 修了 R799 的一次自伤

R799 的脚本把 `END` 锚成 `"/// <summary>"`，**而那个串在我新写的注释里也有**，
第二次运行时区间在 244 字符处闭合，把文件改成 `error CS1022`。

**恢复**：`git checkout --`。**修正**：`END` 改锚 `"/// <summary>\\n/// Fanatics"` + **写盘前四道检查**
（区间 > 4000 字符、含三个关键符号、替换后类声明恰好 1 个、不残留五个路径与 `NoStorefront`）。

### 结果

```
hypecommerce   - - - - - - +   14%
resolved 63/63 · fully covered 51 · exempt 6
```

### 教训

**「把错误改得更诚实」可能连数字都不动 —— 要让数字跟着诚实走，必须改变「声明」本身，而不是声明的内容。**
"""

BACKLOG_ADD = """

## 核心 — hypecommerce 已重写（R799/R800）

**从 71% 降到 14%，数字下降是目的。**

| 项 | 状态 |
|---|---|
| 五个编的店面路径 | **已删**（`/api/auth/login`、`GET /api/entries/{slug}`、`/api/cart`、`/api/cart/checkout`、`/checkout`） |
| 七个诚实失败覆写 | **已删** —— 它们在矩阵里和实现长得一样（R772 的教训） |
| `SubmitOrderAsync` | **保留**：`entries/validate` → `entries/create`（镜像确有两端点） |

**关键认识**：`ModuleCoverageTests` 数的是「有没有覆写」。
**所以「写诚实失败」不改变数字，「不声明」才改变数字。**
**理由应该写在类注释与豁免表，不该指望一个虚高的百分比替你说。**

| 仍 Unknown | |
|---|---|
| `entries` 请求体 | 现在只发 `{entryId}`，很可能被拒 |
| `payment/methods/store` / `settings` 用途 | 未查 |
| 镜像有无店面面 | 只搜过 `hypecommerce` 一种写法 |

**工具教训（R800）**：块替换的 `END` 锚点若可能出现在新内容里，**必须换成区间之外且不会移动的锚**，
并在写盘前做后置检查。R799 的 `END = "/// <summary>"` 就因为出现在替换文本里而把文件改坏了。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R800", BLOCKER)
    ensure(RSTATUS, "R800", BLOCKER)
    ensure(RVERDICT, "第 799–800 轮", VERDICT)
    ensure(BACKLOG, "R799/R800", BACKLOG_ADD)

    ok = True
    for path in (RBLOCK, RSTATUS, RVERDICT, BACKLOG):
        body = io.open(path, encoding="utf-8").read()
        key = "第 799–800 轮" if path == RVERDICT else ("R800" if path != BACKLOG else "R799/R800")
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R799/R800: hypecommerce falls from 71% to 14%, and the fall is the point\n\n"
         "The old flow carried five storefront paths -- /api/auth/login, GET /api/entries/{slug}, /api/cart,\n"
         "/api/cart/checkout and /checkout -- and not one of them is in the image. Only the host,\n"
         "admin.hypecommerce.io, was right. They scored 71% anyway, because the coverage matrix asks whether a step is\n"
         "overridden rather than whether its path came from evidence.\n\n"
         "R799 replaced them with honest failure stubs and the number did not move by one percent. That is the same\n"
         "defect one layer down: a declared failure counts exactly like a working step. So R800 removed the overrides\n"
         "entirely and let the base class refuse those steps. The matrix now reports one of seven, and the reason sits\n"
         "in the class documentation and the exemption entry, which is where a reader looks for reasons anyway.\n\n"
         "One step survives because the image supports it: entries/validate followed by entries/create, both of which\n"
         "have exactly one builder function and a host that is genuinely in the pool.\n\n"
         "R800 also repaired an injury from R799. The block-replacement script anchored its end on the string\n"
         "'/// <summary>', which appears inside the replacement text itself, so a second run closed the span after 244\n"
         "characters and left the file unparseable. git checkout restored it; the anchor became the next class's doc\n"
         "line, which lives outside the region, and writing now requires four preconditions to hold -- span over 4000\n"
         "characters, three expected symbols inside it, exactly one class declaration afterwards, and none of the five\n"
         "invented paths or the stub helper surviving.\n\n"
         "The lesson worth keeping: making an error more honest may not move the number at all. To move it, the\n"
         "declaration has to change, not the content of the declaration.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged; fully covered stays 51 because the module was already\n"
         "exempt and only its self-description changed."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
