import io, json
d = json.load(io.open('docs/xaml_bindings.json', encoding='utf-8'))
for k in d:
    if 'ComboBox' in k:
        print('==', k)
        members = d[k]
        print('   ', ', '.join(sorted(members)) if isinstance(members, (list, set)) else members)
