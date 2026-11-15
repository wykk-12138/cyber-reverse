import io

p = r"D:\projects\cyber-reverse\replica\tools\endpoint-provenance.py"
t = io.open(p, encoding="utf-8").read()

old = """    for name, value in plain:
        out.append((name, value, value))"""

new = """    for name, value in plain.items():
        out.append((name, value, value))"""

if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("fixed the dict iteration")
