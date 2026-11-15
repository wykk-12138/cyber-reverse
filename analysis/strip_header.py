import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

# The spliced block carried its own usings + namespace because it was drafted as a standalone
# file. Strip that header: the insertion point is already inside the namespace.
header = """using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Cybersole.Services;

namespace Cybersole.Ui.Views.Settings;

"""
if header not in t:
    raise SystemExit("spliced header not found")
t = t.replace(header, "", 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("header stripped")
