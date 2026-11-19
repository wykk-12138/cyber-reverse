using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1258: HBX's cart endpoint is attested with its host attached, which is stronger than the assembled Magento case.
/// </summary>
public sealed class HbxApiTests
{
    [Fact]
    public void TheCartEndpointIsCarriedWithItsHost()
    {
        Assert.Equal("https://hbx.com/api/v1/carts", HbxApi.CartsAbsolute);
        Assert.Equal("https://hbx.com/api/v1/carts/", HbxApi.CartsAbsoluteSlash);
        Assert.Equal("api/v1/carts", HbxApi.CartsToken);
    }

    [Fact]
    public void TheOriginPlusTokenReproducesTheAbsoluteLiteral()
    {
        // this is the whole point: the replica builds origin + path, the image writes the joined form out
        Assert.Equal(HbxApi.CartsAbsolute, HbxApi.CartsUrl("https://hbx.com"));
        Assert.Equal(HbxApi.CartsAbsolute, HbxApi.CartsUrl("https://hbx.com/"));
    }

    [Fact]
    public void TheV2ShapeTheReplicaDoesNotUseIsRecorded()
    {
        Assert.Equal("api/v2/carts/contents/", HbxApi.CartsContentsV2);
        Assert.DoesNotContain("shop", HbxApi.CartsContentsV2);
    }
}
