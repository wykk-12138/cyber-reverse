"""Scope the edit to HighsnobietyFlow's own SubmitOrderAsync (the file has seven)."""

import io

FLOWS = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
TESTS = 'replica/tests/Cybersole.Tests/HighsnobietyFlowTests.cs'

text = io.open(FLOWS, encoding='utf-8', newline='').read()

class_start = text.find('class HighsnobietyFlow')
if class_start < 0:
    raise SystemExit('class not found')

branch_marker = 'highsnobiety.paypalOrder'
marker = 'public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)'
position = text.find(marker, class_start)
if position < 0:
    raise SystemExit('no SubmitOrderAsync inside the class')

body_start = text.find('{', position)
if body_start < 0:
    raise SystemExit('no body')

already = text[body_start:body_start + 400].count(branch_marker) > 0
if already:
    print('branch already present')
else:
    branch = '''
        // R1356: PayPal's order path. Its mutation is its own document and its handler distinguishes three
        // outcomes, so it is a branch rather than a value threaded through the GraphQL order below.
        if (!string.IsNullOrEmpty(c.Session.Vars.GetValueOrDefault("highsnobiety.paypalOrder")))
            return await SubmitPayPalOrderAsync(c, ct).ConfigureAwait(false);
'''
    text = text[:body_start + 1] + branch + text[body_start + 1:]
    io.open(FLOWS, 'w', encoding='utf-8', newline='').write(text)
    print('branch inserted inside HighsnobietyFlow.SubmitOrderAsync')

tests = io.open(TESTS, encoding='utf-8').read()
if 'ThePayPalOrderPathIsItsOwnStep' not in tests:
    block = '''
    /// <summary>
    /// R1356: placeOrderWithPaypal is the store's other order path. Its handler distinguishes three outcomes, and
    /// those are the messages the step reports rather than raw GraphQL text.
    /// </summary>
    [Fact]
    public void ThePayPalOrderPathIsItsOwnStep()
    {
        Assert.Equal(843, HighsnobietyFlow.PlaceOrderWithPaypalDocument.Length);
        Assert.StartsWith("query placeOrderWithPaypal($ddc: String!", HighsnobietyFlow.PlaceOrderWithPaypalDocument);
        Assert.Equal("Error submitting order", HighsnobietyFlow.ErrorSubmittingOrderMessage);
        Assert.Equal("Payment Declined", HighsnobietyFlow.PaymentDeclinedMessage);
        Assert.Equal("Your payment could not be processed", HighsnobietyFlow.PaymentNotProcessedMessage);
    }

    [Fact]
    public async Task WithoutAPayPalPayloadTheOrderStepSendsNothing()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var outcome = await new HighsnobietyFlow().SubmitPayPalOrderAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Empty(server.Requests);
    }

    /// <summary>A declined payment becomes the handler's own words, not the server's.</summary>
    [Fact]
    public async Task ADeclinedPaymentBecomesTheHandlersMessage()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\\"data\\":{\\"placeOrderWithPaypal\\":{\\"errors\\":[{\\"code\\":\\"PAYMENT_DECLINED\\"}]}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["highsnobiety.apiHost"] = server.BaseUrl + "/";
        ctx.Session.Vars["highsnobiety.paypalOrder"] = "{\\"ddc\\":\\"x\\"}";

        var outcome = await new HighsnobietyFlow().SubmitPayPalOrderAsync(ctx, default);

        Assert.False(outcome.Ok);
        Assert.Equal(HighsnobietyFlow.PaymentDeclinedMessage, outcome.Error);
    }
}
'''
    tests = tests.rstrip()
    tests = tests[:tests.rfind('}')].rstrip('\n') + '\n' + block
    io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
    print('appended three PayPal-order tests')
