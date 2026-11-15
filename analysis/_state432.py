import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 432 轮：把 `exe-reverse` 从「skill」降级成「两个只读脚本」

### 一、判据：它不是"没用"，而是"当 skill 用会带错方向"

| 它的定位 | 我们的定位 |
|---|---|
| 交付物 = **一个打过补丁、还能跑的 APP.dll** | 交付物 = **忠实重实现，行为相等**（一个字都不改原版） |
| 方法论主干：授权机制、AOB、注入、脱壳、反调试 | 与本任务无关 |
| 自述覆盖边界：`ReadyToRun IL editing and Native AOT symbol recovery` **不在覆盖范围** | 我们的目标正是 NativeAOT |

留在技能目录的风险很具体：**新会话 agent 打开技能列表，看到「licence check / patch / defeat analysis」的
description，可能把任务往"打补丁"方向带** —— 那与本任务方向相反。

### 二、处置（可逆，一行恢复）

```powershell
Move-Item D:\\projects\\cyber-reverse\\.dsh\\skills\\exe-reverse  D:\\projects\\cyber-reverse\\.dsh\\skills-disabled\\exe-reverse
# 需要恢复时：
# New-Item -ItemType Junction -Path D:\\projects\\cyber-reverse\\.dsh\\skills\\exe-reverse -Target D:\\projects\\exe-reverse\\skills\\exe-reverse
```

结果：`.dsh/skills/` 已空 → **本会话的技能目录里 `exe-reverse` 消失**（系统提示已确认）。

**保留的**：两个脚本仍可用绝对路径直调（`--help` 已验证可跑）：

```
python D:\\projects\\exe-reverse\\skills\\exe-reverse\\scripts\\pe_triage.py <exe>
python D:\\projects\\exe-reverse\\skills\\exe-reverse\\scripts\\pe_diff.py   <exeA> <exeB>
```

写进 `AGENTS.md` §1 的白名单，并注明「R431 实测价值：查出 .NET 10、39 导出全是 Brotli、TLS callback、两版六节全重排」。

### 三、与 `seep` / `rea` 的关系没变

- 方法论：`seep-reverse-lab` 第一；
- 证据与判定：`rea` 第二；
- `exe-reverse`：**只读读数器**，用它的两个脚本，不用它的框架。

### 四、这一轮的一句话

> 关掉一个 skill 不等于丢掉它的能力 —— 我把能力留在命令行里，只把"框架"关掉了。

> **降级比删除更准确：删掉会丢工具，留着会丢方向。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| **exe-reverse** | 只读脚本常备', '| **exe-reverse** | 已停用 skill 注册（junction 移到 `.dsh/skills-disabled/`），只留两个只读脚本直调：`pe_triage.py`（PE 分诊）、`pe_diff.py`（版本对照）。R431 实测', 1)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
