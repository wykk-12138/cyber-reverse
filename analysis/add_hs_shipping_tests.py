"""R1354 tests: the shipping step, and the fact that it is the third of three."""

import io

PATH = 'replica/tests/Cybersole.Tests/HighsnobietyFlowTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'TheShippingStepIsTheThirdAddressStep' in text:
    raise SystemExit('tests already present')

block = '''
    /// <summary>
    /// R1354: shipping is the store's third address step. Its document is 4992 characters and declares the same
    /// shape as billing and email — one action object plus two locales — which is what placed it here, together
    /// with its sender being the function the host sweep had already labelled as shipping.
    /// </summary>
    [Fact]
    public void TheShippingStepIsTheThirdAddressStep()
    {
        Assert.Equal(4992, HighsnobietyFlow.SetShippingAddressDocument.Length);
        Assert.StartsWith("mutation setShippingAddress($action: SetCartShippingAddress!",
            HighsnobietyFlow.SetShippingAddressDocument);
        Assert.Contains("$locale", HighsnobietyFlow.SetShippingAddressDocument);
        Assert.Contains("$preferredLocale", HighsnobietyFlow.SetShippingAddressDocument);

        // The three address-shaped documents share the action-plus-two-locales signature, and no two are equal.
        Assert.NotEqual(HighsnobietyFlow.SetBillingAddressDocument, HighsnobietyFlow.SetShippingAddressDocument);
        Assert.NotEqual(HighsnobietyFlow.SetCustomerEmailDocument, HighsnobietyFlow.SetShippingAddressDocument);
    }

    [Fact]
    public async Task WithoutAShippingActionTheStepSendsNothing()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var outcome = await new HighsnobietyFlow().SubmitShippingAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheShippingStepPostsItsEnvelope()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"setShippingAddress\\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";
        ctx.Session.Vars["highsnobiety.shippingAction"] =
            "{\\"type\\":\\"SetCartShippingAddress\\",\\"address\\":{\\"city\\":\\"Seoul\\"}}";

        var outcome = await new HighsnobietyFlow().SubmitShippingAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("setShippingAddress", sent["operationName"]!.ToObject<string>());
        Assert.Equal(HighsnobietyFlow.SetShippingAddressDocument, sent["query"]!.ToObject<string>());
        Assert.Equal("Seoul",
            sent["variables"]!["action"]!["address"]!["city"]!.ToObject<string>());
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('appended three shipping tests')
