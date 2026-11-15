using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 111: Nike's step list, read straight out of the 5.18.32 image.
///
/// <para>
/// One adjacent run in the string pool carries the whole flow with the state-machine ordinals the
/// compiler assigned, which is why the ordinals are consecutive where steps are and skip 45 and 47
/// (those two are the compiler's <c>MoveNext</c> helpers).
/// </para>
///
/// <code>
/// 41 StartEcomSession   42 Authorize          43 GetAccessToken    44 FindVariant
/// 46 CreateBasket       48 SubmitCustomer     49 ValidateAddress   50 SubmitShippingAddress
/// 51 GetShippingMethods 52 SubmitShippingMethod 53 SubmitBillingAddress 54 BeginCheckout
/// 55 CheckInventory     56 GetShopperIp       57 GetPaymentMethods 58 SubmitOrder
/// </code>
///
/// <para>
/// <b>Sixteen, not fourteen.</b> The fourteen figure was inherited from a partial reading and had
/// been repeated in NIKE_PARITY for dozens of rounds. <c>StartEcomSession</c> and <c>BeginCheckout</c>
/// are separate steps; so are <c>Authorize</c> and <c>GetAccessToken</c>. A hand-written list merges
/// exactly those pairs, which is why the count was low.
/// </para>
/// </summary>
public sealed class NikeStepTests
{
    private readonly ITestOutputHelper _out;

    public NikeStepTests(ITestOutputHelper output) => _out = output;

    /// <summary>Sixteen steps, sixteen distinct names.</summary>
    [Fact]
    public void TheImageNamesSixteenSteps()
    {
        foreach (var step in NikeSteps.All) _out.WriteLine($"d__{step.Ordinal}  {step.Name}");

        Assert.Equal(16, NikeSteps.All.Count);
        Assert.Equal(16, NikeSteps.Names.Distinct().Count());
    }

    /// <summary>
    /// The ordinals ascend, and only 45 and 47 are skipped — the two compiler helpers between them.
    /// </summary>
    [Fact]
    public void TheOrdinalsAreConsecutiveExceptForTheTwoHelpers()
    {
        var ordinals = NikeSteps.Ordinals;

        _out.WriteLine(string.Join(", ", ordinals));

        Assert.Equal(ordinals.OrderBy(o => o), ordinals);
        Assert.Equal(41, ordinals[0]);
        Assert.Equal(58, ordinals[^1]);

        var span = 58 - 41 + 1;                 // 18 slots
        var missing = Enumerable.Range(41, span).Except(ordinals).ToList();

        _out.WriteLine($"missing ordinals: {string.Join(", ", missing)}");
        Assert.Equal(new[] { 45, 47 }, missing);
    }

    /// <summary>The pairs a hand-written list merges are separate steps in the image.</summary>
    [Fact]
    public void ThePairsAHandWrittenListMergesAreDistinct()
    {
        Assert.True(NikeSteps.IsStep("StartEcomSession"));
        Assert.True(NikeSteps.IsStep("BeginCheckout"));
        Assert.NotEqual(NikeSteps.Position("StartEcomSession"), NikeSteps.Position("BeginCheckout"));

        Assert.True(NikeSteps.IsStep("Authorize"));
        Assert.True(NikeSteps.IsStep("GetAccessToken"));
        Assert.NotEqual(NikeSteps.Position("Authorize"), NikeSteps.Position("GetAccessToken"));
    }

    /// <summary>Position is 1-based and matches the ordinal order.</summary>
    [Fact]
    public void PositionFollowsTheFlow()
    {
        Assert.Equal(1, NikeSteps.Position("StartEcomSession"));
        Assert.Equal(5, NikeSteps.Position("CreateBasket"));
        Assert.Equal(11, NikeSteps.Position("SubmitBillingAddress"));
        Assert.Equal(16, NikeSteps.Position("SubmitOrder"));

        Assert.Null(NikeSteps.Position("NotAStep"));
        Assert.Null(NikeSteps.Position(null));
        Assert.False(NikeSteps.IsStep("Checkout"));
    }

    /// <summary>
    /// The steps that need the persisted GraphQL operations are all present — the two findings line
    /// up: <c>BeginCheckout</c>/<c>SubmitOrder</c> are steps, and
    /// <c>persisted?operationName=…</c> is how they talk.
    /// </summary>
    [Fact]
    public void TheGraphQlStepsAreInTheList()
    {
        foreach (var name in new[] { "BeginCheckout", "SubmitOrder", "GetPaymentMethods" })
            Assert.True(NikeSteps.IsStep(name), name);

        // and the persisted operations cover the payment half of the same flow
        Assert.Equal(3, NikePersistedOperations.PaymentHalf.Count);

        _out.WriteLine("BeginCheckout/SubmitOrder/GetPaymentMethods ↔ the persisted payment operations");
    }
}
