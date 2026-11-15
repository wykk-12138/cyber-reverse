import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\KeyOrderTableTests.cs"
t = io.open(p, encoding="utf-8").read()

t = t.replace('''        // unwired, the entry points are the engine's own — recorded so the baseline is not guessed at later
        var sources = await bridge.EvaluateAsync(''',
'''        // Unwired, the entry points are the engine's own functions — and the cloak (R172) reformats every native source
        // into WebKit's three-line form, so three lines each is the correct baseline, not one.
        var sources = await bridge.EvaluateAsync(''', 1)

t = t.replace('Assert.Equal("[1,1]", sources);', 'Assert.Equal("[3,3]", sources);', 1)
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("baseline corrected")
