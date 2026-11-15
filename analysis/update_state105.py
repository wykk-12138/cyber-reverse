import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 104 轮。", "最后更新：第 105 轮。"),
    ("**955 通过 / 0 失败 / 2 跳过**", "**960 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R104）。", "上一次跑：全 PASS（R105）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **`docs/ENDPOINT_FAMILIES.md` 是端点族的总表**"
add = """- **六家反爬（R105）**：DataDome / PerimeterX / Akamai / Kasada / TrustDecision / Cloudflare，
  已固化为 `AntiBotVendors`。**最锋利的一条：`datadome.cybersole.io/sensor` —— 原版自己架了
  DataDome sensor 中继**（`api-sdk.datadome.co` 用于 SDK，自家中继用于 sensor 流量，两者并存）。
  **Kasada 版本按店分**：`Converse-`/`Crocs-EU-`/`Crocs-JP-`/`Crocs-`/`Footsites-Kasada-Version`，
  一个全局版本会错掉四个。replica 只有解题种类（Turnstile/reCAPTCHA/hCaptcha/Geetest），
  这六家挑战系统一个都没有。
- **`docs/ENDPOINT_FAMILIES.md` 是端点族的总表**"""
if anchor in t and "六家反爬（R105）" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
