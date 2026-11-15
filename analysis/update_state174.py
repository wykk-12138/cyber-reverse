import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 173 轮。", "最后更新：第 174 轮。", 1)

anchor = "- **外来接收者要抛异常（R173）**"
add = (
    "- **路径式重放（R174）**：`PatchJournal` 按 `pathOf`（`KNOWN` 23 + `Intl` 9）记录 `{path,key,from}`，\n"
    "  重放时把**描述符原样**拷进子 realm；MutationObserver 监听 iframe。实测\n"
    "  `[\"iPhone\",\"iPhone\",5,5,\"function\",true]`（父子一致、子有 canShare 且 `[native code]`）。\n"
    "  **真 bug**：品牌校验不能写 `this instanceof G.Navigator`（子 realm 是 false）→ 改为\n"
    "  `Object.prototype.toString.call(this) === '[object Navigator]'`。\n"
)

if anchor not in t:
    raise SystemExit("anchor missing")
if "路径式重放" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R174 note inserted")
