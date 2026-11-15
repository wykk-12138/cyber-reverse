import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\HelpViewTests.cs"
code = '''using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R346: <c>HelpView.OpenUrl</c> — the one operation the binding table puts on the help page.
///
/// <para>
/// The page itself only draws the two links it owns (<see cref="HelpView.CommunityUrl"/>, <see cref="HelpView.DocsUrl"/>);
/// the operation that opens one is what the image binds, so it is a member rather than a captured local. It returns a
/// bool because a machine with no default browser must not throw out of a click handler — that is asserted below with a
/// URL no shell can resolve.
/// </para>
/// </summary>
public sealed class HelpViewTests
{
    private readonly ITestOutputHelper _out;
    public HelpViewTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheTwoLinksThePageOwnsAreAbsoluteHttps()
    {
        _out.WriteLine(HelpView.CommunityUrl + " | " + HelpView.DocsUrl);

        Assert.StartsWith("https://", HelpView.CommunityUrl, System.StringComparison.Ordinal);
        Assert.StartsWith("https://", HelpView.DocsUrl, System.StringComparison.Ordinal);
    }

    [Fact]
    public void OpeningSomethingUnopenableReportsFalseInsteadOfThrowing()
    {
        Assert.False(HelpView.OpenUrl("not-a-url"));
    }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('HelpViewTests written')
