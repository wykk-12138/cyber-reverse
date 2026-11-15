import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 90 轮。", "最后更新：第 91 轮。"),
    ("**900 通过 / 0 失败 / 2 跳过**", "**904 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R90）。", "上一次跑：全 PASS（R91）。"),
    ("| 注册模块 | **61**", "| 注册模块 | **62**"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **每取一条二进制事实，记下「这条是全的吗」。**"
add = '''- **空结果不是「没有信息」。** R91 查 `bstn` 得到 0 条，但那 3 条命中里有
  `ARROW & BEAST` / `arrowandbeast.com` / `arrowbeast.myshopify.com` ——
  **原版有这个店而 replica 没有**，同时 replica 的 `BstnFlow` 在二进制里毫无踪影。
  补上 `arrowandbeast`（Shopify 别名），`BstnFlow` 保留（有抓包证据），两条事实都进测试。
- **「1 skipped」是最容易被忽略的绿。** 加一个模块后 `mutation-check` 的 round-164 锚点漂了，
  `verify.ps1` 只报 `23 fired, 1 skipped` —— **skipped 既不是红也不是通过**。改锚点后回到 24/0/0。
- **跑测试前先清 `testhost`。** 上一次后台 `verify.ps1` 残留的 testhost 会让 18 条无关 UI 测试一起红；
  `Get-Process testhost | Kill` 后重跑即恢复。**不是代码问题，是环境残留。**
- **每取一条二进制事实，记下「这条是全的吗」。**'''
if anchor in t and "空结果不是「没有信息」" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
