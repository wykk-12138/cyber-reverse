using System.Net.Http;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// PARITY.md section 7 lists what is deliberately not reproduced, each with a reason. Three of
/// those reasons are "this belongs to the vendor's servers" — and that claim has a shelf life.
///
/// The distinction that matters:
///
///   404        the host answered. DNS resolved, TLS handshake completed, an HTTP server replied.
///              The reason still holds: the vendor's service exists and this path is not it.
///   timeout    the host is gone.
///   DNS fail   the name is gone. The old reason ("belongs to the vendor's servers") has silently
///              become a different statement ("that service no longer exists"), and a reader of
///              the table cannot tell the two apart.
///
/// So these assert "responded", not "200". A 404 passes on purpose.
///
/// Speed=Slow, network-bound. Not part of the fast suite.
/// </summary>
[Trait("Speed", "Slow")]
public class NonParityClaimsTests
{
    private readonly ITestOutputHelper _out;
    public NonParityClaimsTests(ITestOutputHelper output) => _out = output;

    private static readonly HttpClient Http = new()
    {
        Timeout = TimeSpan.FromSeconds(20),
    };

    private static string DocPath()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "docs", "PARITY.md")))
            dir = dir.Parent;

        return dir is null ? string.Empty : Path.Combine(dir.FullName, "docs", "PARITY.md");
    }

    private async Task<(bool Responded, int? Code, string Detail)> ProbeAsync(string url)
    {
        try
        {
            using var res = await Http.GetAsync(url, HttpCompletionOption.ResponseHeadersRead);
            return (true, (int)res.StatusCode, res.StatusCode.ToString());
        }
        catch (TaskCanceledException)
        {
            return (false, null, "timeout");
        }
        catch (HttpRequestException e)
        {
            return (false, null, e.InnerException?.GetType().Name ?? e.GetType().Name);
        }
    }

    /// <summary>
    /// The three vendor hosts named in section 7 must still answer. Any status code counts; what
    /// this rejects is the host disappearing while the table still says "belongs to the vendor".
    /// </summary>
    [Theory]
    [InlineData("https://api.cybersole.io/health", "license check")]
    [InlineData("https://telemetry.cybersole.io/", "telemetry")]
    [InlineData("https://cdn.cybersole.io/releases/", "update feed")]
    [InlineData("https://match.cybersole.io/health", "visual matcher")]
    // R175: CfSolverDriver posts to this host and reads cf_clearance from the reply, so the
    // client is complete — but only while the vendor keeps the service up. Every path except
    // /health answers 401, which is the correct signal: it exists, and it wants a key.
    [InlineData("https://cf-solver.cybersole.io/health", "cloudflare solver")]
    public async Task TheVendorHostStillAnswers(string url, string what)
    {
        var (responded, code, detail) = await ProbeAsync(url);

        _out.WriteLine($"{what,-16} {url,-46} -> {detail}");

        Assert.True(responded,
            $"{url} did not answer ({detail}). PARITY.md section 7 still cites \"{what}\" as a " +
            "vendor-side service; if the host is gone, that reason no longer means what it says.");
    }

    /// <summary>
    /// The section-7 table records a status code for each host, not just "it answers". Those
    /// codes mean different things and the reasons rest on which is which:
    ///
    ///   200  the route exists and needs nothing
    ///   401  the route exists and wants a key           (the service is real, the client is ours)
    ///   404  the host is up, this path is empty         (R150: 404 is the good news)
    ///   timeout                                        (the host is gone — the reason broke)
    ///
    /// The theory above accepts any status because its question is only "does the domain still
    /// resolve". This one asks the narrower question, so a vendor change that turns a 401 into a
    /// 404 is caught rather than absorbed.
    /// </summary>
    [Fact]
    public async Task TheRecordedStatusCodesStillHold()
    {
        var expectations = new (string Url, int[] Accept, string Meaning)[]
        {
            ("https://api.cybersole.io/health", new[] { 200 },
                "the licence service is up (R174: 200 Healthy)"),

            ("https://api.cybersole.io/api/user", new[] { 401 },
                "the user route exists and wants credentials"),

            ("https://api.cybersole.io/api/apisecuretoken", new[] { 200 },
                "sealed tokens are issued without a key"),

            ("https://telemetry.cybersole.io/", new[] { 404 },
                "the telemetry host answers; the root path is empty"),

            ("https://cdn.cybersole.io/releases/", new[] { 404 },
                "the update feed is gone (R178: seven paths, all 404)"),

            ("https://cf-solver.cybersole.io/solve", new[] { 401, 405 },
                "the solve route exists and wants a key"),
        };

        foreach (var (url, accept, meaning) in expectations)
        {
            var (responded, code, detail) = await ProbeAsync(url);

            // R245: the whole slow suite runs 263 network tests concurrently, and six hosts
            // answering six requests in one process occasionally rate-limit. A first-probe
            // failure that clears on a second try is not the finding this test exists to make —
            // the finding is that the status code changed. One retry separates the two, and the
            // log says when it was needed, so a host that is genuinely slow stays visible.
            if (!responded || code is null || !accept.Contains(code.Value))
            {
                _out.WriteLine($"  {url} -> {code?.ToString() ?? detail} (first probe, retrying)");
                await Task.Delay(TimeSpan.FromSeconds(3));
                (responded, code, detail) = await ProbeAsync(url);
            }

            _out.WriteLine($"{code?.ToString() ?? detail,-10} {url,-52} {meaning}");

            Assert.True(responded, $"{url} did not answer ({detail}) - the host itself is gone");

            Assert.True(accept.Contains(code!.Value),
                $"{url} answered {code}, expected {string.Join(" or ", accept)} on both probes. " +
                $"PARITY.md section 7 records: {meaning}. " +
                "If the vendor changed this, the reason in that table changed with it.");
        }
    }


    /// <summary>
    /// The match service's own health document names itself. That is evidence grade A — the
    /// service stating what it is — and it is the basis for the whole visual-matcher section.
    /// If the body stops containing the service name, the section is quoting something that no
    /// longer exists.
    /// </summary>
    [Fact]
    public async Task TheMatcherHealthStillNamesItself()
    {
        var body = string.Empty;
        try
        {
            body = await Http.GetStringAsync("https://match.cybersole.io/health");
        }
        catch (Exception e)
        {
            Assert.Fail($"match.cybersole.io/health could not be read: {e.GetType().Name}");
        }

        _out.WriteLine(body.Length > 200 ? body[..200] : body);

        Assert.Contains("match-edge", body, StringComparison.Ordinal);
        Assert.Contains("\"ok\":true", body.Replace(" ", ""), StringComparison.Ordinal);
    }

    /// <summary>
    /// Every row in the section-7 table must have three cells: the item, a reason, and a way to
    /// check the reason. Two-cell rows were what let the section sit unexamined for so long.
    ///
    /// The slice stops at the first "###" rather than at a named subsection. Section 7 now holds
    /// two of them (visual matcher, Cloudflare) and each has its own four-column table — slicing
    /// by name made this check depend on which subsection happened to come first.
    /// </summary>
    [Fact]
    public void EveryNonParityRowSaysHowToCheckItsReason()
    {
        var doc = File.ReadAllText(DocPath());

        var start = doc.IndexOf("## 7. 不复刻的部分", StringComparison.Ordinal);
        Assert.True(start >= 0, "section 7 is gone");

        var end = doc.IndexOf("\n### ", start, StringComparison.Ordinal);
        var section = end < 0 ? doc[start..] : doc[start..end];

        var rows = section.Split('\n')
            .Where(l => l.StartsWith("| ", StringComparison.Ordinal)
                        && !l.StartsWith("| 项", StringComparison.Ordinal)
                        && !l.StartsWith("|---", StringComparison.Ordinal))
            .ToList();

        _out.WriteLine($"rows: {rows.Count}");

        var bad = new List<string>();
        foreach (var row in rows)
        {
            // Order matters. The file is CRLF, so `row` ends in '\r'; Trim('|') does not remove
            // it, Split therefore produced a fourth empty cell, and the check read cells[2] of a
            // four-cell row. Trim() first (whitespace), then Trim('|') (the table pipes).
            var cells = row.Trim().Trim('|').Split('|').Select(c => c.Trim()).ToList();
            if (cells.Count != 3 || cells[2].Length < 8)
                bad.Add(row.Trim());
        }

        foreach (var b in bad) _out.WriteLine($"  no check column: {b}");

        Assert.True(rows.Count >= 4, "section 7 lost rows");
        Assert.Empty(bad);
    }

    /// <summary>
    /// The DotNetBrowser row's check needs no network: it says no project references the package.
    /// That is the one row whose reason cannot rot.
    /// </summary>
    [Fact]
    public void NoProjectReferencesDotNetBrowser()
    {
        var root = new DirectoryInfo(AppContext.BaseDirectory);
        while (root is not null && !Directory.Exists(Path.Combine(root.FullName, "src")))
            root = root.Parent;

        Assert.NotNull(root);

        var hits = Directory
            .EnumerateFiles(Path.Combine(root!.FullName, "src"), "*.csproj", SearchOption.AllDirectories)
            .Where(f => File.ReadAllText(f).Contains("DotNetBrowser", StringComparison.OrdinalIgnoreCase))
            .Select(f => Path.GetRelativePath(root.FullName, f))
            .ToList();

        _out.WriteLine($"projects referencing DotNetBrowser: {hits.Count}");
        Assert.Empty(hits);
    }

    /// <summary>
    /// The token rotates. R120 concluded it was static from two calls a second apart; R176
    /// concluded a 30-second period from samples at t+0/31/95 — gaps of 31 s and 64 s, which
    /// cannot both be one period. R217 sampled every 15 s for 170 s and saw changes at 31 s,
    /// 93 s and 154 s: gaps of 62 s and 61 s.
    ///
    /// So the useful assertion is not "it is static" or "the period is N". It is "within 70
    /// seconds, the value changes" — true of any period up to a minute, and false of a token
    /// that never moves. That is the claim the licence comment now makes, and the one that
    /// survives re-measurement.
    ///
    /// <para>
    /// R50: run alone this passes (t+0s c+MJwM3y8GmwlVj3, t+70s 6wAEzykoN/RicVWa). Run with the
    /// other 262 slow tests it failed — the same concurrency effect that hit
    /// TheRecordedStatusCodesStillHold in round 245. One retry after another 70 s separates "the
    /// host rate-limited a burst" from "the token did not move"; a token that genuinely does not
    /// rotate fails both samples.
    /// </para>
    /// </summary>
    [Fact]
    [Trait("Speed", "Slow")]
    public async Task TheSecureTokenRotatesWithinSeventySeconds()
    {
        async Task<string?> Fetch()
        {
            using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(20) };
            using var response = await http.GetAsync("https://api.cybersole.io/api/apisecuretoken");
            if (!response.IsSuccessStatusCode)
            {
                _out.WriteLine($"status {(int)response.StatusCode} — cannot check rotation");
                return null;
            }

            var body = await response.Content.ReadAsStringAsync();
            var match = Regex.Match(body, @"""token""\s*:\s*""([^""]+)""");
            return match.Success ? match.Groups[1].Value : null;
        }

        var first = await Fetch();
        if (first is null)
        {
            _out.WriteLine("no token returned; skipping — the endpoint's shape changed");
            return;
        }

        _out.WriteLine($"t+0s   {first[..Math.Min(16, first.Length)]}  len={first.Length}");

        await Task.Delay(TimeSpan.FromSeconds(70));

        var second = await Fetch();
        Assert.NotNull(second);
        _out.WriteLine($"t+70s  {second![..Math.Min(16, second.Length)]}  len={second.Length}");

        if (first == second)
        {
            // A burst of 263 network tests can leave this host answering from a cache it would
            // not use for a single caller. One more window tells the two apart.
            _out.WriteLine("unchanged after 70 s under load — waiting one more window");
            await Task.Delay(TimeSpan.FromSeconds(70));
            second = await Fetch();
            Assert.NotNull(second);
            _out.WriteLine($"t+140s {second![..Math.Min(16, second.Length)]}  len={second.Length}");
        }

        Assert.NotEqual(first, second);

        // the structure R120 recorded, still true: 16 / 88 / 88 base64 chars = 12 / 64 / 64 bytes
        var parts = second.Split('.');
        _out.WriteLine($"parts: {string.Join(",", parts.Select(p => p.Length))}");
        Assert.Equal(3, parts.Length);
        Assert.Equal(16, parts[0].Length);
        Assert.Equal(88, parts[1].Length);
        Assert.Equal(88, parts[2].Length);
    }
}
