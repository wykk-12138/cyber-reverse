import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\AdyenBrowserInfoTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    [Fact]
    public void TheSessionSuppliesTheProfileKeyAndOffset()
    {
        var text = Source();

        Assert.Contains("browser.fingerprintKey", text);
        Assert.Contains("browser.timezoneOffsetMinutes", text);
        _out.WriteLine("browser.fingerprintKey / browser.timezoneOffsetMinutes");
    }'''

new = '''    [Fact]
    public void TheSessionSuppliesTheProfileKeyAndOffset()
    {
        var text = Source();

        // R134: the key spellings live in BrowserIdentity now, so the gateway names the class instead
        // of the strings — one spelling of each key, in one file.
        Assert.Contains("BrowserIdentity.Fingerprint", text);
        Assert.Contains("BrowserIdentity.TimeZoneOffset", text);
        Assert.DoesNotContain("\\"browser.fingerprintKey\\"", text);

        foreach (var key in BrowserIdentity.Keys) _out.WriteLine(key);
    }'''

if old not in t:
    raise SystemExit("session anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("key assertions follow the single writer")
