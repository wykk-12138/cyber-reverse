import io
fixes = [
 (r'D:\projects\cyber-reverse\AGENTS.md',
  '把 `Cybersole.exe` 5.18.32（.NET 8 **NativeAOT**，无 IL）在 `replica/` 里做成**功能 1:1** 的复刻件：',
  '把 `Cybersole.exe` 5.18.32（**.NET 10 NativeAOT**，无 IL —— 依据 PDB 路径 `bin/Release/net10.0/win-x64/native/`，R431 用 `pe_triage.py` 读出）\n在 `replica/` 里做成**功能 1:1** 的复刻件（复刻件本身用 .NET 8 + Avalonia，目标框架不必跟随原版）：'),
 (r'D:\projects\cyber-reverse\docs\GOAL.md',
  '把 Cybersole.exe 5.18.32（.NET 8 NativeAOT，无 IL）在 D:\\projects\\cyber-reverse\\replica 里做成功能 1:1 复刻件：',
  '把 Cybersole.exe 5.18.32（.NET 10 NativeAOT，无 IL）在 D:\\projects\\cyber-reverse\\replica 里做成功能 1:1 复刻件：'),
]
for p, old, new in fixes:
    t = io.open(p, encoding='utf-8').read()
    if old in t:
        io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
        print('fixed', p.split('\\')[-1])
    else:
        print('PATTERN MISS', p.split('\\')[-1])
