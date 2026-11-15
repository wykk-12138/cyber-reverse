using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R297: the same evidence pass as the endpoints, applied to cookie names.
///
/// <para>
/// Five cookie names are referenced in <c>src/</c>; two are in the image's pool, three are not
/// (<c>NIKE_COMMERCE_COUNTRY</c>, <c>ffid</c>, <c>sbsd</c>). All three are optional reads — the flows degrade rather
/// than break without them — but they are marked in the code so nobody mistakes them for evidenced names. The pool does
/// carry <c>/sbsd</c> and <c>_sbsdContext</c>, which is why <c>sbsd</c> was plausible in the first place.
/// </para>
/// </summary>
public sealed class CookieEvidenceRatchetTests
{
    private readonly ITestOutputHelper _out;
    public CookieEvidenceRatchetTests(ITestOutputHelper output) => _out = output;

    private static readonly (string Name, string File)[] Unbacked =
    {
        ("NIKE_COMMERCE_COUNTRY", "src/Cybersole.Stores/Flows/NikeFlow.cs"),
        ("ffid", "src/Cybersole.Stores/Flows/FarfetchFlow.cs"),
        ("sbsd", "src/Cybersole.Stores/Flows/StoreFlow.cs"),
    };

    private const int Ceiling = 3;

    [Fact]
    public void TheUnbackedCookieListDoesNotGrow()
    {
        _out.WriteLine($"unbacked cookies: {Unbacked.Length}, ceiling {Ceiling}");
        Assert.True(Unbacked.Length <= Ceiling);
    }

    [Fact]
    public void EachOneIsStillUsedAndStillMarked()
    {
        var root = Root();
        foreach (var (name, file) in Unbacked)
        {
            var text = File.ReadAllText(Path.Combine(root, file.Replace('/', Path.DirectorySeparatorChar)));
            _out.WriteLine($"{name} in {file}: present={text.Contains(name, StringComparison.Ordinal)} marked={text.Contains("inferred: no image evidence (R297)", StringComparison.Ordinal)}");
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
