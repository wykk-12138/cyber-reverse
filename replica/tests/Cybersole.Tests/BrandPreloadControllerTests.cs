using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1173: the two brand storefronts' preload controllers.
///
/// <para>
/// R1172 established that Jacquemus and Maison Margiela are stores the image supports and that the replica
/// has neither. Their step tables are unobserved, so no behaviour can be written yet; what can be written
/// is the half that is a fact, that both storefronts expose a <c>X-Preload</c> controller action, and pinning
/// it here means the future store module has a name to call rather than a guess to make.
/// </para>
/// </summary>
public sealed class BrandPreloadControllerTests
{
    [Fact]
    public void BothBrandsPreloadControllersAreRegistered()
    {
        Assert.Contains(DemandwareControllers.JacquemusPreload, DemandwareControllers.All);
        Assert.Contains(DemandwareControllers.MargielaPreload, DemandwareControllers.All);
    }

    /// <summary>Controller-action names: the store's own name, a hyphen, and the action.</summary>
    [Fact]
    public void TheyKeepTheControllerActionShape()
    {
        Assert.Equal("Jacquemus-Preload", DemandwareControllers.JacquemusPreload);
        Assert.Equal("Margiela-Preload", DemandwareControllers.MargielaPreload);
        foreach (var name in new[]
                 {
                     DemandwareControllers.JacquemusPreload,
                     DemandwareControllers.MargielaPreload,
                 })
        {
            Assert.Contains('-', name);
            Assert.DoesNotContain('/', name);
        }
    }
}
