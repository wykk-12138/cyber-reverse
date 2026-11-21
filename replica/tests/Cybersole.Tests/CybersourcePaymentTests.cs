using Cybersole.Stores.Payments;
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
