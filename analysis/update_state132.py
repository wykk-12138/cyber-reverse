import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 131 轮。", "最后更新：第 132 轮。", 1)

anchor = "- **指纹是三层，不是一层（R131 更正 R130）**"
add = (
    "- **第三层已落地（R132）**：`DlpaProfile.From(fingerprint, utcOffsetMinutes, userAgent, language)`\n"
    "  —— 3DS 画像**从 `BrowserFingerprint` 派生**，不提供「拼装」入口；`AgreesWith()` 是守卫。\n"
    "  `browserTZ` 是**分钟数**（`60` = UTC+1）。`-sans-ua` 只少 `browserUserAgent` 一个键，其余逐一同值。\n"
    "  **凡是描述同一对象的两套数据，唯一正确的构造方式是派生，不是拼装。**\n"
)

if anchor in t and "第三层已落地" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
