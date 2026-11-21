"""Wire the checkout card step in, and test it."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/CheckoutCreditCardTests.cs'

text = io.open(FLOW, encoding='utf-8', newline='').read()
if 'CheckoutCreditCard' in text:
    raise SystemExit('already wired')

marker = 'public virtual async Task<StepOutcome> SubmitCardAsync(FlowContext c, CancellationToken ct)'
position = text.find(marker)
if position < 0:
    raise SystemExit('SubmitCardAsync not found')

body = text.find('{', position)
branch = '''
        // R1368: the generic card finalisation, when a run names the checkout origin and the order id. Both are the
        // run's; the path shape (api/checkout/v1/orders/<id>/finalize) is the image's.
        var checkoutOrigin = c.Session.Vars.GetValueOrDefault("checkout.origin");
        var checkoutOrder = c.Session.Vars.GetValueOrDefault("checkout.orderId");
        if (!string.IsNullOrEmpty(checkoutOrigin) && !string.IsNullOrEmpty(checkoutOrder))
        {
            var card = new Newtonsoft.Json.Linq.JObject();
            foreach (var field in CheckoutCreditCard.CardFields)
            {
                var value = c.Session.Vars.GetValueOrDefault("checkout." + field);
                if (!string.IsNullOrEmpty(value)) card[field] = value;
            }

            if (card.Count == 0)
                return StepOutcome.Fail("checkout-card: no card fields in the session");

            var (cardData, cardError) = await CheckoutCreditCard
                .SubmitAsync(c, checkoutOrigin, checkoutOrder,
                    new Newtonsoft.Json.Linq.JObject { ["input"] = card }, ct)
                .ConfigureAwait(false);
            if (cardData is null) return StepOutcome.Fail(cardError);

            c.Session.Vars["checkoutResult"] = cardData.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }
'''
text = text[:body + 1] + branch + text[body + 1:]
io.open(FLOW, 'w', encoding='utf-8', newline='').write(text)
print('branch inserted into SubmitCardAsync')

tests = '''using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1368: CreditCard finalises an order at a relative path, so the order id travels as a path segment and the card
/// fields are the caller's. No card is a fixture here.
/// </summary>
public sealed class CheckoutCreditCardTests
{
    [Fact]
    public void ThePathAndCardFieldsAreTheObservedOnes()
    {
        Assert.Equal("CreditCard", CheckoutCreditCard.OperationName);
        Assert.Equal("api/checkout/v1/orders/", CheckoutCreditCard.OrderPathPrefix);
        Assert.Equal("/finalize", CheckoutCreditCard.FinalizeSuffix);
        Assert.Equal("Submit order", CheckoutCreditCard.SubmitOrderMessage);
        Assert.Equal(new[] { "cardNumber", "cardCvv", "cardExpiryMonth", "cardExpiryYear", "cardName" },
            CheckoutCreditCard.CardFields);
        Assert.Equal(2867, CheckoutCreditCard.Document.Length);
    }

    [Fact]
    public void TheUrlPutsTheOrderIdInThePath()
    {
        Assert.Equal("https://shop.test/api/checkout/v1/orders/o-1/finalize",
            CheckoutCreditCard.UrlFor("https://shop.test/", "o-1"));
    }

    [Fact]
    public void TheEnvelopeCarriesOperationAndDocument()
    {
        var body = CheckoutCreditCard.Envelope(new JObject());
        Assert.Equal("CreditCard", body["operationName"]!.ToObject<string>());
        Assert.Equal(CheckoutCreditCard.Document, body["query"]!.ToObject<string>());
    }
}
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)
