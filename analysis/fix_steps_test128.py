import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\VerifyStepsTests.cs"
t = io.open(p, encoding="utf-8").read()

old_name = "public void ThereAreSevenNamedSteps()"
new_name = "public void ThereAreEightNamedSteps()"
if old_name in t:
    t = t.replace(old_name, new_name, 1)

old = '''        Assert.Equal(new[]
        {
            "release build", "unit tests", "slow (network)", "slow (kasada live)",
            "store modules", "docs present", "mutation guards",
        }, names);'''
new = '''        Assert.Equal(new[]
        {
            "release build", "unit tests", "slow (network)", "slow (kasada live)",
            "store modules", "docs present", "mutation guards", "endpoint provenance",
        }, names);'''
if old not in t:
    raise SystemExit("names anchor missing")
t = t.replace(old, new, 1)

if "/// Seven steps, each named, no duplicates." in t:
    t = t.replace("/// Seven steps, each named, no duplicates.",
                  "/// Eight steps, each named, no duplicates.", 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("VerifyStepsTests expects eight steps")
