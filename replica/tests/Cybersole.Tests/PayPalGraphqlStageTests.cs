using System.Net;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1154: the graphql stage request, pinned end to end.
///
/// <c>PayPalThreeDs.GqlAsync</c> is the call every 3DS stage goes through, and until now nothing in the
/// suite drove it: the class doc described the composition and the dispatch, and that was the only
/// evidence. These facts put a real request through a real socket and assert what the machine sends.
///
/// The verb stopped being a comment this round too — <c>sub_14110D670</c>, the send step for the frozen
/// <c>https://www.paypal.com/graphql/</c> literal, calls verb slot <c>sub_1408B6310</c> (+24 = PUT) at
/// line 37 of its decompilation, so PUT here is an observation rather than a reading of the doc.
/// </summary>
public sealed class PayPalGraphqlStageTests
{
    private static FlowContext Context(NetClient http, string baseUrl)
    {
        var ctx = new FlowContext
        {
            Http = http,
            Url = "https://www.paypal.com/checkoutnow?token=T",
        };
        ctx.Session.Vars["paypal3ds.graphqlUrl"] = baseUrl;
        return ctx;
    }

    [Fact]
    public async Task TheOperationNameRidesTheQueryStringWithoutASlashBeforeIt()
    {
        string raw = string.Empty;
        using var server = new TinyServer((req, _) =>
        {
            raw = req.RawUrl ?? string.Empty;
            return (200, "{\"data\":{}}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };

        // The seam carries the base the frozen literal names, so the operation lands on the graphql
        // path rather than on the host root.
        var outcome = await PayPalThreeDs.GqlAsync(Context(http, server.BaseUrl + "/graphql"),
            new PayPalThreeDs.StageInput(), PayPalThreeDs.JwtQueryOperation,
            new JObject(), default);

        Assert.True(outcome.Ok);
        // The frozen base ends in a slash and the composition trims it, which is the shape of the four
        // per-operation literals the image carries (https://www.paypal.com/graphql?GetThreeDsJwtQuery).
        Assert.Equal("/graphql?GetThreeDsJwtQuery", raw);
        Assert.Equal("PUT", Assert.Single(server.Requests).Method);
    }

    [Fact]
    public async Task TheBodyCarriesTheDocumentBesideTheVariables()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };

        var variables = new JObject { ["token"] = "T" };
        await PayPalThreeDs.GqlAsync(Context(http, server.BaseUrl), new PayPalThreeDs.StageInput(),
            PayPalThreeDs.LookUpOperation, variables, default);

        var sent = JObject.Parse(Assert.Single(server.Requests).Body);
        Assert.Equal("T", sent["variables"]?["token"]?.ToString());
        Assert.Equal(PayPalThreeDs.DocumentFor(PayPalThreeDs.LookUpOperation),
            sent["query"]?.ToString());
    }

    [Theory]
    [InlineData(200, true, false)]
    [InlineData(403, false, true)]
    [InlineData(429, false, true)]
    [InlineData(500, false, false)]
    public async Task TheDispatchIsTheOneTheCaseBodiesRegister(int status, bool ok, bool retry)
    {
        using var server = new TinyServer((_, _) => (status, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };

        var outcome = await PayPalThreeDs.GqlAsync(Context(http, server.BaseUrl),
            new PayPalThreeDs.StageInput(), PayPalThreeDs.JwtQueryOperation, new JObject(), default);

        Assert.Equal(ok, outcome.Ok);
        Assert.Equal(retry, outcome.Retryable);
    }
}
