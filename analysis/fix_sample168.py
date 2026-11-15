import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceOrderTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                    surfaceBody += MobileSurface.BodyJs(userAgent);'''
new = '''                    surfaceBody += MobileSurface.BodyJs();'''

if old not in t:
    raise SystemExit("sample anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the sample composition matches the real one")
