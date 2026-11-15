using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 101: two endpoint families dumped <b>before</b> any code was written against them — the
/// order R100 concluded was the whole point.
///
/// <para>
/// <b>SCAPI</b> — Salesforce's headless REST API, nine endpoints. The original drives SFCC two ways:
/// the classic <c>demandware.store</c> controllers (DemandwareFlow) and this. The replica had only
/// the first.
/// </para>
///
/// <para>
/// <b>Nike persisted GraphQL</b> — six <c>operationName</c>s under
/// <c>checkouts/internal/graphql/persisted</c>. This is the answer to a question six rounds could not
/// answer: the Nike steps are not REST sub-paths, so no amount of searching for
/// <c>buy/orders/v2/{id}/shipping</c> was ever going to find them.
/// </para>
/// </summary>
public sealed class EndpointFamilies101Tests
{
    private readonly ITestOutputHelper _out;

    public EndpointFamilies101Tests(ITestOutputHelper output) => _out = output;

    /// <summary>Nine SCAPI endpoints, all distinct, all under /scapi/.</summary>
    [Fact]
    public void TheImageCarriesNineScapiEndpoints()
    {
        foreach (var e in ScapiEndpoints.All) _out.WriteLine(e);

        Assert.Equal(9, ScapiEndpoints.All.Count);
        Assert.Equal(9, ScapiEndpoints.All.Distinct().Count());
        Assert.All(ScapiEndpoints.All, e => Assert.True(ScapiEndpoints.IsScapi(e)));
    }

    /// <summary>The basket chain is in checkout order and is a subset of the nine.</summary>
    [Fact]
    public void TheBasketChainIsInCheckoutOrder()
    {
        _out.WriteLine(string.Join(" → ", ScapiEndpoints.BasketChain));

        Assert.Equal(7, ScapiEndpoints.BasketChain.Count);
        Assert.All(ScapiEndpoints.BasketChain, e => Assert.True(ScapiEndpoints.IsKnown(e)));

        Assert.Equal(ScapiEndpoints.CreateBasket, ScapiEndpoints.BasketChain[0]);
        Assert.Equal(ScapiEndpoints.AddItemToBasket, ScapiEndpoints.BasketChain[1]);
        Assert.Equal(ScapiEndpoints.UpdateBillingAddress, ScapiEndpoints.BasketChain[^2]);

        // login is not part of the basket chain
        Assert.DoesNotContain(ScapiEndpoints.GetAccessToken, ScapiEndpoints.BasketChain);
        Assert.Equal(2, ScapiEndpoints.Login.Count);
    }

    /// <summary>SCAPI is a second path, not a replacement — the classic controllers stay.</summary>
    [Fact]
    public void ScapiCoexistsWithTheClassicDemandwareControllers()
    {
        Assert.True(DemandwareControllers.IsKnown(DemandwareControllers.CartAddProduct));
        Assert.True(ScapiEndpoints.IsKnown(ScapiEndpoints.AddItemToBasket));

        // different shapes: one is a demandware.store controller, the other a /scapi/ resource
        Assert.StartsWith("/scapi/", ScapiEndpoints.AddItemToBasket);
        Assert.DoesNotContain("/demandware", ScapiEndpoints.AddItemToBasket);
    }

    /// <summary>Six persisted operations, and the URL builder produces the image's literal.</summary>
    [Fact]
    public void ThePersistedOperationsMatchTheImagesLiterals()
    {
        Assert.Equal(6, NikePersistedOperations.All.Count);

        foreach (var name in NikePersistedOperations.All)
            _out.WriteLine(NikePersistedOperations.Url(name));

        Assert.Equal(
            "checkouts/internal/graphql/persisted?operationName=SubmitForCompletion",
            NikePersistedOperations.Url(NikePersistedOperations.SubmitForCompletion));

        Assert.Equal("/checkouts/internal/graphql", NikePersistedOperations.Endpoint);
        Assert.True(NikePersistedOperations.IsKnown("PollForReceipt"));
        Assert.False(NikePersistedOperations.IsKnown("ShippingAddress"));
    }

    /// <summary>
    /// The three payment-side names are flagged as a reading, and the list is deliberately shorter
    /// than the fourteen Nike steps — six names is not a step mapping and must not be treated as one.
    /// </summary>
    [Fact]
    public void ThePaymentHalfIsAReadingNotAMapping()
    {
        Assert.Equal(3, NikePersistedOperations.PaymentHalf.Count);
        Assert.All(NikePersistedOperations.PaymentHalf,
            n => Assert.True(NikePersistedOperations.IsKnown(n)));

        // the Nike flow has fourteen steps; six operation names cannot address them all
        Assert.True(NikePersistedOperations.All.Count < 14);
        _out.WriteLine($"{NikePersistedOperations.All.Count} names vs 14 steps — mapping still open");
    }
}
