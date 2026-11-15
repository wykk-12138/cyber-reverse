import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\VerifyRetryPolicyTests.cs"
t = io.open(p, encoding="utf-8").read()

# The set filter changed in R109: it now excludes the Kasada group, so the literal counted by this
# test is the new one. Count occurrences of the *set* filter, which is still invoked twice
# (first pass + retry).
old = '''        var runs = Regex.Matches(script, @"--filter ""Speed=Slow""").Count;
        _out.WriteLine($"{runs} slow-set invocations");
        Assert.Equal(2, runs);'''

new = '''        // R109 split the phase: the set filter now excludes the Kasada group, and that filter is
        // still invoked twice (first pass + retry).
        var runs = Regex.Matches(script, @"--filter ""Speed=Slow&FullyQualifiedName!~Kasada""").Count;
        var kasada = Regex.Matches(script, @"--filter ""Speed=Slow&FullyQualifiedName~Kasada""").Count;
        _out.WriteLine($"{runs} set invocations, {kasada} kasada invocations");

        Assert.Equal(2, runs);
        Assert.Equal(1, kasada);'''

if old not in t:
    raise SystemExit("count anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("count test updated for the split")
