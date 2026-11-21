"""Wire the Cybersource payment into a step (so it is not trimmed) and test it."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/CybersourcePaymentTests.cs'

text = io.open(FLOW, encoding='utf-8', newline='').read()
if 'CybersourcePayment' not in text:
    marker = 'public virtual async Task<StepOutcome> GetPaymentTokenAsync(FlowContext c, CancellationToken ct)'
    position = text.find(marker)
    if position < 0:
        raise SystemExit('GetPaymentTokenAsync not found')
    body = text.find('{', position)
    branch = '''
        // R1371: Cybersource's payment creation, when a run names the merchant endpoint. The endpoint and the capture
        // context are the run's; the image names the fields but never a host.
        var cybersourceEndpoint = c.Session.Vars.GetValueOrDefault("cybersource.endpoint");
        if (!string.IsNullOrEmpty(cybersourceEndpoint))
        {
            var customFields = Cybersole.Stores.Payments.CybersourcePayment.BuildCustomFields(
                c.Session.Vars.GetValueOrDefault("cybersource.paymentData"),
                c.Session.Vars.GetValueOrDefault("cybersource.store"),
                int.TryParse(c.Session.Vars.GetValueOrDefault("cybersource.screenHeight"), out var height) ? height : 0,
                int.TryParse(c.Session.Vars.GetValueOrDefault("cybersource.screenWidth"), out var width) ? width : 0,
                c.Session.Vars.GetValueOrDefault("cybersource.customerIp"));

            var paymentVariables = new Newtonsoft.Json.Linq.JObject
            {
                ["amount"] = new Newtonsoft.Json.Linq.JObject
                {
                    ["centAmount"] = long.TryParse(c.Session.Vars.GetValueOrDefault("cybersource.centAmount"),
                        out var cents) ? cents : 0,
                    ["currencyCode"] = c.Session.Vars.GetValueOrDefault("cybersource.currency") ?? "USD",
                },
                ["paymentMethod"] = Cybersole.Stores.Payments.CybersourcePayment.PayerAuthenticationMethod,
                ["customFields"] = customFields,
            };

            var (paymentData, paymentError) = await Cybersole.Stores.Payments.CybersourcePayment
                .CreateAsync(c, cybersourceEndpoint, paymentVariables, ct).ConfigureAwait(false);
            if (paymentData is null) return StepOutcome.Fail(paymentError);

            c.Session.Vars["cybersourcePayment"] =
                paymentData.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }
'''
    text = text[:body + 1] + branch + text[body + 1:]
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(text)
    print('branch inserted into GetPaymentTokenAsync')

tests = '''using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1371: Cybersource's request shape is recoverable from the handler even though its host is not. What is pinned here
/// is the field vocabulary, the refusal, and the reply key — not a merchant endpoint, which the image never names.
/// </summary>
public sealed class CybersourcePaymentTests
{
    [Fact]
    public void TheHandlerVocabularyIsTheObservedOne()
    {
        Assert.Equal("createMyPayment", CybersourcePayment.OperationName);
        Assert.Equal(493, CybersourcePayment.Document.Length);
        Assert.Equal("cybersource", CybersourcePayment.ProviderName);
        Assert.Equal("creditCardWithPayerAuthentication", CybersourcePayment.PayerAuthenticationMethod);
        Assert.Equal(new[] { "isv_payment_data", "isv_store", "isv_screenHeight", "isv_screenWidth",
                             "isv_customerIpAddress" }, CybersourcePayment.CustomFieldNames);
        Assert.Equal("No capture context", CybersourcePayment.NoCaptureContextMessage);
        Assert.Equal("Error processing payment", CybersourcePayment.ErrorProcessingPaymentMessage);
        Assert.Equal("isv_tokenCaptureContextSignature", CybersourcePayment.CaptureContextSignatureKey);
    }

    /// <summary>Empty values are dropped: the provider reads present-but-empty differently from absent.</summary>
    [Fact]
    public void EmptyFieldsAreDropped()
    {
        var fields = CybersourcePayment.BuildCustomFields("blob", "shop", 900, 1440, null);

        Assert.Equal("blob", fields["isv_payment_data"]!.ToObject<string>());
        Assert.Equal("shop", fields["isv_store"]!.ToObject<string>());
        Assert.Equal(900, fields["isv_screenHeight"]!.ToObject<int>());
        Assert.Equal(1440, fields["isv_screenWidth"]!.ToObject<int>());
        Assert.Null(fields["isv_customerIpAddress"]);
    }

    [Fact]
    public void TheEnvelopeCarriesOperationAndDocument()
    {
        var body = CybersourcePayment.Envelope(new JObject());
        Assert.Equal("createMyPayment", body["operationName"]!.ToObject<string>());
        Assert.Equal(CybersourcePayment.Document, body["query"]!.ToObject<string>());
    }
}
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)
