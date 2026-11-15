import io, os, re, json

ROOT = r"D:\projects\cyber-reverse\replica"
SRC = os.path.join(ROOT, "src")

# 1) classes + who constructs them
files = {}
for dirpath, _d, fns in os.walk(SRC):
    if f"{os.sep}obj{os.sep}" in dirpath or f"{os.sep}bin{os.sep}" in dirpath:
        continue
    for fn in fns:
        if fn.endswith('.cs'):
            files[os.path.join(dirpath, fn)] = io.open(os.path.join(dirpath, fn), encoding='utf-8', errors='replace').read()

all_text = '\n'.join(files.values())
classes = sorted({m.group(1) for txt in files.values()
                  for m in re.finditer(r'\bpublic\s+sealed\s+class\s+(\w+)\s*:\s*(?:UserControl|Window)\b', txt)})
unreached = [c for c in classes if not re.search(r'\bnew\s+' + c + r'\s*\(', all_text)]

# 2) bound members that look like they open a view
binds = json.load(io.open(os.path.join(ROOT, 'docs', 'xaml_bindings.json'), encoding='utf-8'))
cands = []
for full, members in binds.items():
    for m in members:
        if not re.match(r'(Show|Open)', m):
            continue
        stem = re.sub(r'^(Show|Open)', '', m)
        for c in unreached:
            cstem = re.sub(r'(View|Window|Modal|Dialog)$', '', c)
            if stem and (stem.lower() == cstem.lower() or stem.lower().startswith(cstem.lower()) or cstem.lower().startswith(stem.lower())):
                cands.append((full.split('.')[-1], m, c))

print('unreached UI classes:', len(unreached))
print()
print('bound Show*/Open* members that name an unreached class:', len(cands))
for t, m, c in cands[:20]:
    print('    %-24s %-22s -> %s' % (t, m, c))
