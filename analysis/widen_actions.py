import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Accounts\AccountGrid.cs"
t = io.open(p, encoding="utf-8").read()

old = 'internal const string ActionsWidth = "200";'
new = ('// R72: 200 clipped "Clear Accounts" — two buttons side by side need the room, and the\n'
       '    // reserved column is what keeps the header and the rows aligned.\n'
       '    internal const string ActionsWidth = "270";')
if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("widened to 270")
