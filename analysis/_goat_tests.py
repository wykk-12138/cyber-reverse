import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\GoatAccountSurfaceTests.cs"
code = '''using System.IO;
using System.Linq;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R328: the four GOAT account paths the image carries are now used by <c>GoatFlow</c>.
///
/// <para>
/// These are <b>source-level</b> assertions, not behavioural ones: <c>NetClient</c> is sealed with non-virtual methods, so
/// the flow's HTTP seam cannot be faked without introducing an interface — a refactor nobody asked for. What matters here
/// is that the evidenced paths stayed in the file, that each says it is evidenced, and that the request bodies (which are
/// NOT evidenced) say so too. That distinction is the whole point of the round.
/// </para>
/// </summary>
public sealed class GoatAccountSurfaceTests
{
    private readonly ITestOutputHelper _out;
    public GoatAccountSurfaceTests(ITestOutputHelper output) => _out = output;

    private static string Source() =>
        File.ReadAllText(Path.Combine(Root(), "src", "Cybersole.Stores", "Flows", "GoatFlow.cs"));

    private static readonly string[] Evidenced =
    {
        "/v1/login",
        "/v1/users/send_otp_token",
        "/v1/addresses",
        "/v1/billing_infos",
    };

    [Fact]
    public void TheFourEvidencedPathsAreStillCalled()
    {
        var src = Source();
        foreach (var path in Evidenced)
        {
            _out.WriteLine(path + (src.Contains(path, System.StringComparison.Ordinal) ? ": present" : ": MISSING"));
            Assert.Contains(path, src, System.StringComparison.Ordinal);
        }
    }

    [Fact]
    public void EachOneSaysThePathIsEvidencedAndTheBodyIsNot()
    {
        var src = Source();
        Assert.Contains("(path evidenced; body inferred)", src, System.StringComparison.Ordinal);
        Assert.Contains("(path evidenced, no body)", src, System.StringComparison.Ordinal);
        // the evidence address itself, so the claim can be re-checked
        Assert.Contains("https://www.goat.com/web-api/", src, System.StringComparison.Ordinal);
    }

    [Fact]
    public void TheBodiesAreMarkedInferred()
    {
        var src = Source();
        var login = src.IndexOf("/v1/login", System.StringComparison.Ordinal);
        var otp = src.IndexOf("/v1/users/send_otp_token", System.StringComparison.Ordinal);

        Assert.Contains("email", src.Substring(login, 200), System.StringComparison.Ordinal);
        Assert.Contains("password", src.Substring(login, 200), System.StringComparison.Ordinal);
        Assert.Contains("email", src.Substring(otp, 200), System.StringComparison.Ordinal);
    }

    [Fact]
    public void SubmittingAnOrderChecksForASavedAddressFirst()
    {
        var src = Source();
        var submit = src.IndexOf("SubmitOrderAsync", System.StringComparison.Ordinal);
        Assert.True(submit > 0);
        Assert.Contains("EnsureAddressAsync", src.Substring(submit, 900), System.StringComparison.Ordinal);
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('GoatAccountSurfaceTests written')
