using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Pop Mart's endpoint constants, held against the image's own inventory.
///
/// <para>
/// R890. Enumerating every <c>/shop/v1/</c> literal in the image yields forty-one distinct paths. Before this round the
/// constant class held thirty-nine, missing <c>store_ticket/reserve</c> and <c>store_ticket/sessionList</c>, and none
/// of its constants was absent from the image — so the gap was exactly two and the direction of the error was
/// one-sided.
/// </para>
///
/// <para>
/// These tests pin both directions. A missing constant means an endpoint the image has and the replica cannot call; an
/// extra constant means one I invented. The first is a gap, the second is a fabrication, and a count alone cannot tell
/// them apart.
/// </para>
/// </summary>
public class PopMartEndpointCoverageTests
{
    /// <summary>The image's inventory of <c>/shop/v1/</c> paths, recovered by scanning its string table.</summary>
    private static readonly string[] ImagePaths =
    {
        "/shop/v1/box/boxCart/addBoxListToCart",
        "/shop/v1/box/box_set/extract",
        "/shop/v1/box/box_set/preview",
        "/shop/v1/box/box_spu/detail",
        "/shop/v1/box/extract",
        "/shop/v1/box/goodsListV2",
        "/shop/v1/coupons/list",
        "/shop/v1/coupons/verify",
        "/shop/v1/drawScratch/chooseGoods",
        "/shop/v1/drawScratch/detail?uniqCode=",
        "/shop/v1/drawScratch/draw",
        "/shop/v1/drawScratch/megaDraw/hit",
        "/shop/v1/freight/result",
        "/shop/v1/mission/claim_reward",
        "/shop/v1/mission/list?group_name=mission_center",
        "/shop/v1/mission/trigger/check_in",
        "/shop/v1/order/list?currentPage=1&pageSize=20",
        "/shop/v1/order/pre/counter",
        "/shop/v1/order/pre/v2/buyNow",
        "/shop/v1/order/v2/detailV2?orderNo=",
        "/shop/v1/promotion/getList",
        "/shop/v1/redeem/lucky_points_redeem_draw",
        "/shop/v1/redeem/points_redeem_draw",
        "/shop/v1/shop/adyen/details",
        "/shop/v1/shop/can/place/order",
        "/shop/v1/shop/cash/desk/adyen/details",
        "/shop/v1/shop/cash/desk/adyen/pay",
        "/shop/v1/shop/cash/desk/alipayGlobal/pay",
        "/shop/v1/shop/cash/desk/pay/query",
        "/shop/v1/shop/cash/desk/paypal/pay",
        "/shop/v1/shop/cash/desk/stripe/customerSession",
        "/shop/v1/shop/cash/desk/stripe/pay",
        "/shop/v1/shop/productDetails?spuId=",
        "/shop/v1/shoppingcart/shoppingCartDataList?actionType=",
        "/shop/v1/storeOfflineDraw/info?alias=",
        "/shop/v1/storeOfflineDraw/join",
        "/shop/v1/storeOfflineDraw/joinResult?alias=",
        "/shop/v1/store_ticket/dateList",
        "/shop/v1/store_ticket/mainPage?uniqID=",
        "/shop/v1/store_ticket/reserve",
        "/shop/v1/store_ticket/sessionList",
    };

    /// <summary>Forty-one, which is what the image has. Not thirty-nine, which is what this file had.</summary>
    [Fact]
    public void TheImageHasFortyOneShopPaths()
    {
        Assert.Equal(41, ImagePaths.Length);
        Assert.Equal(41, ImagePaths.Distinct().Count());
    }

    /// <summary>
    /// Every path the image names must appear verbatim among the constants. A path in the image that the replica never
    /// strings together is an endpoint it cannot call.
    /// </summary>
    [Fact]
    public void EveryImagePathAppearsInTheConstants()
    {
        var source = File.ReadAllText(SourcePath());
        var missing = ImagePaths.Where(p => !source.Contains("\"" + p + "\"")).ToList();

        Assert.True(missing.Count == 0,
            "endpoints the image has and the constants do not: " + string.Join(", ", missing));
    }

    /// <summary>
    /// The reverse: every <c>/shop/v1/</c> literal in the constants must exist in the image. This is the check that
    /// catches an invented endpoint, which is worse than a missing one because it looks like coverage.
    /// </summary>
    [Fact]
    public void EveryConstantAppearsInTheImage()
    {
        var source = File.ReadAllText(SourcePath());
        var declared = Regex.Matches(source, "\"(/shop/v1/[^\"]*)\"")
            .Select(m => m.Groups[1].Value)
            .Distinct()
            .ToList();

        var extra = declared.Where(p => !ImagePaths.Contains(p)).ToList();
        Assert.True(extra.Count == 0,
            "constants naming endpoints the image does not have: " + string.Join(", ", extra));
    }

    private static string SourcePath()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null && !Directory.Exists(Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return Path.Combine(dir!.FullName, "src", "Cybersole.Stores", "Flows", "PopMartEndpoints.cs");
    }
}
