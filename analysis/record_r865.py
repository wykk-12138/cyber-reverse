"""Record R865: rea has no native provider configured, and the missing one is an env var."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### `rea` 的 native provider 一个都没配 —— C7c 那条路卡在配置（R865）

**`mcp__rea__binary_session`：**

| provider | 状态 | 缺什么 |
|---|---|---|
| ghidra | `not_configured` | `GHIDRA_INSTALL_DIR`（Ghidra 12.x） |
| hopper | `unsupported_host` | win32 不支持 |
| **ida** | **`not_configured`** | **`REA_IDA_MCP_CONFIG` 指到 IDA MCP 注册** |
| kuna | `not_configured` | `REA_KUNA_COMMAND` |

**而 `match_native_functions` 要的两侧 `list_procedures` Evidence，只能由 native provider 产出。**

**所以 R864 说的「没试过第二套工具」，落到实处的答案是：工具在，provider 不在。**

### 而缺的那个刚好是我已经有的

**`ida` 那个 provider 只缺 `REA_IDA_MCP_CONFIG` —— 一个指向 IDA MCP 注册的配置。
而本会话的 IDA MCP 一直是通的（`analysis/ida.py` 直连 13337，`str` / `py` / `xrefs` 都在用）。**

**所以配它不需要装东西，只需要：**

1. **写一个 IDA MCP 注册 JSON**（指向 13337）
2. **设 `REA_IDA_MCP_CONFIG` 为它的路径**
3. **重启 REA**

**第 3 步是硬门槛 —— 而「DSH 重启 / 开关 MCP 条目」是 goal 允许停下来等 YG 的两件事之一。**

### 所以 C7c 的完整状态

| 层 | 状态 |
|---|---|
| 工具存在（`match_native_functions` / `compare_functions`） | **是** |
| 工具需要的 provider | **未配（ida 只缺一个环境变量）** |
| 配它要不要停 | **要 —— 重启 REA 属于允许停等 YG 的条目** |
| 配了之后能不能配出足够多函数 | **Unknown**（两侧是不同 AOT 框架） |
"""

if "rea` 的 native provider 一个都没配（R865" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: provider gap appended")

BLOCKER = """

---

## 289. C7c 那条路卡在**配置** —— 而缺的那个 provider 只差一个环境变量

> R865。未改产品代码。**R864 说「没试过第二套工具」；这一轮查清了为什么没试成。**

### 一、`rea` 的四个 native provider 全不可用

| provider | 状态 | 缺什么 |
|---|---|---|
| ghidra | `not_configured` | `GHIDRA_INSTALL_DIR`（Ghidra 12.x） |
| hopper | `unsupported_host` | win32 不支持 |
| **ida** | **`not_configured`** | **`REA_IDA_MCP_CONFIG`** |
| kuna | `not_configured` | `REA_KUNA_COMMAND` |

**而 `match_native_functions` 要的两侧 `list_procedures` Evidence 只能由 native provider 产出。
所以工具在、provider 不在 —— 这是 R864 那条路的准确状态。**

### 二、而缺的那个刚好是我已经有的

**`ida` provider 只缺 `REA_IDA_MCP_CONFIG`：一个指向 IDA MCP 注册 JSON 的路径。**

**而本会话的 IDA MCP 一直是通的** —— `analysis/ida.py` 直连 13337，`str` / `py` / `xrefs` 这几十轮都在用。

**所以配它不需要装任何东西，只需要三步：**

1. 写一个 IDA MCP 注册 JSON（指向 13337）
2. 设 `REA_IDA_MCP_CONFIG` 为它的路径
3. **重启 REA**

**第 3 步是硬门槛。而「DSH 重启 / 开关 MCP 条目」正是 goal 允许停下来等 YG 的两件事之一。**

### 三、所以要停一下

**这不是我能自己推的 —— 它需要动 MCP 条目（`rea` 的环境变量）并重启。**

**而且值得说明的是：这一步的收益不确定。**

| 已知 | Unknown |
|---|---|
| 工具存在且对口（按字节/CFG 指纹配对，前提就是没符号） | **两侧是不同 AOT 框架（.NET 10 ↔ .NET 8），字节相同的函数可能很少** |
| 配 provider 只需要一个环境变量 | **配上之后能不能配足够多的函数，未知** |

**所以这是一个「花一次重启，换一个不确定的收益」的决定。**
**而另一个选项是不动它，按现有优先级做核心，C7c 保持 unknown 并写清理由。**

### 四、这一轮的实际产出

**把「没试过第二套工具」这句话，落成一张可执行的三步清单 + 一个明确的代价。**

**这比「这条路易堵」有用得多 —— 它是**要做，就做这三件事**。**

### 五、验证

```
mcp__rea__binary_session（detail=summary）
  analysis_provider_candidates:
    ghidra  unavailable / not_configured / GHIDRA_INSTALL_DIR
    hopper  unavailable / unsupported_host（win32）
    ida     unavailable / not_configured / REA_IDA_MCP_CONFIG
    kuna    unavailable / not_configured / REA_KUNA_COMMAND
  tool_availability: match_native_functions / compare_functions 在「available: true」那组（MCP 层可用）
                     而 list_procedures 在 target_required 那组（要 open_binary）
本轮未改产品代码
七项度量沿用
```

### 六、仍然 Unknown

- **配好 ida provider 后 `match_native_functions` 能配出多少对**：**Unknown** ——
  **如果很少，这条路依然不通，但至少那时是「试过且知道结果」。**
- **有没有更省的路**：**Unknown** ——
  **比如只对少数几个关键函数做字节比对（不用 REA，直接 `read_bytes` 两侧对比）。**
  **这条路不需要 provider，但只适用于「两侧函数能先按名字对上」的情形 —— 而那正是 C7c 说做不到的事。**
- **`REA_IDA_MCP_CONFIG` 的 JSON 格式**：**Unknown** —— 要先读 `docs/providers/ida-provider.md`。

### 七、教训

**R864 我写「工具存在、没试过」。这一轮一查：工具存在，**但它依赖的东西不存在**。**

**「有个工具能做这件事」和「这个工具在这台机器上能用」是两句话。**
**而我上一轮把第一句当成了第二句 —— 并且因此把 C7c 从「可能到头了」改判成「没试过」。**

**改判的方向是对的（它确实不是结构性到头），但「没试过」这个说法暗含「马上能试」，而事实是「要先配」。**
"""

VERDICT = """

---

## 第 865 轮：C7c 那条路卡在配置，而缺的 provider 只差一个环境变量

### `rea` 的四个 native provider 全不可用

| provider | 状态 | 缺什么 |
|---|---|---|
| ghidra | `not_configured` | `GHIDRA_INSTALL_DIR`（Ghidra 12.x） |
| hopper | `unsupported_host` | win32 不支持 |
| **ida** | **`not_configured`** | **`REA_IDA_MCP_CONFIG`** |
| kuna | `not_configured` | `REA_KUNA_COMMAND` |

**`match_native_functions` 要的两侧 `list_procedures` 只能由 native provider 产出 —— 工具在，provider 不在。**

### 而缺的那个刚好是我已经有的

**`ida` provider 只缺 `REA_IDA_MCP_CONFIG`：一个指向 IDA MCP 注册 JSON 的路径。**
**而本会话的 IDA MCP 一直是通的（`analysis/ida.py` 直连 13337，这几十轮都在用）。**

**三步：① 写注册 JSON（指向 13337）② 设 `REA_IDA_MCP_CONFIG` ③ 重启 REA。**

**第 3 步是硬门槛 —— 而「开关 MCP 条目」是 goal 允许停下来等 YG 的两件事之一。**

### 而收益不确定

| 已知 | Unknown |
|---|---|
| 工具对口（按字节/CFG 指纹配对，前提就是没符号） | **两侧是不同 AOT 框架（.NET 10 ↔ .NET 8），字节相同的函数可能很少** |
| 配 provider 只需一个环境变量 | **配上后能配出多少对，未知** |

> **这是一个「花一次重启，换一个不确定的收益」的决定。**

### 仍然 Unknown

**配好后能配出多少对**（**如果很少，这条路依然不通，但那时至少是「试过且知道结果」**）·
**有没有更省的路**（只对少数关键函数做字节比对，不需要 provider —— **但只适用于「函数能先按名字对上」，而那正是 C7c 说做不到的事**）·
**`REA_IDA_MCP_CONFIG` 的 JSON 格式**（要先读 `docs/providers/ida-provider.md`）

### 教训

> **「有个工具能做这件事」和「这个工具在这台机器上能用」是两句话。**
> **我上一轮把第一句当成了第二句 —— 改判方向对（确实不是结构性到头），但「没试过」暗含「马上能试」，而事实是「要先配」。**
"""

BACKLOG_ADD = """

## 判据 — C7c 卡在 provider 配置（R865）

**`rea` 四个 native provider 全不可用：ghidra/kuna `not_configured` · hopper `unsupported_host` · **ida `not_configured` 缺 `REA_IDA_MCP_CONFIG`**。**
**`match_native_functions` 要的 `list_procedures` 只能由 native provider 产出 → 工具在，provider 不在。**

### 而 ida provider 只差一个环境变量

**本会话 IDA MCP 一直通（`analysis/ida.py` → 13337）。三步：写注册 JSON → 设 `REA_IDA_MCP_CONFIG` → **重启 REA**。**
**第 3 步是硬门槛 —— 「开关 MCP 条目」是允许停等 YG 的两件事之一。**

### 收益不确定

| 已知 | Unknown |
|---|---|
| 工具对口（按字节/CFG 配对，前提是没符号） | **.NET 10 ↔ .NET 8 AOT，字节相同可能很少** |
| 只需一个环境变量 | 配上能配多少对 |

| 仍 Unknown | |
|---|---|
| 配好后能配多少对 | 若很少，路仍不通 —— 但那时是「试过且知道」 |
| 更省的路 | 少数关键函数直接字节比对，不需 provider；**但只适用于能先按名字对上** |
| 注册 JSON 格式 | 读 `docs/providers/ida-provider.md` |

**纪律**：**「有个工具能做」和「这工具在这台机器上能用」是两句话。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R865", BLOCKER)
    ensure(RSTATUS, "R865", BLOCKER)
    ensure(RVERDICT, "第 865 轮", VERDICT)
    ensure(BACKLOG, "R865", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R865" not in h:
        h += ("\n## R865 补充 — C7c 卡在 provider\n\n"
              "**`rea` 四个 native provider 全不可用**：ghidra/kuna `not_configured` · hopper `unsupported_host` · **ida 缺 `REA_IDA_MCP_CONFIG`**。\n"
              "**→ `match_native_functions` 要的 `list_procedures` 出不来：工具在，provider 不在。**\n"
              "**而 ida provider 只差一个环境变量（本会话 IDA MCP 一直通 13337）：写注册 JSON → 设变量 → **重启 REA**（= 允许停等 YG 的条目）。**\n"
              "**收益不确定：.NET 10 ↔ .NET 8 AOT，字节相同的函数可能很少。**\n"
              "**教训：「有个工具能做」≠「这工具在这台机器上能用」。**\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R865"), (RSTATUS, "R865"), (RVERDICT, "第 865 轮"), (BACKLOG, "R865")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R865: the untried road for C7c is a configuration step, and the missing provider is an env var\n\n"
         "R864 concluded that C7c was blocked by an untried tool rather than by structure. Checking rea's provider table"
         " turns that into something executable and less cheerful: all four native providers are unavailable. Ghidra and"
         " Kuna are not configured, Hopper does not run on win32, and the IDA provider is not configured because"
         " REA_IDA_MCP_CONFIG is unset. Since match_native_functions takes list_procedures Evidence, which only a native"
         " provider can produce, the tool exists and its dependency does not.\n\n"
         "The one that is missing is the one already running. This session's IDA MCP has been live on port 13337 for"
         " dozens of rounds, reached directly by analysis/ida.py. Configuring the provider needs no installation: write an"
         " IDA MCP registration JSON pointing at that port, set REA_IDA_MCP_CONFIG to its path, and restart REA. The third"
         " step is the hard one, because toggling an MCP entry is one of the two things the goal allows stopping for.\n\n"
         "The return is also uncertain. The tool pairs functions by unique symbols, identical observed bytes and"
         " CFG, call and string fingerprints, and the two binaries sit on different AOT frameworks -- .NET 10 against"
         " .NET 8 -- so identically-byte'd functions may be rare. That makes this a decision to spend one restart on an"
         " uncertain payoff, against leaving C7c unknown with its reason recorded and pressing on with the core at the"
         " current priorities.\n\n"
         "What this round adds is that the sentence 'an untried tool' is now a three-step checklist with a stated price,"
         " which is more useful than calling the road blocked.\n\n"
         "Unknown: how many pairs match_native_functions could produce once the provider is set, where a small number"
         " leaves the road closed but at least closed by measurement; whether a cheaper route exists by comparing bytes"
         " for a handful of key functions without any provider, which fails precisely because C7c's premise is that the"
         " functions cannot be aligned by name first; and the registration JSON's format, which docs/providers/"
         "ida-provider.md documents.\n\n"
         "The lesson is a distinction between two sentences that sound alike: a tool can do this, and this tool can do"
         " this on this machine. Last round I treated the first as the second, and while the correction in direction was"
         " right -- C7c is not structurally blocked -- the phrase 'untried' implied it could be tried at once, when in"
         " fact it must first be configured.\n\n"
         "No product code changed; seven metrics carry unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
