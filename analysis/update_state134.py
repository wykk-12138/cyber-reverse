import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 133 轮。", "最后更新：第 134 轮。", 1)

anchor = "- **三层接进真实请求了（R133）**"
add = (
    "- **闭环（R134）**：`BrowserIdentity.Record/RecordProfile` 是三个会话键的**唯一写入者**\n"
    "  （`browser.fingerprintKey` / `timezoneOffsetMinutes` / `fingerprintPayload`）；\n"
    "  网关的读也改成 `BrowserIdentity.Fingerprint/TimeZoneOffset`，测试断言网关里**不再出现**那两个键的字面量。\n"
    "  `LauncherAndPaymentAgree` 断言**启动器与支付用同一个 key** —— 这是整条链存在的理由。\n"
    "  **一个只被读取的变量，不是配置，是悬念。**\n"
)

if anchor in t and "闭环（R134）" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
