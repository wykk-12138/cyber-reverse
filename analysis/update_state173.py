import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 172 轮。", "最后更新：第 173 轮。", 1)

anchor = "- **伪装是改写不是查表（R172）**"
add = (
    "- **外来接收者要抛异常（R173）**：`userAgent`/`platform`/`vendor`/`appVersion` 改成**品牌校验访问器**\n"
    "  （`!(this instanceof G.Navigator)` → `TypeError('Illegal invocation')`）。实测 `.get.call({})` 抛、\n"
    "  `get platform`(len 0, 无 prototype) 形状对。三个坑：`{get x(){}}.x` 会调用、原型读值会抛（要从实例读）、\n"
    "  `asNative` 存的源码要抹掉 `get ` 角色。另记 `record`/`pathOf`：补丁按 `KNOWN`+`Intl` **路径**记录以重放子 realm。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "外来接收者要抛异常" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R173 note inserted")
