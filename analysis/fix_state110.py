import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

anchor = "- **slow 阶段已拆成两条检查（R109）**"
add = """- **判据已拆成七步：`tools/verify-steps.ps1`（R110，七步全 PASS）** ——
  `-List` / `-Step n` / `-All`。步骤：build、unit tests、slow(network)、slow(kasada live)、
  store modules、docs present、mutation guards。**本机现在跑不了长命令，所以「七步分别跑」
  就是可用的终判据**；`verify.ps1 -Full` 留给健康机器。
- **慢测「每次挂一条不同的实时测试」根因是测量方式（R110 实测）**：同一个 slow 网络组单独跑 PASS，
  Kasada 实时组单独跑也 PASS。
- **PowerShell 函数返回值会吞输出（R110）**：`if (Invoke-Step $s)` 会把函数产生的字符串一起吃掉 ——
  结果用 `Write-Host`，只 `return $ok`。**`Test-Path` 不设 `$LASTEXITCODE`**，无退出码的步骤按自身输出判定。
- **IDA 库「未正常关闭」会循环**：`Load existing` → `Reload file` 退回载入对话框（等于没载入）；
  有备份时只能「载入 + Repair」（约 14 分钟重分析）。PDB 询问一律选 No。
"""

if anchor not in t:
    raise SystemExit("anchor missing")
if "verify-steps.ps1" in t and "判据已拆成七步" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R110 notes inserted")
