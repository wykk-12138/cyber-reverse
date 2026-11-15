import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs'
t = io.open(p, encoding='utf-8').read()
old = '''            _services.Config.Save();
            Status($"Created {created} profile(s).");'''
new = '''            _services.Config.Save();
            _saved = created > 0;
            Status($"Created {created} profile(s).");'''
assert old in t
t = t.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('_saved set on the bulk path too')
