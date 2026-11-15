import io

# 1) The Help section's id is "help", not "need-help".
p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\SettingsShell.cs"
t = io.open(p, encoding="utf-8").read()
t = t.replace('["need-help"] = ("Get Help", "Take a look at common errors or contact support"),',
              '["help"] = ("Get Help", "Take a look at common errors or contact support"),', 1)
t = t.replace('["need-help"] = "Get Help",', '["help"] = "Get Help",', 1)
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("help id fixed")

# 2) Test data follows.
p2 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\SettingsPageHeadersTests.cs"
t2 = io.open(p2, encoding="utf-8").read()
t2 = t2.replace('[InlineData("need-help", "Get Help"', '[InlineData("help", "Get Help"')
io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("test data fixed")

# 3) R74's fallback test is now about an unknown id: every real page has a header.
p3 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\SettingsPagesTests.cs"
t3 = io.open(p3, encoding="utf-8").read()
old = '''    /// <summary>An unvisited page falls back to its nav label and claims no subtitle.</summary>
    [Fact]
    public void AnUnvisitedPageFallsBackToItsNavLabel()
    {
        var (title, subtitle) = SettingsShell.PageHeaderFor("appearance");

        _out.WriteLine($"{title} / {subtitle ?? "<none>"}");

        Assert.Equal("Appearance", title);
        Assert.Null(subtitle);
    }'''
new = '''    /// <summary>
    /// An unknown id falls back to itself and claims no subtitle.
    ///
    /// <para>
    /// R74 wrote this against <c>appearance</c>, which had not been walked yet. R75 swept the last
    /// eleven pages, so every real section now has a header and there is no unvisited page left to
    /// point at — the test had to move to a genuinely unknown id rather than be deleted.
    /// </para>
    /// </summary>
    [Fact]
    public void AnUnknownPageClaimsNoSubtitle()
    {
        var (title, subtitle) = SettingsShell.PageHeaderFor("does-not-exist");

        _out.WriteLine($"{title} / {subtitle ?? "<none>"}");

        Assert.Equal("does-not-exist", title);
        Assert.Null(subtitle);
    }'''
if old not in t3:
    raise SystemExit("fallback test anchor missing")
io.open(p3, "w", encoding="utf-8", newline="").write(t3.replace(old, new, 1))
print("fallback test updated")
