using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 94: the Demandware controller vocabulary, read out of the PE without IDA.
///
/// <para>
/// R93 lost the IDA database. R94 replaced that tool with a plain UTF-16 literal extraction
/// (<c>analysis/pe_strings.py</c>) — 180,228 distinct strings from the 123 MB image, and the
/// Salesforce Commerce Cloud controllers came out of it:
/// </para>
///
/// <code>
/// Checkout-Begin (22)         Cart-AddProduct (20)      Product-Variation (13)
/// CSRF-Generate (11)          Account-Login (10)        Cart-RemoveProductLineItem (6)
/// CheckoutServices-SubmitCustomer / -SubmitPayment / -PlaceOrder
/// CheckoutShippingServices-SubmitShipping                 AdyenUpgrade-Authorize
/// </code>
///
/// <para>
/// The replica's flow posted to <c>Checkout-Submit</c>, <c>Checkout-SubmitShipping</c> and
/// <c>Checkout-SubmitPayment</c>. <b>None of the three exists in the image.</b> Same shape of
/// mistake as Nike's <c>buy/orders/v2</c>: a plausible-looking route invented where the real one was
/// a different family.
/// </para>
/// </summary>
public sealed class DemandwareControllerTests
{
    private readonly ITestOutputHelper _out;

    public DemandwareControllerTests(ITestOutputHelper output) => _out = output;

    /// <summary>The checkout chain, in the order the platform runs it.</summary>
    [Fact]
    public void TheCheckoutChainIsTheImagesNames()
    {
        _out.WriteLine(string.Join(" → ", DemandwareControllers.CheckoutChain));

        Assert.Equal(new[]
        {
            "Cart-AddProduct", "Cart-Get", "Checkout-Begin",
            "CheckoutServices-SubmitCustomer",
            "CheckoutShippingServices-SubmitShipping",
            "CheckoutServices-SubmitPayment",
            "CheckoutServices-PlaceOrder",
        }, DemandwareControllers.CheckoutChain);
    }

    /// <summary>Every name in the chain is also in the full vocabulary.</summary>
    [Fact]
    public void TheChainIsASubsetOfTheVocabulary()
    {
        foreach (var controller in DemandwareControllers.CheckoutChain)
            Assert.True(DemandwareControllers.IsKnown(controller), controller);

        _out.WriteLine($"{DemandwareControllers.All.Count} confirmed controllers");
        Assert.Equal(DemandwareControllers.All.Count, DemandwareControllers.All.Distinct().Count());
    }

    /// <summary>
    /// The three names the replica invented are absent from the vocabulary — the assertion that
    /// stops them coming back.
    /// </summary>
    [Fact]
    public void TheInventedNamesAreNotInTheImage()
    {
        foreach (var invented in DemandwareControllers.Invented)
        {
            _out.WriteLine($"{invented}: known={DemandwareControllers.IsKnown(invented)}");
            Assert.False(DemandwareControllers.IsKnown(invented));
        }

        Assert.Equal(3, DemandwareControllers.Invented.Count);
    }

    /// <summary>The eight site ids the image names.</summary>
    [Fact]
    public void TheImageNamesEightSites()
    {
        _out.WriteLine(string.Join(", ", DemandwareControllers.Sites));

        Assert.Equal(8, DemandwareControllers.Sites.Count);
        Assert.Contains("asics", DemandwareControllers.Sites);
        Assert.Contains("crocs_", DemandwareControllers.Sites);
        Assert.Contains("vans", DemandwareControllers.Sites);
    }

    /// <summary>
    /// R95: the image spells four URLs out end to end, which fixes the path shape and proves it.
    ///
    /// <code>
    /// https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Cart-AddProduct
    /// https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Product-Variation?pid=
    /// https://www.cpcompany.com/on/demandware.store/Sites-cpcompany-Site/
    /// https://www.stoneisland.com/on/demandware.store/Sites-StoneNA-Site/en_US/SaleRegistration-SignupSubmit
    /// </code>
    ///
    /// The locale is <c>default</c> on Marc Jacobs and <c>en_US</c> on Stone Island, so it is a
    /// parameter — hard-coding either one gets the other store wrong.
    /// </summary>
    [Fact]
    public void TheSitePathReproducesTheImagesUrls()
    {
        var marcJacobs = DemandwareControllers.SitePath(
            DemandwareControllers.Hosts["mjsfra"], "mjsfra", "default",
            DemandwareControllers.CartAddProduct);

        var stone = DemandwareControllers.SitePath(
            DemandwareControllers.Hosts["StoneNA"], "StoneNA", "en_US",
            DemandwareControllers.SaleSignupSubmit);

        var cpcompany = DemandwareControllers.SiteRoot(
            DemandwareControllers.Hosts["cpcompany"], "cpcompany");

        _out.WriteLine(marcJacobs);
        _out.WriteLine(stone);
        _out.WriteLine(cpcompany);

        Assert.Equal("https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Cart-AddProduct",
            marcJacobs);
        Assert.Equal("https://www.stoneisland.com/on/demandware.store/Sites-StoneNA-Site/en_US/SaleRegistration-SignupSubmit",
            stone);
        Assert.Equal("https://www.cpcompany.com/on/demandware.store/Sites-cpcompany-Site/", cpcompany);
    }

    /// <summary>The raffle chain is in the vocabulary; hosts are only the three the image pairs.</summary>
    [Fact]
    public void TheRaffleChainAndHostsAreRecorded()
    {
        Assert.True(DemandwareControllers.IsKnown("SaleRegistration-SignupSubmit"));
        Assert.True(DemandwareControllers.IsKnown("SaleRegistration-Config"));

        Assert.Equal(3, DemandwareControllers.Hosts.Count);
        Assert.Equal("www.marcjacobs.com", DemandwareControllers.Hosts["mjsfra"]);
        Assert.Equal("www.stoneisland.com", DemandwareControllers.Hosts["StoneNA"]);
        Assert.Equal("www.cpcompany.com", DemandwareControllers.Hosts["cpcompany"]);

        // asics / crocs / vans are site ids without a host in the same literal — not guessed
        Assert.False(DemandwareControllers.Hosts.ContainsKey("asics"));
    }

    /// <summary>
    /// The flow source no longer contains an invented controller. A source-level check, because a
    /// constructed flow cannot reach the network in a unit test.
    /// </summary>
    [Fact]
    public void TheFlowNoLongerUsesTheInventedControllers()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        var source = File.ReadAllText(Path.Combine(dir!.FullName, "src", "Cybersole.Stores",
            "Flows", "DemandwareFlow.cs"));

        foreach (var invented in DemandwareControllers.Invented)
        {
            // the only allowed mention is inside a comment explaining why it went
            var uses = source.Split('\n')
                .Where(l => l.Contains('"' + invented + '"', StringComparison.Ordinal)
                            && !l.TrimStart().StartsWith("//", StringComparison.Ordinal))
                .ToList();

            _out.WriteLine($"{invented}: {uses.Count} live string literal(s)");
            Assert.Empty(uses);
        }

        Assert.Contains("DemandwareControllers.PlaceOrder", source);
    }
}
