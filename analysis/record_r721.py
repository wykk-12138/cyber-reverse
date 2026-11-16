"""Record R721: the app-string set is UI wiring, and probing it is blocked on attribution."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 150. 239 条以 UI 接线为主；探针它们卡在**属性名归属**上，这条路关掉

> R721。新增 `analysis/classify_app_functions.py`、`analysis/format_string_functions.py`。

### 一、抽样六条，全是属性赋值

400–1500 字节档抽 6 个，反编译后共同形态是 55–68 行、几乎全为 `sub_143028xx(属性描述符, 值)`：

```c
sub_1405AAA60:
  v2 = sub_143028C10(&unk_144BBB928);
  sub_143028E70(v2 + 16, a1);
  v3 = sub_142E76200(&off_1449271C0, *(_QWORD *)(a1 + 536));
  ...
```

**那是 UI 状态刷新**：把字段写进控件的绑定属性。**是应用代码，但"行为"是"给对象 O 的属性 P 赋值"。**

### 二、我的自动分类器失败了，记下来

我写了个 wiring/logic 分类器（按被调函数前缀）。**它把六个全判成 `logic`** ——
因为前缀表漏了 `off_14492xxxx` 那一家族，而那正是**属性描述符对象**。

**又一次：判据写得像判据，实际不判别。** 已记录，不修正（它证明的是"前缀法不行"，留着比删掉有用）。

### 三、换信号：格式化字符串 → 太稀

若一个函数加载带 `{0}` 的文案，它就**格式化一条消息**，输出可断言、不需要知道任何类型。

```
带占位符的 locale 条目: 114 / 1142
IDA 能定位到的格式串    : 3      ← 只有 3 条
解析到它们的 lea 站点    : 4
映射到的函数            : 0
```

**0 个函数。** 原因：那 3 条字符串的 `lea` 站点没落在已识别函数里，或不是独立冻结对象（R715 同类）。

**这条路太稀，不成规模。**

### 四、所以卡在哪（说清楚缺什么）

探针这 239 条 UI 函数，需要**知道"哪个属性"**才能断言"跑完后它等于什么"。
而属性名归属正是 R715 证明的封锁点：

- 描述符里的 `!Getter/!Setter/!Property` 不给类型（R716/R717）
- `get_X`/`set_X` 字符串不带类型、名字在多个类型上重复（`Name` 37 个类型）
- 代码里没有地址引用可追（七个探针全 0）

**缺的是同一件东西：AOT 元数据的字段/属性归属解析。**

### 五、这一轮的判断

> 我连续两轮在"选探针目标"上：R719 判据错（选胶水），R720 判据对但**选出来的东西不是我能探的**。

**R720 的 239 条没有错** —— 它们确实是应用代码。**错在我默认"应用代码"等于"可探行为"。**
UI 接线的行为是属性赋值，而属性名归属不可得。

**这不是把 R720 撤回，是把它的适用范围收窄**：它是"应用程序的清单"，不是"行为探针的候选清单"。

### 六、C7c 的下一步换思路

不再从原版挑函数，改从**复刻件已有的 1639 条测试**里审：
**哪些断言的行为是从反编译推出来的，哪些是从实现推出来的。**

后者只能证明"实现等于自己"。**把前者数出来，才是 C7c 真正能拿出的证据量。**
R718 那一批（15 条）就是前者的样板。

### 七、仍然 Unknown

- 239 条里 UI 接线与业务逻辑的真实比例：**Unknown**（分类器失败，只抽了 6 条）。
- 114 条格式化文案里其余 111 条为何定位不到：**Unknown**（R715 同类，打包 blob）。
- 那 4 个 `lea` 站点为什么不在任何函数里：**Unknown**（未查）。
"""

VERDICT = """

---

## 第 721 轮：判据对，但选出来的东西不是我能探的

### 抽样六条：全是属性赋值

400–1500 字节档抽 6 个，共同形态 55–68 行、几乎全为 `sub_143028xx(属性描述符, 值)`：

```c
v2 = sub_143028C10(&unk_144BBB928);
sub_143028E70(v2 + 16, a1);
```

**UI 状态刷新。是应用代码，但"行为"是"给属性赋值"。**

### 我的分类器失败了

按被调函数前缀分 wiring/logic，**六个全判成 logic** —— 前缀表漏了 `off_14492xxxx` 那家族（属性描述符）。
**又一次：判据写得像判据，实际不判别。** 留着不删，它证明的是"前缀法不行"。

### 格式化字符串这个信号太稀

```
带占位符的条目 114 / 1142 → 定位到 3 条 → 4 个 lea 站点 → 0 个函数
```

**0 个函数。不成规模。**

### 卡在哪

探针 UI 函数要断言"跑完后属性 P 等于什么"，**而属性名归属是 R715 证明的封锁点**（描述符不给类型、
访问器名不带类型、代码无地址引用）。**缺的是同一件东西：AOT 元数据的属性归属解析。**

### R720 的 239 条没错，是我的默认错了

它们确实是应用代码。**错在我默认"应用代码"等于"可探行为"。**

> **这不是撤回 R720，是收窄它的适用范围：它是「应用程序的清单」，不是「行为探针候选的清单」。**

### 一句话

> 两轮连着：R719 判据错（选胶水），R720 判据对但**选出来的不是我能探的**。

> **找到"是应用代码"的判据之后，我才发现我真正需要的是"是可断言行为"的判据 —— 而这两个不是一回事。**

### 下一轮

换方向：不从原版挑，从**复刻件已有 1639 条测试**里审 —— 哪些断言的期望值来自反编译，哪些来自实现。
**后者只证明"实现等于自己"。把前者数出来，才是 C7c 能拿出的证据量。** R718 那 15 条是样板。
"""


def main():
    for p, marker, text in ((P1, "R721", BLOCKER), (P3, "R721", BLOCKER), (P2, "第 721 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R721: the 239 app-string functions are UI wiring, and probing them is blocked on attribution\n\n"
         "Six samples from the 400-1500 byte band are all 55-68 line functions whose bodies are\n"
         "sub_143028xx(property descriptor, value) sequences -- UI state refresh. App code, but its\n"
         "behaviour is 'assign property P on object O', which cannot be asserted without knowing P.\n\n"
         "My automated wiring/logic classifier called all six 'logic': its prefix list missed the\n"
         "off_14492xxxx family, which is exactly the property-descriptor objects. Kept as the record that\n"
         "a prefix test is not a discriminator.\n\n"
         "The format-string signal is too sparse to replace it: 114 locale entries carry a placeholder,\n"
         "three were located, four lea sites, zero functions mapped.\n\n"
         "So R720's 239 are genuinely app code; what was wrong was assuming app code means assertable\n"
         "behaviour. The set is a map of the app, not a list of probe candidates. What is missing is the\n"
         "same thing each time: AOT metadata attribution for properties and fields."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
