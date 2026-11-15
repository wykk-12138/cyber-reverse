using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Xunit;

namespace Cybersole.Tests;

public class TaskPolicyTests
{
    [Fact]
    public void Monitor_Only_Task_Never_Checks_Out()
    {
        var task = new BotTask { Name = "watch", MonitorMode = true };
        Assert.False(TaskPolicy.ShouldCheckout(task));
        Assert.NotNull(TaskPolicy.SkipReason(task));
    }

    [Fact]
    public void Normal_Task_Checks_Out()
    {
        var task = new BotTask { Name = "buy" };
        Assert.True(TaskPolicy.ShouldCheckout(task));
        Assert.Null(TaskPolicy.SkipReason(task));
    }

    [Fact]
    public void Group_Solver_Overrides_The_Global_One()
    {
        var group = new TaskGroup { CloudflareSolver = "capmonster" };
        Assert.Equal("capmonster", TaskPolicy.ResolveSolver(group, "internal"));
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void Missing_Group_Solver_Falls_Back(string? value)
    {
        var group = new TaskGroup { CloudflareSolver = value };
        Assert.Equal("internal", TaskPolicy.ResolveSolver(group, "internal"));
    }

    [Fact]
    public void Null_Group_Falls_Back()
        => Assert.Equal("internal", TaskPolicy.ResolveSolver(null, "internal"));

    [Fact]
    public void Group_Solver_Is_Trimmed()
    {
        var group = new TaskGroup { CloudflareSolver = "  hcaptcha-ai  " };
        Assert.Equal("hcaptcha-ai", TaskPolicy.ResolveSolver(group, "internal"));
    }
}
