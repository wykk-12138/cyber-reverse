"""R1350 tests: the Highsnobiety payment step."""

import io

PATH = 'replica/tests/Cybersole.Tests/HighsnobietyFlowTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'ThePaymentStepCarriesItsTwoVariables' in text:
    raise SystemExit('tests already present')

block = '''
    /// <summary>
    /// R1350: the payment mutation, 222 characters, placed by its sender's address (0x140B56EA4, inside this
    /// store's own payment sender) rather than by its signature — which matched no family the cluster script knew.
    /// </summary>
    [Fact]
    public void ThePaymentStepCarriesItsTwoVariables()
    {
        Assert.Equal(222, HighsnobietyFlow.CreateCheckoutPaymentDocument.Length);
        Assert.StartsWith("mutation createCheckoutPayment($storefront: Storefront", 
            HighsnobietyFlow.CreateCheckoutPaymentDocument);
        Assert.Contains("$withoutShippingAddressSet", HighsnobietyFlow.CreateCheckoutPaymentDocument);
    }

    [Fact]
    public async Task WithoutAStorefrontThePaymentStepSendsNothing()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var outcome = await new HighsnobietyFlow().SubmitPaymentAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("$storefront", outcome.Error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task ThePaymentStepPostsItsEnvelope()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"createCheckoutPayment\\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["highsnobiety.storefront"] = "hs-store";
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";

        var outcome = await new HighsnobietyFlow().SubmitPaymentAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("createCheckoutPayment", sent["operationName"]!.ToObject<string>());
        Assert.Equal(HighsnobietyFlow.CreateCheckoutPaymentDocument, sent["query"]!.ToObject<string>());
        Assert.Equal("hs-store", sent["variables"]!["storefront"]!.ToObject<string>());
        Assert.False(sent["variables"]!["withoutShippingAddressSet"]!.ToObject<bool>());
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('appended three payment tests')
