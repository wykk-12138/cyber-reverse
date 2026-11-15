import io, re

files = [
    r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\MobileNavigatorTests.cs",
    r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\JsParseTests.cs",
]

for p in files:
    t = io.open(p, encoding="utf-8").read()

    # every call site now takes the agent; the captured appVersion is the same string the bridge sends
    t = t.replace("MobileNavigator.BodyJs()",
                  'MobileNavigator.BodyJs(MobileNavigator.Captured["appVersion"])')

    if p.endswith("MobileNavigatorTests.cs"):
        t = t.replace("Assert.Equal(7, MobileNavigator.Captured.Count);",
                      "Assert.Equal(15, MobileNavigator.Captured.Count);")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("updated", p.split("\\")[-1])
