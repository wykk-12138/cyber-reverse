import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 109 轮。", "最后更新：第 110 轮。"),
    ("**976 通过 / 0 失败 / 2 跳过**", "**976 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：单元测试 976 全绿；`verify.ps1` 未跑完（R109，本机长命令被杀，见下）。",
     "上一次跑：**`verify-steps.ps1` 七步全 PASS**（R110）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:36])
        continue
    t = t.replace(old, new, 1)

anchor = "- **slow 阶段已拆成两条检查（R109）**"
add = """- **判据已拆成七步：`tools/verify-steps.ps1`（R110，七步全 PASS）。**
  `-List` / `-Step n` / `-All`。步骤：build、unit tests、slow(network)、slow(kasada live)、
  store modules、docs present、mutation guards。**本机现在跑不了长命令，所以「七步分别跑」
  就是可用的终判据**；`verify.ps1 -Full` 保留给健康机器。
- **慢测之前「每次都挂一条不同的实时测试」，根因是测量方式不是测试本身（R110 实测）**：
  同一个 slow 网络组单独跑 PASS，Kasada 实时组单独跑也 PASS。
- **PowerShell 函数返回值会吞输出（R110）**：`if (Invoke-Step $s)` 会把函数产生的字符串一起吃掉，
  结果打成 `Write-Host`、只 `return $ok`。**`Test-Path` 不设 `$LASTEXITCODE`**，
  无退出码的步骤要按自身输出判定。
- **IDA 库的「未正常关闭」状态循环**：`Load existing` → `Reload file` 会退回载入对话框（等于没载入）；
  在有备份的前提下只能走「载入 + Repair」（约 14 分钟重分析）。PDB 询问一律选 No。
- **slow 阶段已拆成两条检查（R109）**"""
if anchor in t and "verify-steps.ps1" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
