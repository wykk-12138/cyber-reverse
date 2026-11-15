import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 180 轮。", "最后更新：第 181 轮。", 1)

anchor = "- **环境告警（R180 观测）**"
add = (
    "- **窗口十一个 `_injected_*`（R181）**：原版顶层名字表 **1290** 个，其中 12 个是 Chrome‑for‑iOS 自己注入的钩子\n"
    "  （`_injected_clipboard`、`_injected_passkey_controller`、`__gCrWeb`…）；**我们的窗口一个都没有**，是设备级指纹。\n"
    "  `WindowBaseline` 记录机制：`FRAMED = top !== G`、`MAIN_FRAME_ONLY` 两个名字只从子帧去掉、\n"
    "  基线取「脚本装完时的自有名字」（文件最后一行）。`CSS_DECL` 只有 **11** 个名字。\n"
    "- **分块测试工装（R181）**：`tools\\test-chunks.ps1` —— 单进程跑整套会**静默挂住**（每类 1 s、整套 20 min），\n"
    "  分块后 **26/26 块全绿**（含 100–170 s 的重浏览器块）。这是本机跑全套的正式方式。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "窗口十一个" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R181 notes inserted")
