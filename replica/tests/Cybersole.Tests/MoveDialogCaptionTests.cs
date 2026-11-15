using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 66, second half: the four Move dialogs all said the wrong thing when there was nowhere
/// to move to.
///
/// Each one branched on <c>groups.Count == 0</c>. With exactly one group — the state every new
/// install is in — the dialog opened, listed that single group as the destination, and then the
/// Move button did nothing, because the handler refuses a no-op move. The caption read "only its
/// group changes", which is true and useless: it does not say the move is impossible.
///
/// Found by opening the dialog in the real window, not by any test.
/// </summary>
public sealed class MoveDialogCaptionTests
{
    private readonly ITestOutputHelper _out;

    public MoveDialogCaptionTests(ITestOutputHelper output) => _out = output;

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }

    private static string Read(string relative) =>
        File.ReadAllText(Path.Combine(RepoRoot(), relative.Replace('/', Path.DirectorySeparatorChar)));

    public static TheoryData<string> MoveViews => new()
    {
        "src/Cybersole.Ui/Views/Proxies/ProxyMoveView.cs",
        "src/Cybersole.Ui/Views/Accounts/AccountMoveView.cs",
        "src/Cybersole.Ui/Views/Profiles/ProfileMoveView.cs",
        "src/Cybersole.Ui/Views/Tasks/TaskMoveView.cs",
    };

    /// <summary>
    /// The guard is <c>&lt;= 1</c>. <c>== 0</c> leaves the one-group case with a working-looking
    /// button that silently does nothing.
    /// </summary>
    [Theory]
    [MemberData(nameof(MoveViews))]
    public void TheGuardCoversOneGroup(string file)
    {
        var text = Read(file);

        var coversOne = text.Contains("groups.Count <= 1", StringComparison.Ordinal);
        var onlyZero = Regex.IsMatch(text, @"groups\.Count\s*==\s*0");

        _out.WriteLine($"{Path.GetFileName(file)}  <=1={coversOne}  ==0={onlyZero}");

        Assert.True(coversOne, $"{file} does not handle the single-group case");
        Assert.False(onlyZero, $"{file} still branches on Count == 0 only");
    }

    /// <summary>The caption says the move is impossible, not just that it is a no-op.</summary>
    [Theory]
    [MemberData(nameof(MoveViews))]
    public void TheCaptionSaysThereIsNowhereToGo(string file)
    {
        var text = Read(file);

        var honest = text.Contains("no other group to move to", StringComparison.Ordinal);
        _out.WriteLine($"{Path.GetFileName(file)}  honest-caption={honest}");

        Assert.True(honest,
            $"{file} tells the user nothing about why Move does not respond when there is one group");
    }
}
