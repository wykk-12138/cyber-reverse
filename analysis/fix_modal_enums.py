import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\Modals\SettingsModals.cs"
t = io.open(p, encoding="utf-8").read()

# 1) Thickness lives in Avalonia; the file never needed it before.
if "using Avalonia;" not in t.split("namespace")[0]:
    t = t.replace("using Avalonia.Controls;", "using Avalonia;\nusing Avalonia.Controls;", 1)

# 2) Inside a Window subclass, bare HorizontalAlignment resolves to the instance property.
t = t.replace("HorizontalAlignment = HorizontalAlignment.Stretch",
              "HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Stretch")
t = t.replace("HorizontalAlignment = HorizontalAlignment.Center",
              "HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center")
t = t.replace("HorizontalContentAlignment = HorizontalAlignment.Center",
              "HorizontalContentAlignment = Avalonia.Layout.HorizontalAlignment.Center")
t = t.replace("VerticalAlignment = VerticalAlignment.Center",
              "VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("qualified the enums, added using Avalonia")
