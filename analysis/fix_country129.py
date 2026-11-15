import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\NikeFlow.cs"
t = io.open(p, encoding="utf-8").read()

old = '            ["country"] = NikeFlow.CountryCode,'
new = '            ["country"] = CountryCode,'

if old not in t:
    raise SystemExit("country anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("instance property referenced")
