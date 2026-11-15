import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 127 轮。", "最后更新：第 128 轮。", 1)
t = t.replace("**`verify-steps.ps1` 七步全 PASS**（R110）", "**`verify-steps.ps1` 八步全 PASS**（R128）", 1)

anchor = "- **工作区已迁到 `D:\\projects\\cyber-reverse`（R127）**"
add = (
    "- **溯源闸门 = 验证第 8 步（R128）**：`tools/endpoint-provenance.py` 把所有端点常量的\n"
    "  `Base + path` 按嵌套类作用域解引用成完整值，再逐字比对 `analysis/pe_strings.txt`。\n"
    "  **当前 159 / 159 逐字命中，0 编造。** `EndpointProvenanceTests` 在 C# 侧做同样校验，\n"
    "  缺 dump 时**跳过**而不是假装通过。\n"
    "- **嵌套类共享常量名会让扁平解析串味（R128 自己踩的坑）**：`ScheelsFrontastic` 与\n"
    "  `JohnLewisBff` 各有一个 `Base`，整文件作一个作用域会 last-wins，报出 13 条假编造。\n"
    "  修法是**先把嵌套类区间挖空**再收集本层常量，解析时内层→外层。\n"
)

if anchor in t and "溯源闸门" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
