import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\SmartActions\SmartActionViews.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('        _services.Config.SmartActions.Add(copy);',
              '        _services.Config.SmartActions.Actions.Add(copy);', 1)
# IsEditing is documented as "opened on an existing action" — set it from the constructor
t = t.replace('''        _filters.AddRange(_action.Filters);''',
'''        _filters.AddRange(_action.Filters);
        IsEditing = existing is not null;''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('document collection fixed, IsEditing set')
