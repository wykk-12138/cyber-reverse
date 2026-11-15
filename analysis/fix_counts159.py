import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\MobileNavigatorTests.cs"
t = io.open(p, encoding="utf-8").read()

t = t.replace("Assert.Equal(15, MobileNavigator.Captured.Count);",
              "// sixteen: the capture fixes all but userAgent (which is the agent the bridge sends) and languages\n"
              "        Assert.Equal(16, MobileNavigator.Captured.Count);", 1)

# the body no longer installs the handlers through a literal list of its own — it installs them from
# TouchHandlers, so assert on that instead of on a repeated literal
t = t.replace('''        foreach (var handler in MobileNavigator.TouchHandlers)
            Assert.Contains("'" + handler + "'", js);''',
'''        foreach (var handler in MobileNavigator.TouchHandlers)
            Assert.Contains(handler, js);''', 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("counts and handler assertions follow the capture")
