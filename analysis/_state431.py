import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 431 轮：`exe-reverse` 值不值得用 —— 拿真样本跑过再说

### 一、实测（`D:\\projects\\exe-reverse\\skills\\exe-reverse`，只读脚本，不走 MCP）

**`pe_triage.py` 对 target（20 秒）** 给出我们此前没有的事实：

```
identity    : amd64 / 64-bit / exe   subsystem windows_gui   entry 0x3105ec8
checksum    : declared 0x7b4a13f == computed   ✔
directories : basereloc, debug, exception, export, iat, import, load_config, resource, security, tls
build       : timestamp 2026-11-11T15:56:14Z   linker 14.44   rich 12 entries
debug/pdb   : C:\\actions-runner\\...\\bin\\Release\\net10.0\\win-x64\\native\\Cybersole.pdb
managed     : no CLR directory          ← 确认 NativeAOT
sections    : .text 51.7 MB (ent 5.47) / .rdata 59.7 MB (6.95) / .data / .pdata / .rsrc / .reloc
signals     : TLS callback @0x3105edc；Authenticode 证书表存在
surface     : 17 DLL / 438 imports；39 exports；12 resources
```

**两个立即有用的结果**：

1. **原版是 .NET 10，不是 .NET 8** —— PDB 路径写着 `net10.0`。我们文档里一直写「.NET 8 NativeAOT」，
   **R431 起订正**（`AGENTS.md` / `docs/GOAL.md` 已改；复刻件仍用 .NET 8 + Avalonia，不必跟随）。
2. **TLS callback 存在** —— 断点打 `AddressOfEntryPoint` 会太晚，这条对后面任何动态观察都成立。

**39 个导出全部是 Brotli**（`BrotliDecoderDecompress` 等），不是应用符号 —— 所以"导出表能当符号源"这条路断了。

**`pe_diff.py`（5.18.32 ↔ 5.18.35）**：

```
A 129,243,216 B  129,306,192 B   （+62,976）
sections: 6 个全部 changed [layout changed]
byte diff: 4,195,337 bytes in 9,965 ranges（预算内停止）
normalised: TimeDateStamp / CheckSum / Rich / 13 debug entries / 12 resource timestamps
```

结论：**两版之间所有节都重排了**，字节级 diff 不能承载符号信息。版本对照只能在
"inventory / 资源 / 字符串"层面做（正是 rea `compare_application_versions` 的层面），
不是补丁级 diff 的用法。

### 二、三个来源对本项目的定位（按有用度）

| 排名 | 来源 | 管什么 | 本项目里的用法 |
|---|---|---|---|
| 1 | **seep-reverse-lab** | **方法论 + 就绪判定**：Windows 6 步 SOP、IDA/MCP 三段链、端口、验证口径、提示词工装 | 已用（`MANUAL/IDA-PRO.md` 的"轮询 13337 就绪"直接催生了直连方案）；`POC-VALIDATION.md` 待读 |
| 2 | **rea** | **证据级对照与判定**：`compare_functions` / `match_native_functions` / `compare_application_versions` / `verify_reconstruction` / unknown 账本 | 判定规则已进 `AGENTS.md`；工具等 DSH 重启后挂上 |
| 3 | **exe-reverse** | **PE 结构工具 + 补丁/保护对抗纪律** | 两个只读脚本常备：`pe_triage.py`（分诊）、`pe_diff.py`（版本对照）；其余（许可机制、AOB、注入、脱壳）与本任务无关 |

### 三、`exe-reverse` 为什么排第三（不是不好，是目标不同）

它的 SKILL.md 第一句把自己的交付物写成"**a patched APP.dll that launches…**" ——
它的成功判据是**打补丁后仍能跑**；我们的成功判据是**忠实重实现后行为相等**。
两者在"能不能改字节"上恰好相反（我们一个字都不改原版）。

而且它自己的 `references/dotnet-decompilation.md` 明确写着：

```
| Native AOT output: no CIL to find | the native routes in static-analysis.md |
| ReadyToRun IL editing and Native AOT symbol recovery.   ← 自述不在覆盖范围
```

所以它的 .NET 部分对我们**只对复刻件自身**有意义，对 NativeAOT 原版没有。

### 四、这一轮的一句话

> 三个仓库我都有路径，但只有真跑一次，才知道谁管方法、谁管证据、谁只是个 PE 读数器。

> **"装了"不等于"能帮上忙"，跑一遍才知道边界在哪。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| **rea MCP** |', '''| **exe-reverse** | 只读脚本常备：`pe_triage.py`（PE 分诊）、`pe_diff.py`（版本对照）。R431 实测：原版是 **.NET 10**（PDB 路径）、39 个导出全是 Brotli、TLS callback 存在、5.18.32↔5.18.35 六节全重排 | 已用 |
| **rea MCP** |''', 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
