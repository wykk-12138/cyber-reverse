import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 103 轮。", "最后更新：第 104 轮。"),
    ("**950 通过 / 0 失败 / 2 跳过**", "**955 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R103）。", "上一次跑：全 PASS（R104）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **John Lewis 的 12 条摊在"
add = """- **`docs/ENDPOINT_FAMILIES.md` 是端点族的总表**（19 族 + 数量 + 形态 + 证据轮次 + 常量），
  已进 `verify.ps1` 文档检查。做新族前先看它，别重复 dump。
- **唯一一次「字符串 → 含义」的证明（R104）**：Magento `/account/login/referer/{base64}` 的两条
  payload 解码出 `https://www.panini.it/…` 与 `https://www.footlocker.ph/`。
  其余全是「字面量存在」；**能从存在走到含义的，只有解码过的这一条**。
- **auth 三族**：better-auth（11，`/api/auth/*`）、Magento 账户（8，`/account/login*`）、
  On Running 韩国站（7，**Magento GraphQL**，`?graphql_router=` 是 PWA Studio 招牌）。
  已固化为 `AccountAndAuthFamilies`。
- **John Lewis 的 12 条摊在"""
if anchor in t and "ENDPOINT_FAMILIES.md` 是端点族的总表" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
