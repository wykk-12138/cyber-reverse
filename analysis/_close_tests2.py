import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\CloseAndOpenFamilyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheProxyAndProfileDialogsCarryCloseToo()
    {
        var names = new[]
        {
            typeof(Cybersole.Ui.Views.Proxies.ProxyGroupView),
            typeof(Cybersole.Ui.Views.Proxies.ProxyCreatorView),
            typeof(Cybersole.Ui.Views.Profiles.ProfileGroupView),
        };

        foreach (var type in names)
        {
            var has = type.GetMethods().Any(m => m.Name == "Close");
            _out.WriteLine(type.Name + ": " + has);
            Assert.True(has, type.Name + " has no Close()");
        }
    }

    [Fact]
    public void DeletingAProxyGroupTakesTheListItCameFrom()
    {
        var group = new ProxyGroup { Name = "g" };
        var all = new List<ProxyGroup> { group };
        var view = new Cybersole.Ui.Views.Proxies.ProxyGroupView(group);

        Assert.True(view.Delete(all));
        Assert.False(view.Delete(all));
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('tests appended')
