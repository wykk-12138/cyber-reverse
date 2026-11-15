import io, json
bind = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\xaml_bindings.json', encoding='utf-8'))
hits = [(t, [m for m in ms if 'Url' in m or 'Link' in m or 'Product' in m]) for t, ms in bind.items()]
for t, ms in hits:
    if ms:
        print('%-52s %s' % (t.split('Cybersole.')[-1], ', '.join(ms)))
