import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()

anchor = '''    /// <summary>The group this dialog is editing'''
add = '''    /// <summary>
    /// The Cloudflare solvers this group can pick from (bound as <c>CloudflareSolvers</c>). The dialog fills its combo
    /// from this list, so the property and the control cannot disagree.
    /// </summary>
    public IReadOnlyList<string> CloudflareSolvers =>
        _services.Captcha.Registry.Configs.Select(c => c.Name).DefaultIfEmpty("(none)").ToList();

    /// <summary>The group this dialog is editing'''
assert anchor in t
t = t.replace(anchor, add, 1)

# the combo now reads the property
t = t.replace('''        var solver = UiKit.Combo(_services.Captcha.Registry.Configs
            .Select(c => c.Name)
            .DefaultIfEmpty("(none)").ToList());''',
'''        var solver = UiKit.Combo(CloudflareSolvers);''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('CloudflareSolvers property added and used')
