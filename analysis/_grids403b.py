import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Common\GroupGrid.cs"
t = io.open(p, encoding='utf-8').read()
old = '''        _selectedKey = selectedKey;
        _rows.Children.Clear();
        var built = new List<(string, string)>();'''
new = '''        _selectedKey = selectedKey;
        _rows.Children.Clear();
        var built = new List<(string, string)>();
        var keys = new List<string>();'''
assert old in t
t = t.replace(old, new, 1)
old2 = '''            built.Add((name, badge));'''
new2 = '''            built.Add((name, badge));
            keys.Add(key);'''
assert old2 in t
t = t.replace(old2, new2, 1)
# publish both lists at the end of SetRows
anchor = '''        Rows = built;'''
if anchor in t:
    t = t.replace(anchor, '''        Rows = built;
        Items = keys;''', 1)
    print('Items published alongside Rows')
else:
    print('Rows assignment not found; searching')
    i = t.find('built;', t.find('_rows.Children.Clear()'))
    print(repr(t[i-60:i+40]))
io.open(p, 'w', encoding='utf-8', newline='').write(t)
