import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding="utf-8").read()

if "using Avalonia.Media;" not in t:
    t = t.replace("using Avalonia.Controls;", "using Avalonia.Controls;\nusing Avalonia.Media;", 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("using Avalonia.Media;" in t and "media using present" or "media using missing")
print("first lines:\n" + "\n".join(t.split("\n")[:8]))
