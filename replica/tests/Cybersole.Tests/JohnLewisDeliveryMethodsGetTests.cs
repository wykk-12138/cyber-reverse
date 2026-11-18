using System.Collections.Generic;
using Cybersole.Http;
using Cybersole.Stores.Actions;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1137: John Lewis's <c>GetDeliveryMethods</c> — a GET on the derived
/// <c>v4/orderforms/deliveries/methods</c> URL.
///
/// The image never writes that path as one literal: <c>sub_140A3FB10</c> joins
/// <c>…/orderforms/deliveries/</c> (0x14705db98) with the suffix <c>/methods</c> (0x146ab5dd0) and
/// hands the result to the GET. The step assignment is an inference — the pair map had put both
/// delivery step names on the same POST, which left this read unclaimed.
/// </summary>
public sealed class JohnLewisDeliveryMethodsGetTests
{
    private static FlowContext Context(NetClient http, TinyServer server)
    {
        var c = new FlowContext { Http = http, Url = "https://www.johnlewis.com/ourshop/product" };
        c.Session.Vars["jl.deliveryMethodsUrl"] =
            server.BaseUrl + "/bff/v4/orderforms/deliveries/methods";
        return c;
    }

    [Fact]
    public async Task TheMethodsAreReadWithGet()
    {
        var seen = new List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add((req.Url?.PathAndQuery ?? "") + " " + req.HttpMethod);
            return (200, "{\"methods\":[]}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().GetDeliveryMethodsAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var request = Assert.Single(seen);
        Assert.EndsWith("GET", request);
        Assert.Contains("/bff/v4/orderforms/deliveries/methods", request);
        Assert.Equal("{\"methods\":[]}", ctx.Session.Vars["jl.deliveryMethodsBody"]);
    }

    [Fact]
    public void TheDefaultUrlIsTheJoinedValue()
    {
        Assert.Equal("https://checkout.johnlewis.com/bff/v4/orderforms/deliveries/methods",
            RetailApiFamilies.JohnLewisBff.DeliveryMethodsV4);
    }

    /// <summary>The pair map now names the read and the write separately.</summary>
    [Fact]
    public void ThePairMapSeparatesTheReadFromTheWrite()
    {
        var pairs = JohnLewisStepMap.Pairs;
        Assert.Equal(RetailApiFamilies.JohnLewisBff.DeliveryMethodsV4, pairs["GetDeliveryMethods"]);
        Assert.Equal(RetailApiFamilies.JohnLewisBff.DeliveryDetailsV3, pairs["SubmitDeliveryMethod"]);
    }

    [Fact]
    public void TheStepNameIsKnownToTheRunner()
    {
        Assert.True(StepActionRunner.Knows("GetDeliveryMethods"));
    }

    [Fact]
    public async Task AnHttpFailureIsRetryable()
    {
        using var server = new TinyServer((_, _) => (500, "boom"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http, server);

        var outcome = await new JohnLewisFlow().GetDeliveryMethodsAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
    }
}
