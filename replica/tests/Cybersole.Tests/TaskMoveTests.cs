using Cybersole.Core;
using Cybersole.Core.Models;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 65: <c>Tasks.Context.MoveTo</c>, and the third hand-listed copy found in this codebase.
///
/// <c>TasksViews.CloneTask</c> predated <c>BotTask.Clone</c> (R60) and was never switched over. It
/// had drifted in two ways: it carried <c>StartTime</c> across, and it copied five of
/// <c>Product</c>'s eight fields. Both are the same failure mode — a field list written once and
/// never revisited — and both are invisible until something reads the missing field.
/// </summary>
public sealed class TaskMoveTests
{
    private readonly ITestOutputHelper _out;

    public TaskMoveTests(ITestOutputHelper output) => _out = output;

    private static BotTask Make() => new()
    {
        Name = "Dunk",
        Store = "nike",
        GroupId = "g1",
        ProfileId = "p1",
        ProxyGroupId = "x1",
        AccountId = "a1",
        Quantity = 2,
        MonitorMode = true,
        CheckoutDelay = 500,
        MonitorDelay = 1200,
        RetryDelay = 800,
        Timeout = 45,
        Enabled = true,
        State = TaskState.CheckingOut,
        StartTime = new DateTime(2026, 3, 3, 9, 0, 0, DateTimeKind.Utc),
        Product = new Product
        {
            Name = "Dunk Low",
            Url = "https://www.nike.com/t/dunk",
            Price = "110",
            Variant = "black",
            Image = "https://img/1.jpg",
            Input = "DV0833-001",
            PriceCheck = true,
            Sizes = { "9", "10" },
        },
        ExtraProducts =
        {
            new Product { Name = "AM1", Url = "https://www.nike.com/t/am1", Image = "https://img/2.jpg" },
        },
    };

    /// <summary>
    /// Product carries all eight fields, including the three the old hand-listed copy dropped.
    /// </summary>
    [Fact]
    public void TheCloneKeepsEveryProductField()
    {
        var source = Make();
        var copy = source.Clone();

        _out.WriteLine($"variant={copy.Product.Variant} image={copy.Product.Image} input={copy.Product.Input}");

        Assert.Equal("black", copy.Product.Variant);
        Assert.Equal("https://img/1.jpg", copy.Product.Image);
        Assert.Equal("DV0833-001", copy.Product.Input);
        Assert.Equal("110", copy.Product.Price);
        Assert.True(copy.Product.PriceCheck);
        Assert.Equal(source.Product.Sizes, copy.Product.Sizes);
        Assert.Equal("https://img/2.jpg", copy.ExtraProducts[0].Image);
    }

    /// <summary>
    /// A clone has no start time. The old copy carried it, which made a task that had never run
    /// look like it began hours ago.
    /// </summary>
    [Fact]
    public void TheCloneHasNoStartTime()
    {
        var source = Make();
        var copy = source.Clone();

        _out.WriteLine($"source start={source.StartTime:u} clone start={(copy.StartTime is null ? "(none)" : copy.StartTime.ToString())}");
        _out.WriteLine($"state: {source.State} -> {copy.State}");

        Assert.NotNull(source.StartTime);
        Assert.Null(copy.StartTime);
        Assert.Equal(TaskState.Idle, copy.State);
    }

    /// <summary>
    /// Move updates both sides and leaves the task's own state alone — it is the same task in a
    /// different group, not a new one.
    /// </summary>
    [Fact]
    public void MovingATaskUpdatesBothSides()
    {
        var task = Make();
        var from = new TaskGroup { Name = "A", Id = "g1", Tasks = { task } };
        var to = new TaskGroup { Name = "B", Id = "g2" };
        var groups = new List<TaskGroup> { from, to };

        foreach (var group in groups) group.Tasks.Remove(task);
        to.Tasks.Add(task);
        task.GroupId = to.Id;

        _out.WriteLine($"A={from.Tasks.Count} B={to.Tasks.Count} GroupId={task.GroupId}");
        _out.WriteLine($"state kept={task.State}");

        Assert.Empty(from.Tasks);
        Assert.Single(to.Tasks);
        Assert.Equal("g2", task.GroupId);

        // The task itself is untouched: moving is not cloning.
        Assert.Equal(TaskState.CheckingOut, task.State);
        Assert.NotNull(task.StartTime);
        Assert.Equal("DV0833-001", task.Product.Input);
    }

    /// <summary>
    /// No hand-listed BotTask copy remains — the R63 rule for Profile, applied to tasks.
    /// </summary>
    [Fact]
    public void NoHandListedTaskCopyRemains()
    {
        var root = RepoRoot();
        var offenders = new List<string>();
        var ctor = new System.Text.RegularExpressions.Regex(@"=>\s*new\s*\(\s*\)\s*\{");

        foreach (var file in Directory.EnumerateFiles(Path.Combine(root, "src"), "*.cs",
                     SearchOption.AllDirectories))
        {
            if (file.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")) continue;
            var text = File.ReadAllText(file);

            // a method returning BotTask that builds one with an object initialiser
            if (text.Contains("BotTask CloneTask(BotTask", StringComparison.Ordinal)
                && ctor.IsMatch(text))
                offenders.Add(Path.GetFileName(file));
        }

        _out.WriteLine($"hand-listed task copies: {(offenders.Count == 0 ? "(none)" : string.Join(",", offenders))}");
        Assert.Empty(offenders);
    }

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}
