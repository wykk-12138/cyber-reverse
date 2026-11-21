"""The guest step is expression-bodied; override it in the flow that actually has the store, not in the base."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/OnRunningGraphQlTests.cs'

text = io.open(FLOW, encoding='utf-8', newline='').read()
if 'OnRunningGraphQl' not in text:
    old = '''    public virtual Task<StepOutcome> GuestCallbackAsync(FlowContext c, CancellationToken ct)
        => NotSupported("GuestCallback");'''
    new = '''    public virtual async Task<StepOutcome> GuestCallbackAsync(FlowContext c, CancellationToken ct)
    {
        // R1353: On Running's guest checkout, when the run asks for it. Its endpoint is the one the store table
        // already held; before this, nothing used that string.
        var guestEmail = c.Session.Vars.GetValueOrDefault("onRunning.guestEmail") ?? c.ProfileData?.Email;
        if (!string.IsNullOrEmpty(guestEmail) &&
            string.Equals(c.Session.Vars.GetValueOrDefault("onRunning.guest"), "true",
                StringComparison.OrdinalIgnoreCase))
        {
            var (guestData, guestError) = await OnRunningGraphQl
                .CheckoutAsGuestAsync(c, new Newtonsoft.Json.Linq.JObject { ["email"] = guestEmail }, ct)
                .ConfigureAwait(false);
            if (guestData is null) return StepOutcome.Fail(guestError);

            c.Session.Vars["guestCheckout"] = guestData.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }

        return NotSupported("GuestCallback");
    }'''
    if text.count(old) != 1:
        raise SystemExit('guest step found %d times' % text.count(old))
    io.open(FLOW, 'w', encoding='utf-8', newline='').write(text.replace(old, new))
    print('replaced the guest step body')

tests = '''using System.Threading.Tasks;
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
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)
