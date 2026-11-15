import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NativeMask.cs"
t = io.open(p, encoding="utf-8").read()

old = "      FAKES.set(fn, 'function ' + name + '() { [native code] }');"
new = "      FAKES.set(fn, 'function ' + name + '() {\\n    [native code]\\n}');"

if old not in t:
    raise SystemExit("fakes anchor missing")
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("fakes answer in WebKit's three-line form")
