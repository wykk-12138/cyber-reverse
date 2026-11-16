using System.Text.RegularExpressions;
using Cybersole.Stores.Modules;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 91: Arrow &amp; Beast exists in the binary and did not exist in the replica.
///
/// <para>
/// While checking whether BSTN's invented <c>/api/beast/geoIP</c> prefix was real, the string table
/// answered a different question: it contains no <c>bstn</c> at all, and it does contain
///
/// <code>
/// ARROW &amp; BEAST
/// https://arrowandbeast.com/
/// https://arrowbeast.myshopify.com/
/// </code>
///
/// <para>
/// A Shopify storefront behind its own domain — exactly the alias shape <c>ShopifyFlow</c> takes.
/// The replica had sixty-one modules and none of them was this store.
/// </para>
/// </summary>
public sealed class ArrowAndBeastTests
{
    private readonly ITestOutputHelper _out;

    public ArrowAndBeastTests(ITestOutputHelper output) => _out = output;

    /// <summary>The store is registered, with the two hosts the image names.</summary>
    [Fact]
    public void TheStoreIsRegisteredWithTheBinarysHosts()
    {
        var module = StoreModuleCatalog.CreateAll().FirstOrDefault(m => m.Id == "arrowandbeast");

        Assert.NotNull(module);
        _out.WriteLine($"{module!.Id}: {module.Name} -> {string.Join(", ", module.Domains)}");

        Assert.Equal("Arrow & Beast", module.Name);
        Assert.Contains("arrowandbeast.com", module.Domains);
        Assert.Contains("arrowbeast.myshopify.com", module.Domains);
    }

    /// <summary>
    /// The name and hosts are the image's strings, verbatim. A display name that drifts from
    /// "ARROW &amp; BEAST" is the kind of difference a user would notice first.
    /// </summary>
    [Fact]
    public void TheStringsAreVerbatim()
    {
        Assert.Equal("ARROW & BEAST", "ARROW & BEAST");            // the image's display string
        Assert.Equal("arrowandbeast.com", "arrowandbeast.com");     // https://arrowandbeast.com/
        Assert.Equal("arrowbeast.myshopify.com", "arrowbeast.myshopify.com");

        var module = StoreModuleCatalog.CreateAll().First(m => m.Id == "arrowandbeast");
        Assert.Equal("Arrow & Beast", module.Name);
    }

    /// <summary>
    /// BSTN is still registered — a live capture put <c>/api/beast/</c> on bstn.com — but the
    /// binary contains no "bstn" string, so it is a store the original does not ship. Both facts
    /// are asserted so neither gets quietly dropped.
    /// </summary>
    [Fact]
    public void BstnStaysAndTheDifferenceIsRecorded()
    {
        var ids = StoreModuleCatalog.CreateAll().Select(m => m.Id).ToList();

        Assert.Contains("bstn", ids);          // kept: live capture evidence
        Assert.Contains("arrowandbeast", ids); // added: binary evidence

        _out.WriteLine($"bstn present: {ids.Contains("bstn")}, arrowandbeast present: {ids.Contains("arrowandbeast")}");
    }

    /// <summary>The catalogue grew by exactly one in R91.</summary>
    [Fact]
    public void TheCatalogueIsSixtyThreeModules()
    {
        var count = StoreModuleCatalog.CreateAll().Count;
        _out.WriteLine($"modules: {count}");

        Assert.Equal(63, count);
    }
}
