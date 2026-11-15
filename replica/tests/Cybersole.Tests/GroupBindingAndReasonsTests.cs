using Cybersole.Core.Models;
using Cybersole.Http.Stores;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Two bindings the live UI implies but the replica was missing.
///
/// 1. Cloudflare Providers carries the subtitle "pick one per task group", and the
///    Notifications/Captcha tabs hang off the same group — so the *group* carries the
///    provider ids, not the global settings.
/// 2. Failure reasons come from the Get Help catalogue, so a 403 reads
///    "[General] Forbidden" rather than "403".
/// </summary>
public class GroupBindingAndReasonsTests
{
    [Fact]
    public void AGroupCarriesItsProviderChoices()
    {
        var group = new StoreGroup { Name = "Group 1" };

        Assert.Null(group.CloudflareProviderId);
        Assert.Null(group.CaptchaProviderId);

        group.CloudflareProviderId = "uncaptcha.io";
        group.CaptchaProviderId = "capmonster";

        Assert.Equal("uncaptcha.io", group.CloudflareProviderId);
        Assert.Equal("capmonster", group.CaptchaProviderId);
    }

    [Fact]
    public void MonitorContextCarriesTheGroupSelection()
    {
        using var http = new Cybersole.Http.NetClient();

        var ctx = new MonitorContext
        {
            Http = http,
            Url = "https://example.com/products/x",
            CloudflareProviderId = "uncaptcha.io",
            CaptchaProviderId = "capsolver",
            GroupId = "g1",
        };

        Assert.Equal("uncaptcha.io", ctx.CloudflareProviderId);
        Assert.Equal("capsolver", ctx.CaptchaProviderId);
        Assert.Equal("g1", ctx.GroupId);
    }

    [Fact]
    public void ProviderSelectionIsOptional()
    {
        using var http = new Cybersole.Http.NetClient();

        // no group chosen -> nulls, and the run falls back to the global defaults
        var ctx = new MonitorContext { Http = http, Url = "https://example.com/" };

        Assert.Null(ctx.CloudflareProviderId);
        Assert.Null(ctx.CaptchaProviderId);
        Assert.Null(ctx.GroupId);
    }

    [Theory]
    [InlineData(403, "general.forbidden")]
    [InlineData(404, "general.notfound")]
    [InlineData(503, "general.unavailable")]
    [InlineData(0, "general.connection")]
    public void MonitorFailuresNameTheCatalogueEntry(int status, string expectedId)
    {
        var entry = ErrorCatalog.Classify(status, StepStage.Monitor);
        Assert.Equal(expectedId, entry.Id);
    }

    [Fact]
    public void ReasonsAreHumanReadableNotBareCodes()
    {
        var entry = ErrorCatalog.Classify(403, StepStage.Monitor);

        // the whole point: not "403"
        Assert.Equal("[General] Forbidden", entry.Title);
        Assert.DoesNotContain("403", entry.Title);
        Assert.True(entry.Detail.Length > 20);
    }
}
