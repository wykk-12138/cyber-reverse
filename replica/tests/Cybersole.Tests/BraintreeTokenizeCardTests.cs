using Cybersole.Stores.Payments;
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
