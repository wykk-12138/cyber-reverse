import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\CustomStoresPageTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        // and the empty state is hidden. It stays in the tree — IsVisible=false is how Avalonia
        // removes something from the screen — so the assertion is visibility, not presence.
        var emptyLine = Descendants(view).OfType<TextBlock>()
            .First(t => t.Text == "Nothing to see here");
        _out.WriteLine($"empty state visible: {emptyLine.IsVisible}");
        Assert.False(emptyLine.IsVisible);'''

new = '''        // and the empty state is hidden. It stays in the tree — IsVisible=false is how Avalonia
        // removes something from the screen — and the flag sits on the panel that wraps the two
        // lines, not on the lines themselves, so the assertion walks up to find it.
        var emptyLine = Descendants(view).OfType<TextBlock>()
            .First(t => t.Text == "Nothing to see here");

        var hidden = false;
        for (Avalonia.StyledElement? node = emptyLine; node is not null; node = node.Parent)
            if (node is Control control && !control.IsVisible) { hidden = true; break; }

        _out.WriteLine($"empty state hidden by an ancestor: {hidden}");
        Assert.True(hidden);'''

if old not in t:
    raise SystemExit("assert anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("assertion walks the ancestor chain")
