import io, json
d = json.load(io.open('docs/xaml_bindings.json', encoding='utf-8'))
for k in d:
    if k.endswith('FilterRow') or k.endswith('ActionRow') or k.endswith('InputRow') or k.endswith('FilterInputEntry'):
        print('%-58s %s' % (k, sorted(d[k])))
