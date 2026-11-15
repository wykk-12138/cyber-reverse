import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

# The table renders its own empty state; the separate UiKit.Empty line is gone.
old = '''                count,
                rows,
                empty,
                UiKit.Row("Imap Provider", UiKit.Buttons(provider,'''
new = '''                count,
                rows,
                UiKit.Row("Imap Provider", UiKit.Buttons(provider,'''
if old not in t:
    raise SystemExit("imap content anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("removed the stray empty control")
