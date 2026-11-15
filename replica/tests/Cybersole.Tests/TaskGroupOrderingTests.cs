using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Xunit;

namespace Cybersole.Tests;

public class TaskGroupOrderingTests
{
    private static TaskGroup Group(string name, bool pinned, int tasks = 1)
    {
        var group = new TaskGroup { Name = name, Pinned = pinned };
        for (var i = 0; i < tasks; i++) group.Tasks.Add(new BotTask { Name = $"{name}-{i}" });
        return group;
    }

    [Fact]
    public void Pinned_Groups_Float_To_The_Top()
    {
        var sorted = TaskGroupOrdering.Sort(new[]
        {
            Group("a", false), Group("b", true), Group("c", false), Group("d", true),
        });

        Assert.Equal(new[] { "b", "d", "a", "c" }, sorted.Select(g => g.Name).ToArray());
    }

    [Fact]
    public void Order_Inside_Buckets_Is_Preserved()
    {
        var sorted = TaskGroupOrdering.Sort(new[]
        {
            Group("x", false), Group("y", false), Group("z", true), Group("w", true),
        });

        Assert.Equal(new[] { "z", "w", "x", "y" }, sorted.Select(g => g.Name).ToArray());
    }

    [Fact]
    public void No_Pinned_Groups_Keeps_Original_Order()
    {
        var sorted = TaskGroupOrdering.Sort(new[] { Group("one", false), Group("two", false) });
        Assert.Equal(new[] { "one", "two" }, sorted.Select(g => g.Name).ToArray());
    }

    [Fact]
    public void Empty_Input_Is_Safe()
        => Assert.Empty(TaskGroupOrdering.Sort(Array.Empty<TaskGroup>()));

    [Fact]
    public void Pinned_Task_Count_Adds_Up()
    {
        var groups = new[] { Group("a", true, 3), Group("b", true, 2), Group("c", false, 9) };
        Assert.Equal(5, TaskGroupOrdering.PinnedTaskCount(groups));
    }
}
