import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

anchor = "- **`*.cybersole.io` 十五个主机已入表（R138）**"
add = (
    "- **Cloudflare 是同一条梯子（R139）**：`ICloudflareSolver` + `Service`\n"
    "  （`cf-solver.cybersole.io`）/ `InBot` + `CloudflareStrategyRunner`（服务在前、本地在后；\n"
    "  拒绝当状态不当失败）。与 Kasada 对齐：服务路 / 本地路 / 接口 / 拒绝文案。\n"
    "  协议靠注入，主机已记录；`cf_clearance` 与 `AntiBotProtocol` 一致。\n"
)

if anchor not in t:
    raise SystemExit("anchor still missing")
if "Cloudflare 是同一条梯子" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("R139 note inserted")
