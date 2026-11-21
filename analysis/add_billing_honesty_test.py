"""R1332 tests: the billing step says what it does not do."""

import io

PATH = 'replica/tests/Cybersole.Tests/ShopifyGraphQlTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'TheBillingStepReportsThatItSubmitsNothing' in text:
    raise SystemExit('tests already present')

block = '''
    /// <summary>
    /// R1332: this step returned Success without sending a single request, so the run log said billing was done
    /// while the checkout had not been touched. It still does not submit — the endpoint is not captured — but it
    /// now says so, and marks the session, so a failure downstream can be traced to the step that did nothing.
    /// </summary>
    [Fact]
    public async Task TheBillingStepReportsThatItSubmitsNothing()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/products/x",
            ProfileData = new Cybersole.Core.Models.Profile
            {
                FirstName = "Ada", LastName = "Lovelace", Address1 = "1 Main St",
                City = "Austin", Zip = "78701", Phone = "5550100", Country = "US", Email = "ada@example.test",
            },
        };

        var flow = new ShopifyFlow("testshop", "Test Shop", new[] { "shop.test" });
        var outcome = await flow.SubmitBillingAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Empty(server.Requests);
        Assert.Equal("false", ctx.Session.Vars["shopify.billingSubmitted"]);
        Assert.Contains(ctx.Events, e => e.Name.Contains("no billing request was made"));
        // The address is still recorded, for whatever consumer does have the endpoint.
        Assert.Equal("1 Main St", ctx.Session.Vars["billing1"]);
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('appended the billing honesty test')
