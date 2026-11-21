"""Give the PayPal order path a caller inside the store's own order step, then test it."""

import io

FLOWS = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
TESTS = 'replica/tests/Cybersole.Tests/HighsnobietyFlowTests.cs'

text = io.open(FLOWS, encoding='utf-8', newline='').read()
if 'highsnobiety.paypalOrder' not in text.replace('"highsnobiety.paypalOrder", "place the paypal order"', ''):
    # Insert the branch at the top of HighsnobietyFlow.SubmitOrderAsync.
    marker = '    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)\n    {'
    if text.count(marker) != 1:
        raise SystemExit('SubmitOrderAsync found %d times' % text.count(marker))

    branch = '''
        // R1356: PayPal's order path. The mutation is its own document and its handler distinguishes three
        // outcomes, so it is a branch rather than a value threaded through the GraphQL order below.
        if (!string.IsNullOrEmpty(c.Session.Vars.GetValueOrDefault("highsnobiety.paypalOrder")))
            return await SubmitPayPalOrderAsync(c, ct).ConfigureAwait(false);
'''
    text = text.replace(marker, marker + branch)
    io.open(FLOWS, 'w', encoding='utf-8', newline='').write(text)
    print('order step now branches to the PayPal path')

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
