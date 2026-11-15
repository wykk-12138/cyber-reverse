using System;
using System.IO;
using System.Linq;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R298: third pass of the same audit, now on query parameter names.
///
/// <para>
/// 42 parameter names appear in <c>src/</c>; 38 are carried by the image's pool (as a bare string or as <c>name=</c>),
/// 4 are not: <c>json</c> (a captcha driver), <c>orderID</c> and <c>siteId</c> (Demandware) and <c>productTemplateId</c>
/// (GOAT, where it currently appears only in a doc claim). Two of them have weak support — the pool contains
/// <c>dwfrm_billing_paypal_paypalOrderID</c> and <c>get__siteId</c> — which is exactly the kind of near-miss that reads
/// as evidence when it is not.
/// </para>
/// </summary>
public sealed class QueryParamEvidenceRatchetTests
{
    private readonly ITestOutputHelper _out;
    public QueryParamEvidenceRatchetTests(ITestOutputHelper output) => _out = output;

    private static readonly (string Name, string File)[] Unbacked =
    {
        ("json=", "src/Cybersole.Services/Captcha/ThirdPartyDrivers.cs"),
        ("orderID=", "src/Cybersole.Stores/Flows/DemandwareFlow.cs"),
        ("siteId=", "src/Cybersole.Stores/Flows/DemandwareFlow.cs"),
        ("productTemplateId", "src/Cybersole.Stores/Flows/GoatFlow.cs"),
    };

    [Fact]
    public void TheUnbackedParamListDoesNotGrow()
    {
        _out.WriteLine($"unbacked params: {Unbacked.Length}");
        Assert.True(Unbacked.Length <= 4);
    }

    [Fact]
    public void EachOneIsStillUsedAndMarked()
    {
        var root = Root();
        foreach (var (name, file) in Unbacked)
        {
            var text = File.ReadAllText(Path.Combine(root, file.Replace('/', Path.DirectorySeparatorChar)));
            _out.WriteLine($"{name} in {file}: present={text.Contains(name, StringComparison.Ordinal)}");
            // R306: the R305 mutation pass proved that a file-level Contains is satisfied by any other marked line in
            // the same file. The binding is per line: every code line that names this one must carry the marker.
            var users = text.Split('\n')
                .Where(l => l.Contains(name, StringComparison.Ordinal)
                            && !l.TrimStart().StartsWith("//", StringComparison.Ordinal))
                .ToList();
            var unmarked = users.Where(l => !l.Contains("inferred: no image evidence", StringComparison.Ordinal)).ToList();
            _out.WriteLine($"{name}: {users.Count} code line(s), {unmarked.Count} unmarked");
            Assert.True(users.Count > 0, "the name is gone: " + name);
            Assert.True(unmarked.Count == 0, "unmarked use of " + name + ": " + string.Join(" | ", unmarked.Select(l => l.Trim())));
        }
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
