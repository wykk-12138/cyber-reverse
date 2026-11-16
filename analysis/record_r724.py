"""Record R724: a fourth evidence class the audit was blind to -- the original's own data files."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 153. 第四类证据：**原版自己的磁盘数据** —— 我的审计一直看不见它

> R724。扩 `analysis/test_provenance.py` 的标记集；重生成 `docs/TEST_PROVENANCE.md`。

### 一、怎么发现的

按计划挑一个文件逐条审，选中 `KeyBindMatcherTests.cs`（11 条全无来源）。它的类注释写着：

> **Round 116** found the two schemes had been mixed: the matcher produced Win32 codes (A = 65, F1 = 112)
> while **`settings.json` from the live build** carried Avalonia values (**A = 44, F1 = 90**).

**`A = 44` 这个断言值，来自 `%APPDATA%\\Cybersole\\settings.json`** —— 原版实际写出来的文件。

**那不是"从反编译推的"，是"原版自己输出的"** —— **比反编译更硬**。而我的标记集一个都不认。

### 二、这不是第一次漏

| 轮 | 漏了什么 | 后果 |
|---|---|---|
| R722 | `sub_14XXXXXX` 写法 | R718 自己那 15 条一条没数到 |
| R722 | `[InlineData]` 隔开文档块 | 所有 Theory 的类注释丢失 |
| R723 | 池中文案（locale-derived） | 130 条被算成"无来源" |
| **R724** | **原版磁盘数据（live build / settings.json）** | 又一批被算成"无来源" |

**四次都是同一件事：我在用"我想到的标记"去量"我没想到的来源"。**

### 三、补上标记之后

```
测试方法总数       1553
  binary (direct)     91  ( 5.9%)   ← 83 → 91
  binary (inherited) 475  (30.6%)   ← 419 → 475
  unaccounted       1078  (69.4%)   ← 1134 → 1078
```

按 inherited 排序的前列：

```
PageCopyTests.cs            16 / 16     AccountSelectionTests.cs   12 / 12
KeyBindMatcherTests.cs      11 / 11     StoreFlowStepsTests.cs     11 / 11
SurfaceRuntimeTests.cs      10 / 10     LiveSchemaPinsTests.cs     10 / 10
ServiceHostTests.cs         10 / 10
```

**90 个文件是"每一条方法都有来源"**（占 329 个文件的 27%）。

### 四、四类证据的强弱（这张表现在能说清了）

| 类 | 例子 | 强度 |
|---|---|---|
| **原版磁盘数据** | `settings.json` 里的 `A=44` | **最强** —— 原版实际输出 |
| 反编译 | `sub_141CFA390` 的 Trim 语义 | 强，但依赖我的读法 |
| 池中文案 | `Unknown country` 逐字存在 | 中，只证明文字存在 |
| 复述实现 | `Assert.Equal(x, Foo(x))` | **零** —— 永远绿 |

### 五、仍然 Unknown

- 1078 条里还有多少用了别的原版来源（`%LOCALAPPDATA%` 的东西、网络抓包、运行时观察）：**Unknown** ——
  **这已经是第四次证明"我的标记集不完整"，所以 69.4% 只能当下界**。
- 475 条里有多少真读对了：**Unknown**（无对拍）。
- 「原版磁盘数据」这一类共影响多少条：**Unknown**（未单独计数，混在 475 里）。

### 六、这一轮的判断

> **我第四次用不完整的尺子量出一个"低"数字，然后把它当成发现。**

**这不是谨慎，这是有系统偏差的谨慎。** 每次补完标记集，数字都往上涨，而我从没先问"我漏了哪一类来源"。

**下一轮做的是这件事**：先把「原版能提供的证据种类」列全（磁盘数据 / 反编译 / 字符串池 / 运行时 / 抓包），
**再**去数，而不是先数再补。
"""

VERDICT = """

---

## 第 724 轮：第四类证据 —— 原版自己的磁盘数据

### 怎么发现的

挑 `KeyBindMatcherTests.cs` 逐条审，类注释写着：

> matcher 产出 Win32 码（A=65, F1=112），而 **`settings.json` from the live build** 是 Avalonia 值（**A=44, F1=90**）

**`A = 44` 来自 `%APPDATA%\\Cybersole\\settings.json` —— 原版实际写出的文件。**
**那不是"从反编译推的"，是"原版自己输出的"，比反编译更硬。** 而我的标记集不认。

### 第四次漏

| 轮 | 漏了什么 |
|---|---|
| R722 | `sub_14XXXXXX` 写法 → R718 那 15 条一条没数到 |
| R722 | `[InlineData]` 隔开文档块 → 所有 Theory 的类注释丢失 |
| R723 | 池中文案 → 130 条算成"无来源" |
| **R724** | **原版磁盘数据** → 又一批 |

**四次都是同一件事：用"我想到的标记"去量"我没想到的来源"。**

### 补上之后

```
direct      91  ( 5.9%)   ← 83
inherited  475  (30.6%)   ← 419
unaccounted 1078 (69.4%)
90 个文件"每条方法都有来源"（329 个文件的 27%）
```

### 四类证据的强弱

| 类 | 强度 |
|---|---|
| **原版磁盘数据** | **最强** —— 原版实际输出 |
| 反编译 | 强，依赖我的读法 |
| 池中文案 | 中，只证明文字存在 |
| 复述实现 | **零**，永远绿 |

### 一句话

> **我第四次用不完整的尺子量出一个「低」数字，然后把它当成发现。**

> 这不是谨慎，**是有系统偏差的谨慎**。每次补完标记集数字都往上涨，而我从没先问「我漏了哪一类来源」。

### 下一轮

**先列全「原版能提供的证据种类」**（磁盘数据 / 反编译 / 字符串池 / 运行时 / 抓包），**再**去数 —— 而不是先数再补。
"""


def main():
    for p, marker, text in ((P1, "R724", BLOCKER), (P3, "R724", BLOCKER), (P2, "第 724 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R724: a fourth evidence class the audit could not see -- the original's own on-disk data\n\n"
         "Auditing KeyBindMatcherTests.cs turned up a class comment naming 'settings.json from the live\n"
         "build' as the source of A=44, F1=90. That is %APPDATA%\\Cybersole\\settings.json: what the shipped\n"
         "program actually wrote, which is stronger evidence than decompilation, and none of my markers\n"
         "recognised it.\n\n"
         "That is the fourth blind spot in a row:\n"
         "  R722  sub_14XXXXXX spelling        -> R718's own fifteen probes were invisible\n"
         "  R722  [InlineData] before the doc   -> every Theory's class comment was lost\n"
         "  R723  pool text (locale-derived)    -> 130 tests misfiled as sourceless\n"
         "  R724  on-disk data (live build)     -> another batch misfiled\n\n"
         "After extending the markers: direct 91 (5.9%), inherited 475 (30.6%), unaccounted 1078 (69.4%);\n"
         "90 of 329 files now have a source for every method.\n\n"
         "Each correction moved the number up, and I never once asked which evidence classes I had left\n"
         "out before counting. That is not caution, it is caution with a systematic bias. Next round: list\n"
         "the evidence classes the original can offer -- disk data, decompilation, string pool, runtime,\n"
         "capture -- and only then count."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))


if __name__ == "__main__":
    main()
