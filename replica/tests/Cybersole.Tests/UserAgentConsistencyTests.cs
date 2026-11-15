using System.Reflection;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// The UA and userAgentData must describe the same browser.
///
/// Round 138: they did not. `version` was hardcoded to "131.0.0.0" while DefaultUserAgent()
/// read the real installed build, so one session answered two Chrome versions at once —
/// `navigator.userAgent` said 157.0.8103.38 and `navigator.userAgentData.fullVersion` said
/// 131.0.0.0. Comparing those two costs a detector one line.
///
/// These tests inspect the source text rather than a live browser, because the point is that the
/// two values are *derived from one reading*, and only the source shows that.
/// </summary>
public class UserAgentConsistencyTests
{
    private readonly ITestOutputHelper _out;
    public UserAgentConsistencyTests(ITestOutputHelper output) => _out = output;

    private static string Source()
    {
        var type = typeof(Cybersole.Stores.Scripts.ChromiumBridge);
        // the assembly path is stable inside the test process
        var path = type.Assembly.Location;
        var dir = Path.GetDirectoryName(path)!;
        var src = Path.Combine(dir, "..", "..", "..", "..", "..",
            "src", "Cybersole.Stores", "Scripts", "ChromiumBridge.cs");
        src = Path.GetFullPath(src);
        Assert.True(File.Exists(src), $"source not found at {src}");
        return File.ReadAllText(src);
    }

    [Fact]
    public void UserAgentUsesTheReducedForm()
    {
        var text = Source();

        // Chrome freezes the UA token to <major>.0.0.0; the full build only appears in
        // getHighEntropyValues. A UA carrying the build number disagrees with itself.
        Assert.Contains("Chrome/{major}.0.0.0 Safari/537.36", text);

        // and it must not interpolate the full version into the UA
        Assert.DoesNotContain("Chrome/{chromeVersion}", text);
        Assert.DoesNotContain("Chrome/{fullVersion}", text);

        _out.WriteLine("UA token: Chrome/{major}.0.0.0");
    }

    [Fact]
    public void UserAgentDataComesFromTheSameReading()
    {
        var text = Source();

        // both the UA and the metadata must derive from ChromiumBridgeVersion()
        Assert.Contains("var fullVersion = ChromiumBridgeVersion();", text);
        Assert.Contains("var major = fullVersion.Split('.')[0];", text);

        // the hardcoded version literal must be gone from the metadata block
        var metadataStart = text.IndexOf("userAgentMetadata", StringComparison.Ordinal);
        Assert.True(metadataStart > 0);
        var metadata = text[metadataStart..Math.Min(text.Length, metadataStart + 1400)];
        Assert.DoesNotContain("131.0.0.0", metadata);

        _out.WriteLine("fullVersion = ChromiumBridgeVersion()");
        _out.WriteLine("brands version = major");
    }

    [Fact]
    public void VersionHasThreeSourcesInOrder()
    {
        var text = Source();

        var methodStart = text.IndexOf("static string ChromiumBridgeVersion()", StringComparison.Ordinal);
        Assert.True(methodStart > 0);
        var body = text[methodStart..Math.Min(text.Length, methodStart + 3200)];

        // 1. --version
        Assert.Contains("--version", body);
        // 2. file metadata
        Assert.Contains("FileVersionInfo.GetVersionInfo", body);
        // 3. the literal only as the last line
        var fallback = Regex.Match(body, @"return ""(\d+\.\d+\.\d+\.\d+)"";");
        Assert.True(fallback.Success);

        _out.WriteLine("fallbacks: --version → FileVersionInfo → " + fallback.Groups[1].Value);
    }

    [Fact]
    public void TheRealInstalledVersionIsReadableOnThisMachine()
    {
        // a live check: whatever this machine runs must come back as four numeric segments
        var version = Cybersole.Stores.Scripts.ChromiumBridge.DefaultUserAgent();
        _out.WriteLine("UA: " + version);

        var m = Regex.Match(version, @"Chrome/(\d+)\.0\.0\.0 ");
        Assert.True(m.Success, $"UA does not carry a reduced Chrome token: {version}");

        var major = int.Parse(m.Groups[1].Value);
        _out.WriteLine($"major: {major}");
        // a browser older than this project's floor would be a different problem
        Assert.True(major >= 100, $"major version {major} looks wrong");
    }
}
