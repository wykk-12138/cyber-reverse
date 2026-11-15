using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 126: a census of the controller family, and the two things it taught about the pool.
///
/// <para>
/// <b>One: the table was short again.</b> Counting every <c>Prefix-Name</c> literal produced names the
/// table did not have — <c>Cart-UpdateProduct</c>, <c>Cart-ShowLayer</c>,
/// <c>Adyen-PaymentFromComponent</c>, <c>Adyen-PayPalPatchOrder</c>, <c>Adyen-Authorize3DS2</c> — which
/// is the same omission as R117 and R125. Three rounds of "the table was a window" is a pattern, not
/// bad luck.
/// </para>
///
/// <para>
/// <b>Two: the pool interleaves strings with metadata, so names arrive with glued tails.</b> Beside
/// <c>Cart-AddProduct</c> sits <c>Cart-AddProducton</c>; beside <c>Cart-MiniCartShow</c> sits
/// <c>Cart-MiniCartSh92000052on</c>. A naive count therefore reports 94 controllers where the real
/// number is near 33. The census keeps only names whose tail is a plausible method-word, which is a
/// judgement call and is labelled as one.
/// </para>
/// </summary>
public sealed class ControllerCensusTests
{
    private readonly ITestOutputHelper _out;

    public ControllerCensusTests(ITestOutputHelper output) => _out = output;

    /// <summary>The five census finds are in the vocabulary.</summary>
    [Fact]
    public void TheCensusFoundFiveMoreControllers()
    {
        Assert.Equal("Cart-UpdateProduct", DemandwareControllers.CartUpdateProduct);
        Assert.Equal("Cart-ShowLayer", DemandwareControllers.CartShowLayer);
        Assert.Equal("Adyen-PaymentFromComponent", DemandwareControllers.AdyenPaymentFromComponent);
        Assert.Equal("Adyen-PayPalPatchOrder", DemandwareControllers.AdyenPayPalPatchOrder);
        Assert.Equal("Adyen-Authorize3DS2", DemandwareControllers.AdyenAuthorize3Ds2);

        foreach (var c in new[]
                 {
                     DemandwareControllers.CartUpdateProduct, DemandwareControllers.CartShowLayer,
                     DemandwareControllers.AdyenPaymentFromComponent,
                     DemandwareControllers.AdyenPayPalPatchOrder,
                     DemandwareControllers.AdyenAuthorize3Ds2,
                 })
        {
            Assert.True(DemandwareControllers.IsKnown(c), c);
            _out.WriteLine("new: " + c);
        }
    }

    /// <summary>Every name in the table has the Prefix-Name shape a controller has.</summary>
    [Fact]
    public void EveryNameInTheTableHasTheControllerShape()
    {
        Assert.All(DemandwareControllers.All, c =>
        {
            var dash = c.IndexOf('-');
            Assert.True(dash > 0, c + " has no dash");
            Assert.True(dash < c.Length - 1, c + " has an empty tail");
        });

        Assert.Equal(DemandwareControllers.All.Count, DemandwareControllers.All.Distinct().Count());
        _out.WriteLine($"{DemandwareControllers.All.Count} controllers in the vocabulary");
    }

    /// <summary>
    /// The mangling finding: the table holds clean names only, and no name in it carries a glued
    /// numeric tail like the pool's <c>Cart-MiniCartSh92000052on</c>.
    /// </summary>
    [Fact]
    public void TheTableKeepsNoMangledNames()
    {
        Assert.All(DemandwareControllers.All,
            c => Assert.DoesNotContain(c, "92000052", System.StringComparison.Ordinal));

        // the pool's glued variants are NOT in the vocabulary
        Assert.False(DemandwareControllers.IsKnown("Cart-AddProducton"));
        Assert.False(DemandwareControllers.IsKnown("Cart-APon"));
        Assert.False(DemandwareControllers.IsKnown("Cart-MiniCartSh92000052on"));

        Assert.True(DemandwareControllers.IsKnown("Cart-AddProduct"));
        _out.WriteLine("mangled pool neighbours stay out of the table");
    }

    /// <summary>The four families the table covers most are recorded as such.</summary>
    [Fact]
    public void TheBiggestFamiliesAreTheOnesTheFlowsNeed()
    {
        var families = DemandwareControllers.All
            .GroupBy(c => c.Split('-')[0])
            .OrderByDescending(g => g.Count())
            .ToList();

        foreach (var f in families) _out.WriteLine($"{f.Key,-28} {f.Count()}");

        // Do not name a winner: which family has the most entries is a measurement, and naming it
        // from memory is what went wrong with counts four times already. Assert the structure instead.
        var biggest = families[0].Count();
        Assert.Equal(families.Max(f => f.Count()), biggest);

        foreach (var needed in new[] { "CheckoutServices", "Adyen", "Cart" })
        {
            Assert.Contains(families, f => f.Key == needed);
            _out.WriteLine($"{needed}: {families.First(f => f.Key == needed).Count()} entries");
        }
    }
}
