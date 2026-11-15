import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Tasks\TaskView.cs"
t = io.open(p, encoding="utf-8").read()

subs = [
    # Avalonia has no TextBlock.ToolTip; it is an attached property on the control.
    ("                FontWeight = FontWeight.SemiBold,\n                ToolTip = what,",
     "                FontWeight = FontWeight.SemiBold,"),
    ("        return new Border\n        {\n            Background = new SolidColorBrush(Color.Parse(colour)),",
     "        var box = new Border\n        {\n            Background = new SolidColorBrush(Color.Parse(colour)),"),
    ("                Text = count.ToString(),",
     "                Text = count.ToString(),"),
    ("                ToolTip = what,\n            },\n        };",
     "            },\n        };\n\n        ToolTip.SetTip(box, what);\n        return box;"),
]

for old, new in subs:
    if old not in t:
        raise SystemExit("missing: " + old[:60])
    t = t.replace(old, new, 1)

# The Docked helper never got copied into this file.
anchor = "    private static MenuItem Menu(string header, Action action)"
helper = '''    private static Control Docked(Control control, Avalonia.Controls.Dock dock)
    {
        DockPanel.SetDock(control, dock);
        return control;
    }

'''
if anchor not in t:
    raise SystemExit("menu anchor missing")
t = t.replace(anchor, helper + anchor, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("patched")
