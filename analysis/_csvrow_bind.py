import io, json
d = json.load(io.open('docs/xaml_bindings.json', encoding='utf-8'))
for k in d:
    if 'ProfileCsv' in k or 'ProfileCsvEditor' in k:
        print('==', k, '->', sorted(d[k]) if isinstance(d[k], (list, set)) else d[k])
