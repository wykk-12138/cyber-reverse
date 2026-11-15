import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\VerifyRetryPolicyTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    /// <summary>The retry is recorded, so a green-on-retry run is not reported as a clean one.</summary>
    [Fact]
    public void AGreenOnRetryRunSaysSo()
    {
        var script = Script();

        Assert.Contains("green on retry (first pass had a live-network failure)", script);
        Assert.Contains("if ($slowOk -and $slowRetried)", script);

        _out.WriteLine("retry-aware detail present");
    }'''

new = '''    /// <summary>
    /// A run rescued by individual re-runs says so, per test — a green run must not be reported as
    /// if the set had passed cleanly.
    /// </summary>
    [Fact]
    public void AGreenAfterRerunsSaysSo()
    {
        var script = Script();

        Assert.Contains("green after individual re-runs: ", script);
        Assert.Contains("if ($slowOk -and $slowRetried)", script);
        Assert.Contains("$flaked -join '; '", script);

        _out.WriteLine("retry-aware detail present");
    }'''

if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("detail test updated")
