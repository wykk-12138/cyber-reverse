using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The captcha service the image names, and the not-ready answer that is not a failure.
///
/// <para>
/// R961. SolveCaptchaAsync was one of thirty-six steps returning Ok without doing anything. The image carries
/// api.solvecaptcha.com's two endpoints and three consecutive state machines, so the step now submits and polls. The
/// distinction the tests pin hardest is that CAPCHA_NOT_READY is the normal path: a solve that takes longer than one poll
/// must not be reported as a failure.
/// </para>
/// </summary>
public class SolveCaptchaServiceTests
{
    /// <summary>The two endpoints are the image's, verbatim.</summary>
    [Fact]
    public void TheEndpointsAreVerbatim()
    {
        Assert.Equal("https://api.solvecaptcha.com/in.php", SolveCaptchaService.SubmitUrl);
        Assert.Equal("https://api.solvecaptcha.com/res.php?key=", SolveCaptchaService.PollUrlPrefix);
    }

    /// <summary>A submission answer is an id, with or without the OK prefix, and anything else is a refusal.</summary>
    [Theory]
    [InlineData("12345", "12345")]
    [InlineData("OK|12345", "12345")]
    [InlineData("  OK|12345  ", "12345")]
    [InlineData("ERROR", null)]
    [InlineData("ERROR_WRONG_USER_KEY", null)]
    [InlineData("", null)]
    [InlineData(null, null)]
    public void TaskIdParsing(string? answer, string? expected)
    {
        Assert.Equal(expected, SolveCaptchaService.TaskIdFrom(answer));
    }

    /// <summary>Not-ready is its own kind, so the caller keeps waiting instead of failing.</summary>
    [Fact]
    public void NotReadyIsNotAFailure()
    {
        var poll = SolveCaptchaService.Poll("CAPCHA_NOT_READY");

        Assert.Equal(CaptchaPollKind.NotReady, poll.Kind);
        Assert.Null(poll.Token);
        Assert.NotEqual(CaptchaPollKind.Failed, poll.Kind);
    }

    /// <summary>A solved answer carries the token after the OK prefix.</summary>
    [Theory]
    [InlineData("OK|03AGdBq26abc", "03AGdBq26abc")]
    [InlineData("OK|  spaced  ", "spaced")]
    public void SolvedCarriesTheToken(string answer, string token)
    {
        var poll = SolveCaptchaService.Poll(answer);

        Assert.Equal(CaptchaPollKind.Solved, poll.Kind);
        Assert.Equal(token, poll.Token);
    }

    /// <summary>Refusals are failures, and an empty token after OK is one too.</summary>
    [Theory]
    [InlineData("ERROR_WRONG_KEY")]
    [InlineData("ERROR_ZERO_BALANCE")]
    [InlineData("OK|")]
    public void RefusalsFail(string? answer)
    {
        Assert.Equal(CaptchaPollKind.Failed, SolveCaptchaService.Poll(answer).Kind);
    }

    /// <summary>
    /// An empty answer is the transport failing, not the service refusing, so it stays NotReady. Failing it would let one
    /// network hiccup end a solve that the next poll would have finished -- and the loop already turns an unanswered
    /// deadline into a retryable failure, which is the right place for that verdict.
    /// </summary>
    [Theory]
    [InlineData("")]
    [InlineData(null)]
    public void AnEmptyAnswerIsTheTransportNotTheService(string? answer)
    {
        Assert.Equal(CaptchaPollKind.NotReady, SolveCaptchaService.Poll(answer).Kind);
    }

    /// <summary>
    /// The poll URL carries the key and the id, each escaped. A raw concatenation would break on the ampersands a key can
    /// contain.
    /// </summary>
    [Fact]
    public void ThePollUrlEscapesBothParts()
    {
        var url = SolveCaptchaService.PollUrl("key&with&amp", "id 7");

        Assert.StartsWith(SolveCaptchaService.PollUrlPrefix, url);
        Assert.Contains("&action=get&id=", url);
        Assert.DoesNotContain("key&with&amp&", url);
        Assert.Contains("key%26with%26amp", url);
        Assert.Contains("id%207", url);
    }

    /// <summary>The form carries the five documented fields, and the page URL is escaped rather than dropped.</summary>
    [Fact]
    public void TheFormIsBuiltFromFiveFields()
    {
        var form = SolveCaptchaService.SubmitForm("k", "userrecaptcha", "site", "https://a/b?c=1&d=2");

        Assert.Equal(5, form.Count);
        Assert.Equal("k", form["key"]);
        Assert.Equal("userrecaptcha", form["method"]);
        Assert.Equal("site", form["googlekey"]);
        Assert.Equal("https://a/b?c=1&d=2", form["pageurl"]);
        Assert.Equal("0", form["json"]);

        // SubmitFields is internal, so read it the way the other tests read internal members
        var fields = (string[])typeof(SolveCaptchaService)
            .GetField("SubmitFields", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)!
            .GetValue(null)!;
        Assert.Equal(fields.Length, form.Count);
    }

    /// <summary>The step no longer returns Ok without doing anything, and it uses this service.</summary>
    [Fact]
    public void TheStepUsesTheService()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.DoesNotContain("Task<StepOutcome> SolveCaptchaAsync(FlowContext c, CancellationToken ct) => Ok();", doc);
        Assert.Contains("SolveCaptchaService.SubmitUrl", doc);
        Assert.Contains("SolveCaptchaService.Poll(", doc);
        Assert.Contains("SolveCaptchaService.TaskIdFrom", doc);
    }

    /// <summary>And it writes the token where every captcha consumer in the flow already looks for it.</summary>
    [Fact]
    public void TheTokenLandsWhereConsumersLook()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.Contains("AntiBotTokens[\"g-recaptcha-response\"]", doc);
        Assert.Contains("captchaToken", doc);
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