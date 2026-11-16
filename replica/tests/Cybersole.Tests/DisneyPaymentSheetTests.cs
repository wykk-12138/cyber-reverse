using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Disney's payment sheet: a card tokenised before a checkout, and two API versions kept apart.
///
/// <para>
/// R924. The card endpoint's name says token rather than pay, and it is separate from checkout, so the flow's card never
/// reaches the checkout call. That is implemented rather than described: one method accepts a card, and the checkout
/// method refuses without a token. The two versions -- v1 for checkout, v3 for process -- stay separate because merging
/// them would send one request where the original sends two.
/// </para>
/// </summary>
public class DisneyPaymentSheetTests
{
    private static string Const(string name) =>
        (string)typeof(DisneyPaymentSheet)
            .GetField(name, BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static)!
            .GetRawConstantValue()!;

    private static NetResponse Ok(string body) => new()
    {
        Url = new System.Uri("https://paymentsheet-ent.wdprapps.disney.com/api/v1/card/token"),
        StatusCode = 200,
        Body = body,
        Headers = new Dictionary<string, string>(),
    };

    /// <summary>Four addresses on two distinct hosts, and the two versions differ.</summary>
    [Fact]
    public void TheFourAddressesSpanTwoHostsAndTwoVersions()
    {
        Assert.Equal("https://paymentsheet-ent.wdprapps.disney.com", Const("SheetHost"));
        Assert.Equal("https://registerdisney.go.com", Const("GuestHost"));

        Assert.Equal("/api/v1/card/token", Const("CardToken"));
        Assert.Equal("/api/v1/checkout", Const("Checkout"));
        Assert.Equal("/api/v3/process", Const("Process"));
        Assert.Equal("/jgc/v8/client", Const("GuestClient"));

        Assert.Equal(4, (int)typeof(DisneyPaymentSheet)
            .GetField("RecoveredAddressCount", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetRawConstantValue()!);

        // checkout and process are different versions, and collapsing them would change one of the two calls
        Assert.Contains("/v1/", Const("Checkout"));
        Assert.Contains("/v3/", Const("Process"));
    }

    /// <summary>The token is recorded, and the raw body with it, since the shape is unknown.</summary>
    [Fact]
    public async Task TokenisingLeavesATokenInTheSession()
    {
        var session = new FlowSession { SessionId = "s" };
        string? seenUrl = null;
        string? seenBody = null;

        var outcome = await DisneyPaymentSheet.TokeniseCardAsync(session, "4111111111111111", "12/29", default,
            (url, body, tag, ct) =>
            {
                seenUrl = url;
                seenBody = body;
                return Task.FromResult<NetResponse?>(Ok("{\"cardToken\":\"tok-7\"}"));
            });

        Assert.True(outcome.Ok);
        Assert.Equal("https://paymentsheet-ent.wdprapps.disney.com/api/v1/card/token", seenUrl);
        Assert.Contains("4111111111111111", seenBody);
        Assert.Equal("tok-7", session.Vars["disney.cardToken"]);
        Assert.Equal("{\"cardToken\":\"tok-7\"}", session.Vars["disney.cardTokenBody"]);
    }

    /// <summary>
    /// The property the split exists for: checkout carries the token, never the card. Asserted on the body actually sent,
    /// because a test that only checked the session would pass even if the card were appended.
    /// </summary>
    [Fact]
    public async Task TheCheckoutCarriesTheTokenAndNotTheCard()
    {
        var session = new FlowSession { SessionId = "s" };
        session.Vars["disney.cardToken"] = "tok-7";

        string? seenBody = null;
        var outcome = await DisneyPaymentSheet.CheckoutAsync(session, default, (url, body, tag, ct) =>
        {
            seenBody = body;
            return Task.FromResult<NetResponse?>(Ok("{\"ok\":true}"));
        });

        Assert.True(outcome.Ok);
        Assert.Contains("tok-7", seenBody);
        Assert.DoesNotContain("4111", seenBody ?? "");
        Assert.DoesNotContain("cardNumber", seenBody ?? "");
    }

    /// <summary>A checkout without a token is refused before any request, since it would have to carry the card.</summary>
    [Fact]
    public async Task CheckoutWithoutATokenIsRefused()
    {
        var called = false;
        var outcome = await DisneyPaymentSheet.CheckoutAsync(new FlowSession { SessionId = "s" }, default,
            (url, body, tag, ct) =>
            {
                called = true;
                return Task.FromResult<NetResponse?>(null);
            });

        Assert.False(outcome.Ok);
        Assert.False(called);
        Assert.Contains("tokenise first", outcome.Error ?? "");
    }

    /// <summary>Processing needs a checkout first, and says so rather than sending an empty body.</summary>
    [Fact]
    public async Task ProcessWithoutACheckoutIsRefused()
    {
        var outcome = await DisneyPaymentSheet.ProcessAsync(new FlowSession { SessionId = "s" }, default,
            (url, body, tag, ct) => Task.FromResult<NetResponse?>(null));

        Assert.False(outcome.Ok);
        Assert.False(outcome.Retryable);
    }

    /// <summary>The three steps are recorded in the order the names imply.</summary>
    [Fact]
    public void TheStepOrderIsRecorded()
    {
        var order = (string[])typeof(DisneyPaymentSheet)
            .GetField("StepOrder", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

        Assert.Equal(new[] { "TokeniseCard", "Checkout", "Process" }, order);
    }

    /// <summary>The guest client is named but never called, and the class says so in a constant a test can read.</summary>
    [Fact]
    public void TheGuestClientIsRecordedButNotCalled()
    {
        var note = Const("GuestClientNote");
        Assert.Contains("never called", note);

        var source = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Payments", "DisneyPaymentSheet.cs"));
        // the constant is the only mention of the host beyond its declaration
        var occurrences = source.Split(new[] { "GuestHost + " }, System.StringSplitOptions.None).Length - 1;
        Assert.Equal(0, occurrences);
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}