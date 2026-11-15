using System.Linq;
using Cybersole.Ui.Views.SmartActions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R348: three more bound names exist as members.
///
/// <para>
/// The binding table carries Exit / Minimise / SmartAction / View on <c>HistoryWindow</c> and
/// Clock / Export / OpenCreator / … on <c>SmartActionsView</c>. Exit (close) and Minimise (window state) mean exactly
/// what they say, and OpenCreator is the "new action" path that already existed as a private editor call — those three are
/// members now. SmartAction, View, Clock and Export are still guesses, so they stay named in docs/BINDING_BACKLOG.md.
/// </para>
/// </summary>
public sealed class SmartActionWindowOpsTests
{
    private readonly ITestOutputHelper _out;
    public SmartActionWindowOpsTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheThreeOperationsAreMembers()
    {
        var history = typeof(HistoryWindow).GetMembers().Select(m => m.Name).ToList();
        var view = typeof(SmartActionsView).GetMembers().Select(m => m.Name).ToList();

        _out.WriteLine("history: " + string.Join(", ", history.Where(n => n is "Exit" or "Minimise")));
        Assert.Contains("Exit", history);
        Assert.Contains("Minimise", history);
        Assert.Contains("OpenCreator", view);
    }
}
