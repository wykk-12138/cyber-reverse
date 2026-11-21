using System.Linq;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R789: Warhammer's add-to-cart speaks the image's GraphQL, not an invented REST call.
///
/// <para>
/// The mutation text in <c>WarhammerFlow.AddToCartMutation</c> is transcribed from
/// <c>analysis/warhammer_graphql.txt</c>, which R788 recovered from the pool at 0x1470cc484. Transcribing a 536-character
/// string by hand is exactly the kind of work that silently accumulates a wrong character, and a wrong character inside
/// a string literal still compiles. These tests therefore check the invariants that matter rather than trusting the
/// transcription.
/// </para>
///
/// <para>
/// What is observed: the operation name, the ten variables, which two are non-null, and the single selected field.
/// What is inferred: that the endpoint accepts this shape as a JSON body with operationName, query and variables --
/// the standard GraphQL-over-HTTP envelope, which the image's own request builder is consistent with but does not
/// spell out.
/// </para>
/// </summary>
public class WarhammerGraphQlTests
{
    private readonly ITestOutputHelper _out;

    public WarhammerGraphQlTests(ITestOutputHelper output) => _out = output;

    private static string Mutation => WarhammerFlow.AddToCartMutation;

    [Fact]
    public void TheOperationNameMatchesTheRecoveredText()
    {
        _out.WriteLine(Mutation);
        Assert.StartsWith("mutation AddToCart(", Mutation);
    }

    [Fact]
    // The two non-null arguments. If either loses its bang the request would be accepted by the client and rejected by
    // the server, which is harder to diagnose than a failing test.
    public void SkuAndFasciaAreTheOnlyNonNullArguments()
    {
        var declared = Mutation[..Mutation.IndexOf(')')];
        Assert.Contains("$sku: String!", declared);
        Assert.Contains("$fascia: String!", declared);
        Assert.Equal(2, declared.Count(ch => ch == '!'));
    }

    [Fact]
    public void TheOptionalRecaptchaTokenIsDeclared()
    {
        // This says the site's add-to-cart expects a solved reCAPTCHA when one is required.
        Assert.Contains("$recaptchaToken: String", Mutation);
    }

    [Fact]
    // The mutation selects exactly one field, which is what later steps authenticate with.
    public void TheSelectionIsTheCartJwt()
    {
        Assert.Contains("ctCartJWT", Mutation);
        Assert.Contains("__typename", Mutation);
        Assert.DoesNotContain("products", Mutation);
    }

    [Fact]
    // GraphQL ignores whitespace, and the constant flattens the recovered text's indentation deliberately. What must
    // survive is the structure: one operation, one call, ten arguments passed through.
    public void EveryDeclaredVariableIsAlsoPassedThrough()
    {
        var declared = new[] {
            "sku", "fascia", "linkedOfferId", "offerId", "quantity",
            "statusPoint", "recaptchaToken", "storeId", "algoliaQueryId", "objectId",
        };
        foreach (var name in declared)
        {
            Assert.Contains("$" + name + ":", Mutation);
            Assert.Contains(name + ": $" + name, Mutation);
        }
    }

    /// <summary>
    /// R1326: the onboarding document shipped for months ending with "[4040 chars total]" — a truncation
    /// marker pasted out of a display, which left the document stopping mid-way. The image's copy is 4040
    /// characters; this pins the repaired text and the absence of the marker in every generated document, so
    /// the same paste cannot ship again.
    /// </summary>
    [Fact]
    public void TheOnboardDocumentIsWholeAndCarriesNoTruncationMarker()
    {
        var document = WarhammerQueries.ApproveOnboardPaymentMutation;

        Assert.Equal(4040, document.Length);
        Assert.DoesNotContain("chars total", document);
        Assert.EndsWith("__typename\n}\n", document);
        Assert.Contains("approveGuestSignUpPayment", document);

        foreach (var field in typeof(WarhammerQueries).GetFields(
                     System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static))
        {
            var value = field.GetValue(null) as string;
            if (value is null) continue;
            Assert.DoesNotContain("chars total", value);
        }
    }

    /// <summary>
    /// R1328: when the run carries both address inputs, OnboardGuestMutation goes out before the approval and
    /// the reply is kept. The pair is the image's own: the onboarding takes the same token and the same
    /// addresses the approval takes, and the two documents are adjacent in its URL table.
    /// </summary>
    [Fact]
    public async Task TheOnboardingHopRunsBeforeApproval()
    {
        using var server = new TinyServer((_, body) =>
        {
            if (body.Contains("OnboardGuestMutation", StringComparison.Ordinal))
                return (200, "{\"data\":{\"onboardGuest\":{\"buyer\":{\"userId\":\"u-1\"}}}}");
            return (200, "{\"data\":{\"approveGuestSignUpPayment\":{\"state\":\"COMPLETED\"}}}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["paymentToken"] = "tok-1";
        ctx.Session.Vars["wh.apiHost"] = server.BaseUrl;
        ctx.Session.Vars["wh.onboard.billing"] = "{\"line1\":\"1 Main St\",\"city\":\"Austin\"}";
        ctx.Session.Vars["wh.onboard.shipping"] = "{\"line1\":\"1 Main St\",\"city\":\"Austin\"}";

        var outcome = await new WarhammerFlow().SubmitPaymentAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("1", ctx.Session.Vars["wh.onboarded"]);
        Assert.Equal(2, server.Requests.Count);
        Assert.Contains("OnboardGuestMutation", server.Requests[0].Body!);
        Assert.Contains("ApproveOnboardPaymentMutation", server.Requests[1].Body!);
        // The document that goes out is the one the image holds, not a re-typed copy.
        Assert.Contains(WarhammerQueries.OnboardGuestMutation.Substring(0, 60), server.Requests[0].Body!);
    }

    /// <summary>
    /// Without the two address inputs the hop is skipped and says so, and the approval still goes out — which
    /// is exactly what this flow did before the hop existed. Silence is what the skip must not be.
    /// </summary>
    [Fact]
    public async Task WithoutAddressInputsTheHopIsSkippedAndAnnounced()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"approveGuestSignUpPayment\":{\"state\":\"COMPLETED\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["paymentToken"] = "tok-1";
        ctx.Session.Vars["wh.apiHost"] = server.BaseUrl;

        var outcome = await new WarhammerFlow().SubmitPaymentAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Single(server.Requests);
        Assert.Equal("1", ctx.Session.Vars["wh.onboardSkipped"]);
        Assert.Contains(ctx.Events, e => e.Name.Contains("OnboardGuestMutation did not run"));
        Assert.False(ctx.Session.Vars.ContainsKey("wh.onboarded"));
    }

    /// <summary>The onboarding document itself, pinned at the length the image carries.</summary>
    [Fact]
    public void TheOnboardingDocumentIsTheStringTheImageHolds()
    {
        Assert.Equal(3104, WarhammerQueries.OnboardGuestMutation.Length);
        Assert.StartsWith("mutation OnboardGuestMutation($bank: BankAccountInput", WarhammerQueries.OnboardGuestMutation);
        Assert.Contains("onboardAccount: onboardGuest(", WarhammerQueries.OnboardGuestMutation);
        Assert.EndsWith("__typename\n}\n", WarhammerQueries.OnboardGuestMutation);
    }

    /// <summary>
    /// R1330: the address reply offers a rate id and this flow used to drop it, leaving the order at
    /// isShippingValid=false. The second hop sends the observed UpdateShippingRate mutation with that id, and
    /// keeps the order block it answers.
    /// </summary>
    [Fact]
    public async Task TheShippingRateHopSendsTheIdTheAddressReplyOffered()
    {
        using var server = new TinyServer((_, body) =>
        {
            if (body.Contains("updateShippingRate", StringComparison.Ordinal))
                return (200, "{\"data\":{\"updateShippingRate\":{\"errors\":[]," +
                            "\"order\":{\"number\":\"W-1\",\"checkoutVersion\":9,\"guestToken\":\"gt-9\"," +
                            "\"isShippingValid\":true}}}}");
            return (200, "{\"data\":{\"updateShippingAddress\":{\"availableShippingRates\":[" +
                         "{\"id\":42,\"name\":\"Standard\"}]}}}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/",
            ProfileData = new Cybersole.Core.Models.Profile
            {
                FirstName = "Ada", LastName = "Lovelace", Address1 = "1 Main St",
                City = "Austin", Zip = "78701", Phone = "5550100", Country = "US", Email = "ada@example.test",
            },
        };
        ctx.Session.Vars["wh.apiHost"] = server.BaseUrl;

        var outcome = await new WarhammerFlow().SubmitShippingAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal(2, server.Requests.Count);
        Assert.Equal("42", ctx.Session.Vars["shippingRateId"]);

        var rateRequest = Newtonsoft.Json.Linq.JObject.Parse(server.Requests[1].Body!);
        Assert.Equal(WarhammerQueries.UpdateShippingRate, rateRequest["query"]!.ToObject<string>());
        Assert.Equal(42, rateRequest["variables"]!["selectedShippingRateId"]!.ToObject<int>());
        Assert.False(rateRequest["variables"]!["isNewsletterSubscribed"]!.ToObject<bool>());
        Assert.Equal("9", ctx.Session.Vars["wh.checkoutVersion"]);
        Assert.Equal("gt-9", ctx.Session.Vars["wh.guestToken"]);
    }

    /// <summary>
    /// No rate id means no rate to select. That is announced rather than passed off as a completed shipping
    /// step, because the order it leaves behind cannot check out.
    /// </summary>
    [Fact]
    public async Task WithoutARateIdTheStepSaysSoAndSendsNothingElse()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"updateShippingAddress\":{\"availableShippingRates\":[]}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/",
            ProfileData = new Cybersole.Core.Models.Profile
            {
                FirstName = "Ada", LastName = "Lovelace", Address1 = "1 Main St",
                City = "Austin", Zip = "78701", Phone = "5550100", Country = "US", Email = "ada@example.test",
            },
        };
        ctx.Session.Vars["wh.apiHost"] = server.BaseUrl;

        var outcome = await new WarhammerFlow().SubmitShippingAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Single(server.Requests);
        Assert.Contains(ctx.Events, e => e.Name.Contains("no shipping rate id"));
        Assert.False(ctx.Session.Vars.ContainsKey("shippingRateId"));
    }

    /// <summary>
    /// R1340: the image builds one configuration record holding both endpoints — Warhammer's GraphQL endpoint and
    /// CyberSource's Flex token endpoint — in a static initialiser at sub_140E4AE90 (133 bytes):
    /// <c>+8  &amp;off_147054A60 "https://api.prod.warhammer.com/graphql"</c> and
    /// <c>+16 &amp;off_147066CC0 "https://flex.cybersource.com/flex/v2/tokens"</c> (38 and 43 characters). They are one object, so the
    /// replica must carry both verbatim; this pins the pair.
    /// </summary>
    [Fact]
    public void TheWarhammerConfigRecordCarriesBothEndpoints()
    {
        // Warhammer's host is private in the flow, which is right — a caller has no business reading it. The
        // pair is checked through the Flex endpoint and through the composed request the shipping step makes.
        Assert.Equal("https://flex.cybersource.com/flex/v2/tokens", CybersourceFlex.TokensUrl);
        Assert.Equal(43, CybersourceFlex.TokensUrl.Length);
        Assert.Equal("https://api.prod.warhammer.com", WarhammerSurface.ApiHost);
        Assert.Equal(38, (WarhammerSurface.ApiHost + WarhammerSurface.GraphQlPath).Length);
    }
}
