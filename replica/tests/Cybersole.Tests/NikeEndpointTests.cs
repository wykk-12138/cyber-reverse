using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 87: the Nike endpoint vocabulary, read straight out of the image.
///
/// <para>
/// <c>find_regex "api\.nike\.com"</c> against the 5.18.32 database returns <b>twenty</b> strings and
/// nothing else — that is the complete set of Nike base URLs the binary can call. The replica's flow
/// was meanwhile calling <c>buy/carts/v2/…</c> and <c>buy/orders/v2/…</c>, which are not in the set
/// at all.
/// </para>
///
/// <para>
/// This test pins the vocabulary so a future edit cannot quietly invent a twenty-first endpoint. It
/// does <b>not</b> claim the per-step mapping is solved — that is still open, and
/// docs/NIKE_PARITY.md says so.
/// </para>
/// </summary>
public sealed class NikeEndpointTests
{
    private readonly ITestOutputHelper _out;

    public NikeEndpointTests(ITestOutputHelper output) => _out = output;

    /// <summary>Nineteen distinct bases (the product feed keeps its query in the literal).</summary>
    [Fact]
    public void TheVocabularyIsTheImagesTwentyStrings()
    {
        foreach (var url in NikeEndpoints.All) _out.WriteLine(url);

        Assert.Equal(19, NikeEndpoints.All.Count);
        Assert.Equal(19, NikeEndpoints.All.Distinct().Count());

        // every one is an api.nike.com URL
        Assert.All(NikeEndpoints.All, u => Assert.StartsWith("https://api.nike.com/", u));
    }

    /// <summary>The four families the checkout steps write to.</summary>
    [Fact]
    public void TheCheckoutFamilyIsPresent()
    {
        Assert.Equal("https://api.nike.com/buy/checkouts/v3/", NikeEndpoints.Checkouts);
        Assert.Equal("https://api.nike.com/buy/checkouts_jobs/v3/", NikeEndpoints.CheckoutsJobs);
        Assert.Equal("https://api.nike.com/buy/checkout_previews/v3/", NikeEndpoints.CheckoutPreviews);
        Assert.Equal("https://api.nike.com/buy/checkout_previews_jobs/v3/",
            NikeEndpoints.CheckoutPreviewsJobs);
    }

    /// <summary>
    /// The two families the replica invented are not in the image — the assertion that would have
    /// caught the wrong paths years earlier.
    /// </summary>
    [Fact]
    public void TheInventedFamiliesAreNotInTheBinary()
    {
        _out.WriteLine($"carts/v2 known:  {NikeEndpoints.All.Any(u => u.Contains("buy/carts/"))}");
        _out.WriteLine($"orders/v2 known: {NikeEndpoints.All.Any(u => u.Contains("buy/orders/"))}");

        Assert.DoesNotContain(NikeEndpoints.All, u => u.Contains("buy/carts/", StringComparison.Ordinal));
        Assert.DoesNotContain(NikeEndpoints.All, u => u.Contains("buy/orders/", StringComparison.Ordinal));

        // and the helper agrees
        Assert.False(NikeEndpoints.IsKnown("https://api.nike.com/buy/carts/v2/US/Nike/SNKRS?format=simplified"));
        Assert.False(NikeEndpoints.IsKnown("https://api.nike.com/buy/orders/v2/US/abc/delivery"));
        Assert.True(NikeEndpoints.IsKnown(NikeEndpoints.Checkouts + "abc/"));
    }

    /// <summary>Every endpoint that has a job half lists both halves.</summary>
    [Fact]
    public void JobEndpointsHaveBothHalves()
    {
        var pairs = new (string Direct, string Jobs)[]
        {
            (NikeEndpoints.CheckoutPreviews, NikeEndpoints.CheckoutPreviewsJobs),
            (NikeEndpoints.Checkouts, NikeEndpoints.CheckoutsJobs),
            (NikeEndpoints.PartnerCartPreorder, NikeEndpoints.PartnerCartPreorderJobs),
            (NikeEndpoints.DeferredPaymentForms, NikeEndpoints.DeferredPaymentFormsJobs),
            (NikeEndpoints.PayPalDetails, NikeEndpoints.PayPalDetailsJobs),
            (NikeEndpoints.PayPalMark, NikeEndpoints.PayPalMarkJobs),
            (NikeEndpoints.PaymentPreview, NikeEndpoints.PaymentPreviewJobs),
        };

        foreach (var (direct, jobs) in pairs)
        {
            Assert.Contains(jobs, NikeEndpoints.All);
            Assert.Contains(direct, NikeEndpoints.All);
            _out.WriteLine($"{direct}  ↔  {jobs}");
        }

        Assert.Equal(7, pairs.Length);
    }
}
