import io, json, os, re, glob
R = r'D:\projects\cyber-reverse\replica\src'
bind = json.load(io.open('xaml_bindings.json', encoding='utf-8'))

files = glob.glob(os.path.join(R, '**', '*.cs'), recursive=True)
all_text = []
for f in files:
    try:
        all_text.append(io.open(f, encoding='utf-8').read())
    except Exception:
        pass
blob = '\n'.join(all_text)
print('replica source files:', len(files), 'chars:', len(blob))

true_gap = {}
for typ, members in sorted(bind.items()):
    missing = [m for m in members if not re.search(r'\b' + re.escape(m) + r'\b', blob)]
    if missing:
        true_gap[typ] = missing

total_missing = sum(len(v) for v in true_gap.values())
print('types with something missing ANYWHERE in the replica:', len(true_gap))
print('members missing anywhere:', total_missing)
print()
for typ, missing in sorted(true_gap.items(), key=lambda kv: -len(kv[1]))[:14]:
    print('  %-56s %s' % (typ.split('Cybersole.')[-1], ', '.join(missing[:8])))
