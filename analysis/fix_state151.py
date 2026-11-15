import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 150 轮。", "最后更新：第 151 轮。", 1)

anchor = "- **窗口尺寸跟随 profile + 几何反复钉（R150）**"
add = (
    "- **`VisualViewport` 补上（R151）**：原版 `VV = {offsetLeft/offsetTop/pageLeft/pageTop:0,\n"
    "  width:VW, height:VH, scale:1}` 七字段，只装顶层；真浏览器测到 `[402,684,1,0,0]`。\n"
    "  **`orientation` 在 `SCREEN_ORDER` 里但不在 `SCREEN` 值里 —— 原版不补**，实测报\n"
    "  `landscape-primary`（与竖屏手机不自洽）。**留白要有名字**：测试记录它，不发明它。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "补上（R151）" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R151 note inserted")
