import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''        var name = UiKit.Text(watermark: "Group name");'''
add = '''        var name = UiKit.Text(watermark: "Group name");
        name.TextChanged += (_, _) => _typedName = name.Text ?? string.Empty;'''
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, add, 1))
print('typed name tracked')
