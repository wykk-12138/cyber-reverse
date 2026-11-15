import io, json
d = json.load(io.open('docs/xaml_bindings.json', encoding='utf-8'))
for k in d:
    if 'TaskDetails' in k or 'TaskDetailsView' in k:
        print(k, '->', sorted(d[k]))
