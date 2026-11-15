import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\GroupSummaryTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void CloningCopiesTheGroupAndItsTasks()
    {
        using var services = TestServices.Create();
        var group = new TaskGroup { Name = "G", MonitorDelay = 1000 };
        group.Tasks.Add(new BotTask { Name = "t1", Store = "shop" });
        services.Config.TaskGroups.Add(group);

        var summary = new GroupSummary(services, group);
        var copy = summary.Clone();

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

        Assert.True(summary.Delete());
        Assert.False(summary.Delete());
        Assert.DoesNotContain(group, services.Config.TaskGroups);
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('tests appended')
