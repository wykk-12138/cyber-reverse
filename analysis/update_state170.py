import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 169 轮。", "最后更新：第 170 轮。", 1)

anchor = "- **三处纠正（R169）**"
add = (
    "- **credentials 是转发不是模拟（R170）**：原版给 `navigator` **实例**加一个非枚举自有属性\n"
    "  `credentials`，四个方法各自 `target.apply(native, …)` 转发给引擎容器并伪装源码；原型成员保留。\n"
    "  实测 `[true,false,false,false,-1,\"function\",1,\"[native code]\"]`（for-in 里没有它）。\n"
    "  另装 `canShare`/`share` 为**数据属性**（arity 1，WebKit 的 NotAllowedError 原话）。\n"
    "  **「未实现」的开放项已关 —— 关法是换问题。**\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "credentials 是转发" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R170 note inserted")
