using System.Linq;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1335: the PayPal partner approval, whose document, endpoint and variable names all come from one sender in
/// the image — sub_14110C600 — so none of it is invented.
/// </summary>
public sealed class PayPalPartnerApproveTests
{
    [Fact]
    public void TheEndpointIsTheObservedBasePlusTheObservedOperationName()
    {
        Assert.Equal("https://www.paypal.com/graphql/", PayPalPartnerApprove.BaseUrl);
        Assert.Equal("approveMemberPayment", PayPalPartnerApprove.OperationName);
        Assert.Equal("https://www.paypal.com/graphql/approveMemberPayment", PayPalPartnerApprove.Url);
        Assert.EndsWith("/", PayPalPartnerApprove.BaseUrl);
    }

    [Fact]
    public void TheDocumentIsTheStringTheImageHolds()
    {
        Assert.Equal(5407, PayPalPartnerApprove.Document.Length);
        Assert.StartsWith("mutation approveMemberPayment($token: String!", PayPalPartnerApprove.Document);
        Assert.Contains("fragment ThreeDomainSecureFields on ThreeDomainSecureContingency", PayPalPartnerApprove.Document);
    }

    [Fact]
    public void TheElevenVariableNamesAreTheImageSpelling()
    {
        Assert.Equal(11, PayPalPartnerApprove.VariableNames.Length);
        foreach (var name in new[]
                 {
                     "token", "selectedAddressId", "preferredShippingAddressId", "selectedFundingOptionId",
                     "preferredFundingOptionId", "secondaryFundingOptionIds", "preAuthorizationRequired",
                     "fundingMethodType", "setStickyFiRequired", "scaCompleted", "experiences",
                 })
        {
            Assert.Contains(name, PayPalPartnerApprove.VariableNames);
            // Every one of them is a declared document variable, which is what makes the list checkable.
            Assert.Contains("$" + name, PayPalPartnerApprove.Document);
        }
    }

    [Fact]
    public void TheEnvelopeCarriesTheThreeObservedKeys()
    {
        var body = PayPalPartnerApprove.Envelope(new JObject { ["token"] = "t" });

        Assert.Equal("approveMemberPayment", body["operationName"]!.ToObject<string>());
        Assert.Equal(PayPalPartnerApprove.Document, body["query"]!.ToObject<string>());
        Assert.Equal("t", body["variables"]!["token"]!.ToObject<string>());
    }

    /// <summary>
    /// A tokenless approval is refused before any request: the approval is keyed by the buyer token, and a
    /// request without one cannot mean anything to the partner.
    /// </summary>
    [Fact]
    public async Task ATokenlessApprovalIsRefusedBeforeAnyRequest()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await PayPalPartnerApprove.ApproveAsync(ctx, new JObject(), default);

        Assert.Null(data);
        Assert.Contains("no token", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public async Task TheGatewayTakesThePartnerPathWhenATokenIsPresent()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\"data\":{\"approveMemberPayment\":{\"state\":\"COMPLETED\",\"cart\":{\"paymentId\":\"p-1\"}}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["paypal.partnerToken"] = "tok-1";
        ctx.Session.Vars["paypal.partnerApproveUrl"] = server.BaseUrl + "/graphql/approveMemberPayment";

        var gateway = new PayPalGateway();
        var result = await gateway.AuthorizeAsync(ctx, default);

        Assert.True(result.Ok, result.Error);
        Assert.Equal("COMPLETED", ctx.Session.Vars["paypal.approveState"]);
        var sent = JObject.Parse(server.Requests[0].Body!);
        Assert.Equal(PayPalPartnerApprove.Document, sent["query"]!.ToObject<string>());
        Assert.Equal("tok-1", sent["variables"]!["token"]!.ToObject<string>());
        Assert.Equal("IFRAME", sent["variables"]!["fundingMethodType"]!.ToObject<string>());
    }

    /// <summary>
    /// R1370: the two dialects differ by exactly one declared variable. A payment carrying an encrypted paycode needs
    /// the 5620-character document; everything else takes the 5407-character one. That is a condition on the payment,
    /// which the caller can see, not a per-store list this replica would have had to invent.
    /// </summary>
    [Fact]
    public void TheDialectFollowsThePaycode()
    {
        Assert.Equal(5407, PayPalPartnerApprove.Document.Length);
        Assert.Equal(5620, PayPalPartnerApprove.PaycodeDocument.Length);
        Assert.Equal("paycodeEncrypted", PayPalPartnerApprove.PaycodeVariableName);

        Assert.Same(PayPalPartnerApprove.Document, PayPalPartnerApprove.DocumentFor(false));
        Assert.Same(PayPalPartnerApprove.PaycodeDocument, PayPalPartnerApprove.DocumentFor(true));
    }

    /// <summary>
    /// The difference between the two documents is that one declared name, and nothing else. Comparing the declared
    /// sets says that directly; running string surgery on 3000 characters of GraphQL does not.
    /// </summary>
    [Fact]
    public void TheTwoDocumentsDifferByThatOneName()
    {
        static System.Collections.Generic.HashSet<string> Declared(string document) =>
            new(System.Text.RegularExpressions.Regex.Matches(document, @"\$(\w+)\s*:")
                .Select(m => m.Groups[1].Value));

        var shortSet = Declared(PayPalPartnerApprove.Document);
        var longSet = Declared(PayPalPartnerApprove.PaycodeDocument);

        var onlyInLong = new System.Collections.Generic.HashSet<string>(longSet);
        onlyInLong.ExceptWith(shortSet);
        var onlyInShort = new System.Collections.Generic.HashSet<string>(shortSet);
        onlyInShort.ExceptWith(longSet);

        Assert.Equal(new[] { "paycodeEncrypted" }, System.Linq.Enumerable.OrderBy(onlyInLong, name => name));
        Assert.Empty(onlyInShort);
        Assert.Equal(15, shortSet.Count);
        Assert.Equal(16, longSet.Count);
    }

    /// <summary>The envelope picks the document from the variables it is given.</summary>
    [Fact]
    public void TheEnvelopePicksTheDocumentFromTheVariables()
    {
        var without = PayPalPartnerApprove.EnvelopeFor(new JObject { ["token"] = "t" });
        var with = PayPalPartnerApprove.EnvelopeFor(
            new JObject { ["token"] = "t", ["paycodeEncrypted"] = "enc" });

        Assert.Equal(PayPalPartnerApprove.Document, without["query"]!.ToObject<string>());
        Assert.Equal(PayPalPartnerApprove.PaycodeDocument, with["query"]!.ToObject<string>());
        Assert.Equal("approveMemberPayment", with["operationName"]!.ToObject<string>());
    }
}
