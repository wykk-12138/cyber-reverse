import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 119 轮。", "最后更新：第 120 轮。", 1)

anchor = "- **John Lewis 是 19 步，不是 17（R119 修正）**"
add = (
    "- **序号扫描不能证明归属（R120）**：序号是「每个类各自编号」，同序号 126 上挂着三个类的\n"
    "  方法（`CompletePayPalGuestPayment`/`Register`/`SubmitKlaviyoSubscription`）。\n"
    "  九条扫描结果因此只作为 `CandidateSteps` 候选，**不并进 `StoreFlowSteps`**；\n"
    "  `NoCandidateWasPromotedToAStep` 断言两者互不相交。**可靠单位是「一段连续字面量」，不是序号。**\n"
    "- **候选里两族最值得追**：GraphQL 购物车族（106–109，与 R101 的 persisted 操作互证）\n"
    "  与 PayPal/forward payment 族（125–127）。\n"
    "- **IDA 独立探活**：按 `ida-reverse` 技能的握手（`POST /mcp get_metadata`）可独立确认服务在线；\n"
    "  本会话无 `mcp__ida__*` 工具，仍走 `analysis/ida_mcp.py`。\n"
)

if anchor in t and "序号扫描不能证明归属" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
