using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1304: the Komoju offsite card surface, decoded from <c>0x140D994D0</c>.
///
/// <para>
/// The assertions carry the frozen values rather than the shape, because the values are the decode: the
/// browser block is six constants that never vary by machine (1707×1067 landscape, TZ -60, 24-bit,
/// en-US, Java off), and the two URLs are single literals the machine concatenates onto.
/// </para>
/// </summary>
public sealed class KomojuGatewayTests
{
    [Fact]
    public void TheBrowserBlockIsTheImagesSixConstants()
    {
        var info = KomojuGateway.BrowserInfo();

        Assert.Equal(6, info.Count);
        Assert.Equal("-60", info["browserTZ"]);
        Assert.Equal("1707", info["browserScreenWidth"]);
        Assert.Equal("1067", info["browserScreenHeight"]);
        Assert.Equal("24", info["browserColorDepth"]);
        Assert.Equal("en-US", info["browserLanguage"]);
        Assert.Equal("false", info["browserJavaEnabled"]);
    }

    [Fact]
    public void TheAuthBodyNestsTheBrowserBlockAndKeepsUuidEmpty()
    {
        var body = KomojuGateway.AuthBody("tok_1");

        Assert.Equal("tok_1", body["token"]?.ToString());

        // uuid is the empty-string object in the image, not an omitted key.
        Assert.NotNull(body["uuid"]);
        Assert.Equal(string.Empty, body["uuid"]!.ToString());

        var nested = (Newtonsoft.Json.Linq.JObject)body["browser_info"]!;
        Assert.Equal("1707", nested["browserScreenWidth"]?.ToString());
        Assert.Equal("-60", nested["browserTZ"]?.ToString());
    }

    [Fact]
    public void TheTwoUrlsAreTheFrozenLiterals()
    {
        Assert.Equal("https://komoju.com/gpayments_offsite/auth", KomojuGateway.AuthUrl);
        Assert.Equal("https://degica.as1.gpayments.net/api/v2/brw/info/result?transId=",
            KomojuGateway.BrowserInfoResultPrefix);

        // The id is concatenated straight onto the '=', not passed as a query parameter.
        Assert.Equal("https://degica.as1.gpayments.net/api/v2/brw/info/result?transId=abc123",
            KomojuGateway.BrowserInfoResultUrl("abc123"));
    }

    [Fact]
    public async Task AuthorisingPostsTheBodyToTheOffsiteEndpointAndKeepsTheTransId()
    {
        string? seenPath = null;
        string? seenBody = null;
        using var server = new TinyServer((req, body) =>
        {
            seenPath = req.Url?.PathAndQuery;
            seenBody = body;
            return (200, "{\"transId\":\"tr_9\",\"redirectUrl\":\"https://issuer.test/challenge\"}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/checkout" };
        ctx.Session.Vars["komoju.token"] = "tok_9";

        // The gateway's host is frozen, so the request is aimed at the test server through the same
        // session seam every other gateway in the file uses — never at the real komoju.com.
        ctx.Session.Vars["komoju.authUrl"] = server.BaseUrl + "/gpayments_offsite/auth";

        var result = await new KomojuGateway().AuthorizeAsync(ctx, default);

        Assert.True(result.RequiresAction || result.Ok, result.Error);
        Assert.Equal("/gpayments_offsite/auth", seenPath);
        Assert.Contains("\"browser_info\"", seenBody);
        Assert.Contains("\"uuid\":\"\"", seenBody);
        Assert.Contains("\"token\":\"tok_9\"", seenBody);
        Assert.Equal("tr_9", ctx.Session.Vars["komoju.transId"]);
    }

    [Fact]
    public async Task WithoutATokenItRefusesRatherThanPostingAnEmptyOne()
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = "https://komoju.com/checkout" };

        var result = await new KomojuGateway().AuthorizeAsync(ctx, default);

        Assert.False(result.Ok);
        Assert.Contains("no token", result.Error);
    }

    [Fact]
    public async Task TheBrowserInfoResultNeedsTheTransIdTheAuthorisationStored()
    {
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = "https://komoju.com/checkout" };

        var result = await new KomojuGateway().CompleteActionAsync(ctx, "{}", default);

        Assert.False(result.Ok);
        Assert.Contains("no transId", result.Error);
    }

    [Fact]
    public async Task DirectFormUrlTokenizationPostsCardAndExtractsSecureToken()
    {
        using var server = new TinyServer((req, _) =>
        {
            if (req.Url?.AbsolutePath == "/sessions/pay" && req.HttpMethod == "GET")
                return (200, "<html><head><meta name=\"csrf-token\" content=\"komoju-csrf-1\"/></head></html>");
            if (req.Url?.AbsolutePath == "/sessions/pay" && req.HttpMethod == "POST")
                return (200, "{\"status\":\"confirming\",\"secureToken\":{\"authentication_url\":\"https://komoju.com/3ds/auth?token=tok_direct_1&foo=bar\"}}");
            return (404, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl,
            ProfileData = new Profile { Email = "buyer@komoju.test", FirstName = "Hanako", LastName = "Sato" },
            Card = new Card { Number = "4242 4242 4242 4242", Month = "4", Year = "2029", Cvv = "999", Name = "Hanako Sato" },
        };
        ctx.Session.Vars["komoju.formUrl"] = server.BaseUrl + "/sessions/pay";

        var result = await new KomojuGateway().TokenizeAsync(ctx, default);
        Assert.True(result.RequiresAction, result.Error);
        Assert.Equal("https://komoju.com/3ds/auth?token=tok_direct_1&foo=bar", result.ThreeDsUrl);
        Assert.Equal("tok_direct_1", result.ThreeDsPayload);
        Assert.Equal("tok_direct_1", ctx.Session.Vars["komoju.token"]);
        Assert.Equal("tok_direct_1", ctx.Session.PaymentToken);

        Assert.Equal(2, server.Requests.Count);
        var postHeaders = server.RequestHeaders[1];
        Assert.Equal("*/*", postHeaders["Accept"]);
        Assert.Equal("https://komoju.com", postHeaders["Origin"]);
        Assert.Equal(server.BaseUrl + "/sessions/pay", postHeaders["Referer"]);

        var sent = JObject.Parse(server.Requests[1].Body);
        Assert.Equal("komoju-csrf-1", sent["authenticity_token"]?.ToString());
        Assert.Equal("credit_card", sent["payment_details"]?["type"]?.ToString());
        Assert.Equal("04", sent["payment_details"]?["month"]?.ToString());
        Assert.Equal("29", sent["payment_details"]?["year"]?.ToString());
        Assert.Equal("4242424242424242", sent["payment_details"]?["number"]?.ToString());
        Assert.Equal("999", sent["payment_details"]?["verification_value"]?.ToString());
        Assert.Equal("0", sent["payment_details"]?["persist"]?.ToString());
    }

    [Fact]
    public async Task PaymentPartnersExtractsIframe3dsSrcAndToken()
    {
        const string partnersHtml = """
            <html><body>
              <iframe id="iframe-3ds" src="https://komoju.com/payments_partners/challenge?token=tok_pp_42&amp;locale=ja"></iframe>
            </body></html>
            """;

        var extracted = KomojuGateway.ExtractPaymentPartnersIframeSrc(partnersHtml);
        Assert.Equal("https://komoju.com/payments_partners/challenge?token=tok_pp_42&locale=ja", extracted);

        using var server = new TinyServer((_, _) => (200, partnersHtml));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/payments_partners/authentications" };
        ctx.Session.Vars["komoju.isPaymentPartners"] = "true";

        var result = await new KomojuGateway().TokenizeAsync(ctx, default);
        Assert.True(result.RequiresAction, result.Error);
        Assert.Equal("https://komoju.com/payments_partners/challenge?token=tok_pp_42&locale=ja", result.ThreeDsUrl);
        Assert.Equal("tok_pp_42", result.ThreeDsPayload);
        Assert.Equal("tok_pp_42", ctx.Session.Vars["komoju.token"]);
    }
}
