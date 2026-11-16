"""Record R708: the C10 split, and the four detector gaps it exposed in my own tool."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 137. C10 那 819 个成员拆开了：**682 是链接器干的，55 待查，70 早已结案**

> R708。新增 `analysis/c10_split.py`、`analysis/c10_type_crosscheck.py`。

### 一、判据（先定）

每个成员必须落进且只落进一个桶：

```
visible         产物里有 <Type>__<Member> 或其 get_/set_ 符号
declared-absent 源码在类型里声明了它，产物没有对应符号  -> 被裁剪/内联，不是缺陷
undeclared      类型在源码里，但成员没声明              -> 唯一的缺陷桶
type-absent     源码里没有承载该名字的类型              -> 见交叉检验
```

### 二、结果

```
visible          12  (1.5%)
declared-absent 682 (83.3%)
undeclared       55  (6.7%)
type-absent      70  (8.5%)
sum = 819  MATCHES
```

**交叉检验（重要）**：`type-absent` 的 70 个成员分布在 11 个类型上，
**这 11 个全部已在 `docs/TYPE_PRESENCE_TRIAGE.md` 的 17 条里结案** —— 所以这一桶**不引入新缺口**。

### 三、我自己的工具错了四次，每次都靠另一个工具抓出来

| # | 错 | 症状 | 谁抓到的 |
|---|---|---|---|
| 1 | 只匹配成员名后缀，不带类型 | 报 **378/819 可见**（46%） | 与 `aot_member_coverage.py` 的 12 差太远 |
| 2 | 带了类型但**丢了前导下划线** | 报 **14**（`Action` 撞上 `SmartAction`、`Element` 撞上 `XmlElement`） | 差 2，逐条 diff 出来的 |
| 3 | 只扫类体，不扫 `record` 位置参数 | `Notification.Timestamp` 被判"未声明"，55 条 | R634 明明补过它 |
| 4 | 只认 `class|record`，且没剥泛型元数 | `IDataProvider`/`IWebhook`/`State`/`EditValue\\`1` 被判类型缺失 | 交叉检验说这 4 个不在 triage 里 |

**第 2 条最值得记**：`aot_member_coverage.py` 的 `"_" + base` 是**故意的**，注释里写着「与 func_compare.py 同一个数」。
我把它当成冗余去掉了，于是把 `SmartAction` 的符号算给了 `Action`。
**旧工具是对的，我的"简化"制造了两个假阳性 —— 而总数从 12 变 14 看起来只是"更精确了一点"。**

### 四、第 4 条之后还有一次同型错误

`c10_type_crosscheck.py` 里我**复制**了 `c10_split.py` 的类型解析逻辑，修了后者没修前者，
于是它继续报 `EditValue\\`1` 缺失。**已改成 import 复用 `S.resolve`，不再有第二份实现。**

### 五、剩下 55 条怎么办

看名字就知道多数**不是我漏写**，是我的检测器不认识继承：

```
Close / Save / Create / Delete / Reset / Properties / TimeSpans / View / Test / Export / Edit
```

这些几乎都是基类 view-model 上的命令（`Save`、`Close` 出现在十几个 *View 上）。
**下一轮做继承解析**（沿 `: Base` 链查声明），之后再判这 55 条里哪些是真的没实现。

### 六、仍然 Unknown

- 那 55 条里有多少是继承来的：**Unknown**（继承链未解析）。
- `declared-absent` 682 条里，哪些是**内联**、哪些是**裁剪**、哪些**只在元数据**：**Unknown** ——
  本桶只证明"产物没有独立符号"，分不开这三种成因（需要关 trimming 的诊断构建 + 符号对照）。

### 七、这一轮的方法学

> **两个实现给出不同答案时，先假设新的那个错。**

本轮四次修正，方向全部是「向旧工具靠拢」：
12 是对的、378 是错的；12 是对的、14 是错的；记录位置参数让 55 变小是对的；剥泛型/认接口让 92 变小是对的。
**没有一次是新工具纠正了旧工具。**
"""

VERDICT = """

---

## 第 708 轮：C10 拆开了 —— 682 链接器 / 55 待查 / 70 早已结案

### 四分类（和 = 819）

```
visible          12  (1.5%)   产物有符号
declared-absent 682 (83.3%)   源码有声明、产物无符号 -> 裁剪/内联，不是缺陷
undeclared       55  (6.7%)   类型在、成员没声明 -> 唯一缺陷桶
type-absent      70  (8.5%)   11 个类型，全部已在 triage 的 17 条里
```

### 我的工具错了四次，四次都是旧工具对

| 错 | 报出 | 抓到方式 |
|---|---|---|
| 不带类型 | 378 可见 | 与覆盖工具的 12 差太远 |
| 丢了前导下划线 | 14（`Action`↔`SmartAction`） | 差 2，逐条 diff |
| 只扫类体 | `Notification.Timestamp` 判"未声明" | R634 补过它 |
| 不认接口/泛型元数 | 4 个类型被判缺失 | 交叉检验 |

**第 2 条最典型**：`"_" + base` 是旧工具**故意的**，我去掉它换来两个假阳性，
而总数 12→14 看起来只像"更精确了一点"。

还踩了第 5 次同型错：crosscheck 复制了解析逻辑、只修了一处 → 已改成 import。

### 一句话

> **两个实现给出不同答案时，先假设新的那个错。**

> 本轮四次修正方向全部是「向旧工具靠拢」，没有一次是新工具纠正了旧工具。
> 这不是谦虚，是概率：老代码被跑过更多次，我的新代码这一轮才写。

### 下一轮

55 条里 `Close/Save/Create/Delete/Reset` 几乎全是基类命令 —— 做**继承链解析**，再判哪些是真没实现。
"""


def main():
    for p, marker, text in ((P1, "R708", BLOCKER), (P3, "R708", BLOCKER), (P2, "第 708 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R708: split C10's 819 members -- 682 compiled away, 55 to check, 70 already triaged\n\n"
         "  visible          12  (1.5%)   symbol present in the artifact\n"
         "  declared-absent 682 (83.3%)   source declares it, no symbol: trimmed or inlined\n"
         "  undeclared       55  (6.7%)   type exists, member does not -- the only defect bucket\n"
         "  type-absent      70  (8.5%)   11 types, every one already closed by TYPE_PRESENCE_TRIAGE\n\n"
         "My tool was wrong four times and each time an existing tool caught it: bare-name matching\n"
         "said 378 visible; dropping the leading underscore made Action match SmartAction and Element\n"
         "match XmlElement (14); scanning only class bodies missed record positional parameters, so\n"
         "Notification.Timestamp read as undeclared; and ignoring interfaces plus generic arity markers\n"
         "made four types look absent. A fifth slip of the same kind -- duplicating the resolver in the\n"
         "cross-check script and fixing only one copy -- is now an import.\n\n"
         "Every correction moved toward the older tool's answer. No new tool corrected an old one."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
