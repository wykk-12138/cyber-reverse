import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 164 轮。", "最后更新：第 165 轮。", 1)

anchor = "- **原型与单元素 languages（R164）**"
add = (
    "- **顺序重排实测（R165）**：`NavOrder.ReseatBodyJs` 删后重加（原版在 Screen 上就是这么做的）。\n"
    "  真浏览器：**28/50 个记录名真在 `Navigator.prototype` 上**，在这 28 个之间**相对顺序 100% 达成**；\n"
    "  不可配置的 Blink 名字永远在前。断言写测量事实而非理想。\n"
    "  **另纠**：`NAV_ORDER` 是 **50** 项（R159 的注释写 49），常量改为从列表读。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "顺序重排实测" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R165 note inserted")
