import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 93 轮。", "最后更新：第 94 轮。"),
    ("**905 通过 / 0 失败 / 2 跳过**", "**910 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R93）。", "上一次跑：全 PASS（R94）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **IDA 数据库现在是「无」"
add = """- **端口通了不等于能查。** R94 重载后 `/mcp` 在 IDA **刚开始加载**时就应答（`server_health: ok`），
  但 `find_regex` 要建全库字符串缓存，会死在
  `ida_mcp.sync.IDASyncError: Tool timed out after 60.00s`。
  判据是 **`auto_analysis_ready == true`**，不是端口。
  用 `python analysis/ida_wait.py [分钟]` 轮询，打印 READY 再查。
- **不用 IDA 也能取证：`python analysis/pe_strings.py <exe> <out> 8`。**
  直接从 PE 抽 UTF-16LE 字面量（129 MB → 180,228 条 → 9.3 MB 文本），不需要分析完成。
  R94 用它拿到 Demandware 全族：8 个 `Sites-*` 站点 id + 17 个真控制器名。
  **分析库是加速器，不是数据源** —— 丢了库不等于丢了内容。
- **Demandware 的四个假控制器（R94 已修）**：`Checkout-Submit` / `Checkout-SubmitShipping` /
  `Checkout-SubmitPayment` / `Cart-Show` 在镜像里都不存在，真名是
  `CheckoutServices-PlaceOrder` / `CheckoutShippingServices-SubmitShipping` /
  `CheckoutServices-SubmitPayment` / `Cart-Get`。已固化为 `DemandwareControllers`。
- **目标带 PDB 提示**：`C:\\actions-runner\\_work\\Cybersole\\Cybersole\\...\\net10.0\\win-x64\\native\\Cybersole.pdb`
  —— 目标是 **.NET 10** + GitHub Actions 构建。**拿到那份 PDB 就能让 `sub_*` 变真名。**
- **IDA 数据库现在是「无」"""
if anchor in t and "端口通了不等于能查" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
