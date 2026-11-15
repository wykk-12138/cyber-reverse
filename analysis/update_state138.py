import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 137 轮。", "最后更新：第 138 轮。", 1)

anchor = "- **四条路已落成代码（R137）**"
add = (
    "- **`*.cybersole.io` 十五个主机已入表（R138）**：amazon-waf / analytics / api / castle / cdn /\n"
    "  cf-solver / datadome / forward / images / match / pop4 / proxy / support / telemetry / text-captcha。\n"
    "  **没有 `kasada.cybersole.io`** —— 所以 Kasada `Api` 那条路没有专用主机，候选是 `api.cybersole.io`\n"
    "  （**推断，非抓包**，`KasadaApiEvidence` 明写）。这是会话里第一次把「原版有、我们缺」写成正式条目。\n"
    "- **四个 solver 主机 + 一句分野声明**：`Cloudflare solver refused the token, solving in-bot`\n"
    "  —— 与 Kasada 的 `Api`→`Local` 是同一条策略的两个实例。\n"
)

if anchor in t and "十五个主机已入表" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
