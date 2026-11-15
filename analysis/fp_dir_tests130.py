import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BrowserFingerprintTests.cs"
t = io.open(p, encoding="utf-8").read()

anchor = "    /// <summary>The window size follows the screen, so the two never contradict each other.</summary>"
add = '''    /// <summary>
    /// The profile directory is derived from the same key as the fingerprint, so one profile key keeps
    /// one Chrome directory — the folder and the fingerprint describe the same identity.
    /// </summary>
    [Fact]
    public void TheProfileDirectoryComesFromTheSameKey()
    {
        var fp = BrowserFingerprint.ForProfile("task-7/profile-2");

        var dir = fp.ProfileDirectoryName("task-7/profile-2");
        var arg = fp.ProfileDirectoryArgument("task-7/profile-2");

        _out.WriteLine($"{dir} / {arg}");

        Assert.StartsWith("Profile ", dir, System.StringComparison.Ordinal);
        Assert.Equal("--profile-directory=" + dir, arg);

        // the numbered folders the image ships are exactly this shape
        var number = int.Parse(dir.Substring("Profile ".Length));
        Assert.InRange(number, 0, 8);
    }

    /// <summary>Different keys land on different directories at least sometimes.</summary>
    [Fact]
    public void DifferentKeysSpreadAcrossDirectories()
    {
        var dirs = Enumerable.Range(0, 30)
            .Select(i => BrowserFingerprint.ForProfile("p" + i).ProfileDirectoryName("p" + i))
            .Distinct()
            .ToList();

        _out.WriteLine(string.Join(", ", dirs));
        Assert.True(dirs.Count >= 5, $"only {dirs.Count} directories across 30 profiles");
    }

    /// <summary>The window size follows the screen, so the two never contradict each other.</summary>'''

if anchor not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add, 1))
print("profile directory tests added")
