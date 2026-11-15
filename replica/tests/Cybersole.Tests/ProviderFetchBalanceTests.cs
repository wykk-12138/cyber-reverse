using Cybersole.Core.Settings;
using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R378: <c>CloudflareSolversView.FetchBalance</c> — the page's balance check, as a member instead of a lambda.
///
/// <para>
/// The two early exits are the ones worth pinning: no provider at all, and a provider without an API key. Both must answer
/// with their own sentence and must not try a request — the second one used to be possible only through the button.
/// </para>
/// </summary>
public sealed class ProviderFetchBalanceTests
{
    private readonly ITestOutputHelper _out;
    public ProviderFetchBalanceTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void WithoutAProviderItSaysSo()
    {
        using var services = TestServices.Create();
        var view = new CloudflareSolversView(services);

        var text = view.FetchBalanceCore();

        _out.WriteLine(text);
        Assert.Equal("No Cloudflare provider configured.", text);
    }

    [Fact]
    public void WithoutAnApiKeyItSaysSoAndDoesNotAsk()
    {
        using var services = TestServices.Create();
        services.Config.Settings.CloudflareSolvers.Add(new CloudflareSolverConfig { Name = "cf", Type = "uncaptcha.io" });

        var view = new CloudflareSolversView(services);
        var text = view.FetchBalanceCore();

        _out.WriteLine(text);
        Assert.Equal("cf: no API key, so no balance to ask for.", text);
    }
}
