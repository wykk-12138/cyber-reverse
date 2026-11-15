import io, os

base = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests"

renames = [
    ('"Clone"', '"Clone Proxies"'),
    ('"Copy Proxy"', '"Copy Proxies"'),
]
for name in ["ProxyCloneMoveTests.cs", "ProxyRowTestTests.cs"]:
    p = os.path.join(base, name)
    t = io.open(p, encoding="utf-8").read()
    before = t
    for old, new in renames:
        t = t.replace(old, new)
    if t != before:
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("renamed in", name)

# The select-all CheckBox inherits Button, so it shows up as an empty label.
p = os.path.join(base, "RenderedProxyTableTests.cs")
t = io.open(p, encoding="utf-8").read()
old = """        var labels = header.Children.OfType<Button>()
            .Select(b => (b.Content as TextBlock)?.Text ?? string.Empty).ToList();"""
new = """        // The select-all CheckBox is a Button subclass with no text content; it is not a column.
        var labels = header.Children.OfType<Button>()
            .Select(b => (b.Content as TextBlock)?.Text ?? string.Empty)
            .Where(text => text.Length > 0)
            .ToList();"""
if old not in t:
    raise SystemExit("labels anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("filtered empty labels")
