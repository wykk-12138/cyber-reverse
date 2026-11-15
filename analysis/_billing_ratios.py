import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\BillingView.cs'
t = io.open(p, encoding='utf-8').read()
old = '            var row = new Grid { ColumnDefinitions = new ColumnDefinitions("18,*,*,*,*,*"), Margin = new Thickness(4, 2) };'
new = '''            // R223: measured column proportions, not equal stars. Header label left edges read at two window widths:
            //   1568: Profile 412  Email 550  Card Holder 727  Card 906  → 138 / 177 / 179 / 138
            //   1375: Profile 465  Email 558  Card Holder 678  Card 796  →  93 / 120 / 118 /  96
            //   ratio: 1.00      1.28        1.29         1.00
            // Shipping is the last column and absorbs the remainder, so like the Tasks table's Status it cannot be
            // measured from an empty table and stays at 1.
            var row = new Grid { ColumnDefinitions = new ColumnDefinitions("18,1.0*,1.28*,1.29*,1.0*,1.0*"), Margin = new Thickness(4, 2) };'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('billing columns set to measured ratios')
