using System.Text.Json;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: the original's Kasada solver carries three switches the replica previously had no way
/// to express — MfcEnabled, MobileDv and VersionProvider (symbols at docs/KASADA/11 5.69). Without them the
/// desktop and mobile paths cannot be told apart, because the payload itself is device-agnostic (5.70) and
/// reads whatever identity the host presents.
/// </summary>
public sealed class KasadaMobileSwitchTests
{
    private static string Payload()
    {
        var dir = AppContext.BaseDirectory;
        while (dir is not null && !Directory.Exists(Path.Combine(dir, "fixtures")))
            dir = Directory.GetParent(dir)?.FullName;
        Assert.NotNull(dir);
        return File.ReadAllText(Path.Combine(dir!, "fixtures", "nike-p.js"));
    }

    private static Func<string, string, string, string, string?> Answer(
        out List<string> urls, string ct = "CT-SWITCH-TEST-0123456789")
    {
        var log = new List<string>();
        urls = log;
        return (url, method, headersJson, body) =>
        {
            log.Add(url);
            var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            if (url.EndsWith("/mfc", StringComparison.Ordinal))
            {
                headers["x-kpsdk-h"] = "01";
                headers["x-kpsdk-fc"] = "1";
            }
            else if (url.EndsWith("/r", StringComparison.Ordinal))
            {
                headers["x-kpsdk-ct"] = ct;
            }
            return JsonSerializer.Serialize(new { status = 200, headers, body = "" });
        };
    }

    [Fact]
    public void TheVersionComesFromTheHeaderTheSensorStampedOnItsOwnRequest()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
            Transport = Answer(out _),
        };

        var result = solver.Solve(Payload());

        // /mfc goes out carrying x-kpsdk-v: j-1.2.988 — that is the build the sensor believes it is, and
        // the only authoritative source. A wrong version here is a mismatch the gate can see.
        Assert.Equal("j-1.2.988", result.Version);
    }

    [Fact]
    public void AVersionProviderOverridesWhateverTheSensorSaid()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
            Transport = Answer(out _),
            VersionProvider = () => "j-9.9.999",
        };

        var result = solver.Solve(Payload());

        Assert.Equal("j-9.9.999", result.Version);
        Assert.Equal("j-9.9.999", result.Headers["x-kpsdk-v"]);
    }

    [Fact]
    public void MobileDvIsReportedAsTheDeviceHeaderWhenSet()
    {
        using var desktop = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
            Transport = Answer(out _),
        };
        var noDv = desktop.Solve(Payload());
        Assert.DoesNotContain("x-kpsdk-dv", noDv.Headers.Keys);

        using var mobile = new KasadaSolver(BrowserShim.Ios(href: "https://www.nike.com/"))
        {
            ResourceAddress = "https://www.nike.com/",
            Transport = Answer(out _),
            MobileDv = "dv-from-mobile-profile",
        };
        var withDv = mobile.Solve(Payload());
        Assert.Equal("dv-from-mobile-profile", withDv.Headers["x-kpsdk-dv"]);
    }

    [Fact]
    public void DisablingMfcStopsTheHostFromCallingThatEndpoint()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            ResourceAddress = "https://www.nike.com/",
            Transport = Answer(out var sent),
            MfcEnabled = false,
        };

        var result = solver.Solve(Payload());

        // What the switch controls is the host: it must not reach out to /mfc on the sensor's behalf.
        Assert.DoesNotContain(sent, u => u.EndsWith("/mfc", StringComparison.Ordinal));

        // Measured: refusing /mfc does *not* stop the sensor. It carries on and still issues /r, so a
        // token can arrive even with the remote configuration withheld. MfcEnabled is therefore a switch
        // over the host's own mobile step, not a hard gate on the whole handshake.
        Assert.Contains(sent, u => u.EndsWith("/r", StringComparison.Ordinal));
        Assert.Equal("CT-SWITCH-TEST-0123456789", result.Ct);
    }
}
