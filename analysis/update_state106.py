import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 105 轮。", "最后更新：第 106 轮。"),
    ("**960 通过 / 0 失败 / 2 跳过**", "**965 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R105）。", "上一次跑：全 PASS（R106）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **六家反爬（R105）**"
add = """- **协议层（R106）**：Kasada 九个 `x-kpsdk-*`（cd/ct/dt/dv/fc/h/im/st/v）；
  cookie 族 Akamai `_abck`/`ak_bmsc`、DataDome `datadome`、Cloudflare `cf_clearance`、Kasada `kpsdk`；
  Queue-it `queue-it.net`/`.queue-it.net`/`panini.queue-it.net`/`queue-it-set-cookie`；
  TrustDecision `trustdevice.js`/`trustdevice-botd.js` + `tdfp/{de,sg}/{hash}/fm.js`。
  已固化为 `AntiBotProtocol`。
- **PerimeterX 是故意留空**：镜像里有厂商名和 `PerimeterX-Token`，但**没有任何 `_px` cookie** ——
  所以 `CookiesFor("PerimeterX")` 返回 null 并有测试断言这个空。
  **「凭常识补」已经错过五次，第六次选择留空。**
- **六家反爬（R105）**"""
if anchor in t and "协议层（R106）" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
