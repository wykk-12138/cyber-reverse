import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

for cls in ("ImapView", "GoogleAccountsView", "PayPalAccountsView"):
    i = t.find("public sealed class " + cls)
    j = t.find("public sealed class ", i + 10)
    seg = t[i:j if j > 0 else len(t)]
    print("=" * 10, cls, len(seg), "chars")
    for line in seg.split("\n"):
        s = line.strip()
        if any(k in s for k in ("doc.", "count.Text", "var rows", "ListBox", 'UiKit.Row("', 'UiKit.Button("', "ItemsSource")):
            print("   ", s[:120])
