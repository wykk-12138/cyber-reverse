using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R784: Casio's identifier is <c>casioid</c>, and the pool is what settled it.
///
/// <para>
/// R783 declined to add <c>casioid</c> as a candidate for the cart line's identifier, on the reasoning that
/// <c>sku</c> was the safer, established concept and that a wrong identifier would fail silently. That reasoning
/// assumed the image knew about a Casio sku. It does not: <c>casio.{0,24}sku</c> and <c>casio_sku</c> both match
/// nothing, while <c>casioid</c> sits in the same configuration record as <c>casio_can_purchase</c> and
/// <c>casio_image_url</c>.
/// </para>
///
/// <para>
/// So the ordering flipped: the field the image uses comes first, and the replica's earlier regex stays as a
/// fallback. These tests pin the ordering rather than any claim about which identifier the live site wants, which
/// remains unknown.
/// </para>
/// </summary>
public class CasioIdentifierTests
{
    private readonly ITestOutputHelper _out;

    public CasioIdentifierTests(ITestOutputHelper output) => _out = output;

    private static string? Pick(string body)
    {
        var m = Regex.Match(body, @"""casioid""\s*:\s*""([^""]+)""");
        if (!m.Success) m = Regex.Match(body, @"""sku""\s*:\s*""([^""]+)""");
        var value = m.Success ? m.Groups[1].Value : string.Empty;
        return value.Length > 0 ? value : null;
    }

    [Fact]
    public void CasioidWinsWhenBothArePresent()
    {
        const string body = """{"casioid":"A123","sku":"B456"}""";
        _out.WriteLine(body);
        Assert.Equal("A123", Pick(body));
    }

    [Fact]
    // Pages that carry only a sku must behave exactly as they did before this change.
    public void SkuStillWorksWhenCasioidIsAbsent()
    {
        Assert.Equal("B456", Pick("""{"sku":"B456"}"""));
    }

    [Fact]
    public void NeitherPresentIsNoIdentifier()
    {
        Assert.Null(Pick("""{"title":"G-Shock"}"""));
        Assert.Null(Pick(string.Empty));
    }

    [Fact]
    // The image's own field name, held to by a test so it cannot drift.
    public void TheFieldNameIsTheImages()
    {
        Assert.Equal("casio_can_purchase", Cybersole.Stores.Flows.CasioFlow.CanPurchaseField);
    }
}
