using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The price extractor for John Lewis.
///
/// The live page ships "Free Delivery on orders over £50." inside its meta description, and the
/// old pattern <c>£([\d.,]+)</c> matched that instead of the product price — a wrong number
/// that looks entirely plausible. Structured data does not help: the ld+json blocks carry name
/// and brand but no price.
///
/// So the extractor has to ignore marketing copy and prefer the marked-up price element.
/// </summary>
public class JohnLewisPriceTests
{
    private const string LiveShape = """
    <html><head>
      <meta name="description" content="Shop the OPI range at John Lewis &amp; Partners.
        Free Delivery on orders over £50."/>
    </head><body>
      <h1>OPI Infinite Shine Nail Lacquer, Alpine Snow</h1>
      <span data-test-id="product-price" class="price">£12.75</span>
      <script type="application/ld+json">{"name":"OPI","@type":"Brand"}</script>
    </body></html>
    """;

    [Fact]
    public void TheDeliveryThresholdIsNotThePrice()
    {
        var price = JohnLewisFlow.ExtractPrice(LiveShape);

        Assert.NotEqual("50.", price);
        Assert.NotEqual("50", price);
        Assert.Equal("12.75", price);
    }

    [Fact]
    public void APageWithoutAMarkedPriceElementDoesNotInventOne()
    {
        // nothing but the marketing sentence: better to return empty than a plausible wrong number
        const string onlyMeta = """
        <html><head><meta name="description" content="Free Delivery on orders over £50."/></head>
        <body><h1>Some Product</h1></body></html>
        """;

        Assert.Equal(string.Empty, JohnLewisFlow.ExtractPrice(onlyMeta));
    }

    [Fact]
    public void ThousandsSeparatorsSurvive()
    {
        const string big = """<span data-test-id="product-price">£1,299.00</span>""";
        Assert.Equal("1299.00", JohnLewisFlow.ExtractPrice(big));
    }

    [Fact]
    public void TheProductNameComesFromH1NotTheFoorterTitle()
    {
        // <title> on this site belongs to a footer widget ("Store Finder")
        var name = JohnLewisFlow.ExtractProductName(LiveShape);
        Assert.Equal("OPI Infinite Shine Nail Lacquer, Alpine Snow", name);
    }
}
