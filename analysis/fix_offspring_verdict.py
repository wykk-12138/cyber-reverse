import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\VERDICT.md"
t = io.open(p, encoding="utf-8").read()

old = "该模块用 MagentoFlow，可能不对"
new = ("该模块用 MagentoFlow，可能不对；**R92：UA 里是 `OFFSPRING/3 … poq.ios`，"
       "Poq 移动端 App，不是 Magento**")

if old not in t:
    raise SystemExit("offspring anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("VERDICT offspring line updated")
