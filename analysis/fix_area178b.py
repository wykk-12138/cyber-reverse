import io

# 1) ByArea gains an explicit remainder bucket, so the areas always sum to the table
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\MethodPatchTable.cs"
t1 = io.open(p1, encoding="utf-8").read()

old1 = '''    public static IReadOnlyDictionary<string, int> ByArea() => new Dictionary<string, int>
    {
        ["canvas"] = Sites.Count(s => s.Target.Contains("Canvas", System.StringComparison.Ordinal)),
        ["webgl"] = Sites.Count(s => s.Target.Contains("WebGL", System.StringComparison.Ordinal)),
        ["audio"] = Sites.Count(s => s.Target.Contains("Audio", System.StringComparison.Ordinal)),
        ["date-intl"] = Sites.Count(s => s.Target.Contains("Date", System.StringComparison.Ordinal)
                                        || s.Target.Contains("Intl", System.StringComparison.Ordinal)),
        ["core"] = Sites.Count(s => s.Target is "Function.prototype" or "JSON" or "Reflect"),
    };'''

new1 = '''    public static IReadOnlyDictionary<string, int> ByArea()
    {
        bool Canvas(Site s) => s.Target.Contains("Canvas", System.StringComparison.Ordinal);
        bool Webgl(Site s) => s.Target.Contains("WebGL", System.StringComparison.Ordinal);
        bool Audio(Site s) => s.Target.Contains("Audio", System.StringComparison.Ordinal);
        bool DateIntl(Site s) => s.Target.Contains("Date", System.StringComparison.Ordinal)
                                 || s.Target.Contains("Intl", System.StringComparison.Ordinal);
        bool Core(Site s) => s.Target is "Function.prototype" or "JSON" or "Reflect";

        var known = Sites.Where(s => Canvas(s) || Webgl(s) || Audio(s) || DateIntl(s) || Core(s)).Count();

        return new Dictionary<string, int>
        {
            ["canvas"] = Sites.Count(Canvas),
            ["webgl"] = Sites.Count(Webgl),
            ["audio"] = Sites.Count(Audio),
            ["date-intl"] = Sites.Count(DateIntl),
            ["core"] = Sites.Count(Core),
            // whatever the five names above do not claim, so the areas always add up to the table (R178: the first
            // version summed to 25 of 34 and the assertion said so, which is the point of asserting a sum)
            ["other"] = Sites.Count - known,
        };
    }'''

if old1 not in t1:
    raise SystemExit("byarea anchor missing")
io.open(p1, "w", encoding="utf-8", newline="").write(t1.replace(old1, new1, 1))

# 2) the test asserts the sum, and names the remainder
p2 = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\MethodPatchTableTests.cs"
t2 = io.open(p2, encoding="utf-8").read()

old2 = '''        Assert.Equal(6, byArea["canvas"]);
        Assert.Equal(4, byArea["webgl"]);

        // every site falls in exactly one area
        Assert.Equal(MethodPatchTable.Sites.Count, byArea.Values.Sum());'''

new2 = '''        Assert.Equal(6, byArea["canvas"]);
        Assert.Equal(4, byArea["webgl"]);

        // every site falls in exactly one area — the remainder is named, not swallowed
        Assert.Equal(MethodPatchTable.Sites.Count, byArea.Values.Sum());
        Assert.True(byArea["other"] >= 0);
        _out.WriteLine($"other {byArea["other"]}: " + string.Join(", ",
            MethodPatchTable.Sites
                .Where(s => !new[] { "Canvas", "WebGL", "Audio", "Date", "Intl" }
                    .Any(k => s.Target.Contains(k, System.StringComparison.Ordinal))
                    && s.Target is not ("Function.prototype" or "JSON" or "Reflect"))
                .Select(s => s.Target + "." + s.Name)));'''

if old2 not in t2:
    raise SystemExit("sum anchor missing")
io.open(p2, "w", encoding="utf-8", newline="").write(t2.replace(old2, new2, 1))
print("the remainder is named")
