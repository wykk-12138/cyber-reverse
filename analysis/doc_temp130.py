import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## `%TEMP%\\cyb-chromium-*` 是谁造的：不是原版（第 130 轮补充）

YG 在 `%TEMP%` 看到 **115 个 `cyb-chromium-<8位hex>`** 和 **14 个 `cyb-missing-<32位hex>`**，
问是不是反编译里看不懂的代码来自这里。查清了：**是 replica 自己造的，不是原版。**

| 目录 | 制造者 |
|---|---|
| `cyb-chromium-<8 hex>` | `ChromiumBridge.cs:56` —— `"cyb-chromium-" + Guid.NewGuid().ToString("N")[..8]` |
| `cyb-missing-<32 hex>/h.json` | `CheckoutHistoryTests` 传入一个**不存在目录**下的 `h.json`，而 `CheckoutStats.Flush()` 在 `Dispose` 时**建目录并写入 `[]`** |

原版把浏览器 profile 放在**它自己的数据目录**里，不会用 `cyb-` 前缀。

### 但这条线索抓出了三个真问题

**① `CheckoutStats.Flush()` 有副作用**：空历史 + 文件不存在时仍然建目录、写 `[]`。
一次「打开设置页看一眼」也会落地一个目录；在只读安装上则变成被 `catch` 吞掉的异常。
现在：`_events.Count == 0 && !File.Exists(...)` 直接返回，测试断言**目录不存在**。

**② 1.8 GB 临时垃圾**：129 个目录，`tools/clean-temp.ps1` 已清掉（C: 可用空间随之大涨）。

**③ 一份被遗弃的「变异」**：`ChromiumBridge.cs` 里留着
`var fullVersion = "131.0.0.0";  // MUTATED` —— 那是 `mutation-check.py` 被中途杀掉时留下的。
它让 `UserAgentConsistencyTests` 一直红，而我差点把它当成新回归去查。
现在 `mutation-check.py` **每轮开始先自修复**：变异前把原文件存到 `tools/.mutation-backup/`，
下轮启动时发现文件里还有 `MUTATED` 就从备份还原。

> **一个被杀掉的检查，会留下它正在检查的那个错误。** 这比它自身的失败更难发现。

### 顺带修的一个资源问题

清理后全量重建暴露：`Cybersole.Core.csproj` 里 `Cybersole.Locales.ja.json` **缺
`WithCulture="false"`**，于是它被当成 `ja` 卫星程序集，主程序集只剩 3 个资源字典
（`LocaleDictionaryTests` 期望 4）。补上即绿 —— 正是该 csproj 注释里警告过的那个坑。
'''

if "## `%TEMP%\\cyb-chromium-*` 是谁造的" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("temp-artifact section documented")
else:
    print("already present")
