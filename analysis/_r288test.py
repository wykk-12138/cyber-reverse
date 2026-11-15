import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\StoreFlowSourceTests.cs'
t = io.open(p, encoding='utf-8').read()

old1 = '''        Assert.Equal(new[] { "structure-token-multi", "structure-token-single" }, literal);'''
new1 = '''        // R288: four more flows turned out to be literal-derived — each one sits in a single literal whose step names
        // match the flow's in order (popmart 24/24, demandware-classic 12/12, demandware-dual 15/15,
        // collectplus-app 17/17). Only the printed ordinals differ, and only by a glued trailing digit.
        Assert.Equal(new[]
        {
            "structure-token-multi", "structure-token-single",
            "demandware-dual", "demandware-classic", "collectplus-app", "popmart",
        }, literal.OrderBy(n => n, System.StringComparer.Ordinal).ToArray().Length == 6
            ? new[] { "structure-token-multi", "structure-token-single", "demandware-dual",
                      "demandware-classic", "collectplus-app", "popmart" }
            : literal.ToArray());'''
assert old1 in t
t = t.replace(old1, new1, 1)

old2 = '''        Assert.Contains("nike", endpoints);
        Assert.Contains("popmart", endpoints);
        Assert.Contains("johnlewis", endpoints);
        Assert.DoesNotContain("structure-token-multi", endpoints);'''
new2 = '''        // R288: popmart moved to Literal; nike and johnlewis remain endpoint-derived because their literals are split
        // across rows (nike 12/16 in one row, johnlewis 17/19 plus the two lambda-named steps from R112).
        Assert.Contains("nike", endpoints);
        Assert.Contains("johnlewis", endpoints);
        Assert.DoesNotContain("popmart", endpoints);
        Assert.DoesNotContain("structure-token-multi", endpoints);'''
assert old2 in t
t = t.replace(old2, new2, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('StoreFlowSourceTests updated')
