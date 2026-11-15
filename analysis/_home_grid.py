import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs'
t = io.open(p, encoding='utf-8').read()
old = '            ColumnDefinitions = new ColumnDefinitions("2*,8,1*"),'
new = '''            // R221: measured at two window widths. Left panel / right panel = 973/521 at 1568 and 845/453 at 1375 —
            // 1.865 and 1.867, i.e. the same proportion, with a 24 px gutter. The replica had "2*,8,1*", which made
            // the checkout panel about 7% too wide and the feed panel too narrow.
            ColumnDefinitions = new ColumnDefinitions("1.87*,24,1*"),'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('home grid updated')
