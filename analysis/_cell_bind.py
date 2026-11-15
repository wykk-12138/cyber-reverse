import io, json
d = json.load(io.open('docs/xaml_bindings.json', encoding='utf-8'))
for k in d:
    if k.endswith('ElementCell') or k.endswith('TaskView'):
        print('%-52s %s' % (k, sorted(d[k])))
