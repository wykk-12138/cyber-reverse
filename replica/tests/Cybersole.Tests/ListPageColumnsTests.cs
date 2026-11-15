using System.Linq;
using Cybersole.Ui.Views;
using Cybersole.Ui.Views.Proxies;
using Cybersole.Ui.Views.Tasks;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R333: the column headers of the three list pages, as read off the running 5.18.32 build.
///
/// <para>
/// Tasks / Proxies / Billing each show a sortable header row, and the text and order of those headers is the most
/// visible thing on the page — a rename or a swap would look fine in code and wrong on screen. Tasks was already pinned
/// in <c>TasksPageTests</c>; this covers Proxies and Billing, and re-states all three together so the three orders can be
/// compared in one place.
/// </para>
/// </summary>
public sealed class ListPageColumnsTests
{
    private readonly ITestOutputHelper _out;
    public ListPageColumnsTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TasksColumnsAreSiteProductProfileProxiesStatus()
    {
        var columns = TaskGrid.Headers;
        _out.WriteLine(string.Join(" | ", columns));
        Assert.Equal(new[] { "Site", "Product", "Profile", "Proxies", "Status" }, columns);
    }

    [Fact]
    public void ProxiesColumnsAreIpPortUsernameStatus()
    {
        var columns = ProxyGrid.Headers;
        _out.WriteLine(string.Join(" | ", columns));
        Assert.Equal(new[] { "IP", "Port", "Username", "Status" }, columns);
    }

    [Fact]
    public void BillingColumnsAreProfileEmailCardHolderCardShipping()
    {
        var columns = BillingView.Columns;
        _out.WriteLine(string.Join(" | ", columns));
        Assert.Equal(new[] { "Profile", "Email", "Card Holder", "Card", "Shipping" }, columns);
    }
}
