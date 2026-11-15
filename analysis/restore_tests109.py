import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\VerifyRetryPolicyTests.cs"
t = io.open(p, encoding="utf-8").read()

# Two tests were lost in R108 when the file was truncated at the last closing brace. Restore them,
# plus the marker check, so the class covers what it claims to.
anchor = "    /// <summary>\n    /// A retry that fails again still fails the check"

add = '''    /// <summary>
    /// A run rescued by the retry says so — a green run must not be reported as if the set had
    /// passed cleanly.
    /// </summary>
    [Fact]
    public void AGreenOnRetryRunSaysSo()
    {
        var script = Script();

        Assert.Contains("green on retry (first pass lost a live host)", script);
        Assert.Contains("if ($slowOk -and $slowRetried)", script);
        Assert.Contains("$slowRetried = $true", script);

        _out.WriteLine("retry-aware detail present");
    }

    /// <summary>
    /// A retry that fails again still fails the check — the retry is not a way to launder a
    /// regression into a green run, because the verdict reads the exit code of the last pass.
    /// </summary>
    [Fact]
    public void TheVerdictReadsTheLastExitCode()
    {
        var script = Script();

        Assert.Contains("$slowExit = $LASTEXITCODE", script);
        Assert.Contains("$slowOk = ($slowExit -eq 0)", script);
        Assert.Contains("Check 'slow tests (Speed=Slow)' $slowOk $slowDetail", script);
    }

    /// <summary>
    /// The script carries no merge markers or leftover notes.
    ///
    /// <para>
    /// Brace counting was tried and rejected: the script contains braces inside format strings and
    /// regexes, so a naive count reads 67 open / 68 close on a file the PowerShell parser accepts.
    /// The real parse check is <c>analysis/parse_check108.ps1</c>.
    /// </para>
    /// </summary>
    [Fact]
    public void TheScriptHasNoLeftoverMarkers()
    {
        var script = Script();

        Assert.DoesNotContain("<<<<<<<", script);
        Assert.DoesNotContain(">>>>>>>", script);
        Assert.DoesNotContain("TODO", script);

        _out.WriteLine($"{script.Length} characters, no merge markers");
    }

'''

if anchor not in t:
    raise SystemExit("anchor missing")
if "AGreenOnRetryRunSaysSo" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("restored AGreenOnRetryRunSaysSo, TheVerdictReadsTheLastExitCode, TheScriptHasNoLeftoverMarkers")
