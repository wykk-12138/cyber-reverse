import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs"
t = io.open(p, encoding='utf-8').read()

# use the class's own Selected() helper and its own refresh method
t = t.replace('''        var index = _profiles.SelectedIndex;
        var group = CurrentGroup();
        if (group is null || index < 0 || index >= group.Profiles.Count) return false;

        group.Profiles.RemoveAt(index);
        _services.Config.Save();
        ShowGroup(group);
        return true;''',
'''        var index = _profiles.SelectedIndex;
        var group = Selected();
        if (group is null || index < 0 || index >= group.Profiles.Count) return false;

        group.Profiles.RemoveAt(index);
        _services.Config.Save();
        Refresh();
        return true;''', 1)

t = t.replace('''        var index = _profiles.SelectedIndex;
        var group = CurrentGroup();
        if (group is null || index < 0 || index >= group.Profiles.Count) return false;

        OpenProfileEditor(group.Profiles[index]);
        return true;''',
'''        var index = _profiles.SelectedIndex;
        var group = Selected();
        if (group is null || index < 0 || index >= group.Profiles.Count) return false;

        OpenProfileEditor(group.Profiles[index].Id);
        return true;''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('uses Selected()/Refresh() and the profile id')
