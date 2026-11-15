using Cybersole.Core.Models;
using Cybersole.Services;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R22: the whole Kasada path through the real flow — not the solver in isolation.
/// </summary>
[Trait("Speed", "Slow")]
public class NikeKasadaFlowTests
{
    private readonly ITestOutputHelper _out;
    public NikeKasadaFlowTests(ITestOutputHelper output) => _out = output;

    private static FlowContext Ctx(AppServices services) => new()
    {
        Http = services.Http,
        Url = "https://www.nike.com/",
        Product = new Product { Name = "x", Url = "https://www.nike.com/" },
        TimeoutSeconds = 60,
    };

    [Fact]
    public async Task TheFlowProducesARealTokenThroughTheBrowser()
    {
        using var services = TestServices.Create();
        var ctx = Ctx(services);
        var flow = new NikeFlow();

        var outcome = await flow.GenerateSensorAsync(ctx, default);

        _out.WriteLine($"ok      = {outcome.Ok}");
        _out.WriteLine($"error   = {outcome.Error}");
        _out.WriteLine($"source  = {(ctx.Session.Vars.TryGetValue("kasada.source", out var src) ? src : "(none)")}");
        _out.WriteLine($"ua      = {ctx.Session.UserAgent}");
        _out.WriteLine($"cookies = {ctx.Session.Cookies.Count}");
        foreach (var kv in ctx.Session.AntiBotTokens)
            _out.WriteLine($"  token {kv.Key} = {(kv.Value.Length > 50 ? kv.Value[..50] + "..." : kv.Value)}");

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("chromium", ctx.Session.Vars["kasada.source"]);
    }

    [Fact]
    public async Task TheTokenCarriesTheBrowserIdentity()
    {
        using var services = TestServices.Create();
        var ctx = Ctx(services);
        var flow = new NikeFlow();

        var outcome = await flow.GenerateSensorAsync(ctx, default);
        Assert.True(outcome.Ok, outcome.Error);

        // ct is mandatory
        Assert.True(ctx.Session.AntiBotTokens.ContainsKey("x-kpsdk-ct"));
        Assert.True(ctx.Session.AntiBotTokens["x-kpsdk-ct"].Length >= 16);

        // the UA the token was minted under must be the one we will present
        Assert.False(string.IsNullOrWhiteSpace(ctx.Session.UserAgent));
        Assert.DoesNotContain("Headless", ctx.Session.UserAgent!, StringComparison.OrdinalIgnoreCase);

        // version travels too
        Assert.StartsWith("j-", ctx.Session.Vars["kasada.v"]);
    }

    [Fact]
    public async Task TheScriptEngineFallbackIsNotSilentlyPreferred()
    {
        using var services = TestServices.Create();
        var ctx = Ctx(services);
        var flow = new NikeFlow();

        await flow.GenerateSensorAsync(ctx, default);


        // A browser exists on this machine, so the browser path must have won.
        Assert.Equal("chromium", ctx.Session.Vars["kasada.source"]);
        Assert.DoesNotContain("kasada.browserError", ctx.Session.Vars.Keys);
    }
}

