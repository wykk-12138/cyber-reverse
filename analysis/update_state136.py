import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 135 轮。", "最后更新：第 136 轮。", 1)

anchor = "- **身份链打通（R135）**"
add = (
    "- **Kasada 是四条路（R136）**：`Api`（getting）/ `Local`（solving）/ `Kasada-Fallback` /\n"
    "  `Kasada-Mobile-Fallback`，配 `IKasadaSolver` 接口 —— **replica 只实现了 `Local`**。\n"
    "  12 条状态字符串逐字记录（含 `Kasada API down (Contact staff)`、`(Rotating)`、`(TL)`、`(MFC)`）。\n"
    "  版本头**每店一个**（7 个）；协议头 8 个（新发现 `x-kpsdk-st`）。\n"
)

if anchor in t and "Kasada 是四条路" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
