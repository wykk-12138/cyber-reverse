"""R1328: tests for the onboarding hop — present, skipped, and refusing on a bad reply."""

import io

PATH = 'replica/tests/Cybersole.Tests/WarhammerGraphQlTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'TheOnboardingHopRunsBeforeApproval' in text:
    raise SystemExit('tests already present')

block = '''
    /// <summary>
    /// R1328: when the run carries both address inputs, OnboardGuestMutation goes out before the approval and
    /// the reply is kept. The pair is the image's own: the onboarding takes the same token and the same
    /// addresses the approval takes, and the two documents are adjacent in its URL table.
    /// </summary>
    [Fact]
    public async Task TheOnboardingHopRunsBeforeApproval()
    {
        using var server = new TinyServer((_, body) =>
        {
            if (body.Contains("OnboardGuestMutation", StringComparison.Ordinal))
                return (200, "{\\"data\\":{\\"onboardGuest\\":{\\"buyer\\":{\\"userId\\":\\"u-1\\"}}}}");
            return (200, "{\\"data\\":{\\"approveGuestSignUpPayment\\":{\\"state\\":\\"COMPLETED\\"}}}");
        });
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["paymentToken"] = "tok-1";
        ctx.Session.Vars["wh.onboard.billing"] = "{\\"line1\\":\\"1 Main St\\",\\"city\\":\\"Austin\\"}";
        ctx.Session.Vars["wh.onboard.shipping"] = "{\\"line1\\":\\"1 Main St\\",\\"city\\":\\"Austin\\"}";

        var outcome = await new WarhammerFlow().SubmitPaymentAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Equal("1", ctx.Session.Vars["wh.onboarded"]);
        Assert.Equal(2, server.Requests.Count);
        Assert.Contains("OnboardGuestMutation", server.Requests[0].Body!);
        Assert.Contains("ApproveOnboardPaymentMutation", server.Requests[1].Body!);
        // The document that goes out is the one the image holds, not a re-typed copy.
        Assert.Contains(WarhammerQueries.OnboardGuestMutation.Substring(0, 60), server.Requests[0].Body!);
    }

    /// <summary>
    /// Without the two address inputs the hop is skipped and says so, and the approval still goes out — which
    /// is exactly what this flow did before the hop existed. Silence is what the skip must not be.
    /// </summary>
    [Fact]
    public async Task WithoutAddressInputsTheHopIsSkippedAndAnnounced()
    {
        using var server = new TinyServer((_, _) =>
            (200, "{\\"data\\":{\\"approveGuestSignUpPayment\\":{\\"state\\":\\"COMPLETED\\"}}}"));
        using var http = new NetClient { Transport = TransportMode.SChannel };
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/" };
        ctx.Session.Vars["paymentToken"] = "tok-1";

        var outcome = await new WarhammerFlow().SubmitPaymentAsync(ctx, default);

        Assert.True(outcome.Ok, outcome.Error);
        Assert.Single(server.Requests);
        Assert.Equal("1", ctx.Session.Vars["wh.onboardSkipped"]);
        Assert.Contains(ctx.Events, e => e.Name.Contains("OnboardGuestMutation did not run"));
        Assert.False(ctx.Session.Vars.ContainsKey("wh.onboarded"));
    }

    /// <summary>The onboarding document itself, pinned at the length the image carries.</summary>
    [Fact]
    public void TheOnboardingDocumentIsTheStringTheImageHolds()
    {
        Assert.Equal(3104, WarhammerQueries.OnboardGuestMutation.Length);
        Assert.StartsWith("mutation OnboardGuestMutation($bank: BankAccountInput", WarhammerQueries.OnboardGuestMutation);
        Assert.Contains("onboardAccount: onboardGuest(", WarhammerQueries.OnboardGuestMutation);
        Assert.EndsWith("__typename\\n}\\n", WarhammerQueries.OnboardGuestMutation);
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('appended the onboarding tests')
