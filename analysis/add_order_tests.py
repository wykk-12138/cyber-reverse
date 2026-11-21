"""R1341 tests for the order step and the inventory's own guard."""

import io

TESTS = 'replica/tests/Cybersole.Tests/HighsnobietyFlowTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

if 'TheOrderStepConfirmsWithThePaymentIntent' in text:
    raise SystemExit('tests already present')

block = '''
    /// <summary>
    /// R1341: the confirmation query is keyed by the Stripe payment-intent id. Its document is 4825 characters at
    /// 0x14713E1FC and the sender at 0x140B574F0 passes exactly these three variables.
    /// </summary>
    [Fact]
    public async Task TheOrderStepConfirmsWithThePaymentIntent()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"order\\":{\\"number\\":\\"HS-1\\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["stripePaymentIntentId"] = "pi_123";
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";

        var outcome = await new HighsnobietyFlow().SubmitOrderAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal(4825, HighsnobietyFlow.FetchOrderConfirmationDocument.Length);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("fetchOrderConfirmation", sent["operationName"]!.ToObject<string>());
        Assert.Equal("pi_123", sent["variables"]!["stripePaymentIntentId"]!.ToObject<string>());
        Assert.Equal("en", sent["variables"]!["locale"]!.ToObject<string>());
        Assert.Equal("en", sent["variables"]!["preferredLocale"]!.ToObject<string>());
    }

    [Fact]
    public async Task WithoutAPaymentIntentTheOrderStepSendsNothing()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var outcome = await new HighsnobietyFlow().SubmitOrderAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("stripePaymentIntentId", outcome.Error);
        Assert.Empty(server.Requests);
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('appended two order tests')
