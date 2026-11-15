import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\CloudflareClearanceTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    private static FlowContext Context(string vendor)
    {
        var session = new FlowSession { Url = "https://example.test/" };
        session.Vars["antibot"] = vendor;
        return new FlowContext(session) { Url = session.Url! };
    }'''

new = '''    private static FlowContext Context(string vendor)
    {
        // FlowContext is built by the runner, so the test builds the smallest one it can and sets the
        // two things the helper reads: the vendor the detector recorded, and a URL to solve for.
        var context = new FlowContext { Url = "https://example.test/", Http = null! };
        context.Session.Vars["antibot"] = vendor;
        return context;
    }'''

if old not in t:
    raise SystemExit("context anchor missing")
t = t.replace(old, new, 1)

old2 = '''        Assert.Equal(CloudflareStrategy.ClearanceCookie,
            AntiBotProtocol.CookiesFor("Cloudflare")!.Length > 0
                ? AntiBotProtocol.CookiesFor("Cloudflare")![0]
                : CloudflareStrategy.ClearanceCookie);'''

new2 = '''        var cookies = AntiBotProtocol.CookiesFor("Cloudflare");
        Assert.NotNull(cookies);
        Assert.Contains(CloudflareStrategy.ClearanceCookie, cookies!);'''

if old2 not in t:
    raise SystemExit("cookie anchor missing")
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("test construction aligned with FlowContext's shape")
