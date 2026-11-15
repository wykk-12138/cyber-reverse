import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Profiles\ProfileViews.cs'
t = io.open(p, encoding='utf-8').read()
old = '''                if (!group.Profiles.Contains(_profile)) group.Profiles.Add(_profile);
                _services.Config.Save();
                Status("Profile saved.");
                return;'''
new = '''                if (!group.Profiles.Contains(_profile)) group.Profiles.Add(_profile);
                _services.Config.Save();
                _saved = true;
                Status("Profile saved.");
                return;'''
assert old in t
t = t.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('_saved set on the single-profile path')
