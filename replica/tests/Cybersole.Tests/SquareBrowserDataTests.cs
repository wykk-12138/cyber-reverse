using System;
using System.Linq;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1310: Square's device fingerprint, reproduced from the image rather than retyped.
///
/// <para>
/// The template is 1124 bytes and the second copy in the image is 1102, which is exactly the first minus
/// <c>"user_agent":"__UA__",</c>. That is the relationship these cases pin: not "a fingerprint exists" but
/// "dropping that one member from this string yields the other object the image stores". If a future edit
/// changes a font name or a resolution, the length and the member difference both go red.
/// </para>
/// </summary>
public sealed class SquareBrowserDataTests
{
    private static readonly string UserAgentMember = "\"user_agent\":\"__UA__\",";

    [Fact]
    public void TheTemplateIsTheBytesTheImageHolds()
    {
        Assert.Equal(1124, SquareBrowserData.Template.Length);
        Assert.Contains(SquareBrowserData.UserAgentPlaceholder, SquareBrowserData.Template);
        Assert.StartsWith("{\"user_agent\":\"__UA__\",\"language\":\"en-US\"", SquareBrowserData.Template);
        Assert.EndsWith("]}", SquareBrowserData.Template);
    }

    [Fact]
    public void DroppingTheUserAgentMemberGivesTheSansUaCopy()
    {
        var sans = SquareBrowserData.WithoutUserAgent();

        Assert.Equal(1102, sans.Length);
        Assert.Equal(22, SquareBrowserData.Template.Length - sans.Length);
        Assert.Equal(SquareBrowserData.Template.Replace(UserAgentMember, string.Empty, StringComparison.Ordinal), sans);
        Assert.Contains("\"user_agent\"", SquareBrowserData.Template);
        Assert.DoesNotContain("user_agent", sans);
    }

    [Fact]
    public void TheTwoCopiesDifferInExactlyOneMember()
    {
        var full = JObject.Parse(SquareBrowserData.Template);
        var sans = JObject.Parse(SquareBrowserData.WithoutUserAgent());

        Assert.Equal(10, full.Count);
        Assert.Equal(9, sans.Count);
        Assert.Equal(new[] { "user_agent" }, full.Properties().Select(p => p.Name).Except(sans.Properties().Select(p => p.Name)));

        foreach (var member in sans.Properties())
            Assert.Equal(full[member.Name]!.ToString(), member.Value.ToString());
    }

    [Fact]
    public void TheRecordedDeviceIsTheStoresNotTheCallers()
    {
        var data = JObject.Parse(SquareBrowserData.Template);

        Assert.Equal(5120, data["resolution"]![0]!.Value<int>());
        Assert.Equal(1440, data["resolution"]![1]!.Value<int>());
        Assert.Equal(5120, data["available_resolution"]![0]!.Value<int>());
        Assert.Equal(1392, data["available_resolution"]![1]!.Value<int>());
        Assert.Equal(-120, data["timezone_offset"]!.Value<int>());
        Assert.Equal("Win32", data["navigator_platform"]!.Value<string>());
        Assert.Equal(5, data["regular_plugins"]!.Count());
        Assert.Equal(35, data["js_fonts"]!.Count());
        Assert.False(data["adblock"]!.Value<bool>());
        Assert.Equal(3, data["touch_support"]!.Count());
        Assert.Equal(10, data["touch_support"]![0]!.Value<int>());
        Assert.Equal("Arial", data["js_fonts"]![0]!.Value<string>());
        Assert.Equal("Wingdings 3", data["js_fonts"]![34]!.Value<string>());
    }

    [Fact]
    public void TheRecordedSummaryMatchesTheTemplate()
    {
        var data = JObject.Parse(SquareBrowserData.Template);

        // JArray.ToString() renders across lines, so the widths are read off the elements rather than
        // massaged out of the array's text.
        Assert.Equal(
            $"{data["resolution"]![0]!.Value<int>()}x{data["resolution"]![1]!.Value<int>()}",
            SquareBrowserData.Recorded["resolution"]);
        Assert.Equal(data["timezone_offset"]!.ToString(), SquareBrowserData.Recorded["timezone_offset"]);
        Assert.Equal(data["js_fonts"]!.Count().ToString(), SquareBrowserData.Recorded["fonts"]);
        Assert.Equal(data["regular_plugins"]!.Count().ToString(), SquareBrowserData.Recorded["plugins"]);
    }

    [Fact]
    public void TheStoreConstantsAreTheOnesInTheImage()
    {
        Assert.Equal("1.83.9", SquareBrowserData.SdkVersion);
        Assert.Equal("ComponentsV1", SquareBrowserData.ComponentSet);
        Assert.Equal("L0NR598Z0FFW5", SquareBrowserData.DefaultLocationId);
    }

    [Fact]
    public void AnAgentStringGoesIntoThePlaceholderAndTheResultStillParses()
    {
        const string agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36";

        var built = SquareBrowserData.Build(agent);

        Assert.DoesNotContain(SquareBrowserData.UserAgentPlaceholder, built);
        Assert.Equal(agent, JObject.Parse(built)["user_agent"]!.Value<string>());
        Assert.Equal(SquareBrowserData.Template.Length - 6 + agent.Length, built.Length);
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void NoAgentStringMeansTheSansUaCopy(string? agent)
    {
        Assert.Equal(SquareBrowserData.WithoutUserAgent(), SquareBrowserData.Build(agent));
    }

    /// <summary>
    /// An agent string containing a quote would otherwise end the JSON string early and produce a payload
    /// that no longer parses — which is worse than a rejected one, because it looks like it worked.
    /// </summary>
    [Fact]
    public void AQuoteInTheAgentStringCannotBreakTheJson()
    {
        var built = SquareBrowserData.Build("agent \"with\" quotes\\and a backslash");

        var parsed = JObject.Parse(built);
        Assert.Equal("agent \"with\" quotes\\and a backslash", parsed["user_agent"]!.Value<string>());
    }
}
