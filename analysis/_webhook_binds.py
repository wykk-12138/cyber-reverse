import io, json
d = json.load(io.open('docs/xaml_bindings.json', encoding='utf-8'))
for k in d:
    if 'Webhook' in k:
        print('==', k)
        print('   ', sorted(d[k]) if isinstance(d[k], (list, set)) else d[k])
