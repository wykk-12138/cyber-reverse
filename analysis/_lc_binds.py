import io, json
d = json.load(io.open('docs/xaml_bindings.json', encoding='utf-8'))
for k in d:
    if k.endswith('LoginControl') or k.endswith('UserView'):
        print(' ', k, '->', sorted(d[k]))
