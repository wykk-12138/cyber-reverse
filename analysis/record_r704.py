"""Record R704/R705: both blockers resolved; the copy gap closed by implementing, not by reinterpreting."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 135. 两条卡口**都解了** —— (a) 按裁决结案，(b) 靠**实现**把文案缺口降到 0

> R704/R705。新增 `ProfileValidationLists.cs`、`ProfileValidation.en.json`、`ProfileValidationListsTests.cs`；
> 改 `ProfileViews.cs`、`Cybersole.Core.csproj`、`PARITY.md`、`ProfileCsvCopyTests.cs`。

### 一、(a)：`UNIMPLEMENTED = 0`

YG 裁决（2026-11-16）：登录凭证类功能属用户管理，**不在复刻范围**（`docs/DECISION_LICENSE_OUT_OF_SCOPE.md`）。
triage 据此把 `AuthWindow` / `LicenseControl` 判为 `OUT_OF_SCOPE`：

```
OUT_OF_SCOPE=2, RENAMED=7, STRUCTURAL=1, UNKNOWN(non-discriminative)=6, UNKNOWN(non-discriminating match)=1
```

**17 条合计不变，但 `UNIMPLEMENTED` 归零**，每条都有判定与依据。判据 (a) 的括号允许「不可得 → Unknown + 缺什么」，
范围外条目由**裁决本身**支撑（authority 最高级）。

### 二、(b)：文案缺口 **2 → 0**，靠实现而非改判据

`copy_audit_report.py` 的 `_satisfied` 是「值出现在源码 **或** 键出现在代码（注释剥离）」。此前两条键只存在于
文案表里没有任何代码引用 —— 所以实现校验就会让它们变成 satisfied。**这是唯一诚实的路**：让文案可达，而不是把判据读宽。

四维规则来自 R702 的反编译 + R703 的复验（我从原始字节算出 `lea rdx,[rip+0x05ed5dbe]` → `0x146E4D160`，
并重解 `sub_140F77350` / `sub_140F777E0`）：

| 维度 | 规则 |
|---|---|
| 何时 | 列定义时注册守卫，每行求值（不是导入时一次性） |
| 归一化 | **只 Trim**，没有 ToLower |
| 大小写 | 比较本身大小写不敏感；**不展开缩写，也不是前缀匹配** |
| 按什么 | 国家查**当前 locale 的 country 表**；州表**挂在国家行上**（`[+96]`），无表则**静默放行** |

### 三、数据不是猜的：从原版导出

`analysis/export_profile_lists.py` 用已验证的格式读取器导出：

```
country 244   state 50   state_abbr 50   缩写/州名对齐异常 0
```

判据先定：条数须与 R688 实测一致（244/50/50）。**满足。**

### 四、我在这一轮里犯的三个错（都自己抓回来了）

| # | 错 | 怎么发现的 | 修法 |
|---|---|---|---|
| 1 | 数据文件放在 `Locales/` 下 | `EveryLocaleDictionaryHasTheSameKeyCount` 红 —— 它数该目录所有 `*.json` | **移动**到 `Data/`，**不缩小守卫范围** |
| 2 | `state_owner` 写 `United States` | 州表取不到、3 条断言红 | 表里真实拼写是 **`United States of America`** |
| 3 | **测试断言了前缀匹配** | 实现正确地拒绝了 `"united states"` | **改测试**，并把「不是前缀匹配」写成显式断言 |

**第 3 条最值得记**：我把「大小写/空白不敏感」与「前缀匹配」混成一件事。
**实现是对的，测试是错的** —— 这与"数字对不上就改数字"是同一种危险，方向相反。

### 五、两个计数守卫的更新（写明原因，不放宽断言）

| 守卫 | 旧 | 新 | 原因 |
|---|---|---|---|
| `ProfileCsvCopyTests` | 40 | **42** | 两条校验文案现在有代码引用 |
| `PARITY.md` 内嵌资源 | 19 | **20** | 多了 `Data/ProfileValidation.en.json` |

### 六、验证

```
名字级 4 / 类型级 0 / 类型缺失 17 / 形状 80 / 文案 0
完整套件  1624 通过 / 0 失败 / 0 跳过      ← 1619 + 5 条新行为测试
ProfileValidationListsTests  5/5 通过
```

### 七、仍然 Unknown

- 触发时机的细节（逐行 vs 逐单元格提交）：**Unknown**（证据到"列定义时注册"为止，R702 §3.4 已声明）。
- `[+96]`/`[+72]` 对应哪个托管字段名：**Unknown**（只认代码这么取）。
- 其它 locale 的州表（德 16 / 奥 9 / 阿 22）复刻件尚未导出：**Unknown**（英语那份是当前路径）。
"""

VERDICT = """

---

## 第 704/705 轮：两条卡口都解了

### (a) `UNIMPLEMENTED = 0`

YG 裁决登录凭证功能不在范围 → `AuthWindow`/`LicenseControl` 判 `OUT_OF_SCOPE`，17 条合计不变、真缺归零。

### (b) 文案缺口 **2 → 0**，靠**实现**

四条规则全有反编译依据（R702 解出、R703 我从原始字节复验）：

```
何时：列定义时注册守卫，每行求值
归一化：只 Trim
比较：大小写不敏感；不展开缩写，也不是前缀匹配
范围：国家查当前 locale 表；州表挂在国家行（[+96]），无表则静默放行
```

数据从原版导出（`country 244 / state 50 / abbr 50`，对齐异常 0），判据要求与 R688 实测一致 ✓。

### 我这轮错了三次

1. 数据文件放 `Locales/` → 撞 locale 键数守卫 → **移到 `Data/`，不缩小守卫**
2. `state_owner` 写 `United States` → 表里是 `United States of America`
3. **测试断言了前缀匹配** → 实现是对的，测试是错的

> **第 3 条与"数字对不上就改数字"是同一种危险，只是方向相反：
> 那次是把工具改到符合期望，这次是把期望当成了实现。**

### 收尾

```
名字级 4 / 类型级 0 / 类型缺失 17 / 形状 80 / 文案 0
完整套件 1624 通过 / 0 失败
```

### 下一轮

重跑 `docs/COMPLETION_AUDIT.md`：(a)(b) 现在都该翻成满足。**这是本 session 第一次能让目标接近达成。**
"""


def main():
    for p, marker, text in ((P1, "R704/R705", BLOCKER), (P3, "R704/R705", BLOCKER), (P2, "第 704/705 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R704/R705: both blockers resolved -- (a) by ruling, (b) by implementing the validation\n\n"
         "(a) UNIMPLEMENTED is 0: YG ruled login-credential features out of scope, so AuthWindow and\n"
         "LicenseControl are OUT_OF_SCOPE. 17 types, every one with a verdict and its authority.\n\n"
         "(b) copy gaps 2 -> 0. Not by reading the criterion wider: copy_audit's predicate accepts a key\n"
         "that appears in code, so the two messages needed something that emits them. The rule came from\n"
         "R702's decompilation, re-verified at R703 from raw bytes (lea rdx,[rip+0x05ed5dbe] -> 0x146E4D160)\n"
         "and by re-decompiling both guards.\n\n"
         "Data exported from the original: 244 countries / 50 states / 50 abbreviations, 0 alignment\n"
         "anomalies. Four rules: trim only; case-insensitive; no abbreviation expansion and no prefix\n"
         "match; state list hangs off the country row and a country without one accepts anything.\n\n"
         "Three mistakes of mine fixed during the round: data file landed in Locales/ and tripped the\n"
         "locale key-count guard (moved it instead of narrowing the guard); state_owner spelled 'United\n"
         "States' when the list says 'United States of America'; and a test of mine asserted prefix\n"
         "matching, which the implementation correctly does not do -- the test was wrong, not the code.\n\n"
         "Suite 1624 passed / 0 failed (+5 behaviour tests); metrics 4/0/17/80/0."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
