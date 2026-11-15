import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 107 轮。", "最后更新：第 108 轮。"),
    ("**970 通过 / 0 失败 / 2 跳过**", "**972 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：15/16 PASS（R107，见下）。", "上一次跑：`verify.ps1`（非 Full）全绿；`-Full` 未跑完（R108，见下）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **SFCC 双路径已落地（R107）**"
add = """- **`-Full` 的 slow 阶段现在会「重试整组一次」**（R108），重试才绿时细节写
  `green on retry (first pass lost a live host)`，**不伪装成干净通过**；
  重试仍失败则判定仍是 FAIL（读最后一次 `$LASTEXITCODE`）。`VerifyRetryPolicyTests` 五条钉住。
- **「只重跑失败的那几条」被实现过又回滚**（R108）：逻辑对，但整轮连续两次 0 字节输出。
  **一个会卡住的终判据，等于没有终判据。**
- **数花括号检查 PowerShell 脚本是错的**：`verify.ps1` 实测 67 开 / 68 关，
  但 PowerShell 解析器接受（格式串和正则里有花括号）。真检查用
  `python`/`powershell -File analysis/parse_check108.ps1` → `PARSE OK`。
- **SFCC 双路径已落地（R107）**"""
if anchor in t and "重试整组一次" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
