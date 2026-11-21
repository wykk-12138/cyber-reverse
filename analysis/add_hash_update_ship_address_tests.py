"""Tests for the new hash-family member."""

import io

TESTS = 'replica/tests/Cybersole.Tests/GraphQlHashQueriesTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

if 'TheShipAddressJoinsTheHashFamily' in text:
    raise SystemExit('already present')

block = '''
    /// <summary>
    /// R1364: updateShipAddress' handler carries x-graphql-hash and two more 64-hex values, so it joins the family
    /// that identifies its queries by hash. Its document declares one variable.
    /// </summary>
    [Fact]
    public void TheShipAddressJoinsTheHashFamily()
    {
        Assert.Equal(140, GraphQlHashQueries.UpdateShipAddressDocument.Length);
        Assert.StartsWith("mutation updateShipAddress($address: AddressInput!)",
            GraphQlHashQueries.UpdateShipAddressDocument);
        Assert.Same(GraphQlHashQueries.UpdateShipAddressDocument,
            GraphQlHashQueries.DocumentFor("updateShipAddress"));
    }

    /// <summary>Without a hash the family still sends a well-formed request.</summary>
    [Fact]
    public async Task TheShipAddressSendsItsDocumentWhenNoHashIsGiven()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"updateShipAddress\\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/graphql" };

        var (data, error) = await GraphQlHashQueries.SendAsync(
            ctx, server.BaseUrl + "/graphql", "updateShipAddress",
            new JObject { ["address"] = new JObject() }, null, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(GraphQlHashQueries.UpdateShipAddressDocument, sent["query"]!.ToObject<string>());
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('appended two tests')
