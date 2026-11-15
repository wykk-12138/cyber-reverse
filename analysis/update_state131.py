import io

p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("最后更新：第 130 轮。", "最后更新：第 131 轮。", 1)

anchor = "- **常量干净 ≠ 代码干净（R129）**"
add = (
    "- **指纹是三层，不是一层（R131 更正 R130）**：\n"
    "  `browser`（8 字段，每 profile，`BrowserFingerprint`）/ `payload`（`fingerprint-v1` 与\n"
    "  `fingerprint-v1-sans-ua` 两个变体）/ `dlpa`（3DS 设备画像，来自\n"
    "  **`Cybersole.Helpers.Dlpa.Fingerprint.template.json`**）。\n"
    "  **R130 把模板当成浏览器指纹模板是错的** —— 资源全名里写着 `Dlpa`，字段是\n"
    "  `browserColorDepth/Height/Width/TZ`、`threeDSCompInd`、`challengeWindowSize`，值是字符串。\n"
    "  已固化为 `FingerprintLayers`；**3DS 画像尚未实现**，且实现时必须与浏览器层不矛盾。\n"
    "- **读资源全名 / 命名空间是零成本证据**：我总是先猜语义再找证据，这次一读全名结论就反了。\n"
)

if anchor in t and "指纹是三层" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("traps added")
else:
    print("anchor missing or present")
