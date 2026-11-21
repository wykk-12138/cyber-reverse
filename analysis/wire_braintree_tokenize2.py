"""Insert the Braintree branch at the top of SubmitPaymentAsync's existing body, and write the tests."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/BraintreeTokenizeCardTests.cs'

text = io.open(FLOW, encoding='utf-8', newline='').read()
marker = 'public virtual async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)'
position = text.find(marker)
if position < 0:
    raise SystemExit('marker not found')

body = text.find('{', position)
if body < 0:
    raise SystemExit('no body')

if 'BraintreeTokenizeCard' not in text:
    branch = '''
        // R1360: Braintree tokenisation, when a run supplies a card. The card object is the run's; the image names
        // the host and the fields but never a card.
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

            var tokenizeVariables = new Newtonsoft.Json.Linq.JObject
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

            var (tokenized, tokenizeError) = await Cybersole.Stores.Payments.BraintreeTokenizeCard
                .TokenizeAsync(c, tokenizeVariables, ct).ConfigureAwait(false);
            if (tokenized is null) return StepOutcome.Fail(tokenizeError);

            c.Session.Vars["tokenizedCard"] = tokenized.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }
'''
    text = text[:body + 1] + branch + text[body + 1:]
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(text)
    print('branch inserted into the existing SubmitPaymentAsync body')

tests = '''using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1360: Braintree's card tokenisation, at the host its handler names. No card is a fixture and nothing is sent —
/// the endpoint is Braintree's own, so a test that called it would be calling a third party.
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

    /// <summary>The input mirrors the field names the handler names.</summary>
    [Fact]
    public void TheInputMatchesTheHandlersFieldNames()
    {
        var input = new JObject
        {
            ["creditCard"] = new JObject { ["number"] = "4111" },
            ["client"] = new JObject
            {
                ["clientSdkMetadata"] = new JObject { ["source"] = BraintreeTokenizeCard.ClientSdkName },
            },
        };
        var body = BraintreeTokenizeCard.Envelope(new JObject { ["input"] = input });

        Assert.Equal("dropin2",
            body["variables"]!["input"]!["client"]!["clientSdkMetadata"]!["source"]!.ToObject<string>());
        Assert.NotNull(body["variables"]!["input"]!["creditCard"]);
        Assert.Equal("TokenizeCreditCard", body["operationName"]!.ToObject<string>());
        Assert.Equal(BraintreeTokenizeCard.Document, body["query"]!.ToObject<string>());
    }
}
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)
