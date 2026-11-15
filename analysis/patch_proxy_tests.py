import io, os, re

base = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests"
names = [f for f in os.listdir(base) if f.endswith(".cs")]
total = 0
touched = []
for name in names:
    p = os.path.join(base, name)
    t = io.open(p, encoding="utf-8").read()
    if "ProxyView" not in t:
        continue
    n = t.count("ProxyView")
    t = t.replace("ProxyView", "ProxyGrid")
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    touched.append((name, n))
    total += n

for name, n in touched:
    print("%-34s %d" % (name, n))
print("total", total)
