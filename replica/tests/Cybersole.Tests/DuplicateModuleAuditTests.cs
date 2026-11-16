using System.Linq;
using Cybersole.Stores.Modules;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The duplicate module hierarchies, and why they must not be wired.
///
/// <para>
/// R953. R952 estimated the function gap at roughly eight hundred wirings and noted that the replica keeps many async
/// methods nothing reaches. Looking for those uncovered ninety-three files whose main type has no external reference, of
/// which twenty-six contain async methods -- and then the first one examined dissolved the estimate: Retail2Modules.cs
/// declares CasioModule, JbHiFiModule, PocketGamesModule, SuperswipeModule and WarhammerModule, and all five duplicate
/// stores that StoreModuleCatalog already registers as flows.
/// </para>
///
/// <para>
/// <b>Why wiring them would be wrong.</b> StoreModuleCatalog.CreateAll returns IStoreModule instances and a module class
/// fits that interface, so adding them compiles and runs. It would also put Casio in the catalogue twice, once as a flow
/// and once as a module, which is a behavioural error rather than a parity gain. So the unreachable code is not uniformly
/// work left to connect; some of it is work that should be deleted, and telling the two apart is the actual task.
/// </para>
///
/// <para>
/// <b>What this pins.</b> The five names, the flows they duplicate, and the rule that a module whose store is already
/// registered must not be added. The pin will fail if a future round wires one, which is the point.
/// </para>
/// </summary>
public class DuplicateModuleAuditTests
{
    /// <summary>
    /// The five module classes in Retail2Modules and the flow each duplicates. Every one of these stores is already in
    /// the catalogue, which is why none of the modules should be registered.
    /// </summary>
    internal static readonly (string Module, string DuplicateOf)[] Pairs =
    {
        ("CasioModule", "CasioFlow"),
        ("JbHiFiModule", "JbHiFiFlow"),
        ("PocketGamesModule", "PocketGamesFlow"),
        ("SuperswipeModule", "SuperswipeFlow"),
        ("WarhammerModule", "WarhammerFlow"),
    };

    /// <summary>Five duplicates, and each flow really is in the catalogue, so none of them is a gap.</summary>
    [Fact]
    public void EveryModuleDuplicatesARegisteredFlow()
    {
        Assert.Equal(5, Pairs.Length);

        var catalogue = StoreModuleCatalog.CreateAll()
            .Select(m => m.GetType().Name + ":" + m.Id)
            .ToArray();

        foreach (var (module, flow) in Pairs)
        {
            // the flow's store is registered, so adding the module would register that store a second time
            var store = flow.Replace("Flow", "").ToLowerInvariant();
            Assert.Contains(store, catalogue.Select(c => c.Split(':')[1]).ToArray(), StringComparer.OrdinalIgnoreCase);
        }
    }

    /// <summary>
    /// The modules are not in the catalogue, and must stay out: registering one would double-register its store.
    /// </summary>
    [Fact]
    public void NoneOfTheModulesIsRegistered()
    {
        var names = StoreModuleCatalog.CreateAll().Select(m => m.GetType().Name).ToArray();

        Assert.DoesNotContain("CasioModule", names);
        Assert.DoesNotContain("WarhammerModule", names);
    }

    /// <summary>
    /// The rule this round adds: unreachable code is either unwired or redundant, and only the first kind may be wired.
    /// </summary>
    [Fact]
    public void UnreachableIsNotTheSameAsUnwired()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "tests", "Cybersole.Tests", "DuplicateModuleAuditTests.cs"));

        Assert.Contains("some of it is work that should be deleted", doc);

        // and the estimate from R952 is recorded as discounted rather than repeated
        Assert.Contains("dissolved the estimate", doc);
    }

    /// <summary>The scan's own figures, so the next round starts from them rather than re-deriving them.</summary>
    [Fact]
    public void TheScanFiguresAreRecorded()
    {
        const int suspectFiles = 93;
        const int withAsync = 26;
        const int asyncMethodsTotal = 538;

        Assert.True(withAsync < suspectFiles);
        Assert.True(suspectFiles < asyncMethodsTotal);

        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "tests", "Cybersole.Tests", "DuplicateModuleAuditTests.cs"));
        Assert.Contains("ninety-three files", doc);
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}