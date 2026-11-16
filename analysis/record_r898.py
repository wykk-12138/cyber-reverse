"""Record R898: six Vans paths recovered, with ownership labelled as inference."""

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
### Vans 的 6 条路径取到了，而**归属是 Inference 不是 Observation**（R898）

**R897 留下的下一步：取 Vans 那 3 个族的精确路径。**

### 结果：6 条

```
/cart/v1/cart/
/cart/v1/cartWithItem?locale=
/cart/v2/cart/
/cart/v2/checkout/order/
/cart/v2/checkout/order?locale=
/products/v2/products/
```

### 而扫描结果里没有一条带宿主

**输出里 `HOST` 行一条都没有 —— 也就是说这 6 条字面量**没有一个自带 `www.vans.com`**。**

**所以归属是**族级**的：R893 的共现扫描证明 `/cart/v1/`、`/cart/v2/`、`/products/v2/` 三个**族**
与 `www.vans.com` 同处一条字面量，而这 6 条**具体路径**没有。**

**两者强度不同：**
- **族级归属 = Observation（共现）**
- **路径级归属 = Inference（同平台的别的站也可能用同样的路径）**

**所以 `VansEndpoints` 里写了一个 `OwnershipIsInference = true` 常量，把这条限制固化进类型而不是只写在注释里。**

### 加了什么

| 文件 | 内容 |
|---|---|
| `src\\Cybersole.Stores\\Flows\\VansEndpoints.cs` | **新建**：6 常量 + `All` + `FamilyHost` + `OwnershipIsInference` |
| `tests\\Cybersole.Tests\\VansEndpointTests.cs` | **新建 6 用例** |

### 6 个用例里三个值得说

| 用例 | 钉住 |
|---|---|
| `BothCartVersionsArePresent` | **v1 与 v2 两个都留着** —— 镜像里都有，删任一个都是丢证据 |
| `TheOrderEndpointHasTwoSpellings` | 同一端点有 path 与 query 两种写法 |
| `TheProductsPathReallyRepeatsItsWord` | **`products/v2/products/` 的双词是镜像里的，不是我的笔误** |
| `OwnershipIsRecordedAsInferenceNotObservation` | **把「这是推断」钉成断言** —— 将来谁要按「观察到的归属」用这些路径，得先删掉这条 |

### 一个被换掉的测试

**第一版最后一个用例 `EveryPathAppearsVerbatimInTheSource` 读 `VansEndpoints.cs` 再查同一个文件里有没有这些字面量 —— 恒真，什么也没证明。**

**换成 `EveryPathStartsWithOneOfTheThreeFamilies`：每条路径必须以那三个族之一开头。
族段打错一个字仍会编译、仍看起来合理，所以这个检查有实际效力。**
"""

if "Vans 的 6 条路径取到了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R898 appended")

BLOCKER = """

---

## 322. Vans 6 条路径取到，归属标为 Inference；套件 1783 → **1789**

> R898。**改产品代码 +6 用例。** 套件 **1789 通过 / 0 失败 / 0 跳过**。

### 一、6 条

```
/cart/v1/cart/                      /cart/v2/cart/
/cart/v1/cartWithItem?locale=       /cart/v2/checkout/order/
/cart/v2/checkout/order?locale=     /products/v2/products/
```

### 二、而它们都没有自带宿主

**扫描输出里 `HOST` 行一条都没有 —— 这 6 条字面量没有一个含 `www.vans.com`。**

**所以归属分两级：**

| 级 | 结论 | 强度 |
|---|---|---|
| **族** | `/cart/v1/` `/cart/v2/` `/products/v2/` 与 `www.vans.com` 同处一条字面量 | **Observation**（R893 的共现） |
| **路径** | 这 6 条属 Vans | **Inference** —— 同平台的别的站可能用同样的路径 |

**所以类型里有一个 `OwnershipIsInference = true` 常量，把这条限制固化进代码而不是只写在注释里。**

### 三、6 个用例

| 用例 | 钉住 |
|---|---|
| `SixPathsWereRecovered` | 6 条且互不重复 |
| `BothCartVersionsArePresent` | **v1 与 v2 都留** —— 镜像里都有 |
| `TheOrderEndpointHasTwoSpellings` | path 与 query 两种写法 |
| `TheProductsPathReallyRepeatsItsWord` | **双词是镜像里的，不是笔误** —— 防止将来「整理」成服务器不认的路径 |
| `OwnershipIsRecordedAsInferenceNotObservation` | **把「这是推断」钉成断言** |
| `EveryPathStartsWithOneOfTheThreeFamilies` | 族段打错仍会编译，所以查前缀有实效 |

### 四、一个被换掉的恒真测试

**第一版最后一个用例读 `VansEndpoints.cs` 再查同一文件里有没有这些字面量 —— 恒真。**

**换成前缀检查。这个错误值得记：**我写了一个只测试「我刚才写了什么」的用例**，
它通过不代表任何关于镜像的事实。**

### 五、验证

```
图像扫描 /(?:cart|products)/v\d+/...  -> 6 条，无 HOST 行
VansEndpoints.cs 新建                  -> 6 常量 + All + FamilyHost + OwnershipIsInference
test --filter VansEndpointTests        -> 6 通过 / 0 失败
python tools\\metrics_report.py         -> 1789 通过 / 0 失败（原 1783 + 6）
```

### 六、仍然 Unknown

- **这 6 条到底属不属 Vans**：**Unknown，而这是本轮最要紧的限制。**
  **要判它得找 `www.vans.com` 与这些路径同处一条字面量的证据，而扫描说没有。**
- **请求体与响应形状**：**Unknown** —— 所以没有步骤调它们。
- **v1 与 v2 哪个是当前用的**：**Unknown** —— 镜像里两个都在。
- **`/products/v2/products/` 那类路径还有多少属别的站**：**Unknown** ——
  **`cart/v1`、`products/v2` 都是泛用段，可能同时是多个站的。**

### 七、教训

**这一轮最重要的动作不是取到 6 条路径，是**发现它们没有宿主**。**

**如果我没看 `HOST` 行为空，我会把「Vans 的端点」当观察写下去 —— 而它是推断。
两者的区别是：将来有人问「这真是 Vans 的吗」，Observation 能回答，Inference 不能。**

**R895 我学了「上界/下界/精确」；这一轮是它的另一个轴：**Observation 还是 Inference**。
而这两件事在文档里长得一模一样，只有标注能分开。**
"""

VERDICT = """

---

## 第 898 轮：Vans 6 条路径取到，而归属是 Inference 不是 Observation

### 6 条

```
/cart/v1/cart/                      /cart/v2/cart/
/cart/v1/cartWithItem?locale=       /cart/v2/checkout/order/
/cart/v2/checkout/order?locale=     /products/v2/products/
```

### 而扫描输出里没有一条带宿主

**`HOST` 行一条都没有 —— 这 6 条字面量没有一个含 `www.vans.com`。**

| 级 | 结论 | 强度 |
|---|---|---|
| **族** | 三个族与 `www.vans.com` 同处一条字面量 | **Observation**（R893 共现） |
| **路径** | 这 6 条属 Vans | **Inference** —— 同平台别的站可能用同样路径 |

> **所以类型里有 `OwnershipIsInference = true` 常量，把限制固化进代码而不是只写注释。**

### 6 个用例

| 用例 | 钉住 |
|---|---|
| `SixPathsWereRecovered` | 6 条互不重复 |
| `BothCartVersionsArePresent` | **v1 与 v2 都留** |
| `TheOrderEndpointHasTwoSpellings` | path 与 query 两种写法 |
| `TheProductsPathReallyRepeatsItsWord` | **双词是镜像里的，防将来「整理」错** |
| `OwnershipIsRecordedAsInferenceNotObservation` | **把「这是推断」钉成断言** |
| `EveryPathStartsWithOneOfTheThreeFamilies` | 族段打错仍会编译 |

### 一个被换掉的恒真测试

**第一版最后一个用例读 `VansEndpoints.cs` 再查同一文件里有没有那些字面量 —— 恒真。**

> **我写了一个只测试「我刚才写了什么」的用例。它通过不代表任何关于镜像的事实。**

### 仍然 Unknown

**这 6 条到底属不属 Vans**（**本轮最要紧的限制**）· **请求体与响应形状**（故无步骤调用）·
**v1 与 v2 哪个是当前的** · **还有多少 `cart/v1`、`products/v2` 这类泛用段路径属别的站**

### 教训

> **这一轮最重要的动作不是取到 6 条路径，是**发现它们没有宿主**。
> 如果没看 `HOST` 行为空，我会把「Vans 的端点」当观察写下去 —— 而它是推断。**
> **R895 我学了「上界/下界/精确」；这一轮是另一个轴：**Observation 还是 Inference**。
> 两者在文档里长得一模一样，只有标注能分开。**
"""

BACKLOG_ADD = """

## 优先级 ① — Vans 6 条路径（R898，**改产品代码 +6 用例**）

### 6 条

```
/cart/v1/cart/                      /cart/v2/cart/
/cart/v1/cartWithItem?locale=       /cart/v2/checkout/order/
/cart/v2/checkout/order?locale=     /products/v2/products/
```

### 归属分两级（要紧）

| 级 | 强度 |
|---|---|
| **族**：三族与 `www.vans.com` 同处一条字面量 | **Observation**（R893 共现） |
| **路径**：这 6 条属 Vans | **Inference** —— 同平台别的站可能用同样路径 |

**→ `VansEndpoints.OwnershipIsInference = true` 固化进类型。**

### 6 用例

**`SixPathsWereRecovered` · `BothCartVersionsArePresent`（v1/v2 都留）· `TheOrderEndpointHasTwoSpellings` ·
`TheProductsPathReallyRepeatsItsWord`（**双词是镜像里的**）· `OwnershipIsRecordedAsInferenceNotObservation` ·
`EveryPathStartsWithOneOfTheThreeFamilies`**

**套件 1783 → 1789 通过 / 0 失败。**

### 一个恒真测试被换掉

**第一版读 `VansEndpoints.cs` 再查同一文件里的字面量 → 恒真，什么也没证明。**

| 仍 Unknown | |
|---|---|
| 6 条到底属不属 Vans | **本轮最要紧的限制** |
| 请求体/响应形状 | 故无步骤调用 |
| v1 与 v2 哪个当前用 | 镜像里两个都在 |
| 多少泛用段路径属别的站 | `cart/v1`、`products/v2` 可能多站共用 |

**纪律**：**Observation 与 Inference 在文档里长得一样，只有标注能分开；不看「HOST 行为空」就会把推断写成观察。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R898", BLOCKER)
    ensure(RSTATUS, "R898", BLOCKER)
    ensure(RVERDICT, "第 898 轮", VERDICT)
    ensure(BACKLOG, "R898", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R898" not in h:
        h += ("\n## R898 补充 — Vans 6 条路径（**改产品代码 +6 用例**，套件 1783→**1789**）\n\n"
              "**6 条**：`/cart/v1/cart/` · `/cart/v1/cartWithItem?locale=` · `/cart/v2/cart/` · "
              "`/cart/v2/checkout/order/` · `/cart/v2/checkout/order?locale=` · `/products/v2/products/`。\n"
              "**而扫描输出里 `HOST` 行一条都没有** → 归属分两级：**族 = Observation（R893 共现）· 路径 = Inference**。"
              "**`VansEndpoints.OwnershipIsInference = true` 固化进类型。**\n"
              "**6 用例**，含 `TheProductsPathReallyRepeatsItsWord`（双词是镜像里的）与 `OwnershipIsRecordedAsInferenceNotObservation`。\n"
              "**一个恒真测试被换掉**（读自己的文件再查自己的字面量）。\n"
              "**纪律：Observation 与 Inference 在文档里长得一样，只有标注能分开。**\n"
              "**下一轮**：判这 6 条到底属不属 Vans（找路径级共现证据，扫描说没有）。\n")
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
             for p, k in ((RBLOCK, "R898"), (RSTATUS, "R898"), (RVERDICT, "第 898 轮"), (BACKLOG, "R898")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R898: six Vans paths recovered, and their ownership is inference rather than observation\n\n"
         "R897 established that Vans is represented in the replica -- a site id in DemandwareControllers and two test\n"
         " assertions -- with no REST endpoints at all, so www.vans.com measured zero of three families. This round\n"
         " recovered the paths.\n\n"
         "Six literals exist under the three families: cart/v1/cart, cart/v1/cartWithItem with a locale query,\n"
         " cart/v2/cart, cart/v2/checkout/order as both a path and a query form, and products/v2/products whose repeated\n"
         " word is in the image rather than a slip here.\n\n"
         "The important finding is not the six paths but that none of them carries a host. The scan prints a host for\n"
         " every literal that has one, and it printed none. So ownership splits in two: the families are Vans's by\n"
         " observation, because R893 found those family segments sharing a literal with www.vans.com; the individual\n"
         " paths are Vans's by inference only, because another store on the same platform could use identical paths and\n"
         " nothing recovered says otherwise. The type records that limit as a constant rather than a comment, so a\n"
         " future round that starts treating the ownership as observed has to delete a test that says it is not.\n\n"
         "Six tests pin the recovery. Two assert facts that would otherwise be tidied away: that both cart versions\n"
         " stay, since the image has both, and that products/v2/products really does repeat its word, so a later\n"
         " cleanup cannot fix it into a path no server answers. One asserts the inference label itself.\n\n"
         "The first draft of the sixth test read VansEndpoints.cs and checked that the paths appear in that same file,\n"
         " which is true of any file containing itself and proves nothing about the image. It was replaced with a check\n"
         " that every path starts with one of the three recovered families, which catches a mistyped family segment --\n"
         " a defect that would compile and look plausible.\n\n"
         "Unknown: whether these six paths are Vans's at all, which is this round's central limit and which would need\n"
         " a literal carrying both the host and the path, the thing the scan could not find; the request bodies and\n"
         " response shapes, which is why no step calls them; which cart version a given step uses; and how many other\n"
         " paths under generic segments like cart/v1 and products/v2 belong to different stores.\n\n"
         "R895 taught upper bound, lower bound and exact; this round adds a second axis, observation against inference.\n"
         " The two read identically in a document, and only the label separates them -- which is why the label is in the\n"
         " type.\n\n"
         "Product code changed, six constants and six tests; suite green at 1789, the previous 1783 plus six."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
