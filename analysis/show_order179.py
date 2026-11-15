import io, re

t = io.open(r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\SurfaceOrder.cs",
            encoding="utf-8").read()

for m in re.finditer(r'new Step\((\d+), "([a-z-]+)"', t):
    print(m.group(1), m.group(2))
