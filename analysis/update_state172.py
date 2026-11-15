import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 171 轮。", "最后更新：第 172 轮。", 1)

anchor = "- **方法简写 = 没有 `prototype`（R171）**"
add = (
    "- **伪装是改写不是查表（R172）**：`V8_NATIVE` / `V8_ACCESSOR` 两个正则 —— 抹掉访问器的 `get `/`set `\n"
    "  角色，并把 V8 的单行 `{ [native code] }` **重排成 WebKit 的三行**。实测 `Map`（未碰过）也被重排。\n"
    "  `JsGuard` 扩到**十二份 body**，并学会「正则里的括号不算代码」「字符串里的 `\\n` 是正常 JS」。\n"
    "  同一轮里 TDZ 错误犯了两次（`G.__nativeMask = {…}` 写在 `maskGetter` 之前）。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "伪装是改写不是查表" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R172 note inserted")
