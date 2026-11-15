using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Filtering for <see cref="NetworkRecorder.CollectLinksAsync"/>.
///
/// The recorder's DOM link reader is what found HBX's product path after
/// /products/{slug} turned out to be 404: the real shape is /{gender}/brands/{brand}/{product}.
/// Guessing path shapes had already failed twice, so this filter exists to narrow a rendered
/// page's ~268 anchors down to the handful worth trying, without hiding the product page.
/// </summary>
public class LinkFilterTests
{
    private static readonly string[] RealHbxLinks =
    {
        // the ones that actually were product pages
        "https://hbx.com/men/brands/veja/volley-leather-white-green",
        "https://hbx.com/men/brands/norda/luster-cap-rose",
        "https://hbx.com/men/brands/f-c-real-bristol/training-track-zip-up-hoodie-black",

        // navigation and policy pages that must be filtered out
        "https://hbx.com/men/new-arrivals",
        "https://hbx.com/men/categories/clothing",
        "https://hbx.com/cart",
        "https://hbx.com/checkout",
        "https://hbx.com/login",
        "https://hbx.com/policies/return-policy",
        "https://hbx.com/about",
    };

    [Fact]
    public void CategoryAndPolicyLinksAreDropped()
    {
        var kept = NetworkRecorder.Productish(RealHbxLinks).ToList();

        Assert.DoesNotContain(kept, k => k.Contains("/categories/"));
        Assert.DoesNotContain(kept, k => k.Contains("/cart"));
        Assert.DoesNotContain(kept, k => k.Contains("/checkout"));
        Assert.DoesNotContain(kept, k => k.Contains("/login"));
        Assert.DoesNotContain(kept, k => k.Contains("/policies/"));
        Assert.DoesNotContain(kept, k => k.Contains("/about"));
    }

    [Fact]
    public void ObviousProductShapesSurvive()
    {
        var kept = NetworkRecorder.Productish(new[]
        {
            "https://shop.example.com/p/12345-thing",
            "https://shop.example.com/product/blue-shirt",
            "https://shop.example.com/item/sku-99",
            "https://shop.example.com/shop/sneakers/red",
            "https://shop.example.com/foo/bar/99887766.html",
        }).ToList();

        Assert.Equal(5, kept.Count);
    }

    [Fact]
    public void AnUnrecognisedShapeIsNotSilentlyKept()
    {
        // HBX's own shape matched none of the heuristics — which is why the capture tool falls
        // back to printing the deepest paths instead of pretending the filter found something.
        var kept = NetworkRecorder.Productish(new[]
        {
            "https://hbx.com/men/brands/veja/volley-leather-white-green",
        }).ToList();

        // documents the current behaviour: no match, so the tool's deepest-path fallback runs
        Assert.Empty(kept);
    }

    [Fact]
    public void NonAbsoluteEntriesDoNotThrow()
    {
        var kept = NetworkRecorder.Productish(new[] { "", "/relative/path", "https://x.test/p/1" })
            .ToList();

        // only the absolute one can be judged; the others must not blow up the filter
        Assert.Single(kept);
        Assert.Contains("https://x.test/p/1", kept);
    }
}
