using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Cybersole.Stores.Stores;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Global-e, the first vendor whose URL construction is fully recoverable.
///
/// <para>
/// R922. Four literals give two merchant identifiers, a template placeholder and a complete parameter set, so unlike
/// every vendor before it this one can be checked against the recovered string rather than only against its name.
/// The parameter order matters for that check, which is why it is recorded separately from the names.
/// </para>
/// </summary>
public class GlobalECheckoutTests
{
    private static string[] ParamOrder() =>
        (string[])typeof(GlobalECheckout)
            .GetField("ParamOrder", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

    private static string[] MerchantIds() =>
        (string[])typeof(GlobalECheckout)
            .GetField("RecoveredMerchantIds", BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

    /// <summary>
    /// The ten parameters in the recovered order. Ten is the count in the literal; an edit that adds or drops one
    /// changes the shape of a request the original makes.
    /// </summary>
    [Fact]
    public void TheParameterOrderIsTheRecoveredOne()
    {
        Assert.Equal(
            new[] { "gaSesID", "ga4SID", "chkcuid", "isNECAllowed", "_vwo_store", "vph", "vpw", "ift", "utm_source", "utm_medium" },
            ParamOrder());
    }

    /// <summary>Two merchants, both carried as literals, and neither is the template.</summary>
    [Fact]
    public void TwoMerchantIdentifiersAreRecorded()
    {
        Assert.Equal(new[] { "8x1r", "8um2" }, MerchantIds());
        Assert.DoesNotContain("{_encodedMerchantId}", MerchantIds());
    }

    /// <summary>
    /// A built URL has the recovered path shape and every parameter present, in order. The customer id in it is the
    /// sample from the literal, which is why this test is about shape rather than about a request being correct.
    /// </summary>
    [Fact]
    public void TheBuiltUrlHasEveryParameterInOrder()
    {
        var url = GlobalECheckout.UrlFor("8x1r");

        Assert.StartsWith("https://webservices.global-e.com/Checkout/v2/8x1r/641efc40-744a-443c-ad99-420a092c6644?", url);

        var query = url.Substring(url.IndexOf('?') + 1);
        var names = query.Split('&').Select(p => p.Split('=')[0]).ToArray();
        Assert.Equal(ParamOrder(), names);

        // with no values supplied every parameter is present and empty, which is what the literal shows for two of them
        Assert.Contains("_vwo_store=&", url);
        Assert.EndsWith("utm_medium=", url);
    }

    /// <summary>Values are escaped, so a customer id containing a reserved character cannot break the query.</summary>
    [Fact]
    public void ValuesAreEscaped()
    {
        var url = GlobalECheckout.UrlFor("8x1r", new Dictionary<string, string> { ["utm_source"] = "a&b=c" });
        Assert.Contains("utm_source=a%26b%3Dc", url);
    }

    /// <summary>A missing merchant is refused, because the path segment would otherwise be empty.</summary>
    [Fact]
    public void AMissingMerchantIsRefused()
    {
        Assert.Throws<System.ArgumentException>(() => GlobalECheckout.UrlFor("  "));
    }

    /// <summary>
    /// The non-EU judgement, which is inference and is tested as such: EU members are inside, and a country outside the
    /// set is not.
    /// </summary>
    [Theory]
    [InlineData("DE", false)]
    [InlineData("FR", false)]
    [InlineData("GB", false)]
    [InlineData("US", true)]
    [InlineData("JP", true)]
    [InlineData("", true)]
    public void TheNonEuJudgementIsTestedAsInference(string code, bool expected)
    {
        var m = typeof(GlobalECheckout).GetMethod("IsNonEu", BindingFlags.NonPublic | BindingFlags.Static)!;
        Assert.Equal(expected, (bool)m.Invoke(null, new object[] { code })!);
    }
}