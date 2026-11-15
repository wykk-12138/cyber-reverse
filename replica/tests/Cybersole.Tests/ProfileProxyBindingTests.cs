using System.Reflection;
using System.Text.RegularExpressions;
using Cybersole.Core.Models;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 69: seven <see cref="Profile"/> properties were never referenced by any UI code.
///
///   ProxyGroupId, Region, StreetWithNumber, StreetSecondLine, StreetThirdLine, Mobile, MobilePrefix
///
/// Six of them have no locale label at all — they are fields the model carries for address shapes
/// this replica does not render (Philippine barangay, Japanese kana, split street lines). That is
/// a scope decision, not a defect.
///
/// ProxyGroupId is different: <c>get_ProxyGroupId</c> / <c>set_ProxyGroupId</c> sit next to
/// <c>FromPayPalAccount</c> in the original, so it is a real property of a real profile, and here
/// it was set by nothing and read by nothing.
///
/// It is now offered in the editor as a stored preference. The engine still routes by
/// <c>task.ProxyGroupId</c>; making the profile's binding authoritative needs evidence for
/// precedence that this round does not have, so the value is recorded and not acted on. These
/// tests pin the recording, and pin that the engine was not quietly changed.
/// </summary>
public sealed class ProfileProxyBindingTests
{
    private readonly ITestOutputHelper _out;

    public ProfileProxyBindingTests(ITestOutputHelper output) => _out = output;

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }

    private static string Read(string rel) =>
        File.ReadAllText(Path.Combine(RepoRoot(), rel.Replace('/', Path.DirectorySeparatorChar)));

    /// <summary>The editor offers the choice and writes it back on Save.</summary>
    [Fact]
    public void TheEditorOffersAndWritesAProxyGroup()
    {
        var editor = Read("src/Cybersole.Ui/Views/ProfileEditorWindow.cs");

        var hasRow = editor.Contains("\"Proxy group\"", StringComparison.Ordinal);
        var writes = editor.Contains("profile.ProxyGroupId =", StringComparison.Ordinal);
        var clears = editor.Contains("proxyIndex <= 0", StringComparison.Ordinal);
        var loads = editor.Contains("existing.ProxyGroupId", StringComparison.Ordinal);

        _out.WriteLine($"row={hasRow} writes={writes} clears={clears} loads-existing={loads}");

        Assert.True(hasRow, "the editor has no Proxy group row");
        Assert.True(writes, "the row is shown but never saved");
        Assert.True(clears, "\"(task proxy)\" must clear the binding, not store index 0 as a group");
        Assert.True(loads, "editing an existing profile does not show its current binding");
    }

    /// <summary>
    /// The engine still routes by the task's group. If a future round makes the profile's binding
    /// authoritative, it must do so deliberately — this test is the tripwire that says the
    /// behaviour changed.
    /// </summary>
    [Fact]
    public void TheEngineStillRoutesByTheTask()
    {
        var engine = Read("src/Cybersole.Services/TaskEngine.cs");

        var byTask = engine.Contains("g.Id == task.ProxyGroupId", StringComparison.Ordinal);
        var byProfile = Regex.IsMatch(engine, @"g\.Id\s*==\s*\w*[Pp]rofile\.ProxyGroupId");

        _out.WriteLine($"routes-by-task={byTask} routes-by-profile={byProfile}");

        Assert.True(byTask, "the engine stopped routing by the task's proxy group");
        Assert.False(byProfile,
            "the engine now routes by the profile's proxy group — that is a precedence decision " +
            "and needs its own evidence, not a side effect of adding a dropdown");
    }

    /// <summary>
    /// The seven unreferenced properties, recorded so the count does not drift unnoticed. Six are
    /// address-shape fields with no locale label; the seventh is the binding this round wired.
    /// </summary>
    [Fact]
    public void TheUnreferencedSetIsKnown()
    {
        var ui = Path.Combine(RepoRoot(), "src", "Cybersole.Ui");
        var all = string.Join("\n", Directory
            .EnumerateFiles(ui, "*.cs", SearchOption.AllDirectories)
            .Where(f => !f.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}"))
            .Select(File.ReadAllText));

        var never = typeof(Profile).GetProperties(BindingFlags.Public | BindingFlags.Instance)
            .Where(p => p.Name is not ("Display" or "Last4" or "Id"))
            .Where(p => !Regex.IsMatch(all, @"\." + Regex.Escape(p.Name) + @"\b"))
            .Select(p => p.Name)
            .OrderBy(n => n, StringComparer.Ordinal)
            .ToList();

        _out.WriteLine($"still unreferenced ({never.Count}): {string.Join(", ", never)}");

        // ProxyGroupId must no longer be in this set.
        Assert.DoesNotContain("ProxyGroupId", never);

        // The six address-shape fields remain out of scope; failing here means the set changed.
            // R511 added "Card": a view over the flat card fields. Nothing in src/ reads it yet —
            // the UI edits CardNumber / CardExpiry / CardCvv directly, exactly as the original dialog does.
        Assert.Equal(
            new[] { "Card", "Delivery", "Mobile", "MobilePrefix", "Region", "StreetSecondLine", "StreetThirdLine", "StreetWithNumber" },
            never);
    }
}
