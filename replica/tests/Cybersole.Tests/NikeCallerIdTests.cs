using System.Collections.Generic;
using System.IO;
using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R202: the Nike caller id. R88 read the header names out of the image and left every value to the session — which
/// meant `nike-api-caller-id` was never sent once, because nothing ever seeded it.
/// </summary>
public sealed class NikeCallerIdTests
{
    private readonly ITestOutputHelper _out;
    public NikeCallerIdTests(ITestOutputHelper output) => _out = output;

    private static string Root()
    {
        var dir = new DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    private static string Pool() =>
        File.ReadAllText(Path.Combine(Path.GetDirectoryName(Root())!, "analysis", "pe_strings.txt"));

    [Fact]
    public void TheCallerIdsAreInTheImageAtTheirAddresses()
    {
        var pool = Pool();
        foreach (var id in NikeHeaders.CallerIds)
        {
            var needle = id.Address + "  " + id.Id;
            Assert.True(pool.Contains(needle, System.StringComparison.Ordinal),
                $"{id.Id} is not at {id.Address}");
        }

        Assert.Equal(4, NikeHeaders.CallerIds.Count);
        Assert.Equal(3, NikeHeaders.CallerIds.Count(c => !c.Id.Contains(':')));   // three bare ids, one composed
        Assert.Equal("com.nike.commerce.checkout.web", NikeHeaders.WebCallerId);
    }

    [Fact]
    public void TheComposedFormatIsTheImagesOwn()
    {
        // the image's single composed value pins the format; reproducing it byte for byte is the test
        Assert.Equal(NikeHeaders.IosComposedExample,
            NikeHeaders.ComposeCallerId("com.nike.commerce.omega.ios", "ios", "26.8"));

        Assert.True(Pool().Contains("0x07100354  " + NikeHeaders.IosComposedExample, System.StringComparison.Ordinal));

        // the Android build marks itself differently, and that marker is a literal too
        Assert.True(Pool().Contains("0x07100454  " + NikeHeaders.AndroidMarker, System.StringComparison.Ordinal));
    }

    [Fact]
    public void AHeaderIsSentOnlyWhenItsValueIsKnown()
    {
        var headers = new Dictionary<string, string>(System.StringComparer.Ordinal);

        // nothing known: nothing sent, and the count says so rather than pretending
        Assert.Equal(0, NikeHeaders.Apply(new Dictionary<string, string>(), headers));
        Assert.Empty(headers);

        // one known value: exactly one header
        var vars = new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["nike.apiCallerId"] = NikeHeaders.WebCallerId,
            ["nike.uxId"] = "",                  // blank is not a value
            ["nike.visitId"] = "0192f0aa-7c4f",
        };
        Assert.Equal(2, NikeHeaders.Apply(vars, headers));
        Assert.Equal(NikeHeaders.WebCallerId, headers[NikeHeaders.ApiCallerId]);
        Assert.Equal("0192f0aa-7c4f", headers[NikeHeaders.VisitId]);
        Assert.False(headers.ContainsKey(NikeHeaders.UxId));
    }

    [Fact]
    public void TheFlowSeedsTheCallerIdAndAppliesTheTable()
    {
        var flow = File.ReadAllText(Path.Combine(Root(),
            "src", "Cybersole.Stores", "Flows", "NikeFlow.cs"));

        // the seed, and the call — the two halves that were both missing
        Assert.Contains("NikeHeaders.WebCallerId", flow, System.StringComparison.Ordinal);
        Assert.Contains("NikeHeaders.Apply(", flow, System.StringComparison.Ordinal);

        // and the flow must not claim to be the iOS app
        Assert.DoesNotContain("NikeHeaders.IosComposedExample", flow);
        Assert.DoesNotContain("CallerIds[3]", flow);
    }
}
