import io, json, re, glob, os, collections
segs = json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\flow_step_sequences.json', encoding='utf-8'))

files = glob.glob(r'D:\projects\cyber-reverse\replica\src\Cybersole.Http\Stores\**\*.cs', recursive=True)
if not files:
    files = [f for f in glob.glob(r'D:\projects\cyber-reverse\replica\src\**\*.cs', recursive=True) if 'Store' in f]

methods = collections.defaultdict(set)
for f in files:
    t = io.open(f, encoding='utf-8', errors='replace').read()
    if 'IStoreModule' not in t and 'StoreModule' not in t:
        continue
    name = os.path.basename(f).replace('.cs', '')
    for m in re.finditer(r'\b(?:public|private|internal|protected)\s+(?:async\s+)?[\w<>,\?\[\]\.]+\s+(\w+)\s*\(', t):
        methods[name].add(m.group(1))

print('store module files:', len(methods))
unique = collections.defaultdict(set)
for name, ms in methods.items():
    for m in ms:
        owners = [n for n, other in methods.items() if m in other]
        if len(owners) == 1:
            unique[name].add(m)

print('files with unique methods:', len(unique))
for name in sorted(unique)[:8]:
    print('  %-28s %s' % (name, ', '.join(sorted(unique[name])[:6])))
