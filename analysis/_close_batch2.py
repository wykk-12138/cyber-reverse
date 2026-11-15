import io

close_impl = '''    /// <summary>Closes the hosting dialog (bound as <c>Close</c>). False when this control has no window.</summary>
    public bool Close()
    {
        if (TopLevel.GetTopLevel(this) is not Window host) return false;

        host.Close();
        return true;
    }

'''
cancel_impl = '''    /// <summary>Closes the dialog without starting anything (bound as <c>Cancel</c>). False when it has no window.</summary>
    public bool Cancel()
    {
        if (TopLevel.GetTopLevel(this) is not Window host) return false;

        host.Close();
        return true;
    }

'''

jobs = [
    (r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyGroupView.cs",
     'public sealed class ProxyGroupView', close_impl, 'Close'),
    (r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyCreatorView.cs",
     'public sealed class ProxyCreatorView', close_impl, 'Close'),
    (r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs",
     'public sealed class ProfileGroupView', close_impl, 'Close'),
    (r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\StaggerStartView.cs",
     'public sealed class StaggerStartView', cancel_impl, 'Cancel'),
]

for path, cls, impl, member in jobs:
    t = io.open(path, encoding='utf-8').read()
    start = t.index(cls)
    # find the first member line after the class opening brace to anchor the insertion
    brace = t.index('{', start)
    nxt = t.index('\n', brace) + 1
    if 'public bool ' + member + '()' in t[start:]:
        print('already present:', cls)
        continue
    t = t[:nxt] + '\n' + impl + t[nxt:]
    io.open(path, 'w', encoding='utf-8', newline='').write(t)
    print('added', member, 'to', cls.split('.')[-1])
