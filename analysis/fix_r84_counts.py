import io

base = r"C:\Users\wykk\AppData\Local\Cybersole\replica"

# 1) The header TextBlock's own IsVisible stays true when its Grid parent is hidden — same trap
#    R79 hit with the empty pane. Walk the ancestors instead.
p = base + r"\tests\Cybersole.Tests\AccountTablesTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        var header = Descendants(table).OfType<TextBlock>().First(t => t.Text == "Email ⇅");
        _out.WriteLine($"header visible after clearing: {header.IsVisible}");

        Assert.False(header.IsVisible);'''
new = '''        // IsVisible sits on the header Grid, not on its TextBlock — the child's own flag stays
        // true. Ask the ancestor chain, the way the empty-pane assertion does.
        var header = Descendants(table).OfType<TextBlock>().First(t => t.Text == "Email ⇅");
        var headerHidden = false;
        for (Avalonia.StyledElement? node = header; node is not null; node = node.Parent)
            if (node is Control control && !control.IsVisible) { headerHidden = true; break; }

        _out.WriteLine($"header hidden after clearing: {headerHidden}");
        Assert.True(headerHidden);'''
if old not in t:
    raise SystemExit("header assert anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("header assertion walks ancestors")

# 2) One more UserControl (AccountTable) — the UI counts move by one.
p2 = base + r"\docs\PARITY.md"
t2 = io.open(p2, encoding="utf-8").read()
old2 = "**76 个 UI 类：24 个 `Window` 子类 + 52 个 `UserControl` 子类。**"
new2 = "**77 个 UI 类：24 个 `Window` 子类 + 53 个 `UserControl` 子类。**"
if old2 not in t2:
    raise SystemExit("parity count anchor missing")
io.open(p2, "w", encoding="utf-8", newline="").write(t2.replace(old2, new2, 1))
print("PARITY count 76/52 -> 77/53")

p3 = base + r"\docs\VERDICT.md"
t3 = io.open(p3, encoding="utf-8").read()
old3 = "UI 类 | 89 个，**37 个不可达**"
new3 = "UI 类 | 90 个，**37 个不可达**"
if old3 in t3:
    t3 = t3.replace(old3, new3, 1)
    io.open(p3, "w", encoding="utf-8", newline="").write(t3)
    print("guide 89 -> 90")
else:
    print("guide anchor missing")

p4 = base + r"\tools\mutation-check.py"
t4 = io.open(p4, encoding="utf-8").read()
t4 = t4.replace('"find": "**76 个 UI 类：24 个",', '"find": "**77 个 UI 类：24 个",', 1)
t4 = t4.replace('"replace": "**76 个 UI 类：23 个",', '"replace": "**77 个 UI 类：23 个",', 1)
io.open(p4, "w", encoding="utf-8", newline="").write(t4)
print("mutation anchors updated")
