import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 179 轮。", "最后更新：第 180 轮。", 1)

anchor = "- **引擎方言层（R179）**"
add = (
    "- **键序层：建好但未接线（R180）**：`KeyOrderTable` 实现原版的 `reorder` —— 三个入口\n"
    "  （`Object.getOwnPropertyNames`/`Object.keys`/`Reflect.ownKeys`）、五类规则（全局对象 + `MAIN_FRAME_ONLY`、\n"
    "  `CSSStyleDeclaration.prototype` 录制表、**实例只报数字索引**、`ORDER` 的 `{match,names,drop}`、symbol 放最后）。\n"
    "  接线后 `mutation-check.py` 挂住 → 那一行**注释掉**，`TheLayerIsBuiltButNotWired` 断言这个状态。\n"
    "  Blink 基线：`sources=[3,3]`、`css non-numeric=750:751`（设备是 881 全在原型上）。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "键序层：建好但未接线" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R180 note inserted")
