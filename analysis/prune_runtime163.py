import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SurfaceRuntimeTests.cs"
t = io.open(p, encoding="utf-8").read()

anchor = '''    /// <summary>A Chromium profile gets an empty function, so the honest counts stay honest.</summary>'''

block = '''    /// <summary>
    /// R163: a phone profile must not have the Blink-only members at all, and a desktop profile must keep the one
    /// the payload reads.
    /// </summary>
    [Fact]
    public async Task ThePruneListAnswersPerProfile()
    {
        const string names = string.Join(",", NavPrune.BlinkOnly.Select(n => "'" + n + "'"));

        await using (var phone = await LaunchPatchedAsync(IPhoneUserAgent))
        {
            var present = await phone.EvaluateAsync(
                "JSON.stringify((" + names + ").filter((n) => n in navigator))");
            _out.WriteLine("phone  leaves = " + present);

            // deviceMemory is the one the replica itself installs, so it is the interesting case
            Assert.DoesNotContain("deviceMemory", present!, System.StringComparison.Ordinal);
            Assert.DoesNotContain("connection", present!, System.StringComparison.Ordinal);
        }

        await using (var desktop = await LaunchPatchedAsync("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                                                             "AppleWebKit/537.36 (KHTML, like Gecko) " +
                                                             "Chrome/157.0.0.0 Safari/537.36"))
        {
            var connection = await desktop.EvaluateAsync(
                "JSON.stringify([typeof navigator.connection, navigator.connection && " +
                "navigator.connection.effectiveType])");
            _out.WriteLine("desktop keeps = " + connection);
            Assert.StartsWith("[\\"object\\",\\"4g\\"]", connection, System.StringComparison.Ordinal);
        }
    }

    /// <summary>A Chromium profile gets an empty function, so the honest counts stay honest.</summary>'''

if anchor not in t:
    raise SystemExit("runtime anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, block, 1))
print("the runtime test checks both claims")
