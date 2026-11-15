import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 181 轮。", "最后更新：第 182 轮。", 1)

anchor = "- **窗口十一个"
add = (
    "- **十一个名字已上窗口（R182）**：`WindowBaseline` 接进组合链**第 10 步**（mask 之前）。实测\n"
    "  `probe = [6,\"object\",false,12]`、`Object.keys(window)` 含 `__gCrWeb`/`_injected_clipboard`；\n"
    "  子帧 `[false,false,true,true]`（两个 main-frame-only 名字被去掉）。**分块全套 26/26 PASS**。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "十一个名字已上窗口" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R182 note inserted")
