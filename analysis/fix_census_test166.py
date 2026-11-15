import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavigatorCensusTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        Assert.Contains("WebAuthn", NavigatorCensus.Deferred["credentials"]);
        Assert.Contains("stub", NavigatorCensus.Deferred["serviceWorker"]);'''

new = '''        Assert.Contains("WebAuthn", NavigatorCensus.Deferred["credentials"]);

        // the serviceWorker reason says a shim that never registers is itself a tell; the word to look for is
        // the sentence the reason actually uses
        Assert.Contains("never registers", NavigatorCensus.Deferred["serviceWorker"]);'''

if old not in t:
    raise SystemExit("reason anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the reason assertion quotes the reason")
