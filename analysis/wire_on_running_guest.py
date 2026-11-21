"""Wire the guest checkout into StoreFlow's guest step, and add its tests."""

import io

FLOW = 'replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/OnRunningGraphQlTests.cs'

text = io.open(FLOW, encoding='utf-8', newline='').read()
if 'OnRunningGraphQl' in text:
    raise SystemExit('already wired')

anchor = '    public virtual Task<StepOutcome> GuestCallbackAsync(FlowContext c, CancellationToken ct)'
if text.count(anchor) != 1:
    raise SystemExit('anchor found %d times' % text.count(anchor))

# Find the end of the guest step's body: the next virtual after the anchor.
following = text.find('    public virtual ', text.find(anchor) + len(anchor))
if following < 0:
    raise SystemExit('no following virtual')

body = text[text.find(anchor):following]
insert_at = body.rfind('    }')
if insert_at < 0:
    raise SystemExit('no body end')

branch = '''
        // R1353: On Running's guest checkout, when the run supplies an email for it. The store's endpoint is the
        // one its table already held; before this, nothing used it.
        var guestEmail = c.Session.Vars.GetValueOrDefault("onRunning.guestEmail")
                          ?? c.ProfileData?.Email;
        if (!string.IsNullOrEmpty(guestEmail) &&
            string.Equals(c.Session.Vars.GetValueOrDefault("onRunning.guest"), "true", StringComparison.OrdinalIgnoreCase))
        {
            var (guestData, guestError) = await OnRunningGraphQl
                .CheckoutAsGuestAsync(c, new Newtonsoft.Json.Linq.JObject { ["email"] = guestEmail }, ct)
                .ConfigureAwait(false);
            if (guestData is null) return StepOutcome.Fail(guestError);

            c.Session.Vars["guestCheckout"] = guestData.ToString(Newtonsoft.Json.Formatting.None);
            return StepOutcome.Success();
        }

'''

patched = body[:insert_at] + branch + body[insert_at:]
text = text[:text.find(anchor)] + patched + text[following:]
io.open(FLOW, 'w', encoding='utf-8', newline='').write(text)
print('wired the guest step')

tests = '''using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1353: On Running's guest checkout. Its endpoint was already in the store table as a string nothing used; the
/// document is the operation that uses it.
/// </summary>
public sealed class OnRunningGraphQlTests
{
    [Fact]
    public void TheUrlComesFromTheTableThatAlreadyHeldIt()
    {
        Assert.Equal("https://www.on.com/ko-kr/graphql", OnRunningGraphQl.Url);
        Assert.Equal(AccountAndAuthFamilies.OnRunning.GraphQl, AccountAndAuthFamilies.OnRunning.GraphQl);
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
