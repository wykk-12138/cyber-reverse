using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Pop Mart's price extraction, pinned against the shape a live product page actually had.
///
/// The defect this covers: a first-match regex on <c>"price":</c> lands on
/// <c>"spuPriceInfo":{"price":0,"currency":""}</c> — a placeholder for "no model selected yet".
/// On the real page the figure the user sees is 30, and the SKU list carries 3999 (cents).
/// Mock fixtures never had a zero placeholder, which is exactly why the mock-only test passed.
/// </summary>
public class PopMartPriceTests
{
    private static string PriceOf(string json) => PopMartFlow.ExtractPrice(json);

    /// <summary>The payload shape observed on /us/products/4205/dimoo-becoming-a-tree-figure.</summary>
    private const string LiveShape = """
    {"data":{"spuPriceInfo":{"price":0,"currency":""},
     "skus":[{"id":"3220","price":3999,"stock":{"onlineStock":2}},
             {"id":"3219","price":23994,"stock":{"onlineStock":1}}],
     "desc":"Brand: POP MART"}}
    """;

    [Fact]
    public void TheSpuPlaceholderIsNotMistakenForThePrice()
    {
        // 0 would be the old answer; 39.99 is the first real SKU price in dollars
        Assert.Equal("39.99", PriceOf(LiveShape));
    }

    [Fact]
    public void CentsAreConvertedToDollars()
    {
        Assert.Equal("39.99", PriceOf(LiveShape));
        Assert.Equal("239.94", PriceOf("""{"skus":[{"id":"1","price":23994}]}"""));
    }

    [Fact]
    public void AZeroSkuPriceIsSkipped()
    {
        // a sold-out SKU can carry price 0; the next real one should win
        Assert.Equal("19.99",
            PriceOf("""{"skus":[{"id":"1","price":0},{"id":"2","price":1999}]}"""));
    }

    [Fact]
    public void AnAllZeroSkuListFallsThroughToTheNextStrategy()
    {
        Assert.Equal("9.99",
            PriceOf("""{"skus":[{"id":"1","price":0}],"discountPrice":999}"""));
    }

    [Fact]
    public void APlainDecimalPriceIsStillAccepted()
    {
        Assert.Equal("30.00", PriceOf("""{"price":30,"currency":"USD"}"""));
    }

    [Fact]
    public void NoPriceAtAllYieldsEmptyRatherThanZero()
    {
        // empty means "unknown"; "0" would look like a real free item
        Assert.Equal(string.Empty, PriceOf("""{"name":"something","skus":[]}"""));
        Assert.Equal(string.Empty, PriceOf("not json at all"));
    }
}

