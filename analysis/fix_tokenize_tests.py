"""Drop the test that would hit Braintree's real host — same mistake as the DNS one, caught before running."""

import io

TESTS = 'replica/tests/Cybersole.Tests/BraintreeTokenizeCardTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

start = text.find('    /// <summary>The step builds the input the handler\'s field names describe.</summary>')
if start < 0:
    raise SystemExit('test not found')
end = text.find('    [Fact]\n    public void TheEnvelopeCarriesOperationAndDocument()')
if end < 0:
    raise SystemExit('next test not found')

replacement = '''    /// <summary>
    /// The step builds the input the handler's field names describe. Checked without sending: the endpoint is
    /// Braintree's own host, so a test that sent would be a test that called a third party.
    /// </summary>
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
    }

'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(text[:start] + replacement + text[end:])
print('replaced the network test with a pure one')
