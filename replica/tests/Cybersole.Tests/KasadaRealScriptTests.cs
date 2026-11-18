using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R17: run a real Kasada payload through the local Jint pipeline.
///
/// The fixture is Nike's own <c>p.js</c> (157 KB, fetched from api.nike.com). This is the
/// capability the original is known for, so it deserves a test against the genuine article
/// rather than a hand-written stand-in — including an honest record of how far it gets.
/// </summary>
public class KasadaRealScriptTests
{
    private readonly ITestOutputHelper _out;
    public KasadaRealScriptTests(ITestOutputHelper output) => _out = output;

    private static string FixturePath()
    {
        var dir = AppContext.BaseDirectory;
        for (var i = 0; i < 8 && dir is not null; i++)
        {
            var candidate = Path.Combine(dir, "fixtures", "nike-p.js");
            if (File.Exists(candidate)) return candidate;

            var nested = Path.Combine(dir, "tests", "Cybersole.Tests", "fixtures", "nike-p.js");
            if (File.Exists(nested)) return nested;

            dir = Path.GetDirectoryName(dir);
        }

        throw new FileNotFoundException("fixtures/nike-p.js not found next to the test binary");
    }

    [Fact]
    public void TheFixtureIsTheRealPayload()
    {
        var script = File.ReadAllText(FixturePath());

        Assert.True(script.Length > 100_000, $"expected >100KB, got {script.Length}");
        Assert.Contains("use strict", script[..64]);
    }

    [Fact]
    public void JintRunsThePayloadDeepIntoKasadasOwnVM()
    {
        var script = File.ReadAllText(FixturePath());

        using var solver = new KasadaSolver();
        var executed = solver.Runtime.TryExecute(script, out var error);

        var percent = solver.Runtime.LastErrorColumn * 100.0 / script.Length;
        _out.WriteLine($"executed={executed} stopped at offset {solver.Runtime.LastErrorColumn} " +
                       $"({percent:0.0}% of {script.Length}) error={error}");

        if (!executed)
        {
            // It fails inside Kasada's bytecode interpreter — but it has to have got through
            // the bootstrap, the string table and the decoder first. Anything less than 80%
            // means the sandbox is broken rather than the payload being demanding.
            Assert.True(percent > 80.0,
                $"only reached {percent:0.0}% before failing: {error}");
        }
    }

    [Fact]
    public void TheSolverExplainsWhyItCouldNotProduceAToken()
    {
        var script = File.ReadAllText(FixturePath());

        using var solver = new KasadaSolver();
        var result = solver.Solve(script);

        _out.WriteLine($"ok={result.Ok} executed={result.ScriptExecuted} " +
                       $"stoppedAt={result.StoppedAt} needsBrowser={result.NeedsRealBrowser}");
        _out.WriteLine($"error={result.Error}");

        if (result.Ok)
        {
            Assert.False(string.IsNullOrWhiteSpace(result.Ct));
            Assert.True(result.Ct!.Length >= 16);
            Assert.True(result.ScriptExecuted);
        }
        else
        {
            // A silent empty result would be worse than a failure: the caller has to know
            // whether to retry, give up, or fall back to an embedded browser.
            Assert.NotNull(result.Error);

            // Three distinct outcomes, and they mean different things to the caller:
            //   * the script threw part way through      -> StoppedAt > 0, or the message says so
            //   * it ran to the end but exposed no token -> the host surface is now complete enough
            //     for execution, and what remains is token extraction (see KasadaErrorNoToken)
            Assert.True(
                result.StoppedAt > 0
                || result.Error!.Contains("threw")
                || result.ScriptExecuted,
                $"unexpected failure shape: executed={result.ScriptExecuted} stoppedAt={result.StoppedAt} err={result.Error}");
        }
    }

    [Fact]
    public void AHostApiGapIsFlaggedAsNeedingARealBrowser()
    {
        using var solver = new KasadaSolver();

        // A tiny payload that reproduces the exact failure shape the real one hits.
        var result = solver.Solve("var host = {}; host.missing.bind(null);");

        Assert.False(result.Ok);
        Assert.False(result.ScriptExecuted);
        Assert.True(result.NeedsRealBrowser,
            "a missing host function must be reported as a browser requirement, not a syntax error");
    }

    [Fact]
    public void ASyntaxErrorIsNotFlaggedAsABrowserRequirement()
    {
        using var solver = new KasadaSolver();
        var result = solver.Solve("function {{{ broken");

        Assert.False(result.Ok);
        Assert.False(result.NeedsRealBrowser);
    }

    [Fact]
    public void ScriptUrlMatchingHandlesNikesCrossOriginPath()
    {
        const string html = """
            <html><body>
            <script type="application/javascript"
                    src="https://api.nike.com/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/p.js"></script>
            </body></html>
            """;

        var found = KasadaSolver.FindScriptUrl(html, "https://www.nike.com/launch/t/air-max");

        Assert.NotNull(found);
        Assert.StartsWith("https://api.nike.com/", found);
        Assert.EndsWith("/p.js", found);
    }

    [Fact]
    public void ScriptUrlMatchingStillHandlesClassicIpsJs()
    {
        const string html = """<script src="/a1b2c3d4/ips.js"></script>""";
        var found = KasadaSolver.FindScriptUrl(html, "https://www.footlocker.com/x");

        Assert.NotNull(found);
        Assert.Equal("https://www.footlocker.com/a1b2c3d4/ips.js", found);
    }
}
