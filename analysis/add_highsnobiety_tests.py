"""R1338 tests: the store exists, its documents are the image's, and its unknown variable is refused."""

import io

PATH = 'replica/tests/Cybersole.Tests/HighsnobietyFlowTests.cs'
source = '''using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1338: Highsnobiety, built from the two senders R1337 read — host, operation names, envelope and variable
/// names are observed; the value of $action is not, and is refused rather than guessed.
/// </summary>
public sealed class HighsnobietyFlowTests
{
    [Fact]
    public void TheStoreIsIdentifiedByItsCustomerDomainAndItsApiIsSeparate()
    {
        var flow = new HighsnobietyFlow();

        Assert.Equal("highsnobiety", flow.Id);
        Assert.Equal("Highsnobiety", flow.Name);
        Assert.Contains("highsnobiety.com", flow.Domains);
        Assert.Equal("https://tm-api-eu.highsnobiety.com/", HighsnobietyFlow.ApiHost);
        Assert.DoesNotContain("tm-api-eu.highsnobiety.com", flow.Domains);
    }

    [Fact]
    public void BothDocumentsAreTheImageStrings()
    {
        Assert.Equal(3435, HighsnobietyFlow.AddLineItemDocument.Length);
        Assert.StartsWith("mutation addLineItem($country: Country!, $action: AddCartLineItem!",
            HighsnobietyFlow.AddLineItemDocument);
        Assert.Equal(3399, HighsnobietyFlow.AddDiscountCodeDocument.Length);
        Assert.StartsWith("mutation addDiscountCode($code: String!", HighsnobietyFlow.AddDiscountCodeDocument);
    }

    [Fact]
    public void TheVariableNamesAreTheDocumentsOwn()
    {
        Assert.Equal(new[] { "sku", "action", "country", "locale" }, HighsnobietyFlow.AddLineItemVariables);
        foreach (var name in HighsnobietyFlow.AddLineItemVariables)
            Assert.Contains("$" + name, HighsnobietyFlow.AddLineItemDocument);
    }

    /// <summary>
    /// $action is typed as an enum in the document and the image never names a member, so a run without it is
    /// told what to set. Guessing would send a request whose meaning nobody can check.
    /// </summary>
    [Fact]
    public async Task WithoutTheActionTheStepSaysWhatToSet()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["sku"] = "HS-1";

        var outcome = await new HighsnobietyFlow().AddToCartAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Contains("highsnobiety.action", outcome.Error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheAddPostsTheObservedEnvelope()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"addLineItem\\":{\\"id\\":\\"line-1\\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["sku"] = "HS-1";
        ctx.Session.Vars["highsnobiety.action"] = "ADD";
        ctx.Session.Vars["highsnobiety.country"] = "DE";
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";

        var outcome = await new HighsnobietyFlow().AddToCartAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("addLineItem", sent["operationName"]!.ToObject<string>());
        Assert.Equal(HighsnobietyFlow.AddLineItemDocument, sent["query"]!.ToObject<string>());
        Assert.Equal("HS-1", sent["variables"]!["sku"]!.ToObject<string>());
        Assert.Equal("ADD", sent["variables"]!["action"]!.ToObject<string>());
        Assert.Equal("DE", sent["variables"]!["country"]!.ToObject<string>());
        Assert.Equal("en", sent["variables"]!["locale"]!.ToObject<string>());
    }

    [Fact]
    public async Task TheDiscountPostsItsOwnOperationName()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";

        var outcome = await new HighsnobietyFlow().AddDiscountCodeAsync(ctx, "SAVE10", default);

        Assert.True(outcome.Ok, outcome.Error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("addDiscountCode", sent["operationName"]!.ToObject<string>());
        Assert.Equal("SAVE10", sent["variables"]!["code"]!.ToObject<string>());
    }
}
'''

io.open(PATH, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % PATH)
