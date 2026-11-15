import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\VerifyRetryPolicyTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    /// <summary>The slow phase retries exactly once, and only when the first pass failed.</summary>
    [Fact]
    public void TheSlowPhaseRetriesOnce()
    {
        var script = Script();

        Assert.Contains("$slowRetried = $false", script);
        Assert.Contains("if ($slowExit -ne 0) {", script);
        Assert.Contains("[retry] slow tests failed once", script);

        // exactly two invocations of the slow filter: the first pass and the retry
        var runs = Regex.Matches(script, @"--filter ""Speed=Slow""").Count;
        _out.WriteLine($"{runs} slow-filter invocations");
        Assert.Equal(2, runs);
    }'''

new = '''    /// <summary>
    /// The slow phase re-runs the failing tests <b>individually</b> rather than the whole set.
    ///
    /// <para>
    /// Retrying the set was tried first and did not hold: the retry failed on a different live test
    /// than the first pass did (<c>TheSecureTokenRotates…</c>, then <c>AHundredTimesCallerStillG…</c>).
    /// Aiming the retry at the named tests is what separates "this host hiccuped" from "this code
    /// broke" — a broken test fails alone too.
    /// </para>
    /// </summary>
    [Fact]
    public void TheSlowPhaseRetriesTheNamedTestsOnly()
    {
        var script = Script();

        Assert.Contains("$slowRetried = $false", script);
        Assert.Contains("$flaked = @()", script);
        Assert.Contains("Cybersole\\\\.Tests\\\\.[A-Za-z0-9_]+\\\\.[A-Za-z0-9_]+", script);
        Assert.Contains("flaked in the set, green alone", script);
        Assert.Contains("still failing alone", script);

        // one invocation of the slow filter (the set), then per-name runs by FullyQualifiedName
        var setRuns = Regex.Matches(script, @"--filter ""Speed=Slow""").Count;
        var perTest = Regex.Matches(script, @"--filter ""FullyQualifiedName~\\$name""").Count;
        _out.WriteLine($"set runs={setRuns}, per-test runs={perTest}");

        Assert.Equal(1, setRuns);
        Assert.Equal(1, perTest);
    }

    /// <summary>
    /// A test that fails alone still fails the check — the re-run is not a way to launder a
    /// regression into a green run.
    /// </summary>
    [Fact]
    public void ATestThatFailsAloneStillFailsTheCheck()
    {
        var script = Script();

        Assert.Contains("if ($LASTEXITCODE -ne 0) {", script);
        Assert.Contains("$flaked += \\"still failing alone: $name\\"", script);
        Assert.Contains("$slowExit = if ($flaked | Where-Object { $_ -like 'still failing alone:*' }) { 1 } else { 0 }",
            script);

        _out.WriteLine("a lone failure forces the exit code back to 1");
    }'''

if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("retry-policy tests updated")
