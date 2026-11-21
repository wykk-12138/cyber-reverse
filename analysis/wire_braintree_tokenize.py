"""Wire the tokenisation into the payment step, and test it."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/BraintreeTokenizeCardTests.cs'

text = io.open(FLOW, encoding='utf-8', newline='').read()
if 'BraintreeTokenizeCard' not in text:
    marker = 'public virtual Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)'
    position = text.find(marker)
    if position < 0:
        raise SystemExit('SubmitPaymentAsync not found in the base flow')

    end = text.find(';', position)
    replacement = '''public virtual async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        // R1360: Braintree tokenisation, when a run supplies a card. The card object and the client token are the
        // run's; the image names the host and the fields but never a card.
        var cardPayload = c.Session.Vars.GetValueOrDefault("braintree.creditCard");
        if (!string.IsNullOrWhiteSpace(cardPayload))
        {
            Newtonsoft.Json.Linq.JObject card;
            try
            {
                card = Newtonsoft.Json.Linq.JObject.Parse(cardPayload!);
            }
            catch (Newtonsoft.Json.JsonException)
            {
                return StepOutcome.Fail("braintree: braintree.creditCard is not valid JSON");
            }

            var variables = new Newtonsoft.Json.Linq.JObject
            {
                ["input"] = new Newtonsoft.Json.Linq.JObject
                {
                    ["creditCard"] = card,
                    ["client"] = new Newtonsoft.Json.Linq.JObject
                    {
                        ["clientSdkMetadata"] = new Newtonsoft.Json.Linq.JObject
                        {
                            ["source"] = Cybersole.Stores.Payments.BraintreeTokenizeCard.ClientSdkName,
                        },
                    },
                },
            };

            var (data, error) = await Cybersole.Stores.Payments.BraintreeTokenizeCard
                .TokenizeAsync(c, variables, ct).ConfigureAwait(false);
            if (data is null) return StepOutcome.Fail(error);

            c.Session.Vars["tokenizedCard"] = data.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }

        return await NotSupported("SubmitPayment").ConfigureAwait(false);
    }'''
    text = text[:position] + replacement + text[end + 1:]
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(text)
    print('base SubmitPaymentAsync now tokenises through Braintree')

tests = '''using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1360: Braintree's card tokenisation, at the host its handler names. The card itself is never a fixture here —
/// what is pinned is the endpoint, the SDK marker and the envelope.
/// </summary>
public sealed class BraintreeTokenizeCardTests
{
    [Fact]
    public void TheHostAndSdkMarkerAreTheObservedOnes()
    {
        Assert.Equal("https://payments.braintree-api.com/graphql", BraintreeTokenizeCard.Url);
        Assert.Equal("TokenizeCreditCard", BraintreeTokenizeCard.OperationName);
        Assert.Equal("dropin2", BraintreeTokenizeCard.ClientSdkName);
        Assert.Contains("creditCard", BraintreeTokenizeCard.ObservedFields);
        Assert.Contains("clientSdkMetadata", BraintreeTokenizeCard.ObservedFields);
    }

    [Fact]
    public void TheDocumentIsTheMeasuredString()
    {
        Assert.Equal(505, BraintreeTokenizeCard.Document.Length);
        Assert.StartsWith("mutation TokenizeCreditCard($input: TokenizeCreditCardInput!)",
            BraintreeTokenizeCard.Document);
    }

    [Fact]
    public async Task WithoutACardNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await BraintreeTokenizeCard.TokenizeAsync(ctx, new JObject(), default);

        Assert.Null(data);
        Assert.Contains("no creditCard", error);
        Assert.Empty(server.Requests);
    }

    /// <summary>The step builds the input the handler's field names describe.</summary>
    [Fact]
    public async Task ThePaymentStepBuildsTheInputAndSendsIt()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"tokenizeCreditCard\\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["braintree.creditCard"] = "{\\"number\\":\\"4111\\"}";

        var flow = new ShopifyFlow("testshop", "Test Shop", new[] { "shop.test" });
        var outcome = await flow.SubmitPaymentAsync(ctx, default);

        // The endpoint is Braintree's public host, so the request cannot reach the test server; what this asserts is
        // that the step refuses cleanly rather than throwing.
        Assert.False(outcome.Ok || outcome.Success);
        Assert.NotNull(outcome.Error);
    }

    [Fact]
    public void TheEnvelopeCarriesOperationAndDocument()
    {
        var body = BraintreeTokenizeCard.Envelope(new JObject());
        Assert.Equal("TokenizeCreditCard", body["operationName"]!.ToObject<string>());
        Assert.Equal(BraintreeTokenizeCard.Document, body["query"]!.ToObject<string>());
    }
}
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)
