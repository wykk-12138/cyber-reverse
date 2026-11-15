import io, os

# append the section to VERDICT and add the SESSION_STATE note
v = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
s = r"D:\projects\cyber-reverse\replica\docs\_r183_section.md"

a = io.open(v, encoding="utf-8").read()
b = io.open(s, encoding="utf-8").read()
if "第 183 轮" not in a:
    io.open(v, "w", encoding="utf-8", newline="").write(a.rstrip() + "\n" + b)
    print("appended", os.path.getsize(v))
else:
    print("already present")
os.remove(s)

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()
t = t.replace("最后更新：第 182 轮。", "最后更新：第 183 轮。", 1)

anchor = "- **十一个名字已上窗口（R182）**"
add = (
    "- **两张窗口名单（R183）**：`WINDOW_ALL`（getOwnPropertyNames）**1062** 条、`WINDOW_ENUM`（Object.keys）\n"
    "  **228** 条，逐字生成进 `WindowNameTable.Generated.cs`。**纠正**：R181/R182 的 1290 是正则产物，真值 1062。\n"
    "  关键事实：`webkit` 只在自有名表中且是最后一项，`__gCrWeb` 在两张表都在 —— 这解释了设备样本\n"
    "  `[\"__gCrWeb\",\"hsw\",\"__wdata\",\"webkit\"]` 里 `webkit` 为何排最后。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "两张窗口名单" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R183 note inserted")
