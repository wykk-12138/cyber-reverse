using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: the image keys the sensor build per store — seven "&lt;Store&gt;-Kasada-Version" settings
/// entries (docs/KASADA/11 5.75). These cases pin the table's shape and, more importantly, that it stays a
/// *fallback*: the header the sensor stamps on its own request is still what wins, because the gate
/// compares x-kpsdk-v against what the site's own script published.
/// </summary>
public sealed class KasadaVersionsTests
{
    [Fact]
    public void TheTableCarriesExactlyTheSevenKeysTheImageCarries()
    {
        // The binary's list; the replica previously carried only five and was missing Nike and Scheels.
        Assert.Equal(7, KasadaVersions.SettingKeys.Count);
        Assert.Contains("Nike-Kasada-Version", KasadaVersions.SettingKeys);
        Assert.Contains("Scheels-Kasada-Version", KasadaVersions.SettingKeys);
        Assert.Contains("Crocs-EU-Kasada-Version", KasadaVersions.SettingKeys);
        Assert.Contains("Crocs-JP-Kasada-Version", KasadaVersions.SettingKeys);
        Assert.Contains("Crocs-Kasada-Version", KasadaVersions.SettingKeys);
        Assert.Contains("Converse-Kasada-Version", KasadaVersions.SettingKeys);
        Assert.Contains("Footsites-Kasada-Version", KasadaVersions.SettingKeys);
    }

    [Fact]
    public void EverySettingKeyResolvesToAStoreAndAStoreResolvesToAVersion()
    {
        foreach (var key in KasadaVersions.SettingKeys)
        {
            var store = KasadaVersions.StoreOfSetting(key);
            Assert.False(string.IsNullOrEmpty(store), key);
            Assert.Equal(KasadaVersions.Observed, KasadaVersions.For(store));
            Assert.Equal(KasadaVersions.Observed, KasadaVersions.For(store!.ToUpperInvariant()));
        }
    }

    [Fact]
    public void AnUnknownStoreAnswersNullRatherThanGuessing()
    {
        // A wrong build string fails the gate exactly like a missing one, but looks deliberate. Answering
        // null keeps this table one link in a fallback chain instead of its terminal answer.
        Assert.Null(KasadaVersions.For("some-store-we-never-measured"));
        Assert.Null(KasadaVersions.For(null));
        Assert.Null(KasadaVersions.For("   "));
        Assert.Null(KasadaVersions.StoreOfSetting("Nike-NotAVersion"));
    }
}
