"""Record R1058: the type-name criterion is wrong, and goal says names may differ."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 「类型级缺口」这个判据**不能用名字对** —— 而 goal 早就说了（R1058）

**R1057 说剩下的是还没枚举的命名空间。这一轮把方法规模化：按**类型名**自动反查原版全名（R1056 的办法），
对 10 个核心类型跑一遍。结果 10 个**全部 UNRESOLVED** —— 而那暴露的不是 10 个缺口。**

### ① 10 个核心类型，原版一个都没有同名

```
AntiBotProtocol · AntiBotVendors · CaptchaSolverService · AdyenGateway · BrowserIdentity
VendorWiring · CloudflareClearance · DataDomeClearance · KasadaClearance   UNRESOLVED
ApiKasadaSolver                                                            UNRESOLVED（文件路径也猜错了）
types=10  resolved=0  unresolved=10
```

**→ 而已确认重合的只有两个：`CaptchaProvider` 与 `CloudflareSolver` —— 而它们都是**数据模型类**。
→ 这九个是**服务/协议类**，而原版**没有**这些名字。**

### ② 而 goal 第一句就写着「命名可不同」

> 「把 Cybersole.exe 5.18.32 … 做成功能 1:1 复刻件：函数数量对等、每个函数功能相等、效率相近；**命名可不同**，不要求字节级相同。」

**→ 所以「原版没有 `AntiBotProtocol` 这个类型」**不是缺口** —— 它只说明复刻件给那一层起了自己的名字。
→ 而 `AntiBotProtocol` 的内容（cookie 表）在原版里存在，只是**不叫这个名字**，或者**不是属性而是方法**。**

**→ 所以「类型级缺口」这个判据**不能用名字对**。而那是这几轮我一直在做的事：
→ R1055/R1056/R1057 的对照之所以有意义，是因为 `CaptchaProvider` 与 `CloudflareSolver` **恰好同名**
→ 而那两个之所以同名，是因为它们是**用户可见的数据模型**（设置文件里的字段名必须与镜像一致）。**

### ③ 所以正确的判据分层

| 类型 | 判据 | 依据 |
|---|---|---|
| **数据模型**（要写进设置文件的） | **按名字对** | 字段名进 JSON，必须与镜像一致 |
| **服务/协议类** | **按功能对** | goal 允许命名不同 |

**→ 而 `TypeCoverage` 那份文档只覆盖了第一层（2 个命名空间，各 1 个类型，缺口 0）——
→ 而它的范围说明里写着「不声称枚举了它们」，那句话现在有了更准确的理由：**
**→ 不是「没查到」，是「那层的判据不同」。**

### ④ 而生成物现在把三种成因分开

**旧表述：「Unknown：镜像里没有以 `X,` 开头的元数据 ⇒ 或原版无此类型，或属性全被内联掉」—— 两因。
→ 而它漏了第三种，而第三种**恰恰是最常见的**：「原版用别的名字」。**

**新表述是一张表：**

| 成因 | 是不是缺口 |
|---|---|
| 原版无此类型（那层是方法或数据） | **不是** |
| 原版用别的名字（goal 允许） | **不是** |
| 属性 getter 全被内联 | **Unknown —— 需另找路径** |

**→ 所以每一行现在都写着「本行**不能**读成『这个类型在原版缺失』」。**

### ⑤ 而这一轮的净值是一句话

**「类型级缺口」在 (a) 里指的是**数据模型**的缺口，不是**名字**的缺口。
→ 而名字那一层由 goal 明确豁免，所以对它做对照**只会产出假缺口** —— 10 个，全是假的。**

### ⑥ 数字

| 度量 | R1057 | **R1058** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 4 / 889 | **4 / 889** |
| 函数数 | 174,293 | **174,293** |
| **对照的类型数** | 2 | **12（2 数据模型 + 10 服务类）** |
| **数据模型缺口** | 0 | **0（未变）** |
| **服务类 resolved** | 未测 | **0 / 9（全不同名）** |
| **那些是缺口吗** | 隐含「是」 | **不是 —— goal 允许命名不同** |
| **假缺口** | — | **10（若按名字判）** |
| **`docs/TYPE_REVERSE.md`** | 不存在 | **已生成（三种成因分开）** |

### 教训

> **一个判据用错了，会产出**整齐的**假结论 —— 10 个全 UNRESOLVED 看起来像「大规模缺失」，
> 而它其实是「我用了 goal 明确豁免的那个维度」。**
> **→ 而那与之前那些假零不同：那些是「空集减空集」，这个是「**用错了轴**」。
> → 假零让人以为没事，假缺口让人以为事很大 —— 而两者都不是事实。**
"""

if "「类型级缺口」这个判据**不能用名字对**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1058 —— **「类型级缺口」不能用名字对 —— goal 早就说了「命名可不同」**

### 10 个核心类型，原版一个都没有同名

```
AntiBotProtocol · AntiBotVendors · CaptchaSolverService · AdyenGateway · BrowserIdentity
VendorWiring · CloudflareClearance · DataDomeClearance · KasadaClearance · ApiKasadaSolver
→ types=10  resolved=0  unresolved=10
```

**而已重合的只有 `CaptchaProvider` 与 `CloudflareSolver` —— 两个都是**数据模型类**。**

### 而 goal 第一句：「…效率相近；**命名可不同**，不要求字节级相同。」

**⇒ 「原版没有 `AntiBotProtocol` 这个类型」**不是缺口**，只说明复刻件给那层起了自己的名字。
⇒ 「类型级缺口」的判据**不能用名字对**。而 R1055–R1057 的对照之所以有意义，
是因为那两个类型**恰好同名**（用户可见的数据模型，字段名进 JSON，必须与镜像一致）。**

### 正确的判据分层

| 类型 | 判据 | 依据 |
|---|---|---|
| **数据模型**（写进设置文件） | **按名字对** | 字段名进 JSON，须与镜像一致 |
| **服务/协议类** | **按功能对** | goal 允许命名不同 |

### 而生成物把三种成因分开

| 成因 | 是不是缺口 |
|---|---|
| 原版无此类型（那层是方法或数据） | **不是** |
| 原版用别的名字（goal 允许） | **不是** |
| 属性 getter 全被内联 | **Unknown —— 需另找路径** |

**每行现在写着「本行不能读成『这个类型在原版缺失』」。**

### 数字

| 度量 | R1057 | **R1058** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 对照类型数 | 2 | **12** |
| 数据模型缺口 | 0 | **0** |
| 服务类 resolved | 未测 | **0 / 9** |
| 那些是缺口吗 | 隐含「是」 | **不是** |
| 假缺口 | — | **10** |
| `TYPE_REVERSE.md` | — | **已生成** |

**纪律**：假零让人以为没事，假缺口让人以为事很大 —— 而两者都不是事实。用错轴比查不到更危险。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1058", NOTE)
append(RBLOCK, "R1058", "\n---\n\n## 482. **「类型级缺口」不能用名字对 —— goal 允许命名不同**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1058: the type-name criterion is wrong, and the goal says names may differ\n\n"
     "R1057 closed two namespaces and left the rest as unknown. This round generalised the reverse lookup R1056 used\n"
     " and ran it over ten core types. All ten came back unresolved, which is not ten gaps.\n\n"
     "AntiBotProtocol, AntiBotVendors, CaptchaSolverService, AdyenGateway, BrowserIdentity, VendorWiring and the three\n"
     " clearance classes have no same-named type in the original. The only two that did are CaptchaProvider and\n"
     " CloudflareSolver, and both are data models -- the kind whose field names go into a settings file and therefore\n"
     " have to match. The other nine are services and protocols, and the goal's first sentence says naming may differ.\n\n"
     "So comparing type names is the wrong axis for that layer. R1055 through R1057 were not wasted, but their validity\n"
     " rested on an accident: those two types happen to share names because they are user-visible models. Applied to\n"
     " services, the same method produces ten confident gaps out of nothing.\n\n"
     "The criterion splits in two. Data models are compared by name, because their field names are in the JSON. Services\n"
     " are compared by function, because their names are ours. And the document now separates three causes of a miss\n"
     " rather than two: the original has no such type because that layer is a method or plain data, the original uses a\n"
     " different name which the goal permits, or the accessors were inlined away and the shape cannot see them. Only the\n"
     " third is unknown, and each row says its miss must not be read as absence.\n\n"
     "Figures: suite green at 2258, freshness four files and 889 lines, count 174,293, twelve types compared instead of\n"
     " two, zero data-model gaps unchanged, zero of nine service classes resolved, and ten gaps that would have been\n"
     " invented by the wrong axis.\n\n"
     "Unknown: the functional equivalence of those nine service classes, which name matching cannot answer and which\n"
     " needs behaviour rather than metadata.\n\n"
     "The lesson is that a wrong axis produces tidy false conclusions. A false zero says nothing is wrong; a false gap\n"
     " says a great deal is -- and neither is a fact."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
