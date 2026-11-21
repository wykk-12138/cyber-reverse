"""R1325: tests for the run-time dialect switch."""

import io

PATH = 'replica/tests/Cybersole.Tests/PayPalThreeDsTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'ProviderFieldsRequested' in text:
    raise SystemExit('tests already present')

block = '''
    /// <summary>
    /// R1325: the dialect is now a run-time choice. The image's own condition is still Unknown — what the round
    /// established is that the two variants are two methods of one class, each with a complete frozen document,
    /// so the image picks a method rather than splicing a field. Until a capture settles which method it picks,
    /// the session decides, and the default is the document this class already sent.
    /// </summary>
    [Theory]
    [InlineData(null, true)]
    [InlineData("", true)]
    [InlineData("true", true)]
    [InlineData("FALSE", false)]
    [InlineData("false", false)]
    [InlineData("0", false)]
    [InlineData("1", true)]
    public void TheDialectComesFromTheSessionAndDefaultsToTheLongerDocument(string? declared, bool expected)
    {
        var ctx = new FlowContext { Url = "https://www.paypal.com/graphql" };
        if (declared is not null) ctx.Session.Vars["paypal3ds.providerFields"] = declared;

        Assert.Equal(expected, PayPalThreeDs.ProviderFieldsRequested(ctx));
    }

    /// <summary>
    /// And the request body follows it: the same operation sends one document or the other depending on the
    /// session, which is the whole point of the switch.
    /// </summary>
    [Fact]
    public async Task TheBodyCarriesTheSelectedDialect()
    {
        var sent = new List<string>();
        using var server = new TinyServer((request, body) =>
        {
            sent.Add(body);
            return (200, "{\\"data\\":{}}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/graphql" };
        var input = new PayPalThreeDs.StageInput { ChallengeActive = false };

        await PayPalThreeDs.GqlAsync(ctx, input, PayPalThreeDs.LookUpOperation, new Newtonsoft.Json.Linq.JObject(),
            default, server.BaseUrl + "/graphql");
        ctx.Session.Vars["paypal3ds.providerFields"] = "false";
        await PayPalThreeDs.GqlAsync(ctx, input, PayPalThreeDs.LookUpOperation, new Newtonsoft.Json.Linq.JObject(),
            default, server.BaseUrl + "/graphql");

        Assert.Equal(2, sent.Count);
        var first = Newtonsoft.Json.Linq.JObject.Parse(sent[0])["query"]!.Value<string>();
        var second = Newtonsoft.Json.Linq.JObject.Parse(sent[1])["query"]!.Value<string>();
        Assert.Equal(PayPalThreeDs.LookUpDocument, first);
        Assert.Equal(PayPalThreeDs.LookUpDocumentWithoutProviderFields, second);
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('appended the dialect tests')
