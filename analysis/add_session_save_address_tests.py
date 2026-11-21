"""Tests for saveAddress, and refresh of the async-tail doc."""

import io
import subprocess
import sys

TESTS = 'replica/tests/Cybersole.Tests/StoreSessionQueriesTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

if 'TheAddressSaveJoinsTheSameFamily' not in text:
    block = '''
    /// <summary>
    /// R1366: saveAddress belongs here — four declared variables, no host, and the image's own async tail names a
    /// SaveAddress step, which is what makes it a store step rather than a helper.
    /// </summary>
    [Fact]
    public void TheAddressSaveJoinsTheSameFamily()
    {
        Assert.Equal(296, StoreSessionQueries.SaveAddressDocument.Length);
        Assert.StartsWith("mutation saveAddress(", StoreSessionQueries.SaveAddressDocument);
        Assert.Equal(new[] { "address", "editAddress", "saveAddress", "setDefault" },
            StoreSessionQueries.Declared["saveAddress"]);
        Assert.Same(StoreSessionQueries.SaveAddressDocument, StoreSessionQueries.DocumentFor("saveAddress"));
    }

    [Fact]
    public async Task TheAddressSavePostsItsFourVariables()
    {
        using var server = new TinyServer((_, _) => (200, "{\\"data\\":{\\"saveAddress\\":{}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await StoreSessionQueries.SendAsync(
            ctx, server.BaseUrl + "/graphql", "saveAddress",
            new JObject
            {
                ["address"] = new JObject { ["city"] = "Seoul" },
                ["editAddress"] = false,
                ["saveAddress"] = true,
                ["setDefault"] = false,
            }, default);

        Assert.NotNull(data);
        Assert.Equal(string.Empty, error);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(StoreSessionQueries.SaveAddressDocument, sent["query"]!.ToObject<string>());
    }
}
'''

    text = text.rstrip()
    text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
    io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
    print('appended two tests')

result = subprocess.run([sys.executable, 'analysis/async_tail.py', '--write-doc'],
                        capture_output=True, text=True)
print('async_tail --write-doc exit %d' % result.returncode)
if result.stdout:
    print(result.stdout.splitlines()[0])
