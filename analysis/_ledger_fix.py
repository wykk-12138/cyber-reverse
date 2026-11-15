import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\GeometryLedgerTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        var analytics = Read("src/Cybersole.Ui/Views/Analytics/AnalyticsViews.cs");
        Assert.DoesNotContain("\\"2*,8,1*\\"", analytics);'''
new = '''        // the comment above the template quotes the old value on purpose, so the check runs on code only
        var analytics = string.Join("\\n", Read("src/Cybersole.Ui/Views/Analytics/AnalyticsViews.cs")
            .Split('\\n')
            .Where(line => !line.TrimStart().StartsWith("//", System.StringComparison.Ordinal)));

        Assert.DoesNotContain("\\"2*,8,1*\\"", analytics);'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('assertion now comment-blind')
