import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 118 轮。", "最后更新：第 119 轮。", 1)

anchor = "- **John Lewis 17 步 ↔ 12 端点（R118）**"
add = (
    "- **John Lewis 是 19 步，不是 17（R119 修正）**：R112 读的步表序号 20→23 跳过了 21/22，\n"
    "  我当时当成编译器噪音。**同类的 lambda 表**（`<<FindProduct>g__Available|21_3`、\n"
    "  `<AddToCart>b__22_0`）把 21、22 的名字写出来了 —— 它们是 `FindProduct` / `AddToCart` 两步。\n"
    "  **缺口本身不携带信息，携带信息的是「缺口里有没有名字」，而名字只在第二条字面量里。**\n"
    "  连带：留空步 3 → 5（BFF 没有购物车端点），映射部分不变（新两步无端点）。\n"
    "- **Nike 的 45/47 确实是 MoveNext 助手**，所以「缺口=噪音」只在 Nike 成立，不能推广。\n"
)

if anchor in t and "John Lewis 是 19 步" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
