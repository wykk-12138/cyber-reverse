"""R1339 tests for the two new steps."""

import io

PATH = 'replica/tests/Cybersole.Tests/HighsnobietyFlowTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'TheProductQueryCarriesAllFiveVariables' in text:
    raise SystemExit('tests already present')

block = '''
    /// <summary>
    /// R1339: the product query's document declares five variables, and the step fills all five — the slug from
    /// the run, the three locale fields defaulting to each other, and the country from the profile.
    /// </summary>
    [Fact]
    public async Task TheProductQueryCarriesAllFiveVariables()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"product\\":{\\"id\\":\\"p-1\\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext
        {
            Http = http,
            Url = server.BaseUrl + "/",
            ProfileData = new Cybersole.Core.Models.Profile { Country = "DE" },
        };
        ctx.Session.Vars["slug"] = "hs-tee";
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";

        var outcome = await new HighsnobietyFlow().FindProductAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("fetchProduct", sent["operationName"]!.ToObject<string>());
        Assert.Equal(5718, HighsnobietyFlow.FetchProductDocument.Length);
        Assert.Equal(HighsnobietyFlow.FetchProductDocument, sent["query"]!.ToObject<string>());
        var variables = sent["variables"]!;
        Assert.Equal("hs-tee", variables["slug"]!.ToObject<string>());
        Assert.Equal("de", variables["country"]!.ToObject<string>().ToLowerInvariant());
        Assert.Equal("en", variables["locale"]!.ToObject<string>());
        Assert.Equal("en", variables["preferredLocale"]!.ToObject<string>());
        Assert.Equal("en", variables["fallbackLocale"]!.ToObject<string>());
    }

    [Fact]
    public async Task WithoutASlugTheProductQueryIsNotSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var outcome = await new HighsnobietyFlow().FindProductAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Empty(server.Requests);
    }

    /// <summary>
    /// The email mutation's own input type is SetCartCustomerEmail, not the cart line's AddCartLineItem — the two
    /// are per-operation objects, which is why each step has its own session key.
    /// </summary>
    [Fact]
    public async Task TheEmailStepSendsItsOwnActionObject()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["highsnobiety.emailAction"] = "{\\"email\\":\\"ada@example.test\\"}";
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";

        var outcome = await new HighsnobietyFlow().SubmitEmailAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal(4986, HighsnobietyFlow.SetCustomerEmailDocument.Length);
        Assert.StartsWith("mutation setCustomerEmail($action: SetCartCustomerEmail!", HighsnobietyFlow.SetCustomerEmailDocument);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("setCustomerEmail", sent["operationName"]!.ToObject<string>());
        Assert.Equal("ada@example.test", sent["variables"]!["action"]!["email"]!.ToObject<string>());
    }

    [Fact]
    public async Task WithoutTheEmailActionNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var outcome = await new HighsnobietyFlow().SubmitEmailAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("highsnobiety.emailAction", outcome.Error);
        Assert.Empty(server.Requests);
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('appended four tests')
