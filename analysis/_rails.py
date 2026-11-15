import io
R = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views'

# 1) ProxyView: the rail had no width at all (it sized to content)
p = R + r'\Proxies\ProxyView.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        var grid = new GroupGrid();
        grid.SetRows('''
new = '''        // R222: the rail is a fixed 324 px. Measured on the running build at window widths 1375 and 1566 — the group
        // card inside the rail spanned x 25..349 (324 px) at BOTH widths, so it is fixed, not proportional. This rail
        // had no width at all and sized itself to its content.
        var grid = new GroupGrid { Width = RailWidth };
        grid.SetRows('''
assert old in t
t = t.replace(old, new, 1)
t = t.replace('    private static readonly IBrush AccentBrush',
'''    /// <summary>The left rail's fixed width, measured (see the comment in <see cref="BuildLeftPane"/>).</summary>
    internal const double RailWidth = 324;

    private static readonly IBrush AccentBrush''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('ProxyView rail 324')

# 2) BillingView: 320 -> 324
p2 = R + r'\BillingView.cs'
t2 = io.open(p2, encoding='utf-8').read()
old2 = '            ColumnDefinitions = new ColumnDefinitions("320,*"),'
new2 = '            // R222: 324 px, the measured rail width (see ProxyView.RailWidth).\n            ColumnDefinitions = new ColumnDefinitions("324,*"),'
assert old2 in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(old2, new2, 1))
print('BillingView rail 324')

# 3) AccountView: 300 -> 324
p3 = R + r'\Accounts\AccountView.cs'
t3 = io.open(p3, encoding='utf-8').read()
old3 = '        var pane = new DockPanel { LastChildFill = true, Width = 300 };'
new3 = '        // R222: 324 px, the measured rail width (was 300).\n        var pane = new DockPanel { LastChildFill = true, Width = 324 };'
assert old3 in t3
io.open(p3, 'w', encoding='utf-8', newline='').write(t3.replace(old3, new3, 1))
print('AccountView rail 324')
