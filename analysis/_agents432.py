import io
p = r"D:\projects\cyber-reverse\AGENTS.md"
t = io.open(p, encoding='utf-8').read()

old_row = '| `exe-reverse` skill | **项目级**安装：`.dsh/skills/exe-reverse` → junction → `D:\\projects\\exe-reverse\\skills\\exe-reverse`（Codeberg `reverse-skill-lab/exe-reverse`）。PE 分诊、等长补丁、AOB 签名、许可机制分类、`.NET`/IL2CPP/PyInstaller 判定、硬件观察路线图 | 已配置，`doctor.py` 15/29 ok |'
new_row = '| `exe-reverse` skill | 仓库在 `D:\\projects\\exe-reverse\\skills\\exe-reverse`（Codeberg `reverse-skill-lab/exe-reverse`）。**R432 起不再注册为 skill**（见下），只按白名单直调两个只读脚本 | 已停用注册，脚本可用 |'

old_par = '''`exe-reverse` 的用法边界：它的脚本是**只读输入、显式输出**的独立工具，不走 MCP、不常驻；
`EXEREV_TOOLS` 已持久化为 `D:\\projects\\IDA-pro;C:\\Program Files\\7-Zip`（`static_disassembly`
与 `installer_inspect` 靠它解锁）。它要求的方法论与 `seep-reverse-lab` 冲突时，仍以
`seep-reverse-lab` 为准（见 §1）。'''
new_par = '''`exe-reverse` 的用法边界（R432 收紧）：

- **不再注册为 skill**：junction 已从 `.dsh/skills/` 移到 `.dsh/skills-disabled/`，新会话的技能目录里不会再出现它。
  原因：它的交付判据是"打补丁后仍能运行"，与我们"忠实重实现"方向相反，容易被新 agent 当成方法论主导。
- **仍可用的只有两个只读脚本**（绝对路径直调，不需要加载 skill）：
  ```
  D:\\projects\\IDA-pro\\python311\\python.exe D:\\projects\\exe-reverse\\skills\\exe-reverse\\scripts\\pe_triage.py <exe>
  D:\\projects\\IDA-pro\\python311\\python.exe D:\\projects\\exe-reverse\\skills\\exe-reverse\\scripts\\pe_diff.py   <exeA> <exeB>
  ```
  R431 实测价值：查出原版是 **.NET 10**（PDB 路径）、39 导出全是 Brotli、TLS callback 存在、5.18.32↔5.18.35 六节全重排。
- 需要恢复注册时（一行）：
  `New-Item -ItemType Junction -Path D:\\projects\\cyber-reverse\\.dsh\\skills\\exe-reverse -Target D:\\projects\\exe-reverse\\skills\\exe-reverse`
- `EXEREV_TOOLS` 仍持久化为 `D:\\projects\\IDA-pro;C:\\Program Files\\7-Zip`（`static_disassembly`
  与 `installer_inspect` 靠它解锁）。它要求的方法论与 `seep-reverse-lab` 冲突时，以 `seep-reverse-lab` 为准（见 §1）。'''

assert old_row in t, 'row anchor missing'
t = t.replace(old_row, new_row, 1)
assert old_par in t, 'paragraph anchor missing'
t = t.replace(old_par, new_par, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('AGENTS.md updated (row + boundary paragraph)')
