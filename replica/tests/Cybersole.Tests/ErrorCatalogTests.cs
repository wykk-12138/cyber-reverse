using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The error catalogue behind Settings → Need Help?. Every string here was read off the
/// running 5.18.32 window, so a user comparing the two builds sees the same explanation for
/// the same failure.
/// </summary>
public class ErrorCatalogTests
{
    [Fact]
    public void CatalogueHasTheThirteenLiveEntries()
    {
        Assert.Equal(13, ErrorCatalog.All.Count);
        Assert.Equal(6, ErrorCatalog.Tagged("General").Count());
        Assert.Equal(6, ErrorCatalog.Tagged("Shopify").Count());
        Assert.Equal(1, ErrorCatalog.Tagged("Footsites").Count());
    }

    [Fact]
    public void IdsAreUniqueAndEveryEntryIsFillable()
    {
        var ids = ErrorCatalog.All.Select(e => e.Id).ToList();
        Assert.Equal(ids.Count, ids.Distinct(StringComparer.OrdinalIgnoreCase).Count());

        foreach (var e in ErrorCatalog.All)
        {
            Assert.False(string.IsNullOrWhiteSpace(e.Tag));
            Assert.StartsWith("[" + e.Tag + "]", e.Title);
            Assert.False(string.IsNullOrWhiteSpace(e.Detail));
        }
    }

    [Theory]
    [InlineData("general.connection", "[General] Connection Error")]
    [InlineData("general.forbidden", "[General] Forbidden")]
    [InlineData("shopify.payment", "[Shopify] Payment Error")]
    [InlineData("footsites.ratelimit", "[Footsites] Rate Limit / 429")]
    public void TitlesMatchTheLiveWording(string id, string title)
    {
        Assert.Equal(title, ErrorCatalog.ById(id)!.Title);
    }

    [Fact]
    public void StatusCodesMapToTheRightEntry()
    {
        Assert.Equal("general.forbidden", ErrorCatalog.Classify(403, StepStage.AddToCart).Id);
        Assert.Equal("general.notfound", ErrorCatalog.Classify(404, StepStage.FindProduct).Id);
        Assert.Equal("general.unavailable", ErrorCatalog.Classify(503, StepStage.Monitor).Id);
        Assert.Equal("general.connection", ErrorCatalog.Classify(0, StepStage.Monitor).Id);
        Assert.Equal("general.ratelimit", ErrorCatalog.Classify(429, StepStage.Monitor).Id);
        Assert.Equal("footsites.ratelimit", ErrorCatalog.Classify(429, StepStage.SubmitShipping).Id);
    }

    [Fact]
    public void StageDecidesWhenTheStatusIsGeneric()
    {
        Assert.Equal("shopify.shipping.handle",
            ErrorCatalog.Classify(500, StepStage.SubmitShipping).Id);
        Assert.Equal("shopify.payment",
            ErrorCatalog.Classify(500, StepStage.SubmitPayment).Id);
        Assert.Equal("general.taskfailed",
            ErrorCatalog.Classify(500, StepStage.SubmitOrder).Id);
    }

    [Fact]
    public void AntibotOnSubmitOrderIsItsOwnReason()
    {
        Assert.Equal("shopify.order.ratelimit",
            ErrorCatalog.Classify(200, StepStage.SubmitOrder, blocked: true).Id);
    }
}
