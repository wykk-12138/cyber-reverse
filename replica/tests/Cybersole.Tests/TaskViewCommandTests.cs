using System.IO;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R229: <c>TaskView</c>'s remaining bound commands, and the rule that made them possible — <b>one implementation, a
/// named way in</b>. The behaviour lived in <c>TaskGrid</c>'s private hooks, reachable only by clicking a row menu item;
/// the original binds the same actions as commands on the view, so a rebinding or a keybind can address them.
///
/// <para>
/// Ten names now exist on the view: <c>StartSelected, StopSelected, StopAll, CloneSelected, DeleteSelected,
/// OpenStaggerStart, ForceStartSelected, EditSelected, EditAll, OpenTaskView, OpenBrowser, OpenTaskCreator,
/// OpenSolvers, OpenGroupPopup, CopyUrl, NextGroup, PreviousGroup, SetQuery</c>.
/// </para>
/// </summary>
public sealed class TaskViewCommandTests
{
    private readonly ITestOutputHelper _out;
    public TaskViewCommandTests(ITestOutputHelper output) => _out = output;

    private static string View() => File.ReadAllText(Path.Combine(Root(),
        "src", "Cybersole.Ui", "Views", "Tasks", "TaskView.cs"));

    private static string Grid() => File.ReadAllText(Path.Combine(Root(),
        "src", "Cybersole.Ui", "Views", "Tasks", "TaskGrid.cs"));

    [Fact]
    public void EveryBoundCommandExistsOnTheView()
    {
        var source = View();

        var commands = new[]
        {
            "StartSelected", "StopSelected", "StopAll", "CloneSelected", "DeleteSelected",
            "OpenStaggerStart", "ForceStartSelected", "EditSelected", "EditAll",
            "OpenTaskView", "OpenBrowser", "OpenTaskCreator", "OpenSolvers", "OpenGroupPopup",
            "CopyUrl", "NextGroup", "PreviousGroup", "SetQuery",
        };

        foreach (var command in commands)
        {
            var present = source.Contains("public void " + command + "(", System.StringComparison.Ordinal)
                          || source.Contains("public ICommand " + command, System.StringComparison.Ordinal)
                          || source.Contains("public bool " + command + "(", System.StringComparison.Ordinal);

            _out.WriteLine($"{command}: {(present ? "present" : "MISSING")}");
            Assert.True(present, "TaskView does not expose " + command);
        }
    }

    [Fact]
    public void TheBehaviourLivesOnceAndTheViewDelegatesToIt()
    {
        var grid = Grid();
        var view = View();

        // the entry points on the grid, next to the hooks
        foreach (var entry in new[]
                 {
                     "StartSelectedTasks", "StaggerStartSelectedTasks", "ForceStartSelectedTasks",
                     "StopSelectedTasks", "EditSelectedTasks", "CloneSelectedTasks",
                     "ViewSelectedTask", "OpenSelectedTask", "DeleteSelectedTasks",
                 })
        {
            Assert.Contains("internal void " + entry + "(", grid);
        }

        // and the view's names call them rather than re-implementing
        Assert.Contains("_grid?.StaggerStartSelectedTasks()", view);
        Assert.Contains("_grid?.ForceStartSelectedTasks()", view);
        Assert.Contains("_grid?.EditSelectedTasks()", view);
        Assert.Contains("_grid?.ViewSelectedTask()", view);
        Assert.Contains("_grid?.OpenSelectedTask()", view);
    }

    [Fact]
    public void StopSelectedStopsOnlyTheSelection()
    {
        var view = View();

        // StopAll takes no argument; StopSelected must not be the same call
        Assert.Contains("private void StopSelectedCore()", view);
        Assert.Contains("_grid?.EffectiveSelection()", view);
        Assert.Contains("_services.Tasks.StopAll(picked)", view);

        // and the grid's fallback is documented: empty selection means every visible row
        Assert.Contains("every visible row when nothing is selected", Grid());
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
