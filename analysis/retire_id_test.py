"""Retire the id-premise test: the family no longer refuses on a missing id, it refuses on undeclared variables."""

import io

PATH = 'replica/tests/Cybersole.Tests/StorefrontApiProductTests.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

start = text.find('    [Fact]\n    public async Task WithoutAnIdNothingIsSent()')
if start < 0:
    raise SystemExit('test start not found')
end = text.find('    [Fact]', start + 10)
if end < 0:
    raise SystemExit('test end not found')

replacement = '''    /// <summary>
    /// R1346: a variable the document does not declare cannot be passed — the server would reject the request, so
    /// the family refuses it here instead of letting a run fail later with a GraphQL error nobody expected.
    /// </summary>
    [Fact]
    public async Task AnUndeclaredVariableIsRefused()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StorefrontApiQueries.SendAsync(
            ctx, server.BaseUrl, "getSession", new JObject { ["id"] = "1" }, default);

        Assert.Null(data);
        Assert.Contains("does not declare $id", error);
        Assert.Empty(server.Requests);
    }

'''

text = text[:start] + replacement + text[end:]
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('retired the id test, added the variable-set test')
