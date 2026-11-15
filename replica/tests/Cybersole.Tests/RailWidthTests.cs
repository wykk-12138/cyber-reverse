using System.IO;
using System.Linq;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R222: the left rail is a fixed 324 px on every page that has one. Measured on the running build by reading the
/// group card's edges off the window: at window widths 1375 and 1566 the card spanned <c>x 25..349</c> both times, so
/// the rail is fixed rather than proportional.
///
/// <para>
/// Before this round the three pages disagreed with each other and with the target: Proxies had <b>no width at all</b>
/// (the shared <c>GroupGrid</c> sized itself to its content), Billing said 320 and Accounts said 300. Three pages, three
/// answers, none of them measured.
/// </para>
/// </summary>
public sealed class RailWidthTests
{
    private readonly ITestOutputHelper _out;
    public RailWidthTests(ITestOutputHelper output) => _out = output;

    private static string View(string relative) => File.ReadAllText(Path.Combine(Root(),
        "src", "Cybersole.Ui", "Views", relative.Replace('/', Path.DirectorySeparatorChar)));

    [Fact]
    public void TheThreeRailsAgreeOnTheMeasuredWidth()
    {
        var proxies = View("Proxies/ProxyView.cs");
        var billing = View("BillingView.cs");
        var accounts = View("Accounts/AccountView.cs");

        Assert.Contains("internal const double RailWidth = 324;", proxies);
        Assert.Contains("Width = RailWidth", proxies);

        Assert.Contains("ColumnDefinitions(\"324,*\")", billing);
        Assert.Contains("Width = 324", accounts);

        _out.WriteLine("324 in all three");
    }

    [Fact]
    public void TheMeasurementIsRecordedWhereTheNumberLives()
    {
        var proxies = View("Proxies/ProxyView.cs");

        // two widths, same measurement — that is what makes "fixed" a conclusion instead of a guess
        Assert.Contains("1375 and 1566", proxies);
        Assert.Contains("324 px", proxies);
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    [Fact]
    public void TheBillingColumnsAreTheMeasuredRatios()
    {
        // R223: Profile 1.00 / Email 1.28 / Card Holder 1.29 / Card 1.00 / Shipping 1.00 (last column = remainder)
        var billing = View("BillingView.cs");
        Assert.Contains("\"18,1.0*,1.28*,1.29*,1.0*,1.0*\"", billing);
        Assert.Contains("measured column proportions, not equal stars", billing);
        Assert.Contains("absorbs the remainder", billing);
    }
}
