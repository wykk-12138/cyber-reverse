import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\MainWindow.cs"
t = io.open(p, encoding="utf-8").read()

subs = [
    ('FontFamily = new Media.FontFamily("Consolas,monospace"),',
     'FontFamily = new FontFamily("Consolas,monospace"),'),
    ('FontWeight = Media.FontWeight.SemiBold', 'FontWeight = FontWeight.SemiBold'),
]
for old, new in subs:
    if old not in t:
        raise SystemExit("MISS: " + old[:60])
    t = t.replace(old, new, 1)

# ViewHostModal lives in Cybersole.Ui.Views.Common; add the using if it is not there.
if "using Cybersole.Ui.Views.Common;" not in t:
    anchor = "using Cybersole.Ui.Views.Accounts;"
    if anchor in t:
        t = t.replace(anchor, anchor + "\nusing Cybersole.Ui.Views.Common;", 1)
    else:
        anchor = "using Cybersole.Ui.Views;"
        assert anchor in t
        t = t.replace(anchor, anchor + "\nusing Cybersole.Ui.Views.Common;", 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("patched")
