import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 151 轮。", "最后更新：第 152 轮。", 1)

anchor = "- **`VisualViewport` 补上（R151）**"
add = (
    "- **原版会话 payload 样本（R152）**：池子里捡到一份真实 JSON —— 十六个头键保序，含\n"
    "  `cf_flags` / `fresh-cookie` / `cookie-_cc`（= `_t` 前 24 字符）/ `time-tz-*` 四件套 /\n"
    "  `time-tz-fixed-locale-string`（固定瞬间 2014-03-06 07:58:39 按宿主 locale 格式化）。\n"
    "  **`orientation` 原版也报 landscape** ⇒ R151 的「不自洽」是原版常态。\n"
    "  另有两个「非 DOM」键：`navigator.automationEnabled`、`webdriver_detect`。已落成 `SessionPayload`。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "会话 payload 样本（R152）" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R152 note inserted")
