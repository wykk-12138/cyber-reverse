import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 174 轮。", "最后更新：第 175 轮。", 1)

anchor = "- **路径式重放（R174）**"
add = (
    "- **抛错的堆栈也要伪装（R175）**：品牌校验用 `Error.captureStackTrace`（**启动时只读一次**）\n"
    "  丢掉自己的帧，再插一行 `at get <name> (native)`。实测栈第二行即该原生帧，无 `blob:`/helper 帧。\n"
    "  在可被改写的内建上「抛错时才取值」＝把遥控器交给探针，所以只读一次。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "抛错的堆栈也要伪装" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R175 note inserted")
