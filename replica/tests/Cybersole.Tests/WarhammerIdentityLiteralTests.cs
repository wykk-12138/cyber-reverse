using System;
using System.IO;
using System.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1035: the four Warhammer identity endpoints were built at run time as <c>IdentityHost + "/path"</c>, and the image
/// stores each of them as one complete string.
///
/// <para>
/// The provenance tool reported all four as unresolved, which read like missing evidence and was really a statement
/// about this file's shape: it could not see through a constant concatenation. Writing them out in full is the more
/// faithful form, because the artifact has one literal per endpoint and no composition -- so this guard pins the form
/// that matches the evidence rather than the form that happened to compile.
/// </para>
///
/// <para>
/// <c>IdentityHost</c> stays in the file for the two sites that really are assembled, <c>/api/me</c> and
/// <c>/api/v1/login</c>, which is why this guard names the four constants instead of banning the identifier.
/// </para>
/// </summary>
public sealed class WarhammerIdentityLiteralTests
{
    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    private static string Source() =>
        File.ReadAllText(Path.Combine(Root(), "src", "Cybersole.Stores", "Flows", "RetailFlows.cs"));

    /// <summary>Each of the four is a complete URL literal, as the image has it.</summary>
    [Theory]
    [InlineData("UsernamePasswordLogin", "https://login.mywarhammer.com/usernamepassword/login")]
    [InlineData("UsernamePasswordChallenge", "https://login.mywarhammer.com/usernamepassword/challenge")]
    [InlineData("OAuthToken", "https://login.mywarhammer.com/oauth/token")]
    [InlineData("LoginCallback", "https://login.mywarhammer.com/login/callback")]
    public void EachIsWrittenOutInFull(string name, string url)
    {
        var source = Source();
        var line = source.Split('\n').SingleOrDefault(l => l.Contains("const string " + name, StringComparison.Ordinal));

        Assert.NotNull(line);
        Assert.Contains("\"" + url + "\"", line, StringComparison.Ordinal);
        Assert.DoesNotContain("IdentityHost +", line!, StringComparison.Ordinal);
    }

    /// <summary>
    /// The host constant is still there, because two sites genuinely compose. A guard that banned it outright would be
    /// asserting something false about the file.
    /// </summary>
    [Fact]
    public void TheHostConstantStaysForTheAssembledSites()
    {
        Assert.Contains("IdentityHost", Source(), StringComparison.Ordinal);
    }
}
