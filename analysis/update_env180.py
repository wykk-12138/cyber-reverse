import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

anchor = "- **键序层：建好但未接线（R180）**"
add = (
    "- **环境告警（R180 观测）**：`%TEMP%` 里累积到 **5555** 个目录（单次 `clean-temp.ps1` 就回收 843 MB 的\n"
    "  Chromium profile）。症状：**单个测试类 1 s 跑完，整套 `dotnet test` 却挂住 20 分钟以上**；\n"
    "  期间 `mutation-check.py` 也会超时（它连跑多轮整套测试）。\n"
    "  **处置**：跑全套前先 `tools\\clean-temp.ps1`，并确认没有残留 `chrome`/`testhost`；必要时重启机器。\n"
    "  这不是代码缺陷，但会让「八步全绿」的判定不可信，所以写进状态。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "环境告警" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("environment note inserted")
