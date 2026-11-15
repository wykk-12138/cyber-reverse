import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs"
t = io.open(p, encoding='utf-8').read()
mine = '''    /// <summary>The billing group the combo currently shows, by index into the configuration.</summary>
    private BillingGroup? CurrentGroup()
    {
        var groups = _services.Config.BillingGroups;
        var index = _groups.SelectedIndex;
        return index >= 0 && index < groups.Count ? groups[index] : null;
    }
'''
if mine in t:
    t = t.replace(mine, '', 1)
    io.open(p, 'w', encoding='utf-8', newline='').write(t)
    print('duplicate CurrentGroup removed (the class already had one)')
else:
    print('my version not found; nothing changed')
