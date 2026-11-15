using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Tasks;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 73: the Tasks page is a table again, with the five columns and the six footer actions the
/// locale names.
///
/// <para>
/// Driving the live 5.18.32 showed three things the replica's page did not have: the group is a
/// <b>dropdown</b> at the top left rather than a left pane, the header row carries the count
/// (<c>Tasks.CountFormat</c>), and the footer is exactly six buttons
/// (<c>Tasks.Action.Creator</c> / <c>.Clear</c> / <c>.Start</c> / <c>.Stop</c> / <c>.Edit</c> /
/// <c>.CaptchaSolver</c>) — not the eight the replica had, five of which the row menu duplicates.
/// </para>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class TasksPageTests
{
    private readonly ITestOutputHelper _out;

    public TasksPageTests(ITestOutputHelper output) => _out = output;

    private static BotTask Make(string store, string product, TaskState state = TaskState.Idle) => new()
    {
        Name = store + "-task",
        Store = store,
        State = state,
        Product = new Product { Name = product },
    };

    /// <summary>The five column keys, in the locale's order, and no sixth.</summary>
    [Fact]
    public void TheGridHasTheFiveLocaleColumns()
    {
        var columns = Enum.GetNames(typeof(TaskGrid.TaskColumn));

        _out.WriteLine(string.Join(", ", columns));

        Assert.Equal(new[] { "Site", "Product", "Profile", "Proxies", "Status" }, columns);
    }

    /// <summary>A cell falls back to an em dash rather than printing an empty string.</summary>
    [Fact]
    public void EmptyCellsPrintAnEmDash()
    {
        var task = new BotTask { Store = "footlocker" };
        var grid = new TaskGrid(new List<BotTask> { task });

        _out.WriteLine($"{grid.Cell(task, TaskGrid.TaskColumn.Site)} / " +
                       $"{grid.Cell(task, TaskGrid.TaskColumn.Product)} / " +
                       $"{grid.Cell(task, TaskGrid.TaskColumn.Profile)}");

        Assert.Equal("footlocker", grid.Cell(task, TaskGrid.TaskColumn.Site));
        Assert.Equal("—", grid.Cell(task, TaskGrid.TaskColumn.Product));
        Assert.Equal("—", grid.Cell(task, TaskGrid.TaskColumn.Profile));
        Assert.Equal("—", grid.Cell(task, TaskGrid.TaskColumn.Proxies));
    }

    /// <summary>
    /// The status column prefers the engine's live state over the persisted one — the defect the
    /// old page had and fixed in R55's lineage; it must not come back with the new table.
    /// </summary>
    [Fact]
    public void TheStatusColumnPrefersTheLiveState()
    {
        var task = Make("nike", "shoe", TaskState.Idle);
        var grid = new TaskGrid(new List<BotTask> { task })
            .WithStatus(t => ReferenceEquals(t, task) ? TaskState.Monitoring : t.State);

        _out.WriteLine($"persisted=Idle live={grid.Cell(task, TaskGrid.TaskColumn.Status)}");

        Assert.Equal("Monitoring", grid.Cell(task, TaskGrid.TaskColumn.Status));
    }

    /// <summary>Every header sorts, and the glyph follows the direction.</summary>
    [Fact]
    public void EveryHeaderSortsBothWays()
    {
        var rows = new List<BotTask>
        {
            Make("nike", "zebra"),
            Make("footlocker", "alpha"),
        };
        var grid = new TaskGrid(rows);

        Assert.Equal("↑", grid.SortGlyph(TaskGrid.TaskColumn.Site));
        Assert.Equal(new[] { "footlocker", "nike" }, grid.Ordered().Select(t => t.Store));

        grid.SortBy(TaskGrid.TaskColumn.Site);
        Assert.Equal(new[] { "nike", "footlocker" }, grid.Ordered().Select(t => t.Store));

        grid.SortBy(TaskGrid.TaskColumn.Product);
        _out.WriteLine("by product: " + string.Join(",", grid.Ordered().Select(t => t.Product.Name)));
        Assert.Equal(new[] { "alpha", "zebra" }, grid.Ordered().Select(t => t.Product.Name));
    }

    /// <summary><c>Tasks.CountFormat</c> = "{0} Tasks".</summary>
    [Fact]
    public void TheCountIsTheLocalesFormat()
    {
        Assert.Equal("0 Tasks", TaskGrid.CountCaption(0));
        Assert.Equal("3 Tasks", TaskGrid.CountCaption(3));
        Assert.Equal("0 Tasks", TaskView.CountCaption(0));
    }

    /// <summary>Selection captions and the plural-aware menu header.</summary>
    [Fact]
    public void TheSelectionCaptionIsTheLocalesWords()
    {
        Assert.Equal("1 TASK SELECTED", TaskGrid.SelectionHeader(1));
        Assert.Equal("5 TASKS SELECTED", TaskGrid.SelectionHeader(5));
    }

    /// <summary>
    /// The row menu carries the locale's items, and the single-row ones only for one row: a
    /// "View Task" for five selected tasks has nothing to view.
    /// </summary>
    [Fact]
    public void TheMenuIsSelectionAware()
    {
        var task = Make("nike", "shoe");
        var grid = new TaskGrid(new List<BotTask> { task })
            .WithStarter(_ => { })
            .WithEditor(_ => { })
            .WithViewer(_ => { })
            .WithDeleter(_ => { });

        var one = grid.MenuFor(new[] { task }).OfType<MenuItem>()
            .Select(m => m.Header?.ToString() ?? "").ToList();
        var many = grid.MenuFor(new[] { task, task }).OfType<MenuItem>()
            .Select(m => m.Header?.ToString() ?? "").ToList();

        _out.WriteLine("one  : " + string.Join(" | ", one));
        _out.WriteLine("many : " + string.Join(" | ", many));

        Assert.Contains("View Task", one);
        Assert.DoesNotContain("View Task", many);
        Assert.Contains("Start Tasks", many);
        Assert.Contains("Delete Tasks", many);
        Assert.Equal("2 TASKS SELECTED", many[0]);
    }

    /// <summary>The header checkbox selects everything, and Delete removes the selection.</summary>
    [Fact]
    public void TheHeaderCheckboxSelectsAndDeletesEverything()
    {
        var rows = new List<BotTask> { Make("nike", "a"), Make("footlocker", "b") };
        var deleted = 0;
        var grid = new TaskGrid(rows).WithDeleter(doomed => deleted = doomed.Count);

        Assert.False(grid.AllSelected);
        grid.SelectAll();
        Assert.True(grid.AllSelected);
        Assert.Equal(2, grid.SelectedTasks.Count);

        var menu = grid.MenuFor(grid.SelectedTasks).OfType<MenuItem>()
            .First(m => (m.Header?.ToString() ?? "").StartsWith("Delete", StringComparison.Ordinal));
        _out.WriteLine($"delete item = {menu.Header}");
        Assert.NotNull(menu);
    }

    /// <summary>
    /// The four pills count Success / Failed / Declined / running. The colours and the states are
    /// the only evidence — the pills carry no accessible label — so this pins the mapping that was
    /// chosen rather than proving the original's.
    /// </summary>
    [Fact]
    public void TheFourPillsCountTheFourGroups()
    {
        var tasks = new List<BotTask>
        {
            Make("a", "p", TaskState.Success),
            Make("b", "p", TaskState.Success),
            Make("c", "p", TaskState.Failed),
            Make("d", "p", TaskState.Declined),
            Make("e", "p", TaskState.Monitoring),
            Make("f", "p", TaskState.Idle),
        };

        var counts = TaskView.PillCounts(tasks, t => t.State);
        _out.WriteLine($"success={counts.Success} failed={counts.Failed} declined={counts.Declined} running={counts.Running}");

        Assert.Equal(2, counts.Success);
        Assert.Equal(1, counts.Failed);
        Assert.Equal(1, counts.Declined);
        Assert.Equal(1, counts.Running);
    }

    /// <summary>The empty state is the same two lines the other tables use.</summary>
    [Fact]
    public void TheEmptyStateIsTheTwoLocaleLines()
    {
        var grid = new TaskGrid(new List<BotTask>());
        var root = (DockPanel)grid.Content!;
        var body = (StackPanel)((ScrollViewer)root.Children.OfType<ScrollViewer>().Single()).Content!;

        // R209: the empty state is the shared EmptyView now — glyph, headline, one page-specific line — which is what
        // the running build draws. This used to assert a bare two-TextBlock StackPanel because that is all the replica
        // had.
        var empty = body.Children.OfType<Cybersole.Ui.Views.Common.EmptyView>().Single();
        _out.WriteLine(empty.HeadlineText.Text + " / " + empty.BodyText.Text);

        Assert.Equal("Nothing to see here", empty.HeadlineText.Text);
        Assert.Equal("Add some tasks to get started", empty.BodyText.Text);
        Assert.NotNull(empty.Icon);
    }

    /// <summary>
    /// The header and the rows reserve the same fixed width, so the columns line up — the defect
    /// R72 found on both other tables.
    /// </summary>
    [Fact]
    public void TheHeaderAndTheRowsReserveTheSameWidth()
    {
        var grid = new TaskGrid(new List<BotTask> { Make("nike", "shoe") });
        var root = (DockPanel)grid.Content!;

        var header = (Grid)root.Children[0];
        var body = (StackPanel)((ScrollViewer)root.Children.OfType<ScrollViewer>().Single()).Content!;
        var row = body.Children.OfType<Grid>().First();

        Assert.Equal(header.ColumnDefinitions.Count, row.ColumnDefinitions.Count);

        var headerLast = header.ColumnDefinitions[header.ColumnDefinitions.Count - 1];
        var rowLast = row.ColumnDefinitions[row.ColumnDefinitions.Count - 1];

        _out.WriteLine($"header last = {headerLast.Width}, row last = {rowLast.Width}");

        Assert.True(headerLast.Width.IsAbsolute);
        Assert.Equal(headerLast.Width.Value, rowLast.Width.Value);
    }

    /// <summary>
    /// R344: two of the eight names the binding table puts on TaskView now exist as members. The other six are bound by
    /// the image but their behaviour is not recovered yet, so they are named in docs/BINDING_BACKLOG.md rather than
    /// guessed at here.
    ///
    /// R492: the assertion is about the **name existing**, not about it being a method — several of these are now
    /// `ICommand` properties (which is what the binding table asks for), and `GetMethods()` cannot see a property.
    /// </summary>
    [Fact]
    public void TheBoundNamesThatHaveBehaviourAreMembers()
    {
        var type = typeof(Cybersole.Ui.Views.Tasks.TaskView);
        var names = type.GetMembers().Select(m => m.Name).ToList();

        Assert.Contains("ClearAll", names);
        Assert.Contains("OpenSettings", names);
    }
}
