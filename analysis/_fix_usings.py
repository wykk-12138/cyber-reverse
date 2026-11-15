import io
R = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views'

for rel, ns in ((r'\Tasks\TaskGrid.cs', 'Tasks'), (r'\Proxies\ProxyGrid.cs', 'Proxies')):
    p = R + rel
    t = io.open(p, encoding='utf-8').read()
    if 'using Cybersole.Ui.Views.Common;' not in t:
        t = t.replace('using Cybersole.Core.Models;', 'using Cybersole.Core.Models;\nusing Cybersole.Ui.Views.Common;', 1)
    io.open(p, 'w', encoding='utf-8', newline='').write(t)
    print('using added to', ns)

# TaskGrid: add the margin helper right above Docked
p = R + r'\Tasks\TaskGrid.cs'
t = io.open(p, encoding='utf-8').read()
anchor = '    private static Control Docked(Control control, Dock dock)'
helper = '''    /// <summary>Keeps the measured 60 px gap above the empty state.</summary>
    private static Control WithTopMargin(Control control)
    {
        control.Margin = new Thickness(0, 60, 0, 0);
        return control;
    }

'''
assert anchor in t and 'WithTopMargin' in t
if 'private static Control WithTopMargin' not in t:
    t = t.replace(anchor, helper + anchor, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('helper placed')
