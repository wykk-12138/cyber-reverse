import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 136 轮。", "最后更新：第 137 轮。", 1)

anchor = "- **Kasada 是四条路（R136）**"
add = (
    "- **四条路已落成代码（R137）**：`IKasadaSolver` + `ApiKasadaSolver` / `LocalKasadaSolver` /\n"
    "  `NamedFallbackSolver`（两种）+ `KasadaStrategyRunner`（顺序 Api→Local→Fallback→MobileFallback，\n"
    "  第一个可用即止，全空返回 `Failed Kasada (Retry limit reached)` 并串起经过的状态）。\n"
    "  `KasadaToken` 把 token 与来源模式绑定。**API 地址靠注入，未配置时返回镜像自己的运维文案**。\n"
)

if anchor in t and "四条路已落成代码" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
