import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 139 轮。", "最后更新：第 140 轮。", 1)

anchor = "- **Cloudflare 是同一条梯子（R139）**"
add = (
    "- **检测↔存储之间的调用补上了（R140）**：`CloudflareClearance.ApplyAsync` 只有墙是 Cloudflare 时\n"
    "  才跑梯子，成功则**同时写** `cloudflare.clearance` 与 cookie `cf_clearance`，拒绝则只写状态并\n"
    "  原样发出镜像的文案。**检测在、存储在，中间的调用不在** —— 与 R133/R134 支付侧同一个形状。\n"
    "- **`cf-solver.cybersole.io` 实测 401**：主机真实可达、需要凭据；`ServiceStatusObserved = 401`\n"
    "  与一句人话已记录。**「有主机、没协议」比「什么都没有」更接近能实现。**\n"
)

if anchor in t and "之间的调用补上了" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
