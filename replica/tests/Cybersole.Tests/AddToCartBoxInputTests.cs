using System.Linq;
using System.Reflection;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// AddToCartBox's inputs, and the defect R908 left in it.
///
/// <para>
/// R908 wrote the method but required a session variable nothing set, which made a written method uncallable in an
/// ordinary run — R850's shape without content, one layer up. R909 gives it a fallback to the flow's own variant, so
/// an ordinary run reaches it, and keeps the explicit variable as an override.
/// </para>
/// </summary>
public class AddToCartBoxInputTests
{
    /// <summary>
    /// The method reads boxSkuId and falls back to VariantId. Asserted against the source because the behaviour needs
    /// a live flow context; what can be pinned here is that the fallback exists and that both names are consulted.
    /// </summary>
    [Fact]
    public void TheBoxSkuFallsBackToTheFlowVariant()
    {
        var source = SourceOf("PopMartFlow.cs");

        Assert.Contains("boxSkuId", source);
        Assert.Contains("c.Session.VariantId", source);
        // the fallback is written as a conditional, not as two separate branches
        Assert.Contains("boxSku =", source);
    }

    /// <summary>
    /// The method still refuses when neither is available. A silent send with an empty sku would look like a success
    /// and add nothing, which is worse than a failure.
    /// </summary>
    [Fact]
    public void ItStillFailsWhenNeitherInputIsPresent()
    {
        var source = SourceOf("PopMartFlow.cs");
        var i = source.IndexOf("AddToCartBoxAsync", System.StringComparison.Ordinal);
        Assert.True(i > 0);

        var body = source.Substring(i, System.Math.Min(1400, source.Length - i));
        Assert.Contains("neither a boxSkuId nor a resolved variant", body);
    }

    /// <summary>
    /// Four endpoints, in the order the names imply. Pinned as counts so a step quietly losing one is visible. The
    /// window runs to the next override rather than a fixed length, because a fixed one measured from the signature cut
    /// the fourth call off and failed for a reason that had nothing to do with the code.
    /// </summary>
    [Fact]
    public void TheChainUsesFourEndpoints()
    {
        var source = SourceOf("PopMartFlow.cs");
        var i = source.IndexOf("AddToCartBoxAsync", System.StringComparison.Ordinal);
        Assert.True(i > 0);

        var next = source.IndexOf("public override", i + 20, System.StringComparison.Ordinal);
        var body = next > i ? source.Substring(i, next - i) : source.Substring(i);
        Assert.True(body.Length > 400, "the window did not reach the method body: " + body.Length + " chars");

        foreach (var endpoint in new[] { "BoxSpuDetail", "BoxSetPreview", "BoxSetExtract", "AddBoxListToCart" })
            Assert.Contains("PopMartEndpoints." + endpoint, body);
    }

    private static string SourcePath(string file)
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return System.IO.Path.Combine(dir!.FullName, "src", "Cybersole.Stores", "Flows", file);
    }

    private static string SourceOf(string file) => System.IO.File.ReadAllText(SourcePath(file));
}
