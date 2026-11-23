using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
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
/// R1001: the four payment hosts the coverage table listed as unmatched now have gateways, and each one's endpoint is the
/// literal the image carries rather than a guessed shape.
///
/// <para>
/// What these tests hold is narrower than "the payment works". Mollie, GMO, Touchtech and Midtrans each had exactly one
/// path captured, so one step per gateway calls that path and the others say the endpoint was not captured. A made-up
/// path fails at the far end and comes back looking like the store declined us, which is the failure mode R823 named and
/// R991 removed from the token fallback.
/// </para>
/// </summary>
public sealed class UnmatchedGatewaysTests
{
    private static readonly string[] Added = { "mollie", "gmo", "touchtech", "midtrans" };

    /// <summary>All four are in the default registry, which is the call site that makes them reachable.</summary>
    [Fact]
    public void TheFourAreRegistered()
    {
        var registry = PaymentGatewayRegistry.CreateDefault();
        var ids = registry.All.Select(g => g.Id).ToList();

        foreach (var id in Added)
            Assert.Contains(id, ids);
    }

    /// <summary>
    /// Registration is what puts a gateway in the artifact, so the count matters as much as the names:
    /// 13 original + Checkout.com in Phase 2 + Komoju in R1304, which the offsite card machine
    /// (<c>0x140D994D0</c>) needed as soon as its two frozen endpoints were decoded.
    /// </summary>
    [Fact]
    public void TheRegistryHasFifteen()
    {
        var registry = PaymentGatewayRegistry.CreateDefault();
        Assert.Equal(15, registry.All.Count);
        Assert.NotNull(registry.Resolve("checkoutcom"));
        Assert.NotNull(registry.Resolve("komoju"));
    }

    /// <summary>
    /// The steps the image says nothing about report that, rather than inventing an endpoint.
    ///
    /// <para>
    /// Midtrans is the exception and says so in its own message: Snap session creation is its tokenising step, so asking
    /// it to tokenise separately would be asking for something the protocol does not have. GMO now implements
    /// CreateToken (<c>sub_140ECF2B0</c>).
    /// </para>
    /// </summary>
    [Fact]
    public void TheUncapturedStepsSaySo()
    {
        var registry = PaymentGatewayRegistry.CreateDefault();

        foreach (var id in new[] { "mollie", "touchtech" })
        {
            var gateway = registry.Resolve(id);
            Assert.NotNull(gateway);

            var result = gateway!.TokenizeAsync(null!, default).GetAwaiter().GetResult();
            Assert.False(result.Ok);
            Assert.Contains("not captured", result.Error);
        }
    }

    /// <summary>Midtrans records both Snap versions the image names, so the older one need not be re-captured.</summary>
    [Fact]
    public void MidtransKeepsBothSnapVersions()
    {
        Assert.Equal(new[] { "/snap/v1/transactions", "/snap/v2/transactions" }, MidtransGateway.SnapPaths);
    }

    [Fact]
    public async Task GmoTokenizeBuildsValidCryptoEnvelopeAndParsesToken()
    {
        var card = new Card { Number = "4111 1111 1111 1111", Name = "Taro Yamada", Month = "5", Year = "2030", Cvv = "123" };
        var iv = Enumerable.Range(0, 16).Select(i => (byte)(i + 1)).ToArray();
        var salt = Enumerable.Range(16, 16).Select(i => (byte)(i + 1)).ToArray();

        var built = GmoGateway.BuildCreateTokenPayload(card, GmoGateway.DefaultApiKey, iv, salt);
        Assert.Equal(JTokenType.Null, built["createCount"]!.Type);
        var enc = (JObject)built["encryptionParameters"]!;
        Assert.Equal("SHARED_PK", enc["type"]?.ToString());
        Assert.Equal(GmoGateway.DefaultApiKey, enc["apiKey"]?.ToString());

        var keySpec = enc["keySpec"]!.ToString();
        var encryptedData = built["encryptedData"]!.ToString();
        var expectedSig = GmoGateway.ComputeSignature(GmoGateway.DefaultApiKey, keySpec, encryptedData);
        Assert.Equal(expectedSig, enc["signature"]?.ToString());

        // Verify AES-128-CBC-PKCS7 decryption matches the exact card JSON contract
        var derivedKey = Rfc2898DeriveBytes.Pbkdf2(
            Encoding.UTF8.GetBytes("SecretPassphrase"), salt, 100, HashAlgorithmName.SHA1, 16);
        using var aes = Aes.Create();
        aes.KeySize = 128;
        aes.Mode = CipherMode.CBC;
        aes.Padding = PaddingMode.PKCS7;
        aes.Key = derivedKey;
        var plainJson = Encoding.UTF8.GetString(aes.DecryptCbc(Convert.FromBase64String(encryptedData), iv, PaddingMode.PKCS7));
        var inner = JObject.Parse(plainJson);
        Assert.Equal(string.Empty, inner["deviceFingerprint"]?.ToString());
        Assert.Equal("4111111111111111", inner["card"]?["cardNumber"]?.ToString());
        Assert.Equal("05", inner["card"]?["expiryMonth"]?.ToString());
        Assert.Equal("2030", inner["card"]?["expiryYear"]?.ToString());
        Assert.Equal("123", inner["card"]?["securityCode"]?.ToString());

        using var server = new TinyServer((req, _) =>
        {
            if (req.Url?.AbsolutePath == "/payment/CreateToken.json")
                return (200, "{\"result\":\"success\",\"tokenList\":[\"gmo_tok_99\"]}");
            return (404, "{}");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl, Card = card };
        ctx.Session.Vars["gmo.tokenUrl"] = server.BaseUrl + "/payment/CreateToken.json";

        var result = await new GmoGateway().TokenizeAsync(ctx, default);
        Assert.True(result.Ok, result.Error);
        Assert.Equal("gmo_tok_99", result.GatewayReference);
        Assert.Equal("gmo_tok_99", ctx.Session.PaymentToken);
        Assert.Equal("gmo_tok_99", ctx.Session.Vars["gmo.token"]);
        var reqHeaders = Assert.Single(server.RequestHeaders);
        Assert.Equal("js-legacy", reqHeaders["x-mp-client-type"]);
    }

    [Fact]
    public async Task GmoParsesAndWalksMulPayHtmlHops()
    {
        var iframeHop = GmoGateway.ParseMulPayHtmlHop("<iframe src=\"/acs-step?a=1&amp;b=2\"></iframe>", "https://mulpay.test/start");
        Assert.Equal(GmoGateway.MulPayHopKind.Iframe, iframeHop.Kind);
        Assert.Equal("https://mulpay.test/acs-step?a=1&b=2", iframeHop.Url);

        var methodHop = GmoGateway.ParseMulPayHtmlHop(
            "<div class=\"mainContainer\"><form action=\"/method\"><input id=\"threeDSMethodData\" name=\"threeDSMethodData\" value=\"mdata-1\"/></form></div>",
            "https://mulpay.test/m");
        Assert.Equal(GmoGateway.MulPayHopKind.ThreeDsMethodForm, methodHop.Kind);
        Assert.Equal("mdata-1", methodHop.Inputs["threeDSMethodData"]);

        var locHop = GmoGateway.ParseMulPayHtmlHop("<script>location.href='/done?ok=1';</script>", "https://mulpay.test/x");
        Assert.Equal(GmoGateway.MulPayHopKind.LocationRedirect, locHop.Kind);
        Assert.Equal("https://mulpay.test/done?ok=1", locHop.Url);

        using var server = new TinyServer((req, body) =>
        {
            var path = req.Url?.AbsolutePath ?? "/";
            if (path == "/mulpay/start")
                return (200, "<html><iframe src=\"/mulpay/brw\"></iframe></html>");
            if (path == "/mulpay/brw")
                return (200, "<form name=\"brwInfo\" action=\"/mulpay/callbackSession?id=7\"><input name=\"transId\" value=\"tr-7\"/></form>");
            if (path == "/mulpay/callbackSession" && req.HttpMethod == "POST")
                return (200, "<html><script>location.href='/mulpay/complete';</script></html>");
            return (200, "<html>done</html>");
        });

        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl };
        var res = await new GmoGateway().ProcessMulPayAsync(ctx, server.BaseUrl + "/mulpay/start", default);

        Assert.True(res.Ok, res.Error);
        Assert.Contains(server.Requests, r => r.Path == "/mulpay/brw");
        var cbReq = Assert.Single(server.Requests, r => r.Path == "/mulpay/callbackSession");
        Assert.Contains("transId=tr-7", cbReq.Body);
    }
}
