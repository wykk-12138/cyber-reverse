import io, json
d = json.load(io.open('docs/xaml_bindings.json', encoding='utf-8'))
for n in ('SmartActionsView','DataView','HelpView','CustomStoresView','CustomSizesView'):
    for k in d:
        if k.endswith('.' + n):
            print('%-24s %s' % (n, sorted(d[k])))
