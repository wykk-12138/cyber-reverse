import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 166 轮。", "最后更新：第 167 轮。", 1)

anchor = "- **NAV 户口普查 27/10/13（R166）**"
add = (
    "- **装 standalone + locks（R167）**：`NavigatorLocks` 装 `standalone=false` 与\n"
    "  `locks.request(name,cb)`(len 2) / `locks.query()`(len 0)，在原型上并进 `MaskTargets`；\n"
    "  实测 `[false,\"object\",\"function\",2,\"function\",0]`、回调执行、两者都 `[native code]`。\n"
    "  **顺序即正确性**：安装必须在 reseat **之前**（否则 29/50 且相对顺序 False）。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "standalone + locks" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R167 note inserted")
