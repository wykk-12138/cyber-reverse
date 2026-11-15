import io

p = r"D:\projects\cyber-reverse\replica\tools\mutation-check.py"
t = io.open(p, encoding="utf-8").read()

old = 'REPO = r"C:\\Users\\wykk\\AppData\\Local\\Cybersole\\replica"'

new = '''# R127: the repo moved to D:. Resolve it from this file's own location so a future move is a no-op.
REPO = str(__import__("pathlib").Path(__file__).resolve().parent.parent)'''

if old not in t:
    raise SystemExit("REPO anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("mutation-check resolves its repo from __file__")
