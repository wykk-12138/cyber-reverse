import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 152 轮。", "最后更新：第 153 轮。", 1)

anchor = "- **原版会话 payload 样本（R152）**"
add = (
    "- **payload 能构建了（R153）**：`SessionPayloadBuilder.Build(Inputs)`，键序 == `HeadKeys`；\n"
    "  `cookie-_cc` 由 `CookieTagFor` 派生（`Inputs` 无该字段）；时间四件套同瞬间 ——\n"
    "  **`time-local` 必须按 `getTimezoneOffset()` 偏移后格式化**（实测 07:41:15 vs 样本 09:41:15 才发现）；\n"
    "  固定串用模式 `d-M-yyyy, HH:mm:ss` 复现 `6-3-2014, 07:58:39`。构建器不读时钟。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "payload 能构建了（R153）" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R153 note inserted")
