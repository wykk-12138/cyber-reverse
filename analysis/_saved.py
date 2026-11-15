import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs'
t = io.open(p, encoding='utf-8').read()
old = '''    private void Save(bool bulk)
    {
        try
        {'''
new = '''    private void Save(bool bulk)
    {
        try
        {
            // R253: the bound members follow what actually happened
            IsBulk = bulk;'''
assert old in t
t = t.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('Save records IsBulk')
