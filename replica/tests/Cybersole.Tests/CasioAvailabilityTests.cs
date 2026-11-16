using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R782: Casio decides availability by walking <c>data.products.items</c> and reading
/// <c>casio_can_purchase</c>, not by looking for the word "availability" in the page.
///
/// <para>
/// The evidence is R781: <c>sub_140954410</c> makes three keyed lookups -- data, products, items -- and then reads
/// <c>casio_can_purchase</c> per item. The three key names came out of the string pool; the field name is a literal in
/// the same configuration record as the reCAPTCHA site key.
/// </para>
///
/// <para>
/// What is inferred rather than observed is the comparison: that the field is a boolean and that any item saying yes
/// makes the product available. The image reads the field, and the branch that consumes it sits outside the
/// decompiled window. Hence these tests pin the parse and the "any true" rule as the replica's interpretation, not as
/// the image's.
/// </para>
/// </summary>
public class CasioAvailabilityTests
{
    private readonly ITestOutputHelper _out;

    public CasioAvailabilityTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void OnePurchasableItemMakesTheProductAvailable()
    {
        const string body = """
        {"data":{"products":{"items":[
            {"skuid":"A","casio_can_purchase":false},
            {"skuid":"B","casio_can_purchase":true}
        ]}}}
        """;

        _out.WriteLine(body);
        Assert.True(CasioFlow.CasioAvailability(body));
    }

    [Fact]
    public void AllItemsRefusingMeansUnavailable()
    {
        const string body = """
        {"data":{"products":{"items":[
            {"skuid":"A","casio_can_purchase":false},
            {"skuid":"B","casio_can_purchase":false}
        ]}}}
        """;

        Assert.False(CasioFlow.CasioAvailability(body));
    }

    [Fact]
    // The string form is accepted too: a payload that spells the flag "true" is answering the same question.
    public void TheFlagMayArriveAsAString()
    {
        const string body = """
        {"data":{"products":{"items":[{"casio_can_purchase":"true"}]}}}
        """;

        Assert.True(CasioFlow.CasioAvailability(body));
    }

    [Fact]
    // No items, or items without the field, means the payload is not the shape the image walks -- so the caller keeps
    // its older heuristic rather than being told the product is unavailable.
    public void AShapeWithoutTheFieldIsUndecidedRatherThanUnavailable()
    {
        Assert.Null(CasioFlow.CasioAvailability("""{"data":{"products":{"items":[]}}}"""));
        Assert.Null(CasioFlow.CasioAvailability("""{"data":{"products":{"items":[{"skuid":"A"}]}}}"""));
        Assert.Null(CasioFlow.CasioAvailability("<html><body>InStock</body></html>"));
        Assert.Null(CasioFlow.CasioAvailability(string.Empty));
    }

    [Fact]
    // The field name is the image's, not ours; it is exposed so a test can hold it to that.
    public void TheFieldNameIsTheImages()
    {
        Assert.Equal("casio_can_purchase", CasioFlow.CanPurchaseField);
    }
}
