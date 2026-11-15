import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 134 轮。", "最后更新：第 135 轮。", 1)

anchor = "- **闭环（R134）**"
add = (
    "- **身份链打通（R135）**：`ChromiumBridge` 暴露 `ProfilePath` / `Fingerprint`；\n"
    "  `ChromiumKasadaSolver.SolveAsync(…, FlowSession? session)` 在 `NavigateAsync` **之前**\n"
    "  调 `BrowserIdentity.RecordProfile(…, userAgentAlreadySent: true)`，并把 `ProfileKey` 放进结果。\n"
    "  链：桥建 profile → 求解器记身份 → 网关读同一 key。**数据模型正确 ≠ 数据流正确。**\n"
)

if anchor in t and "身份链打通" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
