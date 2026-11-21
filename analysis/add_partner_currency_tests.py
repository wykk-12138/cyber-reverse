"""R1336 tests: the conversion document, its misspelled variable, and the gateway order."""

import io

PATH = 'replica/tests/Cybersole.Tests/PayPalPartnerCurrencyTests.cs'
source = '''using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1336: CurrencyConversion, from the sender at sub_14110F8C0 — same partner base URL and envelope as the
/// approval, a 10406-character document, and one variable key the image spells differently from its document.
/// </summary>
public sealed class PayPalPartnerCurrencyTests
{
    [Fact]
    public void TheEndpointSharesTheApprovalsBaseAndNamesItsOwnOperation()
    {
        Assert.Equal(PayPalPartnerApprove.BaseUrl, PayPalPartnerCurrency.BaseUrl);
        Assert.Equal("CurrencyConversion", PayPalPartnerCurrency.OperationName);
        Assert.Equal("https://www.paypal.com/graphql/CurrencyConversion", PayPalPartnerCurrency.Url);
        Assert.NotEqual(PayPalPartnerApprove.Url, PayPalPartnerCurrency.Url);
    }

    [Fact]
    public void TheDocumentIsTheStringTheImageHolds()
    {
        Assert.Equal(10406, PayPalPartnerCurrency.Document.Length);
        Assert.StartsWith("mutation CurrencyConversion($conversionType: CheckoutCurrencyConversionType!",
            PayPalPartnerCurrency.Document);
        Assert.Contains("updateCurrencyConversionType(token: $token, conversionType: $conversionType)",
            PayPalPartnerCurrency.Document);
    }

    /// <summary>
    /// The image declares $experiences in the document and sends "expeirences" in the variables. This is the one
    /// test whose job is to stop somebody correcting it: the corrected spelling is a different request.
    /// </summary>
    [Fact]
    public void TheVariableKeyIsSpelledTheWayTheImageSendsIt()
    {
        Assert.Equal(new[] { "token", "conversionType", "expeirences" }, PayPalPartnerCurrency.VariableNames);
        Assert.Contains("$experiences", PayPalPartnerCurrency.Document);
        Assert.DoesNotContain("$expeirences", PayPalPartnerCurrency.Document);
        Assert.Contains("expeirences", PayPalPartnerCurrency.VariableNames);
        Assert.DoesNotContain("experiences", PayPalPartnerCurrency.VariableNames);
    }

    [Fact]
    public void TheEnvelopeCarriesTheOperationNameAndTheDocument()
    {
        var body = PayPalPartnerCurrency.Envelope(new JObject { ["token"] = "t" });

        Assert.Equal("CurrencyConversion", body["operationName"]!.ToObject<string>());
        Assert.Equal(PayPalPartnerCurrency.Document, body["query"]!.ToObject<string>());
        Assert.Equal("VENDOR", PayPalPartnerCurrency.ConversionTypeVendor);
    }

    [Fact]
    public async Task ATokenlessConversionIsRefusedBeforeAnyRequest()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (conversion, error) = await PayPalPartnerCurrency.ConvertAsync(ctx, new JObject(), default);

        Assert.Null(conversion);
        Assert.Contains("no token", error);
        Assert.Empty(server.Requests);
    }

    /// <summary>
    /// With a conversion type in the session the gateway converts first and then approves — two requests, in
    /// that order, which is the ordering the image's two senders imply and this test pins.
    /// </summary>
    [Fact]
    public async Task TheGatewayConvertsBeforeItApproves()
    {
        using var server = new TinyServer((_, body) =>
        {
            if (body.Contains("CurrencyConversion", System.StringComparison.Ordinal))
                return (200, "{\\"data\\":{\\"updateCurrencyConversionType\\":{\\"fundingOptions\\":[]}}}");
            return (200, "{\\"data\\":{\\"approveMemberPayment\\":{\\"state\\":\\"COMPLETED\\"}}}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["paypal.partnerToken"] = "tok-1";
        ctx.Session.Vars["paypal.conversionType"] = "VENDOR";
        ctx.Session.Vars["paypal.currencyUrl"] = server.BaseUrl + "/graphql/CurrencyConversion";
        ctx.Session.Vars["paypal.partnerApproveUrl"] = server.BaseUrl + "/graphql/approveMemberPayment";

        var result = await new PayPalGateway().AuthorizeAsync(ctx, default);

        Assert.True(result.Ok, result.Error);
        Assert.Equal(2, server.Requests.Count);
        Assert.Contains("CurrencyConversion", server.Requests[0].Body!);
        Assert.Contains("approveMemberPayment", server.Requests[1].Body!);
        Assert.Contains("expeirences", server.Requests[0].Body!);
        Assert.False(ctx.Session.Vars.ContainsKey("paypal.conversion") == false);
    }
}
'''

io.open(PATH, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % PATH)
