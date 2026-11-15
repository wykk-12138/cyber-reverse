import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 140 轮。", "最后更新：第 141 轮。", 1)

anchor = "- **检测↔存储之间的调用补上了（R140）**"
add = (
    "- **六道墙普查（R141）**：`VendorWiring` 记六个 vendor 的 检测标记 / cookie / 调用是否已接。\n"
    "  **只有 cloudflare 与 kasada 接了**；四个缺口分四类：datadome（缺协议，主机已知）、\n"
    "  imperva（连 cookie 都没有）、perimeterx（镜像里就是空的，故意留白）、\n"
    "  **queue-it（不是挑战是排队 —— 该等待，不是求解）**。\n"
    "- **`KasadaClearance`（R141）**：与 `CloudflareClearance` 同形 —— 只有墙是 Kasada 时跑策略，\n"
    "  成功写 `kasada.token` + cookie `kpsdk`，并记 `kasada.mode`（token 带着来路）。\n"
)

if anchor in t and "六道墙普查" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
