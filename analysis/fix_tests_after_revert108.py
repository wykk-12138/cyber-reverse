import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\VerifyRetryPolicyTests.cs"
t = io.open(p, encoding="utf-8").read()

# The targeted per-test re-run was tried and reverted in the same round: it is more precise but the
# run produced no output twice in a row on this machine, which is a worse failure mode than a retry.
start = t.find("    /// <summary>\n    /// The slow phase re-runs the failing tests <b>individually</b>")
end = t.find("    /// <summary>\n    /// A test that fails alone still fails the check")
if start < 0 or end < 0:
    raise SystemExit("block bounds: %d %d" % (start, end))

new = '''    /// <summary>
    /// The slow phase retries the filtered set exactly once, and only when the first pass failed.
    ///
    /// <para>
    /// A targeted per-test re-run was written first and reverted the same round: it is more precise,
    /// but on this machine the full run produced no output at all twice in a row with it in place,
    /// and "the judge hung" is a worse failure than "the judge retried". The set retry is the version
    /// that runs.
    /// </para>
    /// </summary>
    [Fact]
    public void TheSlowPhaseRetriesTheSetOnce()
    {
        var script = Script();

        Assert.Contains("$slowRetried = $false", script);
        Assert.Contains("[retry] slow tests failed once", script);
        Assert.DoesNotContain("$flaked", script);

        var runs = Regex.Matches(script, @"--filter ""Speed=Slow""").Count;
        _out.WriteLine($"{runs} slow-set invocations");
        Assert.Equal(2, runs);
    }

'''

t = t[:start] + new + t[end:]

# the detail assertion follows the reverted wording
t = t.replace('Assert.Contains("green after individual re-runs: ", script);',
              'Assert.Contains("green on retry (first pass lost a live host)", script);')
t = t.replace('Assert.Contains("$flaked -join \'; \'", script);',
              'Assert.Contains("$slowRetried", script);')

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("tests follow the reverted implementation")
