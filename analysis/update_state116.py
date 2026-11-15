import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 115 轮。", "最后更新：第 116 轮。", 1)

anchor = "- **步 → 主机第一次接起来（R115）**"
add = (
    "- **Pop Mart 24 步 ↔ 39 端点（R116）**：连了 **14 对**，留空 **10 步 / 25 端点**；\n"
    "  两侧都作为正式字段 `UnmappedSteps` / `UnmappedEndpoints` 记录，并由 `TheRemaindersAddUp`\n"
    "  断言「已连 + 未连 = 总数」。**留空的 25 个端点里有整个收银台族 —— 说明抽签流程与结账流程\n"
    "  是两套，不是一条链的两头。**\n"
)

if anchor in t and "Pop Mart 24 步" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
