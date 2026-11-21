"""Wire the session queries into VerifySessionAsync, and test the family."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/StoreSessionQueriesTests.cs'

text = io.open(FLOW, encoding='utf-8', newline='').read()
if 'StoreSessionQueries' not in text:
    marker = 'public virtual Task<StepOutcome> VerifySessionAsync(FlowContext c, CancellationToken ct)'
    position = text.find(marker)
    if position < 0:
        raise SystemExit('VerifySessionAsync not found')

    end = text.find(';', position)
    replacement = '''public virtual async Task<StepOutcome> VerifySessionAsync(FlowContext c, CancellationToken ct)
    {
        // R1359: the session-shaped family whose handlers name no host. When a run supplies an origin, the customer
        // is read through it; otherwise the step does what it always did.
        var sessionOrigin = c.Session.Vars.GetValueOrDefault("storeSession.origin");
        if (!string.IsNullOrEmpty(sessionOrigin))
        {
            var (data, error) = await StoreSessionQueries
                .SendAsync(c, sessionOrigin, "getCustomerInformation", new Newtonsoft.Json.Linq.JObject(), ct)
                .ConfigureAwait(false);
            if (data is null) return StepOutcome.Fail(error);

            c.Session.Vars["customer"] = data.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }

        return await Ok().ConfigureAwait(false);
    }'''
    text = text[:position] + replacement + text[end + 1:]
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(text)
    print('VerifySessionAsync now consults the session family')

tests = '''using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1359: four session-shaped operations whose handlers name no host, so the origin is the caller's. The declared
/// sets are the documents' own — three of them take no variables at all.
/// </summary>
public sealed class StoreSessionQueriesTests
{
    [Fact]
    public void TheFourDocumentsAreTheMeasuredOnes()
    {
        Assert.Equal(197, StoreSessionQueries.GetCustomerInformationDocument.Length);
        Assert.StartsWith("query getCustomerInformation {", StoreSessionQueries.GetCustomerInformationDocument);
        Assert.Equal(3067, StoreSessionQueries.GetPaymentdMethodsDocument.Length);
        Assert.Equal(67, StoreSessionQueries.ItemDocument.Length);
        Assert.Equal(3234, StoreSessionQueries.GetCartDocument.Length);
        Assert.StartsWith("query getCart", StoreSessionQueries.GetCartDocument);
    }

    /// <summary>getPaymentdMethods keeps the image's own spelling of "methods".</summary>
    [Fact]
    public void TheOperationNameKeepsItsMisspelling()
    {
        Assert.NotNull(StoreSessionQueries.DocumentFor("getPaymentdMethods"));
        Assert.StartsWith("query getPaymentdMethods", StoreSessionQueries.GetPaymentdMethodsDocument);
    }

    [Fact]
    public void ThreeOfTheFourDeclareNoVariables()
    {
        Assert.Empty(StoreSessionQueries.Declared["getCustomerInformation"]);
        Assert.Empty(StoreSessionQueries.Declared["getPaymentdMethods"]);
        Assert.Empty(StoreSessionQueries.Declared["item"]);
        Assert.Equal(new[] { "key", "locale" }, StoreSessionQueries.Declared["getCart"]);
    }

    [Fact]
    public async Task WithoutAnOriginNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, null, "getCart", new JObject(), default);

        Assert.Null(data);
        Assert.Contains("no origin", error);
        Assert.Empty(server.Requests);
    }

    /// <summary>A variable the document does not declare is refused before the request.</summary>
    [Fact]
    public async Task AnUndeclaredVariableIsRefused()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, server.BaseUrl, "getCustomerInformation", new JObject { ["key"] = "x" }, default);

        Assert.Null(data);
        Assert.Contains("does not declare $key", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheQueryPostsItsEnvelope()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"me\\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, server.BaseUrl, "getCustomerInformation", new JObject(), default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal("getCustomerInformation", sent["operationName"]!.ToObject<string>());
        Assert.Equal(StoreSessionQueries.GetCustomerInformationDocument, sent["query"]!.ToObject<string>());
    }
}
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)
