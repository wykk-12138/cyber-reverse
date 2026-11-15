import io, os

v = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
s = r"D:\projects\cyber-reverse\replica\docs\_r185_section.md"

a = io.open(v, encoding="utf-8").read()
b = io.open(s, encoding="utf-8").read()
if "第 185 轮" not in a:
    io.open(v, "w", encoding="utf-8", newline="").write(a.rstrip() + "\n" + b)
    print("appended", os.path.getsize(v))
else:
    print("already present")
os.remove(s)

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()
t = t.replace("最后更新：第 184 轮。", "最后更新：第 185 轮。", 1)

anchor = "- **window/document 两个 prune（R184）**"
add = (
    "- **窗口排序 `topList`（R185）**：`WindowOrder` —— 页面自己的全局**不删而排**（数字索引在前、引擎基表居中、\n"
    "  具名在后）；`WINDOW_BASELINE` 必须是**最后一句**（否则脚本自己装的会被当成页面的）；`webkit` 在\n"
    "  `Raven` 之前显式插入。实测 `shape=[\"function\",…]`、`order=[\"Raven\",true,true]`、`splice=[876,-1,true]`。\n"
    "  坑：`GLOBAL_PRUNE` 会删掉 `__topList` → KEEP 已补 `__topList`/`__globalPrune`/`__documentPrune`。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "窗口排序 `topList`" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R185 note inserted")
