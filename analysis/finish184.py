import io, os

v = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
s = r"D:\projects\cyber-reverse\replica\docs\_r184_section.md"

a = io.open(v, encoding="utf-8").read()
b = io.open(s, encoding="utf-8").read()
if "第 184 轮" not in a:
    io.open(v, "w", encoding="utf-8", newline="").write(a.rstrip() + "\n" + b)
    print("appended", os.path.getsize(v))
else:
    print("already present")
os.remove(s)

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()
t = t.replace("最后更新：第 183 轮。", "最后更新：第 184 轮。", 1)

anchor = "- **两张窗口名单（R183）**"
add = (
    "- **window/document 两个 prune（R184）**：`GlobalPrune` —— `GLOBAL_PRUNE` 按 `DEVICE_GLOBALS`(1062) + `KEEP`(11+6)\n"
    "  删除 `chrome` 等 Blink 全局（**函数形式**，子帧也prune，因为 challenge 跑在 iframe 里）；\n"
    "  `DOCUMENT_PRUNE` 删 8 个 Blink-only 成员（`featurePolicy`/`hasPrivateToken`…），让 hCaptcha 的 **spst=0**。\n"
    "  实测 `[false,\"undefined\",false,false,true,\"object\"]`、子帧 `[false,false]`。组合链现为 **13 步**。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "window/document 两个 prune" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R184 note inserted")
