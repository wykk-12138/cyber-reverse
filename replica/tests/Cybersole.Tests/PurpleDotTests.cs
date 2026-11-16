using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Purple Dot, added in R920 after the coverage table's last non-payment unmatched host turned out to be a vendor.
///
/// <para>
/// One literal names it: host, a preorder-state endpoint, and an API key, all in one URL. Purple Dot handles preorders
/// for shops, so a monitor that treats a preorder as purchasable will try to buy something that ships months later.
/// That is why it sits beside the payment gateways rather than among the stores, and why the unknown case is what these
/// tests care about most.
/// </para>
/// </summary>
public class PurpleDotTests
{
    private static string Url() =>
        (string)typeof(PurpleDot).GetMethod("UrlFor")!.Invoke(null, new object[] { "nike-air-max-1" })!;

    private static NetResponse Ok(string body) => new()
    {
        Url = new System.Uri("https://www.purpledotprice.com/api/v1/products/preorder-state"),
        StatusCode = 200,
        Body = body,
        Headers = new Dictionary<string, string>(),
    };

    /// <summary>
    /// The URL shape is the recovered one: a query string, not a header, and both parameters populated.
    /// </summary>
    [Fact]
    public void TheUrlCarriesTheKeyAndTheHandleInTheQuery()
    {
        var url = Url();

        Assert.StartsWith("https://www.purpledotprice.com/api/v1/products/preorder-state?api_key=", url);
        Assert.Contains("c114b1fe-63fa-4216-9d7c-07a87697fccd", url);
        Assert.Contains("&handle=nike-air-max-1", url);
    }

    /// <summary>A preorder is not purchasable, and the state says which it is rather than only whether.</summary>
    [Fact]
    public async Task APreorderIsNotBuyable()
    {
        var session = new FlowSession { SessionId = "s" };
        var outcome = await PurpleDot.QueryAsync(session, "h", default,
            (u, ct) => Task.FromResult<NetResponse?>(Ok("{\"isPreorder\":true}")));

        Assert.True(outcome.Ok);
        Assert.Equal("preorder", session.Vars[PurpleDot.StateVar]);
        Assert.False(PurpleDot.IsBuyable(session));
    }

    [Fact]
    public async Task AnInStockAnswerIsBuyable()
    {
        var session = new FlowSession { SessionId = "s" };
        var outcome = await PurpleDot.QueryAsync(session, "h", default,
            (u, ct) => Task.FromResult<NetResponse?>(Ok("{\"isPreorder\":false}")));

        Assert.True(outcome.Ok);
        Assert.Equal("in-stock", session.Vars[PurpleDot.StateVar]);
        Assert.True(PurpleDot.IsBuyable(session));
    }

    /// <summary>
    /// The case that matters: an unreadable answer must not be read as "not a preorder". The failure is reported and
    /// the state stays unset, so IsBuyable answers false rather than true by default.
    /// </summary>
    [Fact]
    public async Task AnUnrecognisedAnswerLeavesTheStateUnsetRatherThanBuyable()
    {
        var session = new FlowSession { SessionId = "s" };
        var outcome = await PurpleDot.QueryAsync(session, "h", default,
            (u, ct) => Task.FromResult<NetResponse?>(Ok("{\"something\":\"else\"}")));

        Assert.False(outcome.Ok);
        Assert.False(session.Vars.ContainsKey(PurpleDot.StateVar));
        Assert.False(PurpleDot.IsBuyable(session));

        // the body is kept, because the shape is unknown and dropping it would lose the only evidence
        Assert.Equal("{\"something\":\"else\"}", session.Vars["purpledot.body"]);
    }

    /// <summary>An unreachable host is the same unknown, not a negative answer.</summary>
    [Fact]
    public async Task AnUnreachableHostIsAlsoNotBuyable()
    {
        var session = new FlowSession { SessionId = "s" };
        var outcome = await PurpleDot.QueryAsync(session, "h", default,
            (u, ct) => Task.FromResult<NetResponse?>(null));

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
        Assert.False(PurpleDot.IsBuyable(session));
    }

    /// <summary>A missing handle is refused before any request, since the endpoint would answer for the empty string.</summary>
    [Fact]
    public async Task AMissingHandleIsRefused()
    {
        var session = new FlowSession { SessionId = "s" };
        var called = false;

        var outcome = await PurpleDot.QueryAsync(session, "  ", default, (u, ct) =>
        {
            called = true;
            return Task.FromResult<NetResponse?>(null);
        });

        Assert.False(outcome.Ok);
        Assert.False(called);
    }

    /// <summary>
    /// A fresh session is not buyable: absence of a state is not a yes.
    /// </summary>
    [Fact]
    public void AFreshSessionIsNotBuyable()
    {
        Assert.False(PurpleDot.IsBuyable(new FlowSession { SessionId = "s" }));
    }
}