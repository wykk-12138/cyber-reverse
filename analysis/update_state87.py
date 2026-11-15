import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 86 轮。", "最后更新：第 87 轮。"),
    ("**887 通过 / 0 失败 / 2 跳过**", "**891 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R86）。", "上一次跑：全 PASS（R87）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **常量装不下「每个任务不一样」的东西。**"
add = '''- **IDA 关掉之后的重开流程（R87 实测）**：`ida-mcp-doctor.ps1 -Path Cybersole.exe`
  → 弹「数据库已存在」→ 点 **加载现有(L)** → 再弹「not closed, repair?」→ 点 **Repair**
  → 「请稍候…」约 2 分钟（1 GB 的 `.id0`）。doctor 自己会在 180 s 超时退出，**没关系**：
  IDA 活着就行，之后直接用 `python analysis/ida_mcp.py health / call …`。
  修复完成后 `auto_analysis_ready` / `strings_cache_ready` 会先是 false，`find_regex` 仍可用。
- **`find_regex "api\\.nike\\.com"` = 20 条，这就是 Nike 端点的全集。** 已固化为
  `Cybersole.Stores.Flows.NikeEndpoints`。**replica 用的 `buy/carts/v2/…` 与 `buy/orders/v2/…`
  在二进制里根本不存在**；真实形状是单个 `buy/checkouts/v3/{checkoutId}` 资源，14 步往它上面写，
  但每步的子路径是拼接的、没有字面量，**因此仍无证据**。见 `NIKE_PARITY.md` 第 12 节。
- **常量装不下「每个任务不一样」的东西。**'''
if anchor in t and "IDA 关掉之后的重开流程" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
