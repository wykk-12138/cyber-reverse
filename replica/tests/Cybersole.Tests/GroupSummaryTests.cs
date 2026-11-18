using System.Linq;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Tasks;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R345: the two group-summary operations whose meaning is not in doubt.
///
/// <para>
/// The binding table puts Clone, Delete, Edit, StartAll and StopAll on <c>GroupSummary</c>. StartAll and StopAll mean
/// what they say — start/stop every task in this group through the engine, as the tasks page does — so they are here.
/// Clone, Delete and Edit are <b>not</b>: the image names them without saying whether Clone copies tasks, and Edit's
/// parameter list is unknown. They stay in docs/BINDING_BACKLOG.md as named-but-not-recovered.
/// </para>
/// </summary>
/// <summary>
/// R1165: serialised, because it mutates and asserts on the one on-disk settings file the whole run
/// shares. See <see cref="SharedSettingsCollection"/> for the mechanism.
/// </summary>
[Collection("shared-settings")]
public sealed class GroupSummaryTests
{
    private readonly ITestOutputHelper _out;
    public GroupSummaryTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void StartAllOnlyCountsTasksThatAreNotRunning()
    {
        using var services = TestServices.Create();
        var group = new TaskGroup { Name = "G" };
        group.Tasks.Add(new BotTask { Id = "a", State = TaskState.Idle });
        group.Tasks.Add(new BotTask { Id = "b", State = TaskState.Monitoring });

        var summary = new GroupSummary(services, group);
        var started = summary.StartAllCore();

        _out.WriteLine("started: " + started);
        Assert.Equal(1, started);
    }

    [Fact]
    public void StopAllCountsTheRunningOnes()
    {
        using var services = TestServices.Create();
        var group = new TaskGroup { Name = "G" };
        group.Tasks.Add(new BotTask { Id = "a", State = TaskState.Monitoring });
        group.Tasks.Add(new BotTask { Id = "b", State = TaskState.Idle });

        var summary = new GroupSummary(services, group);

        Assert.Equal(1, summary.StopAllCore());
    }

    [Fact]
    public void CloningCopiesTheGroupAndItsTasks()
    {
        using var services = TestServices.Create();
        var group = new TaskGroup { Name = "G", MonitorDelay = 1000 };
        group.Tasks.Add(new BotTask { Name = "t1", Store = "shop" });
        services.Config.TaskGroups.Add(group);

        var summary = new GroupSummary(services, group);
        var copy = summary.CloneCore();

        _out.WriteLine(copy.Name + " / " + copy.Tasks.Count);
        Assert.Equal("G copy", copy.Name);
        Assert.Single(copy.Tasks);
        Assert.Equal(1000, copy.MonitorDelay);
        Assert.Contains(copy, services.Config.TaskGroups);
        Assert.NotEqual(group.Id, copy.Id);
    }

    [Fact]
    public void DeletingRemovesTheGroupOnce()
    {
        using var services = TestServices.Create();
        var group = new TaskGroup { Name = "G" };
        services.Config.TaskGroups.Add(group);

        var summary = new GroupSummary(services, group);

        // R500: `Delete` is an ICommand now (the binding table asks for a property), so its bool return is gone.
        // The effect is what matters and it is asserted below.
        summary.Delete.Execute(null);
        Assert.DoesNotContain(group, services.Config.TaskGroups);
    }
}
