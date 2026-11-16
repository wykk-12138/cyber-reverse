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
/// eShopWorld's hosted panel and its two polling loops.
///
/// <para>
/// R923. Five paths across two hosts, two of them state endpoints, which makes this vendor a wait rather than a call.
/// The poller is shared between the loops because writing it twice invites the copies to disagree about what counts as
/// done -- which is how a checkout completes on one path and hangs on the other. These tests pin the three outcomes and,
/// most of all, that unsettled is not failed.
/// </para>
/// </summary>
public class EshopWorldPanelTests
{
    private static string Const(string name) =>
        (string)typeof(EshopWorldPanel)
            .GetField(name, BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static)!
            .GetRawConstantValue()!;

    private static NetResponse Ok(string body) => new()
    {
        Url = new System.Uri("https://payments-panel.production.eshopworld.com/api/v2/WebComponent/state"),
        StatusCode = 200,
        Body = body,
        Headers = new Dictionary<string, string>(),
    };

    /// <summary>Two hosts, five paths, and the two hosts are distinct — the panel and the APM session do not share one.</summary>
    [Fact]
    public void TheFiveAddressesSpanTwoDistinctHosts()
    {
        Assert.Equal("https://payments-panel.production.eshopworld.com", Const("PanelHost"));
        Assert.Equal("https://retailer-shopifypayments-api.production.eshopworld.com", Const("ApmpHost"));
        Assert.NotEqual(Const("PanelHost"), Const("ApmpHost"));

        Assert.Equal("/api/v2/PaymentMethods/url", Const("MethodsUrl"));
        Assert.Equal("/api/v2/PaymentMethods?paymentId=", Const("MethodsByPayment"));
        Assert.Equal("/api/v2/WebComponent/state", Const("WebComponentState"));
        Assert.Equal("/api/v1/payment/apm/session/status", Const("ApmpStatus"));
        Assert.Equal("/api/v1/payment/apm/session/post_pay_status", Const("ApmpPostPayStatus"));

        Assert.Equal(5, (int)typeof(EshopWorldPanel)
            .GetField("RecoveredAddressCount", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetRawConstantValue()!);
    }

    /// <summary>Each loop polls its own host, so a flow with both cannot poll one and assume the other.</summary>
    [Fact]
    public void TheTwoLoopsPollDifferentHosts()
    {
        var web = EshopWorldPanel.StateUrl(EshopWorldPanel.Loop.WebComponent, "p1");
        var apm = EshopWorldPanel.StateUrl(EshopWorldPanel.Loop.Apmp, "p1");

        Assert.StartsWith("https://payments-panel.production.eshopworld.com/", web);
        Assert.StartsWith("https://retailer-shopifypayments-api.production.eshopworld.com/", apm);
        Assert.NotEqual(web, apm);
    }

    /// <summary>A settled-success body ends the poll as a success.</summary>
    [Fact]
    public async Task ASuccessStateEndsThePoll()
    {
        var session = new FlowSession { SessionId = "s" };
        var outcome = await EshopWorldPanel.PollAsync(session, EshopWorldPanel.Loop.WebComponent, "p1", default,
            (u, ct) => Task.FromResult<NetResponse?>(Ok("{\"status\":\"completed\"}")), attempts: 3, intervalMs: 0);

        Assert.True(outcome.Ok);
        Assert.Equal("done", session.Vars["eshopworld.settled"]);
    }

    /// <summary>A settled-failure body ends the poll as a failure, and does not retry.</summary>
    [Fact]
    public async Task AFailureStateEndsThePollWithoutRetrying()
    {
        var session = new FlowSession { SessionId = "s" };
        var calls = 0;

        var outcome = await EshopWorldPanel.PollAsync(session, EshopWorldPanel.Loop.Apmp, "p1", default, (u, ct) =>
        {
            calls++;
            return Task.FromResult<NetResponse?>(Ok("{\"state\":\"declined\"}"));
        }, attempts: 5, intervalMs: 0);

        Assert.False(outcome.Ok);
        Assert.Equal(1, calls);
        Assert.Equal("failed", session.Vars["eshopworld.settled"]);
    }

    /// <summary>
    /// The case the shared poller exists for: an unsettled body keeps waiting, then reports unknown rather than failed.
    /// A slow gateway must not look like a declined card.
    /// </summary>
    [Fact]
    public async Task AnUnsettledBodyKeepsWaitingThenReportsUnknown()
    {
        var session = new FlowSession { SessionId = "s" };
        var calls = 0;

        var outcome = await EshopWorldPanel.PollAsync(session, EshopWorldPanel.Loop.WebComponent, "p1", default, (u, ct) =>
        {
            calls++;
            return Task.FromResult<NetResponse?>(Ok("{\"status\":\"pending\"}"));
        }, attempts: 4, intervalMs: 0);

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
        Assert.Equal(4, calls);
        Assert.Equal("unknown", session.Vars["eshopworld.settled"]);
    }

    /// <summary>
    /// An unknown word is not terminal: a guess at a failure word would abandon a payment about to succeed, so only the
    /// listed words end a poll and everything else waits.
    /// </summary>
    [Theory]
    [InlineData("{\"status\":\"completed\"}", "completed")]
    [InlineData("{\"state\":\"declined\"}", "declined")]
    [InlineData("{\"paymentStatus\":\"authorized\"}", "authorized")]
    [InlineData("{\"status\":\"halfway\"}", null)]
    [InlineData("{\"note\":\"completed\"}", null)]
    [InlineData("", null)]
    public void OnlyAListedWordInAStateFieldIsTerminal(string body, string? expected)
    {
        var m = typeof(EshopWorldPanel).GetMethod("StateWord",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)!;
        Assert.Equal(expected, (string?)m.Invoke(null, new object?[] { body }));
    }

    /// <summary>An unreachable endpoint is not a failed payment: it retries through the window, then says so.</summary>
    [Fact]
    public async Task AnUnreachableEndpointRetriesThenSaysSo()
    {
        var session = new FlowSession { SessionId = "s" };
        var calls = 0;

        var outcome = await EshopWorldPanel.PollAsync(session, EshopWorldPanel.Loop.Apmp, "p1", default, (u, ct) =>
        {
            calls++;
            return Task.FromResult<NetResponse?>(null);
        }, attempts: 3, intervalMs: 0);

        Assert.False(outcome.Ok);
        Assert.True(outcome.Retryable);
        Assert.Equal(3, calls);
        Assert.False(session.Vars.ContainsKey("eshopworld.settled"));
    }

    /// <summary>A missing id is refused before any request.</summary>
    [Fact]
    public async Task AMissingIdIsRefused()
    {
        var called = false;
        var outcome = await EshopWorldPanel.PollAsync(new FlowSession { SessionId = "s" },
            EshopWorldPanel.Loop.WebComponent, " ", default, (u, ct) =>
            {
                called = true;
                return Task.FromResult<NetResponse?>(null);
            });

        Assert.False(outcome.Ok);
        Assert.False(called);
    }
}