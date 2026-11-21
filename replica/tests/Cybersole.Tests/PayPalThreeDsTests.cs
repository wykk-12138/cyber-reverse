using System.Linq;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// PayPal 3-D Secure, pinned to the decompiled surface — the request builders (sub_141102970 /
/// sub_141105A80), the send step (sub_14110D670: PUT to the frozen graphql literal 0x147097e78),
/// the persisted-operation bodies (R1085's case bodies: {"operationName": N, "variables": {...}}),
/// the contingency needles, and the machine's four states wired through the gateway (R1086).
/// </summary>
public sealed class PayPalThreeDsTests
{
    private static PayPalThreeDs.StageInput Sample(bool hosted = false) => new()
    {
        ChallengeActive = hosted,   // the normal sample reports 'Solving', the hosted one 'Proccesing'
        Hosted = hosted,
        Euat = "euat-7",
        MetadataId = "meta-7",
        Country = "US",
        HostedAppName = "ctx-app",
        HostedReferer = "https://www.paypal.com/checkout",
        UserAgent = "UA/1",
        SecChUa = @"""Ch"";v=""1""",
        SecChUaPlatform = @"""Windows""",
        Token = "tok-9",
        Amount = 150m,
    };

    private static FlowContext Context(NetClient http) => new()
    {
        Http = http,
        Url = "https://www.paypal.com/checkout",
    };

    /// <summary>The normal dialect's wall, exactly as sub_141102970 assembles it.</summary>
    [Fact]
    public void TheNormalWallMatchesTheDecompiledContract()
    {
        var h = PayPalThreeDs.NormalHeaders(Sample());

        Assert.Equal(16, h.Count);
        Assert.Equal("euat-7", h["x-paypal-internal-euat"]);
        Assert.Equal("meta-7", h["paypal-client-metadata-id"]);
        Assert.Equal("?0", h["sec-ch-ua-mobile"]);
        Assert.Equal(PayPalThreeDs.AppName, h["x-app-name"]);
        Assert.Equal("application/json", h["content-type"]);
        Assert.Equal("*/*", h["accept"]);
        Assert.Equal("https://www.paypal.com", h["origin"]);
        Assert.Equal("https://www.paypal.com", h["referer"]);
        Assert.Equal("same-origin", h["sec-fetch-site"]);
        Assert.Equal("cors", h["sec-fetch-mode"]);
        Assert.Equal("empty", h["sec-fetch-dest"]);
        Assert.Equal("gzip, deflate", h["Accept-Encoding"]);
        Assert.Equal("en-GB", h["Accept-Language"]);
        Assert.Equal("UA/1", h["user-agent"]);

        Assert.False(h.ContainsKey("x-requested-with"));
        Assert.False(h.ContainsKey("x-locale"));
        Assert.False(h.ContainsKey("priority"));
        Assert.False(h.ContainsKey("x-country"));
    }

    /// <summary>The hosted dialect's wall (sub_141105A80) — its own headers, casing and context fields.</summary>
    [Fact]
    public void TheHostedDialectCarriesItsOwnHeadersAndCasing()
    {
        var h = PayPalThreeDs.HostedHeaders(Sample(hosted: true));

        Assert.Equal(17, h.Count);
        Assert.Equal("fetch", h["x-requested-with"]);
        Assert.Equal("en_US", h["x-locale"]);
        Assert.Equal("meta-7", h["paypal-client-context"]);
        Assert.Equal("ctx-app", h["x-app-name"]);
        Assert.Equal("US", h["x-country"]);
        Assert.Equal("https://www.paypal.com/checkout", h["referer"]);
        Assert.Equal("gzip, deflate, br, zstd", h["accept-encoding"]);
        Assert.Equal("en-US,en;q=0.9", h["accept-language"]);
        Assert.Equal("u=1, i", h["priority"]);

        Assert.False(h.ContainsKey("sec-fetch-site"));
        Assert.False(h.ContainsKey("sec-fetch-mode"));
        Assert.False(h.ContainsKey("sec-fetch-dest"));
    }

    /// <summary>The stage texts, including the image's own spelling of "Proccesing".</summary>
    [Fact]
    public void TheStatusTextsKeepTheImageSpelling()
    {
        // R1081: the stage-1 literal carries its "(1)" suffix — an earlier pin trusted the doc's
        // shorthand over the pool listing and pinned the suffix away.
        Assert.Equal("Solving PayPal 3DS (1)", PayPalThreeDs.SolvingStatus);
        Assert.Equal("Proccesing 3D Secure", PayPalThreeDs.ProcessingStatus);   // the typo is the image's
        Assert.Equal(PayPalThreeDs.SolvingStatus, PayPalThreeDs.StatusText(challengeActive: false));
        Assert.Equal(PayPalThreeDs.ProcessingStatus, PayPalThreeDs.StatusText(challengeActive: true));
    }

    /// <summary>The nine decoded stage labels, each matching its pool address; the map is closed.</summary>
    [Fact]
    public void TheDecodedStagesCarryTheirOwnLabels()
    {
        Assert.Equal(9, PayPalThreeDs.StageLabels.Count);
        Assert.Equal("Solving PayPal 3DS (1)", PayPalThreeDs.StageLabels["1"]);
        Assert.Equal("Solving PayPal 3DS (8)", PayPalThreeDs.StageLabels["8"]);
        Assert.True(PayPalThreeDs.StageIsDecoded("8"));
        Assert.False(PayPalThreeDs.StageIsDecoded("9"));   // there is no stage nine — the map is closed
    }

    /// <summary>The frozen literals: target, app name, budget, window, and the four machine states.</summary>
    [Fact]
    public void TheStageConstantsMatchTheFrozenLiterals()
    {
        Assert.Equal("https://www.paypal.com/graphql/", PayPalThreeDs.GraphqlUrl);
        Assert.Equal("checkoutuinodeweb_hermione", PayPalThreeDs.AppName);
        Assert.Equal(30000, PayPalThreeDs.StageTimeoutMs);
        Assert.Equal("https://www.paypal.com/checkoutweb/processThreedsConfirmation",
            PayPalThreeDs.ChallengeWindowUrl);
        Assert.Equal((500, 600), (PayPalThreeDs.ChallengeWindowWidth, PayPalThreeDs.ChallengeWindowHeight));
        Assert.Equal("JWT", PayPalThreeDs.JwtFormField);
        Assert.Equal("MD", PayPalThreeDs.MdFormField);
        Assert.Equal("GetThreeDsJwtQuery", PayPalThreeDs.JwtQueryOperation);
        Assert.Equal("ThreeDsAuthenticateMutation", PayPalThreeDs.AuthenticateOperation);
        Assert.Equal("ThreeDsLookUpMutation", PayPalThreeDs.LookUpOperation);
        Assert.Equal("ResolveThreeDsContingency", PayPalThreeDs.ResolveOperation);
        Assert.Equal(new[] { "Submit3DS", "Process3DS", "Waiting3DS", "Complete3DS" },
            System.Enum.GetNames<PayPalThreeDs.ThreeDsState>());
    }

    /// <summary>
    /// The dispatch the builders register: 200 reaches the success continuation, 403 and 429 share
    /// the retry closure — and every request is a PUT carrying a persisted-operation body.
    /// </summary>
    [Theory]
    [InlineData(200, true, false)]
    [InlineData(403, false, true)]
    [InlineData(429, false, true)]
    [InlineData(500, false, false)]
    public async Task TheStatusDispatchMirrorsTheRegisteredHandlers(int status, bool ok, bool retry)
    {
        var seen = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add(req.Url?.PathAndQuery ?? "");
            return (status, status == 200 ? "{\"done\":true}" : "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);

        var outcome = await PayPalThreeDs.SubmitAsync(ctx, Sample(), default, server.BaseUrl + "/graphql/");

        Assert.Equal(status, outcome.Status);
        Assert.Equal(ok, outcome.Ok);
        Assert.Equal(retry, outcome.Retryable);
        if (ok) Assert.Equal("{\"done\":true}", outcome.Body);

        // The white StatusInfo wall went out with the stage text before the request.
        Assert.Contains(ctx.Events, e => e.Name == PayPalThreeDs.SolvingStatus && e.Type == "StatusInfo");

        // The request is the PUT the send step performs, and R1095 corrected its shape: PayPal
        // puts the operation name in the URL query string and the full document in the body.
        var req = server.Requests.Single();
        Assert.Equal("PUT", req.Method);
        Assert.EndsWith("/graphql?GetThreeDsJwtQuery", seen.Single());
        var body = JObject.Parse(req.Body);
        Assert.Equal("tok-9", (string?)body["variables"]!["token"]);
        Assert.Equal("150.00", (string?)body["variables"]!["amount"]);   // the {0:0.00} format
        Assert.StartsWith("query GetThreeDsJwtQuery(", (string?)body["query"]);
        Assert.Null(body["operationName"]);                              // NOT the Stripe envelope
    }

    /// <summary>
    /// R1095: the four graphql documents are the frozen literals, verbatim — the payload layer
    /// the machine sends. Each operation maps to its own document, and each document declares
    /// the variables the resolver chain binds.
    /// </summary>
    [Fact]
    public void TheFourDocumentsAreTheFrozenLiterals()
    {
        Assert.StartsWith("query GetThreeDsJwtQuery(", PayPalThreeDs.JwtQueryDocument);
        Assert.Contains("$jwtIssuer: String!", PayPalThreeDs.JwtQueryDocument);
        Assert.Contains("$jwtOrgUnitId: String!", PayPalThreeDs.JwtQueryDocument);
        Assert.Contains("threeDSJwt(", PayPalThreeDs.JwtQueryDocument);

        Assert.StartsWith("mutation ThreeDsAuthenticateMutation($token: String, $amount: AmountInput!",
            PayPalThreeDs.AuthenticateDocument);
        Assert.Contains("threeDSAuthenticate(", PayPalThreeDs.AuthenticateDocument);
        Assert.Contains("liabilityShift", PayPalThreeDs.AuthenticateDocument);

        Assert.StartsWith("mutation ThreeDsLookUpMutation($token: String!", PayPalThreeDs.LookUpDocument);
        Assert.Contains("threeDSLookUp(", PayPalThreeDs.LookUpDocument);
        Assert.Contains("acsURL", PayPalThreeDs.LookUpDocument);

        Assert.StartsWith("mutation ResolveThreeDsContingency($token: String!, $authId: String!",
            PayPalThreeDs.ResolveDocument);
        Assert.Contains("resolveThreeDsContingency(", PayPalThreeDs.ResolveDocument);
        Assert.Contains("fragment ThreeDomainSecureFields", PayPalThreeDs.ResolveDocument);

        // Each operation name maps to its own document, and the resolver is the long one.
        Assert.Equal(PayPalThreeDs.JwtQueryDocument, PayPalThreeDs.DocumentFor(PayPalThreeDs.JwtQueryOperation));
        Assert.Equal(PayPalThreeDs.AuthenticateDocument,
            PayPalThreeDs.DocumentFor(PayPalThreeDs.AuthenticateOperation));
        Assert.Equal(PayPalThreeDs.LookUpDocument, PayPalThreeDs.DocumentFor(PayPalThreeDs.LookUpOperation));
        Assert.Equal(PayPalThreeDs.ResolveDocument, PayPalThreeDs.DocumentFor(PayPalThreeDs.ResolveOperation));
        Assert.True(PayPalThreeDs.ResolveDocument.Length > 10000);   // 10,370 chars of fragments
        Assert.Equal(string.Empty, PayPalThreeDs.DocumentFor("NotAnOperation"));
    }

    /// <summary>The REST hop beside graphql is the frozen literal.</summary>
    [Fact]
    public void TheNotifyMethodCompleteEndpointIsTheFrozenLiteral()
    {
        Assert.Equal("https://www.paypal.com/payment-authentication/threeds/v1/notify-method-cmpl",
            PayPalThreeDs.NotifyMethodCompleteUrl);
    }

    /// <summary>
    /// R1096: the device-data pair — the JWT form POSTed to the answer's own
    /// deviceDataCollectionUrl.href (or init-method when absent), then notify-method-cmpl with
    /// threeDSMethodData carrying the base64 of {"threeDSServerTransID": …}.
    /// </summary>
    [Fact]
    public async Task TheDeviceDataPairSubmitsTheJwtThenNotifiesTheMethod()
    {
        var seen = new System.Collections.Generic.List<string>();
        var bodies = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seen.Add(req.Url?.PathAndQuery ?? "");
            bodies.Add(body);
            return (200, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["paypal3ds.initMethodUrl"] = server.BaseUrl + "/v1/init-method";
        ctx.Session.Vars["paypal3ds.notifyUrl"] = server.BaseUrl + "/v1/notify-method-cmpl";

        const string jwtBody = @"{""jwt"":""eyJhbGciOi.payload.sig"",
            ""deviceDataCollectionUrl"":{""href"":""https://paypal.example/ddc""},
            ""threeDSServerTransID"":""txn-42""}";

        var outcome = await new PayPalThreeDs().SubmitDeviceDataAsync(ctx, Sample(), jwtBody, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal(2, seen.Count);
        Assert.Equal("/v1/init-method", seen[0]);                 // the seam fronts the collection hop
        Assert.Equal("/v1/notify-method-cmpl", seen[1]);
        Assert.Contains("JWT=eyJhbGciOi.payload.sig", bodies[0]);  // the decoded form field

        // threeDSMethodData is the base64 of {"threeDSServerTransID":"txn-42"}.
        var expected = System.Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(
            "{\"threeDSServerTransID\":\"txn-42\"}"));
        Assert.Contains("threeDSMethodData=" + System.Uri.EscapeDataString(expected), bodies[1]);
        Assert.Equal(expected, ctx.Session.Vars["paypal3ds.threeDSMethodData"]);
    }

    /// <summary>Without a JWT in the answer the machine is not alive and the pair is skipped.</summary>
    [Fact]
    public async Task TheDeviceDataPairIsSkippedWithoutAJwt()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);

        var outcome = await new PayPalThreeDs().SubmitDeviceDataAsync(ctx, Sample(),
            "{\"data\":{}}", default);

        Assert.True(outcome.Ok);
        Assert.Empty(server.Requests);   // the alive gate kept it off the wire
    }

    /// <summary>
    /// R1097: PayPal has TWO 3DS dialects. The normal path is the heliosnext family — its four
    /// endpoints are their own frozen literals, sharing only the method pair with the hosted path.
    /// </summary>
    [Fact]
    public void TheNormalPathIsItsOwnDialect()
    {
        Assert.Equal("https://www.paypal.com/heliosnext/threeDS?action=verify&flow=3ds&cart_id=",
            PayPalThreeDs.HeliosEntryUrl);
        Assert.Equal("https://www.paypal.com/heliosnext/api/serverData", PayPalThreeDs.HeliosServerDataUrl);
        Assert.Equal("https://www.paypal.com/heliosnext/api/session", PayPalThreeDs.HeliosSessionUrl);
        Assert.Equal("https://www.paypal.com/heliosnext/api/processThreedsConfirmation",
            PayPalThreeDs.HeliosProcessThreedsConfirmationUrl);
        Assert.Equal("https://www.paypal.com/payment-authentication/threeds/v1/init-challenge",
            PayPalThreeDs.InitChallengeUrl);

        // The shared surface is only the method pair — everything else differs by dialect.
        Assert.Equal("https://www.paypal.com/payment-authentication/threeds/v1/init-method",
            PayPalThreeDs.InitMethodUrl);
        Assert.Equal("https://www.paypal.com/payment-authentication/threeds/v1/notify-method-cmpl",
            PayPalThreeDs.NotifyMethodCompleteUrl);

        // The normal path's own failure report, verbatim.
        Assert.Equal("Payment failed (3DS)", PayPalThreeDs.NormalPathFailureStatus);
        Assert.Equal("#FB4961", PayPalThreeDs.NormalPathFailureColour);   // the image's colour literal
    }

    /// <summary>The normal path's bootstrap: serverData then session, both JSON, token + action.</summary>
    [Fact]
    public async Task TheNormalBootstrapRunsServerDataThenSession()
    {
        var seen = new System.Collections.Generic.List<string>();
        var bodies = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seen.Add(req.Url?.AbsolutePath ?? "");
            bodies.Add(body);
            return (200, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["paypal3ds.heliosServerDataUrl"] = server.BaseUrl + "/heliosnext/api/serverData";
        ctx.Session.Vars["paypal3ds.heliosSessionUrl"] = server.BaseUrl + "/heliosnext/api/session";

        var outcome = await new PayPalThreeDs().SubmitNormalBootstrapAsync(ctx, Sample(),
            "cart-9", default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal(2, seen.Count);
        Assert.Equal("/heliosnext/api/serverData", seen[0]);   // server-data first
        Assert.Equal("/heliosnext/api/session", seen[1]);      // then the session hop

        // R1098 correction: both hops are JSON — {"token": …} then {"token": …, "action": "verify"}.
        var first = Newtonsoft.Json.Linq.JObject.Parse(bodies[0]);
        Assert.Equal("cart-9", (string?)first["token"]);
        Assert.Null(first["action"]);

        var second = Newtonsoft.Json.Linq.JObject.Parse(bodies[1]);
        Assert.Equal("cart-9", (string?)second["token"]);
        Assert.Equal("verify", (string?)second["action"]);

        Assert.True(ctx.Session.Vars.ContainsKey("paypal3ds.helios.serverData"));
        Assert.True(ctx.Session.Vars.ContainsKey("paypal3ds.helios.session"));
    }

    /// <summary>
    /// The entry URL the machine composes before the first hop: frozen prefix + cart id +
    /// the go_to segment, verbatim.
    /// </summary>
    [Fact]
    public void TheEntryUrlIsTheFrozenComposition()
    {
        var url = PayPalThreeDs.EntryUrlFor("cart-9");

        Assert.Equal(PayPalThreeDs.HeliosEntryUrl + "cart-9" + PayPalThreeDs.GoToNextSegment, url);
        Assert.Equal(
            "https://www.paypal.com/heliosnext/threeDS?action=verify&flow=3ds&cart_id=cart-9&go_to=next",
            url);
    }

    /// <summary>The confirmation hop PUTs to the frozen endpoint and reports its own failure.</summary>
    [Fact]
    public async Task TheProcessConfirmationHopRunsAgainstTheSeam()
    {
        var seen = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add(req.Url?.AbsolutePath ?? "");
            return (200, "{\"ok\":true}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["paypal3ds.processConfirmationUrl"] = server.BaseUrl + "/heliosnext/api/processThreedsConfirmation";

        var outcome = await new PayPalThreeDs().SubmitProcessConfirmationAsync(ctx, Sample(),
            "{\"liability_shift\":\"Y\"}", default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("/heliosnext/api/processThreedsConfirmation", seen.Single());
        Assert.Equal("{\"ok\":true}", ctx.Session.Vars["paypal3ds.processConfirmation"]);
    }

    /// <summary>
    /// R1102 correction: the challenge hop sends ONLY the JWT, and READS the callback URL out of
    /// the answer's payload (0x14710e630 → 0x146fc54d8). R1101 had put that string in the form;
    /// the disassembly at 0x140d8e6e7/0x140d8e6ff shows it is an answer-side read.
    /// </summary>
    [Fact]
    public async Task TheChallengeInitSendsOnlyTheJwtAndReadsTheCallback()
    {
        var bodies = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((_, body) =>
        {
            bodies.Add(body);
            return (200, "{\"payload\":{\"challenge_callback_url\":\"https://bank.example/cb\"}}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["paypal3ds.initChallengeUrl"] = server.BaseUrl + "/v1/init-challenge";

        var outcome = await new PayPalThreeDs().SubmitChallengeInitAsync(ctx, Sample(),
            "{\"jwt\":\"eyJ.jwt.sig\"}", default);

        Assert.True(outcome.Ok, outcome.Error);
        var body = bodies.Single();
        Assert.Contains("JWT=eyJ.jwt.sig", body);
        Assert.DoesNotContain("challenge_callback_url", body);          // NOT a request field

        // It was read out of the payload and kept on the session.
        Assert.Equal("https://bank.example/cb", ctx.Session.Vars["paypal3ds.challengeCallbackUrl"]);

        // The fragment the machine appends to its final GET, verbatim (47 chars).
        Assert.Equal("state=undefined&code=undefined&liability_shift=",
            PayPalThreeDs.ChallengeCallbackFragment);
        Assert.Equal("https://x/cb?&" + PayPalThreeDs.ChallengeCallbackFragment,
            PayPalThreeDs.ChallengeCallbackUrlFor("https://x/cb?"));

        // R1103: the separator is '?'-aware — '&' when the base already asks, '?' when it does not.
        // The image tests "contains '?'" (sub_141cfa770(base, 63)), not "ends with", so a base
        // that already ends in '?' yields the literal "?&" join — recorded here as the machine's
        // own behaviour rather than tidied away.
        // R1149: the fragment is verbatim, so state/code stay "undefined" as frozen.
        Assert.Equal("https://x/cb?" + PayPalThreeDs.ChallengeCallbackFragment,
            PayPalThreeDs.ChallengeCallbackUrlFor("https://x/cb"));
        Assert.Equal("https://x/cb?a=1&" + PayPalThreeDs.ChallengeCallbackFragment,
            PayPalThreeDs.ChallengeCallbackUrlFor("https://x/cb?a=1"));

    }

    /// <summary>
    /// R1100: the dialect choice is explicit, and each branch walks its own surface. The image
    /// has no field-based branch in a shared function — it has two implementation types with
    /// parallel method tables — so the selector is the API-level expression of that choice.
    /// </summary>
    [Fact]
    public async Task TheDialectSelectorWalksTheChosenSurface()
    {
        static TinyServer Server(out System.Collections.Generic.List<string> seen)
        {
            var log = new System.Collections.Generic.List<string>();
            seen = log;
            return new TinyServer((req, _) =>
            {
                log.Add(req.Url?.AbsolutePath ?? "");
                return (200, "{\"data\":{\"paymentContingencies\":{}}}");
            });
        }

        // Normal branch → the heliosnext surface.
        using (var server = Server(out var normalSeen))
        {
            using var http = new NetClient { Transport = TransportMode.SChannel };
            var ctx = Context(http);
            ctx.Session.Vars["paypal3ds.heliosServerDataUrl"] = server.BaseUrl + "/heliosnext/api/serverData";
            ctx.Session.Vars["paypal3ds.heliosSessionUrl"] = server.BaseUrl + "/heliosnext/api/session";

            var outcome = await new PayPalThreeDs().RunDialectAsync(ctx, Sample(),
                PayPalThreeDs.ThreeDsDialect.Normal, default, server.BaseUrl + "/graphql", "cart-9");

            Assert.True(outcome.Ok, outcome.Error);   // no challenge asked → completes
            Assert.Contains("/heliosnext/api/serverData", normalSeen[0]);
            Assert.DoesNotContain(normalSeen, u => u.Contains("checkoutweb"));
        }

        // Hosted branch → the payment-authentication surface, no heliosnext hop.
        using (var server = Server(out var hostedSeen))
        {
            using var http = new NetClient { Transport = TransportMode.SChannel };
            var ctx = Context(http);

            var outcome = await new PayPalThreeDs().RunDialectAsync(ctx, Sample(hosted: true),
                PayPalThreeDs.ThreeDsDialect.Hosted, default, server.BaseUrl + "/graphql");

            Assert.True(outcome.Ok, outcome.Error);
            Assert.DoesNotContain(hostedSeen, u => u.Contains("heliosnext"));
            Assert.NotEmpty(hostedSeen);
        }
    }

    /// <summary>
    /// R1099, strengthened in R1105: the normal dialect end to end, with the method pair and the
    /// challenge initialisation actually going out on the wire. The first cut left the JWT answer
    /// without a <c>jwt</c>, so the alive gate skipped those hops and the R1099 mutation came back
    /// DECORATIVE — the pin could not see the code it was meant to nail.
    /// </summary>
    [Fact]
    public async Task TheNormalDialectRunsEndToEndAndStopsAtTheWindow()
    {
        var seen = new System.Collections.Generic.List<string>();
        var bodies = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, body) =>
        {
            seen.Add(req.Url?.AbsolutePath ?? "");
            bodies.Add(body);
            if ((req.Url?.AbsolutePath ?? "").Contains("graphql"))
                return (200, @"{""jwt"":""eyJ.normal.sig"",""threeDSServerTransID"":""txn-9"",
                    ""data"":{""paymentContingencies"":{
                    ""threeDomainSecure"":{""status"":""CHALLENGE_REQUIRED"",
                        ""redirectUrl"":{""href"":""https://bank.example/challenge""}},
                    ""threeDSContingencyData"":{""resolution"":{
                        ""paymentCard"":{""id"":""card-77""},
                        ""contingencyContext"":{
                            ""jwtSpecification"":{""jwtIssuer"":""iss-1"",""jwtOrgUnitId"":""org-2""},
                            ""referenceId"":""ref-9""}}}}}}");
            return (200, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["paypal3ds.heliosServerDataUrl"] = server.BaseUrl + "/heliosnext/api/serverData";
        ctx.Session.Vars["paypal3ds.heliosSessionUrl"] = server.BaseUrl + "/heliosnext/api/session";
        ctx.Session.Vars["paypal3ds.initMethodUrl"] = server.BaseUrl + "/v1/init-method";
        ctx.Session.Vars["paypal3ds.notifyUrl"] = server.BaseUrl + "/v1/notify-method-cmpl";
        ctx.Session.Vars["paypal3ds.initChallengeUrl"] = server.BaseUrl + "/v1/init-challenge";

        var outcome = await new PayPalThreeDs().RunNormalAsync(ctx, Sample(), "cart-9", default,
            server.BaseUrl + "/graphql");

        // It stopped at the window, not completed — the same contract as the hosted path.
        Assert.True(outcome.AwaitingChallenge, outcome.Error);
        Assert.Equal(nameof(PayPalThreeDs.ThreeDsState.Waiting3DS), ctx.Session.Vars["paypal3ds.state"]);

        // The normal solver's own order, all seven hops: bootstrap, submit, JWT query, then the
        // method pair and the challenge initialisation.
        Assert.Equal(7, seen.Count);
        Assert.Equal("/heliosnext/api/serverData", seen[0]);
        Assert.Equal("/heliosnext/api/session", seen[1]);
        Assert.Contains("/graphql", seen[2]);
        Assert.Contains("/graphql", seen[3]);
        Assert.Equal("/v1/init-method", seen[4]);            // the JWT form hop
        Assert.Equal("/v1/notify-method-cmpl", seen[5]);     // the threeDSMethodData hop
        Assert.Equal("/v1/init-challenge", seen[6]);         // the normal path's own hop

        Assert.Contains("JWT=eyJ.normal.sig", bodies[4]);
        Assert.Contains("threeDSMethodData=", bodies[5]);
        Assert.Contains("JWT=eyJ.normal.sig", bodies[6]);
        Assert.Equal("0", ctx.Session.Vars["paypal3ds.hosted"]);   // the normal dialect's flag
    }

    /// <summary>
    /// The challenge-init hop (normal path only) posts the JWT and, on refusal, speaks the
    /// normal dialect's own failure line in its own colour.
    /// </summary>
    [Fact]
    public async Task TheChallengeInitPostsTheJwtAndReportsItsOwnFailure()
    {
        var bodies = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((_, body) =>
        {
            bodies.Add(body);
            return (403, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);
        ctx.Session.Vars["paypal3ds.initChallengeUrl"] = server.BaseUrl + "/v1/init-challenge";

        var outcome = await new PayPalThreeDs().SubmitChallengeInitAsync(ctx, Sample(),
            "{\"jwt\":\"eyJ.jwt.sig\"}", default);

        Assert.False(outcome.Ok);
        Assert.Contains("JWT=eyJ.jwt.sig", bodies.Single());
        Assert.Contains(ctx.Events, e => e.Name == PayPalThreeDs.NormalPathFailureStatus
                                         && e.Type == PayPalThreeDs.NormalPathFailureColour);
    }

    /// <summary>
    /// The contingency read pulls the case bodies' needles out of the response — the bank's
    /// redirect, the JWT spec, and the referenceId/card the resolver variables carry.
    /// </summary>
    [Fact]
    public void TheContingencyReadPullsTheCaseBodiesNeedles()
    {
        const string body = @"{""data"":{""paymentContingencies"":{
            ""threeDomainSecure"":{
                ""status"":""CHALLENGE_REQUIRED"",
                ""redirectUrl"":{""href"":""https://bank.example/challenge""},
                ""method"":""GET"",
                ""parameter"":""p-1""},
            ""threeDSContingencyData"":{
                ""resolution"":{
                    ""paymentCard"":{""id"":""card-77""},
                    ""contingencyContext"":{
                        ""jwtSpecification"":{""jwtIssuer"":""iss-1"",""jwtOrgUnitId"":""org-2""},
                        ""referenceId"":""ref-9""}}}}}}";

        var snap = PayPalThreeDs.ReadContingency(body);

        Assert.True(snap.RequiresChallenge);
        Assert.Equal("CHALLENGE_REQUIRED", snap.Status);
        Assert.Equal("https://bank.example/challenge", snap.RedirectUrl);
        Assert.Equal("GET", snap.Method);
        Assert.Equal("p-1", snap.Parameter);
        Assert.Equal("iss-1", snap.JwtIssuer);
        Assert.Equal("org-2", snap.JwtOrgUnitId);
        Assert.Equal("ref-9", snap.ReferenceId);
        Assert.Equal("card-77", snap.CreditCardId);

        // No challenge asked for: the machine is done, not waiting.
        var calm = PayPalThreeDs.ReadContingency("{\"data\":{\"paymentContingencies\":{}}}");
        Assert.False(calm.RequiresChallenge);
    }

    /// <summary>
    /// The machine, scenario one: a response that asks for no challenge completes on the spot.
    /// </summary>
    [Fact]
    public async Task AMachineWithNoChallengeCompletes()
    {
        using var server = new TinyServer((_, _) => (200, "{\"data\":{\"paymentContingencies\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);

        var outcome = await new PayPalThreeDs().RunAsync(ctx, Sample(), default, server.BaseUrl + "/graphql/");

        Assert.True(outcome.Ok);
        Assert.False(outcome.AwaitingChallenge);
        Assert.Equal(nameof(PayPalThreeDs.ThreeDsState.Complete3DS), ctx.Session.Vars["paypal3ds.state"]);
        // Submit only — no JWT query when there is nothing to challenge.
        Assert.Single(server.Requests);
    }

    /// <summary>
    /// The machine, scenario two: a challenge response runs the JWT query, then hands the window
    /// to the host — a real Waiting3DS stop with the snapshot and the window's decoded constants.
    /// </summary>
    [Fact]
    public async Task AMachineWithAChallengeStopsAtTheWindow()
    {
        const string challenge = @"{""data"":{""paymentContingencies"":{
            ""threeDomainSecure"":{""status"":""CHALLENGE_REQUIRED"",
                ""redirectUrl"":{""href"":""https://bank.example/challenge""}},
            ""threeDSContingencyData"":{""resolution"":{
                ""paymentCard"":{""id"":""card-77""},
                ""contingencyContext"":{
                    ""jwtSpecification"":{""jwtIssuer"":""iss-1"",""jwtOrgUnitId"":""org-2""},
                    ""referenceId"":""ref-9""}}}}}}";
        var seen = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add(req.Url?.PathAndQuery ?? "");
            return (200, challenge);
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);

        var outcome = await new PayPalThreeDs().RunAsync(ctx, Sample(), default, server.BaseUrl + "/graphql/");

        Assert.False(outcome.Ok);                       // not done — waiting on the host-driven window
        Assert.True(outcome.AwaitingChallenge);
        Assert.NotNull(outcome.Contingency);
        Assert.Equal("https://bank.example/challenge", outcome.Contingency!.RedirectUrl);
        Assert.Equal("ref-9", outcome.Contingency.ReferenceId);
        Assert.Equal("card-77", outcome.Contingency.CreditCardId);

        Assert.Equal(nameof(PayPalThreeDs.ThreeDsState.Waiting3DS), ctx.Session.Vars["paypal3ds.state"]);
        Assert.Equal("ref-9", ctx.Session.Vars["paypal3ds.referenceId"]);
        Assert.Equal("card-77", ctx.Session.Vars["paypal3ds.creditCardId"]);
        Assert.Equal("tok-9", ctx.Session.Vars["paypal3ds.token"]);

        // Submit + the JWT query — the machine's own synchronous reach. R1095: the operation
        // name rides the URL query string; the body carries the frozen document instead.
        Assert.Equal(2, server.Requests.Count);
        Assert.EndsWith("/graphql?GetThreeDsJwtQuery", seen[1]);
        var jwtBody = JObject.Parse(server.Requests[1].Body);
        Assert.Null(jwtBody["operationName"]);
        Assert.Equal("iss-1", (string?)jwtBody["variables"]!["jwtIssuer"]);
        Assert.Equal("org-2", (string?)jwtBody["variables"]!["jwtOrgUnitId"]);
        Assert.Equal("ref-9", (string?)jwtBody["variables"]!["referenceId"]);
    }

    /// <summary>
    /// The machine's completion: after the window answered, authenticate, lookup, and resolve —
    /// the resolver's six variables in the last PUT, in the case bodies' own order.
    /// </summary>
    [Fact]
    public async Task TheContinuationRunsAuthenticateLookupResolveInOrder()
    {
        var seen = new System.Collections.Generic.List<string>();
        using var server = new TinyServer((req, _) =>
        {
            seen.Add(req.Url?.PathAndQuery ?? "");
            return (200, "{}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);

        var snapshot = new PayPalThreeDs.ContingencySnapshot
        {
            ReferenceId = "ref-9", CreditCardId = "card-77",
        };
        var outcome = await new PayPalThreeDs().ContinueAsync(ctx, Sample(), snapshot,
            "auth-1", "SUCCESS", default, server.BaseUrl + "/graphql/");

        Assert.True(outcome.Ok);
        Assert.Equal(nameof(PayPalThreeDs.ThreeDsState.Complete3DS), ctx.Session.Vars["paypal3ds.state"]);

        var names = seen.Select(u => u[(u.LastIndexOf('?') + 1)..]).ToArray();
        Assert.Equal(new[]
        {
            "ThreeDsAuthenticateMutation", "ThreeDsLookUpMutation", "ResolveThreeDsContingency",
        }, names);

        var resolve = JObject.Parse(server.Requests[2].Body)["variables"]!;
        Assert.Equal("tok-9", (string?)resolve["token"]);
        Assert.Equal("auth-1", (string?)resolve["authId"]);
        Assert.Equal("ref-9", (string?)resolve["referenceId"]);
        Assert.Equal("card-77", (string?)resolve["creditCardId"]);
        Assert.Equal("SUCCESS", (string?)resolve["status"]);
        Assert.Equal(new JArray("HERMES", "EXPRESS_CHECKOUT"), resolve["experiences"]);   // the decoded dialect set
    }

    /// <summary>
    /// The wiring (R1086): the gateway's action completion drives the resolver chain when the
    /// machine left a Waiting3DS state on the session — PayPalThreeDs is reachable from the
    /// payment dispatch, not just from these tests.
    /// </summary>
    [Fact]
    public async Task TheGatewayCompletionDrivesTheResolver()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = Context(http);

        ctx.Session.Vars["paypal3ds.state"] = nameof(PayPalThreeDs.ThreeDsState.Waiting3DS);
        ctx.Session.Vars["paypal3ds.referenceId"] = "ref-9";
        ctx.Session.Vars["paypal3ds.creditCardId"] = "card-77";
        ctx.Session.Vars["paypal3ds.euat"] = "euat-7";
        ctx.Session.Vars["paypal3ds.hosted"] = "0";
        ctx.Session.Vars["paypal3ds.token"] = "tok-9";
        ctx.Session.Vars["paypal3ds.graphqlUrl"] = server.BaseUrl + "/graphql/";

        var gateway = new PayPalGateway();
        var result = await gateway.CompleteActionAsync(ctx,
            "{\"authId\":\"auth-1\",\"status\":\"SUCCESS\"}", default);

        Assert.True(result.Ok, result.Error);
        Assert.Equal(3, server.Requests.Count);   // authenticate, lookup, resolve — the machine ran
        Assert.Equal(nameof(PayPalThreeDs.ThreeDsState.Complete3DS), ctx.Session.Vars["paypal3ds.state"]);
    }

    /// <summary>
    /// R1323: the image sends two variants of the resolve mutation from two different functions, both
    /// referenced once — so both paths are live and the replica has to be able to send either.
    /// <c>sub_141113680</c> (15615 bytes) sends the 10370-character document; <c>sub_14110FDB0</c> (14458
    /// bytes) sends the 10262-character one at 0x1470D7974, which is the same text minus one field block.
    /// </summary>
    [Fact]
    public void BothResolveVariantsAreTheStringsTheImageHolds()
    {
        Assert.Equal(10370, PayPalThreeDs.ResolveDocument.Length);
        Assert.Equal(10262, PayPalThreeDs.ResolveDocumentWithoutProviderFields.Length);
        Assert.True(PayPalThreeDs.ResolveDocument.Length - PayPalThreeDs.ResolveDocumentWithoutProviderFields.Length == 108);
    }

    /// <summary>
    /// The difference is one insertion, not a rewrite: the longer document is the shorter one with a block of
    /// provider and device-data fields added at offset 2890. Asserting the insertion point is what stops a
    /// future edit from "tidying" the two into one text with the fields moved somewhere else.
    /// </summary>
    [Fact]
    public void TheLongerVariantIsTheShorterOnePlusOneBlock()
    {
        var shortText = PayPalThreeDs.ResolveDocumentWithoutProviderFields;
        var longText = PayPalThreeDs.ResolveDocument;

        Assert.Equal(shortText[..2890], longText[..2890]);
        Assert.Equal(shortText[2890..], longText[2998..]);
        Assert.Contains("authenticationProvider", longText[2890..2998]);
        Assert.Contains("cardBrandProcessed", longText[2890..2998]);
        Assert.DoesNotContain("authenticationProvider", shortText);
    }

    [Fact]
    public void TheSelectorDefaultsToTheLongerVariantAndCanAskForTheShorter()
    {
        Assert.Equal(PayPalThreeDs.ResolveDocument, PayPalThreeDs.DocumentFor(PayPalThreeDs.ResolveOperation));
        Assert.Equal(PayPalThreeDs.ResolveDocument,
            PayPalThreeDs.DocumentFor(PayPalThreeDs.ResolveOperation, providerFields: true));
        Assert.Equal(PayPalThreeDs.ResolveDocumentWithoutProviderFields,
            PayPalThreeDs.DocumentFor(PayPalThreeDs.ResolveOperation, providerFields: false));

        // The flag only applies to the resolve operation; the other three are unaffected.
        Assert.Equal(PayPalThreeDs.LookUpDocument,
            PayPalThreeDs.DocumentFor(PayPalThreeDs.LookUpOperation, providerFields: false));
    }
}
