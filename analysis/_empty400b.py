import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Common\EmptyView.cs"
t = io.open(p, encoding='utf-8').read()
# I added a For(key) that already exists; keep the existing one and only add Body(key)
old = '''    /// <summary>The block a page draws, with its own second line.</summary>
    public static EmptyView For(string key, double iconSize = 96) => new(Body(key), iconSize);'''
assert old in t
t = t.replace(old, '', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('duplicate For removed; Body(key) kept')
