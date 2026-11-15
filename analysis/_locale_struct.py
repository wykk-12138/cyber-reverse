import io, json
d = json.load(io.open('src/Cybersole.Core/Locales/Cybersole.Locales.en.json', encoding='utf-8'))
print('top-level:', list(d.keys())[:8])
for k in ('Tasks', 'tasks'):
    if k in d:
        t = d[k]
        print(k, 'items:', len(t))
        print([x for x in t if any(y in x for y in ('Start','Stop','Group','Editor','New'))][:12])
        break
