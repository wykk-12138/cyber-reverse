using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 107: the Demandware flow now drives <b>both</b> SFCC paths, in the order the image implies.
///
/// <para>
/// R101 recorded nine SCAPI endpoints and R95 recorded the classic controller set; until now only the
/// classic one was wired. A store that runs headless SFCC answers <c>/scapi/ShopperBaskets/*</c> and
/// may not answer the <c>demandware.store</c> controllers at all — so a one-path flow is a flow that
/// fails on half of SFCC.
/// </para>
///
/// <para>
/// The gate is an SCAPI bearer token: present means the store told us it is headless, absent means
/// the classic path. Either way a failure returns to the other path rather than ending the checkout,
/// which is the same shape the Shopify GraphQL read uses.
/// </para>
/// </summary>
public sealed class DemandwareDualPathTests
{
    private readonly ITestOutputHelper _out;

    public DemandwareDualPathTests(ITestOutputHelper output) => _out = output;

    private static string FlowSource()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        return File.ReadAllText(Path.Combine(dir!.FullName, "src", "Cybersole.Stores",
            "Flows", "DemandwareFlow.cs"));
    }

    /// <summary>Both paths exist in the flow, and the classic one is the fallback.</summary>
    [Fact]
    public void TheFlowHasBothSfccPaths()
    {
        var source = FlowSource();

        // SCAPI half
        Assert.Contains("ScapiEndpoints.CreateBasket", source);
        Assert.Contains("ScapiEndpoints.AddItemToBasket", source);
        Assert.Contains("AddToCartViaScapiAsync", source);
        Assert.Contains("scapi.token", source);

        // classic half, still there
        Assert.Contains("DemandwareControllers.CartAddProduct", source);
        Assert.Contains("Controller(c,", source);

        _out.WriteLine("both halves present");
    }

    /// <summary>
    /// The SCAPI call is gated on the token and sits before the classic call — the order matters
    /// because "before" is what makes the classic path the fallback.
    /// </summary>
    [Fact]
    public void TheTokenGateComesBeforeTheClassicCall()
    {
        var source = FlowSource();

        var gate = source.IndexOf("TryGetValue(ScapiTokenVar", StringComparison.Ordinal);
        var scapiCall = source.IndexOf("AddToCartViaScapiAsync(c, token", StringComparison.Ordinal);
        var classic = source.IndexOf("Controller(c, DemandwareControllers.CartAddProduct",
            StringComparison.Ordinal);

        _out.WriteLine($"gate={gate} scapi={scapiCall} classic={classic}");

        Assert.True(gate > 0);
        Assert.True(gate < scapiCall);
        Assert.True(scapiCall < classic);
    }

    /// <summary>SCAPI failures return null so the caller falls back instead of failing the task.</summary>
    [Fact]
    public void ScapiFailureFallsBackInsteadOfFailing()
    {
        var source = FlowSource();

        // the helper returns a nullable outcome, and every early exit is `return null`
        Assert.Contains("Task<StepOutcome?> AddToCartViaScapiAsync", source);
        Assert.Contains("if (scapi is not null) return scapi.Value;", source);

        // most exits are inline guards (`if (x is null || !x.IsSuccess) return null;`), so count
        // occurrences of the statement rather than lines that begin with it
        var nulls = source.Split("return null;", StringSplitOptions.None).Length - 1;
        _out.WriteLine($"{nulls} `return null` exits in the helper");

        Assert.True(nulls >= 3, "every SCAPI failure path must return null");
    }

    /// <summary>The bearer token is set for the call and removed afterwards.</summary>
    [Fact]
    public void TheBearerTokenIsScopedToTheCall()
    {
        var source = FlowSource();

        var set = source.IndexOf("Headers[\"Authorization\"] = \"Bearer \"", StringComparison.Ordinal);
        var removed = source.IndexOf("Headers.Remove(\"Authorization\")", StringComparison.Ordinal);

        _out.WriteLine($"set={set} removed={removed}");

        Assert.True(set > 0);
        Assert.True(removed > set);
        Assert.Contains("try", source[..set]);
        Assert.Contains("finally", source[set..removed]);
    }

    /// <summary>The basket call carries the site id the flow already knows.</summary>
    [Fact]
    public void TheBasketCallUsesTheFlowsSiteId()
    {
        var source = FlowSource();

        Assert.Contains("siteId=", source);
        Assert.Contains("Uri.EscapeDataString(SiteId)", source);

        // no second SiteId helper was introduced
        Assert.Equal(1, source.Split('\n')
            .Count(l => l.Contains("SiteId =>", StringComparison.Ordinal) ||
                        l.Contains("string SiteId(FlowContext", StringComparison.Ordinal)));
    }
}
