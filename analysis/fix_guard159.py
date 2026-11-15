import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\JsGuard.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    /// <summary>Every generated body in the workspace, with the name a failure should report.</summary>'''

new = '''    /// <summary>
    /// The agent the phone body needs, so the guard exercises the same code the bridge does rather than a stub.
    /// </summary>
    public const string SampleAgent =
        "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) AppleWebKit/605.1.15 " +
        "(KHTML, like Gecko) CriOS/156.0.8078.54 Mobile/15E148 Safari/604.1";

    /// <summary>Every generated body in the workspace, with the name a failure should report.</summary>'''

if old not in t:
    raise SystemExit("allbodies doc anchor missing")
t = t.replace(old, new, 1)

t = t.replace('("Touches", MobileNavigator.BodyJs()),',
              '("Touches", MobileNavigator.BodyJs(SampleAgent)),', 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the guard passes a real agent")
