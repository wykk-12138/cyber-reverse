import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\KeyBindsPageTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    /// <summary>
    /// Notifications has five tabs, in the live page's order: Checkout, Decline, Captcha,
    /// Smart Actions, Other.
    /// </summary>
    [Fact]
    public void NotificationsHasTheFiveTabs()
    {
        var tabs = NotificationsView.TabCaptions();

        _out.WriteLine(string.Join(" | ", tabs));

        Assert.Equal(new[] { "Checkout", "Decline", "Captcha", "Smart Actions", "Other" }, tabs);
    }'''

new = '''    /// <summary>
    /// Notifications has five tabs, in the live page's order: Checkout, Decline, Captcha,
    /// Smart Actions, Other. (R78 renamed the accessor from TabCaptions to Tabs once the five
    /// panels turned out to be one formula.)
    /// </summary>
    [Fact]
    public void NotificationsHasTheFiveTabs()
    {
        var tabs = NotificationsView.Tabs;

        _out.WriteLine(string.Join(" | ", tabs));

        Assert.Equal(new[] { "Checkout", "Decline", "Captcha", "Smart Actions", "Other" }, tabs);
    }'''

if old not in t:
    raise SystemExit("notifications tab test anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("test updated to the new accessor")
