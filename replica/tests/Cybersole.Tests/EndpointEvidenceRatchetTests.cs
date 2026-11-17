using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R293: the replica's API paths were compared against the image's string pool for the first time.
///
/// <para>
/// 89 api-like paths in <c>src/</c>; 44 appear verbatim in the image, 23 can be accounted for as a composition of parts
/// the image does carry (<c>/cart/add</c> etc.), and <b>22 have no evidence at all</b>. Those 22 are listed below with the
/// file that uses them. This test keeps the ledger honest in two directions: the list may not grow, and every entry must
/// still exist in its file — so removing an endpoint forces the list to be updated, and adding an unbacked one fails.
/// </para>
/// </summary>
public sealed class EndpointEvidenceRatchetTests
{
    private readonly ITestOutputHelper _out;
    public EndpointEvidenceRatchetTests(ITestOutputHelper output) => _out = output;

    /// <summary>Paths with no evidence in the image pool, and where they are used.</summary>
    /// <summary>Paths the code actually sends, with no pool evidence (R299 split).</summary>
    private static readonly (string Path, string File)[] Sent =
    {
        ("/account/recover", "src/Cybersole.Stores/Flows/StoreFlow.cs"),
        ("/account/verify", "src/Cybersole.Stores/Flows/MagentoFlow.cs"),
        ("/api/checkout/v1/basket/{basketId}", "src/Cybersole.Stores/Flows/FarfetchFlow.cs"),
        ("/api/checkout/v1/basket/{basketId}/place-order", "src/Cybersole.Stores/Flows/FarfetchFlow.cs"),
        ("/api/checkout/v1/basket/{basketId}/shipping", "src/Cybersole.Stores/Flows/FarfetchFlow.cs"),
        ("/api/preorder/entry", "src/Cybersole.Stores/Flows/RetailFlows.cs"),
        ("/api/stock", "src/Cybersole.Stores/Flows/PopMartEndpoints.cs"),
        ("/collections/new-releases", "src/Cybersole.Stores/Flows/MagentoFlow.cs"),
        ("/rest/V1/carts/mine/totals", "src/Cybersole.Stores/Flows/MagentoFlow.cs"),
        ("/v1/buys", "src/Cybersole.Stores/Flows/GoatFlow.cs"),

        // R1033: six paths the provenance tool counted that neither ledger held. None is new -- every one was already
        // being sent -- so they belong in Sent rather than in a third list. The literals are copied from the source,
        // not from the tool's display: R1032 recorded that display truncates a template to "{...}", and copying that
        // made StillInItsFile report the path missing.
        ("/api/ff-products/v1/products/{pid}/", "src/Cybersole.Stores/Flows/FarfetchFlow.cs"),
        ("/api/basket/v1/", "src/Cybersole.Stores/Flows/FarfetchFlow.cs"),
        ("/api/checkout/v1/basket/{basketId}/payment", "src/Cybersole.Stores/Flows/FarfetchFlow.cs"),
        ("https://api.nike.com/buy/carts/v2/{CountryCode}/Nike/SNKRS?format=simplified", "src/Cybersole.Stores/Flows/NikeFlow.cs"),
        ("/discount/", "src/Cybersole.Stores/Flows/StoreFlow.cs"),
        ("/api/payments/", "src/Cybersole.Stores/Flows/StoreFlow.cs"),
    };

    /// <summary>
    /// Paths that appear only in a doc comment — a claim about the store, not a request the replica makes. R299: this
    /// split matters, because "/api/beast" reads like an invented request and is in fact a documented observation.
    /// </summary>
    private static readonly (string Path, string File)[] DocumentedOnly =
    {
        ("/api/basket/v1/items", "src/Cybersole.Stores/Flows/FarfetchFlow.cs"),
        ("/api/beast", "src/Cybersole.Stores/Flows/BstnFlow.cs"),
        ("/api/checkout/submit", "src/Cybersole.Stores/Flows/RetailFlows.cs"),
        ("/api/order/submit", "src/Cybersole.Stores/Flows/PopMartEndpoints.cs"),
        ("/api/search", "src/Cybersole.Stores/Flows/ScheelsFlow.cs"),
        ("/api/v2/shop/countries", "src/Cybersole.Stores/Flows/HbxFlow.cs"),
        ("/view/resources/getUserInfo", "src/Cybersole.Stores/Flows/HybrisFlow.cs"),
    };

    // R1033: ten was the count when this ledger was written, not a limit on what the replica may send. Reconciling
    // against the provenance tool found six sent paths nobody had recorded, so the number moves to sixteen and the
    // guard keeps its actual job: catching a seventh.
    private const int SentCeiling = 16;
    private const int DocOnlyCeiling = 7;

    [Fact]
    public void NeitherListGrows()
    {
        _out.WriteLine($"sent={Sent.Length}/{SentCeiling} documented-only={DocumentedOnly.Length}/{DocOnlyCeiling}");
        Assert.True(Sent.Select(s => s.Path).Distinct().Count() <= SentCeiling);
        Assert.True(DocumentedOnly.Select(s => s.Path).Distinct().Count() <= DocOnlyCeiling);
    }

    [Fact]
    public void EveryUnbackedEndpointIsStillInItsFile()
    {
        var root = Root();
        foreach (var (path, file) in Sent.Concat(DocumentedOnly).Distinct())
        {
            var full = Path.Combine(root, file.Replace('/', Path.DirectorySeparatorChar));
            Assert.True(File.Exists(full), "file gone: " + file);
            var text = File.ReadAllText(full);
            Assert.Contains(path, text, StringComparison.Ordinal);
        }
    }


    [Fact]
    public void EveryUnbackedEndpointSaysSoOnItsOwnLine()
    {
        // R305 correction: the first version of this test only asked whether the FILE contained the marker, and a
        // mutation-check pass proved it decorative — GoatFlow.cs carries two markers (R294 and R298), so deleting one
        // left the other behind and the test stayed green. The binding is now per path: the marker must sit on a line
        // that also mentions that path.
        var root = Root();
        foreach (var (path, file) in Sent.Concat(DocumentedOnly).Distinct())
        {
            var full = Path.Combine(root, file.Replace('/', Path.DirectorySeparatorChar));
            var lines = File.ReadAllLines(full);
            // R305: "any line" was still too loose — GoatFlow sends /v1/buys from two places, and one marked line
            // satisfied the check for both. Every line that names an unbacked path now has to be marked.
            // R305: prose is allowed to discuss a path without a marker (BstnFlow's doc comment explains what a live
            // capture showed); what must be marked is every line that actually *uses* it.
            var users = lines.Where(l => l.Contains(path, StringComparison.Ordinal)
                                         && !l.TrimStart().StartsWith("//", StringComparison.Ordinal)).ToList();
            var unmarked = users.Where(l => !l.Contains("inferred: no image evidence", StringComparison.Ordinal)).ToList();

            _out.WriteLine($"{path} in {file}: {users.Count} line(s) use it, {unmarked.Count} unmarked");
            Assert.True(users.Count > 0, $"the path is gone from {file}: {path}");
            Assert.True(unmarked.Count == 0,
                $"unmarked use of {path} in {file}: " + string.Join(" | ", unmarked.Select(l => l.Trim())));
        }
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
