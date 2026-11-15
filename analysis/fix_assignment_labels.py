import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsViews.cs"
t = io.open(p, encoding="utf-8").read()

# 1) A display-name table: the live page prints "Round robin", not the enum's "RoundRobin".
old = ('        var assignment = UiKit.Combo(Enum.GetNames<BrowserProfileAssignment>(),\n'
       '            (int)s.BrowserProfileAssignment);')
new = ('        // R77: the live page prints "Round robin" with a space; Enum.GetNames gave\n'
       '        // "RoundRobin", so the enum name was leaking straight into the UI.\n'
       '        var assignment = UiKit.Combo(AssignmentChoices, (int)s.BrowserProfileAssignment);')
if old not in t:
    raise SystemExit("assignment anchor missing")
t = t.replace(old, new, 1)

anchor = "    /// <summary>The three section headings, in the live page's order.</summary>"
choices = '''    /// <summary>
    /// The Profile Assignment choices as the live page prints them. The enum calls the first one
    /// <c>RoundRobin</c>; the page calls it "Round robin", and the space is the difference between
    /// a UI and a debug view.
    /// </summary>
    public static readonly IReadOnlyList<string> AssignmentChoices = new[]
    {
        "Round robin", "Random", "Least used",
    };

'''
if anchor not in t:
    raise SystemExit("heading anchor missing")
t = t.replace(anchor, choices + anchor, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("assignment labels humanised")
