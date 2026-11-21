"""Wire the Braintree token into the session step, and test it."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/BraintreeClientTokenTests.cs'

text = io.open(FLOW, encoding='utf-8', newline='').read()
if 'BraintreeClientToken' not in text:
    marker = 'public virtual Task<StepOutcome> GetSessionAsync(FlowContext c, CancellationToken ct)'
    position = text.find(marker)
    if position < 0:
        raise SystemExit('GetSessionAsync not found')

    end = text.find(';', position)
    replacement = '''public virtual async Task<StepOutcome> GetSessionAsync(FlowContext c, CancellationToken ct)
    {
        // R1358: Braintree's client token, when a run names an endpoint for it. The authorization fingerprint and
        // the type are the run's; the image never shows what fills them.
        var tokenEndpoint = c.Session.Vars.GetValueOrDefault("braintree.endpoint");
        if (!string.IsNullOrEmpty(tokenEndpoint))
        {
            var variables = new Newtonsoft.Json.Linq.JObject
            {
                ["type"] = c.Session.Vars.GetValueOrDefault("braintree.tokenType"),
                ["authorizationFingerprint"] = c.Session.Vars.GetValueOrDefault("braintree.fingerprint"),
            };

            var (token, tokenError) = await BraintreeClientToken
                .FetchAsync(c, tokenEndpoint, variables, ct).ConfigureAwait(false);
            if (token is null) return StepOutcome.Fail(tokenError);

            c.Session.Vars["clientToken"] = token;
            return StepOutcome.Success();
        }

        return await NotSupported("GetSession").ConfigureAwait(false);
    }'''
    text = text[:position] + replacement + text[end + 1:]
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(text)
    print('GetSessionAsync now fetches the Braintree token')

tests = '''using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1358: Braintree's client token. The handler names the field and the reply key, and gives the failure its own
/// words — a run should read the same here as in the image.
/// </summary>
public sealed class BraintreeClientTokenTests
{
    [Fact]
    public void TheDocumentAndTheHandlersFieldNames()
    {
        Assert.Equal("generateClientToken", BraintreeClientToken.OperationName);
        Assert.Equal(188, BraintreeClientToken.Document.Length);
        Assert.StartsWith("query generateClientToken($type: String)", BraintreeClientToken.Document);
        Assert.Equal("authorizationFingerprint", BraintreeClientToken.AuthorizationFingerprintField);
        Assert.Equal("clientToken", BraintreeClientToken.ClientTokenField);
        Assert.Equal("Error getting token", BraintreeClientToken.ErrorGettingTokenMessage);
    }

    [Fact]
    public async Task WithoutAnEndpointNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (token, error) = await BraintreeClientToken.FetchAsync(ctx, null, new JObject(), default);

        Assert.Null(token);
        Assert.Contains("no endpoint", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheReplyCarries(clientTokensit()
    {
    }
}
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote a placeholder tests file (to be completed)')
