using Cybersole.Stores.Flows;
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
