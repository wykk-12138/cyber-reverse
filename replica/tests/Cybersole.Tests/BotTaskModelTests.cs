using System.Collections.Generic;
using System.Reflection;
using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Newtonsoft.Json;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Pins <see cref="BotTask.Running"/> (<c>bool</c>, getter + setter, <see cref="JsonIgnoreAttribute"/>)
/// matching the compiled binding table while preserving the serialized <c>tasks.json</c> schema.
/// </summary>
public sealed class BotTaskModelTests
{
    [Fact]
    public void RunningMirrorsIsRunningUntilExplicitlySetAndRaisesPropertyChanged()
    {
        var task = new BotTask { State = TaskState.Idle };
        Assert.False(task.IsRunning);
        Assert.False(task.Running);

        task.State = TaskState.Monitoring;
        Assert.True(task.IsRunning);
        Assert.True(task.Running);

        var changed = new List<string?>();
        task.PropertyChanged += (_, e) => changed.Add(e.PropertyName);

        task.Running = false;
        Assert.False(task.Running);
        Assert.Contains(nameof(BotTask.Running), changed);
    }

    [Fact]
    public void SettingBotTaskRunningUpdatesTaskGroupRunning()
    {
        var t1 = new BotTask { State = TaskState.Idle };
        var t2 = new BotTask { State = TaskState.Idle };
        var group = new TaskGroup { Tasks = new List<BotTask> { t1, t2 } };

        Assert.Equal(0, group.Running);

        t1.Running = true;
        Assert.Equal(1, group.Running);

        t2.State = TaskState.Waiting;
        Assert.Equal(2, group.Running);
    }

    [Fact]
    public void RunningIsJsonIgnoredSoTasksJsonSchemaIsUnchanged()
    {
        var prop = typeof(BotTask).GetProperty(nameof(BotTask.Running));
        Assert.NotNull(prop);
        Assert.Equal(typeof(bool), prop!.PropertyType);
        Assert.True(prop.CanRead && prop.CanWrite);
        Assert.NotNull(prop.GetCustomAttribute<JsonIgnoreAttribute>());

        var json = Json.Serialize(new BotTask { State = TaskState.Monitoring });
        Assert.DoesNotContain("\"Running\"", json);
        Assert.DoesNotContain("\"running\"", json);
    }
}
