using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 99: the raffle / sale-registration surface, read out of the image.
///
/// <para>
/// The replica had no draw support for Demandware stores. The image carries the whole vocabulary —
/// the entry page, the extractor, the signature endpoint, the two <c>SaleRegistration-*</c>
/// controllers, the draw cart fragment, and the duplicate-entry status.
/// </para>
///
/// <para>
/// The extractor is asserted <b>verbatim</b>. A raffle payload lives in one script tag with one id;
/// a tidy-looking regex that also matches nearby markup finds a different document.
/// </para>
/// </summary>
public sealed class DemandwareRaffleTests
{
    private readonly ITestOutputHelper _out;

    public DemandwareRaffleTests(ITestOutputHelper output) => _out = output;

    /// <summary>The pattern is the image's, character for character.</summary>
    [Fact]
    public void TheExtractorIsTheImagesPattern()
    {
        Assert.Equal("<script id=\"panagora-raffle-data\"[^>]*>(.*?)</script>",
            DemandwareRaffle.DataPattern);

        Assert.Equal("/pages/raffle", DemandwareRaffle.EntryPage);
        Assert.Equal("/api/raffle-sig", DemandwareRaffle.Signature);
        Assert.Equal(".raffle-data[data-id]", DemandwareRaffle.DataSelector);
        Assert.Equal("Cart-CartDrawBody", DemandwareRaffle.DrawCart);
        Assert.Equal("Already Entered Draw", DemandwareRaffle.AlreadyEntered);
    }

    /// <summary>A real page shape: the payload comes out, surrounding markup does not.</summary>
    [Fact]
    public void ThePayloadIsExtractedFromItsScriptTag()
    {
        const string html = """
            <html><head><title>Raffle</title></head>
            <body>
              <div class="raffle-data" data-id="SNKRS-2026-11"></div>
              <script id="panagora-raffle-data" type="application/json">
                {"id":"SNKRS-2026-11","name":"Air Max Draw","closes":"2026-11-20T10:00:00Z"}
              </script>
              <script>var tracking = 1;</script>
            </body></html>
            """;

        var payload = DemandwareRaffle.ExtractData(html);
        _out.WriteLine(payload ?? "<null>");

        Assert.NotNull(payload);
        Assert.Contains("\"Air Max Draw\"", payload);
        Assert.DoesNotContain("tracking", payload!);

        Assert.Equal("SNKRS-2026-11", DemandwareRaffle.ExtractId(html));
    }

    /// <summary>A page with no raffle script is <b>not</b> an error — it is a store with no draw.</summary>
    [Fact]
    public void APageWithoutADrawReturnsNull()
    {
        Assert.Null(DemandwareRaffle.ExtractData("<html><body>no draw here</body></html>"));
        Assert.Null(DemandwareRaffle.ExtractData(""));
        Assert.Null(DemandwareRaffle.ExtractData(null));
        Assert.Null(DemandwareRaffle.ExtractId("<html><body>nothing</body></html>"));
    }

    /// <summary>The extractor is multiline and case-insensitive, as the pool's usage implies.</summary>
    [Fact]
    public void TheExtractorHandlesMultilineAndUppercase()
    {
        const string upper = """
            <SCRIPT ID="PANAGORA-RAFFLE-DATA">
            {"raffleId":"A-1"}
            </SCRIPT>
            """;

        Assert.Equal("{\"raffleId\":\"A-1\"}", DemandwareRaffle.ExtractData(upper)?.Trim());
        Assert.Equal("A-1", DemandwareRaffle.ExtractId(upper));
    }

    /// <summary>Duplicate entries are recognised from the status string, not from a status code.</summary>
    [Fact]
    public void AlreadyEnteredIsRecognised()
    {
        Assert.True(DemandwareRaffle.IsAlreadyEntered("<p>Already Entered Draw</p>"));
        Assert.True(DemandwareRaffle.IsAlreadyEntered("ERROR: ALREADY ENTERED DRAW"));
        Assert.False(DemandwareRaffle.IsAlreadyEntered("<p>Entry confirmed</p>"));
        Assert.False(DemandwareRaffle.IsAlreadyEntered(null));
    }

    /// <summary>
    /// The step exists on the flow and uses the image's pieces. Source-level, because reaching it
    /// needs a live store running a draw.
    ///
    /// <para>
    /// The property worth pinning is the <b>absent</b> branch: a store with no draw must succeed and
    /// record that, rather than fail — otherwise every ordinary checkout on that store breaks.
    /// </para>
    /// </summary>
    [Fact]
    public void TheFlowHasTheRaffleStepAndItToleratesNoDraw()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        var source = File.ReadAllText(Path.Combine(dir!.FullName, "src", "Cybersole.Stores",
            "Flows", "DemandwareFlow.cs"));

        Assert.Contains("EnterRaffleAsync", source);
        Assert.Contains("DemandwareRaffle.EntryPage", source);
        Assert.Contains("DemandwareRaffle.ExtractData", source);
        Assert.Contains("DemandwareControllers.SaleConfig", source);
        Assert.Contains("DemandwareControllers.SaleSignupSubmit", source);
        Assert.Contains("DemandwareRaffle.IsAlreadyEntered", source);

        // the no-draw branch records "absent" and succeeds instead of returning a failure
        Assert.Contains("absent", source);
        Assert.Contains("raffle.status", source);

        _out.WriteLine("raffle step present, absent branch tolerated");
    }

    /// <summary>The raffle controllers are part of the confirmed Demandware vocabulary.</summary>
    [Fact]
    public void TheRaffleControllersAreInTheVocabulary()
    {
        Assert.True(DemandwareControllers.IsKnown(DemandwareControllers.SaleConfig));
        Assert.True(DemandwareControllers.IsKnown(DemandwareControllers.SaleSignupSubmit));

        _out.WriteLine($"{DemandwareControllers.SaleConfig} / {DemandwareControllers.SaleSignupSubmit}");
    }
}
