import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\VerifyRetryPolicyTests.cs"
t = io.open(p, encoding="utf-8").read()

anchor = "    /// <summary>\n    /// A retry that fails again still fails the check"
add = '''    /// <summary>
    /// Round 109: the Kasada live group is its own check.
    ///
    /// <para>
    /// That group downloads and evaluates a real Kasada script. In R109 it ran past five minutes and
    /// had to be killed — and while it was inside the same check as everything else, a hang there
    /// erased every other live result. Split out, a Kasada problem is attributable to Kasada.
    /// </para>
    /// </summary>
    [Fact]
    public void TheKasadaGroupIsItsOwnCheck()
    {
        var script = Script();

        Assert.Contains("FullyQualifiedName!~Kasada", script);   // the rest, excluding it
        Assert.Contains("FullyQualifiedName~Kasada", script);    // the group on its own
        Assert.Contains("Check 'slow tests (kasada live)'", script);
        Assert.Contains("kasada live group green", script);

        // the two filters are distinct checks, not one
        Assert.Contains("Check 'slow tests (Speed=Slow)'", script);

        _out.WriteLine("two live checks: network group + kasada group");
    }

'''

if anchor not in t:
    raise SystemExit("anchor missing")
if "TheKasadaGroupIsItsOwnCheck" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("kasada-split test added")
