using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Xunit;

namespace Cybersole.Tests;

public class TaskGroupSyncTests
{
    private static (TaskGroup Group, BotTask A, BotTask B) Build(bool linked)
    {
        var group = new TaskGroup { Name = "G", LinkedDelays = linked };
        var a = new BotTask { Name = "a", MonitorDelay = 1000, RetryDelay = 500 };
        var b = new BotTask { Name = "b", MonitorDelay = 2000, RetryDelay = 900 };
        group.Tasks.Add(a);
        group.Tasks.Add(b);
        return (group, a, b);
    }

    [Fact]
    public void Linked_Group_Propagates_Delays()
    {
        var (group, a, b) = Build(linked: true);
        a.MonitorDelay = 1500;
        a.RetryDelay = 700;

        var touched = TaskGroupSync.ApplyLinkedDelays(group, a);

        Assert.Equal(1, touched);
        Assert.Equal(1500, b.MonitorDelay);
        Assert.Equal(700, b.RetryDelay);
    }

    [Fact]
    public void Unlinked_Group_Leaves_Siblings_Alone()
    {
        var (group, a, b) = Build(linked: false);
        a.MonitorDelay = 1500;

        Assert.Equal(0, TaskGroupSync.ApplyLinkedDelays(group, a));
        Assert.Equal(2000, b.MonitorDelay);
    }

    [Fact]
    public void Edited_Task_Is_Not_Counted()
    {
        var (group, a, _) = Build(linked: true);
        Assert.Equal(1, TaskGroupSync.ApplyLinkedDelays(group, a));   // only b
    }

    [Fact]
    public void Single_Task_Group_Touches_Nothing()
    {
        var group = new TaskGroup { LinkedDelays = true };
        var only = new BotTask { Name = "only" };
        group.Tasks.Add(only);

        Assert.Equal(0, TaskGroupSync.ApplyLinkedDelays(group, only));
    }

    [Fact]
    public void Remaining_Checkouts_Respects_Limit()
    {
        var group = new TaskGroup { CheckoutLimit = 5 };
        Assert.Equal(5, TaskGroupSync.RemainingCheckouts(group, 0));
        Assert.Equal(2, TaskGroupSync.RemainingCheckouts(group, 3));
        Assert.Equal(0, TaskGroupSync.RemainingCheckouts(group, 9));
    }

    [Fact]
    public void Zero_Limit_Means_Unlimited()
    {
        var group = new TaskGroup { CheckoutLimit = 0 };
        Assert.Equal(int.MaxValue, TaskGroupSync.RemainingCheckouts(group, 1000));
    }
}
