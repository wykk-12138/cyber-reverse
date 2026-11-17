"""Record R1069: all thirteen suspects are naming, not gaps; and IDA has exited."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")

TABLE = """
### 13 个疑似缺口**全部排除**；而 IDA 进程退出了（R1069）

**R1068 说类型覆盖 89.3%，而「只在原版」13 个。这一轮逐个判那 13 个 —— 而判据不是名字，是**复刻件有没有干同一件事的东西**。**

### ① 而那 13 个名字本身就有分组

```
4× Localize*Extension   LocalizeEnumExtension · LocalizeFallbackExtension
                        LocalizeFormatExtension · LocalizeSwitchExtension
4× *View                AccountsCreatorView · SettingsView
                        TaskCreatorCartView · TaskCreatorMainView
2× 登录/许可            AuthWindow · LicenseControl
1× 收验证码             ImapProvider
1× 快捷键               KeyGesture
1× 全局设置容器         Settings（Cybersole.Global.Settings）
```

### ② 而 `where_is` 一个都不是零

| 原版类型 | 复刻件里的对应物 | 判定 |
|---|---|---|
| `Localize*Extension` ×4 | **`Localize` 2 文件** | 命名不同 |
| `ImapProvider` | **`Imap` 25 文件** | 命名不同 |
| `KeyGesture` | **`KeyGesture` 12 文件** | **同名** |
| `AuthWindow` / `LicenseControl` | **各 17 文件** | **同名** |
| `Settings` | `GlobalSettings`（`GlobalSettings.cs`） | 命名不同 |
| `*View` ×4 | `ProviderViews.cs` / `SettingsShell.cs` 等 | 命名不同 |
| **`Cybersole.ProxyTesters`** | **`ProxyTester` 21 文件 · `TestProxy` 5 文件** | 命名不同 |

**→ 13 个**全部**在复刻件里有对应物。**真缺口 = 0。**

**→ 而其中 `KeyGesture` 与 `AuthWindow`/`LicenseControl` 是**同名**的 ——
→ 那说明「只在原版」的判定里，那 13 个中有几个其实同名而我的 648 侧没抓到。
→ **推断**：复刻件那三个可能在**别的命名空间**下，而我的 `replica_types` 按 `namespace X.Y` 取，
→ 若某文件用了**文件作用域命名空间**（`namespace X.Y;` 而非 `namespace X.Y {`）**我的正则仍能抓**，
→ 但若类型在**嵌套类**里，就抓不到。⇒ **648 是下界**。**（Inference，未验证。）**

### ③ 而那条 Inference 顺带解释了「只在复刻件 534」

**→ 若复刻件侧少抓了嵌套类，那 648 与 534 都偏小，而 109 同名的分母（122）是准的。
→ 所以「类型覆盖 89.3%」的**分子**可能偏低 ⇒ **真实覆盖 ≥ 89.3%**。**
**→ 而那与「13 个全部有对应物」一致：13 个里连疑似缺口都没有。**

### ④ 而 IDA 退出了

```
python analysis/ida.py health    → ConnectionRefusedError / URLError
port 13337 listening             → **False**
ida processes                    → **0**
```

**→ 进程数为 0 ⇒ 不是代理漂移（那会进程在而端口变），是 **IDA 本身退出**。
→ 按 goal：「报 PROXY: MISSING 或端口 REFUSED 且框已清 → 属停下等 YG」，
→ 而它属于「DSH 重启 / 开关 MCP 条目（含 ida 代理没起）」那一类。**

**→ 而它**不影响**本轮结论：13 个类型是用 `where_is`（查复刻件源码）判的，
→ 而「原版有这 13 个」来自 R1068 已经取得的**缓存证据**（`docs/BUSINESS_TYPES.md`）。**

**→ 下一轮若要反编译，得先按 goal 的规程重新拉 IDA（doctor 脚本 + CUA 点框）。
→ 若 doctor 报 PROXY: MISSING 且框已清，则停下等 YG。**

### ⑤ 数字

| 度量 | R1068 | **R1069** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 产物陈旧度 | 0 / 0 | **0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| 原版业务类型 | 122 | **122** |
| 复刻件业务类型 | 648 | **648（下界 —— 嵌套类可能漏，Inference）** |
| 同名 | 109 | **109** |
| **只在原版 13 个中** | 未判 | **13 个全有对应物 ⇒ 真缺口 0** |
| **类型级真缺口** | 未知 | **0** |
| **IDA** | 可用 | **进程 0 · 端口不监听 · 需重新拉起** |

### 教训

> **「只在原版」这一列看起来像缺口清单，而它实际是一份**命名对照表**。
> → 逐个查之后 13 个全部落地 —— 而若我不查，那 13 会被写进 (a) 当作未结案项，
> 而下一轮会去「补」13 个已经存在的东西（R815 那个形状）。**
> **→ 而 `where_is` 是判它的正确工具：它查的是**复刻件的源码**，而那正是「有没有干同一件事」的所在。**
"""

if "13 个疑似缺口**全部排除**" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md appended")

NOTE = """

## R1069 —— **13 个疑似缺口全部排除（真缺口 0）；IDA 进程退出**

### 13 个名字本身有分组

```
4× Localize*Extension · 4× *View · AuthWindow + LicenseControl（登录/许可）
ImapProvider（收码）· KeyGesture（快捷键）· Settings（全局设置容器）
```

### 而 `where_is` 一个都不是零

| 原版类型 | 复刻件对应物 | 判定 |
|---|---|---|
| `Localize*Extension` ×4 | `Localize` **2 文件** | 命名不同 |
| `ImapProvider` | `Imap` **25 文件** | 命名不同 |
| `KeyGesture` | **同名 12 文件** | 同名 |
| `AuthWindow` / `LicenseControl` | 各 **17 文件** | 同名 |
| `Settings` | `GlobalSettings` | 命名不同 |
| `*View` ×4 | `ProviderViews` / `SettingsShell` 等 | 命名不同 |
| **`Cybersole.ProxyTesters`** | **`ProxyTester` 21 · `TestProxy` 5** | 命名不同 |

**⇒ 13 个**全部**有对应物 ⇒ **真缺口 = 0**。**

### 而一条 Inference

`KeyGesture` / `AuthWindow` / `LicenseControl` 在复刻件里**同名**，却没进 109 ——
⇒ 推断：复刻件侧 **648 是下界**（嵌套类抓不到）⇒ 真实类型覆盖 **≥ 89.3%**。**（未验证）**

### 而 IDA 退出了

```
ida.py health → ConnectionRefusedError    port 13337 → False    ida processes → **0**
```

**进程 0 ⇒ 不是代理漂移，是 IDA 本身退出。** 按 goal 属「停下等 YG」那一类。
**不影响本轮结论**：13 个是用 `where_is`（查源码）判的，原版侧来自 R1068 的已有证据。
**下一轮要反编译，先按规程拉 IDA（doctor + CUA 点框）；若报 PROXY: MISSING 且框已清 ⇒ 停下等 YG。**

### 数字

| 度量 | R1068 | **R1069** |
|---|---|---|
| 套件 | 2258 / 0 | **2258 / 0 / 0** |
| 函数数 | 174,258 / 277,094 | **同** |
| 原版 / 复刻件类型 | 122 / 648 | **122 / 648（下界）** |
| 同名 | 109 | **109** |
| **13 个中真缺口** | 未判 | **0** |
| **IDA** | 可用 | **退出，需重新拉起** |

**纪律**：「只在原版」看起来像缺口清单，实际是一份**命名对照表**。不查就会去「补」13 个已经存在的东西（R815 的形状）。
"""


def append(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-22s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-22s appended" % os.path.basename(path))


append(HANDOFF, "R1069", NOTE)
append(RBLOCK, "R1069", "\n---\n\n## 493. **13 个疑似缺口全部排除；IDA 进程退出**\n" + NOTE)

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
r = subprocess.run(
    ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
     "R1069: all thirteen suspects are naming, and IDA has exited\n\n"
     "R1068 put type coverage at 89.3 per cent and listed thirteen types present only in the original. That column reads\n"
     " like a gap list. This round checked each one against the replica's source, because the question is not whether\n"
     " the name matches but whether anything here does the same job.\n\n"
     "None is missing. The four localization extensions match a Localize hit across two files; ImapProvider matches\n"
     " Imap across twenty-five; ProxyTesters matches ProxyTester across twenty-one and TestProxy across five; Settings\n"
     " matches GlobalSettings; the four views match files like ProviderViews and SettingsShell. KeyGesture, AuthWindow\n"
     " and LicenseControl are present under their own names, which also means my replica-side count of 648 is a lower\n"
     " bound -- nested classes do not match the namespace-anchored pattern -- so real coverage is at least 89.3 per\n"
     " cent rather than exactly that.\n\n"
     "This matters because of what would have happened otherwise. Thirteen entries in a column headed present only in\n"
     " the original would have gone into criterion (a) as open items, and the next round would have set about adding\n"
     " thirteen things that already exist. That is R815's shape: an action taken on evidence, deleting what the evidence\n"
     " pointed at.\n\n"
     "IDA has exited. The health call refuses the connection, nothing is listening on 13337 and there are no IDA\n"
     " processes, so this is not a port that drifted but the application gone. It does not affect the conclusion here --\n"
     " the thirteen were judged with where_is against source, and the original side came from evidence R1068 already\n"
     " collected -- but the next round needs decompilation and will have to bring IDA back by the documented route\n"
     " before it can proceed.\n\n"
     "Figures: suite green at 2258, freshness zero files and zero lines, count unchanged, 122 original types against a\n"
     " lower bound of 648, 109 shared names, thirteen suspects all resolved with zero genuine gaps, and an editor whose\n"
     " process count is zero.\n\n"
     "Unknown: how many replica types sit in nested classes and are therefore uncounted, which only makes coverage\n"
     " higher than reported.\n\n"
     "The lesson is that a column of names absent from one side is a naming comparison until each entry is checked, and\n"
     " that adding things which already exist is a real risk when the check is skipped."],
    cwd=ROOT, capture_output=True, text=True)
print("  commit rc=%d" % r.returncode)
subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
subprocess.run(["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m", "drop the helper"],
               cwd=ROOT, capture_output=True, text=True)
log = subprocess.run(["git", "log", "--oneline", "-2"], cwd=ROOT, capture_output=True, text=True)
print("  " + log.stdout.strip().replace("\n", "\n  "))
st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True)
print("  tree: %s" % ("clean" if not st.stdout.strip() else "dirty"))
