import io, json
bind = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\xaml_bindings.json', encoding='utf-8'))
for k in bind:
    if 'SmartActions' in k or 'CreateInputModel' in k:
        print('%-46s (%d): %s' % (k.split('Cybersole.')[-1], len(bind[k]), ', '.join(bind[k])))
