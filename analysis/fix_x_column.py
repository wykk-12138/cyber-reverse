import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

old = 'var grid = new Grid { ColumnDefinitions = new ColumnDefinitions("150,Auto,24,150,Auto") };'
new = ('// Six columns: label, chip, X for the left pair, then the same three for the right\n'
       '            // pair. R76: with five, the right-hand X had no column to land in and drew on\n'
       '            // top of its own chip ("×Ctrl+N").\n'
       '            var grid = new Grid '
       '{ ColumnDefinitions = new ColumnDefinitions("150,Auto,24,150,Auto,24") };')
if old not in t:
    raise SystemExit("grid anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("six columns")
