import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 141 轮。", "最后更新：第 142 轮。", 1)

anchor = "- **六道墙普查（R141）**"
add = (
    "- **调用终于有人调用（R142）**：`DetectAsync` 末尾 `return await SolveDetectedWallAsync(c, ct)`；\n"
    "  只分派 `cloudflare` / `kasada`（与 `VendorWiring.Wired` 一致）。\n"
    "  无 Chromium 时记事实 `antibot.solver = \"unavailable\"` 并继续，**不打失败**。\n"
    "  **「接线」是一串：写端、读端、调用、触发；任何一环缺失功能都等于不存在。**\n"
)

if anchor in t and "调用终于有人调用" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
