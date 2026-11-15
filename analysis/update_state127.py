import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 126 轮。", "最后更新：第 127 轮。", 1)

anchor = "- **控制器族普查（R126）**"
add = (
    "- **工作区已迁到 `D:\\projects\\cyber-reverse`（R127）**：replica / analysis / docs_baseline / target，\n"
    "  IDA 库在 `target\\Cybersole.exe.i64`。C: 原 `current\\` 安装保留未动。见根目录 `MIGRATION.md`。\n"
    "- **`/v5/Order/` 是 Nike 的，不是 Scheels 的（R127 更正）**：全库只有一条字面量\n"
    "  `https://www.nike.com/gs/checkout-api/api/v5/Order/` —— 这正是 Nike 的下单端点\n"
    "  （`api.nike.com` 那 19 条里没有，因为它在 `www.nike.com/gs/checkout-api/api`）。\n"
    "  Scheels 移动 API 回到 **2 端点**，`SubmitOrderApp` 回到未映射。\n"
    "- **规则（第六次同类错误后写进断言）**：**端点的「主机 + 路径」必须来自同一条字面量；\n"
    "  跨字面量拼接 = 发明。** `TheOrderPathBelongsToNikeNotScheels` 守着这一条。\n"
    "- **主机路径基线**：apihub.scheels 17 / mobile-api.scheels 2 / checkout.johnlewis 15 /\n"
    "  api.nike 19 / api2.endclothing 2。JL 的 `/callback/login/guest?email=` 仍不在表里。\n"
)

if anchor in t and "工作区已迁到" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
