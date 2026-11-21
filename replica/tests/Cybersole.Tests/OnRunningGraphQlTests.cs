using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1353: On Running's guest checkout. The endpoint was already in the store table as a string nothing used; the
/// document is the operation that uses it.
/// </summary>
public sealed class OnRunningGraphQlTests
{
    [Fact]
    public void TheUrlComesFromTheTableThatAlreadyHeldIt()
    {
        Assert.Equal("https://www.on.com/ko-kr/graphql", OnRunningGraphQl.Url);
        Assert.Contains(AccountAndAuthFamilies.OnRunning.GraphQl, OnRunningGraphQl.Url);
        Assert.EndsWith("/graphql", OnRunningGraphQl.Url);
    }

    [Fact]
    public void TheDocumentIsTheMeasuredString()
    {
        Assert.Equal(148, OnRunningGraphQl.Document.Length);
        Assert.StartsWith("mutation checkoutAsGuest($email: String!)", OnRunningGraphQl.Document);
        Assert.Equal(new[] { "email" }, OnRunningGraphQl.DeclaredVariables);
    }

    [Fact]
    public async Task WithoutAnEmailNothingIsSent()
    {
        using var server = new TinyServer((_, _) => (200, "{}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };

        var (data, error) = await OnRunningGraphQl.CheckoutAsGuestAsync(ctx, new JObject(), default);

        Assert.Null(data);
        Assert.Contains("no email", error);
        Assert.Empty(server.Requests);
    }

    [Fact]
    public void TheEnvelopeCarriesTheOperationAndDocument()
    {
        var body = OnRunningGraphQl.Envelope(new JObject { ["email"] = "a@b.test" });
        Assert.Equal("checkoutAsGuest", body["operationName"]!.ToObject<string>());
        Assert.Equal(OnRunningGraphQl.Document, body["query"]!.ToObject<string>());
        Assert.Equal("a@b.test", body["variables"]!["email"]!.ToObject<string>());
    }
}
