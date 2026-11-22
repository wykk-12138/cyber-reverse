"""R1375: Saucony's payer step is a 3DS redirect, and the handler that proves it is small and complete.

sub_140A76F60 carries exactly nine literals: MD, SAUCONY-3DS, StatusInfo, "Unexpected 3DS response", error, jwt, red,
redirectUrl and stepUpUrl. That is a 3DS challenge answered one of two ways — a redirect url or a step-up url, with a
jwt alongside and the MD field 3DS uses — and a refusal for anything else.

SauconyFlow.PayerAuthenticate has been a NotCaptured placeholder whose message says "no literal in the image spells a
Saucony API path". That message is still true about the API paths, but it is no longer true about this step's
response: the step can classify what comes back and say the handler's own words when it is neither shape.

Usage: python analysis/add_saucony_three_ds.py
"""
import io

MODEL = 'replica/src/Cybersole.Stores/Flows/SauconyThreeDs.cs'
FLOW = 'replica/src/Cybersole.Stores/Flows/SauconyFlow.cs'
TESTS = 'replica/tests/Cybersole.Tests/SauconyThreeDsTests.cs'

model = '''using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Saucony's 3DS answer, as <c>sub_140A76F60</c> reads it.
///
/// <para>
/// <b>Observed</b> (R1375): that function's nine literals are <c>MD</c>, <c>SAUCONY-3DS</c>, <c>StatusInfo</c>,
/// "Unexpected 3DS response", <c>error</c>, <c>jwt</c>, <c>red</c>, <c>redirectUrl</c> and <c>stepUpUrl</c>. So a
/// reply carries one of two urls — a redirect or a step-up — with a jwt beside them and the MD field 3DS uses, and
/// anything else is answered with the handler's own sentence.
/// </para>
///
/// <para>
/// <b>Not observed:</b> the API paths the payer form posts to. This class therefore reads replies and never invents a
/// request.
/// </para>
/// </summary>
public static class SauconyThreeDs
{
    /// <summary>The step name the image carries.</summary>
    public const string StepName = "SAUCONY-3DS";

    /// <summary>The 3DS message field.</summary>
    public const string MdField = "MD";

    /// <summary>The token field.</summary>
    public const string JwtField = "jwt";

    /// <summary>The redirect field.</summary>
    public const string RedirectUrlField = "redirectUrl";

    /// <summary>The step-up field.</summary>
    public const string StepUpUrlField = "stepUpUrl";

    /// <summary>The handler's words when the reply is neither shape.</summary>
    public const string UnexpectedResponseMessage = "Unexpected 3DS response";

    /// <summary>What a reply turned out to be.</summary>
    public enum Shape
    {
        /// <summary>A redirect to follow.</summary>
        Redirect,

        /// <summary>A step-up challenge to answer.</summary>
        StepUp,

        /// <summary>Neither shape — the handler's own refusal.</summary>
        Unexpected,
    }

    /// <summary>
    /// Classify a reply. The redirect is checked first: when a reply carries both, following it is what the browser
    /// would do, and the step-up url is then redundant rather than competing.
    /// </summary>
    public static (Shape Shape, string? Url, string? Jwt) Classify(JObject? reply)
    {
        if (reply is null) return (Shape.Unexpected, null, null);

        var source = reply["data"] as JObject ?? reply;
        var jwt = source[JwtField]?.ToString();

        var redirect = source[RedirectUrlField]?.ToString();
        if (!string.IsNullOrEmpty(redirect)) return (Shape.Redirect, redirect, jwt);

        var stepUp = source[StepUpUrlField]?.ToString();
        if (!string.IsNullOrEmpty(stepUp)) return (Shape.StepUp, stepUp, jwt);

        return (Shape.Unexpected, null, jwt);
    }
}
'''

io.open(MODEL, 'w', encoding='utf-8', newline='').write(model)
print('wrote %s' % MODEL)

flow = io.open(FLOW, encoding='utf-8', newline='').read()

old = '''    public StepOutcome PayerAuthenticate(FlowContext c) => NotCaptured("PayerAuthenticate", "d__13");'''
new = '''    public StepOutcome PayerAuthenticate(FlowContext c)
    {
        // R1375: the reply can be read even though the request cannot be built. A run supplies what came back; this
        // classifies it the way sub_140A76F60 does and keeps the handler's own sentence for anything else.
        var replyText = c.Session.Vars.GetValueOrDefault("saucony.threeDsReply");
        if (string.IsNullOrWhiteSpace(replyText)) return NotCaptured("PayerAuthenticate", "d__13");

        Newtonsoft.Json.Linq.JObject reply;
        try
        {
            reply = Newtonsoft.Json.Linq.JObject.Parse(replyText!);
        }
        catch (Newtonsoft.Json.JsonException)
        {
            return StepOutcome.Fail("saucony: saucony.threeDsReply is not valid JSON", retryable: false);
        }

        var (shape, url, jwt) = SauconyThreeDs.Classify(reply);
        c.Session.Vars["saucony.threeDsShape"] = shape.ToString();
        if (!string.IsNullOrEmpty(url)) c.Session.Vars["saucony.threeDsUrl"] = url;
        if (!string.IsNullOrEmpty(jwt)) c.Session.Vars["saucony.threeDsJwt"] = jwt;

        return shape == SauconyThreeDs.Shape.Unexpected
            ? StepOutcome.Fail(SauconyThreeDs.UnexpectedResponseMessage, retryable: false)
            : StepOutcome.Success();
    }'''

if old not in flow:
    raise SystemExit('PayerAuthenticate placeholder not found as written')
flow = flow.replace(old, new)
io.open(FLOW, 'w', encoding='utf-8', newline='').write(flow)
print('PayerAuthenticate now classifies the reply')

tests = '''using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1375: Saucony's 3DS reply has two shapes and a refusal, all four named by the image's own handler.
/// </summary>
public sealed class SauconyThreeDsTests
{
    [Fact]
    public void TheHandlerVocabularyIsTheObservedOne()
    {
        Assert.Equal("SAUCONY-3DS", SauconyThreeDs.StepName);
        Assert.Equal("MD", SauconyThreeDs.MdField);
        Assert.Equal("jwt", SauconyThreeDs.JwtField);
        Assert.Equal("redirectUrl", SauconyThreeDs.RedirectUrlField);
        Assert.Equal("stepUpUrl", SauconyThreeDs.StepUpUrlField);
        Assert.Equal("Unexpected 3DS response", SauconyThreeDs.UnexpectedResponseMessage);
    }

    [Fact]
    public void ARedirectReplyIsARedirect()
    {
        var (shape, url, jwt) = SauconyThreeDs.Classify(new JObject
        {
            ["redirectUrl"] = "https://acs.example/challenge",
            ["jwt"] = "token-1",
        });

        Assert.Equal(SauconyThreeDs.Shape.Redirect, shape);
        Assert.Equal("https://acs.example/challenge", url);
        Assert.Equal("token-1", jwt);
    }

    [Fact]
    public void AStepUpReplyIsAStepUp()
    {
        var (shape, url, _) = SauconyThreeDs.Classify(new JObject
        {
            ["stepUpUrl"] = "https://acs.example/stepup",
        });

        Assert.Equal(SauconyThreeDs.Shape.StepUp, shape);
        Assert.Equal("https://acs.example/stepup", url);
    }

    /// <summary>Both present: the redirect wins, because that is what a browser would follow.</summary>
    [Fact]
    public void TheRedirectWinsWhenBothArePresent()
    {
        var (shape, url, _) = SauconyThreeDs.Classify(new JObject
        {
            ["redirectUrl"] = "https://acs.example/r",
            ["stepUpUrl"] = "https://acs.example/s",
        });

        Assert.Equal(SauconyThreeDs.Shape.Redirect, shape);
        Assert.Equal("https://acs.example/r", url);
    }

    [Fact]
    public void AnythingElseIsTheHandlersRefusal()
    {
        var (shape, url, _) = SauconyThreeDs.Classify(new JObject { ["error"] = "declined" });

        Assert.Equal(SauconyThreeDs.Shape.Unexpected, shape);
        Assert.Null(url);
    }
}
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)
