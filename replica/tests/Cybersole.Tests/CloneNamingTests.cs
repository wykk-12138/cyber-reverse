using System.Text.RegularExpressions;
using Cybersole.Core.Models;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 68: a clone must be distinguishable from its original.
///
/// R63 replaced three hand-listed Profile copies with <c>p.Clone()</c>, which copies every field
/// and assigns a new Id — and that was the right fix. But <c>Profile.Clone</c> does not rename,
/// and the two hand-written copies disagreed on whether to: <c>BillingView</c> appended
/// " copy", <c>ProfileViews.Clone</c> did not. Unifying on Clone silently dropped the suffix from
/// the Billing page, so a cloned profile appeared in the list looking exactly like its original.
///
/// A screenshot showed two identical rows. No test did, because the tests asserted the fields were
/// copied — which they were.
/// </summary>
public sealed class CloneNamingTests
{
    private readonly ITestOutputHelper _out;

    public CloneNamingTests(ITestOutputHelper output) => _out = output;

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

    public static TheoryData<string> ProfileCloneSites => new()
    {
        // R208: BillingView dropped its clone action. The running 5.18.32 build draws that page with exactly two
        // buttons — "Add Profile" and "Clear Profiles" — so a clone helper there was a replica invention, and a
        // test that demanded a rename in it was protecting the invention rather than the target.
        "src/Cybersole.Ui/Views/Profiles/ProfileViews.cs",
    };

    /// <summary>
    /// Both profile-clone helpers rename the copy.
    /// </summary>
    [Theory]
    [MemberData(nameof(ProfileCloneSites))]
    public void AProfileCloneIsNamedAsACopy(string file)
    {
        var text = Read(file);
        var renames = Regex.IsMatch(text, @"copy\.Name\s*=\s*\w+\.Name\s*\+\s*""\s*copy""");

        _out.WriteLine($"{Path.GetFileName(file)}  renames={renames}");
        Assert.True(renames, $"{file} produces a clone indistinguishable from its original");
    }

    /// <summary>
    /// The underlying Profile.Clone still does not rename — that is deliberate, and this records
    /// why: the model cannot know whether a caller wants a suffix, and ProfileViews' own editor
    /// uses Clone as a duplicate without one.
    /// </summary>
    [Fact]
    public void ProfileCloneItselfStaysNeutral()
    {
        var source = new Profile { Name = "Alice", Email = "a@example.com", CardNumber = "4111111111111111" };
        var copy = source.Clone();

        _out.WriteLine($"name: {source.Name} -> {copy.Name}");

        Assert.Equal("Alice", copy.Name);            // same name
        Assert.NotEqual(source.Id, copy.Id);         // different record
        Assert.Equal("4111111111111111", copy.CardNumber);
    }

    /// <summary>
    /// The task and proxy clones do rename, through their call sites. Recorded so the three are
    /// not accidentally "unified" again into the silent one.
    /// </summary>
    [Fact]
    public void TaskAndProxyClonesAlsoRename()
    {
        // R73: the page and its clone call site moved out of the grab-bag file.
        var tasks = Read("src/Cybersole.Ui/Views/Tasks/TaskView.cs");
        var taskRenames = Regex.IsMatch(tasks, @"copy\.Name\s*=\s*source\.Name\s*\+\s*""\s*copy""");

        var proxy = Read("src/Cybersole.Ui/Views/Proxies/ProxyGrid.cs");
        // A proxy has no name; the distinguishing field is the address, and CloneProxy keeps the
        // group and adds the row. Nothing to rename there — assert the absence of a rename rather
        // than inventing one.
        var proxyHasName = proxy.Contains("Name = proxy.Name", StringComparison.Ordinal);

        _out.WriteLine($"task renames={taskRenames}  proxy-invents-a-name={proxyHasName}");

        Assert.True(taskRenames, "task clone lost its copy suffix");
        Assert.False(proxyHasName, "proxy clone invented a name field");
    }
}
