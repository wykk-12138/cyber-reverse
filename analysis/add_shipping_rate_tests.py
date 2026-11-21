"""R1330 tests: the rate hop goes out with the id the address reply offered."""

import io

PATH = 'replica/tests/Cybersole.Tests/WarhammerGraphQlTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'TheShippingRateHopSendsTheIdTheAddressReplyOffered' in text:
    raise SystemExit('tests already present')

block = '''
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
                return (200, "{\\"data\\":{\\"updateShippingRate\\":{\\"errors\\":[]," +
                            "\\"order\\":{\\"number\\":\\"W-1\\",\\"checkoutVersion\\":9,\\"guestToken\\":\\"gt-9\\"," +
                            "\\"isShippingValid\\":true}}}}");
            return (200, "{\\"data\\":{\\"updateShippingAddress\\":{\\"availableShippingRates\\":[" +
                         "{\\"id\\":42,\\"name\\":\\"Standard\\"}]}}}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.ProfileData = new Cybersole.Core.Models.Profile
        {
            FirstName = "Ada", LastName = "Lovelace", Address1 = "1 Main St",
            City = "Austin", Zip = "78701", Phone = "5550100", Country = "US", Email = "ada@example.test",
        };
        ctx.Session.Vars["wh.apiHost"] = server.BaseUrl;

        var outcome = await new WarhammerFlow().SubmitShippingAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal(2, server.Requests.Count);
        Assert.Equal("42", ctx.Session.Vars["shippingRateId"]);

        var rateRequest = Newtonsoft.Json.Linq.JObject.Parse(server.Requests[1].Body!);
        Assert.Equal(WarhammerQueries.UpdateShippingRate, rateRequest["query"]!.Value<string>());
        Assert.Equal(42, rateRequest["variables"]!["selectedShippingRateId"]!.Value<int>());
        Assert.False(rateRequest["variables"]!["isNewsletterSubscribed"]!.Value<bool>());
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
            (200, "{\\"data\\":{\\"updateShippingAddress\\":{\\"availableShippingRates\\":[]}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.ProfileData = new Cybersole.Core.Models.Profile
        {
            FirstName = "Ada", LastName = "Lovelace", Address1 = "1 Main St",
            City = "Austin", Zip = "78701", Phone = "5550100", Country = "US", Email = "ada@example.test",
        };
        ctx.Session.Vars["wh.apiHost"] = server.BaseUrl;

        var outcome = await new WarhammerFlow().SubmitShippingAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Single(server.Requests);
        Assert.Contains(ctx.Events, e => e.Name.Contains("no shipping rate id"));
        Assert.False(ctx.Session.Vars.ContainsKey("shippingRateId"));
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('appended the shipping-rate tests')
