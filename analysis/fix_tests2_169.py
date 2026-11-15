import io

# 1) NavPruneTests: the whitelist body carries the kept names, not the deleted ones
p1 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\NavPruneTests.cs"
t1 = io.open(p1, encoding="utf-8").read()

t1 = t1.replace('''        Assert.Contains("key !== 'constructor'", js);
        Assert.Contains("'connection'", js);''',
'''        Assert.Contains("key !== 'constructor'", js);

        // the allowlist is what the body carries; `connection` is deliberately not on it
        Assert.Contains("'plugins'", js);
        Assert.Contains("'mimeTypes'", js);
        Assert.DoesNotContain("'connection'", js);''', 1)

io.open(p1, "w", encoding="utf-8", newline="").write(t1)

# 2) RealmReplayTests: the plugin patch was removed in R169, so its marker goes with it
p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\RealmReplayTests.cs"
t2 = io.open(p2, encoding="utf-8").read()

t2 = t2.replace('"\'plugins\'",                // 3\n', "", 1)
t2 = t2.replace('"\'languages\'",              // 4', '"\'languages\'",              // 3', 1)
t2 = t2.replace('"permissions.query",        // 5', '"permissions.query",        // 4', 1)
t2 = t2.replace('"getParameter",             // 6', '"getParameter",             // 5', 1)
t2 = t2.replace('"\'hardwareConcurrency\'",    // 7', '"\'hardwareConcurrency\'",    // 6', 1)
t2 = t2.replace('"\'outerWidth\'",             // 8', '"\'outerWidth\'",             // 7', 1)

io.open(p2, "w", encoding="utf-8", newline="").write(t2)
print("both tests follow R169")
