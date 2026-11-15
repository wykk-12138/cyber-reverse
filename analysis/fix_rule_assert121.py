import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\GraphQlCartStepTests.cs"
t = io.open(p, encoding="utf-8").read()

# The Rule string reads "pool adjacency is not class membership" — assert exactly that wording.
old = '''        Assert.Contains("Pool adjacency", GraphQlCartSteps.Rule.Replace("not — pool", "not — pool"));'''
new = '''        Assert.Contains("pool adjacency is not", GraphQlCartSteps.Rule,
            System.StringComparison.OrdinalIgnoreCase);'''

if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("assertion now matches the recorded wording")
