"""A test that PayerAuthenticate actually classifies, so the change is behaviour and not a rename."""

import io

TESTS = 'replica/tests/Cybersole.Tests/SauconyFlowTests.cs'
text = io.open(TESTS, encoding='utf-8').read()

if 'ThePayerStepClassifiesInsteadOfRefusing' in text:
    raise SystemExit('already present')

block = '''
    /// <summary>
    /// R1375: PayerAuthenticate used to refuse every call. It still cannot build the request, but it can read the
    /// reply — a redirect, a step-up, or the handler's own sentence.
    /// </summary>
    [Fact]
    public void ThePayerStepClassifiesInsteadOfRefusing()
    {
        var flow = new SauconyFlow();

        var withoutReply = flow.PayerAuthenticate(new Cybersole.Stores.Flows.FlowContext());
        Assert.False(withoutReply.Ok || withoutReply.Success);
        Assert.Contains("d__13", withoutReply.Error);

        var context = new Cybersole.Stores.Flows.FlowContext();
        context.Session.Vars["saucony.threeDsReply"] = "{\\"redirectUrl\\":\\"https://acs.example/r\\"}";
        var withRedirect = flow.PayerAuthenticate(context);

        Assert.True(withRedirect.Ok || withRedirect.Success);
        Assert.Equal("Redirect", context.Session.Vars["saucony.threeDsShape"]);
        Assert.Equal("https://acs.example/r", context.Session.Vars["saucony.threeDsUrl"]);
    }

    /// <summary>A reply with neither url gets the handler's own words, not a generic failure.</summary>
    [Fact]
    public void AnUnexpectedReplyUsesTheHandlersSentence()
    {
        var flow = new SauconyFlow();
        var context = new Cybersole.Stores.Flows.FlowContext();
        context.Session.Vars["saucony.threeDsReply"] = "{\\"error\\":\\"declined\\"}";

        var outcome = flow.PayerAuthenticate(context);

        Assert.False(outcome.Ok || outcome.Success);
        Assert.Equal("Unexpected 3DS response", outcome.Error);
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(TESTS, 'w', encoding='utf-8', newline='').write(text)
print('appended two behaviour tests')
