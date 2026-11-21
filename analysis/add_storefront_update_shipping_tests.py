"""Tests for the new family member, and a note that the SCAPI path is a different transport."""

import io

TESTS = 'replica/tests/Cybersole.Tests/StorefrontApiProductTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

if 'TheShippingUpdateJoinsTheSameFamily' in text:
    raise SystemExit('tests already present')

block = '''
    /// <summary>
    /// R1361: UpdateShippingAddress joins this family because one of its two handlers builds the same api/graphql
    /// path. Its other handler posts to Salesforce's Commerce API — a different transport for a similar idea, and
    /// not something this replica touches.
    /// </summary>
    [Fact]
    public void TheShippingUpdateJoinsTheSameFamily()
    {
        Assert.Equal(2386, StorefrontApiQueries.UpdateShippingAddress.Length);
        Assert.StartsWith("mutation UpdateShippingAddress($input:", StorefrontApiQueries.UpdateShippingAddress);
        Assert.Equal(new[] { "input" }, StorefrontApiQueries.Declared["UpdateShippingAddress"]);
        Assert.Same(StorefrontApiQueries.UpdateShippingAddress,
            StorefrontApiQueries.DocumentFor("UpdateShippingAddress"));
    }

    [Fact]
    public async Task TheShippingUpdatePostsToTheFamilyPath()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"updateShippingAddress\\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StorefrontApiQueries.SendAsync(
            ctx, server.BaseUrl, "UpdateShippingAddress", new JObject { ["input"] = new JObject() }, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        Assert.EndsWith("/api/graphql", server.Requests[0].Path);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(StorefrontApiQueries.UpdateShippingAddress, sent["query"]!.ToObject<string>());
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('appended two tests')
