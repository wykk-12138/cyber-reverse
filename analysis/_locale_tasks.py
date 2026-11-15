import io, json
for lang in ('en', 'zh-Hans'):
    d = json.load(io.open('src/Cybersole.Core/Locales/Cybersole.Locales.%s.json' % lang, encoding='utf-8'))
    ts = {k: v for k, v in d.items() if k.startswith('Tasks.')}
    print('==', lang, 'Tasks keys:', len(ts))
    for k in sorted(ts):
        if any(x in k for x in ('Start', 'Stop', 'Group', 'Editor', 'New', 'Search')):
            print('   %-34s %s' % (k, ts[k]))
