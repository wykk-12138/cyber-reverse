import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 163 轮。", "最后更新：第 164 轮。", 1)

anchor = "- **剪枝纠正 R156（R163）**"
add = (
    "- **原型与单元素 languages（R164）**：NAV 值装 `Navigator.prototype`（非实例）；\n"
    "  `languages` 冻结为 **1 个元素**。实测纠正：`defineProperty` **可能接受但无效**\n"
    "  （platform 仍 Win32），故 put 试原型+实例并**用读回值验证**。\n"
    "  另修 `JsGuard`：注释里的撇号会吞掉后续代码 → 先跳注释再处理引号。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "原型与单元素" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R164 note inserted")
