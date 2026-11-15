using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 130: the profile/fingerprint mechanism YG pointed at, and the gap it exposed.
///
/// <para>
/// The image carries <c>Fingerprint.template.json</c>, a <c>Fingerprint</c> class whose backing fields
/// are <c>ColorDepth, DeviceMemory, HardwareConcurrency, PixelRatio, ScreenWidth, ScreenHeight,
/// AvailableScreenWidth, AvailableScreenHeight</c>, the Chromium switches <c>--profile-directory=</c>
/// and <c>user-data-dir</c>, and numbered profile folders. That is a template filled per profile, with
/// every profile its own Chrome identity — the variety a bot wall needs before it will issue a
/// token.
/// </para>
///
/// <para>
/// The replica hardcoded <c>hardwareConcurrency = 8</c> and <c>deviceMemory = 8</c> for every run and
/// never set the six screen fields, so two sessions from one install reported identical hardware —
/// which is the first thing a fingerprint check looks at.
/// </para>
/// </summary>
public sealed class BrowserFingerprintTests
{
    private readonly ITestOutputHelper _out;

    public BrowserFingerprintTests(ITestOutputHelper output) => _out = output;

    /// <summary>The model has the eight fields the image lists.</summary>
    [Fact]
    public void TheModelHasTheImagesEightFields()
    {
        Assert.Equal(new[]
        {
            "ColorDepth", "DeviceMemory", "HardwareConcurrency", "PixelRatio",
            "ScreenWidth", "ScreenHeight", "AvailableScreenWidth", "AvailableScreenHeight",
        }, BrowserFingerprint.Fields);

        Assert.Equal("Fingerprint.template.json", BrowserFingerprint.TemplateFile);
        Assert.Equal("--window-size=363,684", BrowserFingerprint.ObservedWindowSize);
    }

    /// <summary>
    /// A profile's fingerprint is stable across calls — the same profile must not look like two
    /// different machines.
    /// </summary>
    [Fact]
    public void AFingerprintIsStablePerProfile()
    {
        var a = BrowserFingerprint.ForProfile("task-1/profile-3");
        var b = BrowserFingerprint.ForProfile("task-1/profile-3");

        Assert.Equal(a, b);
        _out.WriteLine($"stable: {a.ScreenWidth}x{a.ScreenHeight} {a.HardwareConcurrency} cores");
    }

    /// <summary>Different profiles get different screens and hardware.</summary>
    [Fact]
    public void DifferentProfilesDiffer()
    {
        var seen = new HashSet<string>();
        for (var i = 0; i < 12; i++)
        {
            var fp = BrowserFingerprint.ForProfile($"profile-{i}");
            var key = $"{fp.ScreenWidth}x{fp.ScreenHeight}/{fp.HardwareConcurrency}/{fp.DeviceMemory}";
            seen.Add(key);
            _out.WriteLine($"profile-{i,-3} {key} ratio {fp.PixelRatio}");
        }

        Assert.True(seen.Count >= 4, $"only {seen.Count} distinct fingerprints across 12 profiles");
    }

    /// <summary>Every generated fingerprint is internally consistent.</summary>
    [Fact]
    public void EveryFingerprintIsConsistent()
    {
        for (var i = 0; i < 20; i++)
        {
            var fp = BrowserFingerprint.ForProfile($"p{i}");

            Assert.True(fp.AvailableScreenWidth <= fp.ScreenWidth);
            Assert.True(fp.AvailableScreenHeight < fp.ScreenHeight);
            Assert.InRange(fp.HardwareConcurrency, 2, 32);
            Assert.Contains(fp.DeviceMemory, new[] { 4, 8, 16 });
            Assert.Contains(fp.PixelRatio, new[] { 1.0, 1.25 });
        }
    }

    /// <summary>The injected script sets all eight fields, with the profile's values.</summary>
    [Fact]
    public void TheScriptSetsAllEightFields()
    {
        var fp = new BrowserFingerprint
        {
            ColorDepth = 30, DeviceMemory = 16, HardwareConcurrency = 12, PixelRatio = 1.25,
            ScreenWidth = 1536, ScreenHeight = 864, AvailableScreenWidth = 1536, AvailableScreenHeight = 824,
        };

        var js = fp.ToJavaScript();

        foreach (var expected in new[]
                 {
                     "'hardwareConcurrency', { get: () => 12",
                     "'deviceMemory', { get: () => 16",
                     "'devicePixelRatio', { get: () => 1.25",
                     "'width', { get: () => 1536",
                     "'height', { get: () => 864",
                     "'availWidth', { get: () => 1536",
                     "'availHeight', { get: () => 824",
                     "'colorDepth', { get: () => 30",
                 })
            Assert.Contains(expected, js, System.StringComparison.Ordinal);

        // braces balance, so the script parses
        Assert.Equal(js.Count(c => c == '{'), js.Count(c => c == '}'));
    }

    /// <summary>
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

    /// <summary>The window size follows the screen, so the two never contradict each other.</summary>
    [Fact]
    public void TheWindowFitsInsideTheScreen()
    {
        var fp = BrowserFingerprint.ForProfile("size-check");
        var arg = fp.WindowSizeArgument();

        Assert.StartsWith("--window-size=", arg, System.StringComparison.Ordinal);
        _out.WriteLine(arg);

        var parts = arg.Substring("--window-size=".Length).Split(',');
        Assert.Equal(2, parts.Length);
        Assert.True(int.Parse(parts[0]) < fp.ScreenWidth);
        Assert.True(int.Parse(parts[1]) < fp.ScreenHeight);
    }
}
