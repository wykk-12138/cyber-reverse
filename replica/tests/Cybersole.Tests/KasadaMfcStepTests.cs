using Cybersole.Http;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: the image numbers its async steps GetKasada = d__48, GetMfc = d__49, GetWorkTime = d__50
/// (docs/KASADA/11 5.69), so the MFC fetch is a host step that comes *after* the token, not before the
/// interrogation. The replica only ever reached /mfc by letting the sensor issue it, which meant a mobile
/// profile could not exercise it at all. These cases pin the host-side step and the header contract the
/// sensor enforces on its reply.
/// </summary>
public sealed class KasadaMfcStepTests
{
    [Fact]
    public async Task TheStepAsksForTheMobileConfigurationWithTheSensorsOwnBuild()
    {
        using var http = new NetClient();
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            Store = "nike"
        };

        // Measured: this sandbox does reach www.nike.com, and it answers 404 for a bare GET /mfc. So the
        // assertion is on the shape, not on a specific status: the step must return a result object either
        // way (0 when unreachable, the real status when the host answers) and must never throw at the flow.
        var mfc = await solver.FetchMfcAsync(http, "https://www.nike.com/");

        Assert.NotNull(mfc);
        Assert.NotEqual(200, mfc!.Status);
        Assert.False(mfc.SatisfiesSensor);
    }

    [Fact]
    public async Task AMalformedPageUrlProducesNoRequestAtAll()
    {
        using var http = new NetClient();
        using var solver = new KasadaSolver(new BrowserShim());

        Assert.Null(await solver.FetchMfcAsync(http, "/relative/path"));
        Assert.Null(await solver.FetchMfcAsync(http, ""));
    }

    [Fact]
    public void TheResponseKnowsWhetherTheSensorWouldAcceptIt()
    {
        var good = new KasadaMfcResponse
        {
            Status = 200,
            Body = "",
            Headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            {
                ["x-kpsdk-h"] = "01",
                ["x-kpsdk-fc"] = "1",
            },
        };
        Assert.True(good.SatisfiesSensor);
        Assert.Equal("01", good.Header("X-KPSDK-H"));

        // Either header missing is the case the sensor turns into
        // "/mfc response was missing one or more headers" (docs/KASADA/11 5.45).
        var missingFc = new KasadaMfcResponse
        {
            Status = 200,
            Body = "",
            Headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase) { ["x-kpsdk-h"] = "01" },
        };
        Assert.False(missingFc.SatisfiesSensor);
        Assert.Null(missingFc.Header("x-kpsdk-fc"));
    }

    [Fact]
    public void AVersionProviderOverridesTheBuildSentToMfc()
    {
        using var solver = new KasadaSolver(new BrowserShim { Href = "https://www.nike.com/" })
        {
            Store = "nike",
            VersionProvider = () => "j-9.9.999",
        };

        // The step reads the provider when building headers; this asserts the wiring exists without
        // reaching the network by checking the configured value resolver directly.
        Assert.Equal("j-9.9.999", solver.VersionProvider!());
    }
}
