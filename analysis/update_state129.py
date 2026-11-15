import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 128 轮。", "最后更新：第 129 轮。", 1)

anchor = "- **溯源闸门 = 验证第 8 步（R128）**"
add = (
    "- **常量干净 ≠ 代码干净（R129）**：闸门扩到**方法体内联字面量**后，202 条里 **29 条不在镜像里**。\n"
    "  当场抓到 `NikeFlow.SubmitOrderAsync` 里的 `api.nike.com/buy/orders/v2/…`（R87 的发明，一直在代码里，\n"
    "  常量扫描看不见）→ 改为 POST `NikeEndpoints.OrderV5`，cartId 放 body。\n"
    "- **三类溯源**：`literal`（镜像里逐字有）/ `live`（无字面量但真实响应过，如 BSTN `/api/beast`）/\n"
    "  `fixture`（故意保留的不存在路径）。台账 `docs/ENDPOINT_PROVENANCE.md`，**24 条待定**。\n"
    "- **第 8 步是棘轮不是零容忍**：`unknown ≤ baseline(24)`，超过才红。**永远红的检查等于没有检查。**\n"
    "- **JohnLewisBff 12 → 13**：补 `/callback/login/guest?email=`（它坐在 `bff/` 旁边，扫 `bff/` 看不见）。\n"
)

if anchor in t and "常量干净 ≠ 代码干净" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
