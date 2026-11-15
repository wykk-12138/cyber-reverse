import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\VerifyRetryPolicyTests.cs"
t = io.open(p, encoding="utf-8").read()

# That test asserted the targeted-re-run behaviour, which was reverted. Replace it with the property
# that still matters: a second failing pass fails the check.
start = t.find("    /// <summary>\n    /// A test that fails alone still fails the check")
end = t.rfind("}")

if start < 0:
    raise SystemExit("block not found")

new = '''    /// <summary>
    /// A retry that fails again still fails the check — the retry is not a way to launder a
    /// regression into a green run, because the verdict reads the exit code of the last pass.
    /// </summary>
    [Fact]
    public void AFailingRetryStillFailsTheCheck()
    {
        var script = Script();

        // the retry reassigns both the output and the exit code
        Assert.Contains("$slow = & $dotnet test", script);
        Assert.Contains("$slowExit = $LASTEXITCODE", script);

        // and the check keys off that final code
        Assert.Contains("$slowOk = ($slowExit -eq 0)", script);
        Assert.Contains("Check 'slow tests (Speed=Slow)' $slowOk $slowDetail", script);

        _out.WriteLine("a failing retry leaves the verdict FAIL");
    }
'''

t = t[:start] + new + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("replaced with the failing-retry property")
