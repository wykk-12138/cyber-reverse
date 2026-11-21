"""Tests for the contact-details member, plus the honest note about its hash twin."""

import io

TESTS = 'replica/tests/Cybersole.Tests/StoreSessionQueriesTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

if 'TheContactDetailsJoinTheSameFamily' in text:
    raise SystemExit('already present')

block = '''
    /// <summary>
    /// R1363: UpdateContactDetails' one handler builds https:// + host + /graphql, so it takes the caller's origin
    /// like the rest of this family. Its other handler sends the same operation by hash; which a run picks is not
    /// established, so only this one is wired.
    /// </summary>
    [Fact]
    public void TheContactDetailsJoinTheSameFamily()
    {
        Assert.Equal(244, StoreSessionQueries.UpdateContactDetailsDocument.Length);
        Assert.StartsWith("mutation UpdateContactDetails", StoreSessionQueries.UpdateContactDetailsDocument);
        Assert.Equal(new[] { "email", "emailOptIn", "phone" },
            StoreSessionQueries.Declared["UpdateContactDetails"]);
        Assert.Same(StoreSessionQueries.UpdateContactDetailsDocument,
            StoreSessionQueries.DocumentFor("UpdateContactDetails"));
    }

    [Fact]
    public async Task TheContactDetailsPostTheirThreeVariables()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"updateContactDetails\\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, server.BaseUrl + "/graphql", "UpdateContactDetails",
            new JObject { ["email"] = "a@b.test", ["emailOptIn"] = false, ["phone"] = "010" }, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(StoreSessionQueries.UpdateContactDetailsDocument, sent["query"]!.ToObject<string>());
        Assert.Equal("a@b.test", sent["variables"]!["email"]!.ToObject<string>());
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('appended two tests')
