import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 170 轮。", "最后更新：第 171 轮。", 1)

anchor = "- **credentials 是转发不是模拟（R170）**"
add = (
    "- **方法简写 = 没有 `prototype`（R171）**：`({ m() {} }).m` 是 WebIDL 操作的样子；\n"
    "  `NativeMask` 导出 `renamed` / `method` / `getter`，`canShare`/`share` 走 `method` 构建。\n"
    "  实测 `[false,true,\"canShare\",1]`（无 prototype、name/arity 对），而\n"
    "  `credentials` 四方法**故意保留** prototype（设备如此）。\n"
    "  另记：原版 `toString` 用 `V8_NATIVE`/`V8_ACCESS` 正则改写真实源码，我这版存假文本（等价但更粗）。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "方法简写 = 没有" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R171 note inserted")
