"""Record R717: the Setter calibration failed, so the descriptor-kind line is closed."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 146. 校准失败：`Setter` 既不是「有 set 访问器」也不是「双向绑定」—— 这条线关掉

> R717。新增 `analysis/setter_semantics.py`；改生成器并重生成 `docs/MEMBER_GAP_EVIDENCE.md`。

### 一、判据（先定）

R716 留下的问题：`Setter` 是唯一变化的维度（77.9%），它编码什么？两个候选读法：
(a) 成员声明了 setter；(b) 绑定是双向的。

**测法**：按描述符把 819 分组，比较两组带 `set_<Member>` 访问器名的比例。

```
G+S 组显著更高  -> 读法 (a)
两组相近        -> 读法 (b)
```

**先声明限制**：`set_X` 不带类型（R715），一个命中可能属于别的同名类型。
**噪声对两组按名字常见度成比例作用，所以组间比较仍然有效，单行判定无效。**

### 二、结果：两个读法都不成立

```
group     members   has set_      share
G+S           638        360      56.4%
G only        181         81      44.8%
```

**只差 11.6 个百分点。** 若 `Setter` 等于「有 set 访问器」，应当是接近 100% 对接近 0%。

而 **G-only 组 44.8% 的基线本身就说明裸名匹配噪声很大** —— 那 181 个"没有 Setter"的成员里，
接近一半的名字在池里存在 `set_N`，几乎肯定属于别的类型。

**所以 `Setter` 的含义仍是 Unknown。** 两个候选都没被证实，读数太接近，无法排除任何一个。

### 三、处置：把这条线明确关掉

从 R714 到 R717，我在描述符种类上花了四轮：方向分布 → 访问器名 → 三种描述符 → 校准。
**结论是：这个字段现有能力解读不了。**

**已做的更正**：

- `docs/MEMBER_GAP_EVIDENCE.md` 的说明段改为：Getter/Property 是常量、只有 Setter 在变、
  **Setter 含义 Unknown**、本表不再给任何形状建议
- 表头确认是三列（`类型 | 成员 | 原版描述符方向`），没有「该做成什么」
- R712 的正文、R714 的推理、R716 的"方向=双向绑定"猜测，**三次修正后停在 Unknown**

**下一轮换方向**，不再碰描述符种类。

### 四、这条线的结论写清楚（供以后接手的人）

| 证据源 | 能给出 | 不能给出 |
|---|---|---|
| XAML 描述符 | 原版**绑定过**这个类型上的这个成员 | 成员的类型、可写性、行为 |
| `get_`/`set_`/`k__BackingField` 字符串 | 某个同名存在访问器/后备字段 | **归属哪个类型**（名字不带类型） |
| 描述符种类（`Getter`/`Setter`/`Property`） | 只有 Setter 在变（77.9%） | Setter 编码什么 |

**要拿到成员类型，缺的是：AOT `EEType`/`FieldDesc` 解析器，或运行期探针（需登录凭据）。**

### 五、仍然 Unknown

- `Setter` 的语义：**Unknown**，且用现有能力**不可得**（已试两种校准，均无区分力）。
- 42 条未声明成员的类型：**Unknown**（同上）。
- `Property` 100% 出现的成因：**Unknown**（未查，也不影响结论）。
"""

VERDICT = """

---

## 第 717 轮：校准失败，这条线关掉

### 判据与结果

按描述符分两组，比 `set_<Member>` 的出现率：

```
G+S   638 成员 → 56.4% 有 set_
G only 181 成员 → 44.8% 有 set_
```

**只差 11.6 个百分点。** 若 Setter = 「有 set 访问器」，该是 100% 对 0%。**没分开。**

而 G-only 那 44.8% 的基线说明**裸名匹配噪声很大**——那 181 个"没 Setter"的成员里近半数在池里有 `set_N`，
几乎肯定属于别的类型。

### 两个读法都没被证实

- (a) 有 set 访问器：**不支持**
- (b) 双向绑定：**未获支持，也未被证否**（读数太近）

**所以 `Setter` 的含义是 Unknown。**

### 四轮之后的结论（供接手）

| 证据源 | 能给 | 不能给 |
|---|---|---|
| XAML 描述符 | 原版绑定过这个成员 | 类型、可写性、行为 |
| `get_`/`set_`/`k__BackingField` | 同名有访问器 | **归属哪个类型** |
| 描述符种类 | 只有 Setter 在变 | Setter 编码什么 |

**要拿类型，缺 AOT `EEType`/`FieldDesc` 解析器，或运行期探针（需凭据）。**

### 已做的更正

`docs/MEMBER_GAP_EVIDENCE.md` 说明段改为「Setter 含义 Unknown、本表不给形状建议」；
表头确认三列无「该做成什么」。**三次修正后停在 Unknown。**

### 一句话

> 校准的价值在于：它让"我猜的"变成一个可以失败的假设，然后**它失败了**。

> **四轮下来最大的收获不是找到了答案，是确认了这个字段在这套工具下没有答案 ——
> 这样下一轮就不会再有人（包括我）把它当判据用。**

### 下一轮

换方向：不再碰描述符种类。回到能动的——`undeclared` 42 条里，凭**基数/排除法**还能判的还有没有；
或者转向 C7c（行为探针），那是"功能相等"唯一站得住的路。
"""


def main():
    for p, marker, text in ((P1, "R717", BLOCKER), (P3, "R717", BLOCKER), (P2, "第 717 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R717: the Setter calibration failed, so the descriptor-kind line is closed\n\n"
         "Split the 819 by descriptor and compared how often the pool carries set_<Member>:\n"
         "  G+S    638 members -> 56.4%\n"
         "  G only 181 members -> 44.8%\n"
         "An 11.6-point gap. If Setter meant 'declares a setter' the split would be near 100 vs 0, so\n"
         "reading (a) is unsupported; reading (b), two-way binding, is neither supported nor refuted. The\n"
         "44.8% baseline in the G-only group also shows how noisy bare-name matching is.\n\n"
         "Four rounds on descriptor kinds (direction, accessor names, three kinds, calibration) end with:\n"
         "the field cannot be read with the tools available. MEMBER_GAP_EVIDENCE.md now states that Setter's\n"
         "meaning is Unknown and gives no shape advice; its header is confirmed at three columns.\n\n"
         "What would unlock member types: an AOT EEType/FieldDesc parser, or a runtime probe needing\n"
         "credentials. Next round moves off this line."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
